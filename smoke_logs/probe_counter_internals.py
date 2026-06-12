"""Offline F1 probe — call generate_counter_offer directly on the same
proposal shapes the wire probe sent, and trace WHY it returns None.
"""
import os
import sys

sys.path.insert(0, r"C:\Users\User\PycharmProjects\project-sovereign-map")
os.environ.setdefault("LLM_MODE", "mock")

from backend.models.world_state import WorldState  # noqa: E402
from backend.game_logic.diplomacy import calculate_acceptance, set_diplomatic_state  # noqa: E402
from backend.game_logic import ai_diplomacy  # noqa: E402


def build_world():
    world = WorldState()
    set_diplomatic_state(world, "France", "Britain", "WAR", "probe")
    key = world._make_diplo_key("France", "Britain")
    world.nation_relations[key] = -40
    # France winning ~+50 (mirror the smoke fixture's battle records)
    world.war_scores[key] = 50 if key.split("|")[0] == "France" else -50
    return world


def trace(proposal, world):
    print(f"\n=== {proposal['type']} | demands={proposal['demands']} sweeteners={proposal['sweeteners']}")
    base = calculate_acceptance(proposal, world)
    print("baseline:", base["score"], base.get("outcome"))
    import copy
    for cat in ("sweeteners", "demands", "clauses"):
        for i, item in enumerate(proposal.get(cat, [])):
            test = copy.deepcopy(proposal)
            test[cat].pop(i)
            r = calculate_acceptance(test, world)
            print(f"  remove {cat}[{i}] {item}: score {r['score']} (impact {r['score'] - base['score']})")
    talleyrand = world.diplomats.get("France")
    print("France diplomat personality:", getattr(talleyrand, "personality", None))
    target_diplomat = world.diplomats.get("Britain")
    print("Britain diplomat personality:", getattr(target_diplomat, "personality", None))
    result = ai_diplomacy.generate_counter_offer(proposal, world)
    print("generate_counter_offer ->", "None (no counter)" if result is None else result)


world = build_world()

peace = {
    "type": "peace",
    "proposer_nation": "France",
    "target_nation": "Britain",
    "sweeteners": [],
    "demands": [{"type": "gold_per_turn", "value": 200}],
    "clauses": [],
}
trace(peace, world)

armistice_generic = {
    "type": "armistice",
    "proposer_nation": "France",
    "target_nation": "Britain",
    "sweeteners": [{"type": "gold_lump", "value": 200}],
    "demands": [],
    "clauses": [],
}
trace(armistice_generic, world)

# F3 drift check: same package, three type strings
for t in ("armistice", "armistice_winning", "armistice_losing"):
    p = dict(armistice_generic, type=t)
    r = calculate_acceptance(p, world)
    print(f"type={t!r}: score={r['score']} outcome={r.get('outcome')}")
