"""Leg E — pair-substitute step 3: confirm -> armistice proposal dialogue -> send."""
import sys, json
sys.path.insert(0, "smoke_logs")
from g4_legE_lib import get, post, save

st, r = post("/respond_to_diplomatic_dialogue",
             {"choice": "confirm_pair_substitute",
              "action_params": {"action": "confirm_pair_substitute"}})
print("confirm_pair_substitute:", st, r.get("success"))
save("g4_legE_pairsub_confirm.json", r)
print("message:", json.dumps(r.get("message"), ensure_ascii=False)[:400])
dd = r.get("diplomatic_dialogue")
if not dd:
    print("no dialogue; error_display:", r.get("error_display"))
    sys.exit(1)
print("dialogue type:", dd.get("type"), "| proposal_type_display:", dd.get("proposal_type_display"))
print("acceptance_estimate:", dd.get("acceptance_estimate"), "| outcome:", dd.get("acceptance_outcome"))
print("options:", [o.get("action") for o in (dd.get("options") or [])])
wcs = dd.get("war_context_snapshot") or {}
if wcs.get("armistice_mechanics"):
    print("armistice_mechanics:", json.dumps(wcs["armistice_mechanics"], ensure_ascii=False)[:700])

# send it
st, r2 = post("/respond_to_diplomatic_dialogue", {"choice": "execute_proposal"})
print("\nexecute_proposal:", st, r2.get("success"))
save("g4_legE_pairsub_send.json", r2)
print("message:", json.dumps(r2.get("message"), ensure_ascii=False)[:600])
print("proposal_result:", json.dumps(r2.get("proposal_result"), indent=1, ensure_ascii=False)[:1500])
dd2 = r2.get("diplomatic_dialogue")
print("dialogue re-attached:", bool(dd2), "| type:", dd2.get("type") if dd2 else None)

st, ds = get("/debug/diplomatic_status")
print("\nstate Britain|France:", ds.get("diplomatic_states", {}).get("Britain|France"),
      "| DP:", ds.get("diplomatic_points"))
save("g4_legE_pairsub_post_diplostatus.json", ds)
