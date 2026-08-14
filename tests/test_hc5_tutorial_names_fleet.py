"""HC-5 "The School Names the Fleet" (gate §6) — tutorial honesty.

Step XIV ("The Instruments") names, in Berthier's voice, the surfaces
landed after July 17 that the School of War never taught: THE ADMIRALTY
(ledger book 7), the F1 wizard incl. the Formables button, the Generals
card's Reward chip, and the ledger's Design rows. Honest pointers, not
new lessons — the R159 self-teaching screens carry the depth; NO new
suggest chip (the tutorial world has no navy authored, so a naval chip
would be a dishonest pointer — T-B1 would rightly refuse it).

"The Congress" second lesson is NOT built here — it stays a named
candidate on the Pre-EA Onboarding & Teaching Pass row.

Source-string pins, the TestOverlayLivenessPins pattern.
"""

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OVERLAY = (REPO / "godot-client" / "project-sovereign" / "scripts"
           / "tutorial_overlay.gd")


def _step_xiv_entry() -> str:
    """The free_books STEPS entry, scraped from the .gd source."""
    source = OVERLAY.read_text(encoding="utf-8")
    match = re.search(
        r'"id":\s*"free_books".*?"advance"', source, re.DOTALL)
    assert match, "step XIV (free_books) is gone from the STEPS table"
    return match.group(0)


class TestStepXIVSurfaceList:
    """The gate's four named surfaces, pinned as source strings."""

    def test_names_the_admiralty(self):
        entry = _step_xiv_entry()
        assert "THE ADMIRALTY" in entry
        assert "seventh book" in entry

    def test_names_the_wizard_and_formables(self):
        entry = _step_xiv_entry()
        assert "F1" in entry
        assert "Formable Nations" in entry

    def test_names_the_reward_chip(self):
        assert "Reward" in _step_xiv_entry()

    def test_names_the_design_rows(self):
        assert "Design rows" in _step_xiv_entry()

    def test_keeps_the_original_four_screens(self):
        # The extension is additive — T/G/D/R stay named.
        entry = _step_xiv_entry()
        for token in ("Strategic Ledger", "Generals",
                      "courts of Europe", "morning dispatch"):
            assert token in entry, token

    def test_no_new_suggest_chip(self):
        # The safer HC-5 shape: honest pointers only. A chip would need
        # the tutorial world to parse it (no navy is authored there).
        entry = _step_xiv_entry()
        assert re.search(r'"suggest":\s*""', entry)
        assert re.search(r'"suggest_action":\s*""', entry)

    def test_doc_row_updated(self):
        doc = (REPO / "docs" / "TUTORIAL_SCRIPT.md").read_text(
            encoding="utf-8")
        assert "HC-5" in doc
        assert "THE ADMIRALTY" in doc
