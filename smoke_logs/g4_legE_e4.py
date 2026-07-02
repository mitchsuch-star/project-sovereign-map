"""Leg E — E4: back out armistice dialogue, then alliance to Prussia + trade to Denmark."""
import sys, json
sys.path.insert(0, "smoke_logs")
from g4_legE_lib import get, post, save

# clear the re-attached armistice dialogue
st, r = post("/respond_to_diplomatic_dialogue", {"choice": "reconsider"})
print("reconsider:", st, r.get("success"), str(r.get("message"))[:120])

st, cd0 = get("/debug/proposal_cooldowns")
save("g4_legE_e4_cooldowns_before.json", cd0)
print("cooldowns before:", json.dumps(cd0, ensure_ascii=False)[:600])
st, ds0 = get("/debug/diplomatic_status")
print("DP before:", ds0.get("diplomatic_points"), "/", ds0.get("max_diplomatic_points"))

# --- alliance to Prussia ---
st, r = post("/command", {"command": "propose alliance with Prussia"})
print("\nalliance mount:", st, r.get("success"))
save("g4_legE_e4_alliance_prussia_mount.json", r)
dd = r.get("diplomatic_dialogue")
if dd:
    print("type:", dd.get("type"), "| est:", dd.get("acceptance_estimate"),
          "| outcome:", dd.get("acceptance_outcome"), "| dp_cost:", dd.get("dp_cost"))
    print("hint:", dd.get("acceptance_hint"))
    st, r2 = post("/respond_to_diplomatic_dialogue", {"choice": "execute_proposal"})
    print("send:", st, r2.get("success"), "| message:", json.dumps(r2.get("message"), ensure_ascii=False)[:400])
    save("g4_legE_e4_alliance_prussia_send.json", r2)
    print("proposal_result:", json.dumps(r2.get("proposal_result"), ensure_ascii=False)[:1200])
    print("DP on response:", r2.get("diplomatic_points"))
else:
    print("no dialogue:", json.dumps(r.get("message"), ensure_ascii=False)[:400])

st, dsa = get("/debug/diplomatic_status")
print("DP after alliance:", dsa.get("diplomatic_points"))

# --- trade to Denmark ---
st, r = post("/command", {"command": "propose trade with Denmark"})
print("\ntrade mount:", st, r.get("success"))
save("g4_legE_e4_trade_denmark_mount.json", r)
dd = r.get("diplomatic_dialogue")
if dd:
    print("type:", dd.get("type"), "| est:", dd.get("acceptance_estimate"),
          "| outcome:", dd.get("acceptance_outcome"), "| dp_cost:", dd.get("dp_cost"))
    print("hint:", dd.get("acceptance_hint"))
    st, r2 = post("/respond_to_diplomatic_dialogue", {"choice": "execute_proposal"})
    print("send:", st, r2.get("success"), "| message:", json.dumps(r2.get("message"), ensure_ascii=False)[:400])
    save("g4_legE_e4_trade_denmark_send.json", r2)
    print("proposal_result:", json.dumps(r2.get("proposal_result"), ensure_ascii=False)[:1200])
    print("DP on response:", r2.get("diplomatic_points"))
else:
    print("no dialogue:", json.dumps(r.get("message"), ensure_ascii=False)[:400])

st, cd1 = get("/debug/proposal_cooldowns")
save("g4_legE_e4_cooldowns_after.json", cd1)
print("\ncooldowns after:", json.dumps(cd1, ensure_ascii=False)[:600])
st, ds1 = get("/debug/diplomatic_status")
print("DP after:", ds1.get("diplomatic_points"), "/", ds1.get("max_diplomatic_points"))
