"""G4F-13 constructible-counter wire loop: grow treasury one turn, propose
armistice (bridge affordable), counter arrives, activate, accept, ARMISTICE
ratified."""
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


post("/new_game", {})
post("/command", {"command": "end turn"})  # treasury 1177 -> ~1576
r = post("/command", {"command": "propose armistice with Britain"})
d = r.get("diplomatic_dialogue") or {}
print("preview:", d.get("acceptance_estimate"), d.get("acceptance_outcome"))
print("constructible:", d.get("counter_constructible"),
      "| display:", d.get("acceptance_outcome_display"))
print("gate warning:", d.get("ratification_gate_warning"))
if not d.get("counter_constructible"):
    print("!! still not constructible — stopping")
    raise SystemExit(0)
act("execute_proposal")
et = post("/command", {"command": "end turn"})
mb = get("/mailbox")
counter_item = next((it for it in (mb.get("items") or [])
                     if it.get("item_type") == "counter_offer_response"), None)
print("counter in mailbox:", bool(counter_item))
if counter_item:
    actv = post("/mailbox/activate", {"mailbox_id": counter_item.get("mailbox_id")})
    inc = actv.get("incoming_proposal") or {}
    print("popup from:", inc.get("from_nation"), "| is_counter:", inc.get("is_counter_offer"))
    print("popup terms:", json.dumps(inc.get("terms") or inc.get("annotated_terms") or {})[:240])
    acc = act("accept_counter_offer")
    print("accept:", acc.get("success"), "|", (acc.get("message") or "")[:170])
    state = get("/diplomatic_preview?nation=Britain")
    print("Britain state after accept:", state.get("current_state"))
