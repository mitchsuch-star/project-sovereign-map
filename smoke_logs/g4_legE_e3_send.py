"""Leg E — E3 step 2: print full armistice_mechanics, then send the armistice."""
import sys, json
sys.path.insert(0, "smoke_logs")
from g4_legE_lib import get, post, save

r = json.load(open("smoke_logs/g4_legE_e3_armistice_mount.json", encoding="utf-8"))
am = r["diplomatic_dialogue"]["war_context_snapshot"]["armistice_mechanics"]
print("armistice_mechanics:")
print(json.dumps(am, indent=1, ensure_ascii=False))

st, r2 = post("/respond_to_diplomatic_dialogue", {"choice": "execute_proposal"})
print("\nsend status:", st, "success:", r2.get("success"))
save("g4_legE_e3_armistice_send.json", r2)
print("message:", json.dumps(r2.get("message"), ensure_ascii=False)[:2500])
pr = r2.get("proposal_result")
print("proposal_result:", json.dumps(pr, indent=1, ensure_ascii=False)[:3500])
dd = r2.get("diplomatic_dialogue")
if dd:
    print("dialogue re-attached, type:", dd.get("type"))
prp = r2.get("proposal_result_popup")
if prp:
    print("proposal_result_popup:", json.dumps(prp, indent=1, ensure_ascii=False)[:2000])

st3, ds = get("/debug/diplomatic_status")
print("\npost-armistice state Britain|France:",
      ds.get("diplomatic_states", {}).get("Britain|France"),
      "rel:", ds.get("nation_relations", {}).get("Britain|France"),
      "DP:", ds.get("diplomatic_points"))
save("g4_legE_e3_post_send_diplostatus.json", ds)
