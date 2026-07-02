"""Gate 4 leg A part 1 — guided authoring surface on the shipped 1805 boot (port 8006).
Mount, rows/suggestions, demand verbs round-trip, dials, DC-4 guard, coverage edits,
focus breakdown, budget recommendation.
"""
import json
import urllib.request

BASE = "http://127.0.0.1:8006"
EV = {}


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


def dlg(resp):
    return resp.get("diplomatic_dialogue") or {}


def rows(resp):
    return {r.get("nation"): r for r in (dlg(resp).get("per_court_acceptance") or [])}


def scores(resp):
    return {n: (r.get("total"), r.get("band")) for n, r in rows(resp).items()}


def floats_in(obj, path=""):
    hits = []
    if isinstance(obj, float) and not obj.is_integer():
        hits.append(f"{path}={obj}")
    elif isinstance(obj, float):
        hits.append(f"{path}={obj} (whole float)")
    elif isinstance(obj, dict):
        for k, v in obj.items():
            hits.extend(floats_in(v, f"{path}.{k}"))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            hits.extend(floats_in(v, f"{path}[{i}]"))
    return hits


print("== A1 mount ==")
post("/new_game", {})
m = post("/command", {
    "command": "propose common peace with Britain",
    "action": "propose_common_peace",
    "target_nation": "Britain", "war_id": "war_1",
})
d = dlg(m)
EV["mount"] = m
print("mode:", d.get("dialogue_mode"), "| courts:", scores(m))
print("carry_verdict:", (d.get("overall_acceptance") or {}).get("carry_verdict_display"))
print("treasury:", d.get("treasury_line"))
print("narration:", (d.get("multi_court_table_narration") or "")[:220])
print("options:", [(o.get("action"), o.get("label")) for o in d.get("options", [])])

print()
print("== A2 rows: suggestions / authoring states / direction ==")
for n, r in rows(m).items():
    suggs = r.get("demand_suggestions") or []
    print(f"{n}: dir={r.get('direction')} lead={r.get('lead_group')} can_author={r.get('can_author')}"
          f" direct_score={r.get('direct_score')}")
    print("   sugg:", [(s.get("clause_type"), s.get("group"), (s.get("reason_display") or "")[:50])
                       for s in suggs][:8])
    print("   current:", [(c.get("line_display"), c.get("direction_display")) for c in (r.get("current_demands") or [])])
print("budget_bound_recommendation:", json.dumps(d.get("budget_bound_recommendation"))[:300])

print()
print("== A3 demand verbs round-trip (suggestion action_params verbatim) ==")
brow = rows(m)["Britain"]
gold = next((s for s in brow.get("demand_suggestions") or []
             if s.get("clause_type") == "gold_indemnity" and s.get("group") == "demand"), None)
print("gold demand suggestion:", json.dumps(gold)[:400] if gold else None)
if gold:
    r1 = act("settlement_demand_add", dict(gold.get("action_params") or {}))
    print("added:", r1.get("success"), "| scores:", scores(r1))
    cur = [(c.get("line_display"), c.get("clause_index")) for c in (rows(r1).get("Britain") or {}).get("current_demands", [])]
    print("Britain current_demands:", cur)
    EV["after_add"] = r1
    # set_magnitude via the ready-made payload
    line = next((c for c in (rows(r1).get("Britain") or {}).get("current_demands", [])
                 if c.get("set_magnitude_action")), None)
    if line:
        p = dict(line["set_magnitude_action"].get("action_params") or {})
        cur_amt = ((line.get("magnitude") or {}).get("value")
                   or (line.get("magnitude") or {}).get("amount") or 0)
        p["amount"] = int(cur_amt) + 100 if cur_amt else 200
        r2 = act("settlement_demand_set_magnitude", p)
        print("set_magnitude:", r2.get("success"), "| Britain:",
              [(c.get("line_display")) for c in (rows(r2).get("Britain") or {}).get("current_demands", [])],
              "| scores:", scores(r2))
    # remove via remove_action
    r2b = act("settlement_demand_remove", dict(
        next(c for c in (rows(r2).get("Britain") or {}).get("current_demands", [])
             if c.get("remove_action"))["remove_action"].get("action_params") or {}))
    print("removed:", r2b.get("success"), "| Britain current:",
          [(c.get("line_display")) for c in (rows(r2b).get("Britain") or {}).get("current_demands", [])])

print()
print("== A4 dials ==")
before = scores(act("settlement_focus_court", {"nation": "Britain"}))
h1 = act("settlement_dial_harsher", {"scope": "table"})
h2 = act("settlement_dial_harsher", {"scope": "table"})
print("harsher x2:", scores(h2), "| success:", h2.get("success"))
beats = dlg(h2).get("authoring_voice_beats") or []
print("beats:", [(b.get("kind"), (b.get("line") or "")[:80]) for b in beats])
g1 = act("settlement_dial_generous", {"scope": "table"})
print("generous x1:", scores(g1))
# DC-4 guard: explicit demand add on a concede-direction court (find one)
target = None
for n, r in rows(g1).items():
    if str(r.get("direction") or "").lower() in ("concede", "offer", "concede_direction"):
        target = n
        break
print("concede-direction court found:", target)
if target:
    row = rows(g1)[target]
    dsg = next((s for s in row.get("demand_suggestions") or [] if s.get("group") == "demand"), None)
    if dsg:
        rr = act("settlement_demand_add", dict(dsg.get("action_params") or {}))
        bb = dlg(rr).get("authoring_voice_beats") or []
        print("DC-4 beats after demand-on-concede-court:",
              [(b.get("kind"), (b.get("line") or "")[:100]) for b in bb])

print()
print("== A5 coverage edits at 3-court width ==")
cur = post("/command", {"command": "propose common peace with Britain",
                        "action": "propose_common_peace",
                        "target_nation": "Britain", "war_id": "war_1"})
print("courts:", sorted(rows(cur)))
drop = act("settlement_cover_drop", {"nation": "Russia"})
dd = dlg(drop)
print("after drop Russia:", sorted(rows(drop)), "| ignored:", dd.get("ignored_participants"),
      "| remaining_wars:", json.dumps(dd.get("remaining_wars"))[:200])
add = act("settlement_cover_add", {"nation": "Russia"})
print("after add-back:", sorted(rows(add)), "| success:", add.get("success"))
act("settlement_cover_drop", {"nation": "Russia"})
act("settlement_cover_drop", {"nation": "Austria"})
last = act("settlement_cover_drop", {"nation": "Britain"})
print("drop LAST:", last.get("success"), "| error:", last.get("error"),
      "| error_display:", (last.get("error_display") or "")[:160])
print("dialogue re-attached:", bool(dlg(last)))
act("settlement_cover_add", {"nation": "Austria"})
act("settlement_cover_add", {"nation": "Russia"})

print()
print("== A6 focus breakdown (REFRONT-9) ==")
f = act("settlement_focus_court", {"nation": "Britain"})
frow = rows(f).get("Britain") or {}
cb = frow.get("component_breakdown") or []
print("focused:", dlg(f).get("focused_court"), "| breakdown rows:", len(cb))
print("components:", [(c.get("component"), c.get("value")) for c in cb])
names = {c.get("component") for c in cb}
print("has concession_credit:", "concession_credit" in names, "| 10 components:", len(cb) == 10)

fl = floats_in(dlg(f), "dialogue")
print()
print("== float scan on final dialogue ==")
print("float hits:", fl[:10] if fl else "NONE")

with open("smoke_logs/g4_legA_part1_evidence.json", "w", encoding="utf-8") as fp:
    json.dump(EV, fp, indent=1, default=str)
print("evidence saved.")
