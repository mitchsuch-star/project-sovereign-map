"""Term-by-term reflection audit (G4F-10 follow-on).

For each live settlement clause type: ratify through the REAL pipeline
(stage -> per-court gate -> ratify) with the scorer patched to accept,
then inspect every reflection surface:

  world effects | dispatch queue/text | campaign log | strategic ledger
  | diplomatic ledger | war status

Prints PASS/GAP per check. gold_per_turn already audited (G4F-10).
"""
import io
import sys
from unittest.mock import patch

sys.path.insert(0, r"C:\Users\User\PycharmProjects\project-sovereign-map")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from backend.game_logic.settlement_preview import (  # noqa: E402
    handle_settlement_dialogue_action,
    stage_settlement_confirm,
)
from backend.game_logic.dispatch import build_morning_dispatch  # noqa: E402
from backend.campaign_log import (  # noqa: E402
    filter_campaign_log,
    format_event_oneliner,
)
from backend.game_logic.ledger import build_strategic_ledger  # noqa: E402
from backend.game_logic.diplomatic_ledger import build_diplomatic_ledger  # noqa: E402
from backend.game_logic.war_status import build_active_wars  # noqa: E402
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
        "war_1",
        attackers=["France"],
        defenders=["Britain", "Prussia"],
        attacker_leader="France",
        defender_leader="Britain",
        created_turn=1,
        created_sequence=1,
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


def ratify(world, terms, covered=("Britain", "Prussia")):
    with patch(_SCORER, side_effect=_accept):
        staged = stage_settlement_confirm(
            world,
            war_id="war_1",
            actor_nation="France",
            settlement_terms=terms,
            covered_enemy_participants=list(covered),
            selected_target_nation=covered[0],
            caller_kind="player_editor",
            dialogue_mode="REVIEW",
        )
        if not staged.get("success"):
            return None, staged
        result = handle_settlement_dialogue_action(
            world,
            action="confirm_settlement",
            dialogue=staged["diplomatic_dialogue"],
            action_params={"action": "confirm_settlement"},
        )
    return result, staged


def check(label, cond, detail=""):
    mark = "PASS" if cond else "GAP "
    print(f"  [{mark}] {label}" + (f"  -> {detail}" if detail and not cond else ""))


def surfaces(world, *, expect_strings, player="France"):
    """Common surface sweep after a ratification."""
    # dispatch (built from pending events)
    dispatch = build_morning_dispatch(world)
    dispatch_text = str(dispatch)
    # campaign log
    log_lines = [
        format_event_oneliner(e)
        for e in filter_campaign_log(list(world.event_log), world)
    ]
    log_text = " | ".join(log_lines)
    # ledgers
    sledger = build_strategic_ledger(world)
    dledger = build_diplomatic_ledger(world)
    wars = build_active_wars(world)
    return {
        "dispatch_text": dispatch_text,
        "log_text": log_text,
        "sledger": sledger,
        "dledger": dledger,
        "wars": wars,
    }


print("=" * 70)
print("CLUSTER A: peace + gold_indemnity(Britain->France 200) +")
print("           territory_cede(Britain->France Waterloo)")
print("=" * 70)
world = build_world()
gold_before = world.nation_gold["France"]
result, staged = ratify(world, [
    {"type": "peace"},
    {"type": "gold_indemnity", "from": "Britain", "to": "France", "amount": 200},
    {"type": "territory_cede", "from": "Britain", "to": "France",
     "region": "Waterloo"},
])
check("ratify succeeded", bool(result and result.get("success")),
      str((result or staged).get("error_display") or (result or staged).get("error")))
if result and result.get("success"):
    check("gold transferred instantly (+200)",
          world.nation_gold["France"] == gold_before + 200,
          f"France gold {world.nation_gold['France']}")
    check("Waterloo controller flipped to France",
          world.regions["Waterloo"].controller == "France",
          world.regions["Waterloo"].controller)
    s = surfaces(world, expect_strings=[])
    dt, lt = s["dispatch_text"], s["log_text"]
    check("dispatch mentions the settlement", "settlement" in dt.lower() or "Settlement" in dt, dt[:200])
    check("dispatch names the gold term", "200" in dt, dt[:300])
    check("dispatch names Waterloo", "Waterloo" in dt, dt[:300])
    check("no raw war_1 in dispatch", "war_1" not in dt, dt[:300])
    check("campaign log carries ratification", "settlement" in lt.lower(), lt[:200])
    check("no raw war_1 in campaign log", "war_1" not in lt, lt[:200])
    check("strategic ledger lists Waterloo income",
          any(r.get("region") == "Waterloo"
              for r in s["sledger"]["economy"]["income_breakdown"]))
    terr = s["sledger"].get("territories") or {}
    check("strategic ledger territories includes Waterloo",
          "Waterloo" in str(terr))
    recent = (s["dledger"].get("ledger") or s["dledger"]).get("recent_settlements") or []
    check("diplomatic ledger has the settlement record", bool(recent))
    if recent:
        summary = " ".join(str(x) for x in recent[0].get("terms_summary") or [])
        check("record names gold + territory",
              "200" in summary and "Waterloo" in summary, summary)
    check("war left the active list",
          not any(w.get("war_instance_id") == "war_1" for w in s["wars"].get("wars", [])))

print()
print("=" * 70)
print("CLUSTER B: vassalage (Prussia -> France)")
print("=" * 70)
world = build_world()
result, staged = ratify(world, [
    {"type": "peace"},
    {"type": "vassalage", "from": "Prussia", "to": "France"},
])
check("ratify succeeded", bool(result and result.get("success")),
      str((result or staged).get("error_display") or (result or staged).get("error")))
if result and result.get("success"):
    vassal = (world.vassals or {}).get("Prussia") or {}
    check("Prussia is France's vassal",
          str(vassal.get("lord") or vassal.get("lord_nation")) == "France",
          str(vassal))
    s = surfaces(world, expect_strings=[])
    dt, lt = s["dispatch_text"], s["log_text"]
    check("dispatch names the vassalage", "vassal" in dt.lower(), dt[:300])
    check("ledger economy shows vassal tribute",
          int(s["sledger"]["economy"].get("vassal_tribute", 0)) > 0,
          str(s["sledger"]["economy"].get("vassal_tribute")))
    nations = (s["dledger"].get("ledger") or s["dledger"]).get("nations") or []
    prussia_row = next((n for n in nations if n.get("nation") == "Prussia"), {})
    check("diplomatic ledger marks Prussia a vassal",
          "vassal" in str(prussia_row).lower(), str(prussia_row)[:200])

print()
print("=" * 70)
print("CLUSTER C: subjugation (Prussia -> France)")
print("=" * 70)
world = build_world()
result, staged = ratify(world, [
    {"type": "peace"},
    {"type": "subjugation", "from": "Prussia", "to": "France"},
])
check("ratify succeeded", bool(result and result.get("success")),
      str((result or staged).get("error_display") or (result or staged).get("error")))
if result and result.get("success"):
    vassal = (world.vassals or {}).get("Prussia") or {}
    check("Prussia subjugated under France",
          str(vassal.get("lord") or vassal.get("lord_nation")) == "France",
          str(vassal))
    s = surfaces(world, expect_strings=[])
    check("dispatch names the subjugation/vassalage",
          ("subjugat" in s["dispatch_text"].lower()
           or "vassal" in s["dispatch_text"].lower()),
          s["dispatch_text"][:300])

print()
print("=" * 70)
print("CLUSTER D: forced_alliance (Britain -> France, +Continental System)")
print("=" * 70)
world = build_world()
result, staged = ratify(world, [
    {"type": "peace"},
    {"type": "forced_alliance", "from": "Britain", "to": "France",
     "includes_continental_system": True},
])
check("ratify succeeded", bool(result and result.get("success")),
      str((result or staged).get("error_display") or (result or staged).get("error")))
if result and result.get("success"):
    pair = "|".join(sorted(("France", "Britain")))
    state = world.diplomatic_states.get(pair)
    check("pair state is an alliance", "ALLIANCE" in str(state).upper(), str(state))
    s = surfaces(world, expect_strings=[])
    check("dispatch names the alliance", "allian" in s["dispatch_text"].lower(),
          s["dispatch_text"][:300])
    treaties = (s["dledger"].get("ledger") or s["dledger"]).get("treaties") or []
    check("diplomatic ledger treaties reflect it",
          "allian" in str(treaties).lower(), str(treaties)[:200])

print()
print("=" * 70)
print("CLUSTER E: liberation (Saxony freed from Britain)")
print("=" * 70)
world = build_world()
world.vassals["Saxony"] = {"lord": "Britain", "loyalty": 50, "autonomy": "medium"}
result, staged = ratify(world, [
    {"type": "peace"},
    {"type": "liberation", "vassal_nation": "Saxony", "lord_nation": "Britain",
     "liberator": "France"},
])
check("ratify succeeded", bool(result and result.get("success")),
      str((result or staged).get("error_display") or (result or staged).get("error")))
if result and result.get("success"):
    check("Saxony released from vassalage", "Saxony" not in (world.vassals or {}),
          str((world.vassals or {}).get("Saxony")))
    s = surfaces(world, expect_strings=[])
    check("dispatch names the liberation",
          "liberat" in s["dispatch_text"].lower() or "Saxony" in s["dispatch_text"],
          s["dispatch_text"][:300])
