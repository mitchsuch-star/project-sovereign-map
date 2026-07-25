"""Pin-20 live in-game pass (July 25, 2026) — the defects it found.

Every test here reproduces something seen ON SCREEN in a live 1805
campaign driven through the Godot client, not a hypothetical:

1. A settlement offer re-opened from the mailbox rendered the territorial
   picture of the turn it ARRIVED — "Austria retains Swabia" five turns
   after France had retaken Swabia — because `/mailbox/activate` reused a
   cached popup payload while the status-quo clause is derived live.
2. The Threat & Coalition tab stated a dissolution rule the engine does
   not implement ("any member's war exhaustion exceeds 80") while Austria
   sat pinned at the exhaustion CAP with the Third Coalition standing.
3. The same tab rendered "WE: 200/100" — a denominator of 100 against
   `WAR_EXHAUSTION_MAX = 200`.
4. Berthier reported "…aided Ney and Lannes and Murat and Bernadotte,
   however, was conspicuously absent."
5. The dispatch said the subsidy "stands at 200 this season" while the
   ledger's PAYMASTER'S PURSE said "pays Austria 300g/turn", same breath.
"""

from __future__ import annotations

import copy
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.game_logic.battle_report import _join_names, _pick_observation
from backend.game_logic.coalition import (
    DISSOLUTION_THREAT_THRESHOLD,
    WAR_EXHAUSTION_MAX,
)
from backend.game_logic.diplomatic_ledger import build_diplomatic_ledger
from backend.game_logic.instruments import build_subsidy_payload
from backend.models.world_state import WorldState

SCENARIO_PATH = (
    Path(__file__).resolve().parents[1]
    / "godot-client" / "project-sovereign" / "assets" / "maps"
    / "europe_1805.json"
)


@pytest.fixture(scope="module")
def world1805():
    return WorldState.from_scenario(str(SCENARIO_PATH))


@pytest.fixture
def world(world1805):
    return WorldState.from_dict(world1805.to_dict())


# ═══════════════════════════════════════════════════════════════════════
# 1. The re-opened settlement offer must describe TODAY's map
# ═══════════════════════════════════════════════════════════════════════

class TestSettlementOfferPopupIsRebuiltOnActivation:
    """The status-quo clause is derived from current controllers, so a
    cached payload is a lie the moment the front moves."""

    def _offer_dialogue(self, world) -> dict:
        war_id = next(iter(world.war_instances), None)
        assert war_id, "the 1805 boot has live war instances"
        return {
            "type": "incoming_settlement_offer",
            "dialogue_type": "incoming_settlement_offer",
            "offer_id": "settlement_offer:test:1:1",
            "war_id": str(war_id),
            "proposer_nation": "Britain",
            "accepting_side": "attackers",
            "accepting_leader": "France",
            "covered_enemy_participants": ["Britain"],
            "settlement_terms": [{"type": "peace"}],
            "turn_created": int(world.current_turn),
        }

    def test_status_quo_clause_follows_a_capture(self, world):
        from backend.game_logic.settlement_offers import (
            build_incoming_settlement_offer_popup,
        )

        dialogue = self._offer_dialogue(world)
        # A province Austria holds at boot, seen in the offer's clause.
        austrian = [
            name for name in world.get_nation_regions("Austria")
            if name in set(world.nation_starting_regions.get("Austria", []))
        ]
        assert austrian, "Austria holds its own soil at boot"
        target = sorted(austrian)[0]

        before = build_incoming_settlement_offer_popup(world, dialogue)
        text_before = str(before)

        # France takes it — the very thing the live pass did with Swabia.
        world.capture_region(target, "France")
        after = build_incoming_settlement_offer_popup(world, dialogue)

        assert f"Austria retains" not in str(after) or target not in str(after), (
            "the rebuilt popup still claims Austria retains a province "
            f"France now holds: {target}"
        )
        assert text_before != str(after), (
            "capturing a province must change the offer's derived clause")

    def test_activate_endpoint_rebuilds_rather_than_replaying_cache(self, world):
        """The regression itself: activation must not serve a stale payload."""
        import backend.main as main_module

        client = TestClient(main_module.app)
        original = main_module.game_state["world"]
        main_module.game_state["world"] = world
        try:
            dialogue = self._offer_dialogue(world)
            # Seed a deliberately WRONG cached payload, as a turn-3 offer
            # re-opened on turn 8 effectively carried.
            dialogue["popup_payload"] = {
                "description": "STALE — Austria retains everything",
            }
            world.dialogue_manager.push(dialogue)
            items = client.get("/mailbox").json()["items"]
            offer_rows = [
                i for i in items
                if i.get("item_type") == "incoming_settlement_offer"
                or i.get("dialogue_type") == "incoming_settlement_offer"
            ]
            assert offer_rows, f"offer did not reach the mailbox: {items}"
            resp = client.post(
                "/mailbox/activate",
                json={"mailbox_id": offer_rows[0]["mailbox_id"]},
            ).json()
            popup = resp.get("incoming_settlement_offer") or {}
            assert popup, f"no popup payload returned: {resp}"
            assert "STALE" not in str(popup), (
                "activation replayed the cached payload instead of "
                "rebuilding it against the live world")
        finally:
            main_module.game_state["world"] = original


# ═══════════════════════════════════════════════════════════════════════
# 2 + 3. The coalition tab may only state rules the engine enforces
# ═══════════════════════════════════════════════════════════════════════

class TestCoalitionDissolutionRuleIsHonest:
    def test_no_war_exhaustion_dissolution_claim(self, world):
        boe = build_diplomatic_ledger(world)["balance_of_europe"]
        assert "dissolution_war_exhaustion_limit" not in boe, (
            "the ledger advertised an exhaustion-based dissolution lever "
            "that `coalition.check_dissolution` has never implemented")

    def test_stated_thresholds_are_the_enforced_ones(self, world):
        boe = build_diplomatic_ledger(world)["balance_of_europe"]
        assert boe["dissolution_threat_threshold"] == DISSOLUTION_THREAT_THRESHOLD
        assert boe["dissolution_min_members"] == 2

    def test_check_dissolution_really_ignores_exhaustion(self, world):
        """The live proof: a member at the cap does not break a coalition."""
        from backend.game_logic.coalition import check_dissolution

        if not world.active_coalition:
            pytest.skip("no active coalition on this boot")
        for member in world.active_coalition.get("members", []):
            world.war_exhaustion[member] = WAR_EXHAUSTION_MAX
        assert check_dissolution(world) != "war_exhaustion", (
            "if exhaustion ever becomes a dissolution condition, the ledger "
            "copy must be restored alongside it")

    def test_exhaustion_scale_is_published_for_the_bar(self, world):
        boe = build_diplomatic_ledger(world)["balance_of_europe"]
        assert boe["war_exhaustion_max"] == WAR_EXHAUSTION_MAX
        assert boe["war_exhaustion_max"] != 100, (
            "the member rows rendered 'WE: 200/100' off a hardcoded 100")


# ═══════════════════════════════════════════════════════════════════════
# 4. Berthier writes sentences
# ═══════════════════════════════════════════════════════════════════════

class TestCoordinationObservationGrammar:
    @pytest.mark.parametrize("names,expected", [
        ([], ""),
        (["Ney"], "Ney"),
        (["Ney", "Soult"], "Ney and Soult"),
        (["Lannes", "Murat", "Bernadotte"], "Lannes, Murat and Bernadotte"),
        (["A", "B", "C", "D"], "A, B, C and D"),
    ])
    def test_join_names_reads_like_prose(self, names, expected):
        assert _join_names(names) == expected

    def test_join_names_drops_blanks(self):
        assert _join_names(["Ney", "", None, "Soult"]) == "Ney and Soult"

    def _mixed_battle(self, failed_names):
        return {
            "outcome": "attacker_victory",
            "attacker_nation": "France",
            "defender_nation": "Austria",
            "attacker": {"name": "Ney", "nation": "France"},
            "defender": {"name": "Mack", "nation": "Austria"},
            "modifier_snapshot": {"attacker": [], "defender": []},
            "coordination_context": {},
            "reinforcement_results_for_report": {
                "attacker": (
                    [{"marshal": "Davout", "arrived": True}]
                    + [{"marshal": n, "arrived": False} for n in failed_names]
                ),
                "defender": [],
            },
        }

    def test_three_absentees_take_a_plural_verb(self):
        seen = set()
        for _ in range(60):
            seen.add(_pick_observation(
                self._mixed_battle(["Lannes", "Murat", "Bernadotte"])))
        joined = " || ".join(seen)
        assert "and Murat and" not in joined, (
            f"the and-chain survived: {joined}")
        assert "Lannes, Murat and Bernadotte" in joined
        assert ", however, was conspicuously absent" not in joined, (
            f"singular verb against three absent marshals: {joined}")

    def test_one_absentee_keeps_the_singular_verb(self):
        seen = set()
        for _ in range(60):
            seen.add(_pick_observation(self._mixed_battle(["Lannes"])))
        joined = " || ".join(seen)
        assert "were conspicuously absent" not in joined, (
            f"plural verb against one absent marshal: {joined}")


# ═══════════════════════════════════════════════════════════════════════
# 5. The purse and the dispatch may not quote different sums
# ═══════════════════════════════════════════════════════════════════════

class TestPaymasterPurseMatchesWhatWasPaid:
    """A paymaster arrangement is a mid-campaign state (the coalition must
    stand and the purse must clear its floor), so the arrangement is
    constructed rather than skipped — the contradiction the live pass saw
    is a COMPOSITION bug and must be pinned deterministically."""

    @pytest.fixture
    def funded(self, world, monkeypatch):
        import backend.game_logic.agendas as agendas
        import backend.game_logic.coalition as coalition_mod

        monkeypatch.setattr(agendas, "get_paymaster_nation",
                            lambda w: "Britain")
        monkeypatch.setattr(coalition_mod, "get_british_subsidy_recipient",
                            lambda w: "Austria")
        # Above AGENDA_SUBSIDY tier 2 so the standing RATE is 300 while the
        # season's transfer went out at the 200 floor — the live case.
        world.nation_gold["Britain"] = 6000
        return world

    def test_rate_reflects_the_treasury_tier(self, funded):
        payload = build_subsidy_payload(funded)
        assert payload is not None
        assert payload["amount"] == 300

    def test_delivered_sum_is_named_when_it_differs_from_the_rate(self, funded):
        funded.log_event({
            "type": "british_subsidy",
            "payer": "Britain",
            "recipient": "Austria",
            "amount": 200,
        })
        payload = build_subsidy_payload(funded)
        assert payload["delivered"] == 200
        assert "200g this season" in payload["line"]
        assert "300g/turn at their present treasury" in payload["line"], (
            "the prospective rate must stay visible beside the delivered sum")

    def test_matching_sums_keep_the_plain_line(self, funded):
        funded.log_event({
            "type": "british_subsidy",
            "payer": "Britain",
            "recipient": "Austria",
            "amount": 300,
        })
        payload = build_subsidy_payload(funded)
        assert payload["line"].endswith("to keep the field")
        assert "this season" not in payload["line"]

    def test_no_payment_this_turn_reads_as_the_standing_rate(self, funded):
        payload = build_subsidy_payload(funded)
        assert payload["delivered"] is None
        assert "this season" not in payload["line"]
        assert "300g/turn to keep the field" in payload["line"]

    def test_last_turns_payment_does_not_leak_into_this_season(self, funded):
        funded.log_event({
            "type": "british_subsidy",
            "payer": "Britain",
            "recipient": "Austria",
            "amount": 200,
        })
        funded.current_turn += 1
        payload = build_subsidy_payload(funded)
        assert payload["delivered"] is None, (
            "a previous turn's transfer must not be quoted as this season's")

    def test_another_pair_s_transfer_is_not_borrowed(self, funded):
        funded.log_event({
            "type": "british_subsidy",
            "payer": "Britain",
            "recipient": "Russia",
            "amount": 200,
        })
        payload = build_subsidy_payload(funded)
        assert payload["delivered"] is None
