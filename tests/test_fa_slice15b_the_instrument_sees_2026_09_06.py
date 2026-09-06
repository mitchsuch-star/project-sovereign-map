"""FA slice 15 (part b) — "THE INSTRUMENT SEES".

The digest is what the whole audit was read off, and the instrument that
wrote it was blind on 22% of its turns. Rows: **FA-N79**, **FA-N86**,
**FA-N87**, **FA-77**, **FA-84** (plus the CRITICAL-rail drop found inside
it), **FA-39** and **FA-N89**.

Landing record: the boxed SLICE 15 (part b) block in `docs/BUG_FIXES.md`
§Final Whole-Game Audit.

⚠ This slice must land BEFORE the FA-D27 balance measurement, so that the
driver that measurement is taken with is the fixed one.
"""

import ast
import importlib.util
import inspect
import json
import pathlib
import textwrap

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]

_spec = importlib.util.spec_from_file_location(
    "playtest_driver_s15b", REPO / "tools" / "playtest_driver.py")
pdriver = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pdriver)


def _code_lines(source):
    """`source` with every full-line and trailing comment removed. A census
    that reads raw source is satisfied by the prose explaining the guard —
    that has now cost this build two INERT pins."""
    return "\n".join(line for line in source.split("\n")
                     if not line.lstrip().startswith("#"))


class _Recorder:
    """A minimal stand-in that borrows the real Digest's methods — which is
    exactly the shape the five real stubs use, and the shape that broke when
    a new surface reached for `self._private`."""

    def __init__(self):
        self.lines = []
        self.records = []
        self.counters = {"commands": 0, "popups": 0, "battles": 0, "turns": 0}

    def _md(self, line):
        self.lines.append(line)

    def record(self, kind, **fields):
        self.records.append({"kind": kind} | fields)

    enemy_phase = pdriver.Digest.enemy_phase
    order_progress = pdriver.Digest.order_progress
    campaign_log = pdriver.Digest.campaign_log
    dispatch = pdriver.Digest.dispatch
    ledger_line = pdriver.Digest.ledger_line


# ═══════════════════════════════════════════════════════════════════════════
# FA-N79 / FA-N86 — the fog
# ═══════════════════════════════════════════════════════════════════════════

class TestTheDigestSaysWhatItCannotSee:

    def test_a_turn_with_nothing_visible_is_no_longer_silent(self):
        """FA-N79. `enemy_phase` returned early on an empty action list, so
        the digest said NOTHING — on 12 of 40 ambient turns, two of which
        were turns Britain took a province."""
        d = _Recorder()
        d.enemy_phase([], {"fog_hidden_summary": [
            "Our scouts report activity within the borders of Britain.",
            "Our scouts report activity within the borders of Russia."]})
        assert d.lines, "the nothing-visible arm is still silent"
        assert "nothing visible" in d.lines[0]
        assert "Britain" in " ".join(d.lines)
        assert d.records[0]["fogged"] == 2

    def test_a_turn_with_nothing_visible_and_no_fog_stays_silent(self):
        """The honest boundary: no actions AND no fog means there is nothing
        to say, and the digest must not invent a line."""
        d = _Recorder()
        d.enemy_phase([], {})
        d.enemy_phase([], None)
        assert d.lines == []

    def test_the_visible_arm_carries_the_fog_sentence_too(self):
        """FA-N86. A fog sentence existed on 40 of 40 ambient turns and
        reached the digest on 0 — the enemy phase was the fogged view with
        the "there is something you cannot see" clause deleted."""
        d = _Recorder()
        d.enemy_phase(
            [{"nation": "Austria", "ai_action": {"action": "attack"},
              "message": "Mack attacks"}],
            {"fog_hidden_nations": "Britain and 5 other courts stirred as well"})
        assert "Britain and 5 other courts" in d.lines[0]

    def test_the_summary_key_wins_over_the_nations_key(self):
        """The two keys are mutually exclusive by construction, and the
        CLIENT enforces the same precedence — `enemy_phase_dialog.gd` guards
        `fog_hidden_nations` with `not has("fog_hidden_summary")`. Mirror it
        or the digest and the screen disagree."""
        assert pdriver.fog_sentences({
            "fog_hidden_summary": "the summary sentence",
            "fog_hidden_nations": "the nations sentence"}) == [
                "the summary sentence"]

    def test_the_fog_rows_are_capped(self):
        d = _Recorder()
        d.enemy_phase([], {"fog_hidden_summary": [f"court {i}" for i in range(12)]})
        printed = [ln for ln in d.lines if "fogged:" in ln]
        assert len(printed) <= pdriver.MAX_FOG_ROWS

    def test_the_client_and_the_digest_read_the_same_keys(self):
        """Drift pin. If the backend renames a fog key the client renders,
        this catches it before a digest goes quiet again."""
        gd = (REPO / "godot-client" / "project-sovereign" / "scripts"
              / "enemy_phase_dialog.gd").read_text(encoding="utf-8")
        driver_src = inspect.getsource(pdriver.fog_sentences)
        for key in ("fog_hidden_summary", "fog_hidden_nations"):
            assert key in gd, key
            assert key in driver_src, key


# ═══════════════════════════════════════════════════════════════════════════
# FA-N87 — the threat figure
# ═══════════════════════════════════════════════════════════════════════════

class TestTheLedgerLineCarriesTheThreat:

    def test_the_driver_reads_the_live_figure_first(self):
        """⚠ FA-N87 is NOT "already fixed". Slice 8 moved the read to the
        morning dispatch's `coalition_status`, and
        `_build_coalition_section` returns None below `THREAT_TENSION_MIN`
        (30) — measured, 17 of 40 LEDGER lines still print no figure, and the
        blank ones are the BACK HALF of the campaign, i.e. exactly the
        collapse the FA-D27 measurement is about.

        `GET /dispatch` is also a cached artefact (it serves the stored
        `last_morning_dispatch`), while `build_base_response` stamps a live
        `threat_level` on every POST.
        """
        src = inspect.getsource(pdriver.run)
        code = "\n".join(ln for ln in src.split("\n")
                         if not ln.strip().startswith("#"))
        i_live = code.index('response.get("threat_level")')
        i_fallback = code.index('morning.get("coalition_status")')
        assert i_live < i_fallback, (
            "the cached dispatch must be the FALLBACK, not the source")

    def test_the_backend_stamps_it_on_every_post(self):
        main = (REPO / "backend" / "main.py").read_text(encoding="utf-8")
        assert '"threat_level": int(getattr(world, \'threat_level\', 0)),' in main

    def test_a_low_threat_still_prints(self):
        """The regression that mattered: below 30 the old source is None."""
        d = _Recorder()
        d.ledger_line(100, 5, 12, provinces=3)
        assert any("threat 12" in ln for ln in d.lines)

    def test_a_genuinely_absent_threat_prints_nothing(self):
        d = _Recorder()
        d.ledger_line(100, 5, None, provinces=3)
        assert not any("threat" in ln for ln in d.lines)


# ═══════════════════════════════════════════════════════════════════════════
# FA-77 — standing-order progress
# ═══════════════════════════════════════════════════════════════════════════

class TestTheDigestFollowsAStandingOrder:

    ROWS = [
        {"marshal": "Soult", "order_status": "continues",
         "message": "Soult marches to Burgundy. 5 region(s) to Madrid."},
        {"marshal": "Ney", "order_status": "active",
         "message": "Ney is marching to Vienna (4 turn(s) remaining)."},
    ]

    def test_every_status_is_printed_not_a_chosen_few(self):
        """⚠ Dedupe, do NOT filter. The statuses that actually occur are
        `active`, `continues` and `completed`, and `continues` is 5 of 8 —
        filtering to a "named interesting set" (the shape the repro proposed)
        would delete the march narrative this exists to recover."""
        d = _Recorder()
        d.order_progress(self.ROWS)
        assert len(d.lines) == 2
        assert "[continues]" in d.lines[0] and "Burgundy" in d.lines[0]

    def test_a_repeated_row_is_printed_once(self):
        """`Answerer.scan` re-runs on drain follow-ups and the strategic
        processor re-emits a parked decision every turn."""
        d = _Recorder()
        d.order_progress(self.ROWS)
        d.order_progress(self.ROWS)
        assert len(d.lines) == 2

    def test_a_changed_message_is_a_new_row(self):
        d = _Recorder()
        d.order_progress([self.ROWS[0]])
        d.order_progress([dict(self.ROWS[0], message="Soult marches to Limousin.")])
        assert len(d.lines) == 2

    def test_it_is_sited_in_the_loop_not_in_the_answerer(self):
        """Measured over 52 driven turns: EVERY `strategic_reports` row
        arrives on the end-turn `/command` response and none on a drain
        follow-up. Both sitings produce byte-identical output; the `scan`
        site costs 20 pin failures because five stub Digests would each need
        the new method. (`/respond_to_objection` CAN carry the key —
        structurally possible, measured zero. Stated limit.)"""
        code = _code_lines(inspect.getsource(pdriver.run))
        assert "order_progress" not in inspect.getsource(pdriver.Answerer.scan)
        # ⚠ BOTH end-turn sites, not one. `run` ends the turn twice — the
        # ordinary call and the retry after a blocker refused it — and a run
        # that takes the retry path loses its ORDER rows for that turn if
        # only the first site carries the call. The sibling count is asserted
        # beside it so the invariant reads as "every end-turn tail is whole"
        # rather than as a magic 2. A first sweep of this pin came back INERT
        # against exactly that mutation.
        assert code.count("digest.order_progress(") == 2
        assert code.count("digest.autonomous_attacks(") == 2


# ═══════════════════════════════════════════════════════════════════════════
# FA-84 — the AI-vs-AI beats, and the CRITICAL rail drop found inside it
# ═══════════════════════════════════════════════════════════════════════════

class TestTheDigestSeesTheOtherPowers:

    def test_every_allowlisted_type_actually_exists(self):
        """⚠ The row's own filed allowlist names `coalition_formed`, which is
        NOT a campaign-log type. This pin is why that could not ship."""
        from backend.campaign_log import CAMPAIGN_LOG_TYPES
        unknown = sorted(pdriver.AI_AI_LOG_TYPES - set(CAMPAIGN_LOG_TYPES))
        assert not unknown, unknown

    def test_an_ai_ai_beat_reaches_the_digest(self):
        d = _Recorder()
        d.campaign_log([{"type": "ai_ai_proposal_refused",
                         "display": "Austria rebuffs Prussia"}])
        assert any("LOG ai_ai_proposal_refused" in ln for ln in d.lines)

    def test_a_type_the_rail_already_printed_is_not_said_twice(self):
        d = _Recorder()
        d.dispatch("head", events=[{"type": "design_promoted", "priority": "HIGH",
                                    "text": "REVANCHE"}])
        d.campaign_log([{"type": "design_promoted", "display": "REVANCHE"}])
        assert sum("design_promoted" in ln for ln in d.lines) == 1

    def test_the_loop_reads_the_endpoint_once_per_turn(self):
        """The behavioural sibling above proves the RENDERER; this proves the
        READ. Scoped to code lines — the comment beside the call explains the
        IGR-B eviction trap and a census over raw source would be satisfied
        by prose. A single read after the loop loses a third of a 40-turn
        campaign, so the position is asserted too, not just the presence."""
        code = _code_lines(inspect.getsource(pdriver.run))
        assert 'transport.get("/campaign_log")' in code
        assert (code.index('transport.get("/campaign_log")')
                < code.index("digest.finish(status)"))

    def test_an_unlisted_type_is_ignored(self):
        d = _Recorder()
        d.campaign_log([{"type": "battle", "display": "a battle"}])
        assert not any("LOG" in ln for ln in d.lines)


class TestTheRailNoLongerDropsTheSeverestNotices:
    """Found while building FA-84 and fixed with it: the rail filtered
    `== "HIGH"`, so it discarded every CRITICAL event. Six types can grade
    CRITICAL, and `RELIABILITY_COMMITMENTS_SPEC` §8.8.10 calls the DG-4
    call-to-arms refusals the severest diplomatic notice in the game."""

    def test_a_critical_row_is_printed(self):
        d = _Recorder()
        d.dispatch("head", events=[{"type": "call_to_arms_refused_defensive",
                                    "priority": "CRITICAL", "text": "refused"}])
        assert any("call_to_arms_refused_defensive" in ln for ln in d.lines)

    def test_critical_outranks_high_under_the_cap(self):
        """⚠ Widening the filter WITHOUT sorting is not enough:
        `diplomatic_ai_proposal` supplies 53 of the 63 HIGH rows on the
        ambient board and would evict the notices this exists to surface."""
        events = [{"type": f"diplomatic_ai_proposal_{i}", "priority": "HIGH",
                   "text": "envoy"} for i in range(pdriver.MAX_RAIL_ROWS + 2)]
        events.append({"type": "bargain_breached", "priority": "CRITICAL",
                       "text": "a compact is broken"})
        d = _Recorder()
        d.dispatch("head", events=events)
        assert any("bargain_breached" in ln for ln in d.lines)

    def test_medium_and_low_are_still_dropped(self):
        d = _Recorder()
        d.dispatch("head", events=[{"type": "intent_hardens", "priority": "LOW",
                                    "text": "chatter"},
                                   {"type": "tide", "priority": "MEDIUM",
                                    "text": "tide"}])
        assert not any("RAIL" in ln for ln in d.lines)


# ═══════════════════════════════════════════════════════════════════════════
# FA-39 / FA-N89 — provenance
# ═══════════════════════════════════════════════════════════════════════════

class TestTheRunRecordsWhoParsedItAndOnWhatBoard:

    def test_a_live_parse_is_marked(self):
        d = _Recorder()
        pdriver.Digest.command(d, "Ney, attack Mack", {
            "success": True, "message": "ok",
            "parse_mode": "anthropic", "parse_confidence": 0.62})
        assert "[anthropic 0.62]" in d.lines[0]
        assert d.records[0]["parse_mode"] == "anthropic"

    def test_a_mock_parse_leaves_the_line_unchanged(self):
        """A mock run's digest must be byte-identical to before, or every
        archived comparison breaks for nothing."""
        d = _Recorder()
        pdriver.Digest.command(d, "Ney, attack Mack", {
            "success": True, "message": "ok", "parse_mode": "mock"})
        assert d.lines[0] == "- CMD `Ney, attack Mack` → ✓ ok"

    def test_a_response_with_no_provenance_is_unchanged(self):
        d = _Recorder()
        pdriver.Digest.command(d, "status", {"success": True, "message": "ok"})
        assert d.lines[0] == "- CMD `status` → ✓ ok"

    def test_the_backend_stamps_the_players_parse_only(self):
        """⚠ `parser.parse` is called THREE times in `main.py` — the player's
        line, and twice more for the CR-5 delegation re-issues, which
        re-parse a sentence the ENGINE composed and clobber `parsed`.
        Stamping those would attribute the engine's line to the player."""
        main = (REPO / "backend" / "main.py").read_text(encoding="utf-8")
        assert main.count("_PARSE_PROVENANCE.set(") == 1
        head = main[:main.index("_PARSE_PROVENANCE.set(")]
        assert head.count("parsed = parser.parse(") == 1, (
            "the stamp is no longer on the FIRST parse")

    def test_a_real_response_carries_the_stamp(self):
        """The sibling above is a census over the SET site; the sweep proved
        it says nothing about the READ. This drives the real endpoint. Mock
        mode stamps `mock`, which the driver then deliberately does not
        render — the stamp being PRESENT is the thing under test, because
        without it a live run's digest cannot say who parsed the line."""
        import contextlib
        import io
        import os
        os.environ.setdefault(
            "INK_IRON_SAVE_DIR",
            str(pathlib.Path(os.environ.get("TEMP", "/tmp")) / "fa_s15b_saves"))
        pathlib.Path(os.environ["INK_IRON_SAVE_DIR"]).mkdir(
            parents=True, exist_ok=True)
        from fastapi.testclient import TestClient

        import backend.main as M
        from backend.commands.parser import CommandParser

        with contextlib.redirect_stdout(io.StringIO()):
            client = TestClient(M.app)
            client.post("/new_game", json={})
            M.parser = CommandParser(use_real_llm=False)
            meta_road = client.post("/command",
                                    json={"command": "status"}).json()
            order_road = client.post(
                "/command", json={"command": "Ney, fortify"}).json()
        # ⚠ BOTH roads. `status` and the refusal arms return straight through
        # `build_base_response`; only an executed order reaches
        # `_build_result_response`. The first cut of this fix stamped the
        # executor road alone and this pin is what measured it.
        for body in (meta_road, order_road):
            assert body.get("parse_mode") == "mock"
            assert "parse_confidence" in body
        # A scored parse carries a number; `status` may not be scored, and
        # the renderer guards for that. Stated rather than assumed.
        assert isinstance(order_road.get("parse_confidence"), (int, float))

    def test_the_provenance_is_display_only(self):
        """GR6. Nothing mechanical may read these keys."""
        import subprocess
        out = subprocess.run(
            ["grep", "-rn", "parse_mode\\|parse_confidence",
             "backend/", "godot-client/"],
            capture_output=True, text=True, cwd=str(REPO)).stdout
        for line in out.splitlines():
            if line.startswith("Binary file"):
                continue  # stale __pycache__, not a source reader
            assert "main.py" in line, f"a second reader appeared: {line}"

    def test_the_meta_records_the_runs_world(self):
        """FA-N89: 52 of 52 archived runs record `scenario` and `script`
        nowhere, so their board cannot be reconstructed — and slice 8's
        FA-40 then let a SCRIPT set the scenario too."""
        src = inspect.getsource(pdriver.run)
        block = src[src.index("digest = Digest(out_dir, {"):]
        block = block[:block.index("})")]
        for key in ("scenario", "script", "cheats", "strict"):
            assert f'"{key}"' in block, key

    def test_the_digest_header_reads_meta_defensively(self):
        """⚠ Two fixtures construct `Digest(tmp_path, {...five keys...})`.
        The header must not subscript a key they do not carry."""
        tree = ast.parse(textwrap.dedent(
            inspect.getsource(pdriver.Digest.__init__)))
        # ⚠ The header reads the bare parameter `meta`, not `self.meta`. A
        # first cut of this pin matched only `ast.Attribute` and was
        # therefore VACUOUS — it returned the empty set no matter what the
        # header subscripted, and the sweep caught it as INERT.
        subscripted = {
            n.slice.value for n in ast.walk(tree)
            if isinstance(n, ast.Subscript)
            and ((isinstance(n.value, ast.Attribute) and n.value.attr == "meta")
                 or (isinstance(n.value, ast.Name) and n.value.id == "meta"))
            and isinstance(n.slice, ast.Constant)}
        assert subscripted, "the walk found nothing — the pin is vacuous again"
        assert subscripted <= {"name", "seed", "llm", "transport", "policy"}, (
            f"new meta keys must be read with .get(): {subscripted}")


class TestTheDocumentationIsNoLongerFalse:

    def test_the_page_no_longer_claims_the_full_action_list(self):
        """`PLAYTESTING.md` said the jsonl `enemy_phase` record "carries the
        FULL action list". Measured: 93 of 1,185 (7.8%), and no record at all
        on 12 of 40 turns. It is the FOGGED view, which is the point of the
        instrument — but an absence in the digest is then not evidence of an
        absence on the board, and the page has to say so."""
        page = (REPO / "docs" / "PLAYTESTING.md").read_text(encoding="utf-8")
        assert "carries the FULL action list" not in page
        assert "FOGGED view" in page

    def test_the_driver_comment_no_longer_says_only_strips_new_state(self):
        src = (REPO / "tools" / "playtest_driver.py").read_text(encoding="utf-8")
        assert 'only strips new_state' not in src or 'never true' in src
