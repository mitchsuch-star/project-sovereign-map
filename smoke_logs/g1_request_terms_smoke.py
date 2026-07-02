"""Slice G1 live smoke on the shipped 1805 boot (port 8006).
Leg 1: request -> next-turn GRANT -> real incoming offer with provenance,
answerable through the wire. Leg 2: cheat-shifted winning court -> voiced
REFUSAL + cooldown clock on the affordance. Leg 3: armistice paradox
exemption (D-G1-1a) — armistice sends where peace still blocks.
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


print("== LEG 1: request -> grant on the live coalition war ==")
post("/new_game", {})
row = war_row()
print("affordance at boot:", row.get("request_terms_state"))
r = cmd("request terms from Britain",
        action="request_terms", target_nation="Britain", war_id="war_1")
print("request:", r.get("success"), "|", (r.get("message") or "")[:120])
row = war_row()
print("state after click:", row.get("request_terms_state"))
et = cmd("end turn")
row = war_row()
print("state after end turn:", row.get("request_terms_state"))
mb = get("/mailbox")
offers = [i for i in (mb.get("items") or [])
          if i.get("item_type") == "incoming_settlement_offer"]
print("offer in mailbox:", [(o.get("summary_text"), o.get("source_nation")) for o in offers])
pe = get("/pending_envoy")
off = pe.get("incoming_settlement_offer") or {}
print("pending envoy dtype:", off.get("dialogue_type"), "| requested_by_player:",
      off.get("requested_by_player"))
nt = get("/notifications")
print("notice titles:", [n.get("title") for n in (nt.get("notifications") or [])][:4])
if offers:
    post("/mailbox/activate", {"mailbox_id": offers[0].get("mailbox_id")})
    rej = act("reject_settlement_offer")
    print("answerable (reject):", rej.get("success"), "|", (rej.get("message") or "")[:60])

print()
print("== LEG 2: refusal by a decisively winning court ==")
post("/new_game", {})
# Make the defenders decisively winning: give Britain French soil + exhaust France.
for reg in ("Flanders", "Picardy", "Normandy", "Champagne", "Burgundy", "Paris"):
    cmd(f"cheat give_region {reg} Britain")
print("war scores:", json.dumps(get("/debug/war_scores"))[:220])
r = cmd("request terms from Britain",
        action="request_terms", target_nation="Britain", war_id="war_1")
print("request:", r.get("success"))
cmd("end turn")
row = war_row()
print("state after end turn:", row.get("request_terms_state"))
nt = get("/notifications")
refusals = [n for n in (nt.get("notifications") or [])
            if n.get("type") == "settlement_terms_request_result"]
print("refusal notice:", [(n.get("title"), (n.get("message") or "")[:90]) for n in refusals])
cl = get("/campaign_log")
beats = [e for t in (cl.get("turns") or []) for e in (t.get("events") or [])
         if "terms_request" in str(e.get("type") or "")]
print("campaign log beats:", [(e.get("type"), (e.get("display") or "")[:70]) for e in beats])

print()
print("== LEG 3: armistice sends where peace still blocks (D-G1-1a) ==")
post("/new_game", {})
m = cmd("propose peace with Britain")
d = m.get("diplomatic_dialogue") or {}
print("peace mount block:", (d.get("commitment_block_warning") or "")[:100])
if d:
    act("dismiss")
m2 = cmd("propose armistice with Britain")
d2 = m2.get("diplomatic_dialogue") or {}
print("armistice mount block:", repr((d2.get("commitment_block_warning") or "")[:60]))
if d2:
    send = act("execute_proposal")
    print("armistice send:", send.get("success"), "|",
          (send.get("message") or "")[:130])
