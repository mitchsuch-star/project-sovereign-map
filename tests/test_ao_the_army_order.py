"""AO — THE ARMY ORDER (Pre-Deploy S13f, October 17, 2026; the record is
`docs/REFORMS_SPEC.md` §5a; the review that opened it is
`docs/audits/COMMAND_FEEL_2026_10_16.md` §10).

The three tiers the user ruled on October 16–17, 2026, pinned on the shipped
1805 boot through the real `POST /command`:

* FOLLOW — "Soult, follow Ney" is a SUPPORT that STANDS: it marches where Ney
  marches and to his guns, and never lapses on "secure" (plain SUPPORT does).
  "follow <enemy>" is the chase (PURSUE). The order serializes.
* THE FAN-OUT — before the Staff, "everyone fortify" / "all marshals march to
  Swabia" goes to every corps in turn, each at its own price, the reply opens
  with the sum against the pool, a refused corps is named, the pool's edge
  names who did not go, and a marshal who objects asks you himself — the
  rest of the order waits behind his question and goes on when he is
  answered (the popup road AND the interrupt road).
* THE ARMY ORDER — with the court's Staff in force a collective standing
  order is ONE order at `ARMY_ORDER_AP`, free for every corps of the Emperor's
  column (within `ARMY_COLUMN_REACH` of the sovereign); a corps beyond is
  named. The authority gate: at 70+ the Staff's order carries every doubt
  (named); 50–69 a doubter refuses the Staff's word and is named; below 50
  the collective falls to the fan-out at each man's price, with the reason.

And what stays as it was: "everyone retreat" is the general retreat,
"everyone attack Mack" is one battle, the stash is never serialized and
never crosses a turn (CR-7-8).
"""

import contextlib
import io

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.commands import executor as executor_mod
from backend.commands import group_orders as G
from backend.commands import objection_v2 as ov2
from backend.commands import strategic_executor as se_mod
from backend.commands.order_quotes import march_quotes_for_region
from backend.commands.strategic import StrategicOrderProcessor
from backend.game_logic import reforms
from backend.models.marshal import StrategicOrder
from tests import _chip_census as C


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


def _post(client, command):
    with _quiet():
        return client.post("/command", json={"command": command}).json()


@pytest.fixture
def client(monkeypatch):
    """A mock-parser 1805 board per test, the mood variance pinned flat (the
    ONE source of randomness in the objection triggers), a fresh game."""
    C.board_env(monkeypatch)
    flat = (lambda concern: concern)
    monkeypatch.setattr(executor_mod, "apply_mood_variance", flat)
    monkeypatch.setattr(se_mod, "apply_mood_variance", flat)
    monkeypatch.setattr(ov2, "apply_mood_variance", flat)
    # An Insist rolls V2b defiance on the process's random stream, which
    # under the parallel hook depends on what ran before on the worker —
    # the roll is pinned to obedience, as test_sr2e does (the defiance
    # machinery is its own slice's pin, not this one's).
    import backend.commands.defiance as DEF
    monkeypatch.setattr(DEF, "calculate_defiance_chance", lambda *a, **k: 0.0)
    c = TestClient(M.app)
    with _quiet():
        c.post("/new_game")
    return c


def _staff_on(world):
    row = next(r for r in reforms.deck(world, world.player_nation) if reforms.is_staff(r))
    row["enacted_turn"] = world.current_turn
    assert reforms.staff_actions(world, world.player_nation) == 1


def _orders(world):
    return {m.name: m.strategic_order for m in world.get_player_marshals()}


def _answer_until_quiet(client, response, *, objection="insist", interrupt="hold_position", limit=12):
    """Answer every question a collective order raises, the way the client
    and the driver do: the popup endpoint for an objection, the interrupt
    endpoint for a first-step contact. Returns the last reply."""
    last = response
    for _ in range(limit):
        if last.get("pending_interrupt"):
            pi = last["pending_interrupt"]
            with _quiet():
                last = client.post("/strategic_response", json={
                    "marshal_name": pi.get("marshal", ""),
                    "response_type": pi.get("interrupt_type", ""),
                    "choice": interrupt}).json()
            continue
        if last.get("pending_objection") or last.get("state") == "awaiting_player_choice" \
                or M.world.pending_objection or M.world.pending_strategic_objection:
            with _quiet():
                last = client.post("/respond_to_objection", json={"choice": objection}).json()
            continue
        break
    return last


# ═══════════════════════════════ FOLLOW ═══════════════════════════════

class TestFollowIsTheSupportThatStands:

    def test_follow_a_friend_stamps_a_standing_support(self, client):
        r = _post(client, "Soult, follow Ney")
        assert r["success"], r["message"]
        order = M.world.get_marshal("Soult").strategic_order
        assert order is not None and order.command_type == "SUPPORT"
        assert order.standing_follow is True
        assert order.target == "Ney"
        assert "follows Ney" in r["message"]
        assert "stands until you cancel it" in r["message"]

    @pytest.mark.parametrize("line", [
        "Lannes, march with Napoleon", "Lannes, keep pace with Napoleon",
        "Lannes, accompany Napoleon", "Lannes, follow Napoleon in and back him up",
    ])
    def test_the_phrasings_of_a_follow(self, client, line):
        r = _post(client, line)
        assert r["success"], (line, r["message"])
        order = M.world.get_marshal("Lannes").strategic_order
        assert order is not None and order.command_type == "SUPPORT" and order.standing_follow, line

    def test_follow_an_enemy_is_the_chase(self, client):
        r = _post(client, "Murat, follow Mack")
        assert r["success"], r["message"]
        order = M.world.get_marshal("Murat").strategic_order
        assert order is not None and order.command_type == "PURSUE" and order.target == "Mack"

    def test_a_plain_support_is_unchanged(self, client):
        r = _post(client, "Soult, support Ney")
        assert r["success"], r["message"]
        order = M.world.get_marshal("Soult").strategic_order
        assert order.command_type == "SUPPORT" and order.standing_follow is False
        assert "moves to support Ney" in r["message"]

    def test_a_follow_never_lapses_on_secure_a_support_does(self, client):
        """Both men at Paris, no enemy near: the support completes "Ney is
        secure", the follow continues — `_execute_support`'s one arm."""
        world = M.world
        ney, soult, davout = (world.get_marshal(n) for n in ("Ney", "Soult", "Davout"))
        for m in (ney, soult, davout):
            m.location = "Paris"
        soult.strategic_order = StrategicOrder(
            command_type="SUPPORT", target="Ney", target_type="marshal",
            started_turn=world.current_turn - 1, original_command="Soult, follow Ney",
            standing_follow=True, issued_turn=world.current_turn - 1)
        davout.strategic_order = StrategicOrder(
            command_type="SUPPORT", target="Ney", target_type="marshal",
            started_turn=world.current_turn - 1, original_command="Davout, support Ney",
            issued_turn=world.current_turn - 1)
        processor = StrategicOrderProcessor(M.executor)
        with _quiet():
            kept = processor._execute_support(soult, world, M.game_state)
            done = processor._execute_support(davout, world, M.game_state)
        assert kept["order_status"] == "continues" and "marches with Ney" in kept["message"]
        assert soult.strategic_order is not None and soult.strategic_order.standing_follow
        assert done["order_status"] in ("completed", "complete") or davout.strategic_order is None

    def test_the_order_serializes_and_a_legacy_save_loads_as_a_support(self):
        order = StrategicOrder(command_type="SUPPORT", target="Ney", target_type="marshal",
                               started_turn=3, original_command="x", standing_follow=True)
        d = order.to_dict()
        assert d["standing_follow"] is True
        assert StrategicOrder.from_dict(d).standing_follow is True
        legacy = {k: v for k, v in d.items() if k != "standing_follow"}
        assert StrategicOrder.from_dict(legacy).standing_follow is False

    def test_the_ledger_and_the_probe_know_the_follow(self, client):
        from backend.game_logic.ledger import _derive_status, _derive_strategic_order_summary
        from backend.commands.state_probe import order_state_refusal
        _post(client, "Soult, follow Ney")
        soult = M.world.get_marshal("Soult")
        assert _derive_status(soult) == "following"
        assert _derive_strategic_order_summary(soult).startswith("Follow Ney")
        assert order_state_refusal(M.world, M.world.get_marshal("Davout"), "follow") == ""


# ═══════════════════════════════ THE FAN-OUT ═══════════════════════════════

class TestTheFanOut:

    def test_everyone_fortify_goes_corps_by_corps_and_waits_behind_an_objection(self, client):
        world = M.world
        r = _post(client, "everyone fortify")
        assert r["success"], r["message"]
        assert "corps by corps" in r["message"]
        # Ney (aggressive) objects to digging in beside Mack; the rest wait.
        assert r.get("pending_objection") or r.get("state") == "awaiting_player_choice", r["message"]
        assert world._pending_group is not None
        assert "waits for" in r["message"] and "behind Ney's question" in r["message"]
        with _quiet():
            a = client.post("/respond_to_objection", json={"choice": "insist"}).json()
        assert "The order goes on." in a["message"], a["message"]
        assert world.get_marshal("Davout").fortified, a["message"]
        assert "Nothing left for" in a["message"]
        assert world._pending_group is None
        assert world.actions_remaining == 0

    def test_the_general_retreat_and_the_single_battle_are_untouched(self, client):
        r = _post(client, "everyone retreat")
        assert r["success"] and "General retreat" in r["message"], r["message"]
        with _quiet():
            client.post("/new_game")
        r = _post(client, "everyone attack Mack")
        assert "corps by corps" not in str(r.get("message")), r["message"]

    def test_a_collective_march_waits_behind_the_first_steps_interrupt_and_goes_on(self, client):
        world = M.world
        r = _post(client, "all marshals march to Swabia")
        assert "corps by corps" in r["message"] and "14 actions for the 4 in hand" in r["message"]
        assert "With the Grand Quartier" in r["message"]   # the Staff hint, pre-reform
        assert r.get("pending_interrupt"), r["message"]
        pi = r["pending_interrupt"]
        with _quiet():
            a = client.post("/strategic_response", json={
                "marshal_name": pi.get("marshal", ""), "response_type": pi.get("interrupt_type", ""),
                "choice": "hold_position"}).json()
        # The order went on past Ney's answer — and Davout (cautious) asks next.
        assert "The order goes on." in a["message"], a["message"]
        assert "behind Davout's question" in a["message"], a["message"]
        last = _answer_until_quiet(client, a)
        assert world._pending_group is None, last["message"]
        # Swabia is Mack's: every corps that reaches it meets him and asks or
        # halts; the order still went to every man the pool could pay for,
        # and named the rest for tomorrow.
        assert "Nothing left for" in last["message"], last["message"]
        assert world.actions_remaining < 4

    def test_the_stash_never_serializes_and_never_crosses_a_turn(self, client):
        world = M.world
        _post(client, "everyone fortify")
        assert world._pending_group is not None
        assert "_pending_group" not in world.to_dict()
        with _quiet():
            client.post("/respond_to_objection", json={"choice": "cancel"})
        # Cancel answered the question; whatever is left is let go at the boundary.
        world._pending_group = {"turn": world.current_turn, "members": ["Davout"], "rest": "fortify",
                                "action": "fortify", "lines": [], "events": []}
        _post(client, "end turn")
        assert world._pending_group is None


# ═══════════════════════════════ THE ARMY ORDER ═══════════════════════════════

class TestTheArmyOrder:

    def test_without_the_staff_the_army_is_the_fan_out(self, client):
        r = _post(client, "the army marches on Munich")
        assert "corps by corps" in r["message"] and "Grand Quartier" in r["message"]

    def test_with_the_staff_the_army_marches_as_one_at_the_staffs_price(self, client):
        world = M.world
        _staff_on(world)
        before = world.actions_remaining
        r = _post(client, "the army marches on Munich")
        assert r["success"], r["message"]
        assert r["message"].startswith("The Grand Quartier"), r["message"]
        assert world.actions_remaining == before - G.ARMY_ORDER_AP
        assert "beyond the emperor's reach" in r["message"].lower() and "Massena" in r["message"]
        orders = _orders(world)
        assert orders["Massena"] is None
        # Ney's first step met Mack and asked (a contact is a question of the
        # field, never an objection); every other corps of the column marches
        # free, without a word — the Staff's order carries.
        if r.get("pending_interrupt"):
            pi = r["pending_interrupt"]
            with _quiet():
                a = client.post("/strategic_response", json={
                    "marshal_name": pi.get("marshal", ""), "response_type": pi.get("interrupt_type", ""),
                    "choice": "hold_position"}).json()
            assert "The order goes on." in a["message"], a["message"]
            assert not a.get("pending_objection") and not world.pending_strategic_objection, a["message"]
            last = _answer_until_quiet(client, a)
            assert world._pending_group is None, last["message"]
        orders = _orders(world)
        # Every corps of the column took the order; the ones whose own first
        # step met Mack answered "hold" above and stand (their order ended by
        # their own answer, not by the gate). At least four march on.
        marching = [n for n, o in orders.items() if o is not None and o.command_type == "MOVE_TO"]
        assert len(marching) >= 4 and "Massena" not in marching, \
            {n: (o.command_type if o else None) for n, o in orders.items()}
        assert world.actions_remaining == before - G.ARMY_ORDER_AP

    def test_at_seventy_the_staffs_order_carries_every_doubt(self, client):
        world = M.world
        _staff_on(world)
        world.authority_tracker.authority = 100
        r = _post(client, "everyone follow Napoleon")
        assert r["success"] and r["message"].startswith("The Grand Quartier"), r["message"]
        assert not r.get("pending_objection") and not r.get("pending_strategic_objection")
        orders = _orders(world)
        followers = [n for n, o in orders.items() if o is not None and o.command_type == "SUPPORT" and o.standing_follow]
        assert "Bernadotte" in followers and "Ney" in followers, followers
        assert "the Staff's order carries" in r["message"]
        assert world.actions_remaining == 4 - G.ARMY_ORDER_AP

    def test_between_fifty_and_seventy_a_doubter_refuses_the_staffs_word(self, client):
        world = M.world
        _staff_on(world)
        world.authority_tracker.authority = 60
        r = _post(client, "everyone follow Napoleon")
        assert r["success"] and r["message"].startswith("The Grand Quartier"), r["message"]
        assert "will not march on the Staff's word" in r["message"]
        orders = _orders(world)
        assert orders["Bernadotte"] is None
        assert orders["Ney"] is not None and orders["Ney"].standing_follow
        assert world.actions_remaining == 4 - G.ARMY_ORDER_AP

    def test_below_fifty_there_is_no_army_order(self, client):
        world = M.world
        _staff_on(world)
        world.authority_tracker.authority = 40
        r = _post(client, "all corps march to Swabia")
        assert "corps by corps" in r["message"] and "would not carry" in r["message"], r["message"]
        assert "authority 40" in r["message"]

    def test_no_emperor_in_the_field_no_army_order(self, client):
        world = M.world
        _staff_on(world)
        world.get_marshal("Napoleon").captured_by = "Austria"
        r = _post(client, "everyone march to Munich")
        assert "corps by corps" in r["message"] and "no Emperor" in r["message"], r["message"]

    def test_tactical_verbs_stay_each_corps_own_labour(self, client):
        world = M.world
        _staff_on(world)
        r = _post(client, "everyone fortify")
        assert "corps by corps" in r["message"] and not r["message"].startswith("The Grand Quartier")


# ═══════════════════════════════ THE QUOTES ═══════════════════════════════

class TestTheQuotes:

    def test_the_army_row_names_the_reform_until_it_is_in_force(self, client):
        q = march_quotes_for_region(M.world, "Munich")
        assert q["army"]["ok"] is False and "Grand Quartier" in q["army"]["refusal"]
        assert q["army"]["command"] == "the army, march to Munich"
        _staff_on(M.world)
        q = march_quotes_for_region(M.world, "Munich")
        a = q["army"]
        assert a["ok"] is True and a["ap"] == G.ARMY_ORDER_AP
        assert "Massena" in a["beyond"] and len(a["corps"]) >= 5
        assert all(c["marshal"] != "Massena" for c in a["corps"])

    def test_the_follow_rows_stand_where_a_corps_of_ours_stands(self, client):
        q = march_quotes_for_region(M.world, "Rhineland")   # Ney and Davout at boot
        allies = {row["ally"] for row in q["follow"]}
        assert {"Ney", "Davout"} <= allies
        row = next(r for r in q["follow"] if r["ally"] == "Ney")
        soult = next(x for x in row["quotes"] if x["marshal"] == "Soult")
        assert soult["command"] == "Soult, follow Ney" and soult["kind"] == "follow"
        # The quote's price is the executor's: send it and compare.
        before = M.world.actions_remaining
        r = _post(client, soult["command"])
        assert r["success"] == soult["ok"], r["message"]
        assert before - M.world.actions_remaining == soult["ap"]

    def test_the_route_is_read_only_and_carries_the_rows(self, client):
        snap = M.world.to_dict()
        with _quiet():
            r = client.get("/march_quotes", params={"region": "Munich"}).json()
        assert {"army", "follow"} <= set(r) and M.world.to_dict() == snap
