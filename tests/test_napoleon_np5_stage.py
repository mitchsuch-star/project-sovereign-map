"""NP-5 — The Stage & the Seat (NAPOLEON_SPEC.md §8/§9, gate §14.1 Q5◆/Q7◆).

The Seat: +1 DP while the sovereign holds court in his own capital (N11),
derived per-turn with zero state, shown in the DP breakdown + the
diplomatic ledger's Tuileries line; the once-per-war "Emperor has taken
the field" dispatch note latched on the war-instance record. The stage:
the emperor map-piece arm (is_sovereign-FIRST derivation, never
cavalry=True), the diorama contingent's sovereign key + locket cipher, the
verdict acknowledgment, and the gazette's literal-genius variant. All
content-dormant without an authored sovereign.
"""

import random as _random

import pytest

from backend.commands.executor import CommandExecutor
from backend.game_logic import gazette
from backend.game_logic.battle_diorama import _contingent, marshal_arm
from backend.game_logic.combat import CombatResolver
from backend.game_logic.diplomacy import (
    _process_dp_regen,
    sovereign_seat_bonus,
)
from backend.models.marshal import Marshal
from backend.models.world_state import WorldState
from backend.modding.validator import validate_scenario


def make_marshal(name, location="Belgium", strength=30000, nation="France",
                 personality="cautious", cavalry=False, **kw):
    m = Marshal(name=name, location=location, strength=strength,
                personality=personality, nation=nation,
                movement_range=2 if cavalry else 1, cavalry=cavalry,
                spawn_location=location)
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


FIXED_DICE = {
    "natural": 7, "modified": 9, "is_critical_success": False,
    "is_critical_failure": False, "multiplier": 1.0,
    "skill_bonus": 2, "flanking_bonus": 0,
}


@pytest.fixture()
def fixed_rng(monkeypatch):
    monkeypatch.setattr(CombatResolver, "roll_combat_dice",
                        lambda self, marshal, flanking_bonus=0: dict(FIXED_DICE))
    monkeypatch.setattr(_random, "uniform", lambda a, b: (a + b) / 2.0)
    monkeypatch.setattr(_random, "random", lambda: 0.5)


# ════════════════════════════════════════════════════════════════════════
# The Seat (§8, N11)
# ════════════════════════════════════════════════════════════════════════

class TestTheSeat:
    def test_seat_bonus_derivations(self):
        s = make_sovereign(location="Paris")
        w = make_world(s)
        assert sovereign_seat_bonus(w, "France") == 1
        s.location = "Belgium"
        assert sovereign_seat_bonus(w, "France") == 0
        s.location = "Paris"
        s.captured_by = "Austria"
        assert sovereign_seat_bonus(w, "France") == 0

    def test_no_sovereign_no_seat(self):
        w = make_world(make_marshal("Ney", personality="aggressive"))
        assert sovereign_seat_bonus(w, "France") == 0

    def test_gr5_enemy_sovereign_seats_his_own_court(self):
        kaiser = make_sovereign("Kaiser", nation="Austria",
                                location="Vienna")
        w = make_world(kaiser)
        if w.get_nation_capital("Austria") != "Vienna":
            pytest.skip("fixture capital differs")
        assert sovereign_seat_bonus(w, "Austria") == 1
        _process_dp_regen(w)
        assert w.nation_dp["Austria"] >= 2  # base + seat above any clamp arm

    def test_dp_tick_carries_the_seat(self):
        s = make_sovereign(location="Paris")
        w = make_world(s)
        _process_dp_regen(w)
        with_seat = w.diplomatic_points
        s.location = "Belgium"
        w.pending_dispatch_events = []
        _process_dp_regen(w)
        without = w.diplomatic_points
        assert with_seat == without + 1

    def test_breakdown_names_the_seat(self):
        s = make_sovereign(location="Paris")
        w = make_world(s)
        w.pending_dispatch_events = []
        _process_dp_regen(w)
        rows = [e for e in w.pending_dispatch_events
                if e.get("type") == "diplomatic_dp_regen"]
        assert rows, w.pending_dispatch_events
        assert "the Emperor holds court" in \
            rows[-1]["template_vars"]["breakdown"]

    def test_ledger_breakdown_carries_seat_bonus(self):
        from backend.game_logic.diplomatic_ledger import (
            build_diplomatic_ledger,
        )
        s = make_sovereign(location="Paris")
        w = make_world(s)
        ledger = build_diplomatic_ledger(w)
        breakdown = ledger["talleyrand"]["dp_breakdown"]
        assert breakdown["seat_bonus"] == 1


class TestTakesTheFieldNote:
    def _world_at_war(self, sovereign_location):
        s = make_sovereign(location=sovereign_location)
        w = make_world(s)
        w.war_instances = {"w1": {
            "active_participants": ["France", "Austria"],
            "ended_turn": None,
        }}
        w.pending_dispatch_events = []
        return w

    def test_first_departure_notes_once_per_war(self):
        w = self._world_at_war("Belgium")
        _process_dp_regen(w)
        notes = [e for e in w.pending_dispatch_events
                 if e.get("type") == "sovereign_takes_field"]
        assert len(notes) == 1
        assert w.war_instances["w1"]["emperor_field_noted"] is True
        # Second tick: latched — no repeat.
        _process_dp_regen(w)
        notes = [e for e in w.pending_dispatch_events
                 if e.get("type") == "sovereign_takes_field"]
        assert len(notes) == 1

    def test_no_note_while_he_holds_the_seat(self):
        w = self._world_at_war("Paris")
        _process_dp_regen(w)
        assert not [e for e in w.pending_dispatch_events
                    if e.get("type") == "sovereign_takes_field"]

    def test_no_note_without_a_war(self):
        s = make_sovereign(location="Belgium")
        w = make_world(s)
        w.war_instances = {}
        w.pending_dispatch_events = []
        _process_dp_regen(w)
        assert not [e for e in w.pending_dispatch_events
                    if e.get("type") == "sovereign_takes_field"]


# ════════════════════════════════════════════════════════════════════════
# The emperor piece (§9, Q7◆)
# ════════════════════════════════════════════════════════════════════════

class TestEmperorPiece:
    def test_arm_derivation_sovereign_first(self):
        assert marshal_arm(make_sovereign()) == "emperor"
        assert marshal_arm(make_sovereign(cavalry=True)) == "emperor"
        assert marshal_arm(make_marshal("Ney", cavalry=True,
                                        personality="aggressive")) == "cavalry"
        assert marshal_arm(make_marshal("Ney",
                                        personality="cautious")) == "infantry"

    def test_map_summary_rides_the_base_dict(self):
        s = make_sovereign(location="Paris")
        w = make_world(s)
        summary = w.get_game_state_summary()
        rows = summary["map_data"]["Paris"]["marshals"]
        entry = next(r for r in rows if r["name"] == "Napoleon")
        assert entry["arm"] == "emperor"

    def test_sprites_on_disk(self):
        from pathlib import Path
        pieces = Path("godot-client/project-sovereign/assets/ui/pieces")
        for layer in ("base", "shadow", "coat", "body"):
            for facing in ("r", "l"):
                assert (pieces / f"emperor_{layer}_{facing}.png").exists()

    def test_contingent_carries_sovereign_and_arm(self):
        s = make_sovereign()
        w = make_world(s)
        entry = _contingent(s, 10000, 500, 9500, "engaged", True, w)
        assert entry["sovereign"] is True
        assert entry["arm"] == "emperor"
        control = _contingent(make_marshal("Ney", personality="aggressive"),
                              10000, 0, 10000, "engaged", True, w)
        assert control["sovereign"] is False

    def test_diorama_verdict_acknowledges_the_register(self, fixed_rng):
        s = make_sovereign(location="Belgium", strength=40000)
        e = make_marshal("Mack", nation="Austria", location="Waterloo",
                         strength=15000)
        w = make_world(s, e)
        executor = CommandExecutor()
        result = executor.execute(
            {"command": {"marshal": "Napoleon", "action": "attack",
                         "target": "Mack", "_muster_confirmed": True}},
            {"world": w})
        payload = result.get("battle_diorama")
        assert payload, result.get("message")
        assert payload["observation"].startswith(
            "The Emperor watched this field.")

    def test_control_verdict_unprefixed(self, fixed_rng):
        a = make_marshal("Ney", personality="aggressive", strength=40000)
        e = make_marshal("Mack", nation="Austria", location="Waterloo",
                         strength=15000)
        w = make_world(a, e)
        executor = CommandExecutor()
        result = executor.execute(
            {"command": {"marshal": "Ney", "action": "attack",
                         "target": "Mack", "_muster_confirmed": True}},
            {"world": w})
        payload = result.get("battle_diorama")
        assert payload
        assert not payload["observation"].startswith(
            "The Emperor watched this field.")


# ════════════════════════════════════════════════════════════════════════
# The gazette's literal genius (§9)
# ════════════════════════════════════════════════════════════════════════

class TestGazetteVariant:
    def _battle_row(self, attacker="Napoleon"):
        return {"type": "battle", "outcome": "attacker_victory",
                "attacker": attacker, "attacker_nation": "France",
                "defender": "Mack", "defender_nation": "Austria",
                "location": "Ulm"}

    def test_emperor_led_victory_reads_as_fact(self):
        s = make_sovereign()
        w = make_world(s)
        lead = gazette._press_lead(w, [self._battle_row("Napoleon")])
        assert "The Emperor himself carries the day" in lead

    def test_marshal_victory_keeps_the_convention(self):
        a = make_marshal("Ney", personality="aggressive")
        w = make_world(a)
        lead = gazette._press_lead(w, [self._battle_row("Ney")])
        assert "the Emperor's genius shines upon the army" in lead


# ════════════════════════════════════════════════════════════════════════
# The modding reference (§10)
# ════════════════════════════════════════════════════════════════════════

class TestWaterlooReference:
    def test_waterloo_mod_authors_a_sovereign_and_validates(self):
        import json
        from pathlib import Path
        path = Path("mods/examples/battle_of_waterloo.json")
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["marshals"]["Napoleon"]["personality"] == "sovereign"
        result = validate_scenario(data, check_adjacency=False)
        assert not any("personality" in e.path for e in result.errors)
