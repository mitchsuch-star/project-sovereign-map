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
# The whole client (every IQ-10 surface × the five resolutions): UXR-0's "exists
# for all 127 surfaces" (137 at the time of shooting). Counts + the worst two
# rows per reading; the BEFORE from the pristine worktree at 05bbee2c.
BEFORE_ALL = RECORDS / "readability_before_all_2026_10_09.json"
AFTER_ALL = RECORDS / "readability_after_all_2026_10_09.json"
# The whole-client ratchet after S1b (October 9, 2026): every remaining flag sits
# on the two ROUTED families — the diorama's tableau labels (UXR-X5) and the
# war-detail popup's computed bar tags (UXR-X6). Lower these when they fall.
ALL_RED_RATCHET = 32
ALL_P1_RATCHET = 92
ROUTED_FAMILIES = ("diorama_", "war_detail_")

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


class TestTheWholeClient:
    """UXR-0's done-when: the census exists for EVERY surface at the five
    resolutions, before and after."""

    @pytest.fixture(scope="class")
    def before_all(self) -> dict:
        return _load(BEFORE_ALL)

    @pytest.fixture(scope="class")
    def after_all(self) -> dict:
        return _load(AFTER_ALL)

    def test_every_surface_at_every_resolution_both_records(self, before_all, after_all):
        for rec in (before_all, after_all):
            assert len(rec["surfaces"]) >= 127, len(rec["surfaces"])
            for sid, surf in rec["surfaces"].items():
                keys = set(surf["readings"])
                for (w, h) in PHYSICAL_RESOLUTIONS:
                    assert any(k.startswith(f"{w}x{h}@") for k in keys), (sid, w, h)

    def test_the_before_names_its_pristine_client(self, before_all):
        assert before_all.get("client_commit") == "05bbee2c"
        assert before_all.get("physical_scale") == "1.0"

    def test_the_whole_client_moved(self, before_all, after_all):
        tb, ta = totals(before_all), totals(after_all)
        assert tb["p1"] >= 4000 and tb["red"] >= 1500, tb
        assert ta["red"] <= ALL_RED_RATCHET, (ta, "the RED count may fall, never rise")
        assert ta["p1"] <= ALL_P1_RATCHET, (ta, "the P1 count may fall, never rise")

    def test_every_remaining_flag_is_a_routed_family(self, after_all):
        """UXR-X5 / UXR-X6 own what is left; anything else is a regression."""
        strays = []
        for sid, surf in after_all["surfaces"].items():
            flagged = sum(r["counts"]["red"] + r["counts"]["p1"] for r in surf["readings"].values())
            if flagged and not sid.startswith(ROUTED_FAMILIES):
                strays.append((sid, flagged))
        assert strays == [], strays


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
