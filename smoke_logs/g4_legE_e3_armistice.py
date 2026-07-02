"""Leg E — E3: back out of peace dialogue, then propose armistice with Britain."""
import sys, json
sys.path.insert(0, "smoke_logs")
from g4_legE_lib import get, post, save

# Back out of the still-mounted peace proposal_confirm
st, r = post("/respond_to_diplomatic_dialogue", {"choice": "reconsider"})
print("reconsider status:", st, "success:", r.get("success"),
      "message:", json.dumps(r.get("message"), ensure_ascii=False)[:400])
save("g4_legE_e3_reconsider.json", r)

# Mount armistice
st, r = post("/command", {"command": "propose armistice with Britain"})
print("\narmistice mount status:", st, "success:", r.get("success"))
save("g4_legE_e3_armistice_mount.json", r)
dd = r.get("diplomatic_dialogue")
if not dd:
    print("NO dialogue; message:", json.dumps(r.get("message"), ensure_ascii=False)[:2000])
else:
    print("type:", dd.get("type"), "keys:", sorted(dd.keys()))
    for k in ("armistice_mechanics", "acceptance_estimate", "acceptance_outcome",
              "acceptance_hint", "ratification_gate_warning", "dp_cost",
              "proposal_type_display", "talleyrand_text", "warnings"):
        if k in dd:
            print(f"--- {k} ---")
            print(json.dumps(dd[k], indent=1, ensure_ascii=False)[:2500])
    print("--- options ---")
    print(json.dumps(dd.get("options"), indent=1, ensure_ascii=False)[:2500])
