"""Row CC, CC-5 "The war table" — Pre-Deploy S13c part 3, October 18, 2026
(plan `~/.claude/plans/sorted-yawning-clover.md` §CC-5).

Every standing order of ours is drawn on the map as a dashed arrow along the
road it has still to walk, with its clock; a click on an arrow opens a card —
[Cancel] through the existing POST /cancel_order, [Change] selects him. `.`
walks the corps with nothing to do. Ctrl-click gathers a group; a province
click opens ONE card with a line per corps, the actions summed against the
pool, and Send goes corps by corps down the typed road, stopping at the first
question or refusal.

RE-SEATED by row IC, the directive (November 19, 2026): the group card's
sequencer is gone. A province click with a group held opens the LIST — ONE
read-only GET (`/directive_quote`, `click=1`: each man's own click order) —
and Give is ONE request (`/command` with `members` and `expect_ap`), one
Take-back unit; the server stops the run at the first question and names who
waits, and a list that no longer holds is drawn again with nothing spent.

The pins:

* THE REMAINING ROAD rides the player-only `tactical_state` (`order_road`,
  `strategic.standing_order_road`) — derived from the order itself (no save
  field, no pathfinding: Rule 8) — and ONLY our corps carry it (the fog
  boundary; sensitive: an enemy given a standing order by hand at full sight
  carries nothing).
* THE ARROW IS THE CARD'S ROAD: a quoted march, sent, stands as an order
  whose remaining road and clock are the quote's (the road past the first
  step taken at once, the turns equal) — so what the card said is what the
  map then draws.
* CC-X14 — a LITERAL man meeting a corps we see on his first step goes
  round him (the executor's own arm); the quote and the reach now say so,
  fog-honestly. CC-2's drift census is byte-identical (the cells are judged
  on what was spent and taken, never the road).
* CC-X16 — the province he stands in at the road's head (a victory's
  advance) is no step left: the Orders tab, the morning dispatch, the desk
  and the relay count the arrow's road.
* THE GROUP'S QUOTES (`GET /march_quotes?marshals=…&dest=…`) are each
  member's own `march_quote`; read-only.
* THE NAMED LIST WAS CQ-8's RELAY, NOT THE FAN-OUT — verified at the part's
  head: `Ney, Davout and Soult, fortify` spent Ney's order only (the second
  name relayed for the seal, never spent), so the group card's Send was a
  sequencer (`SYSTEMS_REFERENCE.md` §129). Row IC turned the seam
  (`directive.a_named_list_is_one_directive`): the named list is now one
  order to every man named (§230); the relay's rule is pinned with it down.
* THE CLIENT, DRIVEN (`tools/cc_client_harness.gd`): an arrow for every
  standing order and none for an enemy, the arrow card's Cancel through
  `/cancel_order` and its Change selecting him, the idle cycle skipping the
  busy, the group's list, its sum and its one Give. SKIPS when the engine is
  absent — and a skip is not a pass.
"""

import contextlib
import io
import json
import os
import random
import re
import subprocess

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.commands import executor as executor_mod
from backend.commands import objection_v2 as ov2
from backend.commands import relay as R
from backend.commands import strategic as S
from backend.commands import strategic_executor as se_mod
from backend.commands.order_quotes import (
    group_march_quotes, literal_detour, march_quote, march_reach,
)
from backend.display_names import humanize_entity_name
from backend.game_logic import ledger as L
from backend.models.intel import FULL, LAST_KNOWN
from backend.models.marshal import StrategicOrder
from tests import _chip_census as C

REPO = C.REPO
PROJECT = C.PROJECT
HARNESS = REPO / "tools" / "cc_client_harness.gd"
MAIN_GD = PROJECT / "scripts" / "main.gd"
MAP_GD = PROJECT / "scenes" / "map_renderer_base.gd"
CARD_GD = PROJECT / "scripts" / "order_confirm_card.gd"
LAYER_GD = PROJECT / "scenes" / "map_order_layer.gd"
LEDGER_GD = PROJECT / "scripts" / "strategic_ledger.gd"


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


def _src(path):
    return path.read_text(encoding="utf-8")


def _func(src, name):
    start = src.index(f"func {name}(")
    nxt = src.find("\nfunc ", start + 1)
    return src[start:] if nxt < 0 else src[start:nxt]


def _flat(mp):
    """The mood variance pinned flat — the ONE source of randomness in the
    objection triggers (CC-2's board)."""
    def flat(concern):
        return concern
    mp.setattr(executor_mod, "apply_mood_variance", flat)
    mp.setattr(se_mod, "apply_mood_variance", flat)
    mp.setattr(ov2, "apply_mood_variance", flat)


@pytest.fixture
def client(monkeypatch):
    C.board_env(monkeypatch)
    _flat(monkeypatch)
    return TestClient(M.app)


def _post(client, command):
    with _quiet():
        return client.post("/command", json={"command": command}).json()


def _game_state(client):
    with _quiet():
        return client.get("/test").json()["game_state"]


def _own_rows(gs):
    """{key: marshal entry} for every corps of ours on the map."""
    out = {}
    for region, row in gs["map_data"].items():
        for m in row.get("marshals", []):
            if m.get("nation") == gs["player_nation"]:
                out[m["name"]] = dict(m, location=region)
    return out


def _field(world):
    return [m for m in world.get_player_marshals()
            if int(m.strength or 0) > 0 and not getattr(m, "captured_by", "")]


# ═══ the remaining road ═════════════════════════════════════════════════════

class TestTheRemainingRoad:

    def test_only_our_corps_carry_it(self, client):
        """The fog boundary: `order_road` lives in `tactical_state`, which no
        foreign corps carries — not even one given a standing order by hand
        and standing in full sight (the sensitivity arm)."""
        C.boot()
        _post(client, "Davout, hold Rhineland")
        w = M.world
        foe = next(e for e in w.marshals.values()
                   if e.nation != w.player_nation and int(e.strength or 0) > 0
                   and w.is_at_war(w.player_nation, e.nation))
        w.get_region_intel(foe.location).visibility = FULL
        foe.strategic_order = StrategicOrder(
            command_type="MOVE_TO", target="Lorraine", target_type="region",
            started_turn=w.current_turn, original_command="(planted)",
            path=["Rhineland", "Lorraine"], issued_turn=w.current_turn)
        gs = _game_state(client)
        seen_foe = False
        for row in gs["map_data"].values():
            for m in row.get("marshals", []):
                if m.get("nation") == gs["player_nation"]:
                    assert isinstance(m["tactical_state"].get("order_road"), dict), m["name"]
                else:
                    seen_foe = seen_foe or m["name"] == foe.name
                    assert "tactical_state" not in m and "order_road" not in json.dumps(m), m["name"]
        assert seen_foe, "the planted foe is not in full sight — the arm is vacuous"
        assert "order_road" not in json.dumps(gs["enemies"])
        rows = _own_rows(gs)
        assert rows["Davout"]["tactical_state"]["order_road"]["kind"] == "hold"
        assert rows["Ney"]["tactical_state"]["order_road"] == {}

    def test_derived_never_saved(self, client):
        C.boot()
        _post(client, "Soult, march to Moravia")
        w = M.world
        assert w.get_marshal("Soult").strategic_order is not None
        assert "order_road" not in json.dumps(w.to_dict(), default=str)

    def test_no_pathfinding_on_the_payload(self, client, monkeypatch):
        """Rule 8: the arrow reads what the order carries — never a road
        search per corps per response."""
        C.boot()
        _post(client, "Soult, march to Moravia")
        w = M.world

        def boom(*a, **k):
            raise AssertionError("the arrow ran a pathfinder")
        for name in ("find_weighted_path", "find_path", "weighted_paths_from"):
            monkeypatch.setattr(type(w), name, boom)
        soult = w.get_marshal("Soult")
        road = S.standing_order_road(w, soult)
        assert road["road"] and road["road"] == S.remaining_road(soult.strategic_order, soult.location)

    def test_the_road_is_the_orders_own(self, client):
        C.boot()
        _post(client, "Soult, march to Moravia")
        _post(client, "Davout, hold Rhineland")
        w = M.world
        gs = _game_state(client)
        rows = _own_rows(gs)
        for key, row in rows.items():
            m = w.get_marshal(key)
            road = row["tactical_state"]["order_road"]
            if m.strategic_order is None:
                assert road == {}, key
                continue
            assert road["road"] == S.remaining_road(m.strategic_order, m.location), key
            assert road["kind"] == S.STANDING_ROAD_KINDS[m.strategic_order.command_type], key
            assert all(isinstance(road[k], int) for k in ("turns", "holds_for", "cancel_ap",
                                                          "cancel_trust")), key
        soult = rows["Soult"]["tactical_state"]["order_road"]
        assert soult["dest"] == "Moravia" and soult["road"][-1] == "Moravia"
        davout = rows["Davout"]["tactical_state"]["order_road"]
        assert davout == dict(davout, kind="hold", road=[], dest="Rhineland", turns=0)

    def test_the_arrow_is_the_cards_road(self, client):
        """A quoted march, sent, stands as an order whose remaining road and
        clock ARE the quote's: the first `range` provinces are taken at once,
        the rest is the arrow, and its turns are the card's turns."""
        C.boot()
        plan = []
        for m in sorted(_field(M.world), key=lambda m: m.name):
            picked = 0
            for dest in sorted(M.world.regions):
                q = march_quote(M.world, m, dest)
                if (q["ok"] and not q["already"] and q["turns"] >= 1 and q["objection"] == "none"
                        and (not q["contact"] or "goes round him" in q["contact"])):
                    plan.append((m.name, dest))
                    picked += 1
                    if picked == 2:
                        break
        assert len(plan) >= 10, plan
        assert any(k == "Soult" for k, _ in plan)
        cells = 0
        for key, dest in plan:
            C.boot()
            w = M.world
            m = w.get_marshal(key)
            q = march_quote(w, m, dest)
            reach = max(1, int(m.movement_range or 1))
            r = _post(client, q["command"])
            assert r.get("success"), (key, dest, r.get("message"))
            road = _own_rows(_game_state(client))[key]["tactical_state"]["order_road"]
            assert road["kind"] == "march", (key, dest)
            assert road["road"] == q["road"][reach:], (key, dest, road["road"], q["road"])
            assert road["turns"] == q["turns"], (key, dest, road["turns"], q["turns"])
            cells += 1
        assert cells == len(plan)

    def test_hold_support_and_follow(self, client):
        C.boot()
        w = M.world
        lannes, murat = w.get_marshal("Lannes"), w.get_marshal("Murat")
        assert lannes.location == murat.location, "the boot board moved: re-pick the pair"
        _post(client, "Lannes, follow Murat")
        _post(client, "Napoleon, support Soult")
        rows = _own_rows(_game_state(client))
        follow = rows["Lannes"]["tactical_state"]["order_road"]
        assert follow["kind"] == "follow" and follow["friend"] == "Murat"
        assert follow["dest"] == murat.location and follow["road"] == []
        support = rows["Napoleon"]["tactical_state"]["order_road"]
        assert support["kind"] == "support" and support["friend"] == "Soult"

    def test_the_cancels_price_and_trust_are_the_cancels_own(self, client):
        """The card says the price before the click: 1 action, and 3 trust
        once he is on the road (nothing on the turn it was given) — the
        executor's own rule (`cancel_trust_change`), read by both."""
        C.boot()
        _post(client, "Soult, march to Moravia")
        w = M.world
        soult = w.get_marshal("Soult")
        road = S.standing_order_road(w, soult)
        assert road["cancel_ap"] == w.get_action_cost("cancel") == 1
        assert road["cancel_trust"] == 0                      # the turn it was given
        soult.strategic_order.started_turn = w.current_turn - 1
        road = S.standing_order_road(w, soult)
        assert road["cancel_trust"] == -3
        trust0, ap0 = soult.trust.value, w.actions_remaining
        with _quiet():
            r = client.post("/cancel_order", json={"marshal": "Soult"}).json()
        assert r["success"] is True
        w = M.world
        assert w.get_marshal("Soult").trust.value - trust0 == road["cancel_trust"]
        assert ap0 - w.actions_remaining == road["cancel_ap"]
        assert w.get_marshal("Soult").strategic_order is None
        rows = _own_rows(r["game_state"])
        assert rows["Soult"]["tactical_state"]["order_road"] == {}


class TestAStaleHeadIsNoStepLeft:
    """CC-X16: the province he stands in at the road's head (a victory's
    advance leaves it there) is no step left — on the arrow, the Orders tab,
    the morning dispatch, the desk and the relay alike."""

    def _stale(self):
        C.boot()
        w = M.world
        ney = w.get_marshal("Ney")
        here = ney.location
        nxt = next(r for r in sorted(w.regions[here].adjacent_regions)
                   if not w.get_enemies_in_region(r, ney.nation))
        far = next(r for r in sorted(w.regions[nxt].adjacent_regions)
                   if r not in (here, nxt) and not w.get_enemies_in_region(r, ney.nation))
        ney.strategic_order = StrategicOrder(
            command_type="MOVE_TO", target=far, target_type="region",
            started_turn=w.current_turn - 1, original_command=f"Ney, march to {far}",
            path=[here, nxt, far], issued_turn=w.current_turn - 1)
        assert ney.in_strategic_mode   # derived from the order
        return w, ney, [nxt, far]

    def test_the_arrow_and_the_one_clock(self, client):
        w, ney, left = self._stale()
        order = ney.strategic_order
        assert S.remaining_road(order, ney.location) == left
        assert S.standing_order_road(w, ney)["turns"] == 2
        # Sensitive: the raw road counts the head.
        assert S.order_turns_remaining(order, w.current_turn, including_current=False,
                                       movement_range=1, before_tick=True) == 3
        assert S.order_turns_remaining(order, w.current_turn, including_current=False,
                                       movement_range=1, before_tick=True,
                                       location=ney.location) == 2

    def test_the_other_surfaces_count_the_same_road(self, client):
        w, ney, left = self._stale()
        with _quiet():
            rows = L.build_strategic_ledger(w)["orders"]
        row = next(r for r in rows if r["marshal"] == "Ney")
        assert row["path_remaining"] == 2 and row["condition"] == "2 regions left"
        assert "(2 turns left)" in L._derive_strategic_order_summary(ney, w.current_turn)
        assert S.order_eta_phrase(ney.strategic_order, w.current_turn,
                                  location=ney.location) == " — 2 turns out"
        assert R._eta_turns(ney, ney.strategic_order, w.current_turn) == 2
        from backend.game_logic import dispatch as D
        with _quiet():
            text = json.dumps(D.build_morning_dispatch(w), ensure_ascii=False)
        assert "2 turns out" in text and "3 turns out" not in text


# ═══ CC-X14 — the literal man goes round ════════════════════════════════════

class TestTheLiteralDetour:

    def test_the_quote_is_the_road_he_walks(self, client):
        """Soult (literal) meets Mack at Swabia on his first step east: the
        executor re-plots the road around him; the quote, the reach and the
        arrow say so."""
        C.boot()
        w = M.world
        soult = w.get_marshal("Soult")
        assert soult.personality == "literal"
        q = march_quote(w, soult, "Moravia")
        assert "goes round him" in q["contact"] and "Swabia" in q["contact"]
        assert "halts at the approach" not in q["contact"]
        assert "Swabia" not in q["road"]
        row = march_reach(w, soult)["reach"]["Moravia"]
        assert row["road"] == q["road"] and row["turns"] == q["turns"]
        r = _post(client, q["command"])
        w = M.world
        soult = w.get_marshal("Soult")
        assert r.get("success") and soult.location == q["road"][0]
        assert soult.strategic_order.path == q["road"][1:]

    def test_on_the_destination_he_halts_at_the_approach(self, client):
        C.boot()
        w = M.world
        soult = w.get_marshal("Soult")
        held = next(rg for rg in sorted(w.regions[soult.location].adjacent_regions)
                    if w.get_visible_enemies_in_region(rg, w.player_nation))
        assert literal_detour(w, soult, held, "MOVE_TO", held) is None
        q = march_quote(w, soult, held)
        assert "halts at the approach" in q["contact"]

    def test_an_unseen_corps_is_never_named_nor_gone_round(self, client):
        C.boot()
        w = M.world
        soult = w.get_marshal("Soult")
        q = march_quote(w, soult, "Moravia")
        blocked = q["contact"].split(" blocks the road at ")[1].split(" ")[0]
        foe = q["contact"].split(" blocks the road at ")[0]
        w.get_region_intel(blocked).visibility = LAST_KNOWN
        q2 = march_quote(w, soult, "Moravia")
        assert foe not in q2["contact"] + q2["note"]
        assert "goes round" not in q2["contact"]


# ═══ the group's quotes ═════════════════════════════════════════════════════

class TestTheGroupsQuotes:

    def test_each_line_is_the_members_own_march_quote(self, client):
        C.boot()
        w = M.world
        dest = w.get_marshal("Ney").location
        with _quiet():
            r = client.get("/march_quotes", params={"marshals": "Davout,Soult,Ney,Nobody",
                                                    "dest": "Franconia"}).json()
        assert r["success"] is True and r["dest"] == "Franconia"
        assert r["ap_left"] == w.actions_remaining
        assert [q["marshal"] for q in r["quotes"]] == ["Davout", "Soult", "Ney", "Nobody"]
        for q in r["quotes"][:3]:
            assert q == json.loads(json.dumps(march_quote(w, w.get_marshal(q["marshal"]), "Franconia")))
        assert r["quotes"][3]["ok"] is False and "Nobody" in r["quotes"][3]["refusal"]
        with _quiet():
            here = client.get("/march_quotes", params={"marshals": "Ney,Davout",
                                                       "dest": dest}).json()
        assert all(q["ok"] is False and q["refusal"] == f"already at {dest}" and q["here"]
                   for q in here["quotes"])   # Ney and Davout both stand at Rhineland

    def test_the_route_writes_nothing(self, client):
        C.boot()
        w = M.world
        before = json.dumps(w.to_dict(), sort_keys=True, default=str)
        state = random.getstate()
        with _quiet():
            for dest in sorted(w.regions)[:10]:
                client.get("/march_quotes", params={"marshals": "Ney,Davout,Soult,Murat",
                                                    "dest": dest})
        assert random.getstate() == state
        assert json.dumps(M.world.to_dict(), sort_keys=True, default=str) == before

    def test_an_unknown_province_is_refused(self, client):
        C.boot()
        with _quiet():
            r = client.get("/march_quotes", params={"marshals": "Ney", "dest": "Atlantis"}).json()
        assert r["success"] is False

    def test_the_helper_is_the_routes(self, client):
        C.boot()
        w = M.world
        with _quiet():
            r = client.get("/march_quotes", params={"marshals": "Ney,Soult", "dest": "Munich"}).json()
        assert r == json.loads(json.dumps(group_march_quotes(w, ["Ney", "Soult"], "Munich")))


class TestTheNamedListIsCQ8sRelay:
    """Verified at the part's head (the landing record's why): the AO fan-out
    reads the collective words only (`group_orders.collective_head`); a
    named list rides CQ-8's relay — the first man's order is spent, the second
    is handed back for the seal, never spent. So one typed line cannot carry
    the group card's sealed orders, and its Send is the sequencer."""

    def test_only_the_first_named_corps_is_spent(self, client, monkeypatch):
        """The Emperor first (a sovereign never objects, so his order is
        simply spent). RE-SEATED by CC-X17 (S13c part 4, October 19, 2026):
        the relay used to carry ONE tail, "Davout, fortify", and Soult was
        only named; it carries every further name now — each Enter gives the
        first of them his order and hands the rest back. Still never spent.

        Row IC, the directive (November 19, 2026): this is the relay's rule
        with `directive.a_named_list_is_one_directive` DOWN; up — as shipped —
        a named list is one order to every man named (the test below)."""
        from backend.commands import directive as DV
        monkeypatch.setattr(DV, "a_named_list_is_one_directive", lambda: False)
        C.boot()
        r = _post(client, "Napoleon, Davout and Soult, fortify")
        w = M.world
        assert w.get_marshal("Napoleon").fortified is True
        assert w.get_marshal("Davout").fortified is False
        assert w.get_marshal("Soult").fortified is False
        assert r.get("relay_command") == "Davout and Soult, fortify"
        assert "The order goes to the army" not in (r.get("message") or "")
        assert not (r.get("group") or {}).get("members")

    def test_a_named_list_goes_to_every_man_named(self, client):
        """Row IC, the directive: one typed line now carries the whole group's
        orders — the fan-out the collective words take, to the men named."""
        C.boot()
        M.world.actions_remaining = 12
        r = _post(client, "Napoleon, Davout and Soult, fortify")
        w = M.world
        assert all(w.get_marshal(n).fortified for n in ("Napoleon", "Davout", "Soult"))
        assert "relay_command" not in r
        assert "The order goes to Napoleon, Davout and Soult" in (r.get("message") or "")
        assert (r.get("group") or {}).get("members") == ["Napoleon", "Davout", "Soult"]


# ═══ the source pins ════════════════════════════════════════════════════════

class TestTheClientsRoads:

    def test_one_cancel_road(self):
        """The arrow card's [Cancel order] and the Orders tab's Cancel are ONE
        sender (CC-X15): the wire guard, the latch retired, the reply read by
        `_on_command_result` so the map and the actions count follow."""
        src = _src(MAIN_GD)
        body = _func(src, "_send_cancel_order")
        for step in ("if not command_input.editable:", "_retire_line_latches()",
                     "set_input_enabled(false)",
                     "api_client.cancel_strategic_order(marshal_key, _on_cancel_order_result)"):
            assert step in body, step
        assert body.index("_retire_line_latches()") < body.index("api_client.cancel_strategic_order(")
        assert "_on_command_result(response)" in _func(src, "_on_cancel_order_result")
        assert "_send_cancel_order(marshal_key)" in _func(src, "_on_standing_cancel_requested")
        assert "_send_cancel_order(marshal_key)" in _func(src, "_on_ledger_cancel_requested")
        assert "instance.cancel_order_requested.connect(_on_ledger_cancel_requested)" in src
        ledger = _func(_src(LEDGER_GD), "_on_meta_clicked")
        assert ledger.index("cancel_order_requested.emit(marshal_name)") < ledger.index(
            "_api_client_ref.cancel_strategic_order(marshal_name, _on_cancel_result)")
        assert src.count("api_client.cancel_strategic_order(") == 1

    def test_the_lists_give_goes_down_the_typed_road(self):
        """RE-SEATED by row IC: the group card's sequencer (`_send_group_line`)
        is gone; the list's Give is ONE request down the typed road's steps."""
        src = _src(MAIN_GD)
        body = _func(src, "_send_directive")
        for step in ("if _chip_command_in_flight or not command_input.editable:", "_add_to_history(line)",
                     "_retire_line_latches()", "set_input_enabled(false)", "order_card.close_given()",
                     "api_client.send_directive(line, members, expect_ap, click, _on_directive_result)"):
            assert step in body, step
        assert body.index("_retire_line_latches()") < body.index("api_client.send_directive(")
        # (the review) the card shuts only once the guard has let the Give through
        guard = body.index("if _chip_command_in_flight or not command_input.editable:")
        assert guard < body.index("order_card.close_given()") < body.index("api_client.send_directive(")
        assert "_on_command_result(response)" in _func(src, "_on_directive_result")
        for gone in ("func _send_group_line(", "func _on_group_line_result(", "func _send_group_orders(",
                     "func _finish_group_run(", "func group_run_report("):
            assert gone not in src, gone

    def test_the_arrow_answers_only_an_empty_line(self):
        body = _func(_src(MAIN_GD), "_arrow_may_take_a_click")
        assert 'command_input.text.strip_edges() == ""' in body and "_order_input_ready()" in body
        left = _src(MAP_GD)
        left = left[left.index("elif event.button_index == MOUSE_BUTTON_LEFT:"):]
        left = left[:left.index("elif event.button_index == MOUSE_BUTTON_RIGHT:")]
        # The piece (and the fog chip) wins over an arrow; the arrow is read
        # before the drag and the fleets.
        assert 'if last_click_marshal == "" and last_click_fogged == ""' in left
        assert left.index("order_arrow_clicked.emit(arrow)") < left.index("_arm_piece_drag(event)")

    def test_the_period_key_at_its_three_doors(self):
        src = _src(MAIN_GD)
        assert "KEY_PERIOD:" in _func(src, "_alt_game_key")
        assert "_cycle_idle_marshal()" in _func(src, "_on_command_input_gui_input")
        assert "event.keycode == KEY_PERIOD" in _func(src, "_unhandled_input")

    def test_the_help_and_the_school_teach_it(self):
        src = _src(MAIN_GD)
        assert "The war table: every standing order is an arrow" in _func(src, "_print_boot_help")
        school = _src(PROJECT / "scripts" / "tutorial_overlay.gd")
        assert "ARROW along the road still to march" in school
        assert "[color=#e8d4a8].[/color] finds your next marshal with nothing to do" in school
        readme = (REPO / "deploy" / "README_TESTER.txt").read_text(encoding="utf-8")
        assert ". / Alt+. — The next marshal with nothing to do" in readme
        assert "Every standing order is drawn as a dashed arrow" in readme
        typed = (REPO / "backend" / "commands" / "meta_executor.py").read_text(encoding="utf-8")
        assert "E end turn | Tab terminal | . next marshal with nothing to do" in typed
        assert "every standing order is an arrow - click it to" in typed


# ═══ the client, driven ═════════════════════════════════════════════════════

_TABLE = ("Soult, march to Moravia", "Davout, hold Rhineland", "Lannes, follow Murat")


def _table(client, *, cancels=0):
    """The war table's board: a march, a hold and a follow standing; Massena
    fortified and Bernadotte drilling (busy without an order); the pool
    refilled; then `cancels` of (Soult, Davout) cancelled through POST
    /cancel_order, in order. Returns the cancel replies."""
    C.boot()
    for line in _TABLE:
        r = _post(client, line)
        assert r.get("success"), (line, r.get("message"))
    w = M.world
    w.get_marshal("Massena").fortified = True
    w.get_marshal("Bernadotte").drilling = True
    w.actions_remaining = 4
    replies = []
    for key in ("Soult", "Davout")[:cancels]:
        with _quiet():
            replies.append(client.post("/cancel_order", json={"marshal": key}).json())
    if cancels:
        M.world.actions_remaining = 4
    return replies


def _idle(gs):
    """The client's rule, read off the board: our corps in the field with no
    standing order and no works, drill or square — in the roster's order."""
    rows = _own_rows(gs)
    out = []
    for key in gs["marshals"]:
        row = rows.get(key)
        if row is None or int(row.get("strength", 0)) <= 0:
            continue
        ts = row["tactical_state"]
        if ts["in_strategic_mode"] or ts["strategic_command_type"]:
            continue
        if ts["fortified"] or ts["drilling"] or ts["drilling_locked"] or ts["square_formation"]:
            continue
        out.append(key)
    return out


def _asks(reply):
    return bool(reply.get("requires_input") or reply.get("pending_objection")
                or reply.get("objection") or reply.get("pending_interrupt"))


def _cc5_block(client):
    _table(client)
    board = _game_state(client)
    with _quiet():
        cancel_reply = client.post("/cancel_order", json={"marshal": "Soult"}).json()
        ledger_reply = client.post("/cancel_order", json={"marshal": "Davout"}).json()
    after = ledger_reply["game_state"]
    idle = _idle(after)
    cc5 = {"board": board, "ap": 4, "march_subject": "Soult", "ledger_subject": "Davout",
           "cancel_reply": cancel_reply, "ledger_reply": ledger_reply, "idle": idle,
           "after_cancels": after}

    # The group: two clean marches beside Ney, whose road meets Mack on its
    # first step (he asks — the question that stops the run). The click road's
    # quotes (row PW: a province next door is the move): the list's own.
    _table(client, cancels=2)
    w = M.world
    others = [k for k in idle if k != "Ney"]
    found = None
    for dest in sorted(w.regions):
        quotes = {k: march_quote(w, w.get_marshal(k), dest, click=True) for k in idle}
        clean = [k for k in others if quotes[k]["ok"] and not quotes[k]["already"]
                 and not quotes[k]["contact"] and quotes[k]["objection"] == "none"
                 and quotes[k]["turns"] >= 1]   # still on the road after the first step
        ney = quotes.get("Ney")
        if (len(clean) >= 2 and ney and ney["ok"] and "asks your orders" in ney["contact"]
                and quotes[clean[0]]["ap"] + ney["ap"] + quotes[clean[1]]["ap"] <= 4):
            found = (dest, clean[0], clean[1])
            break
    assert found is not None, "no province gives two clean marches beside Ney's contact"
    dest, x, y = found
    cc5["toggle_members"] = [x, "Ney", y]

    def line_for(members):
        """The line the client composes for a group sent to `dest`
        (`main.gd::_open_group_card`: the keys as a list, then the march)."""
        return ", ".join(members[:-1]) + " and " + members[-1] + ", march to " + dest

    def listing_for(members):
        """The list the card asks for (`GET /directive_quote`, click=1)."""
        with _quiet():
            reply = client.get("/directive_quote", params={"line": line_for(members), "click": "1"}).json()
        assert reply.get("success"), reply.get("message")
        return reply

    def give(reply):
        """The card's Give with its default ticks: ONE request, the ticked men in
        the list's order and the total the card shows."""
        listing = reply["directive"]
        ticked = [r["marshal"] for r in listing["rows"] if r["ticked"]]
        with _quiet():
            return client.post("/command", json={
                "command": listing["line"], "members": ticked, "expect_ap": listing["total"],
                "click": True, "list_first": True}).json()

    def run(members, before_give=None):
        _table(client, cancels=2)
        q = listing_for(members)
        if before_give is not None:
            before_give()
        return q, give(q)

    # w7 — the real order: X marches, Ney asks; Y waits behind his question.
    q7, r7 = run([x, "Ney", y])
    assert [r["marshal"] for r in q7["directive"]["rows"]] == [x, "Ney", y]
    assert all(r["ticked"] for r in q7["directive"]["rows"])
    assert _asks(r7), ("Ney's march did not ask", r7.get("message"))
    assert M.world.get_marshal(x).strategic_order is not None
    assert M.world.get_marshal(y).strategic_order is None
    cc5["w7"] = {"members": [x, "Ney", y], "dest": dest, "line": line_for([x, "Ney", y]),
                 "quote": q7, "reply": r7, "ap": 4}
    # w8 — the list no longer holds (his works begun since it was drawn): drawn
    # again, nothing spent, nothing sent.
    q8, r8 = run([x, y], before_give=lambda: setattr(M.world.get_marshal(y), "fortified", True))
    assert r8.get("directive_stale") is True and r8.get("directive"), r8.get("message")
    assert M.world.actions_remaining == 4 and M.world.get_marshal(x).strategic_order is None
    cc5["w8"] = {"members": [x, y], "dest": dest, "line": line_for([x, y]), "quote": q8, "reply": r8, "ap": 4}
    # w9 — both go.
    q9, r9 = run([x, y])
    assert r9.get("success") and not _asks(r9), r9.get("message")
    assert all(M.world.get_marshal(k).strategic_order is not None for k in (x, y))
    cc5["w9"] = {"members": [x, y], "dest": dest, "line": line_for([x, y]), "quote": q9, "reply": r9, "ap": 4,
                 "slow": True}   # the harness holds the list past the reading card's wait
    return cc5


@pytest.fixture(scope="module")
def driven(tmp_path_factory):
    exe = C.engine()
    if exe is None:
        pytest.skip("Godot engine not on this machine — the driven pins skip, "
                    "and a skip is not a pass")
    from tests.test_cc_click_and_command import _pick_board
    with pytest.MonkeyPatch.context() as mp:
        C.board_env(mp)
        _flat(mp)
        spec = _pick_board()
        spec["cc5"] = _cc5_block(TestClient(M.app))
    spec["cc5_only"] = True
    work = tmp_path_factory.mktemp("cc5")
    out = work / "out.json"
    log = work / "godot.log"
    spec_path = work / "spec.json"
    spec_path.write_text(json.dumps(dict(spec, out=str(out))), encoding="utf-8")
    env = dict(os.environ, CC_SPEC=str(spec_path))
    proc = subprocess.run(
        [exe, "--headless", "--path", str(PROJECT), "--log-file", str(log),
         "--script", str(HARNESS)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=400, env=env, cwd=str(PROJECT))
    if not out.is_file():
        pytest.fail("the harness wrote no result\n"
                    f"exit={proc.returncode}\nstderr tail:\n{proc.stderr[-2000:]}")
    # UXR3-83 (S15, October 26, 2026): a chip label binds its spaces (U+00A0)
    # in the bbcode; this door reads them as spaces, as the instruments do.
    result = json.loads(out.read_text(encoding="utf-8").replace("\u00a0", " "))
    assert "error" not in result, result.get("error")
    text = log.read_text(encoding="utf-8", errors="replace") if log.is_file() else ""
    result["script_errors"] = text.count("SCRIPT ERROR")
    result["script_error_lines"] = [ln for ln in text.splitlines() if "SCRIPT ERROR" in ln][:5]
    result["spec"] = spec
    return result


def _cc5(driven):
    return driven["spec"]["cc5"]


class TestTheHarnessRanClean:

    def test_no_script_errors(self, driven):
        assert driven["script_errors"] == 0, driven["script_error_lines"]

    def test_the_arrow_clicks_reached_the_map(self, driven):
        assert driven["w2_point"][0] >= 0, "no uncovered point on the march's arrow"
        assert driven["w2_hover"] == _cc5(driven)["march_subject"]


class TestTheArrows:

    def test_an_arrow_for_every_standing_order_of_ours_and_none_for_an_enemy(self, driven):
        cc5 = _cc5(driven)
        rows = _own_rows(cc5["board"])
        standing = sorted(k for k, r in rows.items() if r["tactical_state"]["order_road"])
        assert standing == ["Davout", "Lannes", "Soult"]
        assert driven["w1_arrow_keys"] == standing
        assert not set(driven["w1_arrow_keys"]) & set(cc5["board"]["enemies"])

    def test_each_arrow_is_its_orders_own(self, driven):
        cc5 = _cc5(driven)
        rows = _own_rows(cc5["board"])
        arrows = {a["marshal"]: a for a in driven["w1_arrows"]}
        soult = rows["Soult"]["tactical_state"]["order_road"]
        assert arrows["Soult"]["kind"] == "march" and arrows["Soult"]["anchor"] is False
        assert arrows["Soult"]["points"] == len(soult["road"]) + 1     # his feet, then the road
        assert arrows["Soult"]["label"] == f"{soult['dest']} · {soult['turns']} turns"
        assert arrows["Davout"]["kind"] == "hold" and arrows["Davout"]["anchor"] is True
        assert arrows["Davout"]["label"] == "holds Rhineland"
        assert arrows["Lannes"]["kind"] == "follow" and arrows["Lannes"]["label"] == "follows Murat"
        assert arrows["Lannes"]["points"] == 2                          # a line to the friend's feet


class TestTheArrowCard:

    def test_a_click_opens_the_arrow_face(self, driven):
        cc5 = _cc5(driven)
        soult = _own_rows(cc5["board"])["Soult"]["tactical_state"]["order_road"]
        assert driven["w2_card_open"] is True and driven["w2_card_mode"] == "standing"
        assert driven["w2_card_marshal"] == "Soult" and driven["w2_selected_before"] == ""
        assert driven["w2_title"] == "STANDING ORDER — SOULT"
        assert driven["w2_headline"] == "Soult marches to Moravia"
        assert f"arrives in {soult['turns']} turns" in driven["w2_terms"]
        assert "Road: " + " → ".join(soult["road"]) in driven["w2_terms"]
        assert "Cancelling costs 1 action — no trust lost: it was given this turn." in driven["w2_terms"]
        assert driven["w2_cancel_label"] == "Cancel order  (1 action)"
        assert driven["w2_card_covers_arrow"] is False

    def test_enter_is_change_he_is_selected(self, driven):
        assert driven["w2_selected_after_enter"] == "Soult"
        assert driven["w2_card_open_after_enter"] is False
        assert driven["w2_reach_asked"] == ["march_reach:Soult"]
        assert driven["w2_sends"] == [] and driven["w2_cancels"] == []
        assert driven["w2_arrows_dimmed"] is True      # the selection holds the eye
        assert driven["w2_selected_after_esc"] == ""

    def test_cancel_goes_through_the_cancel_route_and_the_arrow_goes(self, driven):
        cc5 = _cc5(driven)
        assert driven["w3_card_open"] is True
        assert driven["w3_cancels"] == ["cancel:Soult"] and driven["w3_sends"] == []
        assert driven["w3_latch"] is False             # a send retires the armed end turn
        assert driven["w3_input_while_out"] is False   # on the wire like any order
        assert driven["w3_arrow_keys"] == ["Davout", "Lannes"]
        assert driven["w3_ap"] == cc5["cancel_reply"]["action_summary"]["actions_remaining"] == 3
        assert driven["w3_input_after"] is True
        assert "Soult halts his march" in driven["w3_tail"]

    def test_the_orders_tabs_cancel_rides_the_same_road(self, driven):
        """CC-X15: the Orders tab's Cancel retired no latch and refreshed
        nothing but its own book — the map kept the arrow and the actions
        count until the next order."""
        cc5 = _cc5(driven)
        assert driven["w4_cancels"] == ["cancel:Davout"]
        assert driven["w4_latch"] is False
        assert driven["w4_arrow_keys"] == ["Lannes"]
        assert driven["w4_ap"] == cc5["ledger_reply"]["action_summary"]["actions_remaining"]


class TestTheNextIdleMarshal:

    def test_period_walks_the_idle_and_skips_the_busy(self, driven):
        cc5 = _cc5(driven)
        idle = cc5["idle"]
        assert len(idle) >= 3
        for busy in ("Lannes", "Massena", "Bernadotte"):   # a follow, works, a drill
            assert busy not in idle, busy
        assert driven["w5_walk"] == idle + [idle[0]]       # in the roster's order, and it wraps
        assert driven["w5_line"] == ""                     # the key wrote no full stop
        near = [d for d in driven["w5_cam_dist"] if 0.0 <= d < 1.0]
        assert len(near) >= len(idle) - 1, driven["w5_cam_dist"]   # the camera turned to each

    def test_the_bare_key_off_the_line(self, driven):
        idle = _cc5(driven)["idle"]
        assert driven["w5_unfocused"] == idle[1]

    def test_alt_period_over_a_draft_moves_only_the_camera(self, driven):
        assert driven["w5_alt_selected"] == ""
        assert driven["w5_alt_line"] == "Ney, march to "
        assert driven["w5_alt_camera_moved"] is True


class TestTheGroup:

    def test_ctrl_click_gathers_and_lets_go(self, driven):
        members = _cc5(driven)["toggle_members"]
        assert driven["w6_group"] == members and driven["w6_rings"] == 3
        shown = [humanize_entity_name(k) for k in members]
        assert driven["w6_strip"].startswith(", ".join(shown) + " — 3 corps selected")
        assert driven["w6_after_drop"] == [members[0], members[2]]
        assert driven["w6_after_second_drop"] == []          # one left is a selection
        assert driven["w6_selected_after_second_drop"] == members[2]
        assert driven["w6_after_esc"] == [] and driven["w6_selected_after_esc"] == ""

    def test_esc_lets_a_whole_group_go(self, driven):
        assert driven["w6b_after_line_esc"] == []
        assert driven["w6b_after_map_esc"] == []
        assert driven["w6b_pause_open"] is False           # the ladder took ONE step

    def test_one_list_a_row_per_corps_the_sum_against_the_pool(self, driven):
        """Row IC: the province click stands the card at once ("reading") and
        asks ONE read-only GET; the server's list fills it — a row a corps in
        the group's order, ticked while the actions last, the total against
        the actions in hand, and Give."""
        run = _cc5(driven)["w7"]
        listing = run["quote"]["directive"]
        assert driven["w7_card_before_answer"] is False      # it opens once, fully formed (no bob)
        assert driven["w7_card_mode"] == "directive"
        assert driven["w7_asked"] == ["directive_quote:%s|click" % run["line"]]
        rep = driven["w7_report"]
        assert rep["visible"] is True and rep["reading"] is False
        assert rep["title"] == "ORDERS FOR 3 CORPS"
        assert [r["marshal"] for r in rep["rows"]] == [r["marshal"] for r in listing["rows"]] == run["members"]
        assert rep["members"] == [r["marshal"] for r in listing["rows"] if r["ticked"]] == run["members"]
        total = listing["total"]
        assert rep["total"] == total and rep["have"] == 4 and rep["line"] == listing["line"]
        price = f"{total} action{'s' if total != 1 else ''}"
        adds = " + ".join(str(r["ap"]) for r in listing["rows"] if r["ticked"])   # how it adds up
        assert f"Cost: {price} ({adds}) of the 4 in hand — 3 corps go, each by his own order." in rep["total_text"]
        assert rep["give_text"] == "Give the order  (Enter)" and rep["give_disabled"] is False
        for row in rep["rows"]:                              # the row's words, bbcode off
            plain = re.sub(r"\[/?[^\]]+\]", "", row["text"])
            assert plain.startswith(humanize_entity_name(row["marshal"]) + " · "), row
        ney = next(r for r in rep["rows"] if r["marshal"] == "Ney")
        assert "asks your orders" in ney["text"]             # Ney's contact, said before Give

    def test_give_is_one_request_and_a_question_stops_the_rest(self, driven):
        run = _cc5(driven)["w7"]
        listing = run["quote"]["directive"]
        assert driven["w7_given"] == ["directive:%s|%s|%d|click" % (
            listing["line"], ",".join(run["members"]), listing["total"])]
        assert driven["w7_sent"] == []                       # no corps' line sent on its own
        assert driven["w7_input_while_out"] is False         # on the wire like any order
        assert driven["w7_card_while_out"] is False
        assert driven["w7_latch"] is False                   # a send retires the armed end turn
        assert driven["w7_left_on_wire"] == 0
        assert driven["w7_modal"] is True                    # Ney's question stands
        y = humanize_entity_name(run["members"][2])
        assert f"The order waits for {y} behind Ney's question." in driven["w7_tail"]
        assert driven["w7_card_after"] == {}                 # the list given is let go

    def test_a_list_that_no_longer_holds_is_drawn_again_and_nothing_is_spent(self, driven):
        run = _cc5(driven)["w8"]
        y = run["members"][1]
        assert len(driven["w8_given"]) == 1 and driven["w8_sent"] == []
        after = driven["w8_card_after"]
        assert after["visible"] is True and after["mode"] == "directive"
        row = next(r for r in after["rows"] if r["marshal"] == y)
        assert row["ok"] is False and row["ticked"] is False   # he will not go, and why
        assert row["text"] and row["text"] == next(
            r["why"] for r in run["reply"]["directive"]["rows"] if r["marshal"] == y)
        assert "can no longer take this order" in driven["w8_tail"]
        assert "Nothing was sent — here is the list as it stands now." in driven["w8_tail"]
        assert driven["w8_ap_after"] == 4                    # nothing spent

    def test_a_list_slow_to_come_shows_the_reading_card_first(self, driven):
        """Only a list slower than `DIRECTIVE_READING_DELAY_S` stands the card on "reading" first."""
        assert driven["w9_card_before_answer"] is False
        reading = driven["w9_reading"]
        assert reading["visible"] is True and reading["reading"] is True and reading["give_disabled"] is True
        assert driven["w9_report"]["reading"] is False and driven["w9_report"]["members"] == _cc5(driven)["w9"]["members"]

    def test_all_given(self, driven):
        run = _cc5(driven)["w9"]
        assert len(driven["w9_given"]) == 1 and driven["w9_sent"] == []
        names = " and ".join(humanize_entity_name(k) for k in run["members"])
        assert f"The order goes to {names}, corps by corps" in driven["w9_tail"]
        assert driven["w9_modal"] is False

    def test_two_orders_bound_for_one_province_keep_their_badges_apart(self, driven):
        """Both lines march on one province: two arrows end there, and the
        second badge steps beneath the first (it printed on top of it)."""
        run = _cc5(driven)["w9"]
        bound = [lab for lab in driven["w9_arrow_labels"]
                 if lab.split(":", 1)[1].startswith(run["dest"] + " · ")]
        assert len(bound) >= 2, driven["w9_arrow_labels"]
        assert driven["w9_badges_overlap"] is False
