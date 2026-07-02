"""Leg A part 2c — ease-ceiling behavior probe + heavy-pressure carry + PARTIAL ratify."""
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


def scores(resp):
    return {r.get("nation"): (r.get("total"), r.get("band"))
            for r in (dlg(resp).get("per_court_acceptance") or [])}


def mount():
    return cmd("propose common peace with Britain",
               action="propose_common_peace", target_nation="Britain", war_id="war_1")


print("== ease-ceiling escalation probe (does a 2nd/3rd click escalate or dead-end?) ==")
post("/new_game", {})
for c in ("Britain", "Austria", "Russia"):
    cmd(f"cheat set_war_exhaustion {c} 90")
for reg in ("Hanover", "Tyrol", "Bohemia", "Wessex", "Volhynia"):
    cmd(f"cheat give_region {reg} France")
m = mount()
act("settlement_cover_drop", {"nation": "Russia"})
last = None
for i in range(1, 9):
    r = act("settlement_dial_generous", {"scope": "table"})
    d = dlg(r)
    terms = [(t.get("type"), t.get("amount"), t.get("from_nation"), t.get("target_nation") or t.get("to_nation"))
             for t in (d.get("settlement_terms") or [])] if d else "N/A"
    beats = [(b.get("kind"), (b.get("line") or "")[:70]) for b in (d.get("authoring_voice_beats") or [])]
    print(f"ease {i}: success={r.get('success')} err={(r.get('error_display') or '')[:80]}")
    print(f"   scores={scores(r) if d else '-'}")
    print(f"   terms={terms}")
    if beats:
        print(f"   beats={beats}")
    if d:
        last = d
EV["ease_ladder"] = last

print()
print("== heavy pressure -> carry -> PARTIAL ratify ==")
post("/new_game", {})
for c in ("Britain", "Austria", "Russia"):
    cmd(f"cheat set_war_exhaustion {c} 95")
# take many enemy provinces incl. capitals region names on europe map
regions = ("Hanover", "Tyrol", "Bohemia", "Wessex", "Volhynia", "Anglia",
           "Mercia", "Carinthia", "Moravia", "Podolia", "Vienna", "London")
for reg in regions:
    r = cmd(f"cheat give_region {reg} France")
    print("  give", reg, "->", r.get("success"), (r.get("message") or "")[:44])
print("war scores:", json.dumps(get("/debug/war_scores"))[:280])
m = mount()
print("mounted:", scores(m))
drop = act("settlement_cover_drop", {"nation": "Russia"})
d = dlg(drop)
print("courts:", sorted(scores(drop)))
guard = 0
while guard < 10 and not (d.get("overall_acceptance") or {}).get("carries"):
    guard += 1
    r = act("settlement_dial_generous", {"scope": "table"})
    if not r.get("success"):
        print("  dial refused:", (r.get("error_display") or "")[:90])
        break
    d = dlg(r)
    print(f"  ease {guard}:", {rr.get('nation'): rr.get('total') for rr in (d.get('per_court_acceptance') or [])})
oa = d.get("overall_acceptance") or {}
print("carries:", oa.get("carries"))
if not oa.get("carries"):
    print("NOT carrying — stop here; verdict:", (oa.get("carry_verdict_display") or "")[:150])
else:
    sub = act("submit_settlement_for_review")
    sd = dlg(sub)
    print("REVIEW:", sd.get("dialogue_mode"), "| can_ratify:", sd.get("can_ratify"))
    print("options:", [(o.get("action"), o.get("label")) for o in sd.get("options", [])])
    EV["carrying_review"] = sub
    conf = next((o.get("action") for o in sd.get("options", []) if "confirm" in str(o.get("action", ""))), None)
    done = act(conf) if conf else {}
    EV["partial_ratify"] = done
    print("ratified:", done.get("success"))
    print("message:", (done.get("message") or "")[:400])
    st = get("/status")
    wars = (st.get("active_wars") or {}).get("wars") or []
    print("wars after PARTIAL ratify:", [(w.get("war_instance_id"), w.get("opponent"), w.get("opponents"))
                                         for w in wars])
    print("coalition:", json.dumps(get("/debug/coalition_status"), default=str)[:280])
    evs = done.get("events") or []
    print("events:", [(e.get("type"), (e.get("message") or "")[:80]) for e in evs][:10])
    led = get("/diplomatic_ledger")
    body = led.get("ledger") if isinstance(led.get("ledger"), dict) else led
    print("recent_settlements:", json.dumps(body.get("recent_settlements"), default=str)[:350])
    # re-entry on the archived-for-these-courts war
    re_m = mount()
    print("re-entry after partial: success:", re_m.get("success"),
          "| courts:", sorted(scores(re_m)), "| msg:", (re_m.get("message") or "")[:120],
          "| err:", (re_m.get("error_display") or "")[:120])

with open("smoke_logs/g4_legA_part2c_evidence.json", "w", encoding="utf-8") as fp:
    json.dump(EV, fp, indent=1, default=str)
print("saved.")
