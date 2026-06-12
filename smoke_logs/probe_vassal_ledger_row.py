"""Does the diplomatic ledger nations tab mark a settlement-made vassal?"""
import io
import sys
from unittest.mock import patch

sys.path.insert(0, r"C:\Users\User\PycharmProjects\project-sovereign-map")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from backend.game_logic.settlement_preview import (  # noqa: E402
    handle_settlement_dialogue_action,
    stage_settlement_confirm,
)
from backend.game_logic.diplomatic_ledger import build_diplomatic_ledger  # noqa: E402
from backend.models.world_state import WorldState  # noqa: E402
from tests.helpers.full_europe_settlement_fixtures import (  # noqa: E402
    make_synthetic_war_instance,
)

_SCORER = "backend.game_logic.settlement_scoring.calculate_common_peace_acceptance"


def _accept(*a, **k):
    return {
        "score": 90, "verdict": "accept", "components": {},
        "component_debug": {}, "feedback": [], "hard_stops": [],
        "accept_threshold": 50, "near_acceptable_threshold": 35,
        "side_pressure_score": 30, "raw_total": 90,
        "raw_total_harshness": 0.0, "direct_scores": {},
        "direct_score_sources": {},
    }


world = WorldState()
war = make_synthetic_war_instance(
    "war_1", attackers=["France"], defenders=["Britain", "Prussia"],
    attacker_leader="France", defender_leader="Britain",
    created_turn=1, created_sequence=1,
)
world.war_instances["war_1"] = war
for pair in war["active_diplo_keys"]:
    world.diplomatic_states[pair] = "WAR"
    world.war_scores[pair] = 50 if pair.split("|")[0] == "France" else -50
    world.battle_records[pair] = []
world.current_turn = 3
world.nation_gold.update({"France": 2000, "Britain": 800, "Prussia": 800})
world.invalidate_war_instance_indexes()
with patch(_SCORER, side_effect=_accept):
    staged = stage_settlement_confirm(
        world, war_id="war_1", actor_nation="France",
        settlement_terms=[
            {"type": "peace"},
            {"type": "vassalage", "from": "Prussia", "to": "France"},
        ],
        covered_enemy_participants=["Britain", "Prussia"],
        selected_target_nation="Britain",
        caller_kind="player_editor", dialogue_mode="REVIEW",
    )
    handle_settlement_dialogue_action(
        world, action="confirm_settlement",
        dialogue=staged["diplomatic_dialogue"],
        action_params={"action": "confirm_settlement"},
    )
ledger = build_diplomatic_ledger(world)
nations = (ledger.get("ledger") or ledger).get("nations") or []
for n in nations:
    print(
        n.get("name"), "->", n.get("diplomatic_state"),
        "| descriptor:", n.get("relation_descriptor"),
    )
