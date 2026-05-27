"""G2-Slice-G2a umbrella gate test for the settlement-agency landing ledger.

`docs/SETTLEMENT_UI_CLEANUP_SPEC.md` v0.32 line 72 pins:

  The umbrella gate test
  `test_settlement_agency_landing_ledger_has_no_unowned_backlog_controls`
  (authored in G2-Slice-G2a) reads this sub-ledger plus the parent DWL
  table at spec lines 47-53 and fails when any deferred / hidden
  settlement-agency affordance lacks (a) an owning row, (b) a landing
  slice, (c) a completion definition, and (d) at least one spec-named
  behavior test in this spec.

Per CLAUDE.md golden rule 9 every hidden, cut, deferred, later, v2, or
polish player-facing affordance must name a concrete owner row, landing
slice, completion definition, STATUS tracking line, and behavior test.
This test is the doc-only enforcement floor for that contract; future
spec edits that strand a row will fail the suite before merge.

The umbrella gate does NOT require the referenced behavior tests to
exist on disk yet — many are authored by later G2 sub-slices (G2b,
G2c, G2d, G2e, G2f). It only enforces ledger well-formedness so the
landing contract for each row is a stable, machine-readable promise.
"""

from __future__ import annotations

import pathlib
import re
from typing import List

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
SPEC_PATH = REPO_ROOT / "docs" / "SETTLEMENT_UI_CLEANUP_SPEC.md"
STATUS_PATH = REPO_ROOT / "docs" / "STATUS.md"

PARENT_LEDGER_HEADER = "### Deferred Work Landing Ledger"
SUB_LEDGER_HEADER = "### SC-32 / Slice G2 Sub-Slice Ledger (v0.32)"

TEST_NAME_PATTERN = re.compile(r"\btest_[a-z][a-z0-9_]+\b")

EXPECTED_SUB_LEDGER_DECISION_IDS = ("D1", "D2", "D3", "D4a", "D4b", "D4c", "D5", "D6", "D7")
UMBRELLA_GATE_TEST_NAME = "test_settlement_agency_landing_ledger_has_no_unowned_backlog_controls"


def _read_spec() -> str:
    return SPEC_PATH.read_text(encoding="utf-8")


def _is_separator_row(cells: List[str]) -> bool:
    non_empty = [c for c in cells if c]
    if not non_empty:
        return False
    return all(set(cell) <= {"-", ":", " "} for cell in non_empty)


def _extract_table_rows(spec_text: str, header: str) -> List[List[str]]:
    """Return data rows for the markdown table immediately following `header`.

    Skips the column-header row and the dashes separator row. Stops at
    the first blank line or non-pipe line after the table body.
    """
    lines = spec_text.splitlines()
    try:
        start = next(i for i, line in enumerate(lines) if line.strip() == header)
    except StopIteration as exc:
        raise AssertionError(
            f"Spec section header not found: {header!r} in {SPEC_PATH}. "
            f"The v0.32 ledger structure may have drifted."
        ) from exc

    i = start + 1
    while i < len(lines) and not lines[i].lstrip().startswith("|"):
        i += 1

    rows: List[List[str]] = []
    saw_separator = False
    while i < len(lines):
        stripped = lines[i].strip()
        if not stripped or not stripped.startswith("|"):
            break
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if not saw_separator:
            if _is_separator_row(cells):
                saw_separator = True
        else:
            rows.append(cells)
        i += 1
    return rows


def test_settlement_agency_landing_ledger_has_no_unowned_backlog_controls():
    """G2-Slice-G2a umbrella gate.

    Every row in the parent Deferred Work Landing Ledger and the SC-32
    sub-ledger must declare (a) an owning row / decision, (b) a landing
    slice, (c) a completion definition, and (d) at least one spec-named
    behavior test (snake_case `test_<name>`).
    """
    spec_text = _read_spec()

    parent_rows = _extract_table_rows(spec_text, PARENT_LEDGER_HEADER)
    sub_rows = _extract_table_rows(spec_text, SUB_LEDGER_HEADER)

    assert parent_rows, (
        "Parent Deferred Work Landing Ledger has zero data rows. "
        f"Expected the v0.32 7-row table after {PARENT_LEDGER_HEADER!r}."
    )
    for row in parent_rows:
        assert len(row) >= 6, (
            f"Parent DWL row malformed (need >= 6 cells): {row!r}"
        )
        work, _why, owning_row, landing_slice, work_to_land, required_tests = row[:6]
        assert work, (
            f"Parent DWL row missing the deferred-work identifier (col 1): {row!r}"
        )
        assert owning_row, (
            f"Parent DWL row {work!r} has empty 'Owning row'. CLAUDE.md "
            f"golden rule 9 requires every deferred control to name an "
            f"owning spec row."
        )
        assert landing_slice, (
            f"Parent DWL row {work!r} has empty 'Landing slice'. Every "
            f"deferred control must name a concrete landing slice."
        )
        assert work_to_land, (
            f"Parent DWL row {work!r} has empty 'Work that must land' "
            f"completion definition."
        )
        named_tests = TEST_NAME_PATTERN.findall(required_tests)
        assert named_tests, (
            f"Parent DWL row {work!r} has no spec-named behavior test "
            f"(pattern test_<snake_case>). Required by golden rule 9."
        )

    assert sub_rows, (
        "SC-32 sub-ledger has zero data rows. Expected the v0.32 9-row "
        f"table after {SUB_LEDGER_HEADER!r}."
    )
    for row in sub_rows:
        assert len(row) >= 6, (
            f"SC-32 sub-ledger row malformed (need >= 6 cells): {row!r}"
        )
        decision_id, decision, outcome, landing_sub_slice, completion, required_tests = row[:6]
        assert decision_id, f"SC-32 sub-ledger row missing decision id (col 1): {row!r}"
        assert decision, (
            f"SC-32 sub-ledger row {decision_id!r} has empty 'Decision'."
        )
        assert outcome, (
            f"SC-32 sub-ledger row {decision_id!r} has empty 'Outcome'. "
            f"Every decision must record SHIP / CUT / design-lock outcome."
        )
        assert landing_sub_slice, (
            f"SC-32 sub-ledger row {decision_id!r} has empty 'Landing sub-slice'."
        )
        assert completion, (
            f"SC-32 sub-ledger row {decision_id!r} has empty 'Completion "
            f"definition'. CUT rows must record cut evidence; SHIP rows "
            f"must record what to ship."
        )
        named_tests = TEST_NAME_PATTERN.findall(required_tests)
        assert named_tests, (
            f"SC-32 sub-ledger row {decision_id!r} has no spec-named "
            f"behavior test (pattern test_<snake_case>). Required by "
            f"golden rule 9."
        )


def test_parent_dwl_ledger_pins_seven_rows_in_v032():
    """v0.32 Tier 4 amendment added one row (Slice H deferred petitions).

    The parent DWL table at spec lines 47-54 ships with exactly 7 data
    rows: SC-29, SC-30, SC-31 dependency, SC-31 surrender, SC-33, SC-32
    parent, and the new Slice H deferred-petition row. A future
    addition or removal must update this count alongside the spec edit
    so reviewers and the umbrella gate stay synchronized.
    """
    spec_text = _read_spec()
    parent_rows = _extract_table_rows(spec_text, PARENT_LEDGER_HEADER)
    assert len(parent_rows) == 7, (
        f"Parent DWL row count drifted to {len(parent_rows)}. v0.32 "
        f"expects exactly 7 rows. If the row set changed intentionally, "
        f"update this pin and the umbrella gate at the same time."
    )


def test_sc32_sub_ledger_covers_all_seven_locked_decisions():
    """Sub-ledger must include D1, D2, D3, D4a, D4b, D4c, D5, D6, D7.

    D4 splits into D4a (request_open_settlement SHIP), D4b
    (warn_against_sellout SHIP), and D4c (request_consultation +
    request_redress_after_settlement CUT). All 9 decision ids must be
    present so no SC-32 product decision is silently dropped.
    """
    spec_text = _read_spec()
    sub_rows = _extract_table_rows(spec_text, SUB_LEDGER_HEADER)
    decision_ids = tuple(row[0] for row in sub_rows)
    assert decision_ids == EXPECTED_SUB_LEDGER_DECISION_IDS, (
        f"SC-32 sub-ledger decision-id ordering drifted. Expected "
        f"{EXPECTED_SUB_LEDGER_DECISION_IDS!r}, got {decision_ids!r}. "
        f"The sub-ledger must enumerate every locked SC-32 product "
        f"decision in order."
    )


def test_sub_ledger_d5_row_pins_umbrella_gate_test_self_reference():
    """D5 (Conference / veto CUT) is owned by the umbrella gate test.

    Spec line 68 records: "test_settlement_agency_landing_ledger_has_no_unowned_backlog_controls
    (subsumes the conference/veto cut as part of the umbrella gate)."
    This pins the self-reference so a later refactor cannot strand D5
    without a behavior test of its own.
    """
    spec_text = _read_spec()
    sub_rows = _extract_table_rows(spec_text, SUB_LEDGER_HEADER)
    d5_rows = [row for row in sub_rows if row[0] == "D5"]
    assert len(d5_rows) == 1, f"Expected exactly one D5 row, got {d5_rows!r}"
    required_tests_cell = d5_rows[0][5]
    assert UMBRELLA_GATE_TEST_NAME in required_tests_cell, (
        f"D5 row must reference {UMBRELLA_GATE_TEST_NAME!r} as the "
        f"subsuming test. Found: {required_tests_cell!r}"
    )


def test_dwl_dip_conference_remains_superseded_in_status():
    """Sub-ledger D5 completion definition requires DWL-DIP-CONFERENCE
    to remain SUPERSEDED in STATUS.md.

    If a future Congress System is designed, it ships as its own spec
    with its own DWL row — never by reactivating the superseded one.
    """
    status_text = STATUS_PATH.read_text(encoding="utf-8")
    assert "DWL-DIP-CONFERENCE" in status_text, (
        "STATUS.md no longer mentions DWL-DIP-CONFERENCE. Sub-ledger D5 "
        "requires the row to remain SUPERSEDED."
    )
    pattern = re.compile(r"DWL-DIP-CONFERENCE[^\n]*?SUPERSEDED", re.IGNORECASE)
    assert pattern.search(status_text), (
        "STATUS.md DWL-DIP-CONFERENCE row is no longer marked SUPERSEDED. "
        "A new Congress System needs a new spec and a new DWL row; the "
        "superseded row must not be reactivated."
    )


def test_deferred_petition_types_have_slice_h_landing_row():
    """The v0.32 Tier 4 amendment added a dedicated parent DWL row for
    the 2 deferred ally petition types (`request_reward_or_restoration`
    + `demand_bargain_honor`) pointing at Slice H.

    The row names both deferred types, names Slice H as the landing
    slice, and pins absence-guard tests authored in G2-Slice-G2b. This
    test fails if the row is removed without an explicit cut amendment.
    """
    spec_text = _read_spec()
    parent_rows = _extract_table_rows(spec_text, PARENT_LEDGER_HEADER)
    slice_h_rows = [
        row for row in parent_rows
        if "request_reward_or_restoration" in row[0]
        and "demand_bargain_honor" in row[0]
    ]
    assert len(slice_h_rows) == 1, (
        f"Expected exactly one parent DWL row naming both deferred "
        f"petition types; got {len(slice_h_rows)}. The v0.32 Slice H "
        f"deferred-petition row was added by Tier 4 and must remain "
        f"until Slice H lands or an explicit CUT amendment supersedes it."
    )
    row = slice_h_rows[0]
    landing_slice = row[3]
    assert "Slice H" in landing_slice, (
        f"Deferred-petition DWL row must name Slice H as the landing "
        f"slice. Got: {landing_slice!r}"
    )
    required_tests = row[5]
    assert "test_petition_request_reward_or_restoration_absent_until_slice_h_lands" in required_tests, (
        "Deferred-petition DWL row must name the request_reward_or_restoration "
        "absence-guard test for G2-Slice-G2b."
    )
    assert "test_petition_demand_bargain_honor_absent_until_slice_h_lands" in required_tests, (
        "Deferred-petition DWL row must name the demand_bargain_honor "
        "absence-guard test for G2-Slice-G2b."
    )
