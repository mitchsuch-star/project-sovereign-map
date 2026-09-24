"""FA slice 17, Phase 2 batch 2b — "The Mechanics Rulings" (September 11, 2026).

Seven mechanics rulings, each reproduced on the shipped board before a line was
written, built behind flip levers whose False arm reproduces the prior board:

  FA-D4    the spine war boots with a purpose (the live declaration's own)
  FA-D5    the redemption audience offers the arm that pays him
  FA-D6    the treaty's road home is literal — cannon fire never takes it
  FA-D7    the peace mount reads the desk before it drafts
  FA-D19   a detached garrison feeds stability
  FA-D23   trust reaches the field, both sides
  FA-S2-D1 the enemy waits one turn for a freshly-cornered player marshal
"""
from __future__ import annotations

import contextlib
import io
from pathlib import Path

import pytest

from backend.ai.enemy_ai import EnemyAI
from backend.commands.executor import CommandExecutor
from backend.models.marshal import StrategicOrder
from backend.models.world_state import WorldState
from tests.conftest import MarshalFactory, WorldFactory

ROOT = next(p for p in (Path(__file__).resolve().parents[1], Path.cwd()) if (p / "backend").is_dir())
SCENARIO = ROOT / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
GD = ROOT / "godot-client" / "project-sovereign" / "scripts"


def _boot():
    with contextlib.redirect_stdout(io.StringIO()):
        return WorldState.from_scenario(str(SCENARIO))


def _flip(monkeypatch, module, name, value):
    assert hasattr(module, name), f"{getattr(module, '__name__', module)} has no lever {name}"
    monkeypatch.setattr(module, name, value)


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


# ═══════════════════════════════════════════════════════════════════════
# FA-D4 — the spine war has a purpose
# ═══════════════════════════════════════════════════════════════════════
class TestD4TheSpineWarHasAPurpose:
    def test_every_belligerent_boots_with_the_live_declarations_objective(self):
        w = _boot()
        pairs = [(e["attacker"], e["defender"]) for e in w.scenario_starting_wars] if hasattr(w, "scenario_starting_wars") else None
        # the boot coalition war: France vs Britain / Austria / Russia
        for court in ("Britain", "Austria", "Russia"):
            key = w._make_diplo_key("France", court)
            objs = w.war_objectives.get(key) or {}
            assert objs.get("France", {}).get("type") == "defense", (court, objs)
            assert objs.get(court, {}).get("type") == "defense", (court, objs)
            assert objs[court]["target_regions"], "a defense objective names the homeland it holds"
            assert objs["France"]["accumulated_ticking"] == 0

    def test_the_war_row_carries_both_objectives_and_the_verb(self):
        from backend.game_logic.war_status import build_active_wars
        w = _boot()
        row = next(r for r in build_active_wars(w)["wars"] if r.get("is_multi_participant_war"))
        assert row["objective"]["type"] == "defense"
        assert row["enemy_objective"]["type"] == "defense"
        assert f"'set war purpose against {row['opponent']}'" in row["objective_hint"]
        assert "defensive purpose only" in row["objective_hint"]

    def test_the_player_may_still_name_a_purpose_of_his_own(self):
        w = _boot()
        ex = CommandExecutor()
        with _quiet():
            res = ex._diplomatic._set_war_purpose_inner("Britain", "conquest", w)
        assert res.get("success"), res
        key = w._make_diplo_key("France", "Britain")
        assert w.war_objectives[key]["France"]["type"] == "conquest"

    def test_the_boot_war_score_moves_nothing_on_turn_one(self):
        """A defense objective ticks only for homeland LOST — at boot every
        court holds its own, so the purpose changes no number the AI reads."""
        from backend.game_logic.diplomacy import accumulate_war_objective_ticking
        w = _boot()
        with _quiet():
            events = accumulate_war_objective_ticking(w)
        assert events == []
        for objs in w.war_objectives.values():
            for obj in objs.values():
                assert obj["accumulated_ticking"] == 0 and obj["ticking_active"] is False

    def test_lever_down_boots_without_a_purpose(self, monkeypatch):
        from backend.models import world_state as WS
        from backend.game_logic.war_status import build_active_wars
        _flip(monkeypatch, WS, "THE_SPINE_WAR_HAS_A_PURPOSE", False)
        w = _boot()
        assert w.war_objectives == {}
        row = next(r for r in build_active_wars(w)["wars"] if r.get("is_multi_participant_war"))
        assert row["objective"] is None and row["objective_hint"] == ""

    def test_the_client_renders_the_hint(self):
        src = (GD / "war_detail_popup.gd").read_text(encoding="utf-8")
        assert 'w.get("objective_hint", "")' in src


# ═══════════════════════════════════════════════════════════════════════
# FA-D5 — the audience names its cause
# ═══════════════════════════════════════════════════════════════════════
class TestD5TheAudienceNamesItsCause:
    @staticmethod
    def _in_arrears(w, name="Lannes", wins=4):
        from backend.game_logic import dotation as DT
        m = w.marshals[name]
        m.expectation_steps = wins
        assert DT.get_shortfall(m, w) > 0
        m.trust.modify(-100)
        return m

    def test_the_first_arm_is_the_rente_priced_by_the_rails_own_builder(self):
        from backend.game_logic import dotation as DT
        w = _boot()
        m = self._in_arrears(w)
        with _quiet():
            opts = w.disobedience_system._get_available_redemption_options(m, w)
        assert opts[0]["id"] == "settle_account"
        offer = DT.build_rente_offer(m, w)
        assert f"{int(offer['face']):,}g a turn" in opts[0]["text"]
        assert f"pays {int(offer['cost']):,}g a turn" in opts[0]["description"]
        assert [o["id"] for o in opts[1:]] == ["grant_autonomy", "administrative_role", "dismiss"]

    def test_a_marshal_with_no_arrears_is_not_offered_it(self):
        w = _boot()
        m = w.marshals["Lannes"]
        m.trust.modify(-100)
        with _quiet():
            opts = w.disobedience_system._get_available_redemption_options(m, w)
        assert "settle_account" not in [o["id"] for o in opts]

    def test_answering_it_pays_him_through_the_executor_and_retires_the_question(self):
        w = _boot()
        m = self._in_arrears(w)
        m.redemption_pending = True
        ex = CommandExecutor()
        with _quiet():
            opts = w.disobedience_system._get_available_redemption_options(m, w)
            res = w.disobedience_system.handle_redemption_response(
                {"marshal": m.name, "options": opts}, "settle_account",
                {"world": w, "executor": ex})
        assert res["success"] is True and res["choice"] == "settle_account", res
        assert int(m.pension) > 0 and res["pension"] == int(m.pension)
        assert m.redemption_pending is False

    def test_a_refused_payment_leaves_the_question_standing(self, monkeypatch):
        w = _boot()
        m = self._in_arrears(w)
        m.redemption_pending = True
        ex = CommandExecutor()
        monkeypatch.setattr(ex, "execute", lambda cmd, gs: {"success": False, "message": "Not one action remains, Sire."})
        with _quiet():
            opts = w.disobedience_system._get_available_redemption_options(m, w)
            res = w.disobedience_system.handle_redemption_response(
                {"marshal": m.name, "options": opts}, "settle_account",
                {"world": w, "executor": ex})
        assert res["success"] is False and res["standing"] is True
        assert "Not one action" in res["message"]
        assert m.redemption_pending is True
        assert int(getattr(m, "pension", 0) or 0) == 0

    def test_the_answer_must_be_offered(self):
        """FA-N76's guard still runs first: an audience that did not offer the
        rente refuses it."""
        w = _boot()
        m = w.marshals["Lannes"]
        m.trust.modify(-100)
        m.redemption_pending = True
        with _quiet():
            opts = w.disobedience_system._get_available_redemption_options(m, w)
            res = w.disobedience_system.handle_redemption_response(
                {"marshal": m.name, "options": opts}, "settle_account", {"world": w})
        assert res["success"] is False and "not among the courses" in res["message"]

    def test_lever_down_offers_the_three_arms_only(self, monkeypatch):
        from backend.commands import disobedience as DS
        _flip(monkeypatch, DS, "THE_AUDIENCE_NAMES_ITS_CAUSE", False)
        w = _boot()
        m = self._in_arrears(w)
        with _quiet():
            opts = w.disobedience_system._get_available_redemption_options(m, w)
        assert [o["id"] for o in opts] == ["grant_autonomy", "administrative_role", "dismiss"]

    def test_the_client_builds_the_button_from_the_payload(self):
        dlg = (GD / "redemption_dialog.gd").read_text(encoding="utf-8")
        main = (GD / "main.gd").read_text(encoding="utf-8")
        assert 'settle_button.visible = "settle_account" in available_ids' in dlg
        assert 'choice_made.emit("settle_account")' in dlg
        assert '"settle_account":' in main and 'choice == "settle_account"' in main


# ═══════════════════════════════════════════════════════════════════════
# FA-D6 — the road home is literal
# ═══════════════════════════════════════════════════════════════════════
class TestD6TheRoadHomeIsLiteral:
    @staticmethod
    def _board(road=True):
        from backend.game_logic.withdrawal import ROAD_HOME_COMMAND
        w = _boot()
        ney = w.marshals["Ney"]
        ney.location = "Champagne"
        ney.strategic_order = StrategicOrder(
            command_type="MOVE_TO", target="Lorraine", target_type="region",
            started_turn=int(w.current_turn), issued_turn=int(w.current_turn), path=["Lorraine"],
            original_command=ROAD_HOME_COMMAND if road else "Ney, march to Lorraine")
        # a battle France has a stake in, one province over
        w.battles_this_turn.append({"location": "Picardy", "attacker": "Moore", "defender": "Soult",
                                    "attacker_nation": "Britain", "defender_nation": "France",
                                    "turn": w.current_turn})
        return w, ney

    def test_cannon_fire_never_takes_the_road_home(self):
        from backend.commands import strategic as ST
        w, ney = self._board(road=True)
        assert ney.personality == "aggressive"
        with _quiet():
            assert ST.StrategicOrderProcessor(CommandExecutor())._check_interrupts(ney, w) is None

    def test_an_ordinary_march_is_still_redirected(self):
        from backend.commands import strategic as ST
        w, ney = self._board(road=False)
        with _quiet():
            it = ST.StrategicOrderProcessor(CommandExecutor())._check_interrupts(ney, w)
        assert it and it["type"] == "cannon_fire" and it["action"] == "redirect"

    def test_lever_down_abandons_the_road(self, monkeypatch):
        from backend.commands import strategic as ST
        _flip(monkeypatch, ST, "THE_ROAD_HOME_IS_LITERAL", False)
        w, ney = self._board(road=True)
        with _quiet():
            it = ST.StrategicOrderProcessor(CommandExecutor())._check_interrupts(ney, w)
        assert it and it["action"] == "redirect"


# ═══════════════════════════════════════════════════════════════════════
# FA-D7 — the desk is read before the draft
# ═══════════════════════════════════════════════════════════════════════
class TestD7TheDeskIsReadBeforeTheDraft:
    @staticmethod
    def _table(offer=True):
        w = _boot()
        # the armistice-first route the paradox does not block
        w.diplomatic_states[w._make_diplo_key("Bavaria", "Austria")] = "PEACE"
        w.invalidate_bloc_members_cache()
        if offer:
            w.pending_settlement_dialogues.append({
                "type": "incoming_settlement_offer", "war_id": "war_1",
                "covered_enemy_participants": ["Austria", "Britain", "Russia"],
                "turn_created": int(w.current_turn)})
        return w

    @staticmethod
    def _send_arm(w):
        from backend.game_logic.diplomatic_dialogue import generate_dialogue
        with _quiet():
            dlg = generate_dialogue("proposal_confirm", {"target_nation": "Austria", "proposal_type": "peace"}, w)
        return dlg, next(o for o in dlg["options"] if o.get("action") == "execute_proposal")

    def test_the_send_arm_is_greyed_with_the_request_terms_routes_own_sentence(self):
        from backend.game_logic.settlement_routes import evaluate_request_terms_affordance
        w = self._table(offer=True)
        assert evaluate_request_terms_affordance(w, "war_1")["reason"] == "offer_already_pending"
        dlg, send = self._send_arm(w)
        assert send["enabled"] is False and send["available"] is False
        assert "already on the desk" in send["unavailable_reason"]
        assert dlg["desk_block_warning"] == send["unavailable_reason"]
        assert any("already on the desk" in x.get("text", "") for x in dlg["warnings"])

    def test_a_clear_desk_leaves_the_send_arm_live(self):
        w = self._table(offer=False)
        dlg, send = self._send_arm(w)
        assert send.get("enabled") is not False and "desk_block_warning" not in dlg

    def test_a_promoted_offer_counts_too(self, monkeypatch):
        from backend.game_logic import ai_diplomacy as AD
        w = self._table(offer=False)
        monkeypatch.setattr(AD, "_settlement_offer_already_promoted", lambda world, *, war_id: war_id == "war_1")
        dlg, send = self._send_arm(w)
        assert send["enabled"] is False

    def test_lever_down_drafts_over_the_offer(self, monkeypatch):
        from backend.game_logic import diplomatic_dialogue as DD
        _flip(monkeypatch, DD, "THE_DESK_IS_READ_BEFORE_THE_DRAFT", False)
        w = self._table(offer=True)
        dlg, send = self._send_arm(w)
        assert send.get("enabled") is not False and "desk_block_warning" not in dlg


# ═══════════════════════════════════════════════════════════════════════
# FA-D19 — a detachment feeds stability
# ═══════════════════════════════════════════════════════════════════════
class TestD19TheDetachmentFeedsStability:
    @staticmethod
    def _grow(nation="France", province="Champagne", detachment=None, marshal=None):
        w = _boot()
        r = w.get_region(province)
        assert r.controller == nation
        r.stability = 40
        for m in w.marshals.values():
            if m.location == province:
                m.location = "Moscow"
        if detachment is not None:
            r.garrison_detachment = True
            r.garrison_strength = detachment
        if marshal:
            w.marshals[marshal].location = province
        with _quiet():
            w.process_stability_growth()
        return r.stability

    def test_a_detachment_grows_the_province_like_a_marshal(self):
        assert self._grow() == 45
        assert self._grow(detachment=3000) == 50
        assert self._grow(marshal="Ney") == 50

    def test_a_flag_with_no_men_behind_it_feeds_nothing(self):
        assert self._grow(detachment=0) == 45

    def test_the_same_rule_serves_austria(self):
        assert self._grow(nation="Austria", province="Bohemia", detachment=3000) == 50

    def test_lever_down_reads_marshals_only(self, monkeypatch):
        from backend.models import world_state as WS
        _flip(monkeypatch, WS, "THE_DETACHMENT_FEEDS_STABILITY", False)
        assert self._grow(detachment=3000) == 45


# ═══════════════════════════════════════════════════════════════════════
# FA-D23 — trust reaches the field
# ═══════════════════════════════════════════════════════════════════════
class TestD23TrustReachesTheField:
    @staticmethod
    def _pair(w, ex, nation):
        """A lead/ally pair of `nation` whose base scale is positive — Mack and
        Charles are authored at -2 (MC-3), so the Austrian pair is found, not
        assumed."""
        roster = [m for m in w.marshals.values() if m.nation == nation and m.strength > 0]
        for a in roster:
            for b in roster:
                if a is not b and ex._combat._pair_contribution_scale(a, b) > 0:
                    return a, b
        raise AssertionError(f"no positive pair on {nation}'s roster")

    def test_a_broken_marshal_brings_half_his_weight_on_either_side(self):
        w = _boot()
        ex = CommandExecutor()
        for nation in ("France", "Austria"):
            a, b = self._pair(w, ex, nation)
            base = ex._combat._pair_contribution_scale(a, b)
            b.trust.modify(-100)
            assert b.trust.value < 30
            assert ex._combat.BROKEN_TRUST_CONTRIBUTION == 0.5  # the blessed number
            after = ex._combat._pair_contribution_scale(a, b)
            assert 0.0 < after < base, (nation, a.name, b.name, base, after)
            assert after == pytest.approx(base * 0.5)

    def test_wary_and_above_are_untouched(self):
        w = _boot()
        ex = CommandExecutor()
        a, b = w.marshals["Ney"], w.marshals["Davout"]
        base = ex._combat._pair_contribution_scale(a, b)
        b.trust.modify(30 - b.trust.value)
        assert b.trust.value == 30
        assert ex._combat._pair_contribution_scale(a, b) == base

    def test_the_committed_strength_carries_it(self):
        w = _boot()
        ex = CommandExecutor()
        a, b = w.marshals["Ney"], w.marshals["Davout"]
        before = ex._combat._committed_reinforcement_strength(a, [a, b], w)
        b.trust.modify(-100)
        after = ex._combat._committed_reinforcement_strength(a, [a, b], w)
        assert after == pytest.approx(before * ex._combat.BROKEN_TRUST_CONTRIBUTION)

    def test_a_hostile_pair_stays_at_zero(self):
        w = _boot()
        ex = CommandExecutor()
        a, b = w.marshals["Ney"], w.marshals["Davout"]
        a.relationships[b.name] = -2
        b.trust.modify(-100)
        assert ex._combat._pair_contribution_scale(a, b) == 0.0

    def test_lever_down_reads_no_trust(self, monkeypatch):
        w = _boot()
        ex = CommandExecutor()
        _flip(monkeypatch, type(ex._combat), "TRUST_REACHES_THE_FIELD", False)
        a, b = w.marshals["Ney"], w.marshals["Davout"]
        base = ex._combat._pair_contribution_scale(a, b)
        b.trust.modify(-100)
        assert ex._combat._pair_contribution_scale(a, b) == base


# ═══════════════════════════════════════════════════════════════════════
# FA-S2-D1 — the enemy waits one turn
# ═══════════════════════════════════════════════════════════════════════
class TestS2D1TheEnemyWaitsOneTurn:
    """The row's own shape: Ney's 3,000 at Belgium, on France's soil, with
    three Austrian corps standing over him. Before: six Austrian actions
    captured him in one phase (3,000 -> 1,075 -> 400 -> captured). After: the
    first attack raises the question, the rest of the phase waits, and the
    NEXT phase resolves it by his own character (FA-1). Seeded: the fate
    roll is combat's RNG."""

    @staticmethod
    def _world(loc="Belgium", third_at=None):
        ney = MarshalFactory.infantry(name="Ney", location=loc, strength=3000, personality="aggressive")
        mack = MarshalFactory.enemy(name="Mack", location=loc, nation="Austria", strength=40000)
        charles = MarshalFactory.enemy(name="Charles", location=loc, nation="Austria", strength=30000)
        john = MarshalFactory.enemy(name="John", location=third_at or loc, nation="Austria", strength=25000)
        world = WorldFactory.with_marshals([ney, mack, charles, john])
        key = "|".join(sorted(["France", "Austria"]))
        world.diplomatic_states[key] = "WAR"
        world.war_start_turns[key] = world.current_turn
        return world, ney

    @classmethod
    def _phase(cls, actions=6, seed=1, **kw):
        import random
        random.seed(seed)
        world, ney = cls._world(**kw)
        ex = CommandExecutor()
        ai = EnemyAI(ex)
        world.nation_actions["Austria"] = actions
        with _quiet():
            results = ai.process_nation_turn("Austria", world, {"world": world, "executor": ex})
        return world, ney, ai, ex, results

    def test_the_question_survives_the_phase(self):
        for seed in (1, 2, 3):
            world, ney, ai, ex, results = self._phase(seed=seed)
            ask = ney.pending_interrupt
            assert ask and ask["interrupt_type"] == "last_stand", (seed, ask)
            assert ask["raised_by_ai"] is True and ask["raised_turn"] == int(world.current_turn)
            assert not ney.captured_by and ney.strength > 0 and ney.location == "Belgium", (seed, ney.strength, ney.location)
            assert world.get_region("Belgium").controller == "France"
            assert ai._freshly_asked(ney, world) is True
            # ONE attack — the one that asked; the other five actions were not spent on him
            attacks = [r for r in results if (r.get("ai_action") or {}).get("action") == "attack"]
            assert len(attacks) == 1, [(r.get("ai_action") or {}) for r in results]

    def test_the_co_located_corps_hold_over_him(self):
        """P0 reads the WORLD's occupancy lookup — the wait meets it at the
        brake site, so the corps standing over him HOLD (they do not read
        the field as empty and go elsewhere, and they do not strike)."""
        world, ney, ai, ex, results = self._phase()
        for name in ("Mack", "Charles", "John"):
            assert world.marshals[name].location == "Belgium"
        assert ney.pending_interrupt and ney.pending_interrupt["interrupt_type"] == "last_stand"

    def test_the_next_phase_resolves_it_by_his_own_character(self):
        world, ney, ai, ex, results = self._phase()
        world.current_turn += 1
        assert ai._freshly_asked(ney, world) is False
        world.nation_actions["Austria"] = 6
        with _quiet():
            ai.process_nation_turn("Austria", world, {"world": world, "executor": ex})
        assert ney.pending_interrupt is None
        assert ney.captured_by or ney.location != "Belgium" or ney.strength == 0

    def test_a_question_the_players_own_attack_raised_does_not_hide_him(self):
        """The stamp is TRUE, not a constant: outside an AI phase — the
        player's own typed attack cornering his man — `raised_by_ai` is
        False. He had his phase to answer; the enemy does not wait, and
        FA-1 resolves him by his own character."""
        import random
        random.seed(1)
        world, ney = self._world()
        ney.morale = 30  # the defeat breaks him (the slice-2 grind fixture's idiom)
        ex = CommandExecutor()
        with _quiet():
            res = ex.execute({"command": {"type": "specific", "marshal": "Ney",
                                          "action": "attack", "target": "Mack"}},
                             {"world": world, "executor": ex})
        ask = ney.pending_interrupt
        assert ask and ask["interrupt_type"] == "last_stand", (res.get("message"), ask)
        assert ask["raised_by_ai"] is False
        assert ask["raised_turn"] == int(world.current_turn)
        ai = EnemyAI(ex)
        assert ai._freshly_asked(ney, world) is False
        assert any(m.name == "Ney" for m in ai._get_enemy_contacts("Austria", world))
        world.nation_actions["Austria"] = 6
        with _quiet():
            ai.process_nation_turn("Austria", world, {"world": world, "executor": ex})
        assert ney.pending_interrupt is None
        assert ney.captured_by or ney.location != "Belgium" or ney.strength == 0

    def test_the_ai_phase_marker_is_set_only_while_the_court_acts(self):
        world, ney = self._world()
        ex = CommandExecutor()
        ai = EnemyAI(ex)
        seen = {}
        inner = ai._process_nation_turn_marked

        def spy(nation, w, gs):
            seen["during"] = getattr(w, "_ai_phase_nation", "")
            return inner(nation, w, gs)

        ai._process_nation_turn_marked = spy
        assert getattr(world, "_ai_phase_nation", "") == ""
        world.nation_actions["Austria"] = 0
        with _quiet():
            ai.process_nation_turn("Austria", world, {"world": world, "executor": ex})
        assert seen["during"] == "Austria"
        assert getattr(world, "_ai_phase_nation", "") == ""

    def test_yesterdays_question_does_not_hide_him(self):
        world, ney = self._world()
        ai = EnemyAI(CommandExecutor())
        ney.pending_interrupt = {"interrupt_type": "last_stand", "marshal": "Ney", "raised_by_ai": True,
                                 "raised_turn": int(world.current_turn) - 1, "location": "Belgium"}
        assert ai._freshly_asked(ney, world) is False

    def test_lever_down_answers_it_in_the_same_phase(self, monkeypatch):
        from backend.ai import enemy_ai as EA
        _flip(monkeypatch, EA, "THE_ENEMY_WAITS_ONE_TURN", False)
        world, ney, ai, ex, results = self._phase()
        assert ney.captured_by == "Austria" and ney.strength == 0
        assert ney.pending_interrupt is None
        attacks = [r for r in results if (r.get("ai_action") or {}).get("action") == "attack"]
        assert len(attacks) >= 2

    def test_the_wait_is_read_where_a_target_is_chosen_never_where_occupancy_is(self):
        """The three target-choosing reads skip him; the occupancy read
        still finds him standing there — hidden from it, his province read
        as undefended and P4.5 mounted the capture attack the wait exists
        to hold back."""
        world, ney, ai, ex, results = self._phase()
        assert all(m.name != "Ney" for m in ai._get_enemy_contacts("Austria", world))
        mack = world.marshals["Mack"]
        assert all(m.name != "Ney" for m in ai._get_hostile_marshals_in_same_region(mack, world))
        field = world.get_live_visible_enemies_in_region("Belgium", "Austria")
        assert any(m.name == "Ney" for m in field)
        assert all(m.name != "Ney" for m in ai._engageable_enemies(mack, field, "Austria", world))
        assert any(m.name == "Ney" for m in ai._get_hostile_marshals_in_region("Belgium", "Austria", world))

    def test_an_adjacent_corps_neither_strikes_nor_captures_his_province(self):
        """John ADJACENT at Netherlands: after Mack's attack raises the
        question, P4 has no contact and P4.5 reads Belgium as HELD."""
        for seed in (1, 2):
            world, ney, ai, ex, results = self._phase(seed=seed, third_at="Netherlands")
            assert ney.pending_interrupt and ney.pending_interrupt["interrupt_type"] == "last_stand"
            assert world.get_region("Belgium").controller == "France"
            assert not ney.captured_by and ney.strength > 0
            attacks = [(r.get("ai_action") or {}) for r in results if (r.get("ai_action") or {}).get("action") == "attack"]
            assert len(attacks) == 1 and attacks[0]["marshal"] in ("Mack", "Charles"), attacks
            john = world.marshals["John"]
            with _quiet():
                capture = ai._find_undefended_capture(john, "Austria", world)
            assert not capture or capture.get("target") != "Belgium", capture
