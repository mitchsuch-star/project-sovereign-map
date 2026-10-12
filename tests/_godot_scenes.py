"""The client's scenes and scripts, read as text — the ONE parser the layout
censuses share (UXR-2, Pre-Deploy S9, October 12, 2026).

`node_block`, `panel_anchor` and `centre_anchored_surfaces` moved here verbatim
from `tests/test_ui_visual_foundation.py` (which re-imports them under their old
underscore names), so the clamp pins and UXR-2's censuses derive their surface
sets one way. The full-tree parser (`parse_tscn`) adds what those helpers never
needed: every node's path, type, parent and property block, so a census can
walk a node's WHOLE ancestor chain (the PC15-18 wheel census reads only the
direct parent).

Import as `from tests import _godot_scenes as G` (`tests/` is not a package;
pytest's rootdir puts the repo on the path, the `_chip_census` idiom).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
GODOT_PROJ = REPO / "godot-client" / "project-sovereign"
SCENES_DIR = GODOT_PROJ / "scenes"
SCRIPTS_DIR = GODOT_PROJ / "scripts"
THEME = GODOT_PROJ / "ui" / "main_theme.tres"


def read(path: Path) -> str:
    return Path(path).read_text(encoding="utf-8").replace("\r\n", "\n")


# ── moved verbatim from test_ui_visual_foundation.py ──────────────────────

def node_block(src: str, node_name: str) -> str:
    """The property block of a single [node name="X" ...] declaration."""
    match = re.search(
        r'^\[node name="%s"[^\]]*\]\n(.*?)(?=^\[node |\Z)' % re.escape(node_name),
        src, re.M | re.S)
    assert match, f"node {node_name!r} not found"
    return match.group(1)


def panel_anchor(scene_src: str):
    """(anchor_left, anchor_right) of the root PanelContainer, or None."""
    try:
        block = node_block(scene_src, "PanelContainer")
    except AssertionError:
        return None
    left = re.search(r"^anchor_left = ([\d.]+)", block, re.M)
    right = re.search(r"^anchor_right = ([\d.]+)", block, re.M)
    if not left or not right:
        return None
    return float(left.group(1)), float(right.group(1))


def centre_anchored_surfaces():
    """Derived, not hand-maintained. A hand-written list silently under-covers:
    the first version named 12 of the 22 scripts the sweep actually touched, so
    a refactor could drop the clamp from any of the other 10 unnoticed."""
    out = []
    for scene in sorted(SCENES_DIR.glob("*.tscn")):
        anchors = panel_anchor(read(scene))
        if anchors == (0.5, 0.5) and (
                GODOT_PROJ / "scripts" / f"{scene.stem}.gd").exists():
            out.append(scene.stem)
    return out


# ── the full tree ──────────────────────────────────────────────────────────

_HEADER = re.compile(r'^\[node (?P<attrs>[^\]]*)\]\s*$', re.M)
_ATTR = re.compile(r'(\w+)=("(?:[^"\\]|\\.)*"|\S+)')


@dataclass
class Node:
    name: str
    type: str            # "" for an instanced sub-scene (it names no type)
    parent: str | None   # None for the scene's root; "." for the root's children
    path: str            # "" for the root; "A/B/C" below it
    props: dict = field(default_factory=dict)
    block: str = ""


def parse_tscn(text: str) -> list:
    """Every node of a .tscn, in file order, with its path and properties."""
    text = text.replace("\r\n", "\n")
    heads = list(_HEADER.finditer(text))
    nodes = []
    for i, m in enumerate(heads):
        attrs = {k: v.strip('"') for k, v in _ATTR.findall(m.group("attrs"))}
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        # a block ends at the next node OR the next [connection]/[editable] section
        block = re.split(r"(?m)^\[(?!node )", text[m.end():end], maxsplit=1)[0]
        props = {}
        for line in block.split("\n"):
            if " = " in line and not line.startswith((" ", "\t")):
                k, v = line.split(" = ", 1)
                props[k.strip()] = v.strip()
        parent = attrs.get("parent")
        name = attrs.get("name", "")
        if parent is None:
            path = ""
        elif parent == ".":
            path = name
        else:
            path = f"{parent}/{name}"
        nodes.append(Node(name, attrs.get("type", ""), parent, path, props, block))
    return nodes


def by_path(nodes: list) -> dict:
    return {n.path: n for n in nodes}


def ancestors(nodes: list, path: str) -> list:
    """The node's ancestors, nearest first, ending at the scene root."""
    index = by_path(nodes)
    out = []
    while path:
        path = path.rsplit("/", 1)[0] if "/" in path else ""
        if path in index:
            out.append(index[path])
    return out


def func_body(src: str, name: str) -> str:
    """One GDScript function's text, from its `func` line to the next top-level
    `func` / `static func` (a static func ends a body too)."""
    m = re.search(r"(?m)^(static )?func %s\(" % re.escape(name), src)
    assert m, f"func {name} is gone"
    rest = src[m.end():]
    nxt = re.search(r"(?m)^(static )?func ", rest)
    return src[m.start():m.end() + (nxt.start() if nxt else len(rest))]


def code_lines(src: str) -> str:
    """The script with whole-line comments and docstring-only lines dropped,
    so a census counts code, not prose about code."""
    out, in_doc = [], False
    for line in src.replace("\r\n", "\n").split("\n"):
        s = line.strip()
        if in_doc:
            if s.endswith('"""'):
                in_doc = False
            continue
        if s.startswith('"""'):
            if not (len(s) > 3 and s.endswith('"""')):
                in_doc = True
            continue
        if s.startswith("#"):
            continue
        out.append(line.split(" #", 1)[0] if '"' not in line else line)
    return "\n".join(out)


def call_args(src: str, func: str) -> list:
    """Every call of `func(` in `src` (not its definition), split into its
    top-level arguments — bracket- and string-aware, since an argument like
    `c.get("name", "")` carries its own commas."""
    calls = []
    for m in re.finditer(r"(?<!\w)%s\(" % re.escape(func), src):
        if src[max(0, m.start() - 5):m.start()] == "func ":
            continue
        depth, i, start, args, quote = 1, m.end(), m.end(), [], None
        while depth and i < len(src):
            ch = src[i]
            if quote:
                if ch == "\\":
                    i += 1
                elif ch == quote:
                    quote = None
            elif ch in "\"'":
                quote = ch
            elif ch in "([{":
                depth += 1
            elif ch in ")]}":
                depth -= 1
            elif ch == "," and depth == 1:
                args.append(src[start:i].strip())
                start = i + 1
            i += 1
        args.append(src[start:i - 1].strip())
        calls.append(args)
    return calls


def theme_variations(theme_text: str) -> dict:
    """{variation: {"base_type": T, "sizes": {key: n}, "other": [keys]}} for
    every type the project theme declares a `base_type` for."""
    out: dict = {}
    for line in theme_text.split("\n"):
        m = re.match(r'^(\w+)/base_type = &"(\w+)"$', line)
        if m:
            out.setdefault(m.group(1), {"sizes": {}, "other": []})["base_type"] = m.group(2)
    for line in theme_text.split("\n"):
        m = re.match(r"^(\w+)/(\w+)/(\w+) = (.+)$", line)
        if not m or m.group(1) not in out:
            continue
        name, kind, key, value = m.groups()
        if kind == "font_sizes":
            out[name]["sizes"][key] = int(value)
        else:
            out[name]["other"].append(f"{kind}/{key}")
    return out


def client_scripts() -> list:
    return sorted(list(SCRIPTS_DIR.glob("*.gd")) + list(SCENES_DIR.glob("*.gd")))


def client_scenes() -> list:
    return sorted(SCENES_DIR.glob("*.tscn"))
