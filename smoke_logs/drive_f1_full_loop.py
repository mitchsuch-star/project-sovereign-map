"""G4F-13 full-loop wire verification: honest preview -> send -> counter in
mailbox -> activate -> accept -> treaty ratified."""
import json
import urllib.request

BASE = "http://127.0.0.1:8005"


def post(path, body):
    req = urllib.request.Request(
        BASE + path, data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"}, method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def get(path):
    with urllib.request.urlopen(BASE + path, timeout=60) as r:
        return json.load(r)


def act(action, params=None):
    body = {"choice": action}
    body["action_params"] = dict(params or {}, action=action)
    return post("/respond_to_diplomatic_dialogue", body)


print("== LEG A: peace (constructible counter) ==")
post("/new_game", {})
r = post("/command", {"command": "propose peace with Britain"})
d = r.get("diplomatic_dialogue") or {}
print("preview:", d.get("acceptance_estimate"), d.get("acceptance_outcome"))
print("constructible:", d.get("counter_constructible"),
      "| display:", d.get("acceptance_outcome_display"))
act("execute_proposal")
et = post("/command", {"command": "end turn"})
counter_events = [e for e in (et.get("events") or [])
                  if "counter" in str(e.get("message", "")).lower()]
print("counter event:", (counter_events[0].get("message") or "")[:140] if counter_events else "NONE")

mb = get("/mailbox")
print("mailbox raw items:")
for it in (mb.get("items") or []):
    print("   ", json.dumps(it)[:220])
counter_item = next((it for it in (mb.get("items") or [])
                     if "counter" in json.dumps(it).lower()), None)
if counter_item:
    item_id = counter_item.get("mailbox_id")
    print("activating mailbox item:", item_id)
    actv = post("/mailbox/activate", {"mailbox_id": item_id})
    dd = actv.get("diplomatic_dialogue") or {}
    print("active dtype:", dd.get("type"))
    print("talleyrand:", (dd.get("talleyrand_text") or "")[:200])
    print("options:", [o.get("action") for o in dd.get("options", [])])
    inc = actv.get("incoming_proposal") or {}
    print("incoming popup: from", inc.get("from_nation"),
          "| is_counter:", inc.get("is_counter_offer"))
    acc = act("accept_counter_offer")
    print("accept:", acc.get("success"), "|", (acc.get("message") or "")[:160])
    state = get("/diplomatic_preview?nation=Britain")
    print("Britain state after accept:", state.get("current_state"))
else:
    print("!! counter not found in mailbox")

print()
print("== LEG B: armistice (unbridgeable by ~23 gold) ==")
post("/new_game", {})
r2 = post("/command", {"command": "propose armistice with Britain"})
d2 = r2.get("diplomatic_dialogue") or {}
print("preview:", d2.get("acceptance_estimate"), d2.get("acceptance_outcome"))
print("constructible:", d2.get("counter_constructible"),
      "| display:", d2.get("acceptance_outcome_display"))
