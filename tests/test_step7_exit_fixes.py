"""Score Finish Step 7 (October 5, 2026) — the exit's own fixes, pinned.

The Step 7 exit read the final tree against the start reading on
`bc93ffaf` and the September 29 baseline, both with the same instrument.
Three readers were the INSTRUMENT, not the game, and the re-read of the HOLD
arm (left to "the session exit" by SF-V9's closing note) found two game
defects and a judge that could not read four honest refusals:

- **SF7-X36 — narration F1's reader** counted a turn event as the morning's
  headline: on a headless morning the driver recorded the first "text" a
  breadth-first `dig` reached ("Supply cost you 3,331 men, at Swabia.").
  The baseline read "0/40 turns without a headline" on all three commanded
  arms while its records hold 3 / 25 / 30 (the spec's own 58 of 120). The
  reader reads a classed run by the class (`score_run.THE_HEADLINE_IS_ITS_CLASS`)
  and the driver records the headline itself or `(no headline)`
  (`playtest_driver.THE_DIGEST_RECORDS_THE_HEADLINE_ITSELF`).
- **SF7-X40 — ending F2's reader** took a battle report's "The verdict of the
  field went against us" for THE VERDICT (`THE_VERDICT_IS_THE_ENDINGS_OWN`).
- **SF7-X41 — command C5's reader** expected a spend from the general retreat,
  which is free by the game's own rule (`THE_FREE_ORDER_SPENDS_NOTHING`).
- **SF7-X42 — the action pre-gate names the man and the order:** "Not enough
  actions! Need 2, have 1 — Davout cannot hold Lorraine today."
  (`executor.THE_SPENT_DAY_NAMES_THE_ORDER`).
- **SF7-X43 — a backed quarrel is a sponsorship:** "Have Talleyrand back
  Prussia's quarrel with Austria" reaches `sponsor Prussia against Austria`
  (`parser.A_BACKED_QUARREL_IS_A_SPONSORSHIP`).
- **SF7-X44 — the ONE judge reads four of the board's own refusals** (the levy
  where the corps stands, the town that holds no building, a retreat for a
  man in no danger, the design aimed at another court); every committed
  census record re-reads unchanged.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

import playtest_driver as PD  # noqa: E402
import score_run as SR  # noqa: E402


class _FakeArm:
    """The reader's view of one arm: turn blocks of jsonl records."""

    def __init__(self, records):
        self.records = records

    def kind(self, k):
        return [r for r in self.records if r.get("kind") == k]

    def by_turn(self):
        groups = []
        for r in self.records:
            if r.get("kind") == "turn":
                groups.append([r])
            elif groups:
                groups[-1].append(r)
        return groups


def _turn(t, dispatch=None):
    rows = [{"kind": "turn", "turn": t}]
    if dispatch is not None:
        rows.append({"kind": "dispatch", **dispatch})
    return rows


def _arms(per_arm):
    return {name: _FakeArm(sum(turns, [])) for name, turns in per_arm.items()}


CLASSED = [
    _turn(1, {"headline": "Sire — Bohemia has been taken by Austria.",
              "headline_class": "region_lost"}),
    # the headless morning, as the pre-fix driver recorded it: a turn event
    _turn(2, {"headline": "Supply cost you 3,331 men, at Swabia."}),
    _turn(3, {"headline": "Sire — a quiet morning on the front.",
              "headline_class": "quiet_morning"}),
]


class TestTheHeadlineIsItsClass:
    def test_a_classless_record_in_a_classed_run_is_headless(self):
        out = SR.r_narration_F1(_arms({"CMD-H": CLASSED}), {})
        assert out["measured"] and out["pass"] is False
        assert "1/3 turns without a headline" in out["evidence"]

    def test_every_morning_classed_passes(self):
        turns = [CLASSED[0], CLASSED[2]]
        out = SR.r_narration_F1(_arms({"CMD-H": turns}), {})
        assert out["pass"] is True, out["evidence"]

    def test_a_pre_sf_m_archive_keeps_the_old_reading(self):
        # no record carries a class at all: the run cannot be read by class
        turns = [_turn(1, {"headline": "Sire — Bohemia has been taken."}),
                 _turn(2, {"headline": "Supply cost you 3,331 men."})]
        out = SR.r_narration_F1(_arms({"CMD-H": turns}), {})
        assert out["pass"] is True, out["evidence"]

    def test_a_turn_with_no_dispatch_record_is_headless(self):
        turns = [CLASSED[0], _turn(2)]
        out = SR.r_narration_F1(_arms({"CMD-H": turns}), {})
        assert out["pass"] is False and "1/2" in out["evidence"]

    def test_lever_down_the_fallback_line_counts_again(self, monkeypatch):
        monkeypatch.setattr(SR, "THE_HEADLINE_IS_ITS_CLASS", False)
        out = SR.r_narration_F1(_arms({"CMD-H": CLASSED}), {})
        assert out["pass"] is True, out["evidence"]

    def test_the_baseline_archive_reads_its_own_headless_mornings(self):
        """The September 29 baseline, read by the corrected reader: the
        spec's own research counted 58 of 120 commanded turns with no
        headline; the archive's records hold 3 / 25 / 30."""
        base = REPO / "docs" / "audits" / "score_runs" / "2026_09_29_c20d5bba"
        arms = {}
        for name in ("CMD-H", "CMD-A", "CMD-M"):
            path = base / name / "digest.jsonl"
            if not path.exists():
                path = base / "arms" / name / "digest.jsonl"
            records = [json.loads(line) for line in
                       path.read_text(encoding="utf-8").splitlines() if line.strip()]
            arms[name] = _FakeArm(records)
        out = SR.r_narration_F1(arms, {})
        ev = json.loads(out["evidence"])
        assert out["pass"] is False
        assert ev["CMD-H"].startswith("3/40") and ev["CMD-A"].startswith("25/40") \
            and ev["CMD-M"].startswith("30/40"), ev


class TestTheDigestRecordsTheHeadlineItself:
    """The driver's call site: the morning's own headline text, or the plain
    word that there was none — never the first turn event the dig reached."""

    def _record(self, morning, monkeypatch, lever=True):
        # The shipped lever is read as it ships; only the lever-down arm sets it.
        if not lever:
            monkeypatch.setattr(PD, "THE_DIGEST_RECORDS_THE_HEADLINE_ITSELF", False)
        seen = {}

        class _Digest:
            def dispatch(self, text, events=None, turn_events=None, headline_class=""):
                seen["text"] = text
                seen["class"] = headline_class

        PD._record_morning_headline(_Digest(), morning)
        return seen

    def test_a_headless_morning_says_so(self, monkeypatch):
        morning = {"turn_events": [{"text": "Supply cost you 3,331 men, at Swabia."}]}
        seen = self._record(morning, monkeypatch)
        assert seen["text"] == PD.NO_HEADLINE and seen["class"] == ""

    def test_a_morning_with_a_headline_records_its_text(self, monkeypatch):
        morning = {"turn_events": [{"text": "Supply cost you 3,331 men, at Swabia."}],
                   "headline": {"class": "region_lost",
                                "text": "Sire — Bohemia has been taken by Austria."}}
        seen = self._record(morning, monkeypatch)
        assert seen["text"] == "Sire — Bohemia has been taken by Austria."
        assert seen["class"] == "region_lost"

    def test_lever_down_the_dig_returns(self, monkeypatch):
        morning = {"turn_events": [{"text": "Supply cost you 3,331 men, at Swabia."}]}
        seen = self._record(morning, monkeypatch, lever=False)
        assert seen["text"] == "Supply cost you 3,331 men, at Swabia."


class _FakeVerdictArm:
    """The Verdict arm's turn blocks, as `Arm.blocks()` reads the digest."""

    status = "ending-reached"

    def __init__(self, blocks):
        self._blocks = blocks

    def blocks(self):
        return self._blocks


VERDICT_BLOCKS = [
    (21, "- ⚔ Murat (lost 3983, own corps) vs Archduke Charles (lost 964) — "
         "The reinforcement arrived, Sire. The verdict of the field went "
         "against us regardless."),
    (44, "- ENDING — THE VERDICT OF HISTORY: The reign, unfinished, is judged "
         "as it stands. [THE ECLIPSE]"),
]


class TestTheVerdictIsTheEndingsOwn:
    """SF7-X40: a battle report's "The verdict of the field" is not the
    ending. Step 7's start reading took a turn-21 battle line for its Verdict
    and read ending F2 ✗ while the arm reached the turn-44 register."""

    def test_the_battle_line_is_not_the_verdict(self):
        out = SR.r_ending_F2({"VERDICT": _FakeVerdictArm(VERDICT_BLOCKS)}, {})
        assert out["pass"] is True and out["evidence"].startswith("Verdict at turn 44")

    def test_lever_down_the_battle_line_reads_as_the_verdict(self, monkeypatch):
        monkeypatch.setattr(SR, "THE_VERDICT_IS_THE_ENDINGS_OWN", False)
        out = SR.r_ending_F2({"VERDICT": _FakeVerdictArm(VERDICT_BLOCKS)}, {})
        assert out["pass"] is False and out["evidence"].startswith("Verdict at turn 21")

    def test_no_ending_block_is_no_verdict(self):
        out = SR.r_ending_F2({"VERDICT": _FakeVerdictArm(VERDICT_BLOCKS[:1])}, {})
        assert out["pass"] is False and "no Verdict block" in out["evidence"]

    def test_the_battle_copy_still_says_the_verdict_of_the_field(self):
        """The false match's source: if the observation bank ever drops the
        phrase, this pin says the fix's reason has gone with it."""
        src = (REPO / "backend" / "game_logic" / "battle_report.py").read_text(encoding="utf-8")
        assert "The verdict of the field went against us" in src


class _FakeTypedArm:
    """The TYPED arm's command blocks, as `_cmd_blocks` reads the digest."""

    def __init__(self, md):
        self.md = md
        self.records = []

    def blocks(self):
        import re
        out = []
        for m in re.finditer(r"\n## Turn (\d+)[^\n]*\n(.*?)(?=\n## Turn \d+|\Z)", self.md, re.S):
            out.append((int(m.group(1)), m.group(2)))
        return out

    def kind(self, k):
        return []


def _typed(turn_lines, end_unused):
    md = "# Playtest digest — TYPED\n\n## Turn 9 — Late January 1806\n"
    for text, ok, reply in turn_lines:
        md += f"- CMD `{text}` → {'✓' if ok else '✗'} {reply}\n"
    md += f"- CMD `end turn` → ✓ Turn 9 ended. (Warning: {end_unused} actions unused) Turn 10 begins!\n"
    return _FakeTypedArm(md)


SCRIPT = {"turns": {"9": ["quickly attack Mack", "ok retreat", "end turn"]}}


class TestTheFreeOrderSpendsNothing:
    """SF7-X41: the general retreat is free by the game's own rule (FA-R3),
    so a turn whose only carried order is a retreat spends nothing and is
    right to. Step 7's start and final trees carried `ok retreat` on
    typed_road's turn 9 (the attacks refused out of range) and read C5 ✗."""

    def test_a_carried_retreat_alone_expects_no_spend(self):
        arm = _typed([("quickly attack Mack", False, "No marshals in range of Mack"),
                      ("ok retreat", True, "General retreat ordered! Ney falling back!")], 4)
        out = SR.r_command_C5({"TYPED": arm}, {"typed_script": SCRIPT})
        assert out["pass"] is True, out["evidence"]

    def test_a_carried_attack_that_spent_nothing_still_fails(self):
        arm = _typed([("quickly attack Mack", True, "MUSTER — Murat (21,552) vs Mack"),
                      ("ok retreat", False, "No marshals are in danger.")], 4)
        out = SR.r_command_C5({"TYPED": arm}, {"typed_script": SCRIPT})
        assert out["pass"] is False and "1 orders carried out, nothing spent" in out["evidence"]

    def test_lever_down_the_retreat_reads_as_a_missed_spend(self, monkeypatch):
        monkeypatch.setattr(SR, "THE_FREE_ORDER_SPENDS_NOTHING", False)
        arm = _typed([("quickly attack Mack", False, "No marshals in range of Mack"),
                      ("ok retreat", True, "General retreat ordered! Ney falling back!")], 4)
        out = SR.r_command_C5({"TYPED": arm}, {"typed_script": SCRIPT})
        assert out["pass"] is False

    def test_the_general_retreat_is_free_in_the_game(self, monkeypatch):
        """The reader's premise, read off the game: an unaddressed retreat
        carried out through the real parser and executor spends no action
        (FA-R3). If the game ever charges it, this pin says the reader's
        exemption has lost its reason."""
        import contextlib
        import io
        monkeypatch.setenv("LLM_MODE", "mock")
        from backend.commands.executor import CommandExecutor
        from backend.commands.parser import CommandParser
        from backend.models.world_state import WorldState
        with contextlib.redirect_stdout(io.StringIO()):
            world = WorldState()
            executor, parser = CommandExecutor(), CommandParser()
        game_state = {"world": world}
        ney, wellington = world.get_marshal("Ney"), world.get_marshal("Wellington")
        ney.location = wellington.location = "Waterloo"
        ney.strength, wellington.strength = 20000, 60000
        before = world.actions_remaining
        with contextlib.redirect_stdout(io.StringIO()):
            result = executor.execute(parser.parse("ok retreat", game_state), game_state)
        assert result.get("success") is True and "General retreat ordered" in result["message"]
        assert world.actions_remaining == before


# ── SF7-X42: the spent day names the order ──────────────────────────────
class TestTheSpentDayNamesTheOrder:
    """SF7-X42: "Not enough actions! Need 2, have 1." named neither the man
    nor the order — five of the HOLD arm's misses (SF-V9). The sentence's
    head is unchanged; the order rides behind it. Driven at POST /command on
    the 1805 boot."""

    def _post(self, monkeypatch, line, actions=4, admin=2):
        import contextlib
        import io
        monkeypatch.setenv("LLM_MODE", "mock")
        from fastapi.testclient import TestClient
        with contextlib.redirect_stdout(io.StringIO()):
            import backend.main as M
        world = _world_1805()
        world.actions_remaining = actions
        world.admin_actions_remaining = admin
        monkeypatch.setattr(M, "world", world)
        monkeypatch.setitem(M.game_state, "world", world)
        with contextlib.redirect_stdout(io.StringIO()):
            return TestClient(M.app).post("/command", json={"command": line}).json()

    def test_a_standing_order_names_the_man_and_the_place(self, monkeypatch):
        r = self._post(monkeypatch, "Davout, hold Lorraine", actions=1)
        assert r["success"] is False
        assert r["message"] == "Not enough actions! Need 2, have 1 — Davout cannot hold Lorraine today."

    def test_a_pursuit_names_the_quarry(self, monkeypatch):
        r = self._post(monkeypatch, "Ney, pursue Mack", actions=1)
        assert r["message"] == "Not enough actions! Need 2, have 1 — Ney cannot pursue Mack today."

    def test_a_days_order_names_the_man(self, monkeypatch):
        r = self._post(monkeypatch, "Bernadotte, fortify", actions=0)
        assert r["message"] == "Not enough actions! Need 1, have 0 — Bernadotte cannot fortify today."

    def test_the_target_is_the_boards_own_name(self, monkeypatch):
        """The HOLD arm's own line: the parse's target runs on ("Milan For The
        Next Three Turns"); the sentence names the province."""
        r = self._post(monkeypatch, "Massena, stay in Milan and hold it for the next three turns.", actions=1)
        assert r["message"] == "Not enough actions! Need 2, have 1 — Massena cannot hold Milan today."

    def test_an_administrative_order_names_the_man(self, monkeypatch):
        r = self._post(monkeypatch, "Soult, recruit infantry", actions=2, admin=0)
        assert r["message"] == ("No administrative actions remaining this turn. (Military commands: "
                                "2 remaining) Soult cannot raise his levy today.")

    def test_lever_down_the_old_sentences_return(self, monkeypatch):
        from backend.commands import executor as EX
        monkeypatch.setattr(EX, "THE_SPENT_DAY_NAMES_THE_ORDER", False)
        assert self._post(monkeypatch, "Davout, hold Lorraine", actions=1)["message"] ==             "Not enough actions! Need 2, have 1."
        assert self._post(monkeypatch, "Soult, recruit infantry", actions=2, admin=0)["message"] ==             "No administrative actions remaining this turn. (Military commands: 2 remaining)"

    def test_an_order_naming_no_man_of_ours_keeps_the_old_sentence(self):
        world = _world_1805()
        from backend.commands.executor import spent_day_sentence
        assert spent_day_sentence(world, {"action": "attack", "target": "Mack"}, {}) == ""
        assert spent_day_sentence(world, {"action": "attack", "marshal": "Mack"}, {}) == ""


# ── SF7-X43: a backed quarrel is a sponsorship ──────────────────────────
def _world_1805():
    import contextlib
    import io
    from backend.models.world_state import WorldState
    scenario = REPO / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
    with contextlib.redirect_stdout(io.StringIO()):
        return WorldState.from_scenario(str(scenario))


class TestABackedQuarrelIsASponsorship:
    """SF7-X43: "Have Talleyrand back Prussia's quarrel with Austria - a couple
    of hundred gold a turn" answered "Sire, I await your instructions regarding
    Prussia" — the HOLD arm's one blind order SF-V9's worklist left unread."""

    def test_the_idiom_is_the_sponsorship_verb(self):
        from backend.commands.parser import rewrite_plain_attack_forms
        world = _world_1805()
        text, changed = rewrite_plain_attack_forms(
            "Have Talleyrand back Prussia's quarrel with Austria - a couple of hundred gold a turn.",
            {"world": world})
        assert changed is True
        assert text == "sponsor Prussia against Austria - a couple of hundred gold a turn."

    def test_its_family(self):
        from backend.commands.parser import rewrite_plain_attack_forms
        world = _world_1805()
        for line, expected in (
                ("Talleyrand, fund Russia's cause against Sweden, 300 gold",
                 "sponsor Russia against Sweden, 300 gold"),
                ("bankroll Prussia's claim on Hanover", "sponsor Prussia against Hanover"),
                ("back the Ottoman Empire's grievance with Russia",
                 "sponsor Ottoman against Russia")):
            text, changed = rewrite_plain_attack_forms(line, {"world": world})
            assert changed and text == expected, (line, text)

    def test_a_name_no_court_carries_is_left_alone(self):
        from backend.commands.parser import rewrite_plain_attack_forms
        world = _world_1805()
        for line in ("back Ney's quarrel with Mack", "back Prussia's quarrel with Zorglub",
                     "back Prussia's quarrel with Prussia"):
            text, changed = rewrite_plain_attack_forms(line, {"world": world})
            assert not changed and text == line, (line, text)

    def test_lever_down_the_idiom_is_untouched(self, monkeypatch):
        from backend.commands import parser as P
        monkeypatch.setattr(P, "A_BACKED_QUARREL_IS_A_SPONSORSHIP", False)
        world = _world_1805()
        line = "Have Talleyrand back Prussia's quarrel with Austria"
        text, _changed = P.rewrite_plain_attack_forms(line, {"world": world})
        assert text == line

    def test_driven_the_verb_answers_for_the_design(self, monkeypatch):
        """At POST /command on the 1805 boot: the idiom reaches the verb, which
        prices it — granted against Hanover (Prussia's own design), refused
        against Austria with the reason named."""
        import contextlib
        import io
        monkeypatch.setenv("LLM_MODE", "mock")
        from fastapi.testclient import TestClient
        with contextlib.redirect_stdout(io.StringIO()):
            import backend.main as M
        world = _world_1805()
        monkeypatch.setattr(M, "world", world)
        monkeypatch.setitem(M.game_state, "world", world)
        client = TestClient(M.app)
        with contextlib.redirect_stdout(io.StringIO()):
            refused = client.post("/command", json={
                "command": "Have Talleyrand back Prussia's quarrel with Austria"}).json()
            granted = client.post("/command", json={
                "command": "back Prussia's quarrel with Hanover"}).json()
        assert refused["success"] is False and "aimed at Hanover" in refused["message"], refused["message"]
        assert granted["success"] is True, granted["message"]
        assert "sponsors Prussia's design against Hanover" in granted["message"], granted["message"]


# ── SF7-X44: the judge reads four of the board's own refusals ──────────
class TestTheJudgeReadsTheBoardsRefusals:
    """SF7-X44: the HOLD arm, re-read at the exit (SF-V9's closing note left
    it to "the session exit"), carried four honest board refusals the ONE
    judge could not read."""

    def test_the_four_refusals_are_board_gates(self):
        import _score_probes as judge
        for msg in (
                "Davout stands at Swabia, Sire — a corps raises its levy where it stands, not at Rhineland.",
                "Cannot build in Franche-Comte — town regions don't support buildings (need city or larger)",
                "Ney is not in danger. No retreat necessary.",
                "Talleyrand: \"Prussia's design is aimed at Hanover, not Austria. "
                "We can only arm the grievance they already hold.\""):
            assert judge.BOARD_GATE_RX.search(msg), msg

    def test_the_rural_refusal_stays_as_the_committed_census_read_it(self):
        """The fresh census record holds one "rural regions don't support
        buildings" read `as_meant`; the town refusal is matched by its own
        words so that record re-reads unchanged."""
        import _score_probes as judge
        assert not judge.BOARD_GATE_RX.search(
            "Cannot build in Burgundy — rural regions don't support buildings (need city or larger)")

    def test_every_committed_census_record_re_reads_unchanged(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "census_x44", REPO / "tools" / "unrehearsed_census.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        records = sorted((REPO / "docs" / "audits" / "unrehearsed").glob("*.json"))
        assert records
        for path in records:
            rec = json.loads(path.read_text(encoding="utf-8"))
            committed = json.dumps(rec["totals"], sort_keys=True)
            again = mod.reclassify(json.loads(path.read_text(encoding="utf-8")))
            assert json.dumps(again["totals"], sort_keys=True) == committed, path.name
