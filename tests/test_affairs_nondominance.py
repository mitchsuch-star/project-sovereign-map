"""RE-3 — "Affairs of State": the nondominance pin (`docs/RECURRING_EVENTS_SPEC.md`
§16 "RE-3", the critics' rewrite; §6.1 "each answer the better one
somewhere"; §14 the brakes).

On three boards per template — a hoarder at the golden peace, an expander at
war, a France that has spent its standing — wherever the letter can arrive,
EACH answer is strictly better than the other on at least one delivered axis
(gold, diplomatic points, administrative actions, standing, a court's
goodwill, a client's loyalty, the law), the Decline is free of every purse
(no gold, no DP, no action), no answer carries the alarm, and the letter is
absent where `bites` fails. The figures are `moments.plan`'s own — shown =
applied — read on the staged fixture (`tests/fixtures/affairs_block.json`).
"""
import contextlib
import io
import json
from pathlib import Path

import pytest

import backend.main as M
from backend.game_logic import affairs as AF
from backend.game_logic import moments as MO
from tests import _chip_census as C

REPO = Path(__file__).resolve().parents[1]
FIXTURE = REPO / "tests" / "fixtures" / "affairs_block.json"
T1, T2, T3 = "chancellors_letters", "the_host", "berthiers_memorial"
# RE-H (November 1, 2026): the fourth letter — the Haiti letter (§6.5). Its
# premise held only with the Emperor at home until the user's word of the
# same day ("let Decrès write to headquarters") dropped that clause, so it is
# measured on every board whose premise holds (the Arch-Chancellor's letter
# still skips the hoarder).
H1 = "santo_domingo"
# RE-6 (November 2, 2026): the three offers — the Edicts (§6.2 E1–E3). An
# offer's Accept buys a decree for a term (gold and an action out, the
# decree in); its Decline is empty, so each answer is the better one
# somewhere by construction — pinned here on the boards whose premises
# admit them (E1 at war with corps quartered on Bavaria, E2 while the pool
# sits at the boot's 50 %, E3 at the hoarder's golden peace).
E1, E2, E3 = "the_magazines", "the_remounts", "camps_of_instruction"
# AU-2c (November 4, 2026; AUTHORITY_CURRENCY_SPEC.md §5.4): the two letters
# whose refusal is priced in authority alone — the Bank's Panic (a war that
# outruns the chest) and the Pope's Refusal (the war with Britain, the user's
# word). Armed by the user's "Arm both" (November 5, 2026); the `armed` fixture
# below holds them up whatever the seam's default, as the review record did.
B1, P1 = "the_bank", "the_popes_ports"
TEMPLATES = (T1, T2, T3, H1, E1, E2, E3, B1, P1)
PURSES = ("gold", "dp", "admin")


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


@pytest.fixture(autouse=True)
def _restore_active_world():
    prior = (M.world, M.game_state.get("world"), M.parser)
    yield
    M.world = prior[0]
    M.game_state["world"] = prior[1]
    M.parser = prior[2]


@pytest.fixture
def armed(monkeypatch):
    C.board_env(monkeypatch)
    from backend.game_logic import standing
    monkeypatch.setattr(standing, "letters_armed", lambda *a, **k: True)   # AU-2c, armed Nov 5
    world = M.world
    world.moments = MO.from_block(json.loads(FIXTURE.read_text(encoding="utf-8")))
    return world


# ── the three boards (§16): staged on the booted 1805 world ──────────────────

def _hoarder(world):
    """A hoarder at the golden peace: a full chest, no war, full standing."""
    world.nation_gold["France"] = 40_000
    world.diplomatic_points = 7
    world.admin_actions_remaining = 2
    world.authority_tracker.authority = 100
    for court in list(world.get_active_nations()):
        if court != "France" and world.get_diplomatic_state("France", court) == "WAR":
            world.diplomatic_states[world._make_diplo_key("France", court)] = "PEACE"
    world.invalidate_active_nations_cache()


def _expander(world):
    """An expander at war: the 1805 boot's wars, the Emperor afield at Swabia,
    the chest at the campaign's ordinary level, standing 85."""
    world.nation_gold["France"] = 12_000
    world.diplomatic_points = 4
    world.admin_actions_remaining = 2
    world.marshals["Napoleon"].location = "Swabia"
    world.authority_tracker.authority = 85


def _spent(world):
    """A France that has spent its standing: the Emperor afield, authority 72
    — one point above the floor's room for a −5."""
    world.nation_gold["France"] = 6_000
    world.diplomatic_points = 2
    world.admin_actions_remaining = 1
    world.marshals["Napoleon"].location = "Swabia"
    world.authority_tracker.authority = 72


def _strained(world):
    """AU-2c: a France whose war outruns its chest — the 1805 boot's wars, the
    corps raised 15 % over their muster (the upkeep's surcharge bites), 6,000
    in the chest: the ledger's own forecast Net about −500, the chest gone in
    eleven turns (the Bank's premise, genuinely). Standing 85."""
    world.nation_gold["France"] = 6_000
    world.diplomatic_points = 4
    world.admin_actions_remaining = 2
    for m in world.marshals.values():
        if m.nation == "France" and not getattr(m, "is_sovereign", False):
            m.strength = int(m.strength * 1.15)
    world.authority_tracker.authority = 85


BOARDS = {"hoarder": _hoarder, "expander": _expander, "spent": _spent, "strained": _strained}


def _quarter(world, names=("Ney", "Davout"), region="Swabia"):
    for name in names:
        world.marshals[name].location = region
    # the premises sit behind a per-turn memo on the world object (Rule 8):
    # a board staged after another read on the same turn starts it afresh
    world.__dict__.pop("_affairs_memo", None)


OCC = {
    T1: {"id": "chancellors_letters#1", "lord": "France", "bind": {"region": "Swabia"}, "tier": 1},
    T2: {"id": "the_host#1", "lord": "France", "bind": {"host": "Bavaria"}, "tier": 1},
    T3: {"id": "berthiers_memorial#1", "lord": "France", "bind": {"law": "grand_quartier_general"}, "tier": 1},
    H1: {"id": "santo_domingo#1", "lord": "France", "bind": {"region": "Lorraine", "sovereign": "Napoleon"},
         "tier": 1, "turn": 7},
    E1: {"id": "the_magazines#1", "lord": "France", "bind": {}, "tier": 1, "turn": 7},
    E2: {"id": "the_remounts#1", "lord": "France", "bind": {}, "tier": 1, "turn": 7},
    E3: {"id": "camps_of_instruction#1", "lord": "France", "bind": {}, "tier": 1, "turn": 7},
    B1: {"id": "the_bank#1", "lord": "France", "bind": {}, "tier": 1, "turn": 16},
    P1: {"id": "the_popes_ports#1", "lord": "France", "bind": {}, "tier": 1, "turn": 12},
}


def _delivered(plan):
    """What a plan DELIVERS, per axis — the signed change the world would see
    (a cost is negative). `enact_law` counts the law as one unit gained and
    its price as gold lost."""
    axes = {}
    for row in plan["rows"]:
        if row.get("skip") or row.get("refusal"):
            continue
        op = str(row.get("op"))
        if op in ("gold", "dp", "admin"):
            axes[op] = axes.get(op, 0) - int(row.get("amount", 0) or 0)
        elif op == "authority":
            axes["authority"] = axes.get("authority", 0) - int(row.get("loss", 0) or 0)
        elif op == "relation" and "after" in row:
            axes["relation"] = axes.get("relation", 0) + int(row["after"]) - int(row["before"])
        elif op == "loyalty":
            for court_row in row.get("courts") or []:
                axes["loyalty"] = axes.get("loyalty", 0) + int(court_row["after"]) - int(court_row["before"])
        elif op == "enact_law":
            axes["law"] = axes.get("law", 0) + 1
            from backend.game_logic import reforms
            law = reforms.find_law(plan.get("_world"), "France", str(row.get("law") or "")) or {}
            axes["gold"] = axes.get("gold", 0) - int(law.get("price", 0) or 0)
        elif op == "edict" and row.get("currency") == "authority":
            # AU-3a: the Decree — the same edict, its price authority lost
            axes["edict"] = axes.get("edict", 0) + 1
            axes["authority"] = axes.get("authority", 0) - int(row.get("authority", 0) or 0)
        elif op == "edict":
            # RE-6: the decree is one unit gained for its term; its price gold lost
            axes["edict"] = axes.get("edict", 0) + 1
            axes["gold"] = axes.get("gold", 0) - int(row.get("amount", 0) or 0)
    return axes


def _better_somewhere(a: dict, b: dict) -> bool:
    """`a` is strictly better than `b` on at least one axis (more is better on
    every axis: less gold lost, less standing lost, more goodwill, the law)."""
    return any(a.get(axis, 0) > b.get(axis, 0) for axis in set(a) | set(b))


def _plans(world, template):
    e = MO.entry(world, template)
    accept = MO.plan(world, e, MO.ANSWER_ACCEPT, OCC[template])
    decline = MO.plan(world, e, MO.ANSWER_DECLINE, OCC[template])
    accept["_world"] = decline["_world"] = world
    return e, accept, decline


def _can_arrive(world, template):
    """Where the letter can arrive on this board: its premise holds and, for a
    priced standing, `bites` allows it (the engine's own reads)."""
    e = MO.entry(world, template)
    read = AF.premise_holds(world, e, "France")
    if not read.get("holds"):
        return False
    return AF.bites(world, "France", e, 1)


MEASURED = set()        # (template, board) pairs the pin above read — a pin that skips everywhere pins nothing


class TestEachAnswerIsTheBetterOneSomewhere:
    @pytest.mark.parametrize("board", sorted(BOARDS))
    @pytest.mark.parametrize("template", TEMPLATES)
    def test_on_every_board_where_the_letter_can_arrive(self, armed, board, template):
        BOARDS[board](armed)
        _quarter(armed)
        if not _can_arrive(armed, template):
            pytest.skip(f"{template} cannot arrive on the {board} board (its premise or `bites`)")
        MEASURED.add((template, board))
        _e, accept, decline = _plans(armed, template)
        assert accept["ok"], (template, board, accept["refusal"])
        a, d = _delivered(accept), _delivered(decline)
        assert _better_somewhere(a, d), (template, board, a, d)
        assert _better_somewhere(d, a), (template, board, a, d)

    @pytest.mark.parametrize("template", TEMPLATES)
    def test_the_letter_is_measured_on_at_least_one_board(self, template):
        """Read after the boards above (one module, one worker, file order):
        each template was measured on at least one of the three — the
        Arch-Chancellor on the expander alone (AU-2a: `bites: "floor"`, the
        letter at any standing — but the hoarder keeps the Emperor at home, the
        letter's premise, and the spent board at 72 is under the floor's room
        for a −5), the host on all three (AU-2a, the user's "Clamp it first":
        the Host's Decline −2 clamps at the floor, so the spent board at 72 meets
        the letter and pays 1 of the 2, the rest said — under the AU-2a floor it
        did not arrive there), the door where France is at war with the chest
        above the bar."""
        boards = sorted(b for t, b in MEASURED if t == template)
        assert boards, template
        # AU-2c adds the strained board (a genuine war-time deficit): the Host
        # meets it too (the corps quartered on Bavaria, the clamp at any standing)
        if template == T2:
            assert boards == ["expander", "hoarder", "spent", "strained"]
        if template == T1:
            assert boards == ["expander"]
        # AU-2c: the Bank only where the war outruns the chest — the expander's
        # corps on campaign pay in Swabia (the forecast Net −1,124 on 12,000:
        # ten turns) and the strained board; the Pope on every board at war
        # with Britain above the floor's room for a −5
        if template == B1:
            assert boards == ["expander", "strained"]
        if template == P1:
            assert boards == ["expander", "strained"]


class TestTheThirdAnswerIsTheBetterOneSomewhere:
    """AU-3a (AUTHORITY_CURRENCY_SPEC.md §5.3): the three Edict letters carry a
    third answer, "Decree it" — the same edict paid in authority. Each of the
    three answers is strictly better than each other on one delivered axis:
    the Accept on authority, the Decree on gold, the Decline on both (and the
    action); the two purchases on the edict over the Decline."""

    @pytest.mark.parametrize("board", sorted(BOARDS))
    @pytest.mark.parametrize("template", (E1, E2, E3))
    def test_three_answers_on_every_board_where_the_letter_can_arrive(self, armed, board, template):
        BOARDS[board](armed)
        _quarter(armed)
        if not _can_arrive(armed, template):
            pytest.skip(f"{template} cannot arrive on the {board} board")
        e, accept, decline = _plans(armed, template)
        decree = MO.plan(armed, e, MO.ANSWER_DECREE, OCC[template])
        decree["_world"] = armed
        if not decree["ok"]:
            pytest.skip(f"{template} on the {board} board: the Decree is closed ({decree['refusal']})")
        MEASURED_DECREE.add((template, board))
        plans = {"accept": _delivered(accept), "decree": _delivered(decree), "decline": _delivered(decline)}
        for a in plans:
            for b in plans:
                if a != b:
                    assert _better_somewhere(plans[a], plans[b]), (template, board, a, b, plans)
        assert not [r for r in decree["rows"] if r.get("op") == "gold"], decree["rows"]

    def test_the_decree_is_measured_on_at_least_one_board(self):
        assert {t for t, _b in MEASURED_DECREE} == {E1, E2, E3}, sorted(MEASURED_DECREE)


MEASURED_DECREE = set()     # read in file order, one worker (`--dist loadgroup`)


class TestTheDeclineIsFreeOfEveryPurseAndTheAlarmIsNeverTouched:
    @pytest.mark.parametrize("board", sorted(BOARDS))
    @pytest.mark.parametrize("template", TEMPLATES)
    def test_the_decline_touches_no_purse(self, armed, board, template):
        BOARDS[board](armed)
        _quarter(armed)
        _e, _accept, decline = _plans(armed, template)
        assert not [r for r in decline["rows"] if r.get("op") in PURSES], (template, board)
        assert "alarm" not in {r.get("op") for r in decline["rows"]}

    @pytest.mark.parametrize("template", TEMPLATES)
    def test_no_answer_carries_the_alarm_and_the_threat_is_byte_identical(self, armed, template):
        _expander(armed)
        _quarter(armed)
        e, accept, decline = _plans(armed, template)
        for side in (e["accept"], e["decline"]):
            assert "alarm" not in {op.get("op") for op in side.get("ops") or []}
        before = (dict(getattr(armed, "threat_by_target", {}) or {}),
                  dict(getattr(armed, "threat_sources_this_turn", {}) or {}))
        for plan in (accept, decline):
            if plan["ok"]:
                with _quiet():
                    MO._apply(armed, plan)
        after = (dict(getattr(armed, "threat_by_target", {}) or {}),
                 dict(getattr(armed, "threat_sources_this_turn", {}) or {}))
        assert after == before


class TestTheLetterIsAbsentWhereBitesFails:
    def test_the_arch_chancellor_writes_at_any_standing_but_under_the_floor(self, armed):
        """AU-2a (AUTHORITY_CURRENCY_SPEC.md §5.4, the user's Q3 ruling): the
        Chancellor's letter is authored `bites: "floor"` — it arrives at full
        standing too (the hoarder's bill), and only the floor closes it: the
        Decline's −5 must land whole at or above 71 on the grip."""
        _quarter(armed)
        armed.marshals["Napoleon"].location = "Swabia"
        e = MO.entry(armed, T1)
        assert e.get("bites") == "floor" and e.get("bites_since") == "AU-2a"
        for authority in (100, 99, 80, 76):
            armed.authority_tracker.authority = authority
            assert AF.premise_holds(armed, e, "France")["holds"]
            assert AF.bites(armed, "France", e, 1) is True, authority
        for authority in (75, 71, 60):
            armed.authority_tracker.authority = authority
            assert AF.bites(armed, "France", e, 1) is False, authority

    def test_the_host_clamps_at_the_floor_and_the_door_carries_none(self, armed):
        """AU-2a, the user's "Clamp it first" (November 4, 2026): the Host's
        Complaint prices the Host's Decline (−2 / −3 / −4 by tier) with
        `bites: "clamp"` — the letter arrives at every standing, on the bled
        boards too, and the Decline takes what lies above 71 and says the rest.
        Clamped, it still costs relation and loyalty, so it is never free (the
        validator refuses a clamp on a refusal priced in authority alone). The
        Memorial carries no clause."""
        e = MO.entry(armed, T2)
        assert e.get("bites") == "clamp" and "bites_since" not in e
        for authority in (100, 80, 73, 72, 71, 60, 40):
            armed.authority_tracker.authority = authority
            assert AF.bites(armed, "France", e, 1) is True, authority
        for authority, loss, said in ((100, 2, ""), (72, 1, "only 1 of the 2 is taken"),
                                      (71, 0, "nothing is taken: the floor holds at 71"),
                                      (60, 0, "is under the floor of 71")):
            armed.authority_tracker.authority = authority
            rows = MO.plan(armed, e, MO.ANSWER_DECLINE, OCC[T2])["rows"]
            assert [r["op"] for r in rows] == ["authority", "relation", "loyalty"], authority
            assert rows[0]["loss"] == loss and said in rows[0]["line"], (authority, rows[0])
            assert any(int(r.get("before", 0)) != int(r.get("after", 0)) for r in rows[1:]) \
                or any(c.get("before") != c.get("after") for r in rows[1:] for c in r.get("courts") or []), authority
        armed.authority_tracker.authority = 100
        door = MO.entry(armed, T3)
        assert not door.get("bites")
        assert AF.bites(armed, "France", door, 1) is True

    def test_the_seam_down_reads_the_deck_as_before_au_2a(self, armed, monkeypatch):
        """Arm AUP (`tests/_standing_seams.py`): with `standing.hits_armed` held down
        the Chancellor reads `bites: true` (never at 100) and the Host's Decline
        carries no authority op (the letter always bites)."""
        from backend.game_logic import standing
        monkeypatch.setattr(standing, "hits_armed", lambda *a, **k: False)
        _quarter(armed)
        armed.marshals["Napoleon"].location = "Swabia"
        armed.authority_tracker.authority = 100
        assert AF.bites(armed, "France", MO.entry(armed, T1), 1) is False
        assert AF.bites(armed, "France", MO.entry(armed, T2), 1) is True
        rows = MO.plan(armed, MO.entry(armed, T2), MO.ANSWER_DECLINE, OCC[T2])["rows"]
        assert [r["op"] for r in rows] == ["relation", "loyalty"]
