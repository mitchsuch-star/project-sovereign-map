"""Leg E — E5: diplomatic ledger scan; E6: diplomatic preview for Britain/Prussia/Spain."""
import sys, json
sys.path.insert(0, "smoke_logs")
from g4_legE_lib import get, post, save, find_floats, scan_display_strings

# ---- E5: ledger ----
st, led = get("/diplomatic_ledger")
print("ledger status:", st, "success:", led.get("success"))
save("g4_legE_e5_diplomatic_ledger.json", led)
lg = led.get("ledger") or led
print("ledger top keys:", sorted(lg.keys())[:25])
for tab in ("nations", "treaties", "balance_of_europe", "talleyrand", "recent_settlements"):
    v = lg.get(tab)
    kind = type(v).__name__
    size = len(v) if isinstance(v, (list, dict)) else "-"
    print(f"tab {tab}: {kind} len={size} present={v is not None}")

hits = scan_display_strings(led)
print("\nE5 display-string raw-key hits:", len(hits))
for h in hits[:30]:
    print("  ", h[0], "| pat:", h[1], "| text:", h[2][:150])

fl = find_floats(led)
print("E5 float count:", len(fl))
for f in fl[:20]:
    print("  ", f[0], "=", f[1])

# ---- E6: previews ----
for nation in ("Britain", "Prussia", "Spain"):
    st, pv = get(f"/diplomatic_preview?nation={nation}")
    print(f"\npreview {nation}: status={st} success={pv.get('success')}")
    save(f"g4_legE_e6_preview_{nation.lower()}.json", pv)
    print(" top keys:", sorted(pv.keys())[:25])

# nation-list mode
st, pv0 = get("/diplomatic_preview")
save("g4_legE_e6_preview_nationlist.json", pv0)
print("\nnation-list mode keys:", sorted(pv0.keys())[:25])
nl = pv0.get("nations") or pv0.get("nation_list")
if isinstance(nl, list):
    print("nations count:", len(nl))
    print("first 3:", json.dumps(nl[:3], ensure_ascii=False)[:800])
