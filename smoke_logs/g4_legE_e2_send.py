"""Leg E — E2 step 2: send the peace proposal as suggested; expect NO false 'Treaty signed'."""
import sys, json
sys.path.insert(0, "smoke_logs")
from g4_legE_lib import get, post, save

st, r = post("/respond_to_diplomatic_dialogue", {"choice": "execute_proposal"})
print("status:", st, "success:", r.get("success"))
save("g4_legE_e2_peace_send.json", r)

print("message:", json.dumps(r.get("message"), ensure_ascii=False)[:3000])
pr = r.get("proposal_result")
print("proposal_result:", json.dumps(pr, indent=1, ensure_ascii=False)[:3000])
dd = r.get("diplomatic_dialogue")
if dd:
    print("dialogue re-attached, type:", dd.get("type"), "keys:", sorted(dd.keys())[:20])
prs = r.get("peace_ratification_summary")
if prs:
    print("peace_ratification_summary:", json.dumps(prs, indent=1, ensure_ascii=False)[:2000])
# check diplomatic state afterwards
st2, ds = get("/debug/diplomatic_status")
dstates = ds.get("diplomatic_states", {})
rel = ds.get("nation_relations", {})
print("post-send state Britain|France:", dstates.get("Britain|France"), "rel:", rel.get("Britain|France"))
save("g4_legE_e2_post_send_diplostatus.json", ds)
