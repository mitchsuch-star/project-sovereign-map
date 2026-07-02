"""Leg E — E8: activate one mailbox item, record round-trip dialogue dtype."""
import sys, json
sys.path.insert(0, "smoke_logs")
from g4_legE_lib import get, post, save

st, mb = get("/mailbox")
items = mb.get("items") or mb.get("mailbox") or []
print("mailbox now:", len(items), "items")
for it in items:
    print("  ", json.dumps(it, ensure_ascii=False)[:400])
if not items:
    print("mailbox empty — nothing to activate")
    sys.exit(0)
item = items[0]
iid = item.get("id") or item.get("item_id") or item.get("envoy_id")
print("activating id:", iid)
st, r = post("/mailbox/activate", {"id": iid, "item_id": iid, "envoy_id": iid})
print("activate status:", st, "success:", r.get("success"))
save("g4_legE_e8_activate.json", r)
dd = r.get("diplomatic_dialogue") or r.get("incoming_settlement_offer") or r.get("incoming_proposal")
if dd:
    print("dialogue dtype:", dd.get("dialogue_type") or dd.get("type"))
    print("keys:", sorted(dd.keys())[:25])
    print("options:", json.dumps([o.get("action") or o.get("label") for o in (dd.get("options") or [])], ensure_ascii=False))
else:
    print("no dialogue in response; top keys:", sorted(r.keys()))
    print("message:", json.dumps(r.get("message"), ensure_ascii=False)[:400])
