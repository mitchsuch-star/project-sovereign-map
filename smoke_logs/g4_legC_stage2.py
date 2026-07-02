# Leg C stage 2: C7 blocked REVIEW first (while both courts reject at 45/50),
# revise back to PROPOSE, then C5 two generous table dials, then CH-5/C3 probe.
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


def dlg_summary(tag, resp):
    dlg = resp.get("diplomatic_dialogue")
    if not dlg:
        print(f"{tag}: NO diplomatic_dialogue; error_display={json.dumps(resp.get('error_display'), ensure_ascii=True)}; message={json.dumps(resp.get('message'), ensure_ascii=True)[:300]}")
        print(f"{tag}: top keys: {sorted(resp.keys())}")
        return None
    print(f"{tag}: mode={dlg.get('dialogue_mode')} can_ratify={dlg.get('can_ratify')}")
    print(f"{tag}: error_display={json.dumps(resp.get('error_display'), ensure_ascii=True)}")
    print(f"{tag}: ratify_blocked_reason={json.dumps(dlg.get('ratify_blocked_reason'), ensure_ascii=True)}")
    oa = dlg.get("overall_acceptance") or {}
    print(f"{tag}: overall={json.dumps(oa, ensure_ascii=True)[:400]}")
    for row in dlg.get("per_court_acceptance", []):
        print(f"{tag}: court={row.get('nation')} total={row.get('total')}/{row.get('threshold')} band={row.get('band')} band_display={json.dumps(row.get('band_display'), ensure_ascii=True)} delta={json.dumps(row.get('delta_display'), ensure_ascii=True)} direction={row.get('direction')}")
    print(f"{tag}: options={[o.get('action') or o.get('label') for o in dlg.get('options', [])]}")
    print(f"{tag}: available_action_ids={dlg.get('available_action_ids')}")
    beats = dlg.get("authoring_voice_beats")
    if beats:
        print(f"{tag}: authoring_voice_beats={json.dumps(beats, ensure_ascii=True)[:800]}")
    print(f"{tag}: terms={json.dumps(dlg.get('settlement_terms'), ensure_ascii=True)}")
    print(f"{tag}: treasury_line={json.dumps(dlg.get('treasury_line'), ensure_ascii=True)}")
    return dlg


# ---- C7: submit for review while still rejecting (both courts 45/50) ----
r = post("/respond_to_diplomatic_dialogue", {
    "choice": "submit_settlement_for_review",
    "action_params": {"action": "submit_settlement_for_review"},
})
save("g4_legC_03_submit_blocked_review.json", r)
dlg = dlg_summary("C7-submit", r)
if dlg:
    print("C7 blocking =", json.dumps(dlg.get("blocking"), ensure_ascii=True)[:800])
    print("C7 hard_stops =", json.dumps(dlg.get("hard_stops"), ensure_ascii=True)[:400])
    print("C7 terminal_recovery_copy =", json.dumps(dlg.get("terminal_recovery_copy"), ensure_ascii=True)[:600])
    print("C7 recovery_route =", json.dumps(dlg.get("recovery_route"), ensure_ascii=True)[:600])
    rv = dlg.get("review_sections")
    if rv:
        print("C7 review_sections keys:", list(rv.keys()) if isinstance(rv, dict) else f"list[{len(rv)}]")
        print("C7 review_sections =", json.dumps(rv, ensure_ascii=True)[:1500])
    # confirm_settlement must be absent; scan raw
    raw = json.dumps(dlg)
    print("C7 contains 'confirm_settlement':", "confirm_settlement" in raw)
    print("C7 contains 'Ratify':", "Ratify" in raw or "ratify" in json.dumps([o.get("label") for o in dlg.get("options", [])]))

# ---- revise back to PROPOSE ----
r = post("/respond_to_diplomatic_dialogue", {
    "choice": "revise_settlement_terms",
    "action_params": {"action": "revise_settlement_terms"},
})
save("g4_legC_04_revise_back.json", r)
dlg_summary("revise", r)

# ---- C5: generous dial #1 (table) ----
r = post("/respond_to_diplomatic_dialogue", {
    "choice": "settlement_dial_generous",
    "action_params": {"action": "settlement_dial_generous", "scope": "table", "war_id": "war_1"},
})
save("g4_legC_05_dial_generous_1.json", r)
dlg_summary("C5-dial1", r)

# ---- C5: generous dial #2 (table) ----
r = post("/respond_to_diplomatic_dialogue", {
    "choice": "settlement_dial_generous",
    "action_params": {"action": "settlement_dial_generous", "scope": "table", "war_id": "war_1"},
})
save("g4_legC_06_dial_generous_2.json", r)
dlg_summary("C5-dial2", r)
