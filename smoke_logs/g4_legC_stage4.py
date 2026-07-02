# Leg C stage 4: PF-2 draft restore on remount, focused-Harsher D5 guard line,
# blocked review at reject band, C3 re_author_with_concessions BEFORE/AFTER.
import json
import urllib.request

BASE = "http://127.0.0.1:8008"
LOGDIR = "smoke_logs"


def post(path, payload):
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def save(name, data):
    with open(f"{LOGDIR}/{name}", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"[saved] {LOGDIR}/{name}")


def act(choice, params=None):
    p = {"action": choice}
    if params:
        p.update(params)
    return post("/respond_to_diplomatic_dialogue", {"choice": choice, "action_params": p})


def summary(tag, resp):
    dlg = resp.get("diplomatic_dialogue")
    print(f"--- {tag} ---")
    print(f"  error_display={json.dumps(resp.get('error_display'), ensure_ascii=True)}")
    if not dlg:
        print(f"  NO dialogue; message={json.dumps(resp.get('message'), ensure_ascii=True)[:400]}")
        return None
    print(f"  dtype={dlg.get('dialogue_type')} mode={dlg.get('dialogue_mode')} can_ratify={dlg.get('can_ratify')}")
    for row in dlg.get("per_court_acceptance", []):
        print(f"  court={row.get('nation')} total={row.get('total')}/{row.get('threshold')} band={row.get('band')} direction={row.get('direction')} dir_summary={json.dumps(row.get('direction_summary'), ensure_ascii=True)} delta={json.dumps(row.get('delta_display'), ensure_ascii=True)} suggestions={len(row.get('demand_suggestions') or [])}")
    print(f"  actions={dlg.get('available_action_ids')}")
    print(f"  terms={json.dumps(dlg.get('settlement_terms'), ensure_ascii=True)}")
    print(f"  treasury_line={json.dumps(dlg.get('treasury_line'), ensure_ascii=True)}")
    print(f"  authoring_voice_beats={json.dumps(dlg.get('authoring_voice_beats'), ensure_ascii=True)}")
    print(f"  propose_carry_hint={json.dumps(dlg.get('propose_carry_hint'), ensure_ascii=True)}")
    print(f"  budget_bound_recommendation={json.dumps(dlg.get('budget_bound_recommendation'), ensure_ascii=True)[:500]}")
    return dlg


# 1. remount -> PF-2: must restore the KEPT draft (gold 500/500, NO Waterloo, 10/10), not baseline
r = post("/command", {
    "command": "propose common peace with Britain",
    "action": "propose_common_peace",
    "target_nation": "Britain",
    "war_id": "war_1",
})
save("g4_legC_19_remount_kept_draft.json", r)
dlg = summary("PF2-remount", r)

# 2. focused Harsher on Britain (concede-direction court) -> D5 trigger -> DC-4 guard line
r = act("settlement_dial_harsher", {"scope": "Britain", "nation": "Britain", "war_id": "war_1"})
save("g4_legC_20_focused_harsher_britain.json", r)
dlg = summary("D5-focused-harsher", r)

# 3. one demand_suggestion add if present (second D5 trigger: explicit demand-group add)
if dlg:
    for row in dlg.get("per_court_acceptance", []):
        sugg = row.get("demand_suggestions") or []
        if sugg:
            s = sugg[0]
            print("  using suggestion:", json.dumps(s, ensure_ascii=True)[:700])
            ap = dict(s.get("action_params") or {})
            ap.setdefault("action", s.get("action", "settlement_demand_add"))
            if "war_id" not in ap and s.get("war_id"):
                ap["war_id"] = s["war_id"]
            r = post("/respond_to_diplomatic_dialogue", {"choice": ap.get("action", "settlement_demand_add"), "action_params": ap})
            save("g4_legC_21_demand_add_suggestion.json", r)
            dlg = summary("D5-demand-add", r)
            break

# 4. submit -> blocked REVIEW at reject band (Re-author with Concessions expected)
r = act("submit_settlement_for_review")
save("g4_legC_22_submit_review_3.json", r)
dlg = summary("submit3-blocked", r)
before_scores = {}
if dlg:
    for row in dlg.get("per_court_acceptance", []):
        before_scores[row.get("nation")] = row.get("total")
print("C3 BEFORE scores:", before_scores)

# 5. C3: re_author_with_concessions -> expect re-staged guided PROPOSE seeded from concession baseline
r = act("re_author_with_concessions", {"war_id": "war_1"})
save("g4_legC_23_reauthor_concessions.json", r)
dlg = summary("C3-reauthor", r)
if dlg:
    after_scores = {row.get("nation"): row.get("total") for row in dlg.get("per_court_acceptance", [])}
    print("C3 AFTER scores:", after_scores, "(before:", before_scores, ")")
    for row in dlg.get("per_court_acceptance", []):
        for cd in row.get("current_demands") or []:
            print(f"  {row.get('nation')} clause: idx={cd.get('clause_index')} type={cd.get('clause_type')} tag={cd.get('direction_tag')} line={json.dumps(cd.get('line_display'), ensure_ascii=True)} authored_by={json.dumps(cd.get('authored_by'))}")
    print("  talleyrand_text:", json.dumps(dlg.get("talleyrand_text"), ensure_ascii=True)[:600])
    print("  message:", json.dumps(dlg.get("message"), ensure_ascii=True)[:600])
