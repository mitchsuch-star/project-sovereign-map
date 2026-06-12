"""Screens probe — is the recurring payment VISIBLE as rendered prose in
the morning dispatch / campaign log / ledgers? (Mechanics already proven.)
"""
import io
import json
import sys
import urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

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


NEEDLES = (
    "paid", "pays", "gold to", "obligation", "fulfilled", "recurring",
    "per turn", "tribute",
)


def prose_hits(obj):
    hits = []

    def walk(node, path=""):
        if isinstance(node, dict):
            for k, v in node.items():
                walk(v, f"{path}.{k}")
        elif isinstance(node, list):
            for idx, v in enumerate(node):
                walk(v, f"{path}[{idx}]")
        elif isinstance(node, str):
            low = node.lower()
            if any(n in low for n in NEEDLES) and "gold" in low:
                hits.append((path, node.strip()[:160]))

    walk(obj)
    seen = set()
    out = []
    for p, h in hits:
        if h not in seen:
            seen.add(h)
            out.append((p, h))
    return out


print("== setup (ratify 50x3 Prussia tribute) ==")
post("/new_game", {})
post("/command", {
    "command": "propose common peace with Britain",
    "action": "propose_common_peace",
    "target_nation": "Britain", "war_id": "war_1",
})
act("settlement_dial_generous", {"scope": "table"})
act("settlement_demand_add", {
    "nation": "Prussia", "group": "demand",
    "clause_type": "gold_per_turn", "amount": 50, "turns": 3,
})
act("submit_settlement_for_review")
rat = act("confirm_settlement")
print("ratified:", rat.get("success"))

print()
print("== end turn #1: where does the payment line render? ==")
r = post("/command", {"command": "end turn"})
for path, line in prose_hits(r):
    print(f"  [{path}]")
    print(f"      {line}")

print()
print("== campaign log ==")
try:
    log = get("/campaign_log")
    for path, line in prose_hits(log):
        print(f"  {line}")
except Exception as exc:
    print("  /campaign_log:", exc)

print()
print("== strategic ledger (economy) ==")
try:
    ledger = get("/ledger")
    hits = prose_hits(ledger)
    for path, line in hits:
        print(f"  [{path}] {line}")
    if not hits:
        print("  (no recurring-payment prose in the strategic ledger)")
except Exception as exc:
    print("  /ledger:", exc)

print()
print("== diplomatic ledger ==")
try:
    dledger = get("/diplomatic_ledger")
    hits = prose_hits(dledger)
    for path, line in hits:
        print(f"  [{path}] {line}")
    if not hits:
        print("  (no recurring-payment prose in the diplomatic ledger)")
except Exception as exc:
    print("  /diplomatic_ledger:", exc)
