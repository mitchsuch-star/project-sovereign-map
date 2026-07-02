"""Leg E — E4c: behavioral probe of nation extraction breadth on the 1805 boot."""
import sys, json
sys.path.insert(0, "smoke_logs")
from g4_legE_lib import get, post, save

results = {}
for cmd in ["propose peace with Russia",
            "propose armistice with Russia",
            "propose open borders with Denmark",
            "propose alliance with Bavaria",
            "propose open borders with Sweden",
            "propose peace with Austria"]:
    st, r = post("/command", {"command": cmd})
    dd = r.get("diplomatic_dialogue")
    msg = json.dumps(r.get("message"), ensure_ascii=False)[:200]
    mounted = bool(dd)
    tn = dd.get("target_nation") if dd else None
    results[cmd] = {"status": st, "success": r.get("success"), "mounted": mounted,
                    "target_nation": tn, "message": msg}
    print(f"{cmd!r}: mounted={mounted} target={tn} success={r.get('success')} msg={msg[:140]}")
    if mounted:
        # back out to keep state clean
        st2, r2 = post("/respond_to_diplomatic_dialogue", {"choice": "reconsider"})
        print("   (backed out:", r2.get("success"), ")")
save("g4_legE_e4_nation_extraction_probe.json", results)
