"""Drill into the three GAP lines from the term-reflection audit."""
import io
import json
import sys
from unittest.mock import patch

sys.path.insert(0, r"C:\Users\User\PycharmProjects\project-sovereign-map")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from backend.game_logic.settlement_preview import (  # noqa: E402
    handle_settlement_dialogue_action,
    stage_settlement_confirm,
)
from backend.game_logic.dispatch import build_morning_dispatch  # noqa: E402
from backend.game_logic.diplomatic_ledger import build_diplomatic_ledger  # noqa: E402
from backend.models.world_state import WorldState  # noqa: E402
from tests.helpers.full_europe_settlement_fixtures import (  # noqa: E402
    make_synthetic_war_instance,
)

_SCORER = "backend.game_logic.settlement_scoring.calculate_common_peace_acceptance"


def _accept(*args, **kwargs):
    return {
        "score": 90, "verdict": "accept", "components": {},
        "component_debug": {}, "feedback": [], "hard_stops": [],
        "accept_threshold": 50, "near_acceptable_threshold": 35,
        "side_pressure_score": 30, "raw_total": 90,
        "raw_total_harshness": 0.0, "direct_scores": {},
        "direct_score_sources": {},
    }


def build_world():
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
    world.nation_gold["France"] = 2000
    world.nation_gold["Britain"] = 800
    world.nation_gold["Prussia"] = 800
    world.invalidate_war_instance_indexes()
    return world


def ratify(world, terms):
    with patch(_SCORER, side_effect=_accept):
        staged = stage_settlement_confirm(
            world, war_id="war_1", actor_nation="France",
            settlement_terms=terms,
            covered_enemy_participants=["Britain", "Prussia"],
            selected_target_nation="Britain",
            caller_kind="player_editor", dialogue_mode="REVIEW",
        )
        return handle_settlement_dialogue_action(
            world, action="confirm_settlement",
            dialogue=staged["diplomatic_dialogue"],
            action_params={"action": "confirm_settlement"},
        )


print("== A: where does war_1 appear in the dispatch dict? ==")
world = build_world()
ratify(world, [
    {"type": "peace"},
    {"type": "gold_indemnity", "from": "Britain", "to": "France", "amount": 200},
    {"type": "territory_cede", "from": "Britain", "to": "France",
     "region": "Waterloo"},
])
dispatch = build_morning_dispatch(world)


def walk(node, path=""):
    if isinstance(node, dict):
        for k, v in node.items():
            walk(v, f"{path}.{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            walk(v, f"{path}[{i}]")
    elif isinstance(node, str) and "war_1" in node:
        print(f"  {path}: {node[:120]}")


walk(dispatch)

print()
print("== A: settlement lines as the player reads them ==")
for ev in dispatch.get("diplomatic_events", []) or []:
    print("  text:", str(ev.get("text"))[:160])

print()
print("== A: recent_settlements record shape ==")
dl = build_diplomatic_ledger(world)
ledger = dl.get("ledger") or dl
recent = ledger.get("recent_settlements") or []
if recent:
    rec = recent[0]
    print("  keys:", sorted(rec.keys()))
    print("  terms_summary:", rec.get("terms_summary"))
    rows = ((rec.get("review_sections") or {}).get("sections") or {}).get(
        "terms", {}).get("rows", [])
    for row in rows:
        print("  row display_label:", row.get("display_label"))

print()
print("== B: nations-tab row shape for the vassal ==")
world2 = build_world()
ratify(world2, [
    {"type": "peace"},
    {"type": "vassalage", "from": "Prussia", "to": "France"},
])
dl2 = build_diplomatic_ledger(world2)
ledger2 = dl2.get("ledger") or dl2
nations = ledger2.get("nations") or []
print("  nation row keys:", sorted(nations[0].keys()) if nations else "none")
names = [
    (n.get("nation") or n.get("name"), n.get("status") or n.get("political_status"))
    for n in nations
]
print("  rows:", names)
prussia_anywhere = "Prussia" in json.dumps(ledger2)
print("  Prussia anywhere in dledger:", prussia_anywhere)
if prussia_anywhere:
    for tab_name, tab in ledger2.items():
        if "Prussia" in json.dumps(tab, default=str):
            print(f"    appears in tab: {tab_name}")
