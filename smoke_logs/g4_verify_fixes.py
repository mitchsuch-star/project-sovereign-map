"""Wire-verify the three leg-A fixes on the rebuilt server (port 8006).
G4S-1: unresolved choice on staged settlement dialogue -> CH-5 shape.
G4S-2: ease ladder now ceilings + escalates to territory instead of bouncing.
G4S-3: table narration uses the coverage-aware label.
"""
import json
import time
import urllib.request

BASE = "http://127.0.0.1:8006"

for _ in range(30):
    try:
        urllib.request.urlopen(BASE + "/test", timeout=2)
        break
    except Exception:
        time.sleep(1)


def post(path, body):
    req = urllib.request.Request(
        BASE + path, data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"}, method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)


def act(action, params=None):
    return post("/respond_to_diplomatic_dialogue",
                {"choice": action, "action_params": dict(params or {}, action=action)})


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


print("== G4S-3: narration label ==")
post("/new_game", {})
m = mount()
print("narration:", (dlg(m).get("multi_court_table_narration") or "")[:200])

print()
print("== G4S-1: unresolved choice at blocked REVIEW ==")
act("submit_settlement_for_review")
ref = act("confirm_settlement")
print("success:", ref.get("success"))
print("error:", ref.get("error"))
print("error_display:", (ref.get("error_display") or "")[:120])
print("dialogue re-attached:", bool(dlg(ref)), "| mode:", dlg(ref).get("dialogue_mode"))
back = act("return_to_settlement_terms")
print("return_to_settlement_terms still works:", back.get("success"),
      "| mode:", dlg(back).get("dialogue_mode"))
act("suspend_settlement_editor")

print()
print("== G4S-2: ease ladder ceilings -> territory escalation ==")
post("/new_game", {})
for c in ("Britain", "Austria", "Russia"):
    cmd(f"cheat set_war_exhaustion {c} 95")
for reg in ("Hanover", "Tyrol", "Bohemia", "Wessex", "Volhynia", "Moravia",
            "Vienna", "London", "Podolia", "Livonia", "Courland"):
    cmd(f"cheat give_region {reg} France")
m = mount()
r = act("settlement_cover_drop", {"nation": "Russia"})
for i in range(1, 9):
    resp = act("settlement_dial_generous", {"scope": "table"})
    d = dlg(resp)
    terms = [(t.get("type"), t.get("amount"), t.get("region"))
             for t in (d.get("settlement_terms") or [])]
    beats = [(b.get("kind"), (b.get("line") or "")[:80])
             for b in (d.get("authoring_voice_beats") or [])]
    oa = d.get("overall_acceptance") or {}
    print(f"ease {i}: ok={resp.get('success')} err={(resp.get('error_display') or '')[:60]}")
    print(f"   scores={scores(resp)} carries={oa.get('carries')}")
    print(f"   terms={terms}")
    if beats:
        print(f"   beats={beats}")
    if oa.get("carries"):
        print("CARRIES via dial ladder alone.")
        break
