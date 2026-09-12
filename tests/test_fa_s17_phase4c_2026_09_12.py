"""FA slice 17, Phase 4 part C (September 12, 2026) — the design rulings.

Four of the seven open items are BUILT here; three are declined on the
record (D1 with its measurement, D2 to EC-2 pass 2, D7 to the FA-D27
balance owner). Each build sits behind a lever whose False arm reproduces
the prior behaviour.

  FA-S17-D3 (narration half) a war declared ON US names its cause
  FA-S17-D6 (half 2) the driver stops breaking a peace nobody scripted
  FA-S17-D8 the band where the mechanic BITES announces itself
  FA-S17-D9 the orphan popup is retired, and the doc stops naming it
"""
from __future__ import annotations

import contextlib
import io
import json
import re
from pathlib import Path

from backend.game_logic import dispatch as DSP
from backend.game_logic import vassal as VS
from tests.conftest import WorldFactory

ROOT = next(p for p in (Path(__file__).resolve().parents[1], Path.cwd())
            if (p / "backend").is_dir())
GD = ROOT / "godot-client" / "project-sovereign"


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


def _code_only(path: Path) -> str:
    """A file's source with every ``#`` comment removed.

    Used by the census pins below, because a grep over the raw file matches
    the comments that EXPLAIN a guard — so a pin written that way stays
    green when the guard itself is deleted, which is exactly how the first
    cut of this pin passed. String LITERALS are deliberately kept: a
    dictionary key like ``state["courted_turn"] = ...`` is the very write a
    row-key census has to be able to see, and stripping strings would make
    every such census vacuous by construction. Docstrings therefore survive
    too, so a census identifier must be one no prose would use.
    """
    import tokenize
    out = []
    with open(path, "rb") as fh:
        for tok in tokenize.tokenize(fh.readline):
            if tok.type == tokenize.COMMENT:
                continue
            out.append(tok.string)
    return " ".join(out)


# ═══════════════════════════════════════════════════════════════════════
# FA-S17-D3 — the declaration names its cause
# ═══════════════════════════════════════════════════════════════════════
class TestTheDeclarationNamesItsCause:
    @staticmethod
    def _world():
        world = WorldFactory.diplomatic()
        world.threat_sources_this_turn = []
        return world

    def test_a_broken_treaty_is_the_strongest_evidence(self):
        world = self._world()
        line = DSP.war_declaration_cause(
            world, "Britain", {"breached_treaty": "Treaty of Amiens"})
        assert "tears up the Treaty of Amiens" in line, line

    def test_a_grievance_of_ours_is_named_when_nothing_else_is(self):
        world = self._world()
        world.threat_sources_this_turn = [
            {"source": "ultimatum_defied", "amount": 6, "target": "France"},
            {"source": "military_establishment", "amount": 2,
             "target": "France"},
        ]
        line = DSP.war_declaration_cause(world, "Britain", {})
        assert "defied an ultimatum" in line, line

    def test_the_largest_grievance_wins(self):
        world = self._world()
        world.threat_sources_this_turn = [
            {"source": "ultimatum_defied", "amount": 2, "target": "France"},
            {"source": "military_establishment", "amount": 9,
             "target": "France"},
        ]
        line = DSP.war_declaration_cause(world, "Britain", {})
        assert "largest army" in line.lower(), line

    def test_a_grievance_aimed_at_someone_else_is_not_ours(self):
        world = self._world()
        world.threat_sources_this_turn = [
            {"source": "ultimatum_defied", "amount": 6, "target": "Prussia"},
        ]
        assert DSP.war_declaration_cause(world, "Britain", {}) == ""

    def test_a_relieving_row_is_not_a_cause(self):
        """A NEGATIVE threat row is threat coming off the board — never a
        reason someone declared war."""
        world = self._world()
        world.threat_sources_this_turn = [
            {"source": "ultimatum_defied", "amount": -6, "target": "France"},
        ]
        assert DSP.war_declaration_cause(world, "Britain", {}) == ""

    def test_nothing_on_the_record_says_nothing(self):
        world = self._world()
        assert DSP.war_declaration_cause(world, "Britain", {}) == ""

    def test_the_label_comes_from_the_ledgers_own_source(self):
        """Shown = shown: the threat panel and this sentence must name a
        grievance identically, or the player reads two names for one cause."""
        from backend.game_logic.diplomatic_ledger import _threat_source_label
        world = self._world()
        world.threat_sources_this_turn = [
            {"source": "agenda_grudge", "amount": 4, "target": "France"},
        ]
        line = DSP.war_declaration_cause(world, "Britain", {})
        assert _threat_source_label(world, "agenda_grudge").lower() in line

    def test_the_consumer_appends_it_to_the_players_own_beat(self):
        src = (ROOT / "backend" / "game_logic" / "dispatch.py").read_text(
            encoding="utf-8")
        m = re.search(r'other = target if aggressor == player_nation else aggressor'
                      r'(.{0,700}?)_add\("war_touches_us", line=_line\)', src, re.S)
        assert m, "the war_touches_us arm no longer composes the cause"
        body = m.group(1)
        assert "war_declaration_cause(world, aggressor, e)" in body
        # The APPEND, not merely the call: the Phase-4 sweep reported the
        # first cut of this pin INERT because disabling the append left the
        # call standing and the census still matched.
        assert 'if _cause:' in body
        assert '_line = f"{_line} {_cause}"' in body
        # Never about OUR OWN declaration — France does not explain itself
        # to itself, and the ladder reads the AGGRESSOR's court.
        assert 'if aggressor == player_nation' in body

    def test_the_beat_itself_carries_the_cause(self):
        """The behavioural sibling of the census above: the composed
        headline text, through the real builder."""
        from backend.game_logic.dispatch import _build_headline
        world = self._world()
        world.threat_sources_this_turn = [
            {"source": "ultimatum_defied", "amount": 6, "target": "France"},
        ]
        world.event_log = [{
            "type": "war_declaration", "turn": int(world.current_turn),
            "aggressor": "Britain", "target": "France",
        }]
        with _quiet():
            head = _build_headline(world, "France")
        assert head, "no headline was composed at all"
        text = str(head.get("text", ""))
        assert "Britain and France are at war." in text, text
        assert "defied an ultimatum" in text, text

    def test_lever_down_reproduces_the_bare_sentence(self, monkeypatch):
        monkeypatch.setattr(DSP, "THE_DECLARATION_NAMES_ITS_CAUSE", False)
        world = self._world()
        assert DSP.war_declaration_cause(
            world, "Britain", {"breached_treaty": "Treaty of Amiens"}) == ""


# ═══════════════════════════════════════════════════════════════════════
# FA-S17-D6 — the commanded arm, and the peace the driver stops breaking
# ═══════════════════════════════════════════════════════════════════════
class TestTheCommandedArmExists:
    SCRIPT = ROOT / "tools" / "playtest_scripts" / "commanded_full40.json"

    def test_the_script_is_committed_and_runs_the_whole_forty(self):
        data = json.loads(self.SCRIPT.read_text(encoding="utf-8"))
        turns = data["turns"]
        assert sorted(int(k) for k in turns) == list(range(1, 41))

    def test_it_spends_every_military_action_every_turn(self):
        """The defect it exists to remove: the prior 'fighting' scripts spend
        9–22 of 160 action points and stop issuing orders at loop 22–30, so
        Fr@30 and Fr@40 measure a France that has stopped being played."""
        data = json.loads(self.SCRIPT.read_text(encoding="utf-8"))
        counts = {int(k): len(v) for k, v in data["turns"].items()}
        assert min(counts.values()) == 4, min(counts.values())
        assert sum(counts.values()) == 160, sum(counts.values())

    def test_it_never_orders_an_attack_on_a_court_at_peace(self):
        """The second half of the same ruling: the driver answers the
        declare-war confirm, so a script that attacks a court France has
        just signed with would re-declare the war it was measuring."""
        data = json.loads(self.SCRIPT.read_text(encoding="utf-8"))
        orders = [o for v in data["turns"].values() for o in v]
        attacks = [o for o in orders if "attack" in o.lower()]
        # Only the three Austrian commanders of the opening campaign.
        for o in attacks:
            assert re.search(r"Mack|Archduke (Charles|John)", o), o

    def test_the_driver_has_its_own_dial_for_the_declaration(self):
        src = (ROOT / "tools" / "playtest_driver.py").read_text(encoding="utf-8")
        assert '"declare_war": "cancel",' in src
        assert '"force_declare_war_confirmation": "declare_war",' in src
        assert '--declare-war' in src

    def test_cancel_is_the_default_and_proceed_reproduces_the_old_answer(self):
        src = (ROOT / "tools" / "playtest_driver.py").read_text(encoding="utf-8")
        m = re.search(r'if policy_key == "declare_war":(.{0,600}?)\n            if policy_key in',
                      src, re.S)
        assert m, "the declare_war arm moved"
        body = m.group(1)
        assert 'self.policy.get("declare_war", "cancel")) == "proceed"' in body
        # proceed keeps the pre-Phase-4 options[0] answer; cancel takes the
        # last option, which is where the cancel arm is always offered.
        assert "_option_id(options[0])" in body
        assert "_option_id(options[-1])" in body

    def test_the_dial_is_read_before_the_generic_diplomacy_block(self):
        """It was in no table at all, which is how "Proceed — break the
        treaty" became the answer: none of the accept needles match it, so
        the fallback took options[0]."""
        src = (ROOT / "tools" / "playtest_driver.py").read_text(encoding="utf-8")
        arm = src.index('if policy_key == "declare_war":')
        generic = src.index('mode = self.policy["diplomacy"]\n        if mode in ("accept", "propose")')
        assert arm < generic


# ═══════════════════════════════════════════════════════════════════════
# FA-S17-D8 — the crossing announces itself
# ═══════════════════════════════════════════════════════════════════════
class TestTheTierCrossingIsAnnounced:
    def test_falling_out_of_loyal_names_what_it_costs(self):
        line = VS.tier_crossing_line("Bavaria", 60, 58)
        assert "Bavaria" in line and "musters" in line, line

    def test_falling_into_disaffected_names_its_own_cost(self):
        line = VS.tier_crossing_line("Bavaria", 35, 33)
        assert "disaffected" in line, line
        assert "call to arms" in line, line

    def test_a_tick_inside_a_band_says_nothing(self):
        assert VS.tier_crossing_line("Bavaria", 58, 56) == ""
        assert VS.tier_crossing_line("Bavaria", 99, 97) == ""

    def test_it_fires_once_per_crossing_by_arithmetic_not_by_a_latch(self):
        """The whole point of deriving it from THIS tick's own numbers: the
        second tick in the same band is silent with no store to go stale."""
        assert VS.tier_crossing_line("Bavaria", 60, 58) != ""
        assert VS.tier_crossing_line("Bavaria", 58, 56) == ""

    def test_recovering_and_falling_again_is_news_again(self):
        assert VS.tier_crossing_line("Bavaria", 60, 58) != ""
        assert VS.tier_crossing_line("Bavaria", 58, 61) == ""      # rising
        assert VS.tier_crossing_line("Bavaria", 61, 58) != ""      # again

    def test_a_cascade_through_both_bands_names_the_one_that_binds(self):
        line = VS.tier_crossing_line("Bavaria", 62, 30)
        assert "call to arms" in line, line

    def test_a_rise_is_never_a_warning(self):
        assert VS.tier_crossing_line("Bavaria", 30, 70) == ""

    def test_the_boundaries_are_the_vs4_constants(self):
        """Shown = applied. The copy must not carry its own numbers."""
        src = (ROOT / "backend" / "game_logic" / "vassal.py").read_text(
            encoding="utf-8")
        m = re.search(r"def tier_crossing_line\(.*?\n(?=\ndef |\nclass )", src, re.S)
        assert m, "tier_crossing_line moved"
        body = m.group(0)
        assert "CONTRIBUTION_LOYAL_MIN" in body
        assert "CONTRIBUTION_DISAFFECTED_BELOW" in body
        assert not re.search(r"\b(60|35)\b", body.split('"""')[-1]), body

    def test_the_loyalty_pass_still_stamps_no_new_row_key(self):
        """VS-R's guardrail, restated here because this row is what nearly
        broke it: the first cut stored a `tiers_seen` list on the vassal row
        and the guard caught it.

        Scoped to CODE, not to the file — the first cut of THIS pin matched
        the comment that explains why the latch was removed, which is the
        project's own recurring lesson (prose inside a file a pin reads is
        not code). A sensitivity arm proves the scoping still sees strings
        that are really there.
        """
        assert "tiers_seen" not in _code_only(
            ROOT / "backend" / "game_logic" / "vassal.py")

    def test_the_code_census_can_still_see_a_real_key(self):
        """The sensitivity arm for the census above."""
        code = _code_only(ROOT / "backend" / "game_logic" / "vassal.py")
        assert "courted_turn" in code          # WO slice 9's real row key
        assert "CONTRIBUTION_LOYAL_MIN" in code

    def test_the_producer_carries_it_and_says_it(self):
        src = (ROOT / "backend" / "game_logic" / "vassal.py").read_text(
            encoding="utf-8")
        assert 'crossing = tier_crossing_line(vassal_name, int(old_loyalty),' in src
        assert '"tier_crossing": crossing,' in src
        assert '+ (f" {crossing}" if crossing else "")' in src

    def test_lever_down_says_nothing(self, monkeypatch):
        monkeypatch.setattr(VS, "THE_TIER_CROSSING_IS_ANNOUNCED", False)
        assert VS.tier_crossing_line("Bavaria", 60, 58) == ""


# ═══════════════════════════════════════════════════════════════════════
# FA-S17-D9 — the orphan is retired
# ═══════════════════════════════════════════════════════════════════════
class TestTheOrphanPopupIsRetired:
    def test_the_scene_and_its_script_are_gone(self):
        assert not (GD / "scenes" / "proposal_result_popup.tscn").exists()
        assert not (GD / "scripts" / "proposal_result_popup.gd").exists()

    def test_nothing_in_the_client_references_it(self):
        offenders = []
        for path in list((GD / "scripts").glob("*.gd")) + \
                list((GD / "scenes").glob("*.tscn")):
            text = path.read_text(encoding="utf-8", errors="replace")
            for line in text.splitlines():
                if "proposal_result_popup" not in line:
                    continue
                if line.lstrip().startswith("#"):
                    continue        # the dialog_manager layer note
                offenders.append(f"{path.name}: {line.strip()}")
        assert not offenders, offenders

    def test_the_parse_harness_no_longer_names_it(self):
        src = (ROOT / "tools" / "godot_parse_check.gd").read_text(encoding="utf-8")
        assert "proposal_result_popup" not in src

    def test_the_outcome_still_reaches_the_player_twice(self):
        """Retire, not drop: the backend field is a legacy INFORMATIONAL
        channel, and both of its roads are intact."""
        src = (ROOT / "backend" / "main.py").read_text(encoding="utf-8")
        assert 'response["proposal_result"] = proposal_result' in src
        assert "_queue_informational_diplomacy_notices" in src
        notices = re.search(r"def _queue_informational_diplomacy_notices\(.*?\n(?=\ndef )",
                            src, re.S)
        assert notices, "the rail mirror moved"
        assert "DIPLOMATIC_PROPOSAL_RESULT" in notices.group(0)

    def test_the_doc_row_stops_sending_builders_to_it(self):
        text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        row = [ln for ln in text.splitlines()
               if "New dialogue type shows in terminal" in ln]
        assert row, "the troubleshooting row moved"
        assert "Do NOT reach for `world.proposal_result_popup`" in row[0]
