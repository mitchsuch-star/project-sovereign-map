"""Row BA, session BA-6 — its one review (November 17, 2026), run on a frozen
copy before any commit: five finder lanes and a completeness critic over the
backend, tests, tools and records, every finding put to a reproducer and a
refuter (`BATTLE_DIORAMA_SPEC.md` §15.26). Each fix with its behaviour test,
and the three finds the suite's run made after them (BA6-X5 … X7).

BA6-R1  an account on screen never lapses under the player; a settled account
        cannot be answered (and paid for) twice; its card retires.
BA6-R2  the confer route takes only the player's own marshals.
BA6-R3  a fortress stormed into an occupation struck a blow (WS-15 gives
        nothing back for it).
BA6-R4  the courts' "outnumbered" reads the field's men (WS-13's sibling).
BA6-R5  a refused glorious charge keeps its square (WS-15's sibling).
BA6-R6  a strategic defiance names the order it defied in words.
BA6-R8  the campaign log tells a relationship's move only of the player's court.
BA6-X5  a war folded in the middle of the courts' bandwagon pass is skipped.
BA6-X6  a merged war takes a pair live in the absorbed war as live.
BA6-X7  the keyed world probe holds its seams from the boot.
"""
from __future__ import annotations

import inspect
from pathlib import Path

import pytest

from backend.commands import combat_executor as ce
from backend.commands import strategic_executor as SE
from backend.game_logic import precedence as P
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
SCENARIO = REPO / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"


@pytest.fixture(scope="module")
def opening():
    return WorldState.from_scenario(str(SCENARIO))


@pytest.fixture
def world(opening):
    w = WorldState.from_dict(opening.to_dict())
    w.authority_tracker.authority = 90
    return w


# ═══════════════════════════════ BA6-R1 ═══════════════════════════════════

class TestAnAccountOnScreenWaitsForItsAnswer:

    def _on_screen(self, world):
        world.marshal_accounts = [{"lead": "Ney", "others": ["Soult"], "place": "Swabia",
                                   "turn": world.current_turn}]
        card = P._account_card(world, world.marshal_accounts[0])
        world.pending_marshal_petition = card
        return card

    def test_it_does_not_lapse_while_it_is_shown(self, world):
        card = self._on_screen(world)
        view_before = int(world.marshals["Soult"].relationships.get("Ney", 0) or 0)
        world.current_turn += P.ACCOUNT_SHOWS_FOR + 3
        P._push_accounts(world)
        assert world.marshal_accounts, "the account on screen is not let lie under the player"
        assert int(world.marshals["Soult"].relationships.get("Ney", 0) or 0) == view_before, \
            "nothing soured while the card waits"
        r = P.apply_account(world, "take_it", card["context"])
        assert r["success"], r

    def test_a_settled_account_cannot_be_paid_twice(self, world):
        card = self._on_screen(world)
        assert P.apply_account(world, "take_it", card["context"])["success"]
        before = world.authority_tracker.authority
        again = P.apply_account(world, "take_it", card["context"])
        assert not again["success"] and "already settled" in again["message"]
        assert world.authority_tracker.authority == before, "nothing charged the second time"

    def test_the_card_of_a_settled_account_retires(self, world):
        card = self._on_screen(world)
        world.marshal_accounts = []
        assert P.account_retirement_reason(world, card["context"]) == "settled"

    def test_an_unseen_account_still_lapses(self, world):
        world.marshal_accounts = [{"lead": "Ney", "others": ["Soult"], "place": "Swabia",
                                   "turn": world.current_turn}]
        world.pending_marshal_petition = {"kind": "other"}
        world.current_turn += P.ACCOUNT_SHOWS_FOR + 1
        P._push_accounts(world)
        assert not world.marshal_accounts


# ═══════════════════════════════ BA6-R2 ═══════════════════════════════════

class TestTheConferRouteIsTheEmperors:

    def test_an_enemy_marshal_reads_as_unknown_and_nothing_moves(self, world):
        charles = world.marshals["ArchdukeCharles"]
        charles.title_due = {"tier": 1, "name": "Duke of Caldiero", "place": "Venetia",
                             "turn": world.current_turn, "expires": world.current_turn + 8}
        tracker = world.nation_authority if hasattr(world, "nation_authority") else {}
        before = dict(tracker) if isinstance(tracker, dict) else None
        r = P.confer_title(world, "ArchdukeCharles")
        unknown = P.confer_title(world, "Nobody")
        assert not r["success"] and r["message"].replace("ArchdukeCharles", "X") == \
            unknown["message"].replace("Nobody", "X")
        assert charles.title_due and not (charles.honours or [])
        if before is not None:
            assert dict(world.nation_authority) == before

    def test_the_claims_own_grant_still_confers(self):
        assert "_confer_title_on(world, marshal.name)" in inspect.getsource(P.apply_claim)


# ═══════════════════════════════ BA6-R3 ═══════════════════════════════════

class TestAFortressStormedStruckABlow:

    def _stormed(self):
        return {"success": True, "occupation_started": True,
                "events": [{"type": "garrison_destroyed"}, {"type": "occupation_started"}]}

    def test_an_occupation_after_an_assault_is_a_blow(self):
        assert ce.attack_struck_no_blow(self._stormed()) is False

    def test_a_walk_in_is_still_no_blow(self):
        assert ce.attack_struck_no_blow({"success": True, "occupation_started": True,
                                         "events": [{"type": "occupation_started"}]}) is True

    def test_seam_down_the_old_list(self, monkeypatch):
        monkeypatch.setattr(ce, "a_refused_attack_spends_nothing", lambda: False)
        assert ce.attack_struck_no_blow(self._stormed()) is True


# ═══════════════════════════════ BA6-R4 / R5 / R6 ═════════════════════════

class TestTheSiblings:

    def test_the_courts_read_the_fields_odds(self):
        src = inspect.getsource(ce.CombatExecutor._post_combat_pipeline)
        call = src.split("_court_standing.courts_battle(", 1)[1].split("atk_casualties", 1)[0]
        assert "odds_atk, odds_def, bool(conquered)" in call and "pre_atk" not in call

    def test_a_charge_breaks_its_square_only_past_its_refusals(self):
        src = inspect.getsource(ce.CombatExecutor._execute_glorious_charge)
        late = src.index("if a_refused_attack_spends_nothing():\n            self._executor._auto_break_square")
        assert src.index("has already engaged") < late < src.index("world.record_attack(")

    def test_a_refused_charge_keeps_its_square(self, world):
        from backend.commands.executor import CommandExecutor
        ex = CommandExecutor()
        murat = world.marshals["Murat"]
        murat.square_formation, murat.ai_square_cooldown = True, 0
        res = ex._combat._execute_glorious_charge(murat, "Nobody Of That Name", world, {"world": world})
        assert not res.get("success", False)
        assert murat.square_formation is True and murat.ai_square_cooldown == 0

    def test_a_defiance_names_the_order_in_words(self, monkeypatch):
        assert [SE._the_order_in_words(k) for k in ("PURSUE", "MOVE_TO", "SUPPORT", "HOLD")] == [
            "pursuing", "marching", "supporting", "holding"]
        monkeypatch.setattr(SE, "a_defiance_names_the_order_in_words", lambda: False)
        assert SE._the_order_in_words("PURSUE") == "PURSUE"


# ═══════════════════════════════ BA6-R8 ═══════════════════════════════════

class TestABondIsToldOnlyOfOurCourt:

    def _log(self, world, monkeypatch=None):
        from backend.campaign_log import filter_campaign_log
        events = [
            {"type": "relationship_change", "marshal": "Kutuzov", "toward": "Buxhowden", "change": 1,
             "new_value": 0, "new_label": "Professional", "direction": "up", "nation": "Russia",
             "location": "Moravia", "turn": 3},
            {"type": "relationship_change", "marshal": "Ney", "toward": "Soult", "change": 1,
             "new_value": 0, "new_label": "Professional", "direction": "up", "nation": "France",
             "location": "Swabia", "turn": 3},
        ]
        return [e["marshal"] for e in filter_campaign_log(events, world) if e["type"] == "relationship_change"]

    def test_only_the_players_court(self, world):
        assert self._log(world) == ["Ney"]

    def test_seam_down_every_court(self, world, monkeypatch):
        from backend import campaign_log
        monkeypatch.setattr(campaign_log, "a_bond_is_told_only_of_our_court", lambda: False)
        assert self._log(world) == ["Kutuzov", "Ney"]


# ═══════════════════════════════ BA6-X5 / X6 / X7 ═════════════════════════

class TestTheWarMachinery:

    def test_a_war_folded_mid_pass_is_skipped(self, world, monkeypatch):
        """The bandwagon pass reads each war as it comes to it: a war a call
        below folded away is skipped, never read (KeyError: 'war_4')."""
        from backend.game_logic import war_council as WC
        world.war_instances = {
            "war_1": {"active_participants": ["Austria", "Bavaria"], "attacker_leader": "Austria",
                      "defender_leader": "Bavaria"},
            "war_2": {"active_participants": ["Prussia", "Hanover"]},
        }
        seen = []

        def strengths(w, inst):
            seen.append(inst)
            w.war_instances.pop("war_2", None)       # a fold in place, mid-pass
            return [], [], 0, 0
        monkeypatch.setattr(WC, "_side_strengths", strengths)
        WC._bandwagon_join(world, "Sweden", [])
        assert len(seen) == 1

    def test_a_pair_live_in_the_absorbed_war_is_live_in_the_merged_one(self):
        from backend.game_logic.settlement_helpers import _merge_instance_data
        survivor = {"active_diplo_keys": ["Bavaria|France"], "resolved_diplo_keys": ["Austria|Bavaria"],
                    "diplo_key_meta": {"Austria|Bavaria": {"pair_status": "resolved"},
                                       "Bavaria|France": {"pair_status": "war"}}}
        absorbed = {"active_diplo_keys": ["Austria|Bavaria"],
                    "diplo_key_meta": {"Austria|Bavaria": {"pair_status": "war"}}}
        _merge_instance_data(survivor, absorbed)
        assert "Austria|Bavaria" in survivor["active_diplo_keys"]
        assert "Austria|Bavaria" not in survivor["resolved_diplo_keys"]
        assert survivor["diplo_key_meta"]["Austria|Bavaria"]["pair_status"] == "war"

    def test_the_probe_holds_its_seams_from_the_boot(self):
        src = (REPO / "tools" / "keyed_world_probe.py").read_text(encoding="utf-8")
        run = src.split("def run(", 1)[1].split("\ndef ", 1)[0]
        assert run.index("seams = apply_from_env()") < run.index("WorldState.from_scenario(")


# ═══════════════════════════════ BA6-X8 ═══════════════════════════════════

class TestAPeaceEvacuatesAThirdCourtsGround:
    """BA-5's ruling 1, built as it pre-decided: the final measure's ambient
    line read 1 (rivoli: Saxony took Swabia — Bavaria's, held by Austria — and
    kept it at the Austria–Saxony peace)."""

    def test_a_third_courts_ground_taken_from_the_ceder_goes_back(self, world):
        from backend.game_logic import game_end as GE
        kept, gone = GE.aim_evacuations(world, "Austria", "Saxony", "Saxony", "Austria",
                                        {"Saxony": ["Swabia"]})
        assert gone == {"Saxony": ["Swabia"]} and kept == {}

    def test_the_holders_own_homeland_never_goes(self, world):
        from backend.game_logic import game_end as GE
        saxon = sorted((world.nation_starting_regions or {}).get("Saxony") or [])
        assert saxon
        kept, gone = GE.aim_evacuations(world, "Austria", "Saxony", "Saxony", "Austria",
                                        {"Saxony": [saxon[0]]})
        assert kept == {"Saxony": [saxon[0]]} and gone == {}

    def test_the_players_peace_keeps_its_law(self, world):
        from backend.game_logic import game_end as GE
        kept, gone = GE.aim_evacuations(world, "Austria", "France", "France", "Austria",
                                        {"France": ["Swabia"]})
        assert kept == {"France": ["Swabia"]} and gone == {}

    def test_seam_down_only_the_ceders_homeland(self, world, monkeypatch):
        from backend.game_logic import game_end as GE
        monkeypatch.setattr(GE, "a_peace_evacuates_a_third_courts_ground", lambda: False)
        kept, gone = GE.aim_evacuations(world, "Austria", "Saxony", "Saxony", "Austria",
                                        {"Saxony": ["Swabia"]})
        assert kept == {"Saxony": ["Swabia"]} and gone == {}
