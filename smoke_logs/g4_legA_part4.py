"""Leg A part 4 — post-ratify dispatch/campaign-log reflection, mounted-draft-wins
same-war refresh, end-turn discard notice on the 1805 boot."""
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


def cmd(text, **kw):
    return post("/command", dict({"command": text}, **kw))


def dlg(resp):
    return resp.get("diplomatic_dialogue") or {}


def rows(resp):
    return {r.get("nation"): r for r in (dlg(resp).get("per_court_acceptance") or [])}


def mount():
    return cmd("propose common peace with Britain",
               action="propose_common_peace", target_nation="Britain", war_id="war_1")


print("== ratify then check campaign log + dispatch ==")
post("/new_game", {})
for c in ("Britain", "Austria", "Russia"):
    cmd(f"cheat set_war_exhaustion {c} 95")
for reg in ("Hanover", "Tyrol", "Bohemia", "Wessex", "Volhynia", "Moravia",
            "Vienna", "London", "Podolia", "Livonia", "Courland"):
    cmd(f"cheat give_region {reg} France")
r = mount()
for _ in range(3):
    e = act("settlement_dial_generous", {"scope": "table"})
    if not e.get("success"):
        break
    r = e
for court in ("Austria", "Britain", "Russia"):
    row = rows(r).get(court) or {}
    toff = next((s for s in row.get("demand_suggestions") or []
                 if s.get("clause_type") == "territory_cede" and s.get("group") == "offer"), None)
    if toff:
        r = act("settlement_demand_add", dict(toff.get("action_params") or {}))
oa = dlg(r).get("overall_acceptance") or {}
print("carries:", oa.get("carries"))
act("submit_settlement_for_review")
done = act("confirm_settlement")
print("ratified:", done.get("success"))

cl = get("/campaign_log")
entries = cl.get("entries") or cl.get("log") or []
settle = [e for e in entries if "settle" in json.dumps(e).lower()]
print("campaign log settlement entries:", len(settle))
for e in settle[:4]:
    print("  ", json.dumps(e, default=str)[:220])

et = cmd("end turn")
dp = get("/dispatch")
dtxt = json.dumps(dp, default=str)
i = dtxt.lower().find("settlement")
print("dispatch mentions settlement:", i >= 0)
if i >= 0:
    print("  ...", dtxt[max(0, i - 80): i + 240].replace("\\n", " "))
print("raw-key scan in dispatch:", [k for k in ("KingdomOfItaly", "PapalStates") if k in dtxt])

print()
print("== mounted-draft-wins same-war refresh (GT-Slice-4 s6) ==")
post("/new_game", {})
m = mount()
brow = rows(m).get("Britain") or {}
gold = next((s for s in brow.get("demand_suggestions") or []
             if s.get("clause_type") == "gold_indemnity" and s.get("group") == "demand"), None)
r1 = act("settlement_demand_add", dict(gold.get("action_params") or {}))
t1 = [(t.get("type"), t.get("amount")) for t in (dlg(r1).get("settlement_terms") or [])]
print("mounted draft terms:", t1)
m2 = mount()  # same war, dialogue still staged
t2 = [(t.get("type"), t.get("amount")) for t in (dlg(m2).get("settlement_terms") or [])]
print("refresh success:", m2.get("success"), "| terms after refresh:", t2)
print("mounted draft preserved:", t1 == t2, "| msg:", (m2.get("message") or "")[:140],
      "| err:", (m2.get("error_display") or "")[:140])

print()
print("== end-turn discard notice names court + authored work (G4F-22) ==")
post("/new_game", {})
m = mount()
brow = rows(m).get("Britain") or {}
gold = next((s for s in brow.get("demand_suggestions") or []
             if s.get("clause_type") == "gold_indemnity" and s.get("group") == "demand"), None)
act("settlement_demand_add", dict(gold.get("action_params") or {}))
act("suspend_settlement_editor")
et = cmd("end turn")
txt = json.dumps(et, default=str)
idx = txt.find("set aside")
print("notice present:", idx >= 0)
if idx >= 0:
    print("  ...", txt[max(0, idx - 160): idx + 80])
else:
    idx2 = txt.lower().find("draft")
    print("  'draft' context:", txt[max(0, idx2 - 120): idx2 + 120] if idx2 >= 0 else "NONE")
