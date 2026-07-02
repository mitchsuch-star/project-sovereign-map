"""Leg E — E4b: open borders (trade-bearing treaty) with Denmark, full flow."""
import sys, json
sys.path.insert(0, "smoke_logs")
from g4_legE_lib import get, post, save

st, ds0 = get("/debug/diplomatic_status")
print("DP before:", ds0.get("diplomatic_points"))
st, cd0 = get("/debug/proposal_cooldowns")
print("cooldowns before:", json.dumps(cd0.get("player_proposal_cooldowns"), ensure_ascii=False))

st, r = post("/command", {"command": "propose open borders with Denmark"})
print("mount:", st, r.get("success"))
save("g4_legE_e4_openborders_denmark_mount.json", r)
dd = r.get("diplomatic_dialogue")
if dd:
    print("type:", dd.get("type"), "| est:", dd.get("acceptance_estimate"),
          "| outcome:", dd.get("acceptance_outcome"), "| dp_cost:", dd.get("dp_cost"))
    print("hint:", dd.get("acceptance_hint"))
    print("proposal_type_display:", dd.get("proposal_type_display"))
    st, r2 = post("/respond_to_diplomatic_dialogue", {"choice": "execute_proposal"})
    print("send:", st, r2.get("success"))
    save("g4_legE_e4_openborders_denmark_send.json", r2)
    print("message:", json.dumps(r2.get("message"), ensure_ascii=False)[:800])
    print("proposal_result:", json.dumps(r2.get("proposal_result"), indent=1, ensure_ascii=False)[:2000])
    print("DP on response:", r2.get("diplomatic_points"))
else:
    print("no dialogue:", json.dumps(r.get("message"), ensure_ascii=False)[:600])

st, ds1 = get("/debug/diplomatic_status")
print("DP after:", ds1.get("diplomatic_points"))
print("state Denmark|France:", ds1.get("diplomatic_states", {}).get("Denmark|France"),
      "| rel:", ds1.get("nation_relations", {}).get("Denmark|France"))
st, cd1 = get("/debug/proposal_cooldowns")
print("cooldowns after:", json.dumps(cd1.get("player_proposal_cooldowns"), ensure_ascii=False))
save("g4_legE_e4_cooldowns_after2.json", cd1)
