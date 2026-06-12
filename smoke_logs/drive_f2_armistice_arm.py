"""F2 probe — armistice pair-substitute arm visibility on blocked REVIEW.

Leg 1: fresh multilateral mount -> drop Prussia -> submit blocked -> which
substitute arms render?
Leg 2: same but WITHOUT the drop (both courts covered).
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
    oa = d.get("overall_acceptance") or {}
    print("    carries:", oa.get("carries"), "| holdouts:", oa.get("holdout_courts"))
    return d


print("== LEG 1: mount -> drop Prussia -> submit ==")
post("/new_game", {})
mount = post("/command", {
    "command": "propose common peace with Britain",
    "action": "propose_common_peace",
    "target_nation": "Britain", "war_id": "war_1",
})
show_options("MOUNT", mount)
drop = act("settlement_cover_drop", {"nation": "Prussia"})
show_options("AFTER DROP PRUSSIA", drop)
sub = act("submit_settlement_for_review")
show_options("SUBMIT (REVIEW)", sub)

print()
print("== LEG 2: fresh mount -> submit with both courts ==")
post("/new_game", {})
mount2 = post("/command", {
    "command": "propose common peace with Britain",
    "action": "propose_common_peace",
    "target_nation": "Britain", "war_id": "war_1",
})
sub2 = act("submit_settlement_for_review")
show_options("SUBMIT (REVIEW, 2 courts)", sub2)
