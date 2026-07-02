"""Gate 4 leg A part 2 — blocked REVIEW contract, save/load mid-draft, then the
carrying path: shift the field (cheats), ease to carries, ratify PARTIAL (Russia
dropped -> fights on, coalition effects) on the 1805 world with authored -80/-90
relations. Port 8006.
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


def cmd(text, **kw):
    return post("/command", dict({"command": text}, **kw))


def dlg(resp):
    return resp.get("diplomatic_dialogue") or {}


def rows(resp):
    return {r.get("nation"): r for r in (dlg(resp).get("per_court_acceptance") or [])}


def scores(resp):
    return {n: (r.get("total"), r.get("band")) for n, r in rows(resp).items()}


def mount():
    return cmd("propose common peace with Britain",
               action="propose_common_peace", target_nation="Britain", war_id="war_1")


print("== B1 blocked REVIEW contract (fresh turn-1 world) ==")
post("/new_game", {})
m = mount()
sub = act("submit_settlement_for_review")
sd = dlg(sub)
EV["blocked_review"] = sub
opts = [(o.get("action"), o.get("label")) for o in sd.get("options", [])]
aai = sd.get("available_action_ids") or []
print("mode:", sd.get("dialogue_mode"), "| can_ratify:", sd.get("can_ratify"))
print("options:", opts)
print("available_action_ids:", aai)
print("confirm absent from options:", all(o[0] != "confirm_settlement" for o in opts))
print("confirm absent from aai:", "confirm_settlement" not in aai)
print("ratify_blocked_reason:", (sd.get("ratify_blocked_reason") or "")[:200])
print("carry_verdict:", ((sd.get("overall_acceptance") or {}).get("carry_verdict_display") or "")[:200])
frozen = all(not (r.get("dial_actions") or r.get("holdout_actions") or r.get("demand_suggestions"))
             for r in (sd.get("per_court_acceptance") or []))
print("REVIEW rows frozen (no dials/holdouts/suggestions):", frozen)
print("hard_stops:", [(h.get("code"), h.get("code_display"), (h.get("detail") or "")[:80])
                      for h in (sd.get("hard_stops") or [])])

print()
print("== B2 confirm on blocked REVIEW must refuse without mutation ==")
ref = act("confirm_settlement")
print("success:", ref.get("success"), "| error_display:", (ref.get("error_display") or "")[:160])
print("dialogue re-attached:", bool(dlg(ref)), "| mode:", dlg(ref).get("dialogue_mode"))
wars_now = (get("/status").get("active_wars") or {}).get("wars") or []
print("war still active:", [w.get("war_instance_id") for w in wars_now])

print()
print("== B3 Return to terms preserves package ==")
terms_before = [(t.get("type"), t.get("amount")) for t in (sd.get("settlement_terms") or [])]
back = act("revise_settlement_terms")
bd = dlg(back)
print("mode:", bd.get("dialogue_mode"),
      "| terms:", [(t.get("type"), t.get("amount")) for t in (bd.get("settlement_terms") or [])],
      "| same as REVIEW:", terms_before == [(t.get("type"), t.get("amount")) for t in (bd.get("settlement_terms") or [])])

print()
print("== B4 save/load mid-draft (PF-2 across save/load) ==")
brow = rows(back).get("Britain") or {}
gold = next((s for s in brow.get("demand_suggestions") or []
             if s.get("clause_type") == "gold_indemnity" and s.get("group") == "demand"), None)
r1 = act("settlement_demand_add", dict(gold.get("action_params") or {}))
authored = [(t.get("type"), t.get("amount")) for t in (dlg(r1).get("settlement_terms") or [])]
print("authored terms:", authored)
sus = act("suspend_settlement_editor")
print("suspended:", sus.get("success"))
sv = post("/save", {"save_name": "g4_legA_draft"})
print("saved:", sv.get("success"))
ld = post("/load", {"save_name": "g4_legA_draft"})
print("loaded:", ld.get("success"))
re_m = mount()
restored = [(t.get("type"), t.get("amount")) for t in (dlg(re_m).get("settlement_terms") or [])]
print("restored terms:", restored, "| draft survived save/load:", restored == authored)
act("suspend_settlement_editor")

print()
print("== B5 shift the field: exhaustion + captured provinces ==")
post("/new_game", {})
for c in ("cheat set_war_exhaustion Britain 90",
          "cheat set_war_exhaustion Austria 90",
          "cheat set_war_exhaustion Russia 90"):
    r = cmd(c)
    print(c, "->", r.get("success"), (r.get("message") or "")[:60])
for reg in ("Hanover", "Tyrol", "Bohemia", "Galicia", "Wessex"):
    r = cmd(f"cheat give_region {reg} France")
    print("give", reg, "->", r.get("success"), (r.get("message") or "")[:60])
ws = get("/debug/war_scores")
print("war scores:", json.dumps(ws)[:300])

m = mount()
print("mounted scores:", scores(m))
print("mount message:", (m.get("message") or "")[:180])

# ease toward carries (bounded)
d = dlg(m)
guard = 0
while guard < 14:
    guard += 1
    oa = d.get("overall_acceptance") or {}
    if oa.get("carries"):
        break
    resp = act("settlement_dial_generous", {"scope": "table"})
    if not resp.get("success"):
        print("dial refused:", resp.get("error_display"))
        break
    d = dlg(resp)
    print(f"ease {guard}:", {n: r.get('total') for n, r in
                             {r2.get('nation'): r2 for r2 in (d.get('per_court_acceptance') or [])}.items()})
oa = d.get("overall_acceptance") or {}
print("carries:", oa.get("carries"), "| verdict:", (oa.get("carry_verdict_display") or "")[:160])
EV["carry_state"] = d
with open("smoke_logs/g4_legA_part2_evidence.json", "w", encoding="utf-8") as fp:
    json.dump(EV, fp, indent=1, default=str)
print("evidence saved (part2 stage1).")
