"""UXR-3 "The look-and-feel review" — the assembler (Pre-Deploy S11, October 13, 2026).

    .venv/Scripts/python.exe -X utf8 tools/uxr3_review.py marks     --records DIR [--probe probe.json]
    .venv/Scripts/python.exe -X utf8 tools/uxr3_review.py packets   --records DIR --index index.json --packet DIR
    .venv/Scripts/python.exe -X utf8 tools/uxr3_review.py aggregate --records DIR --packet DIR

Reads against `docs/UX_CHECKLIST_V1.json` (frozen; S11 Part 1) and nothing
else. The records directory holds the instruments' records:

    readability.json   tools/uxr0_readability_report.py --record   (R1)
    contrast.json      tools/uxr2b_contrast_report.py --record     (R3; High contrast OFF)
    consistency.json   tools/uxr3_consistency_census.py --record   (R4)
    fit.json           tools/uxr3_fit_report.py --record           (R7)
    probe.json         tools/uxr3_action_probe.py                  (R5's driven half, R6)
    live_citations.json  the live-backend driven records a HANDOFF / NOT PRESSED
                         control may cite (R6), each with its evidence

`marks` writes `instrument_marks.json` (R1, R3, R4, R6, R7 and R5's SILENT
half, each ✓/✗ with its reason). `packets` builds the blind readers' packet:
one evidence card per surface (the surface, its must_show line, its frames —
cropped to its own top-level rects where it does not fill the screen, never
scaled — and the probe's record of its controls), one file per group, the
records copied beside them. `aggregate` reads `panel_raw/reader_{1,2,3}.json`,
takes the mark two of the three give for R2, R8 and R5's reader half
(`tools/score_panel.py eyes`'s rule; no reader may abstain), records the spread,
and writes `review.json`: every surface × item, its score out of 8, the worst
five.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import shutil
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
CHECKLIST = REPO / "docs" / "UX_CHECKLIST_V1.json"
ITEMS = ["R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8"]
READER_ITEMS = ["R2", "R5", "R8"]
FIVE = ["1920x1080", "2560x1440", "3440x1440", "5120x1440", "3840x2160"]

sys.path.insert(0, str(REPO / "tools"))


def load(path: pathlib.Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def checklist() -> dict:
    return json.loads(CHECKLIST.read_text(encoding="utf-8"))


def shot_of(s: dict) -> str | None:
    """The IQ-10 shot a checklist surface is read from. The frozen checklist
    names three popups with `shot: null` (the manifest had never shot them);
    a surface the manifest gains later is read under the id the checklist
    already gives it (SYSTEMS_REFERENCE §113.1; Pre-Deploy S12, UXR3-56 … 58)."""
    if s.get("shot"):
        return s["shot"]
    import iq10_run_captures as R
    return s["id"] if any(x["id"] == s["id"] for x in R.SHOTS) else None


def surfaces(cl: dict) -> list[dict]:
    out = []
    for g in cl["groups"]:
        for s in g["surfaces"]:
            out.append(dict(s, shot=shot_of(s), group=g["key"], group_order=g["order"],
                            top_five=g["top_five"]))
    return out


def _by_resolution(readings: dict) -> dict:
    """{"1920x1080": reading} from keys like "1920x1080@1.00"."""
    out = {}
    for key, r in (readings or {}).items():
        out[key.split("@", 1)[0]] = r
    return out


# ── the instrument items ────────────────────────────────────────────────────

def mark_r1(sid: str, rec: dict) -> tuple[bool, str]:
    surf = (rec.get("surfaces") or {}).get(sid)
    if not surf:
        return False, "no reading: the capture harness does not reach it"
    by = _by_resolution(surf.get("readings"))
    why = []
    for res in FIVE:
        r = by.get(res)
        if r is None:
            why.append(f"{res}: no reading")
            continue
        if not r.get("ok"):
            why.append(f"{res}: the reading failed")
        c = r.get("counts") or {}
        bad = int(c.get("red", 0)) + int(c.get("p1", 0))
        if bad:
            worst = (r.get("flagged") or [{}])[0]
            why.append(f"{res}: {c.get('red', 0)} RED + {c.get('p1', 0)} P1 "
                       f"(worst {worst.get('em')} px em, {worst.get('path', '')} '{worst.get('text', '')}')")
    return (not why), "; ".join(why) or "0 RED / 0 P1 at all five resolutions"


def mark_r3(sid: str, rec: dict) -> tuple[bool, str]:
    surf = (rec.get("surfaces") or {}).get(sid)
    if not surf:
        return False, "no reading: the capture harness does not reach it"
    by = _by_resolution(surf.get("readings"))
    why = []
    for res in FIVE:
        r = by.get(res)
        if r is None:
            why.append(f"{res}: no reading")
            continue
        if not r.get("ok"):
            why.append(f"{res}: the reading failed")
        c = r.get("counts") or {}
        if int(c.get("measured", 0)) < 1:
            why.append(f"{res}: nothing measured")
        if int(c.get("under", 0)):
            u = (r.get("under") or [{}])[0]
            why.append(f"{res}: {c.get('under')} row(s) under the floor (worst {u.get('ratio')} : 1, "
                       f"{u.get('color')} on {u.get('bg')}, {u.get('path')} '{u.get('text')}')")
    return (not why), "; ".join(why) or "0 rows under 4.5 / 3 : 1 at all five resolutions (High contrast off)"


def mark_r4(sid: str, rec: dict) -> tuple[bool, str]:
    surf = (rec.get("surfaces") or {}).get(sid)
    if not surf:
        return False, "the census did not read it"
    if surf.get("pass"):
        return True, f"0 one-off sizes or greys in {len(surf.get('files') or [])} file(s) ({surf.get('road')})"
    parts = [f"{f} ({n})" for f, n in sorted((surf.get("by_file") or {}).items(), key=lambda kv: -kv[1])]
    return False, (f"{surf.get('size_hits', 0)} one-off size(s) and {surf.get('grey_hits', 0)} one-off grey(s): "
                   + ", ".join(parts))


def mark_r7(sid: str, rec: dict) -> tuple[bool, str]:
    surf = (rec.get("surfaces") or {}).get(sid)
    if not surf:
        return False, "no reading: the capture harness does not reach it"
    return bool(surf.get("pass")), "; ".join(surf.get("why") or []) or \
        "nothing clipped, cut, off-screen or under a modal at 1920x1080, 3840x2160, 5120x1440"


def _cited(scene: str, c: dict, citations: list[dict]) -> dict | None:
    for cit in citations:
        if cit.get("scene") and not scene.endswith(cit["scene"]):
            continue
        m = cit.get("match") or {}
        if "text" in m and str(c.get("text", "")).strip() != m["text"]:
            continue
        if "path_endswith" in m and not str(c.get("path", "")).endswith(m["path_endswith"]):
            continue
        if "kind" in m and c.get("kind") != m["kind"]:
            continue
        if "meta_startswith" in m and not str(c.get("meta", "")).startswith(m["meta_startswith"]):
            continue
        return cit
    return None


def mark_r6(sid: str, scene: str, probe: dict, citations: list[dict]) -> tuple[bool, str, dict]:
    rec = (probe.get("shots") or {}).get(sid)
    detail = {"visible": 0, "handoff_cited": 0, "unproven": [], "silent": [], "errors": []}
    if not rec or not rec.get("reached"):
        return False, "the action probe cannot reach it", detail
    actions = [c for c in rec.get("controls") or [] if c.get("result") != "DISABLED"]
    if not actions:
        return False, "no enumerable control: nothing proves an action answers", detail
    for c in actions:
        res = c.get("result")
        label = (c.get("text") or c.get("meta") or c.get("tooltip") or c.get("path", "").split("/")[-1])[:40]
        if c.get("script_errors"):
            detail["errors"].append(f"{label}: {c['script_errors'][0][:160]}")
        if res == "VISIBLE" and not c.get("script_errors"):
            detail["visible"] += 1
        elif res in ("HANDOFF", "NOT PRESSED"):
            cit = _cited(scene, c, citations)
            if cit:
                detail["handoff_cited"] += 1
            else:
                detail["unproven"].append(f"{label} [{res.lower()}"
                                          + (f": {', '.join(s[1] for s in c.get('signals') or [])[:60]}" if c.get("signals") else "")
                                          + (f": {', '.join(c.get('api_calls') or [])[:60]}" if c.get("api_calls") else "")
                                          + "]")
        elif res == "SILENT":
            detail["silent"].append(label)
        else:
            detail["unproven"].append(f"{label} [{str(res).lower()}]")
    ok = not detail["unproven"] and not detail["silent"] and not detail["errors"]
    why = []
    if detail["silent"]:
        why.append(f"{len(detail['silent'])} SILENT: " + "; ".join(detail["silent"][:6]))
    if detail["unproven"]:
        why.append(f"{len(detail['unproven'])} unproven: " + "; ".join(detail["unproven"][:6]))
    if detail["errors"]:
        why.append(f"{len(detail['errors'])} SCRIPT ERROR on press: " + "; ".join(detail["errors"][:3]))
    if ok:
        why.append(f"{detail['visible']} control(s) answer on screen"
                   + (f", {detail['handoff_cited']} by a cited live record" if detail["handoff_cited"] else ""))
    return ok, "; ".join(why), detail


# A HUD component shot ALONE never runs without the war room that hosts it:
# the top bar's nav buttons open nothing when no screen is registered, and the
# war HUD's rows hand their click to main.gd, which is not there. Where the war
# room's own probe pressed the same control (its path is the component's under
# the war room's `Control/` root, with the same words), that record is the
# component's for it. Decided in Part 2, before any reader marked, and applied
# to every component shot alike; the packet shows both records.
HOSTED = {"top_bar.tscn": "war_room_boot", "war_status_panel.tscn": "war_room_boot",
          "notification_bar.tscn": "war_room_boot", "tutorial_overlay.tscn": "war_room_tutorial"}
HOST_ROOT = "Control/"


def host_read(probe: dict) -> dict:
    shots = probe.get("shots") or {}
    hosts = {shot: {(c.get("path"), c.get("text")): c for c in (shots.get(shot) or {}).get("controls") or []}
             for shot in set(HOSTED.values())}
    for sid, rec in shots.items():
        host_shot = HOSTED.get(rec.get("scene", "").rsplit("/", 1)[-1])
        if host_shot is None:
            continue
        for c in rec.get("controls") or []:
            if c.get("result") not in ("SILENT", "HANDOFF"):
                continue
            h = hosts[host_shot].get((HOST_ROOT + str(c.get("path", "")), c.get("text")))
            if h and h.get("result") == "VISIBLE" and not h.get("script_errors"):
                c["alone"] = {"result": c["result"], "changes": c.get("changes"),
                              "signals": c.get("signals"), "api_calls": c.get("api_calls")}
                c["result"] = "VISIBLE"
                c["changes"] = h.get("changes")
                c["host"] = f"read in its host, {host_shot}: " + "; ".join((h.get("changes") or [])[:2])
    return probe


def mark_r5_auto(sid: str, probe: dict) -> tuple[bool | None, str]:
    rec = (probe.get("shots") or {}).get(sid)
    if not rec or not rec.get("reached"):
        return False, "the action probe cannot reach it: the driven half cannot be evidenced"
    silent = [c for c in rec.get("controls") or [] if c.get("result") == "SILENT"]
    if silent:
        return False, "SILENT control(s): " + "; ".join(
            (c.get("text") or c.get("meta") or c.get("path", "").split("/")[-1])[:40] for c in silent[:6])
    return None, "no SILENT control (the readers judge the rest)"


def instrument_marks(records: pathlib.Path) -> dict:
    cl = checklist()
    read = load(records / "readability.json")
    con = load(records / "contrast.json")
    cen = load(records / "consistency.json")
    fit = load(records / "fit.json")
    probe = host_read(load(records / "probe.json"))
    citations = (load(records / "live_citations.json") or {}).get("citations", [])
    out = {}
    for s in surfaces(cl):
        sid, shot = s["id"], s["shot"]
        key = shot or sid
        m = {}
        if shot is None:
            for item in ("R1", "R3", "R7"):
                m[item] = {"pass": False, "why": "no IQ-10 shot: the capture harness cannot reach it"}
        else:
            ok, why = mark_r1(key, read)
            m["R1"] = {"pass": ok, "why": why}
            ok, why = mark_r3(key, con)
            m["R3"] = {"pass": ok, "why": why}
            ok, why = mark_r7(key, fit)
            m["R7"] = {"pass": ok, "why": why}
        ok, why = mark_r4(sid, cen)
        m["R4"] = {"pass": ok, "why": why}
        if shot is None:
            m["R6"] = {"pass": False, "why": "no IQ-10 shot: the action probe cannot reach it"}
            m["R5_auto"] = {"pass": False, "why": "no IQ-10 shot: the driven half cannot be evidenced"}
        else:
            ok, why, detail = mark_r6(key, s["scene"], probe, citations)
            m["R6"] = {"pass": ok, "why": why, "detail": detail}
            ok5, why5 = mark_r5_auto(key, probe)
            m["R5_auto"] = {"pass": ok5, "why": why5}
        out[sid] = m
    return out


# ── the readers' packet ─────────────────────────────────────────────────────

def _frame_for(index: dict, shot: str, res: str):
    for row in index.get("rows", []):
        if str(row.get("base_id")) == shot and "%dx%d" % tuple(row.get("resolution") or (0, 0)) == res:
            for r in row.get("results", []):
                frames = r.get("frames") or []
                if frames:
                    return r, frames[-1]
    return None, None


def crop(png: str, frame: dict, scale: float, out: pathlib.Path) -> str:
    """The surface's own top-level rects (logical px x scale), with a margin;
    the whole frame when they fill most of it. Never scaled."""
    from PIL import Image
    img = Image.open(png)
    view = frame.get("logical_viewport") or [img.width / scale, img.height / scale]
    rects = list((frame.get("surfaces") or {}).values())
    full = img.width * img.height
    box = None
    vw, vh = float(view[0]), float(view[1])
    for r in rects:
        x0, y0, w, h = (float(v) for v in r)
        if w <= 0 or h <= 0:
            continue
        if w * h >= 0.9 * vw * vh:
            continue                      # a full-screen dimmer, not the panel
        b = (x0, y0, x0 + w, y0 + h)
        box = b if box is None else (min(box[0], b[0]), min(box[1], b[1]), max(box[2], b[2]), max(box[3], b[3]))
    if box is not None:
        m = 16.0
        X0 = max(0, int((box[0] - m) * scale))
        Y0 = max(0, int((box[1] - m) * scale))
        X1 = min(img.width, int((box[2] + m) * scale))
        Y1 = min(img.height, int((box[3] + m) * scale))
        if X1 > X0 and Y1 > Y0 and (X1 - X0) * (Y1 - Y0) < 0.7 * full:
            img = img.crop((X0, Y0, X1, Y1))
    out.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(out)
    del view
    return str(out)


def _controls_md(rec: dict | None) -> list[str]:
    if not rec:
        return ["- (no probe record: the probe cannot reach this surface)"]
    if not rec.get("reached"):
        return [f"- (the probe could not open it: {rec.get('errors')})"]
    lines = [f"- live frame from layer {rec.get('live_floor')} (modal layers {rec.get('modal_layers')}); "
             f"{rec.get('control_count', 0)} control(s)"]
    for c in rec.get("controls") or []:
        label = (c.get("text") or c.get("meta") or "").replace("\n", " ")[:60]
        tip = f" — tooltip: \"{c.get('tooltip')[:80]}\"" if c.get("tooltip") else ""
        res = c.get("result")
        extra = ""
        if res in ("VISIBLE", "HANDOFF", "SILENT"):
            bits = []
            if c.get("changes"):
                bits.append("changed: " + "; ".join(c["changes"][:3]))
            if c.get("api_calls"):
                bits.append("api: " + ", ".join(c["api_calls"][:3]))
            if c.get("signals"):
                bits.append("signals: " + ", ".join(s[1] for s in c["signals"][:3]))
            if c.get("taken_by"):
                bits.append("a click at its centre was taken by " + str(c["taken_by"]))
            extra = (" — " + " | ".join(bits).replace("\n", " ⏎ ")) if bits else ""
        if c.get("host"):
            extra += (f" — shot alone, without the war room that hosts it, it was "
                      f"{c['alone']['result']}; {c['host']}").replace("\n", " ⏎ ")
        elif res == "DISABLED":
            extra = f" — beside it: \"{(c.get('beside') or '')[:120]}\""
        elif res == "NOT PRESSED":
            extra = f" — {c.get('why_not', '')}"
        lines.append(f"  - [{c.get('kind')}] \"{label}\" ({c.get('class')}) → **{res}**{tip}{extra}")
    return lines


def build_packets(records: pathlib.Path, index_path: pathlib.Path, packet: pathlib.Path) -> None:
    import iq10_run_captures as R
    cl = checklist()
    index = load(index_path)
    probe = host_read(load(records / "probe.json"))
    shots = {s["id"]: s for s in R.SHOTS}
    packet.mkdir(parents=True, exist_ok=True)
    (packet / "frames").mkdir(exist_ok=True)
    for i in (1, 2, 3):
        (packet / "panel_raw" / f"reader_{i}").mkdir(parents=True, exist_ok=True)
    shutil.copy2(CHECKLIST, packet / "UX_CHECKLIST_V1.json")
    (packet / "records").mkdir(exist_ok=True)
    for name in ("readability.json", "contrast.json", "consistency.json", "fit.json", "probe.json",
                 "live_citations.json", "contrast_hc_on.json"):
        if (records / name).is_file():
            shutil.copy2(records / name, packet / "records" / name)
    groups_index = []
    n = 0
    for g in cl["groups"]:
        lines = [f"# Group {g['order']} — {g['name']}", ""]
        for s in g["surfaces"]:
            n += 1
            sid, shot = s["id"], shot_of(s)
            lines.append(f"## {n}. `{sid}` — {s['surface']}")
            lines.append("")
            if shot is None:
                lines.append("- **No frame and no probe record exist** — the IQ-10 manifest has never shot "
                             "this surface. Every reader-judged item is ✗ (cannot judge from the evidence).")
                lines.append("")
                continue
            lines.append(f"- **must_show (its purpose / key action):** {shots[shot]['must_show']}")
            for res in ("1920x1080", "5120x1440"):
                r, f = _frame_for(index, shot, res)
                if f is None or not f.get("png"):
                    lines.append(f"- frame {res}: **missing** (the shoot has no frame)")
                    continue
                scale = float(r.get("scale", r.get("content_scale_factor", 1.0)))
                out = packet / "frames" / f"{sid}__{res}.png"
                try:
                    path = crop(f["png"], f, scale, out)
                    lines.append(f"- frame {res} (Interface Scale {scale:.2f}): `{path}`"
                                 + ("" if r.get("ok") else f" — the shot reported errors: {r.get('errors')}"))
                except (OSError, ValueError) as exc:
                    lines.append(f"- frame {res}: could not be read ({exc})")
            lines.append("- the other three resolutions' full frames: "
                         + ", ".join(f"`{(_frame_for(index, shot, res)[1] or {}).get('png', '?')}`"
                                     for res in ("2560x1440", "3440x1440", "3840x2160")))
            lines.append("- **the action probe (driven record) — its controls:**")
            lines.extend(_controls_md((probe.get("shots") or {}).get(shot)))
            lines.append("")
        path = packet / f"group_{g['order']:02d}_{g['key']}.md"
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        groups_index.append(f"- Group {g['order']} `{g['key']}` ({len(g['surfaces'])} surfaces): `{path}`")
    (packet / "INDEX.md").write_text("# UXR-3 reader packet\n\n" + "\n".join(groups_index) + "\n",
                                     encoding="utf-8")
    print(f"packet: {n} surfaces in {len(cl['groups'])} group files at {packet}")


# ── aggregation ─────────────────────────────────────────────────────────────

def aggregate(records: pathlib.Path, packet: pathlib.Path) -> dict:
    cl = checklist()
    inst = load(records / "instrument_marks.json")
    answers = []
    for i in (1, 2, 3):
        # each reader writes one file per group as it finishes the group, so a
        # context compaction mid-review never loses a finished group
        marks: dict = {}
        for path in sorted((packet / "panel_raw" / f"reader_{i}").glob("group_*.json")):
            a = load(path)
            marks.update((a.get("marks") if isinstance(a, dict) else None) or {})
        answers.append(marks)
    out = {"checklist": "docs/UX_CHECKLIST_V1.json", "surfaces": {}, "groups": []}
    for s in surfaces(cl):
        sid = s["id"]
        im = inst.get(sid) or {}
        row = {"group": s["group"], "group_order": s["group_order"], "top_five": s["top_five"],
               "surface": s["surface"], "shot": s["shot"], "marks": {}, "readers": {}}
        for item in READER_ITEMS:
            votes = []
            for n, a in enumerate(answers, 1):
                m = (a.get(sid) or {}).get(item)
                p = m.get("pass") if isinstance(m, dict) else None
                if p is None:
                    p = False                  # no abstaining: a missing mark is ✗
                    m = {"pass": False, "cite": "", "why": "no mark given"}
                votes.append((n, bool(p), m))
            yes = [v for v in votes if v[1]]
            no = [v for v in votes if not v[1]]
            side = yes if len(yes) >= 2 else no
            row["readers"][item] = {"pass": len(yes) >= 2, "spread": f"{len(side)}–{3 - len(side)}",
                                    "votes": [{"reader": v[0], "pass": v[1], "cite": v[2].get("cite", ""),
                                               "why": v[2].get("why", "")} for v in votes]}
        notes = [((a.get(sid) or {}).get("R4_note") or "").strip() for a in answers]
        row["r4_notes"] = [x for x in notes if x]
        for item in ITEMS:
            if item in ("R2", "R8"):
                r = row["readers"][item]
                row["marks"][item] = {"pass": r["pass"], "why": f"readers {r['spread']}", "spread": r["spread"]}
            elif item == "R5":
                auto = im.get("R5_auto") or {"pass": False, "why": "no probe record"}
                r = row["readers"]["R5"]
                if auto.get("pass") is False:
                    row["marks"]["R5"] = {"pass": False, "why": auto["why"] + f" (readers {r['spread']})",
                                          "spread": r["spread"], "auto": True}
                else:
                    row["marks"]["R5"] = {"pass": r["pass"], "why": f"readers {r['spread']}",
                                          "spread": r["spread"]}
            else:
                mk = im.get(item) or {"pass": False, "why": "no record"}
                row["marks"][item] = {"pass": bool(mk.get("pass")), "why": mk.get("why", "")}
        row["score"] = sum(1 for item in ITEMS if row["marks"][item]["pass"])
        out["surfaces"][sid] = row
    order = list(out["surfaces"])
    ranked = sorted(order, key=lambda k: (out["surfaces"][k]["score"], order.index(k)))
    out["worst_five"] = ranked[:5]
    reach = [k for k in ranked if out["surfaces"][k]["shot"] is not None]
    out["worst_five_reached"] = reach[:5]
    for g in cl["groups"]:
        ids = [s["id"] for s in g["surfaces"]]
        scores = [out["surfaces"][i]["score"] for i in ids]
        out["groups"].append({"key": g["key"], "order": g["order"], "top_five": g["top_five"],
                              "surfaces": len(ids), "mean": round(sum(scores) / len(scores), 2),
                              "min": min(scores), "eight_of_eight": sum(1 for x in scores if x == 8),
                              "under_six": sum(1 for x in scores if x < 6)})
    return out


# ── the report: the review's tables and the BUG_FIXES rows ──────────────────

ITEM_NAMES = {"R1": "Readable", "R2": "Hierarchy", "R3": "Contrast", "R4": "Consistency",
              "R5": "Affordance", "R6": "Feedback", "R7": "Fit", "R8": "Discoverability"}
# Player-visible items: P2 on a top-five surface, P3 elsewhere. R4 (a source
# census) and R6 (a missing driven proof) are P3; a SCRIPT ERROR a click
# reaches is a P1 (the checklist's "a crash or a P1 found while reading").
VISIBLE_ITEMS = {"R1", "R2", "R3", "R5", "R7", "R8"}
# The census's closing words, lowered in a row's prose so a quoted label never
# closes the row it sits in (tools/defect_census.py CLOSED / DISPOSED / PARTIAL).
_CENSUS_WORDS = ("FIXED", "CLOSED", "LANDED", "BUILT", "RULED", "DECIDED", "TAKEN", "RESOLVED",
                 "REFUTED", "STRUCK", "DUPLICATE", "WITHDRAWN", "RETIRED", "DECLINED",
                 "REPRODUCED", "CANONIZED", "SUPERSEDED", "ACCEPTED", "RE-HOMED", "PARTIAL",
                 "REMAINDER", "ROUTED", "DEFERRED")


# What the conductor verified against the source while filing a ✗ (the
# readers judged the frame; this says where the defect lives). Never a mark.
VERIFIED = {
    ("incoming_peace_losing", "R2"): (
        "Verified against the source while filing: the terms ARE rendered, under a second heading, "
        "\"Proposed Terms\", after the War Summary and below the fold; on the war-context road the "
        "\"Terms:\" header at the top (`incoming_proposal_popup.gd:95`) is left empty "
        "(`_build_peace_preview_section`)."),
}


# Where a never-shot surface's payload is already staged (S12's first fix).
GAP_STAGING = {
    "objection_dialog": ("The board exists: `tests/test_b4b_the_one_tail.py::_payloads` stages a marshal's "
                         "objection the player overrides, through the real endpoints."),
    "capture_choice": ("The board exists: the same B4b board's overridden attack takes a province, and the "
                       "backend asks Plunder or Secure (`pending_capture_choice`)."),
    "talleyrand_objection": ("The popup's payload shape is pinned in `tests/test_deep_audit_session6.py` "
                             "(the `talleyrand_objection` dict main.gd routes)."),
}


def frame_name(sid: str, res: str) -> str:
    return f"docs/audits/uxr3/frames/UXR3_{sid.upper()}_{res}.jpg"


def committed_cite(cite: str, sid: str) -> tuple[str, str]:
    """A reader's cited frame (a packet crop or a shoot frame) → the committed
    frame of that surface at the same resolution, and the resolution."""
    import re
    m = re.search(r"(\d{4})x(\d{3,4})", str(cite or ""))
    res = f"{m.group(1)}x{m.group(2)}" if m and f"{m.group(1)}x{m.group(2)}" in FIVE else "1920x1080"
    return frame_name(sid, res), res


def _safe(text: str) -> str:
    import re
    text = str(text).replace("|", "/").replace("\n", " ")
    for w in _CENSUS_WORDS:
        text = re.sub(r"\b%s\b" % re.escape(w), w.lower(), text)
    return text


def _scene(scene: str) -> str:
    return scene.rsplit("/", 1)[-1]


def _contrast_cause(sid: str, con: dict) -> tuple[frozenset, list[str]]:
    """The colours under the floor, each finding once with every resolution
    it was measured at and its worst ratio."""
    surf = (con.get("surfaces") or {}).get(sid) or {}
    colours: set = set()
    found: dict = {}
    for key, r in sorted((surf.get("readings") or {}).items()):
        for u in r.get("under") or []:
            colours.add(str(u.get("color", ""))[:6])
            k = (str(u.get("color", ""))[:8], str(u.get("path", "")), str(u.get("text", ""))[:30])
            f = found.setdefault(k, {"ratio": 99.0, "bg": u.get("bg"), "floor": u.get("floor"), "res": []})
            f["ratio"] = min(f["ratio"], float(u.get("ratio", 99.0)))
            f["res"].append(key.split("@")[0].split("x")[0])
    lines = [f"{v['ratio']} : 1 against {v['floor']} ({k[0]} on {v['bg']}, {k[1]} '{k[2]}', at "
             f"{'/'.join(v['res'])})" for k, v in sorted(found.items(), key=lambda kv: kv[1]["ratio"])]
    # the cited frame: the first resolution (in FIVE's order) any finding names
    widths = {w for v in found.values() for w in v["res"]}
    first = next((r for r in FIVE if r.split("x")[0] in widths), "1920x1080")
    lines = lines[:4] + ([f"and {len(lines) - 4} more"] if len(lines) > 4 else [])
    return frozenset(colours), lines + [f"@frame {first}"]


def _fit_cause(sid: str, fit: dict) -> tuple[frozenset, list[str]]:
    surf = (fit.get("surfaces") or {}).get(sid) or {}
    kinds, lines = set(), []
    for key, r in sorted((surf.get("readings") or {}).items()):
        for k in ("clipped_text", "truncated_text", "buttons_offscreen", "text_offscreen", "under_modal"):
            for f in r.get(k) or []:
                path = str(f.get("path", "")).split("/")[-1]
                kinds.add((k, path))
                if len(lines) < 5:
                    extra = ""
                    if k == "truncated_text":
                        extra = f" ({f.get('reason')}: {f.get('text_w', f.get('lines', ''))} > {f.get('box_w', f.get('visible_lines', ''))})"
                    elif k == "under_modal":
                        extra = f" under {str(f.get('cover', '')).split('/')[-1]} (layer {f.get('cover_layer')})"
                    lines.append(f"{key}: {k} {path} '{str(f.get('text', ''))[:40]}'{extra}")
        if not r.get("ok", True):
            kinds.add(("failed", key))
            lines.append(f"{key}: the reading failed ({'; '.join(r.get('errors') or [])[:120]})")
    return frozenset(k for k, _ in kinds), lines


def failures(records: pathlib.Path, review: dict) -> list[dict]:
    cl = checklist()
    scenes = {s["id"]: s["scene"] for s in surfaces(cl)}
    inst = load(records / "instrument_marks.json")
    con = load(records / "contrast.json")
    cen = load(records / "consistency.json")
    fit = load(records / "fit.json")
    out = []
    for sid, row in review["surfaces"].items():
        scene = _scene(scenes[sid])
        if row["shot"] is None:
            bad = [i for i in ITEMS if not row["marks"][i]["pass"]]
            out.append({"sid": sid, "items": bad, "scene": scene, "cause": ("harness_gap",),
                        "lines": [f"{i}: {row['marks'][i]['why']}" for i in bad],
                        "top_five": row["top_five"], "group_order": row["group_order"]})
            continue
        for item in ITEMS:
            m = row["marks"][item]
            if m["pass"]:
                continue
            f = {"sid": sid, "items": [item], "scene": scene, "top_five": row["top_five"],
                 "group_order": row["group_order"], "spread": m.get("spread", "")}
            if item in ("R2", "R8") or (item == "R5" and not m.get("auto")):
                votes = [v for v in row["readers"][item]["votes"] if not v["pass"]]
                f["cause"] = ("readers",)
                f["lines"] = [f"reader {v['reader']}: {v['why']}" for v in votes]
                f["cites"] = sorted({committed_cite(v.get("cite", ""), sid) for v in votes})
            elif item == "R5":
                f["cause"] = ("silent",)
                f["lines"] = [m["why"]]
            elif item == "R3":
                cause, lines = _contrast_cause(sid, con)
                f["cause"] = ("contrast", cause)
                f["lines"] = lines or [m["why"]]
            elif item == "R4":
                files = frozenset(((cen.get("surfaces") or {}).get(sid) or {}).get("by_file") or {})
                f["cause"] = ("census", files)
                f["lines"] = [m["why"]]
            elif item == "R6":
                d = (inst.get(sid) or {}).get("R6", {}).get("detail") or {}
                kinds = set()
                for label in d.get("unproven") or []:
                    kinds.add(label.split("[", 1)[-1].split(":")[0].rstrip("]"))
                if d.get("silent"):
                    kinds.add("silent")
                if d.get("errors"):
                    kinds.add("script error")
                f["cause"] = ("feedback", frozenset(kinds) or frozenset({"unreached"}))
                f["lines"] = [m["why"]]
                f["errors"] = d.get("errors") or []
            elif item == "R7":
                cause, lines = _fit_cause(sid, fit)
                f["cause"] = ("fit", cause)
                f["lines"] = lines or [m["why"]]
            else:
                f["cause"] = ("readability",)
                f["lines"] = [m["why"]]
            # the frames a row cites: the readers' own, or where the failure
            # was measured (the first resolution its record names)
            if f.get("cites"):
                f["frames"] = f["cites"]
            else:
                res = "1920x1080"
                if item in ("R1", "R3", "R7"):
                    for line in f["lines"]:
                        if line.startswith("@frame "):
                            res = line.split(" ", 1)[1]
                            break
                        hit = next((r for r in FIVE if r in line), None)
                        if hit:
                            res = hit
                            break
                f["lines"] = [x for x in f["lines"] if not x.startswith("@frame ")]
                f["frames"] = [(frame_name(sid, res), res)]
            out.append(f)
    return out


def bug_rows(fails: list[dict], start: int = 1) -> list[dict]:
    """✗s of one item with one cause on several surfaces of one scene share a
    row (the checklist's filing rule); the harness's gaps are a row each."""
    groups: dict = {}
    order = []
    for f in fails:
        key = (tuple(f["items"]), f["scene"], f["cause"])
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(f)
    rows = []
    for n, key in enumerate(sorted(order, key=lambda k: (min(x["group_order"] for x in groups[k]),
                                                       ITEMS.index(k[0][0]), k[1])), start):
        fs = groups[key]
        items = list(key[0])
        errors = [e for f in fs for e in f.get("errors") or []]
        if errors:
            sev = "P1"
        elif key[2] == ("harness_gap",):
            sev = "P3"
        elif items[0] in VISIBLE_ITEMS and any(f["top_five"] for f in fs):
            sev = "P2"
        else:
            sev = "P3"
        rows.append({"id": f"UXR3-{n}", "sev": sev, "items": items, "scene": key[1],
                     "surfaces": [f["sid"] for f in fs], "failures": fs, "errors": errors})
    return rows


def render_row(r: dict) -> str:
    items = r["items"]
    sids = r["surfaces"]
    what = ", ".join(f"{i} {ITEM_NAMES[i]}" for i in items)
    if r["failures"][0]["cause"] == ("harness_gap",):
        blind = [i for i in items if i != "R4"]
        head = (f"**`{sids[0]}` — the capture harness has never shot it, so {len(blind)} of 8 items "
                f"cannot be evidenced ({', '.join(f'{i} {ITEM_NAMES[i]}' for i in blind)})"
                + (", and R4, read off its files, fails" if "R4" in items else "") + ".**")
        fix = ("First fix: an IQ-10 shot (a staged payload and a `SHOTS` row under this id) and the action "
               "probe's record; then each item re-read. " + GAP_STAGING.get(sids[0], ""))
    else:
        head = f"**`{r['scene']}` — {what} fails on {len(sids)} surface(s).**"
        fix = ""
    body = []
    for f in r["failures"]:
        spread = f" ({f['spread']})" if f.get("spread") else ""
        frames = (" Frame: " + ", ".join(f"`{p}`" for p, _res in f.get("frames") or []) + "."
                  if f["cause"] != ("harness_gap",) and f.get("frames") else "")
        note = VERIFIED.get((f["sid"], f["items"][0]))
        body.append(f"`{f['sid']}`{spread}: " + " / ".join(_safe(x) for x in f["lines"][:4]) + "." + frames
                    + (" " + note if note else ""))
    if r["errors"]:
        body.append("SCRIPT ERROR on a click: " + _safe(r["errors"][0]))
    status = (f"OPEN — owner S12 (\"UXR-3 fixes\"); completion: {', '.join(items)} re-read ✓ on "
              + ", ".join(f"`{s}`" for s in sids)
              + f" against `docs/UX_CHECKLIST_V1.json` ⟨SF step=pre-deploy S12 · UXR-3 {sids[0] if len(sids) == 1 else r['scene']} · pillar=ui_ux⟩")
    bug = head + " " + (fix + " " if fix else "") + "<br>".join(body)
    return f"| **{r['id']}** | {r['sev']} | {status} | {_safe(bug)} |"


def render_table(review: dict) -> str:
    lines = ["| # | Surface | R1 | R2 | R3 | R4 | R5 | R6 | R7 | R8 | Score | Frame |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    n = 0
    for sid, row in review["surfaces"].items():
        n += 1
        cells = []
        for item in ITEMS:
            m = row["marks"][item]
            mark = "✓" if m["pass"] else "✗"
            if item in READER_ITEMS and m.get("spread"):
                mark += f" {m['spread']}"
            if item == "R5" and m.get("auto"):
                mark = "✗ probe"
            cells.append(mark)
        frame = f"`{frame_name(sid, '1920x1080')}`" if row["shot"] else "— (no shot)"
        lines.append(f"| {n} | `{sid}` | " + " | ".join(cells) + f" | **{row['score']}** | {frame} |")
    return "\n".join(lines)


def report(records: pathlib.Path) -> None:
    review = load(records / "review.json")
    fails = failures(records, review)
    rows = bug_rows(fails)
    (records / "bug_rows.json").write_text(json.dumps(
        [{k: v for k, v in r.items() if k != "failures"} for r in rows], indent=1, ensure_ascii=False),
        encoding="utf-8")
    (records / "bug_rows.md").write_text("\n".join(render_row(r) for r in rows) + "\n", encoding="utf-8")
    (records / "review_table.md").write_text(render_table(review) + "\n", encoding="utf-8")
    cited = {(f["sid"], res) for f in fails if f["cause"] != ("harness_gap",)
             for _path, res in (f.get("frames") or [])}
    # the review's table cites every reached surface's 1920x1080 frame too
    cited |= {(sid, "1920x1080") for sid, row in review["surfaces"].items() if row["shot"]}
    (records / "frames_to_commit.json").write_text(
        json.dumps(sorted([list(c) for c in cited]), indent=1), encoding="utf-8")
    print(f"{len(fails)} ✗ in {len(rows)} rows; {len(cited)} surfaces' frames cited")
    sev = {}
    for r in rows:
        sev[r["sev"]] = sev.get(r["sev"], 0) + 1
    print("severity:", sev)


def commit_frames(records: pathlib.Path, index_path: pathlib.Path) -> None:
    """Every frame the review and its rows cite, as a JPEG crop under
    docs/audits/uxr3/frames/ (the surface's own rects, never scaled)."""
    from PIL import Image
    index = load(index_path)
    shots = {s["id"]: s["shot"] for s in surfaces(checklist())}
    wanted = json.loads((records / "frames_to_commit.json").read_text(encoding="utf-8"))
    written = 0
    for sid, res in wanted:
        r, f = _frame_for(index, shots.get(sid) or sid, res)
        if f is None or not f.get("png"):
            print(f"  ! no frame for {sid} at {res}")
            continue
        scale = float(r.get("scale", r.get("content_scale_factor", 1.0)))
        tmp = records / "_crop.png"
        crop(f["png"], f, scale, tmp)
        out = REPO / frame_name(sid, res)
        out.parent.mkdir(parents=True, exist_ok=True)
        Image.open(tmp).convert("RGB").save(out, "JPEG", quality=85, optimize=True)
        tmp.unlink()
        written += 1
    print(f"{written} frames written to docs/audits/uxr3/frames/")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("marks", "packets", "aggregate", "report", "frames"))
    ap.add_argument("--records", required=True)
    ap.add_argument("--index", default="")
    ap.add_argument("--packet", default="")
    args = ap.parse_args(argv)
    records = pathlib.Path(args.records)
    if args.mode == "marks":
        marks = instrument_marks(records)
        (records / "instrument_marks.json").write_text(json.dumps(marks, indent=1, ensure_ascii=False),
                                                        encoding="utf-8")
        for item in ("R1", "R3", "R4", "R6", "R7"):
            ok = sum(1 for m in marks.values() if m[item]["pass"])
            print(f"{item}: {ok} of {len(marks)} ✓")
        silent = sum(1 for m in marks.values() if m["R5_auto"]["pass"] is False)
        print(f"R5 (driven half): {silent} surfaces ✗ before the readers (SILENT or unreachable)")
    elif args.mode == "packets":
        build_packets(records, pathlib.Path(args.index), pathlib.Path(args.packet))
    elif args.mode == "report":
        report(records)
    elif args.mode == "frames":
        commit_frames(records, pathlib.Path(args.index))
    else:
        review = aggregate(records, pathlib.Path(args.packet))
        (records / "review.json").write_text(json.dumps(review, indent=1, ensure_ascii=False),
                                             encoding="utf-8")
        for g in review["groups"]:
            print(f"{g['order']:2d} {g['key']:24s} n={g['surfaces']:3d} mean={g['mean']:.2f} "
                  f"min={g['min']} 8/8={g['eight_of_eight']} <6={g['under_six']}")
        print("worst five:", review["worst_five"])
        print("worst five reached:", review["worst_five_reached"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
