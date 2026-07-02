"""Leg E — E2 step 1: mount bilateral peace proposal to Britain, dump surface."""
import sys, json
sys.path.insert(0, "smoke_logs")
from g4_legE_lib import get, post, save

st, r = post("/command", {"command": "propose peace with Britain",
                          "action": "propose_peace",
                          "target_nation": "Britain"})
print("status:", st, "success:", r.get("success"))
save("g4_legE_e2_peace_mount.json", r)

dd = r.get("diplomatic_dialogue")
if dd:
    print("dialogue_type:", dd.get("dialogue_type") or dd.get("type"))
    print("dialogue keys:", sorted(dd.keys()))
    print("--- message ---")
    print(json.dumps(dd.get("message"), indent=1, ensure_ascii=False)[:3000])
    print("--- options ---")
    print(json.dumps(dd.get("options"), indent=1, ensure_ascii=False)[:3000])
    for k in ("ratification_gate_warning", "acceptance_estimate", "acceptance",
              "relation_gate", "armistice_mechanics", "warnings", "advisory"):
        if k in dd:
            print(f"--- {k} ---")
            print(json.dumps(dd[k], indent=1, ensure_ascii=False)[:2000])
else:
    print("NO diplomatic_dialogue")
    print("message:", json.dumps(r.get("message"), ensure_ascii=False)[:2000])
    print("proposal_result:", json.dumps(r.get("proposal_result"), ensure_ascii=False)[:1000])
    print("error_display:", r.get("error_display"))
    print("top keys:", sorted(r.keys()))
EOF_MARKER = None
