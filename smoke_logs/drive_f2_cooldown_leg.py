"""F2 leg 3 — the F1->F2 coupling: a degraded armistice rejection sets
player_proposal_cooldowns[Britain_armistice]=6; what do the REVIEW arms
look like then? And what does the F1 wizard say for propose_armistice?
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
    with urllib.request.urlopen(BASE + path, timeout=60) as r:
        return json.load(r)


def act(action, params=None):
    body = {"choice": action}
    body["action_params"] = dict(params or {}, action=action)
    return post("/respond_to_diplomatic_dialogue", body)


def show_options(tag, resp):
    d = resp.get("diplomatic_dialogue") or {}
    print(f"--- {tag}: mode={d.get('dialogue_mode')} type={d.get('type')}")
    for o in d.get("options", []):
        marks = []
        if o.get("available") is False:
            marks.append("DISABLED")
        if o.get("disabled_reason_display"):
            marks.append(f"reason={o['disabled_reason_display']!r}")
        print(f"    [{o.get('action')}] {o.get('label')!r} {' '.join(marks)}")
    return d


post("/new_game", {})
print("== send armistice -> degraded rejection (the F1 path) ==")
post("/command", {"command": "propose armistice with Britain"})
act("execute_proposal")
et = post("/command", {"command": "end turn"})
pr = et.get("proposal_result") or {}
print("resolution:", pr.get("outcome"), "|", (pr.get("message") or "")[:90])

print()
print("== now mount settlement -> submit -> REVIEW arms ==")
mount = post("/command", {
    "command": "propose common peace with Britain",
    "action": "propose_common_peace",
    "target_nation": "Britain", "war_id": "war_1",
})
sub = act("submit_settlement_for_review")
show_options("SUBMIT (REVIEW) with cooldowns", sub)

print()
print("== F1 wizard availability for the same pair ==")
prev = get("/diplomatic_preview?nation=Britain")
for a in (prev.get("available_actions") or []):
    if "armistice" in str(a.get("action", "")) or "peace" in str(a.get("action", "")):
        print("   ", a.get("action"), "| available:", a.get("available"),
              "| reason:", a.get("disabled_reason_display") or a.get("reason") or a.get("disabled_reason"),
              "| likelihood:", a.get("likelihood"))
