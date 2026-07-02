"""Leg E — E11: float + raw-key scans over every saved Leg E payload."""
import sys, glob, json
sys.path.insert(0, "smoke_logs")
from g4_legE_lib import find_floats, scan_display_strings

float_hits = {}
display_hits = {}
KNOWN_FLOAT_FIELDS = ("material_share", "support_share", "hegemon_share")

for path in sorted(glob.glob("smoke_logs/g4_legE_*.json")):
    try:
        obj = json.load(open(path, encoding="utf-8"))
    except Exception as e:
        print("skip", path, e)
        continue
    fh = find_floats(obj)
    fh = [(p, v) for p, v in fh if not any(k in p for k in KNOWN_FLOAT_FIELDS)]
    if fh:
        float_hits[path] = fh[:15]
    dh = scan_display_strings(obj)
    if dh:
        display_hits[path] = dh[:15]

print("=== FLOAT HITS (excluding known-designed share fields) ===")
for path, hits in float_hits.items():
    print(path)
    for p, v in hits:
        print("   ", p, "=", v)
print("\n=== DISPLAY-STRING RAW-KEY HITS ===")
for path, hits in display_hits.items():
    print(path)
    for p, pat, text in hits:
        print("   ", p, "| pat:", pat, "| text:", text[:160].encode("ascii", "backslashreplace").decode())

out = {"float_hits": {k: [[p, v] for p, v in vs] for k, vs in float_hits.items()},
       "display_hits": {k: [[p, pat, t] for p, pat, t in vs] for k, vs in display_hits.items()}}
json.dump(out, open("smoke_logs/g4_legE_e11_scan_results.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("\nsaved smoke_logs/g4_legE_e11_scan_results.json")
