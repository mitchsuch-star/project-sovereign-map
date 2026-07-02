# Gate 4 manual smoke — LEG B (settlement_rejected preset, port 8007)
# READ-ONLY driver: exercises the blocked/rejected settlement recovery contract over HTTP.
import json
import re
import urllib.request
import urllib.error

BASE = "http://127.0.0.1:8007"
OUT = "smoke_logs"

results = []            # checks[] accumulator
touched = []            # (label, payload) for the B11 scan


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


def get(path):
    with urllib.request.urlopen(BASE + path, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def check(cid, ok, evidence):
    results.append({"check": cid, "result": "PASS" if ok else "FAIL", "evidence": evidence})


def info(cid, evidence):
    results.append({"check": cid, "result": "INFO", "evidence": evidence})


def dlg(resp):
    return resp.get("diplomatic_dialogue") or {}


def respond(choice, action_params=None):
    body = {"choice": choice}
    if action_params is not None:
        body["action_params"] = action_params
    return post("/respond_to_diplomatic_dialogue", body)


def option_ids(d):
    ids = []
    for o in d.get("options", []):
        if isinstance(o, dict):
            ids.append(o.get("id") or o.get("action") or o.get("choice"))
        else:
            ids.append(o)
    return ids


def terms_signature(d):
    """Canonical signature of the settlement_terms list for identity comparison."""
    return json.dumps(d.get("settlement_terms"), sort_keys=True, ensure_ascii=False)


# ---------------------------------------------------------------- B1: new_game
st, ng = post("/new_game", {})
save("g4_legB_new_game.json", ng)
touched.append(("new_game", ng))
wars = (ng.get("active_wars") or {}).get("wars", [])
war = wars[0] if wars else {}
war_id = war.get("war_instance_id")
b1_ok = (
    st == 200 and len(wars) == 1 and war_id == "war_1"
    and war.get("opponents") == ["Britain", "Prussia"]
    and war.get("settlement_available") is True
)
check("B1 boot+new_game shared war", b1_ok, json.dumps({
    "http": st, "war_count": len(wars), "war_instance_id": war_id,
    "opponents": war.get("opponents"), "opponent_display": war.get("opponent_display"),
    "settlement_available": war.get("settlement_available"),
    "settlement_disabled_reason": war.get("settlement_disabled_reason"),
    "war_detail_actionability.actionable": (war.get("war_detail_actionability") or {}).get("actionable"),
    "accepting_leader": (war.get("settlement_eligibility") or {}).get("accepting_leader"),
}, ensure_ascii=False))

diplo_before = get("/debug/diplomatic_status")
save("g4_legB_diplo_before.json", diplo_before)

# ---------------------------------------------------------------- B2: mount PROPOSE
st, mount = post("/command", {
    "command": "propose common peace with Britain",
    "action": "propose_common_peace",
    "target_nation": "Britain",
    "war_id": war_id,
})
save("g4_legB_mount.json", mount)
touched.append(("mount", mount))
md = dlg(mount)
rows = md.get("per_court_acceptance", [])
row_summary = [
    {"court": r.get("court") or r.get("nation"),
     "score": r.get("score") or r.get("acceptance") or r.get("direct_score"),
     "band": r.get("band"), "carries": r.get("carries")}
    for r in rows
]
baseline_sig = terms_signature(md)
b2_ok = (
    st == 200 and md.get("dialogue_type") == "settlement_confirm"
    and md.get("dialogue_mode") == "PROPOSE" and len(rows) >= 2
)
check("B2 mount PROPOSE with rejecting courts", b2_ok, json.dumps({
    "http": st, "dialogue_type": md.get("dialogue_type"),
    "dialogue_mode": md.get("dialogue_mode"),
    "covered_enemy_participants": md.get("covered_enemy_participants"),
    "rows": row_summary,
    "overall_acceptance": md.get("overall_acceptance"),
    "treasury_line": md.get("treasury_line"),
    "n_terms": len(md.get("settlement_terms") or []),
}, ensure_ascii=False))

# ---------------------------------------------------------------- B3: submit -> blocked REVIEW
st, review = respond("submit_settlement_for_review",
                     {"action": "submit_settlement_for_review"})
save("g4_legB_blocked_review.json", review)
touched.append(("blocked_review", review))
rd = dlg(review)
r_opts = option_ids(rd)
r_avail = rd.get("available_action_ids", [])
oa = rd.get("overall_acceptance") or {}
carry = oa.get("carry_verdict_display") or ""
opt_labels = json.dumps(rd.get("options", []), ensure_ascii=False)
has_confirm = ("confirm_settlement" in r_opts) or ("confirm_settlement" in r_avail)
disabled_ratify = [o for o in rd.get("options", []) if isinstance(o, dict)
                   and o.get("enabled") is False
                   and re.search(r"ratif", json.dumps(o), re.I)]
review_sig = terms_signature(rd)
b3_ok = (
    st == 200 and rd.get("dialogue_mode") == "REVIEW"
    and not has_confirm and not disabled_ratify
    and ("not carry" in carry.lower() or "holding out" in carry.lower())
)
check("B3 blocked REVIEW: no confirm_settlement, carry verdict names holdouts", b3_ok, json.dumps({
    "http": st, "dialogue_mode": rd.get("dialogue_mode"),
    "option_ids": r_opts, "available_action_ids": r_avail,
    "confirm_settlement_present": has_confirm,
    "disabled_ratify_options": disabled_ratify,
    "carry_verdict_display": carry,
    "overall_acceptance": oa,
}, ensure_ascii=False))

# ---------------------------------------------------------------- B4: rows frozen in REVIEW
frozen_violations = []
for r in rd.get("per_court_acceptance", []):
    court = r.get("court") or r.get("nation")
    for key in ("dial_actions", "holdout_actions", "demand_suggestions",
                "current_demands", "add_demand", "authoring", "can_author"):
        v = r.get(key)
        if v:  # present and truthy
            frozen_violations.append({"court": court, "key": key, "value": v})
review_row_keys = sorted({k for r in rd.get("per_court_acceptance", []) for k in r.keys()})
check("B4 REVIEW rows frozen (no dial/holdout/demand authoring)", not frozen_violations,
      json.dumps({"violations": frozen_violations, "row_keys_union": review_row_keys},
                 ensure_ascii=False))

# ---------------------------------------------------------------- B5: recovery affordances
FORBIDDEN_IDS = {"propose_armistice", "propose_peace", "wait_for_enemy_offer", "ask_for_terms"}
forbidden_hits = [i for i in r_opts + r_avail if i in FORBIDDEN_IDS]
forbidden_copy = []
for o in rd.get("options", []):
    txt = json.dumps(o, ensure_ascii=False).lower()
    for phrase in ("wait for enemy offer", "ask for terms", "enemy offer"):
        if phrase in txt:
            forbidden_copy.append({"option": o, "phrase": phrase})
disabled_revise = [o for o in rd.get("options", []) if isinstance(o, dict)
                   and o.get("enabled") is False
                   and re.search(r"revise", json.dumps(o), re.I)]
has_return = "revise_settlement_terms" in r_opts or "revise_settlement_terms" in r_avail
has_backout = any(i in ("suspend_settlement_editor", "back_out_settlement")
                  for i in r_opts + r_avail)
war_detail_opts = [o for o in rd.get("options", []) if isinstance(o, dict)
                   and re.search(r"war detail", json.dumps(o), re.I)]
pair_arms = [i for i in r_opts + r_avail
             if i in ("seek_bilateral_peace", "seek_armistice_instead")]
b5_ok = has_return and has_backout and not forbidden_hits and not forbidden_copy and not disabled_revise
check("B5 recovery affordances on blocked REVIEW", b5_ok, json.dumps({
    "options_verbatim": rd.get("options", []),
    "available_action_ids": r_avail,
    "has_return_to_terms": has_return, "has_back_out": has_backout,
    "pair_substitute_arms": pair_arms,
    "war_detail_options": war_detail_opts,
    "war_payload_actionable": (war.get("war_detail_actionability") or {}).get("actionable"),
    "forbidden_id_hits": forbidden_hits, "forbidden_copy_hits": forbidden_copy,
    "disabled_revise_placeholders": disabled_revise,
}, ensure_ascii=False))

# ---------------------------------------------------------------- B6: pair-substitute chooser
if pair_arms:
    arm = pair_arms[0]
    st, chooser = respond(arm, {"action": arm})
    save("g4_legB_chooser.json", chooser)
    touched.append(("chooser", chooser))
    cd = dlg(chooser)
    chooser_ok = (st == 200
                  and cd.get("dialogue_type") == "settlement_pair_substitute_confirm")
    c_opts = option_ids(cd)
    st2, kept = respond("keep_joint_settlement", {"action": "keep_joint_settlement"})
    save("g4_legB_keep_joint.json", kept)
    touched.append(("keep_joint", kept))
    kd = dlg(kept)
    restored_ok = (st2 == 200 and kd.get("dialogue_mode") == "REVIEW"
                   and terms_signature(kd) == review_sig)
    check("B6 pair-substitute chooser + keep_joint restores REVIEW", chooser_ok and restored_ok,
          json.dumps({
              "arm_clicked": arm, "chooser_http": st,
              "chooser_dialogue_type": cd.get("dialogue_type"),
              "chooser_message": cd.get("message") or cd.get("text") or cd.get("prompt"),
              "chooser_options": cd.get("options", []),
              "keep_http": st2, "restored_mode": kd.get("dialogue_mode"),
              "terms_identical_to_review": terms_signature(kd) == review_sig,
          }, ensure_ascii=False))
    rd = kd  # continue from the restored review
else:
    info("B6 pair-substitute arms", json.dumps({
        "note": "no pair-substitute arm present on blocked REVIEW options",
        "option_ids": r_opts, "available_action_ids": r_avail}, ensure_ascii=False))

# ---------------------------------------------------------------- B7: confirm anyway -> refusal
st, refusal = respond("confirm_settlement", {"action": "confirm_settlement"})
save("g4_legB_confirm_refusal.json", refusal)
touched.append(("confirm_refusal", refusal))
fd = dlg(refusal)
err = refusal.get("error_display") or fd.get("error_display") or ""
status_after = get("/status")
save("g4_legB_status_after_confirm.json", status_after)
diplo_after = get("/debug/diplomatic_status")
save("g4_legB_diplo_after.json", diplo_after)
wars_after = (status_after.get("active_wars") or {}).get("wars", [])
war_still_active = any(w.get("war_instance_id") == war_id for w in wars_after)
diplo_unchanged = json.dumps(diplo_before, sort_keys=True) == json.dumps(diplo_after, sort_keys=True)
b7_ok = (st == 200 and bool(err) and bool(fd)
         and war_still_active and diplo_unchanged)
check("B7 confirm_settlement refused: error_display + dialogue + no mutation", b7_ok, json.dumps({
    "http": st, "error_display": err,
    "dialogue_reattached": bool(fd), "dialogue_mode": fd.get("dialogue_mode"),
    "war_still_active": war_still_active,
    "diplomatic_states_unchanged": diplo_unchanged,
}, ensure_ascii=False))

# ---------------------------------------------------------------- B8: hard_stops rendering
hs = fd.get("hard_stops") or rd.get("hard_stops") or []
hs_bad = []
for h in hs:
    if not isinstance(h, dict):
        hs_bad.append({"entry": h, "why": "not a dict"})
        continue
    cd_ = h.get("code_display")
    det = h.get("detail") or h.get("detail_display")
    if not cd_ or not det:
        hs_bad.append({"entry": h, "why": "missing code_display or detail"})
    elif re.fullmatch(r"[a-z0-9_]+", str(cd_)):
        hs_bad.append({"entry": h, "why": "code_display looks like raw enum"})
if hs:
    check("B8 hard_stops render code_display + humanized detail", not hs_bad,
          json.dumps({"hard_stops": hs, "problems": hs_bad}, ensure_ascii=False))
else:
    info("B8 hard_stops", json.dumps({
        "note": "no hard_stops[] entries on blocked REVIEW payloads",
        "review_hard_stops": rd.get("hard_stops"),
        "refusal_hard_stops": fd.get("hard_stops")}, ensure_ascii=False))

# ---------------------------------------------------------------- B9: revise -> PROPOSE, same terms
st, revised = respond("revise_settlement_terms", {"action": "revise_settlement_terms"})
save("g4_legB_revise_propose.json", revised)
touched.append(("revise_propose", revised))
vd = dlg(revised)
b9_ok = (st == 200 and vd.get("dialogue_mode") == "PROPOSE"
         and terms_signature(vd) == review_sig)
check("B9 revise_settlement_terms -> PROPOSE, package identity preserved", b9_ok, json.dumps({
    "http": st, "dialogue_mode": vd.get("dialogue_mode"),
    "terms_match_review": terms_signature(vd) == review_sig,
    "n_terms": len(vd.get("settlement_terms") or []),
    "settlement_terms": vd.get("settlement_terms"),
}, ensure_ascii=False))

# ---------------------------------------------------------------- B10: suspend/restore + discard
# distinguish the draft first: dial harsher on the whole table
st, dialed = respond("settlement_dial_harsher",
                     {"action": "settlement_dial_harsher", "scope": "table"})
save("g4_legB_dial_modified.json", dialed)
touched.append(("dial_modified", dialed))
dd = dlg(dialed)
modified_sig = terms_signature(dd)
dial_changed = modified_sig != baseline_sig
st, susp = respond("suspend_settlement_editor", {"action": "suspend_settlement_editor"})
save("g4_legB_suspend.json", susp)
touched.append(("suspend", susp))
st2, remount1 = post("/command", {
    "command": "propose common peace with Britain",
    "action": "propose_common_peace",
    "target_nation": "Britain",
    "war_id": war_id,
})
save("g4_legB_remount_restored.json", remount1)
touched.append(("remount_restored", remount1))
r1d = dlg(remount1)
restored = terms_signature(r1d) == modified_sig
st3, backed = respond("back_out_settlement", {"action": "back_out_settlement"})
save("g4_legB_backout.json", backed)
touched.append(("backout", backed))
st4, remount2 = post("/command", {
    "command": "propose common peace with Britain",
    "action": "propose_common_peace",
    "target_nation": "Britain",
    "war_id": war_id,
})
save("g4_legB_remount_fresh.json", remount2)
touched.append(("remount_fresh", remount2))
r2d = dlg(remount2)
fresh = terms_signature(r2d) == baseline_sig
discarded = terms_signature(r2d) != modified_sig
b10_ok = dial_changed and restored and fresh and discarded
check("B10 suspend restores scoped draft (PF-2); back_out discards to fresh baseline", b10_ok,
      json.dumps({
          "dial_http": st, "dial_changed_terms": dial_changed,
          "suspend_http": st, "remount1_http": st2,
          "remount1_mode": r1d.get("dialogue_mode"), "draft_restored": restored,
          "backout_http": st3, "remount2_http": st4,
          "remount2_mode": r2d.get("dialogue_mode"),
          "fresh_equals_baseline": fresh, "modified_discarded": discarded,
          "baseline_terms": (dlg(mount)).get("settlement_terms"),
          "modified_terms": dd.get("settlement_terms"),
          "remount2_terms": r2d.get("settlement_terms"),
      }, ensure_ascii=False))
# leave clean: suspend the final mount so no hard-stop lingers (server dies anyway)
respond("suspend_settlement_editor", {"action": "suspend_settlement_editor"})

# ---------------------------------------------------------------- B11: payload hygiene scan
float_hits, display_raw_hits, conference_hits, rawid_hits = [], [], [], []
SNAKE = re.compile(r"\b[a-z][a-z0-9]*(?:_[a-z0-9]+)+\b")
CAMEL_NATION = re.compile(r"\b(KingdomOfItaly|PapalStates)\b")


def walk(label, node, path):
    if isinstance(node, dict):
        for k, v in node.items():
            walk(label, v, f"{path}.{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            walk(label, v, f"{path}[{i}]")
    elif isinstance(node, float) and not isinstance(node, bool):
        if node != int(node) or True:  # record ALL floats (json 0.0 reaches Godot as float)
            float_hits.append({"payload": label, "path": path, "value": node})
    elif isinstance(node, str):
        low = node.lower()
        keyname = path.rsplit(".", 1)[-1]
        is_displayish = (keyname.endswith("_display") or keyname in
                         ("message", "text", "label", "prompt", "detail",
                          "description", "header", "title", "treasury_line"))
        if is_displayish:
            snakes = [m for m in SNAKE.findall(node)
                      if m not in ("_", ) and len(m) > 3]
            if snakes or CAMEL_NATION.search(node):
                display_raw_hits.append({"payload": label, "path": path,
                                         "value": node, "tokens": snakes})
            if re.search(r"\bwar_\d+\b", node):
                rawid_hits.append({"payload": label, "path": path, "value": node})
        if "conference" in low or re.search(r"\bveto\b", low):
            conference_hits.append({"payload": label, "path": path, "value": node})


for label, payload in touched:
    walk(label, payload, label)

# dedupe float paths (strip indices + payload) to keep the report readable
float_fields = {}
for h in float_hits:
    generic = re.sub(r"\[\d+\]", "[]", h["path"].split(".", 1)[-1] if "." in h["path"] else h["path"])
    float_fields.setdefault(generic, {"example": h, "count": 0})
    float_fields[generic]["count"] += 1
scan_report = {
    "float_fields": {k: {"count": v["count"], "example_path": v["example"]["path"],
                         "example_value": v["example"]["value"]}
                     for k, v in float_fields.items()},
    "display_raw_key_hits": display_raw_hits,
    "conference_or_veto_hits": conference_hits,
    "raw_war_id_in_display_hits": rawid_hits,
}
save("g4_legB_scan_report.json", scan_report)
check("B11 payload hygiene scan (floats/raw display keys/conference-veto/raw ids)",
      not display_raw_hits and not conference_hits and not rawid_hits and not float_fields,
      json.dumps(scan_report, ensure_ascii=False)[:6000])

save("g4_legB_results.json", results)
print(json.dumps(results, indent=2, ensure_ascii=False))
