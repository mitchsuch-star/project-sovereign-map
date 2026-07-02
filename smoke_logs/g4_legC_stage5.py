# Leg C stage 5: apply concession baseline replacement (C3 AFTER),
# then DC-4 guard-line probe via a demand-group add on a concede-direction court.
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
        print(f"  court={row.get('nation')} total={row.get('total')}/{row.get('threshold')} band={row.get('band')} direction={row.get('direction')} dir_summary={json.dumps(row.get('direction_summary'), ensure_ascii=True)} delta={json.dumps(row.get('delta_display'), ensure_ascii=True)}")
    print(f"  actions={dlg.get('available_action_ids')}")
    print(f"  terms={json.dumps(dlg.get('settlement_terms'), ensure_ascii=True)}")
    print(f"  authoring_voice_beats={json.dumps(dlg.get('authoring_voice_beats'), ensure_ascii=True)}")
    return dlg


# 1. C3: apply the concession baseline replacement
r = act("apply_concession_baseline_replacement", {"war_id": "war_1"})
save("g4_legC_24_apply_concession_replacement.json", r)
dlg = summary("C3-apply-replacement", r)
if dlg:
    after = {row.get("nation"): row.get("total") for row in dlg.get("per_court_acceptance", [])}
    print("C3 AFTER-apply scores:", after, "(BEFORE was Britain 10, Prussia 10)")
    for row in dlg.get("per_court_acceptance", []):
        for cd in row.get("current_demands") or []:
            print(f"  {row.get('nation')} clause: type={cd.get('clause_type')} tag={cd.get('direction_tag')} line={json.dumps(cd.get('line_display'), ensure_ascii=True)} authored_by={json.dumps(cd.get('authored_by'))}")

# 2. list suggestion groups on the Britain row; add a DEMAND-group one -> DC-4 guard line probe
if dlg:
    brit = next((row for row in dlg.get("per_court_acceptance", []) if row.get("nation") == "Britain"), None)
    if brit:
        for s in brit.get("demand_suggestions") or []:
            print(f"  Britain suggestion: group={s.get('group')} type={s.get('clause_type')} label={json.dumps(s.get('label'), ensure_ascii=True)}")
        demand_s = next((s for s in (brit.get("demand_suggestions") or []) if s.get("group") == "demand"), None)
        if demand_s:
            print("  ADDING demand-group suggestion:", json.dumps(demand_s, ensure_ascii=True)[:600])
            ap = dict(demand_s.get("action_params") or {})
            ap.setdefault("action", demand_s.get("action", "settlement_demand_add"))
            if "war_id" not in ap and demand_s.get("war_id"):
                ap["war_id"] = demand_s["war_id"]
            r = post("/respond_to_diplomatic_dialogue", {"choice": ap.get("action", "settlement_demand_add"), "action_params": ap})
            save("g4_legC_25_demand_group_add_guardline.json", r)
            dlg2 = summary("DC4-guardline-probe", r)
        else:
            print("  NO demand-group suggestion on Britain row (record verbatim groups above)")
