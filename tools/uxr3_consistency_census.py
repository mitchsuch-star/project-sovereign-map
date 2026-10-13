"""UXR-3 R4 "Consistency" — the census (Pre-Deploy S11, October 13, 2026).

    .venv/Scripts/python.exe -X utf8 tools/uxr3_consistency_census.py <run>/index.json \
        [--record docs/audits/uxr3/consistency_<label>.json]

R4's frozen rule (`docs/UX_CHECKLIST_V1.json`): ✓ iff the census finds 0 hits
in the surface's own files. A hit is

  (a) a ONE-OFF SIZE — a raw font-size override exactly as
      `tests/test_uxr2_override_diet.py::raw_sites` counts it (the RAW_RATCHET
      census, its named exemptions included), or a BBCode `[font_size=` in
      script code;
  (b) a ONE-OFF GREY — a colour in `Utils.is_dim`'s class (chroma <= 0.12 and
      0.15 <= luminance <= luminance(UI_TEXT_DIM) + 0.02, luminance =
      0.2126 r + 0.7152 g + 0.0722 b on the authored values) written as a
      literal and not routed through Utils.toned / toned_hex / the COLOR
      tokens: in script code a numeric `Color(r, g, b[, a])`, a hex in
      `Color("…")` / `Color.html("…")`, a `[color=…]` hex, a bare 6- or
      8-digit hex string, or a named Godot grey, outside any `toned(` /
      `toned_hex(` call; in a scene, a `theme_override_colors/*`, `modulate`
      or `self_modulate` value that is not a step of `Utils.DIM_LADDER`
      (±1/255 per channel).

The surface's own files are the scene files and scripts (with their base
scripts) of every node visible in its frames and of their ancestors, plus the
shot's own scene and root script — the capture harness records them per frame
(`files`). Never `scripts/utils.gd` (the palette's home), `scripts/ui_settings.gd`,
the theme, `tools/**` or the engine's built-ins. A surface with no frame (the
three the manifest never shot) is read statically: its scene, the scripts that
scene attaches, and their bases.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
PROJECT = REPO / "godot-client" / "project-sovereign"
CHECKLIST = REPO / "docs" / "UX_CHECKLIST_V1.json"
sys.path.insert(0, str(REPO))

from tests import _godot_scenes as G  # noqa: E402 — the ONE scene/script reader
from tests.test_uxr2_override_diet import raw_sites  # noqa: E402 — the RAW_RATCHET census itself

EXCLUDED = {"res://scripts/utils.gd", "res://scripts/ui_settings.gd"}
UI_TEXT_DIM = (0.75, 0.72, 0.65)
DIM_LADDER = [(0.4, 0.4, 0.4392), (0.502, 0.502, 0.502), (0.6275, 0.6275, 0.6588),
              UI_TEXT_DIM, (0.8667, 0.8392, 0.7843)]
LADDER_TOL = 1.0 / 255.0 + 1e-9
# Godot's named colours that are greys (value per the engine's color_names).
NAMED = {
    "GRAY": (0.745098, 0.745098, 0.745098), "DIM_GRAY": (0.411765, 0.411765, 0.411765),
    "DARK_GRAY": (0.662745, 0.662745, 0.662745), "LIGHT_GRAY": (0.827451, 0.827451, 0.827451),
    "SILVER": (0.752941, 0.752941, 0.752941), "WEB_GRAY": (0.501961, 0.501961, 0.501961),
    "SLATE_GRAY": (0.439216, 0.501961, 0.564706), "LIGHT_SLATE_GRAY": (0.466667, 0.533333, 0.6),
    "DARK_SLATE_GRAY": (0.184314, 0.309804, 0.309804), "GAINSBORO": (0.862745, 0.862745, 0.862745),
}

_NUM = r"([0-9]*\.?[0-9]+)"
RE_COLOR_NUM = re.compile(r"(?<![\w.])Color\(\s*%s\s*,\s*%s\s*,\s*%s\s*(?:,\s*%s\s*)?\)" % (_NUM, _NUM, _NUM, _NUM))
RE_COLOR_HEX = re.compile(r'(?<![\w.])Color(?:\.html|\.from_string)?\(\s*"#?([0-9A-Fa-f]{6}(?:[0-9A-Fa-f]{2})?)"')
RE_BB_HEX = re.compile(r"\[color=#?([0-9A-Fa-f]{6}(?:[0-9A-Fa-f]{2})?)\]")
RE_BARE_HEX = re.compile(r'"#?([0-9A-Fa-f]{6}(?:[0-9A-Fa-f]{2})?)"')
RE_NAMED = re.compile(r"(?<![\w.])Color\.(%s)\b" % "|".join(NAMED))
RE_FONT_SIZE_BB = re.compile(r"\[font_size=")
RE_SCENE_COLOR = re.compile(
    r"^(theme_override_colors/\w+|modulate|self_modulate) = Color\(\s*%s\s*,\s*%s\s*,\s*%s\s*(?:,\s*%s\s*)?\)"
    % (_NUM, _NUM, _NUM, _NUM), re.M)
RE_EXT_SCRIPT = re.compile(r'\[ext_resource[^\]]*type="Script"[^\]]*path="(res://[^"]+)"')
RE_EXTENDS_PATH = re.compile(r'(?m)^extends\s+"(res://[^"]+)"')
RE_EXTENDS_CLASS = re.compile(r"(?m)^extends\s+(\w+)")
RE_CLASS_NAME = re.compile(r"(?m)^class_name\s+(\w+)")


def luminance(rgb) -> float:
    r, g, b = rgb
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


DIM_TOP = luminance(UI_TEXT_DIM) + 0.02


def is_dim(rgb) -> bool:
    chroma = max(rgb) - min(rgb)
    lum = luminance(rgb)
    return chroma <= 0.12 and 0.15 <= lum <= DIM_TOP


def on_ladder(rgb) -> bool:
    return any(all(abs(a - b) <= LADDER_TOL for a, b in zip(rgb, step)) for step in DIM_LADDER)


def _hex_rgb(h: str):
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


def _routed_spans(code: str) -> list[tuple[int, int]]:
    """The argument spans of every toned( / toned_hex( call — a literal inside
    one is routed through the High-contrast tone."""
    spans = []
    for m in re.finditer(r"(?<!\w)toned(?:_hex)?\(", code):
        depth, i, quote = 1, m.end(), None
        while depth and i < len(code):
            ch = code[i]
            if quote:
                if ch == "\\":
                    i += 1
                elif ch == quote:
                    quote = None
            elif ch in "\"'":
                quote = ch
            elif ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
            i += 1
        spans.append((m.end(), i))
    return spans


def _source_line(text: str, code: str, pos: int, snippet: str) -> int:
    """The SOURCE line of a hit found in the comment-stripped copy: the k-th
    occurrence of the same snippet in the source, where k counts the ones
    before it in the copy (comments drop whole lines, never a code token)."""
    k = code.count(snippet, 0, pos)
    at = -1
    for _ in range(k + 1):
        at = text.find(snippet, at + 1)
        if at < 0:
            return code.count("\n", 0, pos) + 1
    return text.count("\n", 0, at) + 1


def script_hits(path: str, text: str) -> list[dict]:
    hits: list[dict] = []
    name = pathlib.Path(path).name
    for args in raw_sites(name, text):
        hits.append({"file": path, "kind": "size", "what": "raw font-size override",
                     "snippet": (", ".join(args) if isinstance(args, list) else str(args))[:80]})
    code = G.code_lines(text)
    text = text.replace("\r\n", "\n")
    for m in RE_FONT_SIZE_BB.finditer(code):
        hits.append({"file": path, "kind": "size", "what": "BBCode [font_size=",
                     "line": _source_line(text, code, m.start(), m.group(0)),
                     "snippet": code[m.start():m.start() + 24]})
    spans = _routed_spans(code)
    seen: set[int] = set()

    def routed(pos: int) -> bool:
        return any(a <= pos < b for a, b in spans)

    def add(pos: int, m: re.Match, rgb, what: str) -> None:
        """`pos` keys the literal (one literal, one hit); the match `m` locates
        it in the source (comments drop whole lines, never a code token)."""
        if pos in seen:
            return
        seen.add(pos)
        if is_dim(rgb) and not routed(pos):
            hits.append({"file": path, "kind": "grey", "what": what,
                         "line": _source_line(text, code, m.start(), m.group(0)),
                         "value": "%02x%02x%02x" % tuple(int(round(c * 255)) for c in rgb),
                         "snippet": m.group(0)[:80]})

    for m in RE_COLOR_NUM.finditer(code):
        rgb = tuple(float(m.group(i)) for i in (1, 2, 3))
        if max(rgb) > 1.0:
            continue                      # Color8-style ints are not this form
        add(m.start(), m, rgb, "Color(r, g, b) literal")
    # One literal, one hit: every hex form is keyed by where its digits start.
    for m in RE_COLOR_HEX.finditer(code):
        add(m.start(1), m, _hex_rgb(m.group(1)), "Color(\"hex\") literal")
    for m in RE_BB_HEX.finditer(code):
        add(m.start(1), m, _hex_rgb(m.group(1)), "[color=hex] literal")
    for m in RE_BARE_HEX.finditer(code):
        add(m.start(1), m, _hex_rgb(m.group(1)), "bare hex string")
    for m in RE_NAMED.finditer(code):
        add(m.start(), m, NAMED[m.group(1)], "named Godot grey")
    return hits


def scene_hits(path: str, text: str) -> list[dict]:
    hits: list[dict] = []
    name = pathlib.Path(path).name
    for _site in raw_sites(name, text):
        hits.append({"file": path, "kind": "size", "what": "raw font-size override (scene)"})
    for m in RE_SCENE_COLOR.finditer(text):
        rgb = tuple(float(m.group(i)) for i in (2, 3, 4))
        if is_dim(rgb) and not on_ladder(rgb):
            hits.append({"file": path, "kind": "grey", "what": f"scene {m.group(1)} off the dim ladder",
                         "line": text.count("\n", 0, m.start()) + 1,
                         "value": "%02x%02x%02x" % tuple(int(round(c * 255)) for c in rgb),
                         "snippet": m.group(0)[:80]})
    return hits


def res_path(res: str) -> pathlib.Path:
    return PROJECT / res.replace("res://", "")


def _class_index() -> dict:
    out = {}
    for p in G.client_scripts():
        m = RE_CLASS_NAME.search(G.read(p))
        if m:
            out[m.group(1)] = "res://" + p.relative_to(PROJECT).as_posix()
    return out


def base_chain(script: str, classes: dict) -> list[str]:
    """A script and the project scripts it extends (by path or class_name)."""
    out, cur = [], script
    while cur and cur not in out:
        out.append(cur)
        p = res_path(cur)
        if not p.is_file():
            break
        text = G.read(p)
        m = RE_EXTENDS_PATH.search(text)
        if m:
            cur = m.group(1)
            continue
        m = RE_EXTENDS_CLASS.search(text)
        cur = classes.get(m.group(1)) if m else None
    return out


def static_files(scene: str, classes: dict) -> list[str]:
    files = [scene]
    p = res_path(scene)
    if p.is_file():
        for script in RE_EXT_SCRIPT.findall(G.read(p)):
            files.extend(base_chain(script, classes))
    return sorted(set(files))


def own(files) -> list[str]:
    return sorted({f for f in files
                   if f.startswith("res://") and not f.startswith("res://../")
                   and f not in EXCLUDED and (f.endswith(".gd") or f.endswith(".tscn"))})


def census_file(res: str, cache: dict) -> list[dict]:
    if res not in cache:
        p = res_path(res)
        if not p.is_file():
            cache[res] = [{"file": res, "kind": "missing", "what": "file not found"}]
        else:
            text = G.read(p)
            cache[res] = scene_hits(res, text) if res.endswith(".tscn") else script_hits(res, text)
    return cache[res]


def surface_files(index_path: pathlib.Path | None) -> dict:
    """{shot id: set(files)} — the union over every frame the run shot."""
    out: dict = {}
    if index_path is None:
        return out
    index = json.loads(index_path.read_text(encoding="utf-8"))
    for row in index.get("rows", []):
        base = str(row.get("base_id") or row.get("id"))
        for res in row.get("results", []):
            for f in (res.get("frames") or []):
                out.setdefault(base, set()).update(f.get("files") or [])
    return out


def run(index_path: pathlib.Path | None) -> dict:
    checklist = json.loads(CHECKLIST.read_text(encoding="utf-8"))
    classes = _class_index()
    frames = surface_files(index_path)
    cache: dict = {}
    record = {"rule": "docs/UX_CHECKLIST_V1.json R4", "source": str(index_path or ""),
              "excluded": sorted(EXCLUDED) + ["the theme .tres", "tools/**"], "surfaces": {}, "files": {}}
    for group in checklist["groups"]:
        for s in group["surfaces"]:
            # §113.1: a surface the checklist names with no shot is read under
            # its own id once the manifest shoots it (S12, UXR3-56 … 58).
            sid, shot = s["id"], s["shot"] or s["id"]
            if shot is not None and frames.get(shot):
                files = own(frames[shot])
                road = "frames"
            else:
                files = own(static_files(s["scene"], classes))
                road = "static (no frame)"
            hits = []
            for f in files:
                hits.extend(census_file(f, cache))
            sizes = [h for h in hits if h["kind"] == "size"]
            greys = [h for h in hits if h["kind"] == "grey"]
            record["surfaces"][sid] = {
                "road": road, "files": files, "pass": not hits,
                "size_hits": len(sizes), "grey_hits": len(greys),
                "by_file": {f: len(census_file(f, cache)) for f in files if census_file(f, cache)},
            }
    record["files"] = {f: h for f, h in sorted(cache.items()) if h}
    return record


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("index", nargs="?", default="")
    ap.add_argument("--record", default="")
    args = ap.parse_args(argv)
    record = run(pathlib.Path(args.index) if args.index else None)
    surfaces = record["surfaces"]
    passed = sum(1 for s in surfaces.values() if s["pass"])
    print(f"R4 census: {passed} of {len(surfaces)} surfaces with 0 hits; "
          f"{len(record['files'])} files carry hits")
    for f, hits in record["files"].items():
        kinds = {}
        for h in hits:
            kinds[h["kind"]] = kinds.get(h["kind"], 0) + 1
        print(f"  {f}: {kinds}")
    if args.record:
        p = pathlib.Path(args.record)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(record, indent=1, ensure_ascii=False), encoding="utf-8")
        print("record:", p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
