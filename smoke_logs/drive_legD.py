# Gate 4 manual smoke - LEG D: settlement_multiwar_ambiguity preset (port 8011)
# READ-ONLY driver: POSTs/GETs against the smoke server, saves raw payloads
# to smoke_logs/g4_legD_*.json. No codebase writes.
import json
import os
import urllib.request
import urllib.parse
import urllib.error

BASE = "http://127.0.0.1:8011"
OUT = os.path.dirname(os.path.abspath(__file__))

captured = {}


def save(name, obj):
    path = os.path.join(OUT, f"g4_legD_{name}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
    captured[name] = obj
    print(f"  [saved] g4_legD_{name}.json")
    return path


def _do(req):
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            raw = r.read().decode("utf-8")
            code = r.status
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        code = e.code
    try:
        return code, json.loads(raw)
    except Exception:
        return code, {"_raw_text": raw, "_status": code}


def post(path, body):
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        BASE + path, data=data,
        headers={"Content-Type": "application/json"}, method="POST")
    return _do(req)


def get(path, **params):
    url = BASE + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    return _do(urllib.request.Request(url, method="GET"))


def dlg(resp):
    return resp.get("diplomatic_dialogue") if isinstance(resp, dict) else None


def summarize_dialogue(d):
    if not isinstance(d, dict):
        return None
    return {
        "type": d.get("type"),
        "dialogue_mode": d.get("dialogue_mode"),
        "war_id": d.get("war_id"),
        "selected_target_nation": d.get("selected_target_nation"),
        "covered_enemy_participants": d.get("covered_enemy_participants"),
        "settlement_terms": d.get("settlement_terms"),
        "overall_acceptance": d.get("overall_acceptance"),
        "n_per_court_rows": len(d.get("per_court_acceptance") or []),
        "per_court_nations": [
            r.get("nation") for r in (d.get("per_court_acceptance") or [])
        ],
        "available_action_ids": d.get("available_action_ids"),
        "treasury_line": d.get("treasury_line"),
    }


def mount(target, war_id=None, tag=""):
    body = {
        "command": f"propose common peace with {target}",
        "action": "propose_common_peace",
        "target_nation": target,
    }
    if war_id is not None:
        body["war_id"] = war_id
    sc, resp = post("/command", body)
    save(f"mount_{tag or target}", resp)
    d = dlg(resp)
    print(f"  mount target={target} war_id={war_id!r} http={sc} "
          f"success={resp.get('success')} dialogue={'YES' if d else 'no'}")
    if not d:
        print(f"    message={resp.get('message')!r}")
        print(f"    error={resp.get('error')!r} error_display={resp.get('error_display')!r}")
    else:
        print(f"    staged: {json.dumps(summarize_dialogue(d))[:400]}")
    return sc, resp


def respond(choice, action_params=None, tag=""):
    body = {"choice": choice}
    if action_params is not None:
        body["action_params"] = action_params
    sc, resp = post("/respond_to_diplomatic_dialogue", body)
    if tag:
        save(tag, resp)
    d = dlg(resp)
    print(f"  respond choice={choice} http={sc} success={resp.get('success')} "
          f"dialogue={'YES' if d else 'no'} error_display={resp.get('error_display')!r}")
    return sc, resp


print("=== D1: boot + /new_game + war inventory ===")
sc, ng = post("/new_game", {})
save("new_game", ng)
print(f"  /new_game http={sc} success={ng.get('success')}")

sc, status = get("/status")
save("status", status)
wars = (((status.get("active_wars") or {}).get("wars")) or [])
war_rows = []
for w in wars:
    row = {
        "war_instance_id": w.get("war_instance_id"),
        "opponent": w.get("opponent"),
        "settlement_available": w.get("settlement_available"),
        "settlement_disabled_reason": w.get("settlement_disabled_reason"),
        "eligibility_error": (w.get("settlement_eligibility") or {}).get("error"),
        "eligibility_available_wars": (w.get("settlement_eligibility") or {}).get("available_wars"),
    }
    war_rows.append(row)
    print(f"  war row: {json.dumps(row)}")
save("d1_war_rows", war_rows)

sc, ws = get("/debug/war_scores")
save("war_scores", ws)
print(f"  /debug/war_scores: {json.dumps(ws)[:500]}")

sc, ds = get("/debug/diplomatic_status")
save("diplomatic_status", ds)

opponents = [w.get("opponent") for w in wars]
print(f"  opponents at war: {opponents}")

print("=== D2: mount with NO war_id per opponent (ambiguity contract) ===")
d2_results = {}
for opp in opponents:
    sc, resp = mount(opp, war_id=None, tag=f"d2_nowar_{opp}")
    d2_results[opp] = {
        "http": sc,
        "success": resp.get("success"),
        "message": resp.get("message"),
        "error": resp.get("error"),
        "error_display": resp.get("error_display"),
        "dialogue_attached": bool(dlg(resp)),
        "dialogue_war_id": (dlg(resp) or {}).get("war_id"),
    }
    # if a dialogue mounted unexpectedly, back out non-destructively
    if dlg(resp):
        respond("suspend_settlement_editor", tag=f"d2_suspend_{opp}")
save("d2_summary", d2_results)

print("=== D3: mount with EXPLICIT war_id per HUD row ===")
d3_results = {}
for w in wars:
    opp = w.get("opponent")
    wid = w.get("war_instance_id")
    sc, resp = mount(opp, war_id=wid, tag=f"d3_explicit_{wid}_{opp}")
    d = dlg(resp)
    d3_results[f"{wid}:{opp}"] = {
        "http": sc,
        "success": resp.get("success"),
        "message": resp.get("message"),
        "error": resp.get("error"),
        "error_display": resp.get("error_display"),
        "dialogue": summarize_dialogue(d),
    }
    if d:
        respond("suspend_settlement_editor", tag=f"d3_suspend_{wid}_{opp}")
save("d3_summary", d3_results)

print("=== D4: wizard surfaces ===")
sc, nl = get("/diplomatic_preview")
save("d4_nation_list", nl)
print(f"  nation-list mode keys: {list(nl.keys())[:20]}")
for opp in opponents:
    sc, pv = get("/diplomatic_preview", nation=opp)
    save(f"d4_preview_{opp}", pv)
    actions = pv.get("actions") or []
    st = next((a for a in actions if a.get("action") in ("open_settlement", "propose_common_peace")), None)
    print(f"  preview {opp}: settlement action = {json.dumps(st) if st else 'ABSENT'}")

print("=== done phase 1 ===")
print(json.dumps({"d2": d2_results, "d3": {k: {kk: vv for kk, vv in v.items() if kk != 'dialogue'} for k, v in d3_results.items()}}, indent=1)[:3000])
