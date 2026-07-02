"""Leg E — E2 step 1 retry: plain-text command through the mock parser."""
import sys, json
sys.path.insert(0, "smoke_logs")
from g4_legE_lib import get, post, save

st, r = post("/command", {"command": "propose peace with Britain"})
print("status:", st, "success:", r.get("success"))
save("g4_legE_e2_peace_mount2.json", r)

dd = r.get("diplomatic_dialogue")
if dd:
    print("dialogue_type:", dd.get("dialogue_type") or dd.get("type"))
    print("dialogue keys:", sorted(dd.keys()))
    print("--- message ---")
    print(json.dumps(dd.get("message"), indent=1, ensure_ascii=False)[:4000])
    print("--- options ---")
    print(json.dumps(dd.get("options"), indent=1, ensure_ascii=False)[:4000])
    for k in ("ratification_gate_warning", "acceptance_estimate", "acceptance",
              "relation_gate", "armistice_mechanics", "warnings", "advisory",
              "terms", "proposal_type", "target_nation"):
        if k in dd:
            print(f"--- {k} ---")
            print(json.dumps(dd[k], indent=1, ensure_ascii=False)[:2500])
else:
    print("NO diplomatic_dialogue")
    print("message:", json.dumps(r.get("message"), ensure_ascii=False)[:3000])
    print("proposal_result:", json.dumps(r.get("proposal_result"), ensure_ascii=False)[:1500])
    print("error_display:", r.get("error_display"))
