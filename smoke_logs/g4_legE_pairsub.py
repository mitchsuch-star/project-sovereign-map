"""Leg E — pair-substitute probe: settlement table -> seek_armistice_instead -> confirm.
This is the designed armistice escape for the shared war (typed bilateral is paradox-blocked)."""
import sys, json
sys.path.insert(0, "smoke_logs")
from g4_legE_lib import get, post, save

# Mount the settlement table for war_1 targeting Britain
st, r = post("/command", {"command": "propose common peace with Britain",
                          "action": "propose_common_peace",
                          "target_nation": "Britain",
                          "war_id": "war_1"})
print("settlement mount:", st, r.get("success"))
save("g4_legE_pairsub_mount.json", r)
dd = r.get("diplomatic_dialogue")
if not dd:
    print("NO dialogue:", json.dumps(r.get("message"), ensure_ascii=False)[:600])
    sys.exit(1)
print("type:", dd.get("type"), "| mode:", dd.get("dialogue_mode"))
print("available_action_ids:", dd.get("available_action_ids"))
opts = [o.get("action") for o in (dd.get("options") or [])]
print("options:", opts)
rows = dd.get("per_court_acceptance") or []
print("per_court rows:", [(row.get("nation"), row.get("score"), row.get("band")) for row in rows])

# Try seek_armistice_instead
st, r2 = post("/respond_to_diplomatic_dialogue",
              {"choice": "seek_armistice_instead",
               "action_params": {"action": "seek_armistice_instead", "nation": "Britain"}})
print("\nseek_armistice_instead:", st, r2.get("success"))
save("g4_legE_pairsub_seek_armistice.json", r2)
print("message:", json.dumps(r2.get("message"), ensure_ascii=False)[:500])
print("error_display:", r2.get("error_display"))
dd2 = r2.get("diplomatic_dialogue")
if dd2:
    print("new dialogue type:", dd2.get("type"), "| dtype:", dd2.get("dialogue_type"))
    print("options:", [o.get("action") for o in (dd2.get("options") or [])])
    for k in ("armistice_mechanics", "acceptance_estimate", "pair_nation", "target_nation"):
        v = dd2.get(k)
        if v is not None:
            print(k, ":", json.dumps(v, ensure_ascii=False)[:600])
    wcs = dd2.get("war_context_snapshot") or {}
    if wcs.get("armistice_mechanics"):
        print("armistice_mechanics:", json.dumps(wcs["armistice_mechanics"], ensure_ascii=False)[:700])
