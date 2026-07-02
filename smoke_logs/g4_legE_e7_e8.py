"""Leg E — E7: 3 end-turns tracking coalition threat/popups/subsidy; E8: AI traffic."""
import sys, json
sys.path.insert(0, "smoke_logs")
from g4_legE_lib import get, post, save

track = []
for t in range(1, 4):
    st, r = post("/command", {"command": "end turn"}, timeout=300)
    save(f"g4_legE_e7_endturn_{t}.json", r)
    entry = {
        "iteration": t,
        "status": st,
        "success": r.get("success"),
        "turn_after": (r.get("game_state") or {}).get("turn"),
        "threat_level_on_response": r.get("threat_level"),
        "coalition_popup": r.get("coalition_popup"),
        "coalition_brewing": r.get("coalition_brewing"),
        "incoming_proposal": bool(r.get("incoming_proposal")),
        "incoming_proposal_type": (r.get("incoming_proposal") or {}).get("proposal_type") if isinstance(r.get("incoming_proposal"), dict) else None,
        "pending_envoy_count": r.get("pending_envoy_count"),
    }
    st2, cs = get("/debug/coalition_status")
    entry["coalition_threat"] = cs.get("threat_level")
    entry["coalition_active"] = bool(cs.get("active_coalition"))
    entry["coalition_leader"] = (cs.get("active_coalition") or {}).get("leader")
    save(f"g4_legE_e7_coalition_t{t}.json", cs)
    st3, mb = get("/mailbox")
    entry["mailbox_count"] = len(mb.get("items") or mb.get("mailbox") or [])
    save(f"g4_legE_e8_mailbox_t{t}.json", mb)
    st4, pe = get("/pending_envoy")
    save(f"g4_legE_e8_pending_envoy_t{t}.json", pe)
    entry["pending_envoy"] = json.dumps(pe, ensure_ascii=False)[:200]
    st5, nt = get("/notifications")
    save(f"g4_legE_e8_notifications_t{t}.json", nt)
    entry["notification_count"] = len(nt.get("notifications") or [])
    track.append(entry)
    print(json.dumps(entry, ensure_ascii=False, indent=1))

save("g4_legE_e7_track.json", track)

# subsidy check: Austria gold via debug status if present
st, ds = get("/debug/diplomatic_status")
save("g4_legE_e7_diplostatus_after3turns.json", ds)
tal = ds.get("talleyrand")
print("talleyrand keys:", list(tal.keys()) if isinstance(tal, dict) else None)
