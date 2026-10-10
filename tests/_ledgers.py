"""The session docs as ONE text each, archives included (CODE-4, October 9, 2026).

`docs/BUG_FIXES.md`, `docs/DESIGN_REFINEMENT.md` and `docs/STATUS.md` keep
only the current quarter; everything older moved verbatim to
`docs/archive/<STEM>_<year>_Q<n>.md`, and `CLAUDE.md`'s whole 2026 "Current
Phase" record to `docs/archive/CLAUDE_CURRENT_PHASE_2026.md`. A pin that
reads one of these files for a row, a phrase or a record reads it through
here, so the move changed nothing a pin could see:

    from tests._ledgers import doc_text
    assert "UX23-R9" in doc_text("BUG_FIXES.md")
    assert "PLAYTESTING.md" in doc_text("CLAUDE.md")

The live file comes first, then the archives oldest-last, so a substring
search finds the live copy before any archived one.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DOCS = REPO / "docs"
ARCHIVE = DOCS / "archive"


def doc_paths(name: str) -> list[Path]:
    """The live doc and every quarterly archive the docs diet gave it."""
    name = name.split("/")[-1]
    if name == "CLAUDE.md":
        live = REPO / "CLAUDE.md"
        archives = [ARCHIVE / "CLAUDE_CURRENT_PHASE_2026.md"]
    else:
        live = DOCS / name
        stem = re.escape(name[:-3])
        archives = sorted(p for p in ARCHIVE.glob("*.md")
                          if re.fullmatch(stem + r"_\d{4}_Q[1-4]\.md", p.name))
    return [live] + [p for p in archives if p.exists()]


def doc_text(name: str) -> str:
    """The doc's text, live first, every archive appended after a divider."""
    parts = []
    for p in doc_paths(name):
        parts.append(p.read_text(encoding="utf-8"))
    return "\n\n<!-- archive -->\n\n".join(parts)
