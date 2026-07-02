# Gate 4 LEG D phase 2: extra probes + B11-style payload scans (port 8011)
import glob
import json
import os
import re
import urllib.request
import urllib.parse
import urllib.error

BASE = "http://127.0.0.1:8011"
OUT = os.path.dirname(os.path.abspath(__file__))


def save(name, obj):
    path = os.path.join(OUT, f"g4_legD_{name}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
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


print("=== extra GET captures for scan coverage ===")
for name, path in [
    ("dispatch", "/dispatch"),
    ("notifications", "/notifications"),
    ("mailbox", "/mailbox"),
    ("pending_envoy", "/pending_envoy"),
    ("diplomatic_ledger", "/diplomatic_ledger"),
    ("coalition_status", "/debug/coalition_status"),
    ("proposal_cooldowns", "/debug/proposal_cooldowns"),
]:
    sc, resp = get(path)
    save(name, resp)
    print(f"  GET {path} -> {sc}")

print("=== probe: invalid war_id mount ===")
sc, resp = post("/command", {
    "command": "propose common peace with Britain",
    "action": "propose_common_peace",
    "target_nation": "Britain",
    "war_id": "war_999",
})
save("probe_invalid_war_id", resp)
print(f"  http={sc} success={resp.get('success')} error={resp.get('error')!r} "
      f"error_display={resp.get('error_display')!r} message={resp.get('message')!r} "
      f"dialogue={'YES' if resp.get('diplomatic_dialogue') else 'no'}")

print("=== probe: no target_nation mount ===")
sc, resp = post("/command", {
    "command": "propose common peace",
    "action": "propose_common_peace",
})
save("probe_no_target", resp)
print(f"  http={sc} success={resp.get('success')} error={resp.get('error')!r} "
      f"error_display={resp.get('error_display')!r} message={resp.get('message')!r} "
      f"dialogue={'YES' if resp.get('diplomatic_dialogue') else 'no'}")

print("=== D7 scans over all g4_legD_*.json payloads ===")

DISPLAYISH_KEYS = re.compile(
    r"(_display$|^display_|_label$|^label$|^message$|^text$|^title$|^subtitle$"
    r"|^body$|^copy$|_line$|^line$|^reason$|display_reason|disabled_reason$"
    r"|^error_display$|_copy$|^name_display$|^display_name$)"
)
SNAKE_TOKEN = re.compile(r"\b[a-z][a-z0-9]*(?:_[a-z0-9]+)+\b")
CAMEL_NATION = re.compile(r"\b(KingdomOfItaly|PapalStates|OttomanEmpire|UnitedKingdom)\b")

float_hits = {}
display_hits = {}


def walk(obj, path, fname):
    if isinstance(obj, dict):
        for k, v in obj.items():
            walk(v, f"{path}.{k}", fname)
            if isinstance(v, str) and DISPLAYISH_KEYS.search(str(k)):
                snakes = SNAKE_TOKEN.findall(v)
                camels = CAMEL_NATION.findall(v)
                if snakes or camels:
                    key = f"{re.sub(r'\\[\\d+\\]', '[]', path)}.{k}"
                    display_hits.setdefault(key, []).append(
                        {"file": fname, "value": v, "tokens": snakes + camels})
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            walk(v, f"{path}[{i}]", fname)
    elif isinstance(obj, float):
        key = re.sub(r"\[\d+\]", "[]", path)
        float_hits.setdefault(key, []).append({"file": fname, "value": obj})


for fp in sorted(glob.glob(os.path.join(OUT, "g4_legD_*.json"))):
    fname = os.path.basename(fp)
    if fname in ("g4_legD_scan_floats.json", "g4_legD_scan_display_keys.json"):
        continue
    try:
        with open(fp, encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"  !! could not load {fname}: {e}")
        continue
    walk(data, "$", fname)

float_summary = {
    k: {"n": len(v), "example": v[0]} for k, v in sorted(float_hits.items())
}
display_summary = {
    k: {"n": len(v), "example": v[0]} for k, v in sorted(display_hits.items())
}
save("scan_floats", float_summary)
save("scan_display_keys", display_summary)
print(f"  float paths: {len(float_summary)}")
for k, v in float_summary.items():
    print(f"    FLOAT {k}  example={v['example']['value']!r} in {v['example']['file']} (n={v['n']})")
print(f"  display-key paths: {len(display_summary)}")
for k, v in display_summary.items():
    print(f"    DISPLAY {k}  tokens={v['example']['tokens']} value={v['example']['value'][:120]!r} in {v['example']['file']} (n={v['n']})")
