"""UXR-0 "The readability instrument" — the pins on the COMMITTED census records
(October 9, 2026). These run on the records under `docs/audits/uxr0/`, never on
Godot; the instrument (`tools/iq10_run_captures.py --physical` → the harness's
text census → `tools/uxr0_readability_report.py --record`) wrote them.

The done-when of UXR-1 (`docs/UX_UI_REVIEW_PLAN.md`): 0 RED rows on the tutorial,
the dispatch, the terminal, the top bar and the Generals screen at every one of
the five resolutions with the auto-derived scale, and 0 P1 anywhere. The RED
count over the whole named set is a RATCHET: it may fall, never rise.
"""
from __future__ import annotations

import json
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
RECORDS = REPO / "docs" / "audits" / "uxr0"
BEFORE = RECORDS / "readability_before_named_2026_10_09.json"
AFTER = RECORDS / "readability_after_named_2026_10_09.json"

sys.path.insert(0, str(REPO / "tools"))
from uxr0_readability_report import PHYSICAL_RESOLUTIONS, classify, derive_ui_scale, totals  # noqa: E402

# The five named surfaces of the done-when, by the ids the census groups on.
NAMED = {
    "tutorial": ("tutorial_card", "war_room_tutorial"),
    "dispatch": ("dispatch_boot_today", "dispatch_t20"),
    "terminal": ("war_room_boot",),
    "top bar": ("top_bar_boot",),
    "Generals": ("generals_boot",),
}
# The RED ratchet over the whole named set (eleven surfaces × five resolutions)
# at the derived scales — the value the AFTER record was committed with.
RED_RATCHET = 0


def _load(path: pathlib.Path) -> dict:
    assert path.is_file(), f"the committed record is missing: {path}"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def before() -> dict:
    return _load(BEFORE)


@pytest.fixture(scope="module")
def after() -> dict:
    return _load(AFTER)


class TestTheRecordsExist:
    def test_both_records_cover_the_named_surfaces_at_every_resolution(self, before, after):
        for rec in (before, after):
            for ids in NAMED.values():
                for sid in ids:
                    surf = rec["surfaces"].get(sid)
                    assert surf is not None, sid
                    keys = set(surf["readings"])
                    for (w, h) in PHYSICAL_RESOLUTIONS:
                        assert any(k.startswith(f"{w}x{h}@") for k in keys), (sid, w, h, keys)

    def test_the_before_is_the_shipped_default_and_the_after_the_derivation(self, before, after):
        for surf in before["surfaces"].values():
            for key, r in surf["readings"].items():
                assert r["scale"] == 1.0, (key, r["scale"])
        for surf in after["surfaces"].values():
            for key, r in surf["readings"].items():
                w, h = r["window"]
                assert r["scale"] == pytest.approx(derive_ui_scale(w, h), abs=1e-6), (key, r["scale"])

    def test_every_reading_rendered(self, before, after):
        for rec in (before, after):
            for sid, surf in rec["surfaces"].items():
                for key, r in surf["readings"].items():
                    assert r["ok"], (sid, key)
                    assert r["counts"]["rows"] > 0, (sid, key)


class TestTheDoneWhen:
    @pytest.mark.parametrize("surface", sorted(NAMED))
    def test_zero_red_on_the_named_surface_at_every_resolution(self, after, surface):
        for sid in NAMED[surface]:
            for key, r in after["surfaces"][sid]["readings"].items():
                assert r["counts"]["red"] == 0, (surface, sid, key, r["flagged"][:3])
                assert r["counts"]["p1"] == 0, (surface, sid, key, r["flagged"][:3])

    def test_no_p1_anywhere_after(self, after):
        t = totals(after)
        assert t["p1"] == 0, t

    def test_the_red_ratchet(self, after):
        t = totals(after)
        assert t["red"] <= RED_RATCHET, (t, "the RED count may fall, never rise — "
                                        "lower RED_RATCHET when it falls")

    def test_the_before_picture_was_really_red(self, before):
        """The instrument saw what the user reported: at the shipped 1.0 the
        tutor card's body (13 px — exactly the P1 line, so RED) and the
        terminal's output (11 px, P1) were flagged on every monitor."""
        t = totals(before)
        assert t["p1"] >= 500 and t["red"] >= 100, t
        tut = before["surfaces"]["war_room_tutorial"]["readings"]
        for key, r in tut.items():
            paths = {f["path"].split("/")[-1]: f for f in r["flagged"]}
            body = paths.get("BodyText", {})
            assert body.get("verdict") == "red" and body.get("em") == 13.0, (key, body)
            out = paths.get("OutputDisplay", {})
            assert out.get("verdict") == "p1" and out.get("em") == 11.0, (key, out)


class TestTheFloorIsOneRule:
    def test_classify_reads_the_tiers(self):
        assert classify({"em_px": 15.9, "tier": "body"}) == "red"
        assert classify({"em_px": 16.0, "tier": "body"}) == "ok"
        assert classify({"em_px": 12.9, "tier": "body"}) == "p1"
        assert classify({"em_px": 13.9, "tier": "caption"}) == "red"
        assert classify({"em_px": 14.0, "tier": "caption"}) == "ok"
        assert classify({"em_px": 11.9, "tier": "caption"}) == "p1"
        assert classify({"em_px": 6.0, "tier": "map"}) == "map"

    def test_the_map_tier_is_counted_beside_the_floor(self, after):
        """The world-space furniture (UXR-X4) is reported, never scored."""
        war = after["surfaces"]["war_room_boot"]["readings"]
        assert any(r["counts"]["map"] > 0 for r in war.values())
        for r in war.values():
            for f in r["flagged"]:
                assert "/MapViewport/" not in f["path"], f
