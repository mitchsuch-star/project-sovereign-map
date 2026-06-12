"""Live wire probe — does a ratified gold_per_turn clause actually pay
each turn, and where does the player SEE it (dispatch / ledgers)?

Ratifies a 50-gold x 3-turn demand on Prussia in the multilateral smoke
war, then ends 4 turns watching: France's treasury, the morning dispatch
text, the strategic ledger economy section, and the diplomatic ledger.
"""
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
    with urllib.request.urlopen(BASE + path, timeout=30) as r:
        return json.load(r)


def act(action, params=None):
    body = {"choice": action}
    body["action_params"] = dict(params or {}, action=action)
    return post("/respond_to_diplomatic_dialogue", body)


def rows(resp):
    d = resp.get("diplomatic_dialogue") or {}
    return {
        r.get("nation"): r.get("total")
        for r in (d.get("per_court_acceptance") or [])
    }


def find_recurring_text(obj, needles=("recurring", "tribute", "gold per turn", "per turn")):
    """Walk any JSON payload and return strings mentioning the payment."""
    hits = []

    def walk(node):
        if isinstance(node, dict):
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)
        elif isinstance(node, str):
            low = node.lower()
            if any(n in low for n in needles):
                hits.append(node.strip()[:130])

    walk(obj)
    seen = set()
    out = []
    for h in hits:
        if h not in seen:
            seen.add(h)
            out.append(h)
    return out


print("== setup: mount, ease to carry, add 50x3 tribute on Prussia ==")
post("/new_game", {})
post("/command", {
    "command": "propose common peace with Britain",
    "action": "propose_common_peace",
    "target_nation": "Britain", "war_id": "war_1",
})
eased = act("settlement_dial_generous", {"scope": "table"})
print("after ease:", rows(eased))
added = act("settlement_demand_add", {
    "nation": "Prussia", "group": "demand",
    "clause_type": "gold_per_turn", "amount": 50, "turns": 3,
})
print("after add 50x3:", rows(added),
      "| ok:", added.get("success"), added.get("error_display"))
d = added.get("diplomatic_dialogue") or {}
oa = d.get("overall_acceptance") or {}
if not oa.get("carries"):
    extra = act("settlement_dial_generous", {"scope": "table"})
    print("extra ease:", rows(extra))
sub = act("submit_settlement_for_review")
print("review carries:", (sub.get("diplomatic_dialogue") or {}).get(
    "overall_acceptance", {}).get("carries"))
rat = act("confirm_settlement")
print("ratified:", rat.get("success"), "|",
      (rat.get("message") or "")[:110])

print()
print("== walk 4 turns ==")
for i in range(1, 5):
    r = post("/command", {"command": "end turn"})
    gold = r.get("gold")
    if gold is None:
        gs = r.get("game_state") or {}
        gold = gs.get("gold")
    mentions = find_recurring_text(r)
    print(f"--- end turn #{i}: France gold={gold}")
    for m in mentions:
        print("    dispatch/screen:", m)
    if not mentions:
        print("    (no recurring-payment text anywhere in the end-turn payload)")

print()
print("== ledgers after the run ==")
try:
    ledger = get("/ledger")
    for m in find_recurring_text(ledger):
        print("  strategic ledger:", m)
except Exception as e:
    print("  /ledger error:", e)
try:
    dledger = get("/diplomatic_ledger")
    for m in find_recurring_text(dledger):
        print("  diplomatic ledger:", m)
except Exception as e:
    print("  /diplomatic_ledger error:", e)
