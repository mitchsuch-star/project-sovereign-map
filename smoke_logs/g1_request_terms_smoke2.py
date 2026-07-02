"""Slice G1 live smoke, take 2 — respects the war-age clock.
Boot -> end 2 turns (war eligible at turn 3) -> the periodic producer fires
spontaneously -> reject that offer -> the affordance returns AVAILABLE
(request bypasses the periodic cooldown) -> request -> end turn -> GRANT
with provenance. Then the refusal leg on a cheat-shifted winning court.
"""
import json
import time
import urllib.request

BASE = "http://127.0.0.1:8006"

for _ in range(40):
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


def get(path):
    with urllib.request.urlopen(BASE + path, timeout=120) as r:
        return json.load(r)


def act(action, params=None):
    return post("/respond_to_diplomatic_dialogue",
                {"choice": action, "action_params": dict(params or {}, action=action)})


def cmd(text, **kw):
    return post("/command", dict({"command": text}, **kw))


def war_row():
    wars = (get("/status").get("active_wars") or {}).get("wars") or []
    return next((w for w in wars if w.get("war_instance_id") == "war_1"), {})


def clear_spontaneous_offer():
    mb = get("/mailbox")
    offers = [i for i in (mb.get("items") or [])
              if i.get("item_type") == "incoming_settlement_offer"]
    for o in offers:
        post("/mailbox/activate", {"mailbox_id": o.get("mailbox_id")})
        act("reject_settlement_offer")
    return len(offers)


print("== LEG 1: grant with provenance (request bypasses the periodic cooldown) ==")
post("/new_game", {})
cmd("end turn")
cmd("end turn")  # turn 3: war age satisfies the producer minimum
cleared = clear_spontaneous_offer()
print("spontaneous offers rejected:", cleared)
rt = (war_row().get("request_terms_state") or {})
print("affordance now:", rt.get("state"), "|", rt.get("reason"))
r = cmd("request terms from Britain",
        action="request_terms", target_nation="Britain", war_id="war_1")
print("request:", r.get("success"), "|", (r.get("message") or "")[:110])
rt = (war_row().get("request_terms_state") or {})
print("after click:", rt.get("state"), rt.get("status"), "|", (rt.get("reason_display") or "")[:70])
cmd("end turn")
rt = (war_row().get("request_terms_state") or {})
print("after end turn:", rt.get("status"), "|", rt.get("resolve_reason"))
pe = get("/pending_envoy")
off = pe.get("incoming_settlement_offer") or {}
print("granted offer:", off.get("dialogue_type"), "| requested_by_player:",
      off.get("requested_by_player"), "| from:", off.get("proposer_nation"))
mb = get("/mailbox")
offers = [i for i in (mb.get("items") or [])
          if i.get("item_type") == "incoming_settlement_offer"]
print("mailbox row:", [(o.get("summary_text")) for o in offers])
if offers:
    post("/mailbox/activate", {"mailbox_id": offers[0].get("mailbox_id")})
    rej = act("reject_settlement_offer")
    print("answerable (reject):", rej.get("success"))

print()
print("== LEG 2: voiced refusal by a decisively winning court + cooldown clock ==")
post("/new_game", {})
cmd("end turn")
cmd("end turn")
clear_spontaneous_offer()
for reg in ("Flanders", "Picardy", "Normandy", "Champagne", "Burgundy", "Paris"):
    cmd(f"cheat give_region {reg} Britain")
cmd("end turn")  # let the stored per-pair war score absorb the map change
clear_spontaneous_offer()
r = cmd("request terms from Britain",
        action="request_terms", target_nation="Britain", war_id="war_1")
print("request:", r.get("success"))
cmd("end turn")
rt = (war_row().get("request_terms_state") or {})
print("state:", rt.get("status"), "|", rt.get("resolve_reason"),
      "| affordance:", rt.get("state"), "|", (rt.get("reason_display") or "")[:60])
nt = get("/notifications")
refusals = [n for n in (nt.get("notifications") or [])
            if n.get("type") == "settlement_terms_request_result"]
print("refusal notice:", [(n.get("title"), (n.get("message") or "")[:110]) for n in refusals])
cl = get("/campaign_log")
beats = [e for t in (cl.get("turns") or []) for e in (t.get("events") or [])
         if "terms_request" in str(e.get("type") or "")]
print("campaign log beats:", [(e.get("type"), (e.get("display") or "")[:80]) for e in beats])
