"""G4F-9 probe — why does the bilateral estimator score Talleyrand's own
suggested peace terms 3/100 at war score +50 (Dictated Terms)?

Builds the smoke-shaped world offline, generates the suggestion, and dumps
the acceptance component breakdown for: the suggestion, white peace, and a
gold-only ask.
"""
import sys

sys.path.insert(0, r"C:\Users\User\PycharmProjects\project-sovereign-map")

from backend.models.world_state import WorldState  # noqa: E402
from backend.game_logic.diplomacy import calculate_acceptance  # noqa: E402
from backend.game_logic.diplomatic_templates import (  # noqa: E402
    calculate_treaty_harshness,
    generate_suggested_terms,
)
from tests.helpers.full_europe_settlement_fixtures import (  # noqa: E402
    make_synthetic_war_instance,
)


def build_world():
    world = WorldState()
    war = make_synthetic_war_instance(
        "war_1",
        attackers=["France"],
        defenders=["Britain", "Prussia"],
        attacker_leader="France",
        defender_leader="Britain",
        created_turn=1,
        created_sequence=1,
    )
    world.war_instances["war_1"] = war
    for opponent in ("Britain", "Prussia"):
        pair = "|".join(sorted(("France", opponent)))
        world.diplomatic_states[pair] = "WAR"
        first = pair.split("|")[0]
        world.war_scores[pair] = 50 if first == "France" else -50
    world.invalidate_war_instance_indexes()
    return world


def dump(world, label, proposal):
    result = calculate_acceptance(proposal, world)
    if isinstance(result, dict):
        score = result.get("score", result.get("total"))
        print(f"--- {label}: score={score} verdict={result.get('verdict') or result.get('outcome')}")
        comp = result.get("components") or result.get("breakdown") or {}
        for key, value in sorted(
            comp.items(), key=lambda kv: kv[1] if isinstance(kv[1], (int, float)) else 0
        ):
            print(f"      {key}: {value}")
    else:
        print(f"--- {label}: raw result = {result!r}")
    return result


world = build_world()
suggested = generate_suggested_terms("Britain", "peace", world)
print("SUGGESTED TERMS:", {
    k: suggested.get(k) for k in ("type", "demands", "sweeteners")
})
print("harshness (clamped):", calculate_treaty_harshness(suggested))

base = {
    "proposer_nation": "France",
    "target_nation": "Britain",
}
dump(world, "SUGGESTED", {**suggested, **base, "type": suggested.get("type", "peace")})
dump(world, "WHITE PEACE", {**base, "type": "peace", "demands": [], "sweeteners": []})
dump(world, "GOLD 300 LUMP ONLY", {
    **base, "type": "peace",
    "demands": [{"type": "gold_lump", "value": 300}], "sweeteners": [],
})
dump(world, "GOLD 200/TURN ONLY", {
    **base, "type": "peace",
    "demands": [{"type": "gold_per_turn", "value": 200}], "sweeteners": [],
})
