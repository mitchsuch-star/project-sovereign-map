"""G4F-8/9 live probe — confirmed pair-substitute handoff with terms
carry-over, and the eased bilateral suggestion (no more self-rejecting
Talleyrand). Real wire shapes."""
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


def act(action, params=None):
    body = {"choice": action}
    body["action_params"] = dict(params or {}, action=action)
    return post("/respond_to_diplomatic_dialogue", body)


print("== mount -> submit (blocked) ==")
post("/new_game", {})
post("/command", {
    "command": "propose common peace with Britain",
    "action": "propose_common_peace",
    "target_nation": "Britain", "war_id": "war_1",
})
sub = act("submit_settlement_for_review")
d = sub.get("diplomatic_dialogue") or {}
print("review options:", [o.get("action") for o in d.get("options", [])])
print("verdict:", (d.get("overall_acceptance") or {}).get("carry_verdict_display"))

print()
print("== click 'Make peace with Britain only' -> chooser ==")
ch = act("seek_bilateral_peace")
cd = ch.get("diplomatic_dialogue") or {}
print("dtype:", cd.get("type"))
print("options:", [o.get("action") for o in cd.get("options", [])])
print("talleyrand:", (cd.get("talleyrand_text") or "")[:110])

print()
print("== cancel -> REVIEW restored ==")
keep = act("keep_joint_settlement")
kd = keep.get("diplomatic_dialogue") or {}
print("mode:", kd.get("dialogue_mode"), "| type:", kd.get("type"))

print()
print("== again -> confirm -> bilateral with carried terms ==")
ch2 = act("seek_bilateral_peace")
conf = act("confirm_pair_substitute")
bd = conf.get("diplomatic_dialogue") or {}
print("dtype:", bd.get("type"), "| carried:", bd.get("carried_from_settlement"))
for opt in bd.get("options", []):
    if opt.get("action") == "execute_proposal" and opt.get("terms"):
        t = opt["terms"]
        print("demands:", t.get("demands"))
        print("sweeteners:", t.get("sweeteners"))
        break
print("acceptance:", bd.get("acceptance_estimate"), bd.get("acceptance_outcome"))
print("harshness:", bd.get("harshness_label"))
tt = str(bd.get("talleyrand_text") or "")
print("voice contradiction present:", "rewards their failure" in tt)
