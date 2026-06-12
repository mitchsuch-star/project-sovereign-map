"""F1 forensic — where did the in-transit proposal resolution go?
Dump every top-level key of the end_turn response + mailbox after sending."""
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


import sys

cmd = "propose peace with Britain" if "peace" in sys.argv else "propose armistice with Britain"
post("/new_game", {})
r = post("/command", {"command": cmd})
d = r.get("diplomatic_dialogue") or {}
print("preview:", d.get("acceptance_estimate"), d.get("acceptance_outcome"))
send = act("execute_proposal")
print("send ok:", send.get("success"), "|", (send.get("message") or "")[:80])

for i in range(1, 4):
    et = post("/command", {"command": "end turn"})
    print(f"\n===== end_turn #{i} — non-empty keys =====")
    for k in sorted(et.keys()):
        v = et[k]
        if v in (None, "", [], {}, False):
            continue
        s = json.dumps(v) if not isinstance(v, str) else v
        print(f"  {k}: {s[:300]}")
    mb = get("/mailbox")
    print("  MAILBOX count:", mb.get("count"), "| items:",
          [(it.get("type"), it.get("title")) for it in (mb.get("items") or [])])
