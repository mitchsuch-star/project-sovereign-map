"""Part-2 sweep legs 7/8 â€” save/load with a staged draft and with an active
recurring tribute stream."""
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


def dlg(resp):
    return resp.get("diplomatic_dialogue") or {}


print("== LEG 7: save/load with a staged draft ==")
post("/new_game", {})
post("/command", {
    "command": "propose common peace with Britain",
    "action": "propose_common_peace",
    "target_nation": "Britain", "war_id": "war_1",
})
act("settlement_demand_add", {
    "nation": "Britain", "clause_type": "gold_indemnity",
    "group": "demand", "amount": 275,
})
act("suspend_settlement_editor")
save_resp = post("/save", {"save_name": "part2probe"})
print("save:", save_resp.get("success"), (save_resp.get("message") or "")[:80])
post("/new_game", {})
load_resp = post("/load", {"filename": "part2probe.json"})
print("load:", load_resp.get("success"), (load_resp.get("message") or "")[:80])
reopen = post("/command", {
    "command": "propose common peace with Britain",
    "action": "propose_common_peace",
    "target_nation": "Britain", "war_id": "war_1",
})
reopen_dialogue = dlg(reopen)
terms = [
    t for t in (reopen_dialogue.get("settlement_terms") or [])
    if t.get("type") == "gold_indemnity"
]
print("draft restored with authored 275:",
      any(t.get("amount") == 275 for t in terms),
      "| terms:", json.dumps(terms)[:160])

print()
print("== LEG 8: save/load with an active recurring stream ==")
post("/new_game", {})
mount = post("/command", {
    "command": "propose common peace with Britain",
    "action": "propose_common_peace",
    "target_nation": "Britain", "war_id": "war_1",
})
recurring = act("settlement_demand_add", {
    "nation": "Britain", "clause_type": "gold_per_turn",
    "group": "demand", "amount": 50, "turns": 3,
})
print("recurring authored:", recurring.get("success"),
      recurring.get("error_display") or "")
current = dlg(recurring)
guard = 0
while guard < 10:
    guard += 1
    if (current.get("overall_acceptance") or {}).get("carries"):
        break
    current = dlg(act("settlement_dial_generous", {"scope": "table"}))
act("submit_settlement_for_review")
ratified = act("confirm_settlement")
print("ratified:", ratified.get("success"), (ratified.get("message") or "")[:100])
save2 = post("/save", {"save_name": "part2probe2"})
print("save:", save2.get("success"))
post("/new_game", {})
load2 = post("/load", {"filename": "part2probe2.json"})
print("load:", load2.get("success"))
end_turn = post("/command", {"command": "end turn"})
paid = [
    e for e in (end_turn.get("events") or [])
    if "paid" in str(e.get("message", "")).lower()
    and "gold" in str(e.get("message", "")).lower()
]
print("stream ticked after load:", len(paid) > 0,
      [(e.get("message") or "")[:110] for e in paid[:2]])
ledger = get("/ledger")
econ = (ledger.get("ledger") or {}).get("economy") or {}
print("ledger settlement_gold:", econ.get("settlement_gold"),
      "| streams:", json.dumps(econ.get("settlement_streams") or [])[:200])



