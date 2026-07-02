"""Focused repro: confirm_settlement sent at a BLOCKED REVIEW — full payload capture."""
import json
import urllib.request

BASE = "http://127.0.0.1:8006"


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
    body = {"choice": action}
    body["action_params"] = dict(params or {}, action=action)
    return post("/respond_to_diplomatic_dialogue", body)


post("/new_game", {})
m = post("/command", {"command": "propose common peace with Britain",
                      "action": "propose_common_peace",
                      "target_nation": "Britain", "war_id": "war_1"})
sub = act("submit_settlement_for_review")
sd = sub.get("diplomatic_dialogue") or {}
print("REVIEW staged:", sd.get("dialogue_mode"), "| options:",
      [o.get("action") for o in sd.get("options", [])])

print()
print("---- send confirm_settlement (not in options) ----")
ref = act("confirm_settlement")
print("keys:", sorted(ref.keys()))
print(json.dumps({k: ref.get(k) for k in
                  ("success", "message", "error", "error_display", "detail")}, indent=1)[:600])
print("dialogue attached:", bool(ref.get("diplomatic_dialogue")))
with open("smoke_logs/g4_confirm_refusal_raw.json", "w", encoding="utf-8") as f:
    json.dump(ref, f, indent=1, default=str)

print()
print("---- state after ----")
st = get("/status")
print("pending dialogue in status:", bool(st.get("diplomatic_dialogue")))
mb = get("/mailbox")
print("mailbox count:", mb.get("count"), "| items:",
      [(i.get("dialogue_type"), i.get("title")) for i in (mb.get("items") or [])][:5])

print()
print("---- revise_settlement_terms after the refusal ----")
back = act("revise_settlement_terms")
print(json.dumps({k: back.get(k) for k in
                  ("success", "message", "error", "error_display")}, indent=1)[:500])
print("dialogue attached:", bool(back.get("diplomatic_dialogue")))

print()
print("---- ordinary command while (maybe) stuck ----")
c = post("/command", {"command": "status"})
print("status cmd success:", c.get("success"), "| msg head:", (c.get("message") or "")[:120])

print()
print("---- fresh REVIEW, then a FAKE action id ----")
post("/new_game", {})
post("/command", {"command": "propose common peace with Britain",
                  "action": "propose_common_peace",
                  "target_nation": "Britain", "war_id": "war_1"})
act("submit_settlement_for_review")
fake = act("settlement_totally_fake_action")
print(json.dumps({k: fake.get(k) for k in
                  ("success", "message", "error", "error_display")}, indent=1)[:500])
print("dialogue attached:", bool(fake.get("diplomatic_dialogue")))
back2 = act("revise_settlement_terms")
print("revise after fake — success:", back2.get("success"),
      "| dialogue attached:", bool(back2.get("diplomatic_dialogue")),
      "| mode:", (back2.get("diplomatic_dialogue") or {}).get("dialogue_mode"))
