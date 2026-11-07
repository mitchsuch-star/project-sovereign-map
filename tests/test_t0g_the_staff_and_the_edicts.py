"""T0-G "the Staff and the Edicts" — the seventh slice of Tier 0 of the
November 6, 2026 whole-game review (`docs/audits/GAME_REVIEW_2026_11_06.md`
§4.1 #12; `BUG_FIXES.md` §GR GR-47, GR-15, GR-46; the rules
`SYSTEMS_REFERENCE.md` §182).

GR-47 — the save-for-the-Staff rule had no reachability guard: a court in
the band [half the Staff's price, an unreachable bar) enacted NOTHING for
the rest of the game (Prussia and Russia on every seed). The rung saves only
for a Staff its chest can reach now — `staff_is_reachable`, the purse
ceiling (the Charges' fixed point) against `_purse_bar` — else it buys what
it can afford. ONE saving predicate, `ai_is_saving_for_the_staff`. Seam:
`the_staff_must_be_reachable`.
GR-15 — the AI's edict rung ignored the save and drained the chest the
Staff needs. `find_ai_edict` reads the same predicate now: a saving court's
gold is the Staff's, the authority Decree stays open. Seam:
`edicts_respect_the_save`.
GR-46 — DOCTRINES_SPEC T8's re-measure is the probe's, not a unit pin:
`tools/_sr7d_t8_probe.py` → `tools/_sr7d_t8_probe.json`, before and after
this slice (the record in `SYSTEMS_REFERENCE.md` §182).

The counsel sibling (Rule 10): `counsel._law_terms` reads the same guard —
never "save for the Staff" toward a bar the ceiling cannot stand at — while
keeping its own lever semantics.
"""
from __future__ import annotations

import contextlib
import io
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

import backend.main as M  # noqa: E402
from backend.ai import counsel as CN  # noqa: E402
from backend.game_logic import affairs as AF  # noqa: E402
from backend.game_logic import ledger as LG  # noqa: E402
from backend.game_logic import moments as MO  # noqa: E402
from backend.game_logic import reforms as RF  # noqa: E402
from backend.models.world_state import WorldState  # noqa: E402
from tests import _chip_census as C  # noqa: E402

SCENARIO = REPO / "godot-client/project-sovereign/assets/maps/europe_1805.json"
FIXTURE = REPO / "tests" / "fixtures" / "affairs_block.json"
E1 = "the_magazines"


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


@pytest.fixture(scope="module")
def _board():
    with _quiet():
        return WorldState.from_scenario(str(SCENARIO)).to_dict()


@pytest.fixture
def world(_board):
    return WorldState.from_dict(_board)


def _russia_in_the_band(world):
    """The GR-47 row's own repro: Russia at turn 20, the Opolchenie and the
    Extraordinary Levy in force, the Staff's bar at 12,750 over a bounded
    ceiling of ~11,740 — the chest can never stand at the bar."""
    world.current_turn = 20
    rows = RF.deck(world, "Russia")
    for law_id in ("opolchenie", "extraordinary_levy"):
        row = next(r for r in rows if r.get("id") == law_id)
        row["enacted_turn"] = 2
        row.setdefault("in_force", True)
    return next(r for r in rows if RF.is_staff(r))


class TestTheStaffMustBeReachable:
    """GR-47."""

    def test_the_band_is_opened(self, world):
        """Russia buys what it can afford at every chest of the row's
        repro, where the pre-fix rung returned None forever."""
        staff = _russia_in_the_band(world)
        assert RF.staff_is_reachable(world, "Russia", staff) is False
        for chest in (6000, 9000, 12000):
            world.nation_gold["Russia"] = chest
            assert RF.ai_is_saving_for_the_staff(world, "Russia", chest) is None
            with _quiet():
                order = RF.find_ai_enactment(world, "Russia", chest, 2)
            assert order == {"action": "enact_law",
                             "target": "arakcheev_artillery"}, (chest, order)

    def test_the_seam_down_restores_the_band(self, world, monkeypatch):
        staff = _russia_in_the_band(world)
        monkeypatch.setattr(RF, "the_staff_must_be_reachable", lambda: False)
        world.nation_gold["Russia"] = 12000
        assert RF.ai_is_saving_for_the_staff(world, "Russia", 12000) is staff
        with _quiet():
            assert RF.find_ai_enactment(world, "Russia", 12000, 2) is None, (
                "the pre-fix band: saving unconditional, nothing enacted")

    def test_under_half_the_price_nobody_saves(self, world):
        _russia_in_the_band(world)
        assert RF.ai_is_saving_for_the_staff(world, "Russia", 3000) is None

    def test_the_ceiling_states_read_as_the_guard_says(self, world, monkeypatch):
        staff = _russia_in_the_band(world)
        bar = RF._purse_bar(world, "Russia", staff)

        def _econ(state, ceiling):
            return lambda w, n, rows=True: {"ceiling": ceiling,
                                            "ceiling_state": state,
                                            "net": 0, "state_charges": 0}

        monkeypatch.setattr(LG, "_build_economy",
                            _econ(LG.CEILING_BOUNDED, bar))
        assert RF.staff_is_reachable(world, "Russia", staff) is True
        monkeypatch.setattr(LG, "_build_economy",
                            _econ(LG.CEILING_BOUNDED, bar - 1))
        assert RF.staff_is_reachable(world, "Russia", staff) is False
        monkeypatch.setattr(LG, "_build_economy",
                            _econ(LG.CEILING_NO_RATE, 0))
        assert RF.staff_is_reachable(world, "Russia", staff) is True
        monkeypatch.setattr(LG, "_build_economy",
                            _econ(LG.CEILING_NO_SURPLUS, 0))
        assert RF.staff_is_reachable(world, "Russia", staff) is False

    def test_a_reachable_staff_still_holds_the_cheaper_laws(self, world, monkeypatch):
        """The DC-2 rule is kept where it worked: ceiling at the bar, the
        court past half the price — saving, nothing cheaper enacted."""
        staff = _russia_in_the_band(world)
        bar = RF._purse_bar(world, "Russia", staff)
        monkeypatch.setattr(
            LG, "_build_economy",
            lambda w, n, rows=True: {"ceiling": bar, "ceiling_state":
                                     LG.CEILING_BOUNDED, "net": 500,
                                     "state_charges": 0})
        world.nation_gold["Russia"] = 6000
        assert RF.ai_is_saving_for_the_staff(world, "Russia", 6000) is staff
        with _quiet():
            assert RF.find_ai_enactment(world, "Russia", 6000, 2) is None


class TestTheEdictsRespectTheSave:
    """GR-15 — on the affairs fixture board (`test_affairs_edicts`'s own
    staging: the Magazines' storm premise against Austria at turn 8)."""

    @pytest.fixture(autouse=True)
    def _restore_active_world(self):
        prior = (M.world, M.game_state.get("world"), M.parser)
        yield
        M.world = prior[0]
        M.game_state["world"] = prior[1]
        M.parser = prior[2]

    @pytest.fixture
    def armed(self, monkeypatch):
        C.board_env(monkeypatch)
        world = M.world
        world.moments = MO.from_block(
            json.loads(FIXTURE.read_text(encoding="utf-8")))
        world.__dict__.pop("_affairs_memo", None)
        world.current_turn = 8
        world.invalidate_active_nations_cache()
        world.war_intents["Prussia"] = {
            "coveter": "Prussia", "target": "Austria",
            "design_id": "silesia", "foregrounded": True,
            "foregrounded_turn": 5}
        return world

    def test_a_court_not_saving_decrees_in_gold(self, armed, monkeypatch):
        monkeypatch.setattr(RF, "ai_is_saving_for_the_staff",
                            lambda w, n, t: None)
        with _quiet():
            order = AF.find_ai_edict(armed, "Austria", 18_500, 2)
        assert order == {"action": "decree_edict", "target": E1}, order

    def test_a_saving_court_holds_its_gold(self, armed, monkeypatch):
        """The gold arm is held; the Decree in authority alone may go out
        (the chest the Staff needs is untouched either way)."""
        monkeypatch.setattr(RF, "ai_is_saving_for_the_staff",
                            lambda w, n, t: {"id": "the_staff"})
        with _quiet():
            order = AF.find_ai_edict(armed, "Austria", 18_500, 2)
        assert order is None or order.get("currency") == "authority", order

    def test_the_seam_down_restores_the_spend(self, armed, monkeypatch):
        monkeypatch.setattr(RF, "ai_is_saving_for_the_staff",
                            lambda w, n, t: {"id": "the_staff"})
        monkeypatch.setattr(AF, "edicts_respect_the_save", lambda: False)
        with _quiet():
            order = AF.find_ai_edict(armed, "Austria", 18_500, 2)
        assert order == {"action": "decree_edict", "target": E1}, (
            "the pre-fix spend")

    def test_the_rung_reads_the_laws_rungs_own_predicate(self, armed, monkeypatch):
        """One reading: whatever `ai_is_saving_for_the_staff` says, the
        edict rung agrees — no second copy of the saving rule."""
        calls = []
        real = RF.ai_is_saving_for_the_staff

        def _spy(w, n, t):
            out = real(w, n, t)
            calls.append((n, int(t), out is not None))
            return out

        monkeypatch.setattr(RF, "ai_is_saving_for_the_staff", _spy)
        with _quiet():
            AF.find_ai_edict(armed, "Austria", 18_500, 2)
        assert calls and calls[0][0] == "Austria" and calls[0][1] == 18_500


class TestTheCounselSibling:
    """GR-47's sibling (Rule 10): the player's hint never says "save" for
    an unreachable Staff."""

    def test_the_hint_reads_the_guard(self, world, monkeypatch):
        world.nation_gold[world.player_nation] = 6000
        from backend.game_logic.instruments import purse_of
        chest = int(purse_of(world, world.player_nation)[1])
        rows = [r for r in RF.deck(world, world.player_nation)
                if isinstance(r, dict)]
        staff = next((r for r in rows
                      if RF.is_staff(r) and not RF.is_in_force(r)), None)
        if staff is None or chest < int(staff.get("price", 0) or 0) * RF.AI_SAVES_FOR_THE_STAFF_FROM:
            pytest.skip("the board does not put France in the saving band")
        monkeypatch.setattr(RF, "staff_is_reachable", lambda w, n, s: True)
        with _quiet():
            saving_hint = CN._law_terms(world, world.player_nation)
        monkeypatch.setattr(RF, "staff_is_reachable", lambda w, n, s: False)
        with _quiet():
            open_hint = CN._law_terms(world, world.player_nation)
        # reachable: the hint holds the cheaper laws for the Staff (the
        # Staff itself, or nothing while the purse refuses it);
        # unreachable: the first affordable law is named instead.
        assert saving_hint is None or saving_hint.startswith("enact the Staff")
        assert open_hint is not None and not open_hint.startswith(
            "enact the Staff"), open_hint
