"""Pre-Deploy S13b part 2, slice S13b-3 — DD-B's field rows, DDB-13 … 20
and DDB-36 … 44 (October 15, 2026; `docs/BUG_FIXES.md` §DD-B; rules
`SYSTEMS_REFERENCE.md` §117). Driven through the real endpoints on the 1805
boot (the in-process TestClient), never a mocked executor.

  DDB-13  the Gold counter carries the projected net; the end-turn gate warns
          of a negative treasury; the muster quotes the materiel bill; the
          battle's reply names it directly under the battle's lines.
  DDB-14  the player's lead is refused a field on soil France is at peace
          with, as his supporters are; a joiner's muster line says where he
          will stand; the works halt sends the joiners home.
  DDB-15  an attack on a province where nothing fights raises no strength concern.
  DDB-16  the last-stand card names each road's chance; the answer prints its
          fate; the desk answers a prisoner with where and since when.
  DDB-17  the charge card says it goes in alone; the narrative line is chosen
          in the outcome's register.
  DDB-18  the counsel never offers a hopeless attack.
  DDB-19  the attack objection reads the muster's expected totals.
  DDB-20  a SUPPORT onto the ally's contested field stands at the approach;
          SUPPORT of a marshal on the same field passes the engagement gate.
  DDB-36  the posture header claims the band's burden only when it is one;
          the cautious line gives the solo figures.
  DDB-37  the battle event carries `advanced_to`; "Where was" skips by-rule no-shows.
  DDB-38  a forced retreat clears the counter-punch; a stalemate's diorama
          reads the field.
  DDB-39  "Morale dropped" only when it fell.
  DDB-40  fortify is priced from the stance.
  DDB-41  an objection can be withdrawn at no cost.
  DDB-42  a win on one's own soil, and a capture of titled soil, add no alarm;
          the result names any alarm it adds.
  DDB-43  a province passing between other courts is a dispatch line; our corps
          on soil whose entry just closed are told.
  DDB-44  a move into a province the stack outruns quotes the supply loss.
"""
from __future__ import annotations

import contextlib
import io
import random
from pathlib import Path
from types import SimpleNamespace

import pytest

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "godot-client" / "project-sovereign" / "scripts"


@pytest.fixture
def client(monkeypatch):
    import backend.main as M
    from backend.commands.parser import CommandParser
    from fastapi.testclient import TestClient
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    with contextlib.redirect_stdout(io.StringIO()):
        M._reset_world_state()
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    return TestClient(M.app), M.world


def _cmd(c, text: str) -> dict:
    with contextlib.redirect_stdout(io.StringIO()):
        return c.post("/command", json={"command": text}).json()


def _post(c, path: str, body: dict) -> dict:
    with contextlib.redirect_stdout(io.StringIO()):
        return c.post(path, json=body).json()


def _src(name: str) -> str:
    return (SCRIPTS / name).read_text(encoding="utf-8")


def _combat():
    import backend.main as M
    return M.executor._combat


def _muster(w, lead: str, enemy: str) -> dict:
    with contextlib.redirect_stdout(io.StringIO()):
        return _combat()._build_muster_preview(
            w.get_marshal(lead), w.get_marshal(enemy), w, {"world": w})


def _relocate(w, **where) -> None:
    for name, loc in where.items():
        w.get_marshal(name).location = loc
    w._build_marshal_index()
    w.invalidate_active_nations_cache()
    w.calculate_visibility()


def _attack_mack_at_swabia(c, w, mack_strength: int = 52000, seed: int = 7) -> dict:
    """Davout (cautious, 26k, Rhineland) on Mack at Swabia, the boot's own
    board: Ney beside him, Soult (literal) and the Emperor at Lorraine,
    Lannes and Murat at Franche-Comte — every corps in reach."""
    w.get_marshal("Mack").strength = mack_strength
    w.calculate_visibility()
    random.seed(seed)
    return _cmd(c, "Davout, attack Mack")


# ═══════════════════════════════════════════════════════════════════════════
# DDB-13 — the treasury's net, said before End Turn and at the battle
# ═══════════════════════════════════════════════════════════════════════════

class TestDDB13:
    def test_every_response_carries_the_ledgers_projected_net(self, client):
        c, w = client
        from backend.game_logic.ledger import chest_forecast
        r = _cmd(c, "status")
        assert r["gold_projected_net"] == chest_forecast(w, "France")["net"]

    def test_the_muster_quotes_the_battles_materiel_bill(self, client):
        c, w = client
        from backend.models.world_state import MATERIEL_RATE
        note = _muster(w, "Davout", "Mack")["materiel_note"]
        assert note.startswith(
            f"Materiel: every 1,000 men we lose costs {int(round(1000 * MATERIEL_RATE))}g")
        assert "a hard day (15% of the" in note

    def test_the_battle_names_its_bill_under_the_battle_and_the_chest_after(self, client):
        c, w = client
        msg = _attack_mack_at_swabia(c, w)["message"]
        assert "Materiel: every 1,000 men we lose" in msg, msg  # the muster's quote
        bill = msg.index("[Materiel] Guns, horses and stores lost")
        assert f"Our treasury stands at {int(w.gold):,} gold." in msg
        # Directly under the battle's own lines: before the advance, the
        # conquest and the alarm.
        for rider in ("advances into", "[Alarm]"):
            if rider in msg:
                assert bill < msg.index(rider), msg

    def test_the_client_shows_the_net_and_gates_a_negative_treasury(self):
        src = _src("main.gd")
        assert '"gold_projected_net"' in src
        assert "next turn" in src
        assert "func _treasury_goes_negative() -> bool:" in src
        assert ("if _current_lapsing_count > 0 or not _current_decision_names.is_empty() "
                "or (_treasury_goes_negative() and not _treasury_warned):") in src


# ═══════════════════════════════════════════════════════════════════════════
# DDB-14 — where the corps that march to the guns stand, and whose soil
# ═══════════════════════════════════════════════════════════════════════════

class TestDDB14:
    def test_the_lead_is_refused_a_field_on_peace_soil(self, client):
        c, w = client
        _relocate(w, Mack="Nassau")
        ap = int(w.actions_remaining)
        r = _cmd(c, "Davout, attack Mack")
        assert r.get("success") is False, r.get("message")
        assert ("Nassau is Hesse's soil, and we are at peace with Hesse — "
                "no corps of ours may take the field there") in r["message"]
        assert w.get_marshal("Davout").location == "Rhineland"
        assert int(w.actions_remaining) == ap
        assert not r.get("battle_report")

    def test_no_objection_is_raised_before_the_refusal(self, client):
        """Found by this module: the objection fired first, so Insist was
        paid for an attack the executor then refused (the PF-4 idiom)."""
        c, w = client
        _relocate(w, Mack="Nassau")
        w.get_marshal("Davout").modify_trust(-30)
        w.get_marshal("Mack").strength = 300000  # the board that objects on war soil
        w.calculate_visibility()
        for seed in range(4):
            random.seed(seed)
            r = _cmd(c, "Davout, attack Mack")
            assert not r.get("objection") and not r.get("pending_objection"), r.get("message")
            assert w.pending_objection is None
            assert "we are at peace with Hesse" in r["message"]

    def test_an_army_on_its_own_courts_soil_is_the_war_purpose_road(self, client):
        """Found by the hook: Brunswick on Prussia's own soil is no third
        party's field — the attack declares war, as it always did."""
        c, w = client
        r = _cmd(c, "Bernadotte, attack Brunswick")
        assert "cannot march on" not in str(r.get("message")), r.get("message")
        assert "war purpose against Prussia" in str(r.get("message")) or r.get("pending_objection"), r.get("message")

    def test_the_ai_lead_keeps_the_frontier_rule(self, client):
        """GR5's named difference: the AI's lead keeps PT-F1 (the School of
        War's counter-blow on Senarmont in Bavaria still lands)."""
        c, w = client
        from backend.commands.combat_executor import field_on_peace_soil
        _relocate(w, Davout="Nassau")
        assert field_on_peace_soil(_combat(), w.get_marshal("Mack"), "Nassau", w) is None
        # ...and the player's own lead on the same soil is refused.
        _relocate(w, Davout="Rhineland", Mack="Nassau")
        block = field_on_peace_soil(_combat(), w.get_marshal("Davout"), "Nassau", w)
        assert block is not None and block["owner"] == "Hesse"

    def test_a_joiners_muster_line_says_where_he_will_stand(self, client):
        c, w = client
        preview = _muster(w, "Davout", "Mack")
        rows = {r["marshal"]: r for r in preview["rows"]}
        assert rows["Ney"]["stands_after"] == "— and will stand at Swabia"
        msg = _attack_mack_at_swabia(c, w)["message"]
        assert "— and will stand at Swabia" in msg

    def test_the_works_halt_sends_the_joiners_home(self, client):
        c, w = client
        from backend.commands.combat_executor import returns_reinforcers_from_works
        davout, ney = w.get_marshal("Davout"), w.get_marshal("Ney")
        ney.location = "Swabia"
        ctx = SimpleNamespace(atk_participants=[davout, ney], marshal=davout,
                              reinforcer_origin={"Ney": "Rhineland"},
                              target_location="Swabia")
        assert returns_reinforcers_from_works(ctx) == " Ney returns to Rhineland — the works still hold."
        assert ney.location == "Rhineland" and davout.location == "Rhineland"


# ═══════════════════════════════════════════════════════════════════════════
# DDB-15 — no strength concern against a walk-in
# ═══════════════════════════════════════════════════════════════════════════

class TestDDB15:
    def test_a_province_where_nothing_fights_raises_no_concern(self, client):
        c, w = client
        from backend.commands.objection_v2 import ConcernLevel, evaluate_cautious
        _relocate(w, ArchdukeJohn="Vienna")  # Tyrol stands empty
        bernadotte = w.get_marshal("Bernadotte")  # cautious, at Franconia
        assert not [m for m in w.get_marshals_in_region("Tyrol") if m.strength > 0]
        order = {"action": "attack", "target": "Tyrol"}
        assert evaluate_cautious(bernadotte, "attack", order, {"world": w}) == ConcernLevel.NONE

    def test_the_walk_in_is_taken_without_an_objection(self, client):
        c, w = client
        _relocate(w, ArchdukeJohn="Vienna")
        r = _cmd(c, "Bernadotte, attack Tyrol")
        assert not r.get("objection") and not r.get("pending_objection"), r.get("message")


# ═══════════════════════════════════════════════════════════════════════════
# DDB-16 — the cornered marshal's fate, told
# ═══════════════════════════════════════════════════════════════════════════

def _corner(w, name="Ney"):
    ney, mack = w.get_marshal(name), w.get_marshal("Mack")
    ney.strength = 3000
    ney.pending_interrupt = {
        "interrupt_type": "last_stand", "marshal": ney.name, "enemy": mack.name,
        "enemy_nation": mack.nation, "location": ney.location,
        "options": ["fight_to_the_last", "attempt_breakout"],
        "message": f"{ney.name} is cornered.",
    }
    return ney, mack


class TestDDB16:
    def test_the_card_names_each_roads_chance(self, client):
        combat = _combat()
        line = combat.last_stand_odds_line()
        breakout = int(round((combat.MARSHAL_FATE_ESCAPE_CHANCE
                              - combat.LAST_STAND_BREAKOUT_PENALTY) * 100))
        assert f"Attempt a breakout: {breakout}% he cuts his way out, {100 - breakout}% he is taken." in line
        assert f"one final defense at +{int(round(combat.LAST_STAND_BONUS * 100))}%" in line
        assert "the survivors are taken, certainly" in line

    @pytest.mark.parametrize("roll,fate", [(0.0, "escaped"), (0.999, "captured")])
    def test_the_breakout_prints_its_fate(self, client, monkeypatch, roll, fate):
        c, w = client
        _corner(w)
        monkeypatch.setattr(random, "random", lambda: roll)
        r = _post(c, "/strategic_response", {"marshal_name": "Ney", "response_type": "last_stand",
                                             "choice": "attempt_breakout"})
        assert r.get("last_stand_fate") == fate, r.get("message")
        assert not r.get("battle_diorama"), "a peeked earlier defeat is not this answer's"

    def test_the_last_stand_prints_its_fate(self, client):
        c, w = client
        _corner(w)
        r = _post(c, "/strategic_response", {"marshal_name": "Ney", "response_type": "last_stand",
                                             "choice": "fight_to_the_last"})
        assert r.get("last_stand_fate") == "fallen", r.get("message")

    def test_the_desk_answers_a_prisoner(self, client):
        c, w = client
        ney = w.get_marshal("Ney")
        ney.captured_by, ney.captured_turn, ney.location = "Austria", 3, "Vienna"
        msg = _cmd(c, "where is Ney")["message"]
        assert "prisoner of Austria, held at Vienna since turn 3" in msg, msg

    def test_the_client_prints_the_fate_first(self):
        src = _src("main.gd")
        assert 'response.get("last_stand_fate"' in src or "last_stand_fate" in src


# ═══════════════════════════════════════════════════════════════════════════
# DDB-17 — the charge goes in alone; the line follows the outcome
# ═══════════════════════════════════════════════════════════════════════════

class TestDDB17:
    def test_the_card_says_the_charge_goes_in_alone(self):
        assert "charges ALONE — no corps joins a charge" in _src("glorious_charge_dialog.gd")

    @pytest.mark.parametrize("outcome,banned", [
        ("defender_victory", ("brilliant", "devastating", "perfect coordination",
                              "decisive", "overwhelming")),
        ("attacker_victory", ("falters", "collapses", "stumble", "struggles",
                              "difficult", "fierce resistance")),
        ("stalemate", ("brilliant", "devastating", "perfect coordination",
                       "decisive", "overwhelming")),
    ])
    def test_the_narrative_reads_in_the_outcomes_register(self, client, outcome, banned):
        c, w = client
        from backend.game_logic.combat import CombatResolver
        murat, mack = w.get_marshal("Murat"), w.get_marshal("Mack")
        resolver = CombatResolver()
        for crit_s, crit_f, roll in ((True, False, 12), (False, True, 2), (False, False, 10),
                                     (False, False, 3)):
            for seed in range(6):
                random.seed(seed)
                text = resolver._generate_description(
                    murat, mack, outcome, 1000, 1000,
                    {"modified": roll, "is_critical_success": crit_s,
                     "is_critical_failure": crit_f}).lower()
                assert not any(b in text.split(".")[0] for b in banned), (outcome, text)


# ═══════════════════════════════════════════════════════════════════════════
# DDB-18 — no hopeless attack in the counsel
# ═══════════════════════════════════════════════════════════════════════════

class TestDDB18:
    def test_the_emperors_few_hundred_are_not_offered_against_mack(self, client):
        c, w = client
        from backend.ai import counsel
        far = {n: "Paris" for n in ("Davout", "Ney", "Soult", "Lannes", "Murat", "Bernadotte")}
        _relocate(w, Napoleon="Rhineland", **far)
        w.get_marshal("Napoleon").strength = 400
        assert counsel._hopeless_attack(w, w.get_marshal("Napoleon"), w.get_marshal("Mack"))
        lines = counsel.military_counsel(w, "France", limit=8)
        assert not any("attack Mack" in line for line in lines), lines

    def test_a_fair_attack_is_still_offered(self, client):
        c, w = client
        from backend.ai import counsel
        lines = counsel.military_counsel(w, "France", limit=8)
        assert any("attack Mack" in line for line in lines), lines


# ═══════════════════════════════════════════════════════════════════════════
# DDB-19 — the objection and the band read one attack
# ═══════════════════════════════════════════════════════════════════════════

class TestDDB19:
    def test_the_objection_ratio_is_the_musters_expected_totals(self, client):
        c, w = client
        from backend.commands.objection_v2 import _get_attack_odds_ratio
        from backend.models.personality import _get_strength_ratio
        w.muster_hint_shown = False
        preview = _muster(w, "Davout", "Mack")
        w.muster_hint_shown = False
        ours = preview["attacker"]["committed_strength"]
        theirs = preview["target"]["committed_strength"]
        assert ours > w.get_marshal("Davout").strength, "the joiners are counted"
        davout = w.get_marshal("Davout")
        ratio = _get_attack_odds_ratio(davout, {"action": "attack", "target": "Mack"}, {"world": w})
        assert ratio == pytest.approx(theirs / ours)
        assert _get_strength_ratio(davout, "Mack", w) == pytest.approx(ours / theirs)
        assert w.muster_hint_shown is False, "a read is not a showing"


# ═══════════════════════════════════════════════════════════════════════════
# DDB-20 — the muster's "order him to support" can be carried out
# ═══════════════════════════════════════════════════════════════════════════

class TestDDB20:
    def test_support_onto_the_allys_contested_field_stands_at_the_approach(self, client):
        c, w = client
        _relocate(w, Davout="Swabia")  # Davout and Mack share contested Swabia
        r = _cmd(c, "Soult, support Davout")
        assert "at the approach to Swabia" in r["message"], r["message"]
        soult = w.get_marshal("Soult")
        assert soult.location == "Lorraine"
        assert soult.strategic_order is not None
        assert soult.strategic_order.command_type == "SUPPORT"

    def test_support_of_a_marshal_on_the_same_field_passes_the_gate(self, client):
        c, w = client
        _relocate(w, Davout="Swabia", Soult="Swabia")
        r = _cmd(c, "Soult, support Davout")  # literal: no objection of his own
        soult = w.get_marshal("Soult")
        assert soult.strategic_order is not None, r["message"]
        assert soult.strategic_order.command_type == "SUPPORT"

    def test_the_turn_tick_keeps_the_order_standing(self, client):
        c, w = client
        from backend.commands.strategic import support_stands_at_approach
        order = SimpleNamespace(command_type="SUPPORT")
        davout = w.get_marshal("Davout")
        assert support_stands_at_approach(order, davout, davout.location)
        assert not support_stands_at_approach(SimpleNamespace(command_type="MOVE_TO"),
                                              davout, davout.location)


# ═══════════════════════════════════════════════════════════════════════════
# DDB-36 — the posture header and the cautious line
# ═══════════════════════════════════════════════════════════════════════════

class TestDDB36:
    def test_the_header_claims_the_burden_only_when_it_is_one(self, client):
        c, w = client
        davout, mack = w.get_marshal("Davout"), w.get_marshal("Mack")
        davout.stance = type(davout.stance)["DEFENSIVE"]
        hurts = _combat()._posture_note(davout, mack, w, band_hurts=True)
        held = _combat()._posture_note(davout, mack, w, band_hurts=False)
        assert hurts.startswith("The band weighs more than the men: ")
        assert held.startswith("Standing modifiers, already in the band: ")
        assert hurts.split(": ", 1)[1] == held.split(": ", 1)[1]

    def test_the_cautious_line_gives_the_solo_figures(self, client):
        c, w = client
        msg = _attack_mack_at_swabia(c, w, mack_strength=60000)["message"]
        assert "on his own numbers — his own 26k against 60k" in msg, msg


# ═══════════════════════════════════════════════════════════════════════════
# DDB-37 — the advance on the event; by-rule no-shows are not failures
# ═══════════════════════════════════════════════════════════════════════════

class TestDDB37:
    def test_the_battle_event_carries_the_advance(self, client):
        c, w = client
        r = _attack_mack_at_swabia(c, w, mack_strength=4000)
        battles = [e for e in (r.get("events") or []) if e.get("type") == "battle"]
        assert battles, r.get("message")
        assert w.get_marshal("Davout").location == "Swabia"
        assert battles[0].get("advanced_to") == "Swabia"

    def test_where_was_skips_a_literal_marshal_without_orders(self):
        from backend.game_logic.battle_report import _pick_observation
        result = {"outcome": "attacker_victory", "attacker_nation": "France",
                  "attacker": {"casualties": 2000}, "defender": {"casualties": 9000},
                  "attacker_original_strength": 26000, "defender_original_strength": 30000,
                  "coordination": {"reinforcements": [
                      {"marshal": "Soult", "arrived": False, "reason": "literal_personality"},
                      {"marshal": "Ney", "arrived": True}]}}
        for seed in range(5):
            random.seed(seed)
            text = _pick_observation(result, "France") or ""
            assert "Soult" not in text, text

    def test_the_enemy_phase_says_the_advance(self):
        assert "and advances into" in _src("enemy_phase_dialog.gd")


# ═══════════════════════════════════════════════════════════════════════════
# DDB-38 — the routed have no free strike; the diorama reads the field
# ═══════════════════════════════════════════════════════════════════════════

class TestDDB38:
    def test_a_forced_retreat_clears_the_counter_punch(self, client):
        c, w = client
        from backend.commands.combat_executor import forced_retreat_clears_counter_punch
        bern = w.get_marshal("Bernadotte")
        bern.counter_punch_available, bern.counter_punch_turns = True, 1
        forced_retreat_clears_counter_punch(bern, w)
        assert bern.counter_punch_available is False and bern.counter_punch_turns == 0

    def test_every_forced_retreat_passes_the_seam(self):
        import inspect
        from backend.commands.combat_executor import CombatExecutor
        src = inspect.getsource(CombatExecutor._apply_forced_retreat_or_break)
        assert "forced_retreat_clears_counter_punch(marshal, world)" in src

    @pytest.mark.parametrize("side,field,register", [
        ("defender", {"defender_routed": True}, "defeat"),
        ("defender", {"province_taken": True}, "defeat"),
        ("attacker", {"defender_routed": True}, "triumph"),
        ("attacker", {"province_taken": True}, "triumph"),
        ("attacker", {"attacker_routed": True}, "defeat"),
        ("attacker", {}, "grim"),
    ])
    def test_a_stalemates_register_reads_the_field(self, side, field, register):
        from backend.game_logic.battle_diorama import derive_register
        assert derive_register(side, "stalemate", field=field) == register


# ═══════════════════════════════════════════════════════════════════════════
# DDB-39 — "dropped" only when it fell
# ═══════════════════════════════════════════════════════════════════════════

class TestDDB39:
    def test_a_rising_morale_is_still_low_not_dropped(self, client):
        c, w = client
        w.get_marshal("Soult").morale = 30  # Soult stands in French Lorraine
        w.gold = 5000
        r = _cmd(c, "recruit infantry for soult")
        assert r.get("success"), r.get("message")
        assert "Morale is still low at" in r["message"], r["message"]
        assert "Morale dropped" not in r["message"]
        assert w.get_marshal("Soult").morale >= 30


# ═══════════════════════════════════════════════════════════════════════════
# DDB-40 — fortify, priced from the stance
# ═══════════════════════════════════════════════════════════════════════════

class TestDDB40:
    def test_from_neutral_the_price_is_two_actions(self, client):
        c, w = client
        note = _muster(w, "Davout", "Mack")["province_fights_note"]
        assert "fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify)" in note

    def test_from_defensive_it_is_one(self, client):
        c, w = client
        for m in w.marshals.values():
            if m.nation == "France":
                m.stance = type(m.stance)["DEFENSIVE"]
        note = _muster(w, "Davout", "Mack")["province_fights_note"]
        assert "fortify him (1 AP)" in note
        assert w._action_costs["fortify"] == 1


# ═══════════════════════════════════════════════════════════════════════════
# DDB-41 — Cancel withdraws the order at no cost
# ═══════════════════════════════════════════════════════════════════════════

class TestDDB41:
    def _object(self, c, w):
        davout, mack = w.get_marshal("Davout"), w.get_marshal("Mack")
        _relocate(w, Davout="Lorraine")
        davout.strength = 12000
        davout.modify_trust(-30)
        mack.strength = 300000
        w.calculate_visibility()
        r = _cmd(c, "Davout, attack Mack")
        assert r.get("pending_objection") or r.get("objection"), r.get("message")

    def test_cancel_spends_nothing(self, client):
        c, w = client
        self._object(c, w)
        davout = w.get_marshal("Davout")
        trust, ap, auth = davout.trust.value, int(w.actions_remaining), w.authority_tracker.authority
        r = _post(c, "/respond_to_objection", {"choice": "cancel"})
        assert r.get("success") is True and r.get("objection_withdrawn") is True, r
        assert "withdrawn" in r["message"] and "nothing is spent" in r["message"]
        assert w.pending_objection is None
        assert davout.trust.value == trust and int(w.actions_remaining) == ap
        assert w.authority_tracker.authority == auth
        assert davout.location == "Lorraine" and not r.get("battle_report")

    def test_the_dialog_offers_cancel(self):
        src = _src("objection_dialog.gd")
        assert '"cancel"' in src and "Cancel" in src


# ═══════════════════════════════════════════════════════════════════════════
# DDB-42 — Europe fears the conqueror, read on the province
# ═══════════════════════════════════════════════════════════════════════════

def _france_rows(w, before):
    return [r for r in w.threat_sources_this_turn[before:] if r.get("target") == "France"]


class TestDDB42:
    def test_a_win_on_our_own_soil_adds_no_alarm(self, client):
        c, w = client
        _relocate(w, Mack="Lorraine", Soult="Paris", Napoleon="Paris")
        w.get_marshal("Mack").strength = 4000
        before = len(w.threat_sources_this_turn)
        random.seed(3)
        r = _cmd(c, "Davout, attack Mack")
        assert r.get("battle_report"), r.get("message")
        assert not [x for x in _france_rows(w, before)
                    if x.get("source") in ("battle_win", "decisive_victory")]
        assert "[Alarm]" not in r["message"]

    def test_a_win_on_foreign_soil_says_what_it_adds(self, client):
        c, w = client
        before = len(w.threat_sources_this_turn)
        r = _attack_mack_at_swabia(c, w, mack_strength=30000)
        rows = _france_rows(w, before)
        if any(x.get("source") == "battle_win" for x in rows):
            assert "[Alarm] Europe's alarm rises +" in r["message"]
            assert "Won a battle +3" in r["message"]

    def test_a_field_the_win_itself_conquered_is_no_home_soil(self, client):
        """Found by the slice's own re-run: the pipeline asks after the
        conquest, so a captured field read as the victor's own."""
        c, w = client
        from backend.commands.combat_executor import battle_win_on_own_soil
        assert battle_win_on_own_soil(w, "Lorraine", "France") is True
        assert battle_win_on_own_soil(w, "Lorraine", "France", conquered=True) is False

    def test_recovering_titled_soil_is_no_conquest(self):
        from backend.game_logic import game_end as GE
        from backend.models.world_state import capture_recovers_title
        assert capture_recovers_title({"kind": GE.TITLE_TREATY, "holder": "France"}, "France")
        assert capture_recovers_title({"kind": GE.TITLE_CONQUEST, "from": "France"}, "France")
        assert not capture_recovers_title({"kind": GE.TITLE_CONQUEST, "from": "Austria"}, "France")
        assert not capture_recovers_title({}, "France")


# ═══════════════════════════════════════════════════════════════════════════
# DDB-43 — a province changing hands between other courts
# ═══════════════════════════════════════════════════════════════════════════

class TestDDB43:
    def test_the_change_and_the_closed_soil_are_dispatch_lines(self, client):
        c, w = client
        from backend.models.world_state import announce_third_party_capture
        before = len(w.pending_dispatch_events)
        # Bernadotte stands in Bavarian Franconia; Prussia (at peace with
        # France, no open borders) takes it.
        w.get_region("Franconia").controller = "Prussia"
        announce_third_party_capture(w, "Franconia", "Bavaria", "Prussia")
        events = w.pending_dispatch_events[before:]
        kinds = [e.get("event_type") or e.get("type") for e in events]
        assert "province_changed_hands" in kinds, events
        assert "corps_on_closed_soil" in kinds, events
        from backend.game_logic.dispatch import _DIPLOMATIC_EVENT_TEMPLATES as T
        closed = next(e for e in events if (e.get("event_type") or e.get("type")) == "corps_on_closed_soil")
        line = T["corps_on_closed_soil"].format(**closed.get("template_vars", closed.get("vars", {})))
        assert line.startswith("Bernadotte stands on Franconia, now Prussia's soil")
        assert "no corps of ours may enter it again" in line

    def test_a_change_the_player_is_party_to_is_not_announced_here(self, client):
        c, w = client
        from backend.models.world_state import announce_third_party_capture
        before = len(w.pending_dispatch_events)
        announce_third_party_capture(w, "Swabia", "Bavaria", "France")
        assert len(w.pending_dispatch_events) == before


# ═══════════════════════════════════════════════════════════════════════════
# DDB-44 — the supply warning on the move
# ═══════════════════════════════════════════════════════════════════════════

class TestDDB44:
    def test_a_move_into_a_province_the_stack_outruns_quotes_the_loss(self, client):
        c, w = client
        w.get_marshal("Soult").strength = 150000  # Lorraine already crowded
        r = _cmd(c, "Davout, move to Lorraine")
        assert r.get("success"), r.get("message")
        forecast = w.supply_forecast("Lorraine", "France")
        assert forecast and forecast["loss"] > 0
        assert (f"Lorraine feeds {forecast['fed']:,}; the {forecast['standing']:,} men "
                f"standing there would lose ~{forecast['loss']:,} a turn") in r["message"], r["message"]

    def test_a_march_says_it_where_its_step_stops(self, client):
        c, w = client
        w.get_marshal("Soult").strength = 150000
        r = _cmd(c, "Davout, march to Lorraine")
        assert w.get_marshal("Davout").location == "Lorraine", r.get("message")
        forecast = w.supply_forecast("Lorraine", "France")
        assert f"Lorraine feeds {forecast['fed']:,}" in r["message"], r["message"]

    def test_the_marchs_turn_reports_say_it_too(self):
        import inspect
        from backend.commands import strategic
        src = inspect.getsource(strategic.StrategicOrderProcessor)
        assert src.count("_supply_warning(world, marshal)") >= 2

    def test_a_province_that_carries_them_says_nothing(self, client):
        c, w = client
        _relocate(w, Soult="Paris", Napoleon="Paris")
        r = _cmd(c, "Davout, move to Lorraine")
        assert w.supply_forecast("Lorraine", "France")["loss"] == 0
        assert "feeds" not in r["message"], r["message"]
