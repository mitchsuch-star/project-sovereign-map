"""NP-3 — The Court (NAPOLEON_SPEC.md §6.2/§6.3/§6.5, gate §14.1 Q4◆).

The Shadow: glory ×0.5 (int-truncated, both polarities) for every
non-sovereign marshal on a side that includes a sovereign — the court's
engine: safe, buffed, disciplined, and DIM at his side. The Petition for
Independent Command: the fifth kind on the single petition channel,
riding the B0 status contract (latch stamps only on QUEUED). The card:
the sovereign apex variant + the stated reward refusal.
"""

import pytest

from backend.game_logic import jealousy
from backend.game_logic.marshal_overview import build_marshal_overview
from backend.models.marshal import Marshal
from backend.models.world_state import WorldState


def make_marshal(name, location="Belgium", strength=30000, nation="France",
                 personality="cautious", **kw):
    skills = kw.pop("skills", None)
    m = Marshal(name=name, location=location, strength=strength,
                personality=personality, nation=nation,
                skills=skills, spawn_location=location)
    for k, v in kw.items():
        setattr(m, k, v)
    return m


def make_sovereign(name="Napoleon", nation="France", location="Paris",
                   strength=10000, **kw):
    return make_marshal(name, location=location, strength=strength,
                        nation=nation, personality="sovereign", **kw)


def make_world(*marshals, wars=(("France", "Austria"),)):
    w = WorldState()
    w.marshals = {m.name: m for m in marshals}
    for a, b in wars:
        key = w._make_diplo_key(a, b)
        w.diplomatic_states[key] = "WAR"
    return w


def glory_sum(marshal):
    return sum(e["points"] for e in marshal.glory_events)


# ════════════════════════════════════════════════════════════════════════
# The Shadow (§6.2, N6)
# ════════════════════════════════════════════════════════════════════════

class TestGloryShadow:
    def _battle(self, world, attacker, defender, atk_parts=None,
                def_parts=None, attacker_won=True, conquered=True,
                atk_cas=1000, def_cas=5000):
        jealousy.record_battle_glory(
            world, attacker, defender,
            attacker_won=attacker_won, defender_won=not attacker_won,
            attacker_casualties=atk_cas, defender_casualties=def_cas,
            conquered=conquered,
            pre_attacker_strength=attacker.strength,
            pre_defender_strength=defender.strength,
            attacker_participants=atk_parts, defender_participants=def_parts)

    def test_victory_glory_halved_under_the_eye(self):
        # Control battle first — same shape, no sovereign.
        a1 = make_marshal("Ney", personality="aggressive")
        e1 = make_marshal("Mack", nation="Austria")
        w1 = make_world(a1, e1)
        self._battle(w1, a1, e1, atk_parts=[a1])
        full = glory_sum(a1)
        assert full > 0

        s = make_sovereign(location="Belgium")
        a2 = make_marshal("Ney", personality="aggressive")
        e2 = make_marshal("Mack", nation="Austria")
        w2 = make_world(s, a2, e2)
        self._battle(w2, a2, e2, atk_parts=[a2, s])
        assert glory_sum(a2) == int(full * jealousy.GLORY_SHADOW_MULT)

    def test_shadow_shields_defeat_glory_symmetrically(self):
        # A primary's defeat points halve toward zero too.
        a1 = make_marshal("Ney", personality="aggressive")
        e1 = make_marshal("Mack", nation="Austria")
        w1 = make_world(a1, e1)
        self._battle(w1, a1, e1, atk_parts=[a1], attacker_won=False,
                     conquered=False, atk_cas=8000, def_cas=1000)
        full_defeat = glory_sum(a1)
        assert full_defeat < 0

        s = make_sovereign(location="Belgium")
        a2 = make_marshal("Ney", personality="aggressive")
        e2 = make_marshal("Mack", nation="Austria")
        w2 = make_world(s, a2, e2)
        self._battle(w2, a2, e2, atk_parts=[a2, s], attacker_won=False,
                     conquered=False, atk_cas=8000, def_cas=1000)
        # int() truncation toward zero: the shadow SHIELDS in defeat.
        assert glory_sum(a2) == int(full_defeat * jealousy.GLORY_SHADOW_MULT)
        assert abs(glory_sum(a2)) <= abs(full_defeat)

    def test_participant_plus_one_truncates_to_zero(self):
        s = make_sovereign(location="Belgium")
        a = make_marshal("Ney", personality="aggressive")
        p = make_marshal("Lannes", personality="aggressive")
        e = make_marshal("Mack", nation="Austria")
        w = make_world(s, a, p, e)
        self._battle(w, a, e, atk_parts=[a, p, s])
        # The supporting corps' +1 halves to 0 — neither shines nor stains.
        assert glory_sum(p) == 0

    def test_stalemate_glory_shadowed(self):
        s = make_sovereign(location="Belgium")
        a = make_marshal("Ney", personality="aggressive")
        e = make_marshal("Mack", nation="Austria")
        w = make_world(s, a, e)
        self._battle(w, a, e, atk_parts=[a, s], attacker_won=False,
                     conquered=True, atk_cas=1000, def_cas=2500)
        # attacker_won=False, defender_won=False, conquered -> STALEMATE_GLORY
        # halves 1 -> 0 under the eye.
        assert glory_sum(a) == int(
            jealousy.STALEMATE_GLORY * jealousy.GLORY_SHADOW_MULT)

    def test_gr5_enemy_side_shadow(self):
        kaiser = make_sovereign("Kaiser", nation="Austria",
                                location="Bavaria")
        a = make_marshal("Ney", personality="aggressive")
        d1 = make_marshal("Mack", nation="Austria", location="Bavaria")
        w1 = make_world(a, d1)
        self._battle(w1, a, d1, def_parts=[d1], attacker_won=False,
                     conquered=False, atk_cas=6000, def_cas=1000)
        full = glory_sum(d1)
        assert full > 0

        a2 = make_marshal("Ney", personality="aggressive")
        d2 = make_marshal("Mack", nation="Austria", location="Bavaria")
        w2 = make_world(a2, d2, kaiser)
        self._battle(w2, a2, d2, def_parts=[d2, kaiser], attacker_won=False,
                     conquered=False, atk_cas=6000, def_cas=1000)
        assert glory_sum(d2) == int(full * jealousy.GLORY_SHADOW_MULT)

    def test_detached_command_shines_fully(self):
        # The sovereign exists but is NOT on this field — no shadow.
        s = make_sovereign(location="Paris")
        a = make_marshal("Ney", personality="aggressive")
        e = make_marshal("Mack", nation="Austria")
        w = make_world(s, a, e)
        self._battle(w, a, e, atk_parts=[a])
        assert glory_sum(a) > 0
        a_ctrl = make_marshal("Ney", personality="aggressive")
        e_ctrl = make_marshal("Mack", nation="Austria")
        w_ctrl = make_world(a_ctrl, e_ctrl)
        self._battle(w_ctrl, a_ctrl, e_ctrl, atk_parts=[a_ctrl])
        assert glory_sum(a) == glory_sum(a_ctrl)


# ════════════════════════════════════════════════════════════════════════
# The shadow counter (zero new serialized fields)
# ════════════════════════════════════════════════════════════════════════

class TestShadowCounter:
    def test_counter_ticks_and_resets(self):
        s = make_sovereign(location="Paris")
        a = make_marshal("Ney", location="Paris", personality="aggressive")
        w = make_world(s, a)
        jealousy.process_turn(w)
        assert jealousy._shadow_turns(a) == 1
        w.current_turn += 1
        jealousy.process_turn(w)
        assert jealousy._shadow_turns(a) == 2
        a.location = "Belgium"
        w.current_turn += 1
        jealousy.process_turn(w)
        assert jealousy._shadow_turns(a) == 0

    def test_zero_writes_without_a_sovereign(self):
        a = make_marshal("Ney", personality="aggressive")
        b = make_marshal("Davout", personality="cautious")
        w = make_world(a, b)
        jealousy.process_turn(w)
        assert "__shadow__" not in a.jealousy_history
        assert "__shadow__" not in b.jealousy_history

    def test_counter_survives_serialization(self):
        a = make_marshal("Ney", personality="aggressive")
        a.jealousy_history["__shadow__"] = {"turns": 3}
        loaded = Marshal.from_dict(a.to_dict())
        assert jealousy._shadow_turns(loaded) == 3


# ════════════════════════════════════════════════════════════════════════
# The Petition for Independent Command (§6.3, N7)
# ════════════════════════════════════════════════════════════════════════

def petition_world(skill=9, shadow_turns=4, dim_glory=0, peer_glory=6):
    s = make_sovereign(location="Paris")
    dim = make_marshal("Ney", location="Paris", personality="aggressive",
                       skills={"tactical": skill, "shock": skill})
    star = make_marshal("Davout", location="Bavaria", personality="cautious")
    w = make_world(s, dim, star)
    dim.jealousy_history["__shadow__"] = {"turns": shadow_turns}
    if dim_glory:
        dim.glory_events.append({"turn": 1, "points": dim_glory})
    star.glory_events.append({"turn": 1, "points": peer_glory})
    return w, dim


class TestShadowPetition:
    def test_fires_and_latches_on_queued(self):
        w, dim = petition_world()
        events = []
        jealousy.check_shadow_petitions(w, events)
        petition = w.pending_marshal_petition
        assert petition is not None
        assert petition["kind"] == "shadow_command"
        assert petition["speaker"] == "Ney"
        assert {o["id"] for o in petition["options"]} == {
            "detach", "stays", "promise"}
        assert "shadow@Ney" in w.jealousy_confrontations_seen
        assert any(e["type"] == "shadow_petition" for e in events)

    def test_blocked_slot_does_not_burn_the_latch(self):
        w, dim = petition_world()
        w.pending_marshal_petition = {"kind": "war_weary"}  # occupied
        jealousy.check_shadow_petitions(w, [])
        assert "shadow@Ney" not in w.jealousy_confrontations_seen
        # ...and it retries clean once the slot frees.
        w.pending_marshal_petition = None
        jealousy.check_shadow_petitions(w, [])
        assert "shadow@Ney" in w.jealousy_confrontations_seen

    def test_once_per_marshal_per_campaign(self):
        w, dim = petition_world()
        jealousy.check_shadow_petitions(w, [])
        w.pending_marshal_petition = None
        jealousy.check_shadow_petitions(w, [])
        assert w.pending_marshal_petition is None

    @pytest.mark.parametrize("kwargs", [
        {"skill": 5},                 # skills not worth using
        {"shadow_turns": 3},          # not long enough at HQ
        {"dim_glory": 6, "peer_glory": 6},  # not below the median
    ])
    def test_gates_hold(self, kwargs):
        w, _ = petition_world(**kwargs)
        jealousy.check_shadow_petitions(w, [])
        assert w.pending_marshal_petition is None

    def test_dormant_world_never_fires(self):
        w, _ = petition_world()
        w.scenario_name = "tutorial"
        jealousy.check_shadow_petitions(w, [])
        assert w.pending_marshal_petition is None
        assert "shadow@Ney" not in w.jealousy_confrontations_seen

    def test_detach_arm_counsels_a_posting(self):
        w, dim = petition_world()
        jealousy.check_shadow_petitions(w, [])
        result = jealousy.handle_petition_response(w, "detach")
        assert result["success"] is True
        assert "the order is yours to give" in result["message"]
        assert w.pending_marshal_petition is None

    def test_stays_arm(self):
        w, dim = petition_world()
        jealousy.check_shadow_petitions(w, [])
        result = jealousy.handle_petition_response(w, "stays")
        assert result["success"] is True
        assert "shadow" in result["message"].lower()

    def test_promise_arm_charges_and_banks_trust(self):
        w, dim = petition_world()
        jealousy.check_shadow_petitions(w, [])
        start_ap = w.actions_remaining
        start_trust = dim.trust.value
        result = jealousy.handle_petition_response(w, "promise")
        assert result["success"] is True
        assert w.actions_remaining == start_ap - jealousy.SHADOW_PROMISE_AP
        assert dim.trust.value == start_trust + jealousy.SHADOW_PROMISE_TRUST
        assert jealousy._shadow_turns(dim) == 0

    def test_promise_without_ap_reattaches_the_card(self):
        w, dim = petition_world()
        jealousy.check_shadow_petitions(w, [])
        w.actions_remaining = 0
        result = jealousy.handle_petition_response(w, "promise")
        assert result["success"] is False
        assert result.get("marshal_petition") is not None
        assert w.pending_marshal_petition is not None

    def test_frontier_posting_is_a_real_frontier(self):
        w, dim = petition_world()
        posting = jealousy._frontier_posting(w, dim)
        if posting:  # the bare flag world may hold no France-Austria border
            region = w.regions[posting]
            assert region.controller == "France"


# ════════════════════════════════════════════════════════════════════════
# The card (§6.5)
# ════════════════════════════════════════════════════════════════════════

class TestSovereignCard:
    def test_sovereign_card_carries_the_apex_flag(self):
        s = make_sovereign()
        a = make_marshal("Ney", personality="aggressive")
        w = make_world(s, a)
        cards = {c["name"]: c for c in build_marshal_overview(w)}
        assert cards["Napoleon"]["sovereign"] is True
        assert cards["Napoleon"]["sovereign_note"] == "The Empire is his estate."
        assert "sovereign" not in cards["Ney"]

    def test_sovereign_card_has_no_glory_and_no_reward_claim(self):
        s = make_sovereign()
        w = make_world(s)
        w.sovereign_map = "europe"
        s.battles_won = 12  # would be expectation 480 for anyone else
        card = build_marshal_overview(w)[0]
        assert card["glory"] == 0
        assert card["expectation"] == 0
        assert card["expectation_shortfall"] == 0
