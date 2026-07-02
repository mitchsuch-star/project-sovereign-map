# Leg C stage 3: reset -> remount -> C5 dials in PROPOSE -> D5 harsher guard line
# -> CH-5 probe -> blocked REVIEW -> armistice pair-substitute arm -> keep joint -> suspend.
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
        print(f"  top keys: {sorted(resp.keys())}")
        return None
    print(f"  dtype={dlg.get('dialogue_type')} mode={dlg.get('dialogue_mode')} can_ratify={dlg.get('can_ratify')}")
    for row in dlg.get("per_court_acceptance", []):
        print(f"  court={row.get('nation')} total={row.get('total')}/{row.get('threshold')} band={row.get('band')} delta={json.dumps(row.get('delta_display'), ensure_ascii=True)}")
    print(f"  overall={json.dumps((dlg.get('overall_acceptance') or {}).get('carry_verdict_display'), ensure_ascii=True)}")
    print(f"  actions={dlg.get('available_action_ids')}")
    print(f"  option labels={[o.get('label') for o in dlg.get('options', [])]}")
    print(f"  terms={json.dumps(dlg.get('settlement_terms'), ensure_ascii=True)}")
    print(f"  treasury_line={json.dumps(dlg.get('treasury_line'), ensure_ascii=True)}")
    beats = dlg.get("authoring_voice_beats")
    print(f"  authoring_voice_beats={json.dumps(beats, ensure_ascii=True)}")
    return dlg


# 1. discard current carrying REVIEW
r = act("back_out_settlement")
save("g4_legC_07_backout_discard.json", r)
summary("backout", r)

# 2. remount fresh
r = post("/command", {
    "command": "propose common peace with Britain",
    "action": "propose_common_peace",
    "target_nation": "Britain",
    "war_id": "war_1",
})
save("g4_legC_08_remount_first_paint.json", r)
dlg = summary("remount", r)

# 3. C5 dial generous (table) x2 in PROPOSE
r = act("settlement_dial_generous", {"scope": "table", "war_id": "war_1"})
save("g4_legC_09_dial_generous_propose_1.json", r)
summary("C5-propose-dial1", r)

r = act("settlement_dial_generous", {"scope": "table", "war_id": "war_1"})
save("g4_legC_10_dial_generous_propose_2.json", r)
summary("C5-propose-dial2", r)

# 4. D5 trigger: harsher (table) on concede-direction courts -> DC-4 guard line expected
r = act("settlement_dial_harsher", {"scope": "table", "war_id": "war_1"})
save("g4_legC_11_dial_harsher_1.json", r)
summary("D5-harsher1", r)

r = act("settlement_dial_harsher", {"scope": "table", "war_id": "war_1"})
save("g4_legC_12_dial_harsher_2.json", r)
summary("D5-harsher2", r)

# 5. CH-5 probe: action not in available_action_ids
r = act("re_author_with_concessions", {"war_id": "war_1"})
save("g4_legC_13_probe_reauthor.json", r)
summary("CH5-probe-reauthor", r)

# 6. submit for review (should be blocked if scores back at 45)
r = act("submit_settlement_for_review")
save("g4_legC_14_submit_review_2.json", r)
dlg = summary("submit2", r)

# 7. armistice pair-substitute arm
r = act("seek_armistice_instead", {"scope": "selected_pair", "war_id": "war_1", "selected_target_nation": "Britain"})
save("g4_legC_15_seek_armistice.json", r)
dlg = summary("seek-armistice", r)
if dlg:
    print("  pair-sub full options:", json.dumps(dlg.get("options"), ensure_ascii=True)[:1200])
    print("  pair-sub message:", json.dumps(dlg.get("message") or dlg.get("talleyrand_text"), ensure_ascii=True)[:600])

# 8. keep joint settlement
r = act("keep_joint_settlement")
save("g4_legC_16_keep_joint.json", r)
summary("keep-joint", r)

# 9. return to terms, then non-destructive suspend
r = act("return_to_settlement_terms")
save("g4_legC_17_return_to_terms.json", r)
summary("return-to-terms", r)

r = act("suspend_settlement_editor")
save("g4_legC_18_suspend.json", r)
summary("suspend", r)
wars = (r.get("active_wars") or {}).get("wars", [])
for w in wars:
    print("  post-suspend war:", w.get("war_instance_id"), "settlement_draft_kept=", w.get("settlement_draft_kept"))
