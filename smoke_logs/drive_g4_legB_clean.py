# Gate 4 LEG B — clean minimal B10 repro on a fresh game:
# new_game -> mount(baseline) -> dial harsher -> submit REVIEW -> back_out (discard)
# -> remount -> EXPECT fresh baseline. Also probes /mailbox for stacked dialogues.
import json
import urllib.request
import urllib.error

BASE = "http://127.0.0.1:8007"
results = []


def save(name, obj):
    with open(f"smoke_logs/{name}", "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


def post(path, body):
    req = urllib.request.Request(
        BASE + path, data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        txt = e.read().decode("utf-8", errors="replace")
        try:
            return e.code, json.loads(txt)
        except Exception:
            return e.code, {"_raw_error_body": txt}


def get(path):
    with urllib.request.urlopen(BASE + path, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def respond(choice, params):
    return post("/respond_to_diplomatic_dialogue",
                {"choice": choice, "action_params": params})


def dlg(r):
    return r.get("diplomatic_dialogue") or {}


def sig(d):
    return json.dumps(d.get("settlement_terms"), sort_keys=True, ensure_ascii=False)


# mailbox BEFORE reset (stack leakage probe from the previous session)
mb0 = get("/mailbox")
save("g4_legB_mailbox_before_reset.json", mb0)
results.append({"step": "mailbox before reset (stack-leak probe)",
                "entries": [{"dialogue_type": e.get("dialogue_type"),
                             "dialogue_mode": e.get("dialogue_mode"),
                             "title": e.get("title") or e.get("label")}
                            for e in (mb0.get("mailbox") or mb0.get("entries") or [])],
                "raw_keys": sorted(mb0.keys())})

st, ng = post("/new_game", {})
results.append({"step": "new_game", "http": st})

st, m = post("/command", {"command": "propose common peace with Britain",
                          "action": "propose_common_peace",
                          "target_nation": "Britain", "war_id": "war_1"})
md = dlg(m)
base_sig = sig(md)
results.append({"step": "mount", "http": st, "mode": md.get("dialogue_mode"),
                "terms": md.get("settlement_terms")})

st, dial = respond("settlement_dial_harsher",
                   {"action": "settlement_dial_harsher", "scope": "table"})
dd = dlg(dial)
mod_sig = sig(dd)
results.append({"step": "dial_harsher", "http": st, "terms": dd.get("settlement_terms"),
                "changed": mod_sig != base_sig})

st, rev = respond("submit_settlement_for_review",
                  {"action": "submit_settlement_for_review"})
rd = dlg(rev)
results.append({"step": "submit_review", "http": st, "mode": rd.get("dialogue_mode")})

st, bo = respond("back_out_settlement", {"action": "back_out_settlement"})
wars_bo = ((bo.get("active_wars") or {}).get("wars") or [{}])[0]
save("g4_legB_clean_backout.json", bo)
results.append({"step": "back_out_settlement", "http": st,
                "success": bo.get("success"), "message": bo.get("message"),
                "settlement_draft_kept_after": wars_bo.get("settlement_draft_kept"),
                "dialogue_after": bool(dlg(bo))})

# mailbox right after back_out — any settlement dialogue still stacked?
mb1 = get("/mailbox")
save("g4_legB_clean_mailbox_after_backout.json", mb1)
results.append({"step": "mailbox after back_out",
                "payload_head": json.dumps(mb1, ensure_ascii=False)[:800]})

st, m2 = post("/command", {"command": "propose common peace with Britain",
                           "action": "propose_common_peace",
                           "target_nation": "Britain", "war_id": "war_1"})
m2d = dlg(m2)
save("g4_legB_clean_remount.json", m2)
results.append({"step": "remount after discard", "http": st,
                "mode": m2d.get("dialogue_mode"),
                "terms": m2d.get("settlement_terms"),
                "fresh_equals_baseline": sig(m2d) == base_sig,
                "modified_discarded": sig(m2d) != mod_sig})

respond("suspend_settlement_editor", {"action": "suspend_settlement_editor"})
save("g4_legB_clean_results.json", results)
print(json.dumps(results, indent=2, ensure_ascii=False))
