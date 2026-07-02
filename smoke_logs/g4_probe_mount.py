"""Gate 4 leg-A mount probe on the shipped 1805 boot (port 8006)."""
import json
import sys
import urllib.request

BASE = "http://127.0.0.1:" + (sys.argv[1] if len(sys.argv) > 1 else "8006")


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


ng = post("/new_game", {})
wars = (ng.get("active_wars") or {}).get("wars") or []
print("wars:", [(w.get("war_instance_id"), w.get("opponent"),
                 w.get("settlement_available"),
                 w.get("settlement_disabled_reason")) for w in wars])

war_id = wars[0].get("war_instance_id") if wars else None
print("war_id:", war_id)

m = post("/command", {
    "command": "propose common peace with Britain",
    "action": "propose_common_peace",
    "target_nation": "Britain", "war_id": war_id,
})
d = m.get("diplomatic_dialogue") or {}
print("mount success:", m.get("success"), "| dtype:", d.get("type"),
      "| mode:", d.get("dialogue_mode"))
print("message:", (m.get("message") or "")[:200])
print("error_display:", m.get("error_display"))
rows = d.get("per_court_acceptance") or []
print("courts:", [(r.get("nation"), r.get("total"), r.get("band")) for r in rows])
print("covered:", d.get("covered_enemy_participants"))
print("terms:", [(t.get("type"), t.get("target_nation") or t.get("from_nation"))
                 for t in (d.get("settlement_terms") or [])])
oa = d.get("overall_acceptance") or {}
print("overall:", {k: oa.get(k) for k in ("carries", "holdouts")})
print("treasury_line:", d.get("treasury_line"))
print("dialogue keys:", sorted(d.keys())[:40])
with open("smoke_logs/g4_legA_mount_raw.json", "w", encoding="utf-8") as f:
    json.dump(m, f, indent=1)
print("raw saved.")
