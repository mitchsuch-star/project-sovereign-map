"""SR-5r RF-3 — "The AI enacts" (`docs/REFORMS_SPEC.md` §3, §7, §11 T3; gate
record §0 RULED September 27, 2026 — Q4: both boards, the agendas idiom).

Every AI great power enacts from its own authored deck, in deck order, at the
player's prices, through the SAME verb and the SAME executor (GR5). The rung
(`reforms.find_ai_enactment`, the admin chain's P1.78) takes the first law
`law_refusal` passes with the court's OWN admin budget and whose purse test
passes (`ai_purse_refusal`): the chest keeps a reserve and five turns of the
slate's upkeep, the forecast Net carries the new upkeep, an authority price
never takes the court below 30, and — §3's "the rung weighs it", made TRUE —
never leaves it fewer than 3 diplomatic points a turn. One enactment every
three turns; the AI never repeals. Lever `reforms.THE_AI_ENACTS` — down, no
AI court enacts and the prior BASELINE_SERIES reproduces byte for byte
(`tools/_rf3_series_arms.py`).
"""
import contextlib
import io
import json
from pathlib import Path

import pytest

import backend.main as M
from backend.game_logic import reforms as R
from tests import _chip_census as C

ROOT = Path(__file__).resolve().parents[1]


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


@pytest.fixture(autouse=True)
def _restore_active_world():
    prior = (M.world, M.game_state.get("world"), M.parser)
    yield
    M.world = prior[0]
    M.game_state["world"] = prior[1]
    M.parser = prior[2]


@pytest.fixture
def world(monkeypatch):
    C.board_env(monkeypatch)
    return M.world


@pytest.fixture
def carried(monkeypatch):
    """Hold the court's forecast Net fixed: a test chest large enough to pass
    the bar also raises EB-1's Charges of Empire (they scale with the chest),
    which is the forecast arm's own business — pinned apart."""
    import backend.game_logic.ledger as L
    monkeypatch.setattr(L, "_build_economy",
                        lambda w, n, income_data=None: {"net": 5000})


def rich(world, nation, gold=60000):
    world.nation_gold[nation] = gold
    world.nation_authority[nation] = 60


class TestTheRung:

    def test_the_first_affordable_law_in_deck_order(self, world, carried):
        rich(world, "Austria", 60000)
        order = R.find_ai_enactment(world, "Austria", 60000, 2)
        assert order == {"action": "enact_law", "target": "corps_d_armee"}, order

    def test_the_staff_unaffordable_it_takes_the_next(self, world, carried):
        """The chest (9,500) pays the Staff's price, so `law_refusal` passes
        it — but not the purse bar (9,000 + 1,000 + 5 x 300 = 11,500), so the
        rung walks on to the Landwehr."""
        rich(world, "Austria", 9500)
        assert R.law_refusal(world, "Austria", "corps_d_armee", admin_actions=2) == ""
        order = R.find_ai_enactment(world, "Austria", 9500, 2)
        assert order == {"action": "enact_law", "target": "landwehr"}, order

    def test_never_the_player(self, world, carried):
        world.gold = 60000
        world.nation_gold["France"] = 60000
        assert R.law_refusal(world, "France", "grand_quartier_general",
                             admin_actions=2) == ""
        assert R.find_ai_enactment(world, "France", 60000, 2) is None

    def test_no_admin_action_no_order(self, world, carried):
        """The AI's budget is the one the loop hands in — never the player's
        pool, which holds actions here."""
        rich(world, "Austria")
        world.admin_actions_remaining = 2
        assert R.find_ai_enactment(world, "Austria", 60000, 0) is None
        assert R.find_ai_enactment(world, "Austria", 60000, 1) is not None

    def test_one_enactment_every_three_turns(self, world, carried):
        rich(world, "Austria")
        R.enact_law(world, "Austria", R.find_law(world, "Austria", "corps_d_armee"))
        assert R.find_ai_enactment(world, "Austria", 60000, 2) is None
        world.current_turn += R.AI_ENACTMENT_EVERY_TURNS - 1
        assert R.find_ai_enactment(world, "Austria", 60000, 2) is None
        world.current_turn += 1
        assert R.find_ai_enactment(world, "Austria", 60000, 2) is not None

    def test_lever_down_no_court_enacts(self, world, carried, monkeypatch):
        rich(world, "Austria")
        assert R.find_ai_enactment(world, "Austria", 60000, 2) is not None
        monkeypatch.setattr(R, "THE_AI_ENACTS", False)
        assert R.find_ai_enactment(world, "Austria", 60000, 2) is None

    def test_a_court_without_a_deck(self, world):
        world.nation_gold["Bavaria"] = 60000
        assert R.find_ai_enactment(world, "Bavaria", 60000, 2) is None


class TestThePurseTest:

    def test_the_chest_keeps_a_reserve_and_five_turns_of_upkeep(self, world, carried):
        row = R.find_law(world, "Austria", "corps_d_armee")
        bar = 9000 + R.AI_PURSE_RESERVE + R.AI_PURSE_UPKEEP_TURNS * 300
        rich(world, "Austria", bar - 1)
        assert "under the bar" in R.ai_purse_refusal(world, "Austria", row, bar - 1)
        assert R.ai_purse_refusal(world, "Austria", row, bar) == ""

    def test_the_bar_counts_the_slate_already_in_force(self, world, carried):
        rich(world, "Austria", 60000)
        R.enact_law(world, "Austria", R.find_law(world, "Austria", "jager_battalions"))
        row = R.find_law(world, "Austria", "corps_d_armee")
        bar = 9000 + R.AI_PURSE_RESERVE + R.AI_PURSE_UPKEEP_TURNS * (300 + 100)
        assert "under the bar" in R.ai_purse_refusal(world, "Austria", row, bar - 1)
        assert R.ai_purse_refusal(world, "Austria", row, bar) == ""

    def test_an_authority_law_asks_no_gold_price(self, world, carried):
        """An authority price is paid in authority, never in gold: the chest's
        bar is the reserve and five turns of upkeep only (the Landwehr:
        1,000 + 5 x 150)."""
        rich(world, "Austria")
        row = R.find_law(world, "Austria", "landwehr")
        bar = R.AI_PURSE_RESERVE + R.AI_PURSE_UPKEEP_TURNS * 150
        assert bar == 1750
        assert "under the bar" in R.ai_purse_refusal(world, "Austria", row, bar - 1)
        assert R.ai_purse_refusal(world, "Austria", row, bar) == ""

    def test_a_lapsed_law_prices_its_arrears(self, world, carried):
        """R8 at the rung: the Staff that lapsed last turn has lain dead two
        turns, so it restores for half its price plus two turns' upkeep — and
        the bar carries both, as the executor will charge them."""
        rich(world, "Austria")
        row = R.find_law(world, "Austria", "corps_d_armee")
        row["lapsed_turn"] = int(world.current_turn) - 1
        quote = R.restoration_price(world, "Austria", row)
        assert (quote["price"], quote["arrears"]) == (4500, 600)
        bar = 4500 + 600 + R.AI_PURSE_RESERVE + R.AI_PURSE_UPKEEP_TURNS * 300
        assert "under the bar" in R.ai_purse_refusal(world, "Austria", row, bar - 1)
        assert R.ai_purse_refusal(world, "Austria", row, bar) == ""

    def test_the_forecast_net_must_carry_the_upkeep(self, world, monkeypatch):
        import backend.game_logic.ledger as L
        rich(world, "Austria", 60000)
        row = R.find_law(world, "Austria", "corps_d_armee")
        monkeypatch.setattr(L, "_build_economy", lambda w, n, income_data=None: {"net": 299})
        assert "forecast Net" in R.ai_purse_refusal(world, "Austria", row, 60000)
        monkeypatch.setattr(L, "_build_economy", lambda w, n, income_data=None: {"net": 300})
        assert R.ai_purse_refusal(world, "Austria", row, 60000) == ""

    def test_authority_never_below_thirty(self, world, carried):
        rich(world, "Austria")
        row = R.find_law(world, "Austria", "landwehr")
        world.nation_authority["Austria"] = 44
        assert "under 30" in R.ai_purse_refusal(world, "Austria", row, 60000)
        world.nation_authority["Austria"] = 45
        assert R.ai_purse_refusal(world, "Austria", row, 60000) == ""

    def test_the_diplomatic_point_is_weighed(self, world, carried, monkeypatch):
        """§3: a political act from 60 loses the +1 above 60. The rung weighs
        it by a floor — never fewer than 3 points a turn after the act."""
        import backend.game_logic.diplomacy as D
        rich(world, "Austria")
        row = R.find_law(world, "Austria", "landwehr")
        seen = {}

        def dp(diplomat, authority, controls_capital):
            seen["authority"] = authority
            return 2
        monkeypatch.setattr(D, "calculate_dp", dp)
        assert "diplomatic points" in R.ai_purse_refusal(world, "Austria", row, 60000)
        assert seen["authority"] == 45, "weighed at the authority AFTER the act"
        monkeypatch.setattr(D, "calculate_dp", lambda d, a, c: 3)
        assert R.ai_purse_refusal(world, "Austria", row, 60000) == ""

    def test_a_court_without_its_capital_keeps_its_authority(self, world, carried):
        rich(world, "Austria")
        row = R.find_law(world, "Austria", "landwehr")
        world.diplomats.pop("Austria", None) if isinstance(getattr(world, "diplomats", None), dict) else None
        world.regions[world.get_nation_capital("Austria")].controller = "France"
        # base 3, no skilled envoy, below 60, no capital: 3 - 1 = 2 < 3
        assert "diplomatic points" in R.ai_purse_refusal(world, "Austria", row, 60000)


class TestTheSameExecutor:

    def test_the_ai_enacts_through_the_shared_executor_with_its_own_budget(self, world):
        rich(world, "Austria", 60000)
        world.admin_actions_remaining = 0   # the PLAYER's pool — never the AI's
        command = {"command": {"action": "enact_law", "target": "landwehr",
                               "_acting_nation": "Austria", "type": "specific"}}
        with _quiet():
            result = M.executor.execute(command, M.game_state)
        assert result.get("success") is True, result.get("message")
        assert R.is_in_force(R.find_law(world, "Austria", "landwehr"))
        assert world.nation_authority["Austria"] == 45

    def test_the_admin_chain_orders_it(self, world, carried):
        from backend.ai.enemy_ai import EnemyAI
        rich(world, "Austria", 60000)
        ai = EnemyAI(M.executor)
        order = ai._pick_admin_action("Austria", world, 2, set())
        assert order is not None and order.get("action") in (
            "recruit", "purchase_levy", "grant_dotation", "grant_pension",
            "invest_vassal", "grant_region_to_vassal", "change_autonomy",
            "recruit_marshal", "enact_law"), order
        skip = {"recruit", "purchase_levy", "grant_dotation", "grant_pension",
                "invest_vassal", "grant_region_to_vassal", "change_autonomy",
                "recruit_marshal"}
        order = ai._pick_admin_action("Austria", world, 2, skip)
        assert order == {"action": "enact_law", "target": "corps_d_armee"}, order

    def test_a_skipped_enactment_is_not_ordered_again(self, world, carried):
        from backend.ai.enemy_ai import EnemyAI
        rich(world, "Austria", 60000)
        skip = {"recruit", "purchase_levy", "grant_dotation", "grant_pension",
                "invest_vassal", "grant_region_to_vassal", "change_autonomy",
                "recruit_marshal", "enact_law"}
        order = EnemyAI(M.executor)._pick_admin_action("Austria", world, 2, skip)
        assert not order or order.get("action") != "enact_law"


class TestTheMeasuredBoard:
    """T3 on the committed attribution (`tools/_rf3_series_arms.json`)."""

    ARMS = json.loads((ROOT / "tools" / "_rf3_series_arms.json").read_text(encoding="utf-8"))

    def test_arm_zero_is_the_prior_series(self):
        assert self.ARMS["arms"]["0"]["series"] == self.ARMS["recorded"]
        assert self.ARMS["arms"]["0"]["rf3"]["enacted"] == []

    def test_t3_two_courts_by_turn_twenty_five_and_no_lapse(self):
        enacted = self.ARMS["arms"]["1"]["rf3"]["enacted"]
        courts = {n for t, n, _law in enacted if t <= 25}
        assert len(courts) >= 2, courts
        assert self.ARMS["arms"]["1"]["rf3"]["lapsed"] == []

    def test_the_shipped_series_is_arm_one(self):
        """RE-SEATED by the AI drill fix (September 27, 2026): the series was
        re-recorded once more. RF-3's arm 1 is now the prior record the drill
        fix's arm 0 (every drill lever down) reproduces byte for byte; the
        drill fix's arm 1 is the standing series."""
        from tests.test_ai_intent_threat_migration import BASELINE_SERIES
        drill = json.loads((ROOT / "tools" / "_drill_fix_series_arms.json").read_text(
            encoding="utf-8"))
        assert self.ARMS["arms"]["1"]["series"] == drill["recorded"]
        assert drill["arms"]["0"]["series"] == drill["recorded"]
        assert BASELINE_SERIES == drill["arms"]["1"]["series"]
