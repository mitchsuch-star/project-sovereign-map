# Leg C stage 1: C1 boot/new_game + C2 mount propose_common_peace, first-paint capture.
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


def get(path):
    with urllib.request.urlopen(BASE + path, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def save(name, data):
    with open(f"{LOGDIR}/{name}", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"[saved] {LOGDIR}/{name}")


# ---------- C1: new game ----------
ng = post("/new_game", {})
save("g4_legC_01_new_game.json", ng)
wars = ng.get("active_wars", {}).get("wars", [])
print(f"C1: wars={len(wars)}")
for w in wars:
    print(json.dumps({
        "war_instance_id": w.get("war_instance_id"),
        "opponent": w.get("opponent"),
        "opponents": w.get("opponents"),
        "opponent_display": w.get("opponent_display"),
        "war_score": w.get("war_score"),
        "breakdown": w.get("breakdown"),
        "settlement_available": w.get("settlement_available"),
        "settlement_disabled_reason": w.get("settlement_disabled_reason"),
        "settlement_tier": w.get("settlement_tier"),
        "settlement_tier_display": w.get("settlement_tier_display"),
        "in_coalition": w.get("in_coalition"),
        "is_coalition_leader": w.get("is_coalition_leader"),
        "peace_seeking_controls": (w.get("war_detail_actionability") or {}).get("peace_seeking_controls"),
    }, indent=2))

war = wars[0]
wid = war["war_instance_id"]

ws = get("/debug/war_scores")
save("g4_legC_01b_war_scores.json", ws)
print("C1 debug war_scores:", json.dumps(ws)[:800])

# ---------- C2: mount settlement table ----------
mount = post("/command", {
    "command": "propose common peace with Britain",
    "action": "propose_common_peace",
    "target_nation": "Britain",
    "war_id": wid,
})
save("g4_legC_02_mount_first_paint.json", mount)
dlg = mount.get("diplomatic_dialogue")
if not dlg:
    print("C2: NO diplomatic_dialogue attached! top keys:", sorted(mount.keys()))
    print("message:", mount.get("message"))
    raise SystemExit(1)

print("C2 dialogue keys:", sorted(dlg.keys()))
FIRST_PAINT_FIELDS = [
    "dialogue_type", "dialogue_mode", "overall_acceptance", "treasury_line",
    "covered_enemy_participants", "concession_baseline_visible",
    "losing_for_concession_baseline", "losing_side_pressure_voice",
    "recurring_gold_preset_visible", "recurring_gold_preset_reason",
    "losing_for_surrender_preset", "available_action_ids", "hard_stops",
    "budget_bound_recommendation", "authoring_voice_beats",
]
for k in FIRST_PAINT_FIELDS:
    if k in dlg:
        print(f"  {k} = {json.dumps(dlg[k], ensure_ascii=False)[:600]}")
    else:
        print(f"  {k} = <ABSENT>")

if "concession_baseline" in dlg:
    print("  concession_baseline =", json.dumps(dlg["concession_baseline"], ensure_ascii=False)[:2000])
else:
    print("  concession_baseline = <ABSENT>")
if "recurring_gold_preset_payload" in dlg:
    print("  recurring_gold_preset_payload =", json.dumps(dlg["recurring_gold_preset_payload"], ensure_ascii=False)[:800])

print("  settlement_terms =", json.dumps(dlg.get("settlement_terms"), ensure_ascii=False)[:1200])
for row in dlg.get("per_court_acceptance", []):
    print("  per_court row:", json.dumps({k: row.get(k) for k in (
        "court", "court_display", "nation", "score", "acceptance_score", "band",
        "band_display", "direction", "direction_display", "carries", "accepts",
        "delta_display")}, ensure_ascii=False))
for o in dlg.get("options", []):
    print("  option:", json.dumps({k: o.get(k) for k in ("id", "choice", "label", "text", "display", "enabled", "disabled_reason_display")}, ensure_ascii=False))

# any surrender-ish affordance anywhere
raw = json.dumps(dlg, ensure_ascii=False)
for kw in ("surrender", "Surrender"):
    idx = 0
    while True:
        i = raw.find(kw, idx)
        if i < 0:
            break
        print(f"  SURRENDER-HIT ...{raw[max(0, i - 120):i + 160]}...")
        idx = i + 1
        break  # one hit per keyword is enough for the log
