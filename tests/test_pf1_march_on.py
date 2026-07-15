"""PF-1 (Combat Overhaul Phase 6 — Parser & Play-Friction Cleanup).

"march on Tyrol" tokenizes via the bare "march" MOVE_TO keyword, leaving the
target text "on tyrol". `_clean_target_text` stripped leading articles and a
DIRECTION-word-plus-connector lead-in, but a BARE leading preposition ("on")
slipped through, so the target became the phantom "On Tyrol" (title-cased,
matching no region) instead of "Tyrol".

The fix strips a bare leading preposition in `_clean_target_text` (the single
source), so the order is labelled and resolved as "Tyrol" from parse time.
"""
import pytest

from backend.ai.strategic_parser import _clean_target_text, _classify_target


class TestStripsLeadingPreposition:
    # Inputs are lowercased (as _extract_target_text feeds them); the function
    # preserves the remaining case.
    @pytest.mark.parametrize("raw,expected", [
        ("on tyrol", "tyrol"),
        ("onto hanover", "hanover"),
        ("to belgium", "belgium"),
        ("at vienna", "vienna"),
        ("into moravia", "moravia"),
        ("for swabia", "swabia"),
        ("toward vienna", "vienna"),
        ("towards vienna", "vienna"),
    ])
    def test_bare_preposition_stripped(self, raw, expected):
        assert _clean_target_text(raw) == expected

    @pytest.mark.parametrize("raw,expected", [
        ("tyrol", "tyrol"),               # no leading preposition
        ("north", "north"),               # BARE direction preserved for resolve_direction
        ("east prussia", "east prussia"),  # cardinal-prefixed region, not a preposition
        # FALSIFIABLE NEGATIVES — the trailing \s+ anchor must prevent eating a
        # word that merely BEGINS with a preposition's letters:
        ("toulon", "toulon"),             # begins with "to"
        ("forez", "forez"),               # begins with "for"
        ("ontario", "ontario"),           # begins with "on"/"onto"
        ("atlas", "atlas"),               # begins with "at"
    ])
    def test_non_preposition_preserved(self, raw, expected):
        assert _clean_target_text(raw) == expected

    def test_directional_lead_in_still_works(self):
        # The pre-existing directional strip (direction + connector) is untouched.
        assert _clean_target_text("north to tyrol") == "tyrol"
        assert _clean_target_text("south toward vienna") == "vienna"


class _StubWorld:
    """Minimal world for _classify_target's region branch (which returns before
    touching marshals/directions)."""
    def __init__(self, regions):
        self.regions = {name: object() for name in regions}
        self.marshals = {}
        self.player_nation = "France"


def test_phantom_target_resolves_to_region():
    """End-to-end: the cleaned "on tyrol" classifies as the region Tyrol — the
    phantom "On Tyrol" (pre-fix) is gone."""
    world = _StubWorld(["Tyrol", "Bavaria"])
    cleaned = _clean_target_text("on tyrol")
    assert cleaned == "tyrol"
    result = _classify_target(cleaned, None, world)
    assert result["target"] == "Tyrol"
    assert result["target_type"] == "region"


def test_march_to_phrase_keyword_still_resolves():
    """Negative guard: "march to Tyrol" (via the "march to" phrase keyword,
    after= "tyrol") is unaffected and still resolves to the region."""
    world = _StubWorld(["Tyrol"])
    cleaned = _clean_target_text("tyrol")
    result = _classify_target(cleaned, None, world)
    assert result["target"] == "Tyrol"
    assert result["target_type"] == "region"
