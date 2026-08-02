"""NV-2 — Free Ireland (docs/NAVAL_SPEC.md §5.2; the DEF-5 rider whose
completion definition this file honors VERBATIM: invade → clause → created
client with active `erin_free` deck, GR5, once-only).

Ireland's only map connection is Ulster↔Highlands — INSIDE Britain — which
is why this arc was structurally impossible pre-naval. The §4.3 expedition
is the door; the NA-6c carve machinery is the rest (zero new creation code:
Ireland is one authored `formable_nations` row).
"""

from pathlib import Path

import pytest

from backend.commands.executor import CommandExecutor
from backend.game_logic import naval
from backend.game_logic.formations import (
    build_formables_payload,
    create_client_nation,
)
from backend.game_logic.settlement_validation import (
    evaluate_create_client_eligibility,
)
from backend.models.world_state import WorldState

SCENARIO_PATH = (
    Path(__file__).resolve().parents[1]
    / "godot-client" / "project-sovereign" / "assets" / "maps"
    / "europe_1805.json"
)


@pytest.fixture
def world():
    return WorldState.from_scenario(str(SCENARIO_PATH))


def _britain_war_instance(world, participant="France"):
    for war_id, war in (world.war_instances or {}).items():
        sides = war.get("side_by_nation") or {}
        if "Britain" in sides and participant in sides:
            return war
    raise AssertionError("no Britain war instance at boot")


def _hold_ireland(world, carver="France"):
    world.regions["Ulster"].controller = carver
    world.regions["Munster"].controller = carver
    world.invalidate_active_nations_cache()


# ═══════════════════════════════════════════════════════════════════════════
# THE AUTHORED ROW
# ═══════════════════════════════════════════════════════════════════════════

class TestAuthoredTemplate:
    def test_ireland_is_in_the_catalogue(self, world):
        template = world.formable_nations["Ireland"]
        assert template["provinces"] == ["Ulster", "Munster"]
        assert template["grudge_label"] == "The Irish Question"
        assert template["aggrieved"] == ["Britain"]

    def test_the_deck_is_the_owner_rows_erin_free(self, world):
        deck = world.formable_nations["Ireland"]["deck"]
        assert len(deck) == 1
        entry = deck[0]
        assert entry["id"] == "erin_free"
        assert entry["type"] == "guard_neutrality"
        assert entry["regions"] == ["Ulster", "Munster"]
        # guard_neutrality may not carry a forms block (validator rule) —
        # Ireland is the formation, not a stage toward another.
        assert "forms" not in entry


# ═══════════════════════════════════════════════════════════════════════════
# THE CLAUSE (§5.2-2: holding both Irish provinces at war with Britain
# flips the availability gate — the REAL settlement predicate)
# ═══════════════════════════════════════════════════════════════════════════

class TestAvailabilityGate:
    def test_not_available_at_boot(self, world):
        war = _britain_war_instance(world)
        verdict = evaluate_create_client_eligibility(
            world, war_instance=war, template_id="Ireland",
            from_court="Britain", carver="France")
        assert not verdict.get("eligible")

    def test_holding_both_at_war_flips_the_gate(self, world):
        _hold_ireland(world)
        war = _britain_war_instance(world)
        verdict = evaluate_create_client_eligibility(
            world, war_instance=war, template_id="Ireland",
            from_court="Britain", carver="France")
        assert verdict.get("eligible"), verdict

    def test_one_province_is_not_enough(self, world):
        world.regions["Ulster"].controller = "France"
        world.invalidate_active_nations_cache()
        war = _britain_war_instance(world)
        verdict = evaluate_create_client_eligibility(
            world, war_instance=war, template_id="Ireland",
            from_court="Britain", carver="France")
        assert not verdict.get("eligible")

    def test_gr5_the_predicate_is_nation_neutral(self, world):
        """The DEF-5 rider's GR5 pin: an AI court on the same path reaches
        the same gate (predicate-reachable — the AI-3r honest-zero
        discipline; no ambient AI expeditions in v1)."""
        _hold_ireland(world, carver="Spain")
        war = _britain_war_instance(world, participant="Spain")
        verdict = evaluate_create_client_eligibility(
            world, war_instance=war, template_id="Ireland",
            from_court="Britain", carver="Spain")
        assert verdict.get("eligible"), verdict

    def test_formables_button_lists_ireland_with_honest_terms(self, world):
        rows = {r["tag"]: r for r in build_formables_payload(world)["formables"]}
        row = rows["Ireland"]
        assert row["cls"] == "C"
        assert row["available"] is False  # not held at boot
        term_texts = " · ".join(t["text"] for t in row["gate_terms"])
        assert "Ulster" in term_texts and "Munster" in term_texts

    def test_formables_button_flips_live(self, world):
        _hold_ireland(world)
        rows = {r["tag"]: r for r in build_formables_payload(world)["formables"]}
        assert rows["Ireland"]["available"] is True
        assert rows["Ireland"]["deep_link"] is not None


# ═══════════════════════════════════════════════════════════════════════════
# THE CREATED CLIENT (§5.2-3: carve pricing, loyalty, the deck — inherited)
# ═══════════════════════════════════════════════════════════════════════════

class TestCreatedClient:
    def test_creation_seeds_the_republic(self, world):
        _hold_ireland(world)
        create_client_nation(world, "Ireland", "France", ceded_from="Britain")
        assert "Ireland" in world.get_active_nations()
        assert world.regions["Ulster"].controller == "Ireland"
        assert world.regions["Munster"].controller == "Ireland"
        assert world.vassals["Ireland"]["lord"] == "France"

    def test_the_deck_attaches_dormant_and_wakes_on_independence(self, world):
        """§5.2: latent while vassalized, wakes on independence (the
        dormant-satellite idiom the Holland deck established)."""
        from backend.game_logic.agendas import get_active_agenda
        _hold_ireland(world)
        create_client_nation(world, "Ireland", "France", ceded_from="Britain")
        assert world.agendas["Ireland"][0]["id"] == "erin_free"
        assert get_active_agenda("Ireland", world) is None  # a client dreams
        # Independence: the lord releases the republic.
        world.vassals.pop("Ireland")
        world.diplomatic_states[world._make_diplo_key("France", "Ireland")] = "PEACE"
        world.invalidate_active_nations_cache()
        active = get_active_agenda("Ireland", world)
        assert active is not None and active.id == "erin_free"

    def test_britain_carries_the_irish_question(self, world):
        """Template-level aggrieved: the erection itself offends London."""
        _hold_ireland(world)
        create_client_nation(world, "Ireland", "France", ceded_from="Britain")
        record = world.nation_formations.get("Ireland")
        assert record is not None
        assert record.get("sponsor") == "France"

    def test_once_only(self, world):
        _hold_ireland(world)
        create_client_nation(world, "Ireland", "France", ceded_from="Britain")
        war = _britain_war_instance(world)
        verdict = evaluate_create_client_eligibility(
            world, war_instance=war, template_id="Ireland",
            from_court="Britain", carver="France")
        assert not verdict.get("eligible")
        assert verdict.get("refusal_code") == "carve_tag_already_exists"


# ═══════════════════════════════════════════════════════════════════════════
# THE INVASION (§5.2-1 end-to-end: the expedition is the door)
# ═══════════════════════════════════════════════════════════════════════════

class TestTheInvasion:
    def test_bantry_to_dublin_end_to_end(self, world):
        """Invade (expedition → capture Munster → march → capture Ulster)
        → the clause flips → the client is created with the deck. The RN
        is sunk for determinism — the ODDS arc is pinned in
        test_naval_channel_gate.py; this is the rider's mechanical chain."""
        executor = CommandExecutor()
        game_state = {"world": world}
        world.fleets["Britain"]["ships"] = 0
        soult = world.get_marshal("Soult")
        soult.location = "Brittany"
        soult.strength = 12000
        world._build_marshal_index()

        result = executor._naval._execute_naval_expedition(
            {"marshal": "Soult", "action": "naval_expedition",
             "target": "Munster",
             "raw_command": "land Soult in Munster confirmed"}, game_state)
        assert result["landed"]
        assert soult.location == "Munster"
        # Resolve the capture-choice if the pipeline staged one (secure).
        if world.pending_capture_choice:
            executor.handle_capture_choice("secure", game_state)
        assert world.regions["Munster"].controller == "France"

        # March overland to Ulster (they are land-adjacent inside Ireland).
        soult.moved_this_turn = False
        move = executor._movement._execute_move(soult, "Ulster", world,
                                                game_state)
        assert move["success"], move["message"]
        if world.pending_capture_choice:
            executor.handle_capture_choice("secure", game_state)
        assert world.regions["Ulster"].controller == "France"

        war = _britain_war_instance(world)
        verdict = evaluate_create_client_eligibility(
            world, war_instance=war, template_id="Ireland",
            from_court="Britain", carver="France")
        assert verdict.get("eligible"), verdict

        create_client_nation(world, "Ireland", "France", ceded_from="Britain")
        assert world.regions["Ulster"].controller == "Ireland"
        assert world.agendas["Ireland"][0]["id"] == "erin_free"
