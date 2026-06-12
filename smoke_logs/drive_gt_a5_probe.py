"""GT-A5 live probe — dial territory escalation at the gold ceiling.

Presses the whole table past both courts' budgets and watches the ladder:
gold grows -> ceiling -> ONE suggested territory demand per court -> notes.
Then eases twice to confirm the authored land walks back like any
suggested line. Real wire shapes (the popup's exact payloads).
"""
import json
import urllib.request

BASE = "http://127.0.0.1:8005"


def post(path, body):
    req = urllib.request.Request(
        BASE + path, data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"}, method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def dial(action):
    return post("/respond_to_diplomatic_dialogue", {
        "choice": action,
        "action_params": {"action": action, "scope": "table"},
    })


def show(tag, resp):
    d = resp.get("diplomatic_dialogue") or {}
    terms = d.get("settlement_terms") or []
    gold = [
        (t.get("from"), t.get("amount"))
        for t in terms if t.get("type") == "gold_indemnity"
    ]
    terr = [
        (t.get("from"), "->", t.get("to"), t.get("region"),
         t.get("authored_by"))
        for t in terms if str(t.get("type") or "").startswith("territory")
    ]
    rows = {
        r.get("nation"): r.get("total")
        for r in (d.get("per_court_acceptance") or [])
    }
    beats = [
        (b.get("kind"), (b.get("line") or "")[:72])
        for b in (d.get("authoring_voice_beats") or [])
    ]
    print(f"--- {tag}: scores={rows}")
    print("    gold:", gold)
    print("    territory:", terr)
    if beats:
        for kind, line in beats:
            print(f"    beat[{kind}]: {line}")


print("== new_game + mount ==")
post("/new_game", {})
mount = post("/command", {
    "command": "propose common peace with Britain",
    "action": "propose_common_peace",
    "target_nation": "Britain",
    "war_id": "war_1",
})
show("MOUNT", mount)

for i in range(1, 13):
    show(f"HARSHER #{i}", dial("settlement_dial_harsher"))

print("== walk-back: two generous clicks drop the authored land first ==")
for i in range(1, 3):
    show(f"GENEROUS #{i}", dial("settlement_dial_generous"))
