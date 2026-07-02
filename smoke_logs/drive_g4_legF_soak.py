"""Gate 4 Leg F driver: SC-5 no-exposure soak + stability, 50 end-turns on shipped 1805 boot.

READ-ONLY on the codebase; writes evidence only under smoke_logs/.
Server: http://127.0.0.1:8013 (booted separately with LLM_MODE=mock, no SOVEREIGN_* vars).
"""
import json
import time
import urllib.request
import urllib.error

BASE = "http://127.0.0.1:8013"
OUT_SOAK = "smoke_logs/g4_legF_soak.json"
OUT_NEWGAME = "smoke_logs/g4_legF_newgame_raw.json"
OUT_HITS = "smoke_logs/g4_legF_forbidden_hits.json"
OUT_LAST = "smoke_logs/g4_legF_last_turn_raw.json"
OUT_SIDE = "smoke_logs/g4_legF_side_endpoints.json"

FORBIDDEN_ANYWHERE = [
    "Wait for Enemy Offer",
    "wait_for_enemy_offer",
    "ask_for_terms",
    "Ask for terms",
]
# "incoming_settlement_offer" is allowed ONLY as a dict key whose value is None.
SPECIAL_KEY = "incoming_settlement_offer"


def http(method, path, body=None, timeout=120):
    url = BASE + path
    data = None
    headers = {}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            ms = (time.perf_counter() - t0) * 1000.0
            return resp.status, raw, ms
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        ms = (time.perf_counter() - t0) * 1000.0
        return e.code, raw, ms
    except Exception as e:  # noqa: BLE001
        ms = (time.perf_counter() - t0) * 1000.0
        return -1, f"EXC: {type(e).__name__}: {e}", ms


def walk(obj, path=""):
    """Yield (path, key_or_None, value) triples for every node."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{path}.{k}" if path else str(k)
            yield (p, k, v)
            yield from walk(v, p)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            p = f"{path}[{i}]"
            yield (p, None, v)
            yield from walk(v, p)


def scan_forbidden(obj, raw_text, context):
    """Return list of hit dicts. Enforces:
    - FORBIDDEN_ANYWHERE strings: any occurrence in the raw JSON text = hit.
    - SPECIAL_KEY: allowed only as a dict key whose value is None; any other
      occurrence (string VALUE anywhere, or key with non-null value) = hit.
    """
    hits = []
    for s in FORBIDDEN_ANYWHERE:
        if s in raw_text:
            # find structural locations for evidence
            locs = []
            for p, k, v in walk(obj):
                if isinstance(v, str) and s in v:
                    locs.append({"path": p, "value": v[:300]})
                if k is not None and s in str(k):
                    locs.append({"path": p, "key": k})
            hits.append({"context": context, "string": s, "locations": locs[:10]})
    if SPECIAL_KEY in raw_text:
        for p, k, v in walk(obj):
            if k == SPECIAL_KEY:
                if v is not None:
                    hits.append({
                        "context": context, "string": SPECIAL_KEY,
                        "kind": "key_with_non_null_value", "path": p,
                        "value_preview": json.dumps(v)[:500],
                    })
            elif isinstance(v, str) and SPECIAL_KEY in v:
                hits.append({
                    "context": context, "string": SPECIAL_KEY,
                    "kind": "string_value", "path": p, "value": v[:300],
                })
    return hits


def find_floats(obj, cap=5):
    """Return up to cap paths holding non-integral float values (Godot crash risk).
    Integral floats (e.g. 5.0) are ALSO reported since Godot int expectations break,
    but flagged separately."""
    out = []
    for p, _k, v in walk(obj):
        if isinstance(v, float):
            out.append({"path": p, "value": v, "integral": float(v).is_integer()})
            if len(out) >= cap:
                break
    return out


def main():
    results = {
        "leg": "F",
        "base": BASE,
        "turns": [],
        "forbidden_hits": [],
        "side_endpoint_checks": [],
        "incoming_proposals": [],  # (turn, nation, type)
        "non_200s": [],
        "missing_success_flag": [],
        "float_sightings": [],
        "game_over": None,
    }

    # ---- F1: /new_game ----
    status, raw, ms = http("POST", "/new_game", {})
    print(f"/new_game -> {status} in {ms:.0f}ms, {len(raw)} bytes")
    with open(OUT_NEWGAME, "w", encoding="utf-8") as f:
        f.write(raw)
    ng = json.loads(raw) if status == 200 else {}
    results["new_game"] = {
        "status": status, "ms": round(ms),
        "success": ng.get("success"),
        "turn": (ng.get("game_state") or {}).get("turn"),
        "active_wars_count": len(((ng.get("active_wars") or {}).get("wars")) or []),
        "wars": [
            {"war_instance_id": w.get("war_instance_id"), "opponent": w.get("opponent"),
             "settlement_available": w.get("settlement_available")}
            for w in (((ng.get("active_wars") or {}).get("wars")) or [])
        ],
    }
    hits = scan_forbidden(ng, raw, "new_game")
    results["forbidden_hits"].extend(hits)
    iso = ng.get("incoming_settlement_offer", "ABSENT")
    results["new_game"]["incoming_settlement_offer"] = (
        "ABSENT" if iso == "ABSENT" else ("null" if iso is None else "NON-NULL")
    )

    side_paths = ["/mailbox", "/pending_envoy", "/notifications", "/dispatch"]

    # ---- F2: 50 end-turns ----
    last_raw = raw
    for i in range(1, 51):
        status, raw, ms = http("POST", "/command", {"command": "end turn"})
        rec = {"iteration": i, "status": status, "ms": round(ms, 1)}
        if status != 200:
            rec["body_preview"] = raw[:2000]
            results["non_200s"].append(rec)
            results["turns"].append(rec)
            print(f"[{i}] NON-200: {status} ms={ms:.0f}")
            continue
        obj = json.loads(raw)
        last_raw = raw
        gs = obj.get("game_state") or {}
        rec["turn_after"] = gs.get("turn")
        rec["success"] = obj.get("success")
        if "success" not in obj:
            results["missing_success_flag"].append({"iteration": i})
        events = obj.get("events")
        rec["events_count"] = len(events) if isinstance(events, list) else None
        # enemy_phase events sometimes nested
        ep = obj.get("enemy_phase") or {}
        ep_events = ep.get("events") if isinstance(ep, dict) else None
        rec["enemy_phase_events_count"] = len(ep_events) if isinstance(ep_events, list) else None

        # incoming_settlement_offer field check
        iso = obj.get("incoming_settlement_offer", "ABSENT")
        rec["incoming_settlement_offer"] = (
            "ABSENT" if iso == "ABSENT" else ("null" if iso is None else "NON-NULL")
        )
        if iso not in ("ABSENT", None):
            results["forbidden_hits"].append({
                "context": f"end_turn_{i}", "string": SPECIAL_KEY,
                "kind": "top_level_non_null",
                "value_preview": json.dumps(iso)[:800],
            })

        # forbidden string scan
        hits = scan_forbidden(obj, raw, f"end_turn_{i}")
        if hits:
            results["forbidden_hits"].extend(hits)
            print(f"[{i}] FORBIDDEN HITS: {len(hits)}")

        # incoming proposal presence (F3)
        ip = obj.get("incoming_proposal")
        rec["incoming_proposal"] = bool(ip)
        if ip:
            nation = ip.get("from_nation") or ip.get("nation") or "?"
            ptype = ip.get("proposal_type") or ip.get("type") or "?"
            results["incoming_proposals"].append(
                {"iteration": i, "nation": nation, "type": ptype})
            rec["incoming_proposal_detail"] = {"nation": nation, "type": ptype}
        # also check diplomatic_dialogue mounted spontaneously
        dd = obj.get("diplomatic_dialogue")
        if dd:
            rec["diplomatic_dialogue_type"] = dd.get("dialogue_type") or dd.get("type")

        # float scan (Godot int rule) — sample
        fl = find_floats(obj, cap=3)
        if fl:
            results["float_sightings"].append({"iteration": i, "floats": fl})

        # game over?
        go = obj.get("game_over") or gs.get("game_over")
        if go:
            results["game_over"] = {"iteration": i, "detail": go,
                                    "victory": obj.get("victory"),
                                    "message": (obj.get("message") or "")[:500]}
            results["turns"].append(rec)
            print(f"[{i}] GAME OVER: {go}")
            break

        results["turns"].append(rec)
        print(f"[{i}] turn_after={rec['turn_after']} ms={ms:.0f} "
              f"events={rec['events_count']} ip={rec['incoming_proposal']} "
              f"iso={rec['incoming_settlement_offer']}")

        # every ~10 turns: side endpoints
        if i % 10 == 0:
            side_snap = {"iteration": i, "endpoints": {}}
            for sp in side_paths:
                s2, r2, m2 = http("GET", sp)
                entry = {"status": s2, "ms": round(m2, 1), "bytes": len(r2)}
                if s2 == 200:
                    try:
                        o2 = json.loads(r2)
                        h2 = scan_forbidden(o2, r2, f"{sp}@{i}")
                        if h2:
                            results["forbidden_hits"].extend(h2)
                            entry["forbidden_hits"] = len(h2)
                    except json.JSONDecodeError:
                        entry["json_error"] = True
                else:
                    entry["body_preview"] = r2[:500]
                    results["non_200s"].append(
                        {"iteration": i, "path": sp, "status": s2,
                         "body_preview": r2[:500]})
                side_snap["endpoints"][sp] = entry
            results["side_endpoint_checks"].append(side_snap)

    # save last end-turn raw for evidence
    with open(OUT_LAST, "w", encoding="utf-8") as f:
        f.write(last_raw)

    # side endpoint raw dump at end (final snapshot for evidence)
    finals = {}
    for sp in side_paths:
        s2, r2, _m2 = http("GET", sp)
        try:
            finals[sp] = {"status": s2, "body": json.loads(r2)}
        except json.JSONDecodeError:
            finals[sp] = {"status": s2, "body_raw": r2[:5000]}
    with open(OUT_SIDE, "w", encoding="utf-8") as f:
        json.dump(finals, f, indent=1)

    # ---- timing summary (F5) ----
    ok_times = sorted(t["ms"] for t in results["turns"] if t.get("status") == 200)
    if ok_times:
        n = len(ok_times)
        med = ok_times[n // 2] if n % 2 == 1 else (ok_times[n // 2 - 1] + ok_times[n // 2]) / 2
        results["timing"] = {
            "count": n, "median_ms": round(med, 1),
            "max_ms": round(ok_times[-1], 1), "min_ms": round(ok_times[0], 1),
        }

    # ---- proposal volume summary (F3) ----
    vol = {}
    for p in results["incoming_proposals"]:
        key = f"{p['nation']}|{p['type']}"
        vol.setdefault(key, []).append(p["iteration"])
    results["proposal_volume_by_nation_type"] = vol

    with open(OUT_SOAK, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=1)
    with open(OUT_HITS, "w", encoding="utf-8") as f:
        json.dump(results["forbidden_hits"], f, indent=1)

    print("\n=== SUMMARY ===")
    print(json.dumps({
        "turns_run": len(results["turns"]),
        "forbidden_hits": len(results["forbidden_hits"]),
        "non_200s": len(results["non_200s"]),
        "missing_success_flag": len(results["missing_success_flag"]),
        "float_sightings": len(results["float_sightings"]),
        "timing": results.get("timing"),
        "proposal_volume": {k: len(v) for k, v in vol.items()},
        "game_over": results["game_over"],
    }, indent=1))


if __name__ == "__main__":
    main()
