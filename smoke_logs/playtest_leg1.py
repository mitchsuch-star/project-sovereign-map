"""Gate-4 leg-1 API playtest (multilateral, post-G4F fixes).

Drives the guided PROPOSE loop end to end through the real wire shapes the
Godot client sends, asserting the leg-1 verification focus.
"""
import json
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


def row(d, nation):
    for r in d.get("per_court_acceptance") or []:
        if r.get("nation") == nation:
            return r
    return {}


def gold_from(d, payer):
    return sum(
        int(t.get("amount", 0) or 0)
        for t in (d.get("settlement_terms") or [])
        if t.get("type") == "gold_indemnity" and t.get("from") == payer
    )


post("/new_game", {})
mount = post("/command", {
    "command": "propose common peace with Britain",
    "action": "propose_common_peace", "target_nation": "Britain", "war_id": "war_1",
})
d = mount.get("diplomatic_dialogue") or {}

# 1. Mount shape
check("1.1 PROPOSE mounts with baseline (never blank)", d.get("dialogue_mode") == "PROPOSE" and bool(d.get("settlement_terms")))
check("1.2 both courts in per_court_acceptance", {r.get("nation") for r in d.get("per_court_acceptance") or []} == {"Britain", "Prussia"})
check("1.3 rows authorable with suggestions", all(r.get("can_author") and (r.get("demand_suggestions")) for r in d.get("per_court_acceptance") or []))
check("1.4 treasury line present", isinstance(d.get("treasury_line"), dict))

# 2. Dials are live (the frozen-63 class)
b0 = row(d, "Britain").get("total")
r1 = dialogue_action("settlement_dial_harsher", {"scope": "table"})
d = r1.get("diplomatic_dialogue") or d
# ensure a gold demand exists to press: author one on each court
r_add_b = dialogue_action("settlement_demand_add", {"nation": "Britain", "clause_type": "gold_indemnity", "group": "demand", "amount": 300})
d = r_add_b.get("diplomatic_dialogue") or d
check("2.1 demand add succeeds with court reaction beat", r_add_b.get("success") is True and any(
    b.get("kind") == "court_reaction" for b in (d.get("authoring_voice_beats") or [])))
b_before = row(d, "Britain").get("total")
r2 = dialogue_action("settlement_dial_harsher", {"scope": "Britain"})
d2 = r2.get("diplomatic_dialogue") or {}
b_after = row(d2, "Britain").get("total")
check("2.2 focused press moves the pressed court's score", r2.get("success") is True and b_after is not None and b_before is not None and b_after < b_before,
      f"before={b_before} after={b_after}")
d = d2

# 3. Press to the cap — clamp + note, never a validator bounce
bounced = False
cap_note = False
for _ in range(14):
    r = dialogue_action("settlement_dial_harsher", {"scope": "table"})
    if r.get("error") == "submitted_terms_failed_revalidation":
        bounced = True
        break
    d = r.get("diplomatic_dialogue") or d
    if "can pay no more" in str(r.get("message") or ""):
        cap_note = True
check("3.1 no press ever bounces off the validator", not bounced)
check("3.2 ceiling press says so in voice", cap_note)
check("3.3 gold never exceeds payer balances", gold_from(d, "Prussia") <= 800 and gold_from(d, "Britain") <= 1500,
      f"prussia={gold_from(d, 'Prussia')} britain={gold_from(d, 'Britain')}")

# 4. Focus court — REFRONT-9 breakdown
r = dialogue_action("settlement_focus_court", {"nation": "Britain"})
d = r.get("diplomatic_dialogue") or d
focused = row(d, "Britain")
check("4.1 focused row carries 10-component breakdown", len(focused.get("component_breakdown") or []) >= 10)

# 5. Magnitude refusal in voice (explicit over balance)
line_params = None
for line in row(d, "Prussia").get("current_demands") or []:
    act = line.get("set_magnitude_action") or {}
    p = act.get("action_params") or {}
    if str(p.get("expected_type") or "") == "gold_indemnity":
        line_params = dict(p)
        break
if line_params is None:
    r_seed = dialogue_action("settlement_demand_add", {"nation": "Prussia", "clause_type": "gold_indemnity", "group": "demand", "amount": 100})
    d = r_seed.get("diplomatic_dialogue") or d
    for line in row(d, "Prussia").get("current_demands") or []:
        act = line.get("set_magnitude_action") or {}
        p = act.get("action_params") or {}
        if str(p.get("expected_type") or "") == "gold_indemnity":
            line_params = dict(p)
            break
r = dialogue_action("settlement_demand_set_magnitude", dict(line_params, amount=5000))
check("5.1 over-balance magnitude refused in voice", r.get("success") is False and "Sire" in str(r.get("error_display") or "") and "Prussia" in str(r.get("error_display") or ""),
      str(r.get("error_display") or "")[:80])
check("5.2 refusal re-attaches dialogue (CH-5)", bool(r.get("diplomatic_dialogue")))

# 6. Ease back down toward a carrying table — the player's real moves:
#    ease the table, Remove stubborn player lines, drop a final holdout.
def _carries(dd):
    return bool((dd.get("overall_acceptance") or {}).get("carries"))


for _ in range(16):
    if _carries(d):
        break
    r = dialogue_action("settlement_dial_generous", {"scope": "table"})
    if not r.get("success"):
        print("   [ease failed]", r.get("error"), str(r.get("error_display") or "")[:60])
        break
    d = r.get("diplomatic_dialogue") or d
if not _carries(d):
    # Remove any remaining player-authored gold lines (protected from dials).
    for nation in ("Britain", "Prussia"):
        for line in list(row(d, nation).get("current_demands") or []):
            act = line.get("remove_action") or {}
            p = act.get("action_params") or {}
            if p.get("clause_index") is None:
                continue
            r = dialogue_action("settlement_demand_remove", dict(p))
            if r.get("success"):
                d = r.get("diplomatic_dialogue") or d
if not _carries(d):
    # Final agency: drop the holdout court(s) — the designed escape.
    for holdout in list((d.get("overall_acceptance") or {}).get("holdout_courts") or []):
        covered = d.get("covered_enemy_participants") or []
        if len(covered) <= 1:
            break
        r = dialogue_action("settlement_cover_drop", {"nation": holdout})
        if r.get("success"):
            d = r.get("diplomatic_dialogue") or d
print("   [post-ease]", "carries=", _carries(d),
      "totals=", {rr.get("nation"): rr.get("total") for rr in d.get("per_court_acceptance") or []},
      "terms=", [(t.get("type"), t.get("from"), t.get("amount")) for t in d.get("settlement_terms") or []])
check("6.1 player agency reaches a carrying table", _carries(d))
r = dialogue_action("submit_settlement_for_review")
d_rev = r.get("diplomatic_dialogue") or {}
if not r.get("success"):
    print("   [submit]", r.get("error"), str(r.get("error_display") or "")[:80])
check("6.2 submit lands REVIEW", r.get("success") is True and d_rev.get("dialogue_mode") == "REVIEW")
check("6.3 REVIEW rows frozen (no dial affordances)", bool(d_rev.get("per_court_acceptance")) and all(
    not (rr.get("dial_actions") or rr.get("holdout_actions")) for rr in d_rev.get("per_court_acceptance") or []))

# 7. Carrying REVIEW: confirm offered, return-to-terms correctly absent
#    (that's the blocked-REVIEW recovery route). Ratify and verify routing.
rev_options = [o.get("action") for o in d_rev.get("options") or []]
print("   [carrying REVIEW options]", rev_options)
check("7.1 carrying REVIEW offers confirm_settlement", "confirm_settlement" in rev_options)
r = dialogue_action("confirm_settlement")
check("7.2 ratification succeeds", r.get("success") is True,
      f"{r.get('error')} {str(r.get('error_display') or '')[:60]}")
feedback = r.get("settlement_result_feedback") or {}
check("7.3 result feedback routes to ledger", feedback.get("review_target") == "ledger_settlements")
status = post("/command", {"command": "status"})
wars_after = ((status.get("active_wars") or {}).get("wars")) or []
check("7.4 ratified war leaves the active war list", len(wars_after) == 0,
      f"wars={[(w.get('opponent'), w.get('war_instance_id')) for w in wars_after]}")

# 8. Blocked REVIEW contract: fresh game, submit the not-yet-carrying mount
#    baseline straight to REVIEW; confirm must be absent, return-to-terms
#    present and working.
post("/new_game", {})
mount = post("/command", {
    "command": "propose common peace with Britain",
    "action": "propose_common_peace", "target_nation": "Britain", "war_id": "war_1",
})
d = mount.get("diplomatic_dialogue") or {}
if _carries(d):
    # press the table once so it stops carrying before the blocked submit
    r = dialogue_action("settlement_dial_harsher", {"scope": "table"})
    d = r.get("diplomatic_dialogue") or d
r = dialogue_action("submit_settlement_for_review")
d_rev = r.get("diplomatic_dialogue") or {}
blocked_options = [o.get("action") for o in d_rev.get("options") or []]
print("   [blocked REVIEW options]", blocked_options, "carries=", _carries(d_rev))
check("8.1 blocked REVIEW omits confirm_settlement", "confirm_settlement" not in blocked_options)
check("8.2 blocked REVIEW offers return_to_settlement_terms", "return_to_settlement_terms" in blocked_options)
r = dialogue_action("return_to_settlement_terms")
d = r.get("diplomatic_dialogue") or {}
check("8.3 return_to_settlement_terms re-stages PROPOSE with draft intact",
      d.get("dialogue_mode") == "PROPOSE" and bool(d.get("settlement_terms")))

print()
print(f"LEG 1: {len(PASS)} passed, {len(FAIL)} failed")
if FAIL:
    print("FAILED:", FAIL)
