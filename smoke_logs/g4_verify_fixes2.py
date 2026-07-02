"""Final wire-verify of the E-1/E-2/E-3/E-4/E-5 fixes on the shipped 1805 boot."""
import json
import time
import urllib.request

BASE = "http://127.0.0.1:8006"

for _ in range(40):
    try:
        urllib.request.urlopen(BASE + "/test", timeout=2)
        break
    except Exception:
        time.sleep(1)


def post(path, body):
    req = urllib.request.Request(
        BASE + path, data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"}, method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)


def get(path):
    with urllib.request.urlopen(BASE + path, timeout=120) as r:
        return json.load(r)


def act(action, params=None):
    return post("/respond_to_diplomatic_dialogue",
                {"choice": action, "action_params": dict(params or {}, action=action)})


post("/new_game", {})

print("== E-1 + E-2: propose armistice with Russia (roster extraction + mount-time paradox) ==")
m = post("/command", {"command": "propose armistice with Russia"})
d = m.get("diplomatic_dialogue") or {}
print("mounted:", bool(d), "| target:", d.get("target_nation"))
print("commitment_block_warning:", (d.get("commitment_block_warning") or "")[:180])
if d:
    act("dismiss")

print()
print("== E-4: open borders to Saxony -> notice title must not say Rejected ==")
m2 = post("/command", {"command": "propose open borders with Saxony"})
if m2.get("diplomatic_dialogue"):
    send = act("execute_proposal")
    pr = send.get("proposal_result") or {}
    print("outcome:", pr.get("outcome"), "| msg:", (pr.get("message") or "")[:100])
    nt = get("/notifications")
    titles = [n.get("title") for n in (nt.get("notifications") or [])]
    print("notice titles:", titles[:4])

print()
print("== E-3 + E-5: soak to the Britain offer, check mailbox label, answer it ==")
for i in range(6):
    post("/command", {"command": "end turn"})
    mb = get("/mailbox")
    offers = [it for it in (mb.get("items") or [])
              if it.get("item_type") == "incoming_settlement_offer"]
    if offers:
        print(f"offer arrived turn ~{i+2}: summary_text: {offers[0].get('summary_text')}")
        post("/mailbox/activate", {"mailbox_id": offers[0].get("mailbox_id")})
        rej = act("reject_settlement_offer")
        print("reject resolved:", rej.get("success"),
              "| msg:", (rej.get("message") or "")[:120])
        mb2 = get("/mailbox")
        left = [it for it in (mb2.get("items") or [])
                if it.get("item_type") == "incoming_settlement_offer"]
        print("offer cleared from mailbox:", not left)
        break
else:
    print("no offer within 6 turns (cooldown/pressure timing) — covered by unit tests")
