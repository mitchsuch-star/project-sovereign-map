"""Leg E — E1: new game + diplomatic status + coalition status."""
import sys
sys.path.insert(0, "smoke_logs")
from g4_legE_lib import get, post, save

st, ng = post("/new_game", {})
print("new_game status:", st, "success:", ng.get("success"))
save("g4_legE_new_game.json", ng)

wars = (ng.get("active_wars") or {}).get("wars", [])
print("wars:", len(wars))
for w in wars:
    print(" war:", w.get("war_instance_id"), "| opponent:", w.get("opponent"),
          "| opponent_display:", w.get("opponent_display"),
          "| settlement_available:", w.get("settlement_available"),
          "| settlement_tier:", w.get("settlement_tier"),
          "| actionability:", w.get("war_detail_actionability"))
    print("   contribution_share count:", len(w.get("contribution_share") or []))

st, ds = get("/debug/diplomatic_status")
save("g4_legE_diplomatic_status_t1.json", ds)
print("diplomatic_status keys:", list(ds.keys())[:20])

st, cs = get("/debug/coalition_status")
save("g4_legE_coalition_status_t1.json", cs)
print("coalition_status:", cs)
