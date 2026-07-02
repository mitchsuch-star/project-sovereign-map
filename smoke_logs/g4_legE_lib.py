"""Shared HTTP helpers for Gate 4 Leg E smoke (port 8012). stdlib only."""
import json
import urllib.request
import urllib.error

BASE = "http://127.0.0.1:8012"


def _do(method, path, body=None, timeout=60):
    url = BASE + path
    data = None
    headers = {"Content-Type": "application/json"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            payload = json.loads(e.read().decode("utf-8"))
        except Exception:
            payload = {"_raw": "unreadable"}
        return e.code, payload


def get(path, timeout=60):
    return _do("GET", path, None, timeout)


def post(path, body, timeout=120):
    return _do("POST", path, body, timeout)


def save(name, obj):
    p = "smoke_logs/" + name
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
    print("saved", p)


# ---------- scanners ----------

def find_floats(obj, path="$"):
    """Return list of (path, value) for non-int floats anywhere in payload."""
    hits = []
    if isinstance(obj, float):
        if not obj.is_integer() or True:  # ANY float type reaching client is suspect
            hits.append((path, obj))
    elif isinstance(obj, dict):
        for k, v in obj.items():
            hits.extend(find_floats(v, f"{path}.{k}"))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            hits.extend(find_floats(v, f"{path}[{i}]"))
    return hits


RAW_KEY_PATTERNS = [
    "KingdomOfItaly", "PapalStates", "OttomanEmpire", "UnitedKingdom",
    "DEFENSIVE_ALLIANCE", "NON_AGGRESSION", "TRADE_AGREEMENT", "MILITARY_ACCESS",
    "gold_indemnity", "near_acceptable", "hard_reject", "war_instance",
    "propose_", "settlement_", "_penalty", "_bonus", "_mod",
]

DISPLAY_KEY_HINTS = ("display", "message", "summary", "text", "label", "line",
                     "description", "copy", "title", "name", "reason", "advisory",
                     "voice", "beat", "narrative", "feedback", "warning")


def scan_display_strings(obj, path="$", parent_key=""):
    """Scan strings in display-ish fields for raw internal keys."""
    hits = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            hits.extend(scan_display_strings(v, f"{path}.{k}", k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            hits.extend(scan_display_strings(v, f"{path}[{i}]", parent_key))
    elif isinstance(obj, str):
        key_l = parent_key.lower()
        is_displayish = any(h in key_l for h in DISPLAY_KEY_HINTS)
        if is_displayish:
            for pat in RAW_KEY_PATTERNS:
                if pat in obj:
                    hits.append((path, pat, obj[:220]))
    return hits
