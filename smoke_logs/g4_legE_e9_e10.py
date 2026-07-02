"""Leg E — reject offer, then E9 /status war surface + E10 capitals."""
import sys, json
sys.path.insert(0, "smoke_logs")
from g4_legE_lib import get, post, save

st, r = post("/respond_to_diplomatic_dialogue", {"choice": "reject_settlement_offer"})
print("reject offer:", st, r.get("success"), "| message:", json.dumps(r.get("message"), ensure_ascii=False)[:400])
save("g4_legE_e8_reject_offer.json", r)

# E9: /status
st, s = get("/status")
save("g4_legE_e9_status.json", s)
aw = s.get("active_wars") or {}
wars = aw.get("wars") or []
print("\nE9 wars:", len(wars))
for w in wars:
    print("war_instance_id:", w.get("war_instance_id"))
    print("opponent:", w.get("opponent"), "| opponent_display:", repr(w.get("opponent_display")))
    print("settlement_available:", w.get("settlement_available"),
          "| settlement_tier:", w.get("settlement_tier"),
          "| tier_display:", w.get("settlement_tier_display"))
    print("war_detail_actionability:", json.dumps(w.get("war_detail_actionability"), ensure_ascii=False)[:600])
    cs = w.get("contribution_share") or []
    print("contribution_share rows:", len(cs), "| overflow:", w.get("contribution_overflow_count"))
    for row in cs:
        print("   ", json.dumps(row, ensure_ascii=False)[:240])

# E10: /debug/war_scores
st, ws = get("/debug/war_scores")
save("g4_legE_e10_war_scores.json", ws)
print("\nE10 war_scores payload:")
print(json.dumps(ws, indent=1, ensure_ascii=False)[:3000])
