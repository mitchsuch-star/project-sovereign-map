"""Leg E — pair-substitute step 2: replace draft -> PROPOSE table -> seek_armistice_instead."""
import sys, json
sys.path.insert(0, "smoke_logs")
from g4_legE_lib import get, post, save

st, r = post("/respond_to_diplomatic_dialogue",
             {"choice": "replace_current_scope_draft",
              "action_params": {"action": "replace_current_scope_draft"}})
print("replace:", st, r.get("success"))
save("g4_legE_pairsub_replace.json", r)
dd = r.get("diplomatic_dialogue")
if not dd:
    print("no dialogue:", json.dumps(r.get("message"), ensure_ascii=False)[:400])
    sys.exit(1)
print("type:", dd.get("type"), "| mode:", dd.get("dialogue_mode"))
print("available_action_ids:", dd.get("available_action_ids"))
print("options:", [o.get("action") for o in (dd.get("options") or [])])
rows = dd.get("per_court_acceptance") or []
print("per_court rows:", [(row.get("nation"), row.get("score"), row.get("band")) for row in rows])
print("treasury_line:", json.dumps(dd.get("treasury_line"), ensure_ascii=False)[:300])
print("overall_acceptance:", dd.get("overall_acceptance"))

st, r2 = post("/respond_to_diplomatic_dialogue",
              {"choice": "seek_armistice_instead",
               "action_params": {"action": "seek_armistice_instead", "nation": "Britain"}})
print("\nseek_armistice_instead:", st, r2.get("success"))
save("g4_legE_pairsub_seek_armistice2.json", r2)
print("message:", json.dumps(r2.get("message"), ensure_ascii=False)[:500])
print("error_display:", r2.get("error_display"))
dd2 = r2.get("diplomatic_dialogue")
if dd2:
    print("new dialogue type:", dd2.get("type"))
    print("options:", [o.get("action") for o in (dd2.get("options") or [])])
    for k in ("pair_nation", "target_nation", "substitute_kind", "carryover_summary"):
        v = dd2.get(k)
        if v is not None:
            print(k, ":", json.dumps(v, ensure_ascii=False)[:400])
