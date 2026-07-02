# Gate 4 LEG B follow-up: corrected B9 (return_to_settlement_terms) and B10 discard
# sequencing (back_out_settlement is a REVIEW-mode affordance). Continues the live
# session on port 8007 where the scoped draft currently holds the dialed 50/50 terms.
import json
import urllib.request
import urllib.error

BASE = "http://127.0.0.1:8007"
OUT = "smoke_logs"
results = []


def save(name, obj):
    with open(f"{OUT}/{name}", "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


def post(path, body):
    req = urllib.request.Request(
        BASE + path, data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body_txt = e.read().decode("utf-8", errors="replace")
        try:
            return e.code, json.loads(body_txt)
        except Exception:
            return e.code, {"_raw_error_body": body_txt}


def respond(choice, action_params=None):
    body = {"choice": choice}
    if action_params is not None:
        body["action_params"] = action_params
    return post("/respond_to_diplomatic_dialogue", body)


def dlg(resp):
    return resp.get("diplomatic_dialogue") or {}


def sig(d):
    return json.dumps(d.get("settlement_terms"), sort_keys=True, ensure_ascii=False)


MODIFIED = json.dumps(
    [{"type": "peace"},
     {"type": "gold_indemnity", "from": "France", "to": "Britain", "amount": 50},
     {"type": "gold_indemnity", "from": "France", "to": "Prussia", "amount": 50}],
    sort_keys=True, ensure_ascii=False)
BASELINE = json.dumps(
    [{"type": "peace"},
     {"type": "gold_indemnity", "from": "France", "to": "Britain", "amount": 150},
     {"type": "gold_indemnity", "from": "France", "to": "Prussia", "amount": 150}],
    sort_keys=True, ensure_ascii=False)

# 1. remount (draft should restore the dialed 50/50 per PF-2)
st, m = post("/command", {"command": "propose common peace with Britain",
                          "action": "propose_common_peace",
                          "target_nation": "Britain", "war_id": "war_1"})
md = dlg(m)
save("g4_legB_fix_remount.json", m)
results.append({"step": "remount", "http": st, "mode": md.get("dialogue_mode"),
                "terms": md.get("settlement_terms"),
                "restored_modified": sig(md) == MODIFIED})

# record PROPOSE-mode option ids verbatim (for B5/B10 evidence)
results.append({"step": "propose_options_verbatim", "options": md.get("options", []),
                "available_action_ids": md.get("available_action_ids", [])})

# 2. submit -> REVIEW
st, rev = respond("submit_settlement_for_review", {"action": "submit_settlement_for_review"})
rd = dlg(rev)
save("g4_legB_fix_review.json", rev)
review_sig = sig(rd)
results.append({"step": "submit_review", "http": st, "mode": rd.get("dialogue_mode"),
                "terms": rd.get("settlement_terms")})

# 3. B9 proper: return_to_settlement_terms -> PROPOSE, same terms
st, back = respond("return_to_settlement_terms", {"action": "return_to_settlement_terms"})
bd = dlg(back)
save("g4_legB_fix_return_to_terms.json", back)
results.append({"step": "B9 return_to_settlement_terms", "http": st,
                "mode": bd.get("dialogue_mode"),
                "terms_match_review": sig(bd) == review_sig,
                "terms": bd.get("settlement_terms"),
                "message": (back.get("message") or "")[:400],
                "error_display": back.get("error_display")})

# 4. submit again -> REVIEW, then B10 discard: back_out_settlement
st, rev2 = respond("submit_settlement_for_review", {"action": "submit_settlement_for_review"})
rd2 = dlg(rev2)
results.append({"step": "resubmit_review", "http": st, "mode": rd2.get("dialogue_mode")})

st, bo = respond("back_out_settlement", {"action": "back_out_settlement"})
save("g4_legB_fix_backout.json", bo)
results.append({"step": "back_out_settlement (from REVIEW)", "http": st,
                "success": bo.get("success"),
                "message": (bo.get("message") or "")[:500],
                "error_display": bo.get("error_display"),
                "dialogue_after": bool(dlg(bo))})

# 5. remount -> fresh baseline expected (150/150)
st, m2 = post("/command", {"command": "propose common peace with Britain",
                           "action": "propose_common_peace",
                           "target_nation": "Britain", "war_id": "war_1"})
m2d = dlg(m2)
save("g4_legB_fix_remount_fresh.json", m2)
results.append({"step": "B10 remount after discard", "http": st,
                "mode": m2d.get("dialogue_mode"),
                "terms": m2d.get("settlement_terms"),
                "fresh_equals_baseline": sig(m2d) == BASELINE,
                "modified_discarded": sig(m2d) != MODIFIED})

# leave clean
respond("suspend_settlement_editor", {"action": "suspend_settlement_editor"})

save("g4_legB_fix_results.json", results)
print(json.dumps(results, indent=2, ensure_ascii=False))
