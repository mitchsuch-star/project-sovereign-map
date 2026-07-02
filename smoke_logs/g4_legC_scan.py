# Leg C C8 scan: floats, raw internal keys in display-ish fields, forbidden copy.
import glob
import json
import re

DISPLAYISH = re.compile(
    r"(_display$|^display_|^label$|^description$|^line$|^reasoning$|^talleyrand_text$|"
    r"^message$|^voice_line$|^reason_display$|^summary$|^text$|^standing_phrase$|"
    r"^direction_summary$|^propose_carry_hint$|^losing_side_pressure_voice$|"
    r"^recurring_gold_preset_reason$|^ratify_blocked_reason$)"
)
RAW_KEY = re.compile(r"\b[a-z][a-z0-9]*(?:_[a-z0-9]+)+\b")  # snake_case token
FORBIDDEN = re.compile(r"\b(conference|veto)\b", re.IGNORECASE)

floats = {}
rawkey_hits = {}
forbidden_hits = {}


def walk(node, path, fname):
    if isinstance(node, dict):
        for k, v in node.items():
            walk(v, f"{path}.{k}", fname)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            walk(v, f"{path}[{i}]", fname)
    elif isinstance(node, float):
        if not node.is_integer() or True:  # report ALL floats (ints must be ints)
            floats.setdefault(f"{path.split('.')[-1]}={node!r}", []).append(f"{fname}:{path}")
    elif isinstance(node, str):
        key = path.rsplit(".", 1)[-1].split("[")[0]
        if FORBIDDEN.search(node):
            forbidden_hits.setdefault(node[:160], []).append(f"{fname}:{path}")
        if DISPLAYISH.search(key):
            m = RAW_KEY.findall(node)
            # allow ordinary English words with no underscores; flag snake_case tokens
            if m:
                rawkey_hits.setdefault(f"{key}: {node[:140]} -> tokens {m}", []).append(f"{fname}:{path}")


for fn in sorted(glob.glob("smoke_logs/g4_legC_*.json")):
    with open(fn, encoding="utf-8") as f:
        data = json.load(f)
    walk(data, "$", fn.split("\\")[-1].split("/")[-1])

print("=== FLOAT VALUES (all) ===")
for k, locs in sorted(floats.items()):
    print(f"  {k}  x{len(locs)}  e.g. {locs[0]}")
print(f"  total distinct float field/value combos: {len(floats)}")

print("=== RAW snake_case TOKENS IN DISPLAY-ISH FIELDS ===")
for k, locs in sorted(rawkey_hits.items()):
    print(f"  {k}  x{len(locs)}  e.g. {locs[0]}")

print("=== FORBIDDEN COPY (conference/veto) ===")
for k, locs in sorted(forbidden_hits.items()):
    print(f"  {k}  x{len(locs)}  e.g. {locs[0]}")
if not forbidden_hits:
    print("  none")
