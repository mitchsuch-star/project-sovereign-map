"""Leg E — E8 retry: activate mailbox item 8 with correct field name."""
import sys, json
sys.path.insert(0, "smoke_logs")
from g4_legE_lib import get, post, save

st, r = post("/mailbox/activate", {"mailbox_id": 8})
print("activate status:", st, "success:", r.get("success"))
save("g4_legE_e8_activate2.json", r)
dd = (r.get("diplomatic_dialogue") or r.get("incoming_settlement_offer")
      or r.get("incoming_proposal") or r.get("popup"))
if dd:
    print("dialogue dtype:", dd.get("dialogue_type") or dd.get("type"))
    print("keys:", sorted(dd.keys()))
    opts = dd.get("options") or []
    print("options:", json.dumps([{ "label": o.get("label"), "action": o.get("action")} for o in opts], ensure_ascii=False))
    for k in ("message", "summary", "title", "offer_summary", "terms_display"):
        if dd.get(k):
            print(k, ":", json.dumps(dd[k], ensure_ascii=False)[:600])
else:
    print("no dialogue; top keys:", sorted(r.keys()))
    print(json.dumps(r, ensure_ascii=False)[:1500])
