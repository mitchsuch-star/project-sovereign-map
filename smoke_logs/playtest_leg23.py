"""Gate-4 legs 2+3 API playtest (settlement_losing / settlement_rejected).

Run with the matching SOVEREIGN_SMOKE_START fixture on the server:
    python playtest_leg23.py losing
    python playtest_leg23.py rejected
"""
import json
import sys
import urllib.request

BASE = "http://127.0.0.1:8005"
PASS = []
FAIL = []


def post(path, body):
    req = urllib.request.Request(
        BASE + path, data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"}, method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("PASS " if cond else "FAIL ") + name + (f"  [{detail}]" if detail and not cond else ""))


def dialogue_action(action, params=None):
    body = {"choice": action}
    if params is not None:
        body["action_params"] = dict(params, action=action)
    return post("/respond_to_diplomatic_dialogue", body)


def mount(target="Britain"):
    post("/new_game", {})
    r = post("/command", {
        "command": f"propose common peace with {target}",
        "action": "propose_common_peace", "target_nation": target, "war_id": "war_1",
    })
    return r.get("diplomatic_dialogue") or {}


def material(d):
    return [t for t in d.get("settlement_terms") or [] if t.get("type") != "peace"]


leg = sys.argv[1] if len(sys.argv) > 1 else "losing"

if leg == "losing":
    d = mount()
    rows = d.get("per_court_acceptance") or []
    print("   [mount]", {r.get("nation"): (r.get("total"), r.get("direction")) for r in rows})
    print("   [terms]", [(t.get("type"), t.get("from"), t.get("to"), t.get("amount") or t.get("region")) for t in d.get("settlement_terms") or []])
    check("L2.1 PROPOSE mounts on the losing fixture", d.get("dialogue_mode") == "PROPOSE")
    concede_rows = [r for r in rows if r.get("direction") == "concede"]
    check("L2.2 concede-direction courts present", len(concede_rows) >= 1)
    france_paid = [t for t in material(d) if t.get("from") == "France"]
    check("L2.3 baseline authors France-paid concessions", len(france_paid) >= 1)
    # CH-4 convergence: the concession-baseline payload terms equal the same
    # generator's output the front door mounted (the rail can never diverge).
    baseline = d.get("concession_baseline") or {}
    check("L2.4 concession baseline payload present with reasoning",
          bool(baseline.get("terms")) and "lift acceptance" in str(baseline.get("reasoning") or ""))
    check("L2.5 baseline payload terms == mounted baseline terms",
          baseline.get("terms") == d.get("settlement_terms"),
          f"payload={baseline.get('terms')} mounted={d.get('settlement_terms')}")
    # D5/DC-4: press a concede court until a demand appears — the guard line
    # must ride the restage.
    target = concede_rows[0].get("nation") if concede_rows else "Britain"
    guard_seen = False
    r = None
    for _ in range(10):
        r = dialogue_action("settlement_dial_harsher", {"scope": target})
        if not r.get("success"):
            break
        d = r.get("diplomatic_dialogue") or d
        beats = d.get("authoring_voice_beats") or []
        if any("not the ones suing for peace" in str(b.get("line") or "") for b in beats):
            guard_seen = True
            break
    check("L2.6 pressing a winning court fires the DC-4 guard line", guard_seen)
    check("L2.7 presses never bounce the validator",
          (r or {}).get("error") != "submitted_terms_failed_revalidation")
    # Submit below threshold -> blocked REVIEW with the no-dead-end route.
    r = dialogue_action("submit_settlement_for_review")
    d_rev = r.get("diplomatic_dialogue") or {}
    opts = [o.get("action") for o in d_rev.get("options") or []]
    carries = bool((d_rev.get("overall_acceptance") or {}).get("carries"))
    print("   [REVIEW]", "carries=", carries, "options=", opts)
    if not carries:
        check("L2.8 blocked REVIEW omits confirm + offers return",
              "confirm_settlement" not in opts and "return_to_settlement_terms" in opts)
        r = dialogue_action("return_to_settlement_terms")
        d = r.get("diplomatic_dialogue") or {}
        check("L2.9 return re-stages PROPOSE", d.get("dialogue_mode") == "PROPOSE")
    else:
        check("L2.8 carrying losing REVIEW offers confirm", "confirm_settlement" in opts)
        check("L2.9 (skipped — table carried)", True)

elif leg == "rejected":
    d = mount()
    rows = d.get("per_court_acceptance") or []
    print("   [mount]", {r.get("nation"): (r.get("total"), r.get("direction")) for r in rows})
    check("L3.1 PROPOSE mounts on the rejected fixture", d.get("dialogue_mode") == "PROPOSE")
    # Make sure it does NOT carry, then submit into blocked REVIEW.
    for _ in range(6):
        if not bool((d.get("overall_acceptance") or {}).get("carries")):
            break
        r = dialogue_action("settlement_dial_harsher", {"scope": "table"})
        d = r.get("diplomatic_dialogue") or d
    r = dialogue_action("submit_settlement_for_review")
    d_rev = r.get("diplomatic_dialogue") or {}
    opts = [o.get("action") for o in d_rev.get("options") or []]
    carries = bool((d_rev.get("overall_acceptance") or {}).get("carries"))
    print("   [REVIEW]", "carries=", carries, "options=", opts)
    check("L3.2 blocked REVIEW is not a lone Back Out",
          not carries and len([o for o in opts if o != "back_out_settlement"]) >= 2)
    check("L3.3 confirm absent on blocked REVIEW", "confirm_settlement" not in opts)
    check("L3.4 War Detail recovery offered", "open_war_detail" in opts)
    check("L3.5 pair substitutes offered",
          "seek_bilateral_peace" in opts or "seek_armistice_instead" in opts)
    # Pair substitute hand-off — clicked from the blocked REVIEW where the
    # option lives — stages the bilateral proposal flow.
    r = dialogue_action("seek_bilateral_peace")
    check("L3.6 seek_bilateral_peace stages the bilateral proposal flow",
          r.get("success") is True and bool(r.get("diplomatic_dialogue")),
          f"{r.get('error')} {str(r.get('error_display') or '')[:70]} msg={str(r.get('message') or '')[:60]}")
    # Open War Detail preserves the draft and routes (fresh blocked REVIEW).
    d = mount()
    r = dialogue_action("submit_settlement_for_review")
    d_rev = r.get("diplomatic_dialogue") or {}
    r = dialogue_action("open_war_detail")
    route = r.get("recovery_route") or {}
    check("L3.7 open_war_detail routes to war detail (draft preservation proven by L3.8 restore)",
          r.get("success") is True and route.get("surface") == "war_detail",
          f"success={r.get('success')} err={r.get('error')} route={route} preserved={r.get('draft_preserved')}")
    # Reopen restores the preserved draft (PF-2 promise).
    r = post("/command", {
        "command": "propose common peace with Britain",
        "action": "propose_common_peace", "target_nation": "Britain", "war_id": "war_1",
    })
    d2 = r.get("diplomatic_dialogue") or {}
    check("L3.8 reopen restores the suspended draft",
          r.get("draft_restored_from_scope") is True and bool(d2.get("settlement_terms")))

print()
print(f"LEG {leg}: {len(PASS)} passed, {len(FAIL)} failed")
if FAIL:
    print("FAILED:", FAIL)
