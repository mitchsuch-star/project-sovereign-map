"""Gate 4 leg A part 2b — save/load mid-draft, carry path via shifted field,
PARTIAL ratify (Russia dropped, fights on) + coalition effects, then FULL ratify
on a fresh world. Port 8006."""
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


def scores(resp_or_d):
    d = resp_or_d if isinstance(resp_or_d, dict) and "per_court_acceptance" in resp_or_d else dlg(resp_or_d)
    return {r.get("nation"): (r.get("total"), r.get("band")) for r in (d.get("per_court_acceptance") or [])}


def mount():
    return cmd("propose common peace with Britain",
               action="propose_common_peace", target_nation="Britain", war_id="war_1")


def shift_field():
    for c in ("cheat set_war_exhaustion Britain 90",
              "cheat set_war_exhaustion Austria 90",
              "cheat set_war_exhaustion Russia 90"):
        r = cmd(c)
        print(" ", c, "->", r.get("success"), (r.get("message") or "")[:50])
    for reg in ("Hanover", "Tyrol", "Bohemia", "Galicia", "Wessex", "Kent", "Volhynia"):
        r = cmd(f"cheat give_region {reg} France")
        print("  give", reg, "->", r.get("success"), (r.get("message") or "")[:50])


def ease_to_carry(d, max_iter=14):
    guard = 0
    while guard < max_iter:
        guard += 1
        if (d.get("overall_acceptance") or {}).get("carries"):
            break
        resp = act("settlement_dial_generous", {"scope": "table"})
        if not resp.get("success"):
            print("  dial refused:", resp.get("error_display"))
            break
        d = dlg(resp)
    return d


print("== C1 save/load mid-draft (PF-2 across save/load) ==")
post("/new_game", {})
m = mount()
brow = rows(m).get("Britain") or {}
gold = next((s for s in brow.get("demand_suggestions") or []
             if s.get("clause_type") == "gold_indemnity" and s.get("group") == "demand"), None)
r1 = act("settlement_demand_add", dict(gold.get("action_params") or {}))
authored = [(t.get("type"), t.get("amount")) for t in (dlg(r1).get("settlement_terms") or [])]
print("authored:", authored)
print("suspend:", act("suspend_settlement_editor").get("success"))
print("save:", post("/save", {"save_name": "g4_legA_draft"}).get("success"))
print("load:", post("/load", {"filename": "g4_legA_draft.json"}).get("success"))
re_m = mount()
restored = [(t.get("type"), t.get("amount")) for t in (dlg(re_m).get("settlement_terms") or [])]
print("restored:", restored, "| survived save/load:", restored == authored)
act("suspend_settlement_editor")

print()
print("== C2 shifted field -> PARTIAL settlement (drop Russia) ==")
post("/new_game", {})
shift_field()
print("war scores:", json.dumps(get("/debug/war_scores"))[:240])
m = mount()
print("mounted:", scores(m))
drop = act("settlement_cover_drop", {"nation": "Russia"})
print("dropped Russia:", sorted(scores(drop)))
d = ease_to_carry(dlg(drop))
oa = d.get("overall_acceptance") or {}
print("carries:", oa.get("carries"), "|", {n: s for n, s in scores(d).items()})
print("verdict:", (oa.get("carry_verdict_display") or "")[:160])
if oa.get("carries"):
    sub = act("submit_settlement_for_review")
    sd = dlg(sub)
    print("REVIEW mode:", sd.get("dialogue_mode"), "| can_ratify:", sd.get("can_ratify"))
    print("options:", [(o.get("action"), o.get("label")) for o in sd.get("options", [])])
    EV["carrying_review"] = sub
    conf = next((o.get("action") for o in sd.get("options", [])
                 if "confirm" in str(o.get("action", ""))), None)
    if conf:
        done = act(conf)
        EV["partial_ratify"] = done
        print("ratified:", done.get("success"))
        print("message:", (done.get("message") or "")[:400])
        pr = done.get("proposal_result") or {}
        print("proposal_result:", json.dumps(pr, default=str)[:400])
        st = get("/status")
        wars = (st.get("active_wars") or {}).get("wars") or []
        print("wars after PARTIAL ratify:", [(w.get("war_instance_id"), w.get("opponent"),
                                              w.get("opponents")) for w in wars])
        print("coalition after:", json.dumps(get("/debug/coalition_status"), default=str)[:300])
        dip = get("/debug/diplomatic_status")
        states = dip.get("diplomatic_states") or dip.get("states") or {}
        rel = {k: v for k, v in (states.items() if isinstance(states, dict) else [])
               if "France" in k and any(n in k for n in ("Britain", "Austria", "Russia"))}
        print("France pair states:", rel)
        evs = [e for e in (done.get("events") or [])]
        print("events:", [(e.get("type"), (e.get("message") or "")[:90]) for e in evs][:8])
        led = get("/diplomatic_ledger")
        rs = (led.get("ledger") or led).get("recent_settlements") if isinstance(led, dict) else None
        print("recent_settlements:", json.dumps(rs, default=str)[:400])

with open("smoke_logs/g4_legA_part2b_evidence.json", "w", encoding="utf-8") as fp:
    json.dump(EV, fp, indent=1, default=str)
print("evidence saved.")
