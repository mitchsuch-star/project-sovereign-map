"""Gate-4 leg-1 finding reproduction driver (read-only investigation aid).

Mirrors the Godot client's exact wire shapes:
- POST /command with structured propose_common_peace (war detail Open Settlement)
- POST /respond_to_diplomatic_dialogue {"choice": ..., "action_params": ...}
"""
import json
import urllib.request

BASE = "http://127.0.0.1:8005"


def post(path, body):
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def dlg_of(resp):
    return resp.get("diplomatic_dialogue") or {}


def summarize(tag, resp):
    d = dlg_of(resp)
    pca = d.get("per_court_acceptance") or []
    oa = d.get("overall_acceptance") or {}
    terms = d.get("settlement_terms") or []
    gold = [
        (t.get("from"), t.get("amount"))
        for t in terms
        if t.get("type") == "gold_indemnity"
    ]
    print(f"--- {tag}")
    print(
        "  success:", resp.get("success"),
        "| error:", resp.get("error"),
        "| error_display:", (resp.get("error_display") or "")[:70],
    )
    print("  message:", (resp.get("message") or "")[:90])
    print(
        "  mode:", d.get("dialogue_mode"),
        "| covered:", d.get("covered_enemy_participants"),
        "| carries:", oa.get("carries"),
        "| holdouts:", oa.get("holdout_courts"),
    )
    print("  gold terms:", gold)
    for r in pca:
        print(
            "   row:", r.get("nation"),
            "| total:", r.get("total"),
            "| dir:", r.get("direction"),
            "| can_author:", r.get("can_author"),
            "| sugg:", len(r.get("demand_suggestions") or []),
            "| cur_demands:", len(r.get("current_demands") or []),
            "| dial_actions:", [a.get("action") for a in (r.get("dial_actions") or [])],
        )
    return d


print("== new_game ==")
post("/new_game", {})

print("== open settlement (structured propose_common_peace) ==")
mount = post("/command", {
    "command": "propose common peace with Britain",
    "action": "propose_common_peace",
    "target_nation": "Britain",
    "war_id": "war_1",
})
d = summarize("MOUNT", mount)
print("  treasury_line:", json.dumps(d.get("treasury_line"))[:160])
print("  options:", [
    (o.get("action"), o.get("label")) for o in (d.get("options") or [])
])

# Replay the rail Harsher affordance exactly as the popup would.
for i in range(1, 7):
    resp = post("/respond_to_diplomatic_dialogue", {
        "choice": "settlement_dial_harsher",
        "action_params": {"action": "settlement_dial_harsher", "scope": "table"},
    })
    d = summarize(f"HARSHER #{i}", resp)

print("== focused: Press Prussia ==")
resp = post("/respond_to_diplomatic_dialogue", {
    "choice": "settlement_dial_harsher",
    "action_params": {"action": "settlement_dial_harsher", "scope": "Prussia"},
})
summarize("PRESS PRUSSIA", resp)
