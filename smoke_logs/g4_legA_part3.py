"""Leg A part 3 — reach carry via row territory offers, PARTIAL ratify (Russia
dropped, fights on), coalition effects, then FULL ratify on a fresh world +
archived re-entry + history surfaces."""
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


def cmd(text, **kw):
    return post("/command", dict({"command": text}, **kw))


def dlg(resp):
    return resp.get("diplomatic_dialogue") or {}


def rows(resp):
    return {r.get("nation"): r for r in (dlg(resp).get("per_court_acceptance") or [])}


def scores(resp):
    return {r.get("nation"): (r.get("total"), r.get("band"))
            for r in (dlg(resp).get("per_court_acceptance") or [])}


def mount():
    return cmd("propose common peace with Britain",
               action="propose_common_peace", target_nation="Britain", war_id="war_1")


def prep_world():
    post("/new_game", {})
    for c in ("Britain", "Austria", "Russia"):
        cmd(f"cheat set_war_exhaustion {c} 95")
    for reg in ("Hanover", "Tyrol", "Bohemia", "Wessex", "Volhynia", "Moravia",
                "Vienna", "London", "Podolia", "Livonia", "Courland"):
        cmd(f"cheat give_region {reg} France")


def add_territory_offer(resp, court):
    row = rows(resp).get(court) or {}
    toff = next((s for s in row.get("demand_suggestions") or []
                 if s.get("clause_type") == "territory_cede" and s.get("group") == "offer"), None)
    if not toff:
        print(f"  no territory offer suggestion on {court} row:",
              [(s.get("clause_type"), s.get("group")) for s in row.get("demand_suggestions") or []])
        return resp
    r = act("settlement_demand_add", dict(toff.get("action_params") or {}))
    print(f"  offer territory to {court}: success={r.get('success')}"
          f" err={(r.get('error_display') or '')[:70]} scores={scores(r)}")
    return r


print("== PARTIAL settlement: Russia dropped, Britain+Austria signed ==")
prep_world()
m = mount()
r = act("settlement_cover_drop", {"nation": "Russia"})
print("courts:", sorted(scores(r)))
# ease gold to the working plateau then add territory offers via rows
for _ in range(4):
    e = act("settlement_dial_generous", {"scope": "table"})
    if not e.get("success"):
        break
    r = e
print("after gold ease:", scores(r))
r = add_territory_offer(r, "Austria")
r = add_territory_offer(r, "Britain")
d = dlg(r)
oa = d.get("overall_acceptance") or {}
print("carries:", oa.get("carries"), "| verdict:", (oa.get("carry_verdict_display") or "")[:140])
if not oa.get("carries"):
    # try one more territory offer each if available
    r = add_territory_offer(r, "Austria")
    r = add_territory_offer(r, "Britain")
    d = dlg(r)
    oa = d.get("overall_acceptance") or {}
    print("carries after 2nd offers:", oa.get("carries"), scores(r))
if oa.get("carries"):
    sub = act("submit_settlement_for_review")
    sd = dlg(sub)
    print("REVIEW:", sd.get("dialogue_mode"), "| can_ratify:", sd.get("can_ratify"))
    print("options:", [(o.get("action"), o.get("label")) for o in sd.get("options", [])])
    EV["carrying_review"] = sub
    done = act("confirm_settlement")
    EV["partial_ratify"] = done
    print("ratified:", done.get("success"))
    print("message:", (done.get("message") or "")[:500])
    pr = done.get("proposal_result") or {}
    print("proposal_result keys:", sorted(pr.keys()) if isinstance(pr, dict) else pr)
    st = get("/status")
    wars = (st.get("active_wars") or {}).get("wars") or []
    print("wars after PARTIAL:", [(w.get("war_instance_id"), w.get("opponent"), w.get("opponents"))
                                  for w in wars])
    print("coalition:", json.dumps(get("/debug/coalition_status"), default=str)[:300])
    evs = done.get("events") or []
    print("events:", [(e.get("type"), (e.get("message") or "")[:90]) for e in evs][:10])
    led = get("/diplomatic_ledger")
    body = led.get("ledger") if isinstance(led.get("ledger"), dict) else led
    print("recent_settlements:", json.dumps(body.get("recent_settlements"), default=str)[:400])

print()
print("== FULL settlement on a fresh world (all three courts) + archived re-entry ==")
prep_world()
m = mount()
r = m
for _ in range(4):
    e = act("settlement_dial_generous", {"scope": "table"})
    if not e.get("success"):
        break
    r = e
print("after gold ease:", scores(r))
for court in ("Austria", "Britain", "Russia"):
    r = add_territory_offer(r, court)
d = dlg(r)
oa = d.get("overall_acceptance") or {}
print("carries:", oa.get("carries"), scores(r))
if not oa.get("carries"):
    for court in ("Austria", "Britain", "Russia"):
        r = add_territory_offer(r, court)
    d = dlg(r)
    oa = d.get("overall_acceptance") or {}
    print("carries 2nd round:", oa.get("carries"), scores(r))
if oa.get("carries"):
    act("submit_settlement_for_review")
    done = act("confirm_settlement")
    EV["full_ratify"] = done
    print("FULL ratified:", done.get("success"))
    print("message:", (done.get("message") or "")[:400])
    st = get("/status")
    wars = (st.get("active_wars") or {}).get("wars") or []
    print("wars after FULL:", [(w.get("war_instance_id"), w.get("opponent")) for w in wars])
    print("coalition:", json.dumps(get("/debug/coalition_status"), default=str)[:260])
    # archived re-entry (G4F-21)
    re_m = mount()
    print("re-entry: success:", re_m.get("success"),
          "| error:", re_m.get("error"),
          "| error_display:", (re_m.get("error_display") or "")[:140],
          "| recovery_route:", re_m.get("recovery_route"))
    led = get("/diplomatic_ledger")
    body = led.get("ledger") if isinstance(led.get("ledger"), dict) else led
    print("recent_settlements:", json.dumps(body.get("recent_settlements"), default=str)[:500])
    # pair states after full peace
    dip = get("/debug/diplomatic_status")
    print("dip keys:", sorted(dip.keys())[:12])
    txt = json.dumps(dip)
    for n in ("Britain", "Austria", "Russia"):
        idx = txt.find(f"France-{n}") if f"France-{n}" in txt else txt.find(f"{n}")
    states = dip.get("states") or dip.get("diplomatic_states") or {}
    if isinstance(states, dict):
        rel = {k: v for k, v in states.items()
               if "France" in k and any(n in k for n in ("Britain", "Austria", "Russia"))}
        print("France pair states:", rel)

with open("smoke_logs/g4_legA_part3_evidence.json", "w", encoding="utf-8") as fp:
    json.dump(EV, fp, indent=1, default=str)
print("saved.")
