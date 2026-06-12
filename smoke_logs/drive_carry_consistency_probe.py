"""G4F-7 probe — does the REVIEW (submit) score match the PROPOSE table?

Mount -> read per-court scores -> ease until every court >= 50 on the
table -> submit -> compare REVIEW rows against the last PROPOSE rows.
Any drift = same-tick scorer-seam bug. Also captures the blocked-submit
shape (mount fresh, submit immediately at 44/35) to show the exact
options the smoke saw.
"""
import json
import urllib.request

BASE = "http://127.0.0.1:8005"


def post(path, body):
    req = urllib.request.Request(
        BASE + path, data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"}, method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def act(action, params=None):
    body = {"choice": action}
    body["action_params"] = dict(params or {}, action=action)
    return post("/respond_to_diplomatic_dialogue", body)


def rows_of(resp):
    d = resp.get("diplomatic_dialogue") or {}
    return {
        r.get("nation"): (r.get("total"), r.get("band"), r.get("band_display"))
        for r in (d.get("per_court_acceptance") or [])
    }


def show(tag, resp):
    d = resp.get("diplomatic_dialogue") or {}
    oa = d.get("overall_acceptance") or {}
    print(f"--- {tag}: mode={d.get('dialogue_mode')} carries={oa.get('carries')} holdouts={oa.get('holdout_courts')}")
    for nation, (total, band, bd) in sorted(rows_of(resp).items()):
        print(f"    {nation}: total={total} band={band} display={bd!r}")
    return d


print("== leg A: fresh mount -> immediate submit (the smoke path) ==")
post("/new_game", {})
mount = post("/command", {
    "command": "propose common peace with Britain",
    "action": "propose_common_peace",
    "target_nation": "Britain", "war_id": "war_1",
})
d = show("MOUNT (PROPOSE)", mount)
print("    mount message:", (mount.get("message") or "")[:120])
table_rows = rows_of(mount)
sub = act("submit_settlement_for_review")
d2 = show("SUBMIT (REVIEW)", sub)
print("    submit message:", (sub.get("message") or "")[:160])
print("    review options:", [
    (o.get("action"), o.get("label"))
    for o in (sub.get("diplomatic_dialogue") or {}).get("options", [])
])
review_rows = rows_of(sub)
drift = {
    n: (table_rows.get(n), review_rows.get(n))
    for n in set(table_rows) | set(review_rows)
    if (table_rows.get(n) or (None,))[0] != (review_rows.get(n) or (None,))[0]
}
print("    SCORE DRIFT table->review:", drift if drift else "NONE (consistent)")

print()
print("== leg B: ease to all-accept on the table, then submit ==")
back = act("return_to_settlement_terms")
show("RETURN TO TERMS", back)
last = back
for i in range(1, 9):
    last = act("settlement_dial_generous", {"scope": "table"})
    r = rows_of(last)
    print(f"    ease #{i}:", {n: v[0] for n, v in sorted(r.items())})
    if all((v[0] or 0) >= 50 for v in r.values()):
        break
table_rows = rows_of(last)
show("TABLE BEFORE SUBMIT", last)
sub2 = act("submit_settlement_for_review")
d3 = show("SUBMIT (REVIEW)", sub2)
review_rows = rows_of(sub2)
drift2 = {
    n: (table_rows.get(n), review_rows.get(n))
    for n in set(table_rows) | set(review_rows)
    if (table_rows.get(n) or (None,))[0] != (review_rows.get(n) or (None,))[0]
}
print("    SCORE DRIFT table->review:", drift2 if drift2 else "NONE (consistent)")
print("    review options:", [
    (o.get("action"), o.get("label"))
    for o in (sub2.get("diplomatic_dialogue") or {}).get("options", [])
])
