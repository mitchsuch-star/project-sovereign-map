"""Row IC "Independent Command", the desk (November 19, 2026) — IC-1: THE PEACE, THE WAR, TO DECIDE.

The user's first playtest ended "everything feels convoluted and opaque and disconnected"; research and
three rounds of expert panels gave `docs/INDEPENDENT_COMMAND_SPEC.md`, and his approved plan built its
display-only half first. Pinned here: the ONE `desk` key (`backend/game_logic/today.py`) on every reply and
at boot; the fixed order of TO DECIDE; every row one sentence of 90 characters at most with one door; that
reading it writes nothing, draws no random number and leaves Take back open; that nothing hidden is read;
that a reader that fails takes nothing else down; and that the client's End Turn reasons and the backend's
rows are one list. The real client is driven at the first player's own setup by
`tests/test_dd_b_the_client_hands.py::TestRowICTheDesk`.
"""

from __future__ import annotations

import contextlib
import io
import json
import pathlib
import random
import re

import pytest

from backend.commands import take_back as TB
from backend.game_logic import threats, today

REPO = pathlib.Path(__file__).resolve().parents[1]
SCENARIO = REPO / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
SCRIPTS = REPO / "godot-client" / "project-sovereign" / "scripts"

# (+ "directive": row IC's second commit — a row that opens the LIST of an order to several corps)
DOOR_KINDS = {"marshal", "region", "day", "envoys", "ledger", "congress", "generals", "idle", "war", "court",
              "directive"}


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


def _src(name: str) -> str:
    return (SCRIPTS / name).read_text(encoding="utf-8")


def _func(source: str, name: str) -> str:
    match = re.search(rf"^(?:static )?func {re.escape(name)}\(.*?(?=^\S|\Z)", source, re.S | re.M)
    assert match, f"no func {name}"
    return match.group(0)


@pytest.fixture(scope="module")
def _boot():
    from backend.models.world_state import WorldState
    with _quiet():
        return WorldState.from_scenario(str(SCENARIO))


@pytest.fixture
def world(_boot):
    """The shipped 1805 board, a private copy per test."""
    from backend.models.world_state import WorldState
    return WorldState.from_dict(json.loads(json.dumps(_boot.to_dict(), default=str)))


@pytest.fixture
def client(world, monkeypatch):
    """The real endpoint on the shipped 1805 board (the keyless parser)."""
    import backend.main as main_module
    from backend.commands.parser import CommandParser
    from fastapi.testclient import TestClient
    monkeypatch.setattr(main_module, "world", world)
    monkeypatch.setattr(main_module, "game_state", {"world": world})
    with _quiet():
        monkeypatch.setattr(main_module, "parser", CommandParser(use_real_llm=False))
    TB.new_board()
    yield TestClient(main_module.app)
    TB.new_board()


def _say(client, text: str) -> dict:
    with _quiet():
        return client.post("/command", json={"command": text}).json()


def _open_province_beside(world, foe_name: str = "Mack"):
    """A province of ours next to `foe_name` with NOTHING in his way: its corps marched off, its
    garrison and its works gone."""
    foe = world.marshals[foe_name]
    for name in world.get_region(foe.location).adjacent_regions:
        region = world.get_region(name)
        if region is not None and region.controller == world.player_nation:
            for m in world.get_marshals_in_region(name):
                m.location = "Paris"
            region.garrison_strength = 0
            region.garrison_detachment = False
            region.buildings = [b for b in region.buildings if b["type"] != "fortification"]
            return region
    raise AssertionError(f"no province of ours stands beside {foe_name}")


def _see(world, region_name: str, level: str) -> None:
    from backend.models.intel import RegionIntel
    intel = world.intel.get(region_name)
    if intel is None:
        intel = world.intel[region_name] = RegionIntel(region_name)
    intel.visibility = level


def _ids(rows) -> list:
    return [str(r["id"]) for r in rows]


# ═════════════════════════════════════════════════════════════════════════════
# 1. The key — on every reply and at boot, one builder
# ═════════════════════════════════════════════════════════════════════════════

class TestTheOneKey:
    def test_the_boot_and_every_reply_carry_the_same_desk(self, client):
        boot = client.get("/test").json()
        reply = _say(client, "status")
        assert boot["desk"] is not None
        assert boot["desk"] == reply["desk"]
        assert set(boot["desk"]) >= {"peace", "war", "decide", "more", "shown", "danger"}

    def test_the_peace_says_how_the_campaign_is_won_and_how_far_along(self, world):
        from backend.game_logic import congress
        view = congress.titled(world)
        peace = today.peace(world)
        assert "Congress of Paris" in peace["text"]
        assert str(view["needed"]) in peace["text"] and str(view["count"]) in peace["text"]
        assert peace["door"] == {"kind": "congress"} and peace["hint"]
        # Lever L5 of the second blind reading (all three readers: "I cannot tell what a 'titled
        # province' is, or how to get the other ten"): "titled" is the game's own word and stays
        # (golden rule 11); the plain words ride beside it ON the line — a frame cannot hover.
        from backend.game_logic import game_end
        turns = int(game_end.cfg(world, "title_turns", game_end.TITLE_TURNS_DEFAULT))
        assert peace["text"] == (
            f"Win the peace: hold {view['needed']} titled provinces — your homeland, lands a treaty gave "
            f"you, and conquests kept {turns} turns — then summon the Congress of Paris. "
            f"You hold {view['count']}.")
        assert peace["hint"].startswith(
            "A titled province is one held for good: your homeland, a province a treaty gave you, "
            f"or a conquest you have held for {turns} turns.")

    def test_the_war_names_who_and_what_for(self, world):
        from backend.game_logic.war_status import build_active_wars
        wars = build_active_wars(world)
        said = today.war(world, wars)
        first = next(w for w in wars["wars"] if w["status"] == "war")
        assert str(first["war_title"]) in said["text"]
        assert "to hold the homeland" in said["text"]          # the boot purpose: defense, in plain words
        assert said["door"] == {"kind": "war", "opponent": first["opponent"]}

    def test_the_desk_reads_the_wars_and_the_forecast_the_envelope_holds(self, world, monkeypatch):
        """The envelope hands over what it built: the desk does not work the wars or the
        treasury's forecast out a second time (it rides every reply)."""
        import backend.game_logic.ledger as ledger
        import backend.game_logic.war_status as war_status
        from backend.game_logic.war_status import build_active_wars
        wars = build_active_wars(world)

        def _never(*_a, **_k):
            raise AssertionError("worked out twice")
        monkeypatch.setattr(war_status, "build_active_wars", _never)
        monkeypatch.setattr(ledger, "chest_forecast", _never)
        built = today.desk(world, wars, {"gold_projected_net": 100})
        assert built is not None and built["war"]["text"]

    def test_every_row_is_one_short_sentence_with_one_door(self, world):
        rows = today.decide(world)
        assert rows
        for row in rows:
            assert set(row) >= {"id", "tier", "text", "door"}, row
            assert 0 < len(row["text"]) <= today.ROW_CAP, (len(row["text"]), row["text"])
            assert row["text"].endswith((".", "…", "?")), row["text"]
            assert row["door"].get("kind") in DOOR_KINDS, row
            assert "_" not in row["text"], row["text"]            # no internal key leaks into the words
        tiers = [row["tier"] for row in rows]
        assert tiers == sorted(tiers)                               # what bites, then what wastes, then what grows

    def test_the_list_is_whole_and_the_desk_shows_three(self, world):
        built = today.desk(world)
        assert built["shown"] == today.ROWS_SHOWN == 3
        assert len(built["decide"]) <= today.MAX_ROWS
        assert built["more"] == max(0, len(today.decide(world)) - today.MAX_ROWS)

    def test_the_first_morning_names_the_enemy_in_reach(self, world):
        """Turn one of 1805 already says something to do (the design's own first morning)."""
        rows = today.decide(world)
        reach = [r for r in rows if r["id"].startswith("reach:")]
        assert reach, _ids(rows)
        assert reach[0]["id"] == "reach:Mack" and "Mack" in reach[0]["text"]
        assert reach[0]["door"]["kind"] == "marshal"
        assert world.marshals[reach[0]["door"]["marshal"]].nation == world.player_nation

    def test_the_first_open_line_rides_once(self, world):
        from backend.game_logic import first_open
        built = today.desk(world)
        assert built["first_open"]["screen"] == "desk"
        line = built["first_open"]["line"]
        assert "Sire" in line and len(line) <= first_open.LINE_CAP
        for word in ("THE PEACE", "THE WAR", "TO DECIDE"):
            assert word in line
        assert first_open.mark_seen(world, "desk")
        world.current_turn += 1
        assert "first_open" not in today.desk(world)

    def test_the_seam_down_is_no_desk_at_all(self, client, monkeypatch):
        monkeypatch.setattr(today, "the_desk_is_shown", lambda: False)
        assert client.get("/test").json()["desk"] is None
        reply = _say(client, "what now?")
        assert reply["desk"] is None
        assert "To decide now:" not in str(reply.get("message") or "")

    def test_no_desk_in_the_school_or_after_the_end(self, world, monkeypatch):
        from backend.game_logic import game_end, tutorial_state
        monkeypatch.setattr(tutorial_state, "is_school_world", lambda w: True)
        assert today.desk(world) is None
        monkeypatch.setattr(tutorial_state, "is_school_world", lambda w: False)
        assert today.desk(world) is not None
        monkeypatch.setattr(game_end, "terminal_ending", lambda w: {"cause": "x"})
        assert today.desk(world) is None

    def test_what_now_answers_from_the_same_rows(self, client, world):
        message = str(_say(client, "what now?").get("message") or "")
        head, sep, block = message.partition("\nTo decide now:\n")
        assert sep, message
        assert head.startswith("These orders would be carried out today, Sire:")
        want = [f"  {row['text']}" for row in today.decide(world)[:3]]
        assert block.split("\n") == want


# ═════════════════════════════════════════════════════════════════════════════
# 2. Reading it changes nothing
# ═════════════════════════════════════════════════════════════════════════════

class TestReadingItChangesNothing:
    def test_the_board_and_the_dice_are_untouched(self, world):
        _open_province_beside(world)                    # a board with a danger row on it too
        before = json.dumps(world.to_dict(), sort_keys=True, default=str)
        dice = random.getstate()
        for _ in range(3):
            assert today.desk(world) is not None
            today.what_now_lines(world)
            threats.in_danger(world, world.player_nation)
        assert json.dumps(world.to_dict(), sort_keys=True, default=str) == before
        assert random.getstate() == dice

    def test_take_back_stays_open(self, client):
        reply = _say(client, "Davout, march to Lorraine")
        assert reply["success"] and reply["undo"]["available"], reply.get("message")
        kept = reply["undo"]
        assert client.get("/test").json()["undo"] == kept
        assert _say(client, "what now?")["undo"] == kept
        assert _say(client, "status")["undo"] == kept


# ═════════════════════════════════════════════════════════════════════════════
# 3. Nothing hidden is read
# ═════════════════════════════════════════════════════════════════════════════

class TestNothingHiddenIsRead:
    def test_an_unseen_corps_gives_no_row_and_no_mark(self, world):
        region = _open_province_beside(world, "Mack")
        _see(world, world.marshals["Mack"].location, "unknown")
        built = today.desk(world)
        assert built["danger"] == []
        assert not [r for r in built["decide"] if "Mack" in r["text"] or r["id"].endswith(":Mack")]
        assert threats.in_danger(world, world.player_nation) == []
        assert region.name not in json.dumps(built["danger"])

    def test_a_corps_half_seen_is_named_with_its_band_never_its_count(self, world):
        region = _open_province_beside(world, "Mack")
        mack = world.marshals["Mack"]
        _see(world, mack.location, "partial")
        rows = threats.in_danger(world, world.player_nation)
        assert [r["region"] for r in rows] == [region.name]
        line = rows[0]["line"]
        assert line.startswith(f"Nothing holds {region.name} — Mack (")
        assert f"{int(mack.strength):,}" not in line and str(int(mack.strength)) not in line
        assert not any(ch.isdigit() for ch in line), line
        for row in today.decide(world):
            assert f"{int(mack.strength):,}" not in row["text"], row["text"]

    def test_a_corps_in_full_sight_is_counted(self, world):
        region = _open_province_beside(world, "Mack")
        mack = world.marshals["Mack"]
        _see(world, mack.location, "full")
        built = today.desk(world)
        assert built["danger"] == [{"region": region.name,
                                    "line": f"Nothing holds {region.name} — Mack ({int(mack.strength):,} men) "
                                            f"is one march away."}]
        row = next(r for r in built["decide"] if r["id"] == f"danger:{region.name}")
        assert row["tier"] == today.TIER_BITES and row["door"] == {"kind": "region", "region": region.name}

    def test_the_readers_ask_only_what_the_player_may_know(self):
        """The desk's own source never reaches for the omniscient roster reads."""
        for module in ("today.py", "threats.py"):
            source = (REPO / "backend" / "game_logic" / module).read_text(encoding="utf-8")
            code = "\n".join(line for line in source.split("\n") if not line.strip().startswith("#"))
            assert "get_enemies_of_nation" not in code, module
            assert "get_enemy_marshals" not in code, module
            assert ".regions.values()" not in code and ".regions.items()" not in code, module   # golden rule 8


# ═════════════════════════════════════════════════════════════════════════════
# 4. What stands in the way — the game's own rule, for our ground
# ═════════════════════════════════════════════════════════════════════════════

class TestWhatStandsInTheWay:
    def test_a_corps_a_fighting_garrison_or_works_stop_a_march(self, world):
        region = _open_province_beside(world, "Mack")
        player = world.player_nation
        assert threats.stands_in_the_way(world, region, player, "Austria") == ""
        region.garrison_detachment = True
        region.garrison_strength = 200                  # under the surrender floor: it gives way
        assert threats.stands_in_the_way(world, region, player, "Austria") == ""
        region.garrison_strength = 3000                 # a detachment that fights
        assert threats.stands_in_the_way(world, region, player, "Austria") == "garrison"
        region.garrison_strength = 0
        region.buildings.append({"type": "fortification", "damaged": False})
        assert threats.stands_in_the_way(world, region, player, "Austria") == "works"
        world.marshals["Ney"].location = region.name
        assert threats.stands_in_the_way(world, region, player, "Austria") == "corps"

    def test_only_an_open_province_is_in_danger(self, world):
        region = _open_province_beside(world, "Mack")
        player = world.player_nation
        assert region.name in [r["region"] for r in threats.in_danger(world, player)]
        region.buildings.append({"type": "fortification", "damaged": False})
        assert region.name not in [r["region"] for r in threats.in_danger(world, player)]
        region.buildings = []
        world.marshals["Ney"].location = region.name
        assert region.name not in [r["region"] for r in threats.in_danger(world, player)]

    def test_is_it_safe_reads_the_same_rule(self, world):
        """IC-D1, the sibling: the typed "is X safe?" said "held, but threatened" of a token
        garrison a march walks through."""
        from backend.ai.question_desk import _answer_safe
        region = _open_province_beside(world, "Mack")
        player = world.player_nation
        assert _answer_safe(world, player, region.name).endswith(
            "It is in danger — nothing of ours stands in its way.")
        region.garrison_detachment = True
        region.garrison_strength = 200
        assert _answer_safe(world, player, region.name).endswith(
            "It is in danger — the garrison is too small to stop a march.")
        region.garrison_strength = 3000
        assert _answer_safe(world, player, region.name).endswith("It is held, but threatened.")
        region.garrison_strength = 0
        region.buildings.append({"type": "fortification", "damaged": False})
        assert _answer_safe(world, player, region.name).endswith(
            "Its works must be besieged, which buys time — but it is threatened.")

    def test_the_two_march_reading_is_one_place(self):
        source = (REPO / "backend" / "ai" / "question_desk.py").read_text(encoding="utf-8")
        body = source[source.index("def _answer_safe("):source.index("def _safe_for_the_holder(")]
        assert "_threats.visible_threats(world, player, region_name)" in body
        assert "get_visible_enemies" not in body.split('"""', 2)[2]      # the loop itself moved out

    def test_the_danger_sentence_always_fits(self):
        row = {"region": "Mecklenburg-Vorpommern-Strelitz", "by_shown": ["Archduke Ferdinand of Austria-Este"],
               "force": "substantial force", "more": 3}
        for cap in (90, 70, 50):
            line = threats.danger_line(row, cap)
            assert len(line) <= cap
            # the review: the last resort cut a word in half — it ends on a whole word now
            assert line.endswith((".", "…")), line
            if line.endswith("…"):
                assert (line[:-1] + " ") in (
                    "Mecklenburg-Vorpommern-Strelitz: nothing holds it, and an enemy is one march away. "), line

    def test_a_token_garrison_is_said_to_be_too_small(self, world):
        """"Nothing holds X" was said of a province with 200 men in it. A march walks through
        them (`garrison_report.garrison_fights`), and the line says so."""
        region = _open_province_beside(world, "Mack")
        mack = world.marshals["Mack"]
        _see(world, mack.location, "full")
        region.garrison_detachment = True
        region.garrison_strength = 200
        row = next(r for r in threats.in_danger(world, world.player_nation) if r["region"] == region.name)
        assert row["garrison"] == 200
        assert row["line"] == (f"{region.name}'s garrison is too small to hold it — Mack "
                               f"({int(mack.strength):,} men) is one march away.")
        region.garrison_strength = 0
        row = next(r for r in threats.in_danger(world, world.player_nation) if r["region"] == region.name)
        assert row["garrison"] == 0 and row["line"].startswith(f"Nothing holds {region.name} — ")

    def test_a_raiding_party_in_full_sight_is_no_danger(self, world):
        """The review (IC-R1): a corps of under 5,000 men holds no homeland province it walks
        onto — where the player SEES the count, the mark is not raised. Half-seen, he knows only
        a band, and a mark that vanished below the floor would hand him the number: it stands."""
        from backend.commands.movement_executor import RAIDING_PARTY_FLOOR, raiding_party_holds_no_ground
        region = _open_province_beside(world, "Mack")
        mack = world.marshals["Mack"]
        mack.strength = RAIDING_PARTY_FLOOR - 1
        assert raiding_party_holds_no_ground(mack, region, world)       # the board's own rule says so
        _see(world, mack.location, "full")
        assert region.name not in [r["region"] for r in threats.in_danger(world, world.player_nation)]
        _see(world, mack.location, "partial")
        assert region.name in [r["region"] for r in threats.in_danger(world, world.player_nation)]
        mack.strength = RAIDING_PARTY_FLOOR
        _see(world, mack.location, "full")
        assert region.name in [r["region"] for r in threats.in_danger(world, world.player_nation)]

    def test_a_recovering_corps_is_still_warned_of(self, world):
        """No screen shows the player an enemy's recovery after a retreat, so the reading does
        not use it: the warning stands (the cautious reading, and it gives nothing away)."""
        source = (REPO / "backend" / "game_logic" / "threats.py").read_text(encoding="utf-8")
        code = "\n".join(line for line in source.split("\n") if not line.strip().startswith("#"))
        assert "corps_takes_no_ground(" not in code.replace("(`corps_takes_no_ground`)", "")
        assert "in_retreat_recovery" not in code

    def test_water_the_gate_shuts_is_no_road(self, world, monkeypatch):
        """The review (IC-R8): `adjacent_regions` counts the sea links. A crossing the gate shuts
        to his court is no march."""
        from backend.game_logic import naval
        region = _open_province_beside(world, "Mack")
        mack = world.marshals["Mack"]
        assert region.name in [r["region"] for r in threats.in_danger(world, world.player_nation)]
        monkeypatch.setattr(naval, "is_sea_link", lambda w, a, b: {a, b} == {mack.location, region.name})
        monkeypatch.setattr(naval, "crossing_allowed", lambda w, nation, a, b: False)
        assert region.name not in [r["region"] for r in threats.in_danger(world, world.player_nation)]
        monkeypatch.setattr(naval, "crossing_allowed", lambda w, nation, a, b: True)
        assert region.name in [r["region"] for r in threats.in_danger(world, world.player_nation)]


# ═════════════════════════════════════════════════════════════════════════════
# 5. The rows, one reader at a time, in the list's fixed order
# ═════════════════════════════════════════════════════════════════════════════

class TestTheRows:
    def test_the_order_of_the_list_is_the_design_s(self):
        assert [name for name, _reader in today.READERS] == [
            "last_stand", "battle_days", "lapses", "treasury", "peril", "danger", "strike",
            "take", "reach_and_idle", "restless",
            "exact_orders",      # row IC, Session 2 (IC-9): if-thens used up, or struck
            "congress", "law", "commission"]

    def test_a_last_stand_and_a_day_of_battle_lead(self, world, monkeypatch):
        from backend.commands import strategic
        from backend.game_logic import battle_day
        monkeypatch.setattr(strategic, "pending_marshal_decisions", lambda w: ["Lannes"])
        monkeypatch.setattr(battle_day, "awaiting", lambda w: [
            {"enemy": "Mack", "enemy_shown": "Mack", "lead": "Ney", "lead_shown": "Ney",
             "field": "Swabia", "field_shown": "Swabia", "side": "attacker", "ours": 2}])
        rows = today.decide(world)
        assert _ids(rows)[:2] == ["last_stand:Lannes", "day:Mack"]
        assert rows[0]["door"] == {"kind": "marshal", "marshal": "Lannes"}
        assert rows[1]["door"] == {"kind": "day", "enemy": "Mack"}
        assert rows[1]["text"] == "The battle at Swabia has no winner yet — Ney still waits for your orders."

    def test_letters_that_lapse_are_counted(self, world, monkeypatch):
        monkeypatch.setattr(type(world.dialogue_manager), "get_lapsing_count", lambda self, turn: 2)
        rows = [r for r in today.decide(world) if r["door"].get("kind") == "envoys"]
        assert [r["text"] for r in rows] == ["2 envoys are still unanswered — their offers end when the turn ends."]
        assert rows[0]["tier"] == today.TIER_BITES
        monkeypatch.setattr(type(world.dialogue_manager), "get_lapsing_count", lambda self, turn: 1)
        rows = [r for r in today.decide(world) if r["door"].get("kind") == "envoys"]
        assert [r["text"] for r in rows] == ["1 envoy is still unanswered — the offer ends when the turn ends."]

    def test_a_petition_and_a_letter_of_state_say_what_silence_does(self, world, monkeypatch):
        """The gate's own words: a priced petition "will be REFUSED"; a letter of state lapses AS
        ITS DECLINE (S14C-X26). The row says what the silence does, not that something "lapses"."""
        from backend.game_logic import mailbox_payloads, moments
        monkeypatch.setattr(type(world.dialogue_manager), "get_lapsing_count", lambda self, turn: 3)
        monkeypatch.setattr(mailbox_payloads, "lapsing_petitions", lambda w, n: [
            {"vassal": "Bavaria", "court": "Bavaria", "penalised": True, "price_line": "Bavaria — −10 loyalty"},
            {"vassal": "Baden", "court": "Baden", "penalised": False, "price_line": ""}])
        monkeypatch.setattr(moments, "lapse_gate_rows", lambda w: [
            {"title": "The Reich Letter", "price_line": "Let Baden keep her."}])
        rows = {r["id"]: r for r in today.decide(world) if r["door"].get("kind") == "envoys"}
        assert rows["petition:Bavaria"]["text"] == "Bavaria's petition counts as refused if you do not answer it this turn."
        assert rows["petition:Bavaria"]["more"] == "Bavaria — −10 loyalty"
        assert rows["petition:Baden"]["text"] == "Baden's petition goes unanswered if you do not answer it this turn."
        assert rows["moment:The Reich Letter"]["text"] == (
            "The Reich Letter counts as declined if you do not answer it this turn.")
        assert "lapse" not in rows                       # all three were named: no bare count is left

    def test_a_treasury_about_to_go_below_zero(self, world):
        world.gold = 800
        rows = today.decide(world, {"gold_projected_net": -1000})
        row = next(r for r in rows if r["id"] == "treasury")
        # the gate's own sentence and its three figures, with a true minus sign (U+2212)
        assert row["text"] == "The treasury will stand at −200 gold when the turn ends (800 now, −1,000 a turn)."
        assert row["door"] == {"kind": "ledger", "tab": 2}
        gate = _func(_src("main.gd"), "_show_lapse_confirmation")
        assert '"The treasury will stand at %s gold when the turn ends (%s now, %s next turn)' in gate
        assert today._signed(1200) == "+1,200" and today._signed(-486) == "−486" and today._signed(0) == "0"
        assert "treasury" not in _ids(today.decide(world, {"gold_projected_net": -700}))   # 800 − 700 ≥ 0
        assert "treasury" not in _ids(today.decide(world, {"gold_projected_net": None}))

    def test_the_army_s_warnings_each_open_the_corps_they_name(self, world, monkeypatch):
        from backend.game_logic import dispatch
        peril = ("Ney's corps (17,000) stands in peril — an enemy force of ~52,000 shares the "
                 "field (Belgium).")
        morale = ("Lannes's corps stands below 40% morale beside Bagration (55,404, Podolia) — "
                  "end the turn anyway?")
        halt = ("Massena (aggressive) holds a standing order at Bohemia with Kutuzov's ~33,000 two "
                "provinces off — he will drop it for any battle within two provinces in a war of ours.")
        monkeypatch.setattr(dispatch, "end_turn_peril_reading",
                            lambda w, n: {"location": "Belgium", "foe": 52000, "corps": ["Ney"], "line": peril})
        monkeypatch.setattr(dispatch, "end_turn_morale_reading",
                            lambda w, n: {"corps": ["Lannes"], "location": "Podolia", "line": morale})
        monkeypatch.setattr(dispatch, "end_turn_interrupt_reading",
                            lambda w, n: {"corps": [{"marshal": "Massena", "foe": "Kutuzov", "hops": 2}],
                                          "line": halt})
        rows = {r["id"]: r for r in today.decide(world)}
        assert rows["peril"]["door"] == {"kind": "marshal", "marshal": "Ney"}
        assert rows["peril"]["more"] == peril and len(rows["peril"]["text"]) <= 90
        assert rows["morale"]["text"] == "Lannes's corps stands below 40% morale beside Bagration (55,404, Podolia)."
        assert rows["morale"]["more"] == morale
        assert rows["interrupt:Massena"]["door"] == {"kind": "marshal", "marshal": "Massena"}
        assert "Kutuzov is close" in rows["interrupt:Massena"]["text"]
        assert rows["interrupt:Massena"]["more"] == halt
        # The third blind reading ("a standing order that I never gave?"): the row names what he
        # would break off by the order's own plain word — the march, the pursuit, the post.
        for order, words in (("MOVE_TO", "Massena will break off his march to join a battle near him — Kutuzov is close."),
                             ("PURSUE", "Massena will break off his pursuit to join a battle near him — Kutuzov is close."),
                             ("HOLD", "Massena will leave his post to join a battle near him — Kutuzov is close."),
                             ("SUPPORT", "Massena will leave the corps he supports to join a battle near him — Kutuzov is close."),
                             ("", "Massena will leave his standing order to join a battle near him — Kutuzov is close.")):
            monkeypatch.setattr(dispatch, "end_turn_interrupt_reading",
                                lambda w, n, order=order: {"corps": [{"marshal": "Massena", "foe": "Kutuzov",
                                                                      "hops": 2, "order": order}], "line": halt})
            row = next(r for r in today.decide(world) if r["id"] == "interrupt:Massena")
            assert row["text"] == words, (order, row["text"])
            assert len(row["text"]) <= today.ROW_CAP

    def test_the_interrupt_reading_says_which_order_he_holds(self, world):
        """The reading's rows carry the order's type (the gate's sentence is unchanged)."""
        from backend.game_logic import dispatch
        source = (REPO / "backend" / "game_logic" / "dispatch.py").read_text(encoding="utf-8")
        body = source[source.index("def end_turn_interrupt_reading("):]
        body = body[:body.index("\ndef ", 10)]
        assert '"order": str(getattr(getattr(m, "strategic_order", None), "command_type", "") or "")' in body
        read = dispatch.end_turn_interrupt_reading(world, world.player_nation)
        for man in (read or {}).get("corps") or []:
            assert set(man) == {"marshal", "foe", "hops", "order"}

    def test_the_gate_s_sentences_are_the_readings_own(self, world):
        """The three End Turn sentences are each `…_reading(...)["line"]` — the words unchanged."""
        from backend.game_logic import dispatch
        player = world.player_nation
        for warning, reading in ((dispatch.end_turn_peril_warning, dispatch.end_turn_peril_reading),
                                 (dispatch.end_turn_morale_warning, dispatch.end_turn_morale_reading),
                                 (dispatch.end_turn_interrupt_warning, dispatch.end_turn_interrupt_reading)):
            read = reading(world, player)
            assert warning(world, player) == (read["line"] if read else None)
        ney = world.marshals["Ney"]
        ney.location = world.marshals["Mack"].location           # a corps beside a far larger army
        ney.strength = 5000
        _see(world, ney.location, "full")
        read = dispatch.end_turn_peril_reading(world, player)
        assert read and read["corps"] == ["Ney"] and read["location"] == ney.location
        assert dispatch.end_turn_peril_warning(world, player) == read["line"]
        assert read["line"].startswith("Ney's corps (5,000) stands in peril — an enemy force of ~")

    def test_a_man_who_may_attack_without_orders_bites_tonight(self, world):
        world.marshals["Murat"].jealousy_autonomous_warned = True
        row = next(r for r in today.decide(world) if r["id"] == "strike:Murat")
        assert row["tier"] == today.TIER_BITES
        assert row["text"] == "Murat may attack on his own when the turn ends — an order that reaches him stops it."
        assert row["door"] == {"kind": "marshal", "marshal": "Murat"}

    def test_an_order_that_reaches_him_takes_the_row_away(self, world):
        """The row's promise is the game's own rule (`jealousy.cancel_autonomous_warning_on_order`:
        "your orders reached him in time")."""
        from backend.game_logic import jealousy
        murat = world.marshals["Murat"]
        murat.jealousy_autonomous_warned = True
        assert "strike:Murat" in _ids(today.decide(world))
        note = jealousy.cancel_autonomous_warning_on_order(world, murat)
        assert "your orders reached him in time" in note
        assert "strike:Murat" not in _ids(today.decide(world))

    def test_a_corps_on_ground_it_could_take(self, world):
        ney = world.marshals["Ney"]
        target = next(name for name, r in sorted(world.regions.items())
                      if r.controller == "Austria" and not r.is_capital)
        region = world.get_region(target)
        for m in world.get_marshals_in_region(target):
            m.location = "Vienna"
        region.garrison_strength = 0
        region.buildings = [b for b in region.buildings if b["type"] != "fortification"]
        ney.location = target
        assert today.takers(world) == [{"marshal": "Ney", "place": target, "fort": False,
                                        "label": f"Take {target}"}]
        row = next(r for r in today.decide(world) if r["id"] == "take:Ney")
        assert row["text"] == f"Ney stands in {target} and nothing holds it — one action takes it."
        assert row["tier"] == today.TIER_WASTES
        assert row["door"] == {"kind": "marshal", "marshal": "Ney"}     # the corps, never the order itself
        world.actions_remaining = 0
        assert today.takers(world) == []

    def test_the_idle_corps_are_one_row(self, world):
        rows = today.decide(world)
        named = [r for r in rows if r["id"].startswith("reach:")]
        idle = [r for r in rows if r["id"] == "idle"]
        assert len(named) <= today.REACH_ROWS and len(idle) <= 1
        for m in world.get_player_marshals():
            m.fortified = True                             # every corps has something to do
        assert not [r for r in today.decide(world) if r["id"] == "idle" or r["id"].startswith("reach:")]

    def test_with_no_action_left_a_corps_with_no_orders_is_no_matter(self, world):
        """Lever L4 of the blind reading (reader 3: "Actions 0/4 — '6 corps have no orders'
        cannot be acted on"): with nothing left to give, there is nothing to decide — no row
        here, and no reason for End Turn to stop (the take warning's own rule)."""
        assert [r for r in today.decide(world) if r["id"] == "idle" or r["id"].startswith("reach:")]
        world.actions_remaining = 0                        # nothing can be ordered
        rows = today.decide(world)
        assert not [r for r in rows if r["id"] == "idle" or r["id"].startswith("reach:")]
        gate = _func(_src("main.gd"), "_ui5_idle_warning_stands")
        assert "int(actions_remaining) > 0" in gate

    def test_a_reach_row_says_ours_first_then_the_enemy(self, world):
        """The review: "Mack is in Swabia — A, B and C are within one march, with no orders" read
        as the ENEMY's march. Ours first."""
        row = next(r for r in today.decide(world) if r["id"] == "reach:Mack")
        assert " no orders and Mack (" in row["text"] and row["text"].endswith("is within one march, in Swabia.")
        assert row["text"].split(" ")[0] != "Mack"
        # the second reading, reader 3: "'7 corps of yours' does not tell me which ones" — the
        # row's hover names every one of them
        assert row["more"].startswith("No orders: ") and row["more"].endswith(".")
        named = row["more"][len("No orders: "):-1].split(", ")
        assert len(named) >= 2 and all(world.marshals[n].nation == world.player_nation for n in named)

    def test_a_literal_man_left_out(self, world, monkeypatch):
        from backend.game_logic import jealousy
        soult = world.marshals["Soult"]
        assert soult.personality == "literal"
        soult.consecutive_hold_turns = jealousy.LITERAL_RESTLESS_AT
        row = next(r for r in today.decide(world) if r["id"] == "restless:Soult")
        assert row["text"] == "Soult has been left out for 2 turns while others march — give him a task."
        monkeypatch.setattr(jealousy, "jealousy_dormant", lambda w: True)
        assert "restless:Soult" not in _ids(today.decide(world))

    def test_what_could_grow_the_empire_comes_last(self, world, monkeypatch):
        from backend.ai import counsel
        from backend.game_logic import congress, recruitment
        world.gold = 50_000
        monkeypatch.setattr(congress, "titled", lambda w: {"titled": [], "held": [], "count": 46, "needed": 45})
        monkeypatch.setattr(counsel, "congress_counsel", lambda w, n: ["F1 → the Congress"])
        monkeypatch.setattr(recruitment, "first_affordable_commission",
                            lambda w, n: {"name": "Oudinot", "cost": 600})
        monkeypatch.setattr(recruitment, "commission_counsel_need", lambda w, n: True)
        rows = today.decide(world)
        grows = [r for r in rows if r["tier"] == today.TIER_GROWS]
        assert _ids(grows)[0] == "congress" and _ids(grows)[-1] == "commission"
        assert grows[0]["door"] == {"kind": "congress"}
        assert grows[0]["text"] == "You can summon the Congress of Paris now — the way to win; it cannot be undone."
        law = next(r for r in grows if r["id"].startswith("law:"))
        assert law["door"] == {"kind": "ledger", "tab": 7} and "gold" in law["text"]
        assert grows[-1]["text"] == "You can commission Oudinot to lead a new corps (600 gold)."
        assert grows[-1]["door"] == {"kind": "generals"}
        assert rows[-len(grows):] == grows

    def test_a_marshal_is_urged_only_where_the_army_needs_one(self, world, monkeypatch):
        """The review (IC-R4): without the counsel's own need (a thin roster or an army under
        strength — the PT-I4 ruling) the row was a standing nudge to spend."""
        from backend.game_logic import recruitment
        monkeypatch.setattr(recruitment, "first_affordable_commission",
                            lambda w, n: {"name": "Oudinot", "cost": 600})
        monkeypatch.setattr(recruitment, "commission_counsel_need", lambda w, n: False)
        assert "commission" not in _ids(today.decide(world))
        monkeypatch.setattr(recruitment, "commission_counsel_need", lambda w, n: True)
        assert "commission" in _ids(today.decide(world))

    def test_no_law_is_urged_that_is_paid_in_authority(self, world):
        from backend.game_logic import reforms
        world.gold = 0
        affordable = [row for row in reforms.deck(world, world.player_nation)
                      if not reforms.law_refusal(world, world.player_nation, row["id"])]
        assert affordable and all(str(row.get("currency")) == "authority" for row in affordable)
        assert not [r for r in today.decide(world) if r["id"].startswith("law:")]

    def test_a_reader_that_fails_takes_nothing_else_down(self, world, monkeypatch):
        def _boom(w, have):
            raise RuntimeError("a reading broke")
        patched = [(name, _boom if name == "danger" else reader) for name, reader in today.READERS]
        monkeypatch.setattr(today, "READERS", patched)
        built = today.desk(world)
        assert built is not None and built["decide"] and built["peace"]["text"]

    def test_fit_takes_the_fullest_form_that_fits(self):
        assert today._fit(["a long sentence that will not fit", "short."], 10) == "short."
        cut = today._fit(["one two three four five six seven"], 20)
        assert len(cut) <= 20 and cut.endswith("…")
        assert today._names(["Ney"]) == "Ney"
        assert today._names(["Ney", "Davout"]) == "Ney and Davout"
        assert today._names(["Ney", "Davout", "Lannes"]) == "Ney, Davout and Lannes"
        assert today._names(["Ney", "Davout", "Lannes", "Murat"]) == "Ney, Davout and 2 more"


# ═════════════════════════════════════════════════════════════════════════════
# 6. The desk and End Turn are one list
# ═════════════════════════════════════════════════════════════════════════════

# Every reason the client's End Turn stops for, and the desk reader that says it.
GATE_REASONS = {
    "_current_lapsing_count > 0": "lapses",
    "_current_decision_names.is_empty()": "last_stand",
    "_treasury_goes_negative()": "treasury",
    "_army_warning_stands()": "peril",
    "_ic_danger_warning_stands()": "danger",
    "_ic_strike_warning_stands()": "strike",
    "_day_warning_stands()": "battle_days",
    "_pw_take_warning_stands()": "take",
    "_ui5_idle_warning_stands()": "reach_and_idle",
}


class TestTheDeskAndTheGateAreOneList:
    def test_every_reason_the_gate_stops_for_has_a_row(self):
        gate = _func(_src("main.gd"), "_execute_end_turn")
        readers = {name for name, _reader in today.READERS}
        for predicate, reader in GATE_REASONS.items():
            assert predicate in gate, predicate
            assert reader in readers, reader
        # … and the gate asks nothing this table does not name
        asked = set(re.findall(r"\b(_\w+_stands)\(\)", gate)) | set(re.findall(r"\b(_treasury_goes_negative)\(\)", gate))
        assert asked == {"_army_warning_stands", "_ic_danger_warning_stands", "_ic_strike_warning_stands",
                         "_day_warning_stands", "_pw_take_warning_stands", "_ui5_idle_warning_stands",
                         "_treasury_goes_negative"}
        assert gate.count("_show_lapse_confirmation()") == 6

    def test_the_idle_reading_is_the_client_s_own(self, world):
        """`today.is_idle` and `main.gd::_idle_marshals` name the same corps: the client's
        predicate, replayed over the board the server sends."""
        client_idle = _func(_src("main.gd"), "_idle_marshals")
        for key in ("in_strategic_mode", "strategic_command_type", "fortified", "drilling",
                    "drilling_locked", "square_formation"):
            assert f'"{key}"' in client_idle, key
        world.marshals["Davout"].fortified = True
        world.marshals["Lannes"].drilling = True
        summary = world.get_filtered_game_state_summary()
        mirrored = []
        for region in summary["map_data"].values():
            for row in region.get("marshals") or []:
                state = row.get("tactical_state")
                if not isinstance(state, dict) or int(row.get("strength", 0) or 0) <= 0:
                    continue
                if state.get("in_strategic_mode") or state.get("strategic_command_type"):
                    continue
                if state.get("fortified") or state.get("drilling") or state.get("drilling_locked") \
                        or state.get("square_formation"):
                    continue
                mirrored.append(str(row.get("name")))
        assert sorted(m.name for m in today.idle_corps(world)) == sorted(mirrored)
        assert "Davout" not in mirrored and "Lannes" not in mirrored and "Ney" in mirrored

    def test_the_takers_are_the_client_s_own(self, world):
        takers = _func(_src("main.gd"), "_pw_takers")
        assert 'bool(stands.get("ok", false))' in takers
        assert 'bool(stands.get("open", false)) or code == "fort"' in takers
        warning = _func(_src("main.gd"), "_pw_take_warning_stands")
        assert "int(actions_remaining) > 0" in warning
        source = (REPO / "backend" / "game_logic" / "today.py").read_text(encoding="utf-8")
        body = source[source.index("def takers("):source.index("def _rows_take(")]
        assert 'stands.get("ok")' in body and 'stands.get("open") or code == "fort"' in body
        assert '"actions_remaining", 0) or 0) <= 0' in body


# ═════════════════════════════════════════════════════════════════════════════
# 7. The review's cases — long names, the other faces of THE PEACE and THE WAR,
#    stub boards, the list's cap
# ═════════════════════════════════════════════════════════════════════════════

class TestTheReviewsCases:
    def test_no_name_however_long_breaks_the_cap(self, world, monkeypatch):
        """Every row is cut to the cap by `_fit` — with the longest names the board could carry."""
        from backend.commands import strategic
        from backend.game_logic import battle_day
        long_man = "Archduke Ferdinand Karl Joseph of Austria-Este"
        long_place = "Mecklenburg-Vorpommern-Strelitz-Schwerin"
        monkeypatch.setattr(today, "humanize_entity_name", lambda name: long_man)
        monkeypatch.setattr(strategic, "pending_marshal_decisions", lambda w: ["Lannes"])
        monkeypatch.setattr(battle_day, "awaiting", lambda w: [
            {"enemy": "Mack", "lead_shown": long_man, "field_shown": long_place, "field": long_place}])
        world.marshals["Murat"].jealousy_autonomous_warned = True
        world.gold = 0
        rows = today.decide(world, {"gold_projected_net": -123_456_789})
        assert len(rows) >= 5
        for row in rows:
            assert 0 < len(row["text"]) <= today.ROW_CAP, (len(row["text"]), row["text"])
            assert not row["text"].endswith((" ", ",", "—")), row["text"]

    def test_the_peace_has_a_sentence_for_every_state_of_the_campaign(self, world, monkeypatch):
        from backend.game_logic import congress, fall
        assert today.peace(world)["tone"] == ""                                   # the count not yet met
        monkeypatch.setattr(congress, "titled", lambda w: {"titled": [], "held": [], "count": 47, "needed": 45})
        met = today.peace(world, {})
        assert met["tone"] == "good" and met["text"].startswith(
            "Win the peace: you hold 47 titled provinces (45 needed) — summon the Congress of Paris")
        monkeypatch.setattr(congress, "record", lambda w: {"status": congress.SITTING})
        assert today.peace(world)["text"] == "The Congress of Paris sits — Europe is answering."
        monkeypatch.setattr(congress, "imperial_peace_signed", lambda w: True)
        assert today.peace(world)["text"] == "The Imperial Peace is signed — the campaign is won."
        # a Fall clock takes the line while it runs: the more urgent truth
        monkeypatch.setattr(fall, "clock_lines", lambda w: [{"clock_line": "Paris falls in 2 turns."}])
        monkeypatch.setattr(fall, "warning_state", lambda w: {"message": "Retake Paris."})
        falling = today.peace(world)
        assert falling == {"text": "Paris falls in 2 turns.", "hint": "Retake Paris.",
                           "door": {"kind": "congress"}, "tone": "bad"}

    def test_the_peace_is_blank_on_a_board_with_no_congress(self, world, monkeypatch):
        from backend.game_logic import congress
        monkeypatch.setattr(congress, "armed", lambda w: False)
        assert today.peace(world) == {"text": "", "hint": "", "door": {}, "tone": ""}
        assert today.desk(world)["peace"]["text"] == ""
        assert "congress" not in _ids(today.decide(world))

    def test_the_war_in_a_truce_and_at_peace(self, world, monkeypatch):
        truce = {"wars": [{"status": "armistice", "opponent": "Austria", "opponent_display": "Austria"}]}
        said = today.war(world, truce)
        assert said["text"] == "No war is being fought — a truce holds with Austria."
        assert said["door"] == {"kind": "war", "opponent": "Austria"} and said["parts"] == []
        monkeypatch.setattr(today, "_pressing_want", lambda w: None)
        assert today.war(world, {"wars": []})["text"] == "At peace."
        monkeypatch.setattr(today, "_pressing_want", lambda w: {
            "text": "Prussia wants the Hanoverian Prize.", "door": {"kind": "court", "nation": "Prussia"}})
        at_peace = today.war(world, {"wars": []})
        assert at_peace["text"] == "At peace. Prussia wants the Hanoverian Prize."
        assert at_peace["door"] == {"kind": "court", "nation": "Prussia"}

    def test_more_than_two_wars_are_counted(self, world):
        wars = {"wars": [{"status": "war", "opponent": f"Court{i}", "war_title": f"War {i}",
                          "war_roster_display": f"Court{i}", "objective": {"type": "defense"}}
                         for i in range(4)]}
        said = today.war(world, wars)
        assert len(said["parts"]) == today.WARS_SHOWN == 2
        assert said["text"].endswith(" · +2 more.")

    def test_a_board_with_no_player_has_no_desk(self):
        class _Stub:
            player_nation = ""
        assert today.desk(_Stub()) is None
        assert today.desk(None) is None

    def test_the_list_is_capped_and_the_rest_are_counted(self, world, monkeypatch):
        def _many(w, have):
            return [today._row(f"idle{i}", today.TIER_WASTES, f"Matter {i}.", {"kind": "idle"})
                    for i in range(today.MAX_ROWS + 5)]
        monkeypatch.setattr(today, "READERS", [("many", _many)])
        built = today.desk(world)
        assert len(built["decide"]) == today.MAX_ROWS and built["more"] == 5
