"""Part-2 coverage sweep — the settlement surfaces no eyes have touched.
Legs: (1) coverage edits incl. last-court refusal, (2) holdout row
affordances, (3) white peace, (4) SC-28 discard notice, (5) dependency
clause authoring via rows, (6) archived-war re-entry, (7) save/load with a
staged draft, (8) save/load with an active recurring stream.
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


def mount():
    post("/new_game", {})
    return post("/command", {
        "command": "propose common peace with Britain",
        "action": "propose_common_peace",
        "target_nation": "Britain", "war_id": "war_1",
    })


def rows(resp):
    d = resp.get("diplomatic_dialogue") or {}
    return {r.get("nation"): r for r in (d.get("per_court_acceptance") or [])}


def dlg(resp):
    return resp.get("diplomatic_dialogue") or {}


print("===== LEG 1: coverage edits =====")
m = mount()
r = rows(m)
print("courts:", sorted(r))
prow = r.get("Prussia") or {}
print("Prussia holdout_actions:", [a.get("action") for a in (prow.get("holdout_actions") or [])])
drop_action = next((a for a in (prow.get("holdout_actions") or [])
                    if a.get("action") == "settlement_cover_drop"), None)
print("row Drop affordance present:", bool(drop_action))
dropped = act("settlement_cover_drop", dict((drop_action or {}).get("action_params") or {"nation": "Prussia"}))
dd = dlg(dropped)
print("after drop courts:", sorted(rows(dropped)))
print("covered:", dd.get("covered_enemy_participants"))
print("ignored_participants:", dd.get("ignored_participants"))
print("message:", (dropped.get("message") or "")[:140])
# re-add via the coverage suggestion
add_params = None
for key in ("coverage_suggestions", "cover_add_suggestions", "remaining_wars"):
    val = dd.get(key)
    if val:
        print(f"{key}:", json.dumps(val)[:240])
add_back = act("settlement_cover_add", {"nation": "Prussia"})
ab = dlg(add_back)
print("after add-back courts:", sorted(rows(add_back)), "| success:", add_back.get("success"))
# drop BOTH -> last covered court must refuse with reason
act("settlement_cover_drop", {"nation": "Prussia"})
last = act("settlement_cover_drop", {"nation": "Britain"})
ld = dlg(last)
print("drop LAST court: success:", last.get("success"),
      "| error_display:", last.get("error_display") or ld.get("error_display"))
print("dialogue still attached:", bool(ld), "| mode:", ld.get("dialogue_mode"))

print()
print("===== LEG 2: holdout Ease affordance =====")
m = mount()
r = rows(m)
brow = r.get("Britain") or {}
ease = next((a for a in (brow.get("holdout_actions") or [])
             if "generous" in str(a.get("action", "")) or "ease" in str(a.get("action", "")).lower()), None)
print("Britain row affordances:", [a.get("action") for a in (brow.get("holdout_actions") or [])])
if ease:
    before = (r.get("Britain") or {}).get("total")
    eased = act(ease["action"], dict(ease.get("action_params") or {}))
    after = (rows(eased).get("Britain") or {}).get("total")
    print(f"row Ease: {before} -> {after} | success: {eased.get('success')}")

print()
print("===== LEG 3: white peace =====")
m = mount()
d = dlg(m)
# remove every staged demand line via current_demands remove_action
removed = 0
guard = 0
while guard < 12:
    guard += 1
    d_rows = (d.get("per_court_acceptance") or [])
    line = None
    for row in d_rows:
        for cd in (row.get("current_demands") or []):
            if cd.get("remove_action"):
                line = cd
                break
        if line:
            break
    if not line:
        break
    resp = act("settlement_demand_remove", dict(line["remove_action"].get("action_params") or {}))
    if not resp.get("success"):
        print("remove refused:", resp.get("error_display"))
        break
    removed += 1
    d = dlg(resp)
print("removed lines:", removed)
terms_left = [t.get("type") for t in (d.get("settlement_terms") or [])]
print("terms left:", terms_left)
print("white_peace flag:", d.get("white_peace"))
sub = act("submit_settlement_for_review")
sd = dlg(sub)
print("submit success:", sub.get("success"), "| mode:", sd.get("dialogue_mode"))
print("white-peace copy present:",
      "white peace" in str(sd.get("talleyrand_text", "")).lower()
      or bool(sd.get("white_peace")))
print("options:", [(o.get("action"), o.get("label")) for o in sd.get("options", [])])

print()
print("===== LEG 4: SC-28 end-turn discard notice =====")
m = mount()
d = dlg(m)
authored = act("settlement_demand_add", {
    "nation": "Britain", "clause_type": "gold_indemnity",
    "group": "demand", "amount": 250,
})
print("authored:", authored.get("success"))
sus = act("suspend_settlement_editor")
print("suspended:", sus.get("success"))
et = post("/command", {"command": "end turn"})
notices = [e for e in (et.get("events") or [])
           if "draft" in str(e.get("message", "")).lower()
           or "discard" in str(e.get("type", "")).lower()
           or "settlement_draft" in str(e.get("type", ""))]
print("draft notices in events:", len(notices))
for n in notices[:3]:
    print("   ", n.get("type"), "|", (n.get("message") or "")[:160])
notif = [n for n in (et.get("notifications") or [])
         if "draft" in str(n.get("message", "")).lower()]
print("draft notices in notifications:", len(notif),
      [(n.get("title"), (n.get("message") or "")[:100]) for n in notif[:2]])

print()
print("===== LEG 5: dependency clause authoring via rows =====")
m = mount()
d = dlg(m)
for nation, row in rows(m).items():
    suggs = row.get("demand_suggestions") or []
    types = [s.get("clause_type") for s in suggs]
    print(f"{nation} suggestion types:", types)
    fa = next((s for s in suggs if s.get("clause_type") == "forced_alliance"), None)
    if fa:
        print(f"  forced_alliance on {nation}: supports_cs:", fa.get("supports_continental_system"),
              "| reason:", (fa.get("reason_display") or "")[:90])
        resp = act("settlement_demand_add", dict(fa.get("action_params") or {}))
        rd = dlg(resp)
        print("  authored forced_alliance:", resp.get("success"))
        threat_bits = [k for k in rd.keys() if "threat" in k.lower() or "coalition" in k.lower()]
        print("  threat keys on dialogue:", threat_bits)
        for k in threat_bits:
            print("   ", k, ":", json.dumps(rd.get(k))[:200])
        beats = rd.get("authoring_voice_beats") or []
        print("  voice beats:", [(b.get("kind"), (b.get("line") or "")[:80]) for b in beats])
        break

print()
print("===== LEG 6: archived-war re-entry =====")
m = mount()
d = dlg(m)
guard = 0
while guard < 10:
    guard += 1
    oa = (d.get("overall_acceptance") or {})
    if oa.get("carries"):
        break
    resp = act("settlement_dial_generous", {"scope": "table"})
    d = dlg(resp)
print("carries:", (d.get("overall_acceptance") or {}).get("carries"))
sub = act("submit_settlement_for_review")
sd = dlg(sub)
ratify = next((o for o in sd.get("options", []) if "confirm" in str(o.get("action", ""))), None)
print("ratify option:", ratify.get("action") if ratify else None)
if ratify:
    done = act(ratify["action"])
    print("ratified:", done.get("success"), "|", (done.get("message") or "")[:120])
    # now re-enter the archived war
    re_enter = post("/command", {
        "command": "propose common peace with Britain",
        "action": "propose_common_peace",
        "target_nation": "Britain", "war_id": "war_1",
    })
    red = dlg(re_enter)
    print("re-entry success:", re_enter.get("success"))
    print("re-entry dtype:", red.get("type"), "| mode:", red.get("dialogue_mode"))
    print("re-entry message:", (re_enter.get("message") or "")[:180])
    print("settlement_history present:", bool(re_enter.get("settlement_history") or red.get("settlement_history")))
