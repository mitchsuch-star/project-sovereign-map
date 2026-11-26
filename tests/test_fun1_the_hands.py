"""Row FUN, FUN-1 "the hands" (November 25, 2026) — the real-window probe.

The user's second play: "when I click on generals the line goes crazy if I move
the mouse around" and "clicks aren't accurate on ultrawide". The review
(`docs/GAMEPLAY_REVIEW_2026_11_25.md` §1.1–§1.2) found no constant pixel
offset — but every driver had injected clicks already divided by the Interface
Scale (`push_input(ev, true)`), so no test had clicked the way a real mouse
does. And it found the cursor promising one thing while the click did another:
Mack's name plate named Mack and the click opened Rhineland; a Bernadotte stack
with Bavaria's Deroy in front opened the Bavaria panel; with a corps selected
the line vanished over every piece.

This probe drives the REAL client through `tools/dd_b_client.gd`'s window-road
verbs (`whover`, `wclick`: window pixels through `Input.parse_input_event`) at
the first player's own setup (5120x1377 at Interface Scale 1.8) and at the
small window (1920x1080 at 1.0), and holds one rule: **what the box under the
cursor names is what the click does**; and, with a corps selected, the line
never blanks over a target it has a road to, and the tag names what the click
will do. It SKIPS without the engine (a skip is not a pass).
"""
from __future__ import annotations

import json

import pytest

from tests.test_dd_b_the_client_hands import (
    _act,
    _answer_chain,
    _start_engine_run,
    _stop_engine_run,
)

SETUPS = {
    "players_setup": ("1.8", "5120x1377", (2844, 765)),
    "small_window": ("1.0", "1920x1080", (1920, 1080)),
}


def _center(p: dict) -> tuple:
    return int(p["center"][0]), int(p["center"][1])


def _inside(r, x, y) -> bool:
    return r[0] <= x < r[0] + r[2] and r[1] <= y < r[1] + r[3]


def _clear_point(state: dict, target: dict, strict: bool = False):
    """A point of `target`'s own rect that no box the map asks FIRST covers —
    for a figure no other figure; for a plate or a fog chip no figure and no
    other plate (on the 1805 board Murat's stack plate lies over half of
    Mack's fog chip, and a click there is the plate's) — nearest its centre;
    its centre when every point is covered (None when `strict`)."""
    others = [p["rect"] for p in state.get("pieces") or []
              if p is not target and (p["kind"] == "piece"
                                      or (target["kind"] != "piece" and p["kind"] == "plate"))]
    x0, y0, w, h = target["rect"]
    cx, cy = x0 + w / 2, y0 + h / 2
    pts = sorted(((x0 + dx, y0 + dy) for dx in range(2, max(3, int(w) - 1), 3)
                  for dy in range(2, max(3, int(h) - 1), 3)),
                 key=lambda pt: (pt[0] - cx) ** 2 + (pt[1] - cy) ** 2)
    for x, y in pts:
        if not any(_inside(r, x, y) for r in others):
            return int(x), int(y)
    return None if strict else _center(target)


def _find(state: dict, kind: str, name: str):
    for p in state.get("pieces") or []:
        if p.get("kind") == kind and p.get("name") == name:
            return p
    return None


def _own(state: dict) -> set:
    return set((state.get("click") or {}).get("own") or [])


def _touching(a: dict, b: dict) -> bool:
    ax, ay, aw, ah = a["rect"]
    bx, by, bw, bh = b["rect"]
    return (ax - 2 <= bx + bw and bx - 2 <= ax + aw
            and ay - 2 <= by + bh and by - 2 <= ay + ah)


def _neighbours(state: dict):
    """One of OUR figures and another court's standing against it — the
    Bernadotte/Deroy stack of the 1805 board (side by side, edge to edge)."""
    own = _own(state)
    figures = [p for p in state.get("pieces") or [] if p.get("kind") == "piece"]
    for a in figures:
        if a["name"] not in own:
            continue
        for b in figures:
            if b["name"] not in own and _touching(a, b):
                return a, b
    return None


def _enemy(state: dict, name: str):
    return _find(state, "piece", name) or _find(state, "fog", name)


def _place(state: dict, province: str):
    for row in state.get("map") or []:
        if str(row.get("kind", "")).startswith("place") \
                and str(row.get("text", "")).strip().lower() == province.lower():
            r = row["rect"]
            return int(r[0] + r[2] / 2), int(r[1] + r[3] / 2)
    return None


def _beside(state: dict, target: dict):
    """A point 4 px outside `target`'s rect that no piece or plate covers —
    ground beside an enemy, where a click is the province's (PW-R19)."""
    rects = [p["rect"] for p in state.get("pieces") or [] if p.get("kind") in ("piece", "plate", "fog")]
    x0, y0, w, h = target["rect"]
    for x, y in ((x0 - 4, y0 + h / 2), (x0 + w + 4, y0 + h / 2), (x0 + w / 2, y0 - 4),
                 (x0 + w / 2, y0 + h + 4)):
        if not any(_inside(r, x, y) for r in rects):
            return int(x), int(y)
    return None


def _clear(run, state: dict) -> dict:
    """Let go of whatever the last click opened — Esc only while something
    stands (a bare Esc opens the pause menu), up to three times (a card over a
    selection takes two), and the menu shut if it rose."""
    for _ in range(3):
        click = state.get("click") or {}
        if not any(click.get(k) for k in ("selected", "panel", "card", "picker")):
            break
        state = _act(run, "key Escape")
    if "pause" in json.dumps(state.get("open") or {}).lower():
        state = _act(run, "key Escape")
    return state


def _agreement(probe: dict) -> str:
    """'' when the click did what the box named, else the plain mismatch."""
    hover = probe.get("hover") or {}
    click = probe.get("click") or {}
    own = set(click.get("own") or [])
    regions = {p["name"]: p.get("region", "") for p in probe.get("pieces") or []
               if p.get("kind") in ("piece", "fog")}
    named = hover.get("marshal") or hover.get("fogged") or ""
    stack = hover.get("stack") or []
    if not (named or hover.get("region")):
        # (the review, lane C: every probe aims at a piece, a plate or a
        # province — an empty hover is the record failing, never agreement)
        return f"{probe['label']}: the box named nothing (hover record {hover!r})"
    if named and len(stack) >= 2 and named in stack:
        # a stack's plate stands for all of them: its click asks "which of them"
        if click.get("picker"):
            return ""
        return (f"{probe['label']}: the box named the stack {stack}; the click opened no "
                f"pick-list (selected {click.get('selected')!r}, opened {click.get('panel')!r})")
    if named:
        if named in own and hover.get("marshal"):
            if click.get("selected") == named:
                return ""
            return (f"{probe['label']}: the box named {named} (ours); the click selected "
                    f"{click.get('selected')!r} and opened {click.get('panel')!r}")
        where = regions.get(named, "")
        if where and click.get("panel") == where:
            return ""
        return (f"{probe['label']}: the box named {named}, who stands in {where!r}; "
                f"the click opened {click.get('panel')!r}")
    if hover.get("region"):
        if click.get("panel") == hover["region"]:
            return ""
        return (f"{probe['label']}: the box named {hover['region']}; the click opened "
                f"{click.get('panel')!r} and selected {click.get('selected')!r}")
    return ""   # open water: nothing promised, nothing owed


@pytest.fixture(scope="module", params=sorted(SETUPS))
def hands(request, tmp_path_factory) -> dict:
    scale, window, _logical = SETUPS[request.param]
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("DD_B_UI_SCALE", scale)
        mp.setenv("DD_B_WINDOW", window)
        run, sup = _start_engine_run(tmp_path_factory, f"fun1_{request.param}")
    rec: dict = {"setup": request.param, "probes": [], "orders": []}
    try:
        state = _act(run, "click Begin the 1805 Campaign")
        state = _answer_chain(run, state, [])
        rec["board"] = state
        probes = []
        for name in ("Soult", "Massena"):
            fig = _find(state, "piece", name)
            if fig:
                probes.append((f"{name}'s figure", _clear_point(state, fig)))
        mack_plate = _find(state, "plate", "Mack")
        if mack_plate:
            probes.append(("Mack's name plate", _clear_point(state, mack_plate)))
        mack = _enemy(state, "Mack")
        if mack:
            probes.append(("Mack's figure", _clear_point(state, mack)))
        pair = _neighbours(state)
        rec["neighbours"] = [pair[0]["name"], pair[1]["name"]] if pair else []
        if pair:
            probes.append((f"{pair[1]['name']}'s figure beside {pair[0]['name']}", _clear_point(state, pair[1])))
            probes.append((f"{pair[0]['name']}'s figure beside {pair[1]['name']}", _clear_point(state, pair[0])))
        for province in ("Bavaria", "Austria", "Hesse"):
            at = _place(state, province)
            if at:
                probes.append((f"{province}'s name", at))
        rec["let_go"] = []
        for label, (x, y) in probes:
            hover = _act(run, f"whover {x} {y}")
            click = _act(run, f"wclick {x} {y}")
            rec["probes"].append({"label": label, "at": [x, y], "hover": hover.get("hover"),
                                  "click": click.get("click"), "pieces": click.get("pieces")})
            after = _clear(run, click)
            if (click.get("click") or {}).get("selected"):
                rec["let_go"].append({"label": label, "hover": after.get("hover"), "click": after.get("click")})
        # With Soult selected: the line and its tag over each kind of target.
        soult = _find(state, "piece", "Soult")
        if soult:
            sx, sy = _clear_point(state, soult)
            picked = _act(run, f"wclick {sx} {sy}")
            rec["selected"] = (picked.get("click") or {}).get("selected")
            targets = []
            if mack:
                targets.append(("an enemy", _clear_point(state, mack)))
            massena = _find(state, "piece", "Massena")
            if massena:
                targets.append(("one of ours", _clear_point(state, massena)))
            targets.append(("himself", (sx, sy)))
            for province in ("Bavaria", "Hesse"):
                at = _place(state, province)
                if at:
                    targets.append((f"{province}'s name", at))
                    targets.append((f"21 px right of {province}'s name", (at[0] + 21, at[1])))
            west = _place(state, "France")
            if west:
                targets.append(("west of him, France's name", west))
            if mack:
                beside = _beside(state, mack)
                if beside:
                    targets.append(("ground beside an enemy", beside))
            for label, (x, y) in targets:
                seen = _act(run, f"whover {x} {y}")
                rec["orders"].append({"label": label, "at": [x, y], "hover": seen.get("hover")})
            # the RIGHT button on an enemy: his attack card (FUN1-9's fog chip names
            # him). Aimed from the board as it stands NOW — with a corps selected
            # the label layer moves plates clear of the order's marks, so the boot
            # layout's clear point can lie under a plate by then.
            if mack:
                now = _act(run, "look")
                mack_now = _enemy(now, "Mack") or mack
                aim = _clear_point(now, mack_now, strict=True)
                if aim is None:
                    rec["right_on_enemy"] = {"covered": True}
                else:
                    mx, my = aim
                    seen = _act(run, f"whover {mx} {my}")
                    card = _act(run, f"wrclick {mx} {my}")
                    rec["right_on_enemy"] = {"hover": seen.get("hover") or {}, "click": card.get("click") or {}}
                    _act(run, "key Escape")   # the card shuts; the selection stays
            _clear(run, _act(run, "look"))
    finally:
        _stop_engine_run(run, sup)
    rec["run"] = json.loads((run / "run.json").read_text(encoding="utf-8"))
    return rec


class TestFUN1TheHands:

    def test_the_run_stands_at_its_setup(self, hands):
        board = hands["board"]
        _scale, window, logical = SETUPS[hands["setup"]]
        assert board["factor"]["physical_size"] == [int(v) for v in window.split("x")]
        got = board["factor"]["logical_size"]
        assert [round(float(got[0])), round(float(got[1]))] == list(logical), got
        assert hands["run"]["n_script_errors"] == 0, hands["run"]["script_errors"]

    def test_the_probe_found_its_targets(self, hands):
        labels = [p["label"] for p in hands["probes"]]
        musts = ["Soult's figure"]
        if hands["setup"] == "players_setup":
            musts += ["Mack's name plate", "Bavaria's name"]
            assert hands["neighbours"], "the 1805 board's Bernadotte/Deroy stack was not found"
        for must in musts:
            assert must in labels, labels

    def test_what_the_box_names_is_what_the_click_does(self, hands):
        """FUN1-1, FUN1-2: by a real mouse's road, every probe's click does what
        its box named — our corps selected, anyone else's (a plate, a fog chip,
        an ally's figure beside ours) the province HE stands in, a province's
        own window opened."""
        wrong = [w for w in (_agreement(p) for p in hands["probes"]) if w]
        assert wrong == [], "\n".join(wrong)

    def test_a_courts_figure_beside_ours_opens_his_province_not_the_one_under_it(self, hands):
        """FUN1-2: Bernadotte and Bavaria's Deroy stand edge to edge in
        Franconia; a click on Deroy opened the Bavaria panel (the colour under
        the cursor). The box names Deroy, so the click opens Franconia."""
        if not hands["neighbours"]:
            pytest.skip("no court's figure stands beside ours on this board at this window")
        ours, theirs = hands["neighbours"]
        probe = next(p for p in hands["probes"] if p["label"].startswith(f"{theirs}'s figure"))
        assert (probe["hover"] or {}).get("marshal") == theirs, probe["hover"]
        stands = next(p.get("region") for p in probe["pieces"] if p["name"] == theirs and p["kind"] == "piece")
        assert (probe["click"] or {}).get("panel") == stands, (probe["click"], stands)
        mine = next(p for p in hands["probes"] if p["label"].startswith(f"{ours}'s figure"))
        assert (mine["click"] or {}).get("selected") == ours, mine["click"]

    def test_letting_go_takes_the_tag_with_it(self, hands):
        """FUN1-10 (found by this probe's first green run): "Let Soult go" stood
        on the map after Esc had let him go."""
        assert hands["let_go"], "no probe selected a corps of ours"
        for row in hands["let_go"]:
            assert not (row["click"] or {}).get("selected"), row
            assert (row["hover"] or {}).get("lone_tag", "") == "", row

    def test_the_line_never_blanks_and_its_tag_names_the_click(self, hands):
        """FUN1-3, FUN1-4: with a corps selected, a target with a road always
        shows it (an enemy his attack road at once), one of ours says it will be
        selected, the corps himself says the click lets him go."""
        assert hands.get("selected") == "Soult", hands.get("selected")
        rows = {o["label"]: (o["hover"] or {}) for o in hands["orders"]}
        enemy = rows.get("an enemy")
        if enemy is not None:
            # his attack road at once — or, where no road reaches him, a tag saying why
            assert enemy.get("road_points", 0) >= 2 or enemy.get("lone_tag", ""), enemy
            if enemy.get("road_points", 0) >= 2:
                assert enemy.get("road_kind") == "attack", enemy
        ours = rows.get("one of ours")
        if ours is not None:
            assert ours.get("lone_tag", "").startswith("Select "), ours
            assert ours.get("road_points", 0) == 0, ours
        himself = rows["himself"]
        assert himself.get("lone_tag", "").startswith("Let "), himself
        # FUN1-4: the tag stands EAST of a road heading west, where there is room
        west = rows.get("west of him, France's name")
        if west is not None and west.get("road_points", 0) >= 2:
            assert west.get("badge_west") is False, west
        # PW-R19 kept: ground beside an enemy is the province's, never an attack
        beside = rows.get("ground beside an enemy")
        if beside is not None:
            assert beside.get("region") and not beside.get("fogged") and not beside.get("marshal"), beside
        for label, row in rows.items():
            if "name" not in label:
                continue
            named_ours = row.get("marshal") and row.get("lone_tag", "").startswith("Select ")
            if row.get("region") or row.get("marshal") and not named_ours:
                assert row.get("road_points", 0) >= 2 or row.get("lone_tag", ""), (label, row)

    def test_the_right_button_on_an_enemy_opens_his_attack_card(self, hands):
        """FUN1-1, FUN1-9: the right click reads what the box names — Mack,
        a fog chip at the 1805 boot — and opens the card of the attack on him."""
        got = hands.get("right_on_enemy")
        if got is None:
            pytest.skip("no enemy piece on this board at this window")
        if got.get("covered"):
            # at this window every point of his chip lies under a plate: the
            # plate is what a click there touches (and the box names it)
            pytest.skip("Mack's chip is wholly covered by name plates at this window")
        hover, click = got["hover"], got["click"]
        named = hover.get("marshal") or hover.get("fogged")
        assert named == "Mack", hover          # aimed where no plate covers his chip now
        assert click.get("card") == "enemy:Mack", click
