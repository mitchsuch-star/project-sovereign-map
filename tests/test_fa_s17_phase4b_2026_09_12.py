"""FA slice 17, Phase 4 part B (September 12, 2026) — the re-score's P3/P4
rows, each behind a lever whose False arm reproduces the prior behaviour.

  FA-S17-13 one state, one answer: a hostile verb aimed at a court at peace
            names the road, at every verb
  FA-S17-14 the marshal quotes the player's own words, not the engine's
            resolution of them
  FA-S17-15 one court, one envoy per war
  FA-S17-16 one letter, one name
  FA-S17-17 FA-D4's boot purpose reaches a LOADED campaign
  FA-S17-18 the standing block says which side each row is on
  FA-S17-19 a ticking rate is not printed beside "not ticking"
"""
from __future__ import annotations

import contextlib
import io
import re
from pathlib import Path

from backend import campaign_log as CL
from backend.commands import delegation as DG
from backend.commands import strategic as ST
from backend.commands.executor import CommandExecutor
from backend.game_logic import ai_diplomacy as AID
from backend.models import world_state as WS
from tests.conftest import MarshalFactory, WorldFactory

ROOT = next(p for p in (Path(__file__).resolve().parents[1], Path.cwd())
            if (p / "backend").is_dir())
GD = ROOT / "godot-client" / "project-sovereign" / "scripts"


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


def _peace(world, a="France", b="Austria", state="PEACE", turns=0):
    key = "|".join(sorted([a, b]))
    world.diplomatic_states[key] = state
    if turns:
        world.armistice_cooldowns[key] = turns
    return world


# ═══════════════════════════════════════════════════════════════════════
# FA-S17-13 — one state, one answer
# ═══════════════════════════════════════════════════════════════════════
class TestThePeacefulCourtGetsOneAnswer:
    """Measured on the Phase-3 accept arms: four verbs, four different
    replies for the SAME state, two of them false about their own cause."""

    @staticmethod
    def _board(state="PEACE", turns=0):
        ney = MarshalFactory.infantry(name="Ney", location="Belgium",
                                      strength=20000, personality="aggressive")
        # The raw scenario KEY is the name the old pursue refusal printed.
        mack = MarshalFactory.enemy(name="ArchdukeCharles", location="Waterloo",
                                    nation="Austria", strength=9000)
        world = _peace(WorldFactory.with_marshals([ney, mack]),
                       state=state, turns=turns)
        world.calculate_visibility()
        return world, ney, mack

    def test_at_peace_it_names_the_state_and_the_two_roads(self):
        world, ney, mack = self._board()
        line = ST.hostile_verb_at_peace(world, ney, mack, "pursue")
        assert "not at war with Austria" in line, line
        assert "Declare war on Austria" in line, line
        assert "leave him be" in line, line

    def test_the_name_is_humanized_not_the_scenario_key(self):
        """NPC-12's class — the defect the row actually names."""
        world, ney, mack = self._board()
        line = ST.hostile_verb_at_peace(world, ney, mack, "pursue")
        assert "Archduke Charles" in line, line
        assert "ArchdukeCharles" not in line, line

    def test_at_war_it_answers_nothing_so_a_caller_may_use_it_alone(self):
        world, ney, mack = self._board(state="WAR")
        assert ST.hostile_verb_at_peace(world, ney, mack, "pursue") == ""

    def test_an_armistice_names_the_turns_left(self):
        world, ney, mack = self._board(state="ARMISTICE", turns=4)
        line = ST.hostile_verb_at_peace(world, ney, mack, "charge")
        assert "armistice with Austria" in line, line
        assert "4 more turns" in line, line  # F2 LV-9: the count and the noun agree

    def test_our_own_marshal_is_never_refused_by_this_rule(self):
        world, ney, _ = self._board()
        davout = MarshalFactory.infantry(name="Davout", location="Belgium")
        world.marshals["Davout"] = davout
        assert ST.hostile_verb_at_peace(world, ney, davout, "charge") == ""

    def test_the_pursue_arm_reads_it(self):
        world, ney, mack = self._board()
        ex = CommandExecutor()
        parsed = {
            "command": {"action": "strategic_command", "marshal": "Ney",
                        "target": "ArchdukeCharles",
                        "raw_command": "Ney, pursue Archduke Charles"},
            "is_strategic": True,
            "strategic_type": "PURSUE",
        }
        with _quiet():
            res = ex.execute(parsed, {"world": world, "executor": ex})
        msg = str(res.get("message", ""))
        assert res.get("success") is False, msg
        assert "not at war with Austria" in msg, msg
        # The two halves of the old sentence are gone.
        assert "Cannot pursue" not in msg, msg
        assert "ArchdukeCharles" not in msg, msg

    def test_the_charge_arm_stops_blaming_the_map(self):
        """`charge` filtered its lookup on `is_at_war`, so a marshal standing
        in the next province read as "Cannot find target"."""
        world, ney, mack = self._board()
        ney.location = "Waterloo"          # co-located: he is RIGHT THERE
        ney.cavalry_count = 5000
        ex = CommandExecutor()
        with _quiet():
            res = ex._execute_glorious_charge(
                ney, "ArchdukeCharles", world, {"world": world})
        msg = str(res.get("message", ""))
        assert res.get("success") is False, msg
        assert "Cannot find target" not in msg, msg
        assert "not at war with Austria" in msg, msg

    def test_a_name_that_resolves_to_nobody_still_says_not_found(self):
        """The honest arm must survive: an invented name is not a peace
        problem, and the fix must not swallow the real not-found case."""
        world, ney, _ = self._board()
        ney.cavalry_count = 5000
        ex = CommandExecutor()
        with _quiet():
            res = ex._execute_glorious_charge(
                ney, "Kutz", world, {"world": world})
        msg = str(res.get("message", ""))
        assert res.get("success") is False, msg
        assert "Cannot find target 'Kutz'" in msg, msg

    def test_lever_down_reproduces_all_four_replies(self, monkeypatch):
        monkeypatch.setattr(ST, "THE_PEACEFUL_COURT_GETS_ONE_ANSWER", False)
        world, ney, mack = self._board()
        assert ST.hostile_verb_at_peace(world, ney, mack, "pursue") == ""
        ex = CommandExecutor()
        parsed = {
            "command": {"action": "strategic_command", "marshal": "Ney",
                        "target": "ArchdukeCharles", "raw_command": "x"},
            "is_strategic": True, "strategic_type": "PURSUE",
        }
        with _quiet():
            res = ex.execute(parsed, {"world": world, "executor": ex})
        assert "Cannot pursue ArchdukeCharles" in str(res.get("message", ""))


# ═══════════════════════════════════════════════════════════════════════
# FA-S17-14 — the quote is the player's own
# ═══════════════════════════════════════════════════════════════════════
class TestTheQuoteIsThePlayersOwn:
    @staticmethod
    def _match(spoken="deal with the Austrians", clause="deal with Mack",
               personality="literal"):
        return DG.DelegationMatch("Soult", personality, "Mack", "Swabia",
                                  "Mack", "deal with", clause, spoken)

    def test_the_ask_quotes_what_the_player_typed(self):
        q = DG._ask_question(self._match())
        assert '"deal with the Austrians"' in q, q
        assert '"deal with Mack"' not in q, q

    def test_the_engine_states_its_reading_beside_the_quote(self):
        q = DG._ask_question(self._match())
        assert "I read that as Mack." in q, q

    def test_an_exact_order_gains_no_redundant_reading(self):
        """`Soult, deal with Mack` needs no gloss — and must not get one."""
        q = DG._ask_question(self._match(spoken="deal with Mack"))
        assert "I read that as" not in q, q
        assert '"deal with Mack"' in q, q

    def test_the_neutral_arm_takes_the_same_rule(self):
        q = DG._ask_question(self._match(personality="aggressive"))
        assert '"deal with the Austrians"' in q, q
        assert "I read that as Mack." in q, q

    def test_the_slot_is_declared_so_it_serializes_with_the_object(self):
        """`DelegationMatch` uses __slots__ — an undeclared attribute would
        raise, which is why the field had to be added to the tuple."""
        assert "spoken" in DG.DelegationMatch.__slots__
        m = self._match()
        assert m.spoken == "deal with the Austrians"

    def test_the_default_keeps_every_other_caller_honest(self):
        """Positional construction without `spoken` falls back to the clause,
        so no existing producer starts quoting an empty string."""
        m = DG.DelegationMatch("Soult", "literal", "Mack", "Swabia", "Mack",
                               "deal with", "deal with Mack")
        assert m.spoken == "deal with Mack"

    def test_the_producer_carries_the_typed_remainder(self):
        # ADJACENT provinces of the fixture world: the nation arm resolves
        # through fog (R5), so a quarry our staff cannot see never reaches
        # the ASK at all — which is why a distant pair made this pin vacuous.
        soult = MarshalFactory.infantry(name="Soult", location="Rhineland",
                                        personality="literal")
        mack = MarshalFactory.enemy(name="Mack", location="Bavaria",
                                    nation="Austria")
        world = WorldFactory.with_marshals([soult, mack])
        world.diplomatic_states["Austria|France"] = "WAR"
        world.war_start_turns["Austria|France"] = 1
        world.calculate_visibility()
        assert world.get_visible_enemies("France"), "the quarry must be in view"
        with _quiet():
            m = DG.detect_delegation(world, "Soult, deal with the Austrians",
                                     {"marshal": "Soult"})
        # No early-out: a delegation that does not match makes this pin
        # vacuous, and the first Phase-4 sweep reported exactly that.
        assert m is not None, "the demonym delegation no longer resolves"
        assert m.spoken == "deal with the Austrians", m.spoken
        assert m.clause == "deal with Mack", m.clause
        assert m.spoken != m.clause

    def test_a_typed_raw_key_is_never_quoted_back_as_a_key(self):
        """R7, and the reason the quote is NARROWED: a player who types the
        raw scenario key gets the clean form back, because humanizing it
        yields exactly the display name and there is nothing to gloss.
        CR-5's own review pinned that no camelCase key reaches player copy."""
        soult = MarshalFactory.infantry(name="Soult", location="Rhineland",
                                        personality="literal")
        charles = MarshalFactory.enemy(name="ArchdukeCharles",
                                       location="Bavaria", nation="Austria")
        world = WorldFactory.with_marshals([soult, charles])
        world.diplomatic_states["Austria|France"] = "WAR"
        world.war_start_turns["Austria|France"] = 1
        world.calculate_visibility()
        with _quiet():
            m = DG.detect_delegation(world, "Soult, deal with ArchdukeCharles",
                                     {"marshal": "Soult"})
        assert m is not None
        assert m.target == "ArchdukeCharles"          # RAW for the executor
        assert m.spoken == "deal with Archduke Charles", m.spoken
        q = DG._ask_question(m)
        assert "ArchdukeCharles" not in q, q
        assert "I read that as" not in q, q            # nothing to gloss

    def test_lever_down_reproduces_the_engines_own_quote(self, monkeypatch):
        monkeypatch.setattr(DG, "THE_QUOTE_IS_THE_PLAYERS_OWN", False)
        q = DG._ask_question(self._match())
        assert '"deal with Mack"' in q, q
        assert "the Austrians" not in q, q
        assert "I read that as" not in q, q


# ═══════════════════════════════════════════════════════════════════════
# FA-S17-15 — one court, one envoy per war
# ═══════════════════════════════════════════════════════════════════════
class TestTheCourtSendsOneEnvoyPerWar:
    """Measured tyrant-accept/austerlitz T18: "ENVOYS WAITING 2 · Austria
    peace · Austria settlement offer" — answering one left the other
    refusing itself ("We already have PEACE with France")."""

    @staticmethod
    def _war(world, war_id="w1"):
        world.war_instances = {war_id: {
            "war_id": war_id,
            "attackers": ["France"], "defenders": ["Austria"],
            "active_participants": ["France", "Austria"],
            "attacker_leader": "France", "defender_leader": "Austria",
        }}
        return war_id

    def test_a_pending_offer_for_the_same_war_blocks_the_bilateral(self):
        world = WorldFactory.diplomatic()
        wid = self._war(world)
        world.pending_settlement_dialogues = [
            {"type": "incoming_settlement_offer", "war_id": wid},
        ]
        assert AID._settlement_offer_already_pending(
            world.pending_settlement_dialogues, war_id=wid) is True

    def test_an_offer_for_a_different_war_does_not_block(self):
        world = WorldFactory.diplomatic()
        wid = self._war(world)
        pending = [{"type": "incoming_settlement_offer", "war_id": "other"}]
        assert AID._settlement_offer_already_pending(pending, war_id=wid) is False

    def test_the_pair_lookup_is_direction_blind(self):
        world = WorldFactory.diplomatic()
        self._war(world)
        assert AID._find_war_instance_for_pair(world, "Austria", "France")
        assert AID._find_war_instance_for_pair(world, "France", "Austria")
        assert AID._find_war_instance_for_pair(world, "France", "Russia") is None

    def test_the_guard_is_wired_into_the_p1_arm(self):
        """A source census on the ONE call site, because the arm itself needs
        a losing coalition war to reach and the predicates above carry the
        behaviour. Paired with the sensitivity arm below."""
        src = (ROOT / "backend" / "game_logic" / "ai_diplomacy.py").read_text(
            encoding="utf-8")
        m = re.search(
            r"if not coalition_blocked and THE_COURT_SENDS_ONE_ENVOY_PER_WAR:"
            r"(.{0,900}?)\n        if not coalition_blocked:", src, re.S)
        assert m, "the FA-S17-15 guard is no longer above the P1 decision"
        body = m.group(1)
        assert "_find_war_instance_for_pair" in body
        assert "_settlement_offer_already_pending" in body
        assert "_settlement_offer_already_promoted" in body
        assert "coalition_blocked = True" in body

    def test_the_lever_exists_and_gates_the_guard(self):
        assert AID.THE_COURT_SENDS_ONE_ENVOY_PER_WAR is True
        src = (ROOT / "backend" / "game_logic" / "ai_diplomacy.py").read_text(
            encoding="utf-8")
        # The lever must be READ at the guard, not merely defined.
        assert src.count("THE_COURT_SENDS_ONE_ENVOY_PER_WAR") >= 2


# ═══════════════════════════════════════════════════════════════════════
# FA-S17-16 — one letter, one name
# ═══════════════════════════════════════════════════════════════════════
class TestTheLogNamesWhatWasProposed:
    def test_the_offered_type_wins_when_the_producer_knew_it(self):
        line = CL.format_event_oneliner({
            "type": "ai_proposal_rejected", "turn": 9, "source": "Hanover",
            "proposal_type": "friendly_gift",
            "proposal_type_offered": "open_borders",
        })
        assert "open borders" in line.lower(), line
        assert "gift" not in line.lower(), line

    def test_it_falls_back_to_the_intent_for_an_older_event(self):
        line = CL.format_event_oneliner({
            "type": "ai_proposal_rejected", "turn": 9, "source": "Hanover",
            "proposal_type": "friendly_gift",
        })
        assert "gift" in line.lower(), line

    def test_an_empty_offered_type_is_not_trusted(self):
        line = CL.format_event_oneliner({
            "type": "ai_proposal_rejected", "turn": 9, "source": "Hanover",
            "proposal_type": "friendly_gift", "proposal_type_offered": "",
        })
        assert "gift" in line.lower(), line

    def test_the_collapse_predicate_still_keys_on_the_intent(self):
        """IGR-B buckets by `(turn, proposal_type)`. Re-keying it would change
        what collapses; the row is about the SENTENCE, not the bucket."""
        src = (ROOT / "backend" / "campaign_log.py").read_text(encoding="utf-8")
        m = re.search(r"def collapse_refusal_family\(.*?\n(?=\ndef |\nclass )",
                      src, re.S)
        assert m, "collapse_refusal_family moved"
        assert "proposal_type_offered" not in m.group(0)

    def test_the_producer_stamps_it(self):
        src = (ROOT / "backend" / "commands" / "diplomatic_executor.py").read_text(
            encoding="utf-8")
        assert '"proposal_type_offered": str(terms.get("type") or "")' in src

    def test_lever_down_reproduces_the_intent_label(self, monkeypatch):
        monkeypatch.setattr(CL, "THE_LOG_NAMES_WHAT_WAS_PROPOSED", False)
        line = CL.format_event_oneliner({
            "type": "ai_proposal_rejected", "turn": 9, "source": "Hanover",
            "proposal_type": "friendly_gift",
            "proposal_type_offered": "open_borders",
        })
        assert "gift" in line.lower(), line
        assert "open borders" not in line.lower(), line


# ═══════════════════════════════════════════════════════════════════════
# FA-S17-17 — FA-D4's purpose reaches a loaded campaign
# ═══════════════════════════════════════════════════════════════════════
class TestTheLoadedWarHasAPurposeToo:
    @staticmethod
    def _purposeless(**over):
        world = WorldFactory.diplomatic()
        world.diplomatic_states["Austria|France"] = "WAR"
        world.war_objectives = {}
        # The row's OWN geometry. FA-D4's boot pass lives in `from_scenario`,
        # so only a Europe/scenario world was ever supposed to have war
        # purposes at all — the legacy fixture world boots purposeless BY
        # DESIGN (N1), and the first cut of this migration perturbed it.
        world.sovereign_map = "europe"
        for k, v in over.items():
            setattr(world, k, v)
        return world

    def test_a_purposeless_war_gets_the_defenders_default_both_ways(self):
        world = self._purposeless()
        with _quiet():
            world._migrate_missing_war_purposes()
        got = (world.war_objectives or {}).get("Austria|France") or {}
        assert set(got) == {"France", "Austria"}, got
        for side in ("France", "Austria"):
            assert str(got[side].get("type")) == "defense", got[side]

    def test_a_war_that_already_has_a_purpose_is_untouched(self):
        world = self._purposeless()
        world.war_objectives = {"Austria|France": {
            "France": {"type": "conquest", "target_regions": ["Swabia"]}}}
        before = dict(world.war_objectives["Austria|France"])
        with _quiet():
            world._migrate_missing_war_purposes()
        assert world.war_objectives["Austria|France"] == before

    def test_a_pair_not_at_war_is_never_given_one(self):
        world = self._purposeless()
        world.diplomatic_states["Austria|France"] = "ARMISTICE"
        with _quiet():
            world._migrate_missing_war_purposes()
        assert not (world.war_objectives or {}).get("Austria|France")

    def test_a_malformed_key_is_skipped_not_crashed(self):
        world = self._purposeless()
        world.diplomatic_states["nonsense"] = "WAR"
        with _quiet():
            world._migrate_missing_war_purposes()      # must not raise
        assert not (world.war_objectives or {}).get("nonsense")

    def test_from_dict_calls_it(self):
        """The seam that matters: a round trip of a purposeless save."""
        world = self._purposeless()
        with _quiet():
            data = world.to_dict()
        data["war_objectives"] = {}
        with _quiet():
            revived = WS.WorldState.from_dict(data)
        got = (revived.war_objectives or {}).get("Austria|France") or {}
        assert set(got) == {"France", "Austria"}, got

    def test_the_legacy_world_is_never_touched(self):
        """N1: the legacy fixture world is at war with no objectives on
        purpose, and a load must leave it exactly as it was — which is also
        what keeps to_dict/from_dict identity for `war_objectives`."""
        world = self._purposeless()
        world.sovereign_map = "legacy"
        with _quiet():
            world._migrate_missing_war_purposes()
        assert not (world.war_objectives or {}).get("Austria|France")

    def test_lever_down_leaves_the_loaded_war_purposeless(self, monkeypatch):
        monkeypatch.setattr(WS, "THE_LOADED_WAR_HAS_A_PURPOSE_TOO", False)
        world = self._purposeless()
        with _quiet():
            world._migrate_missing_war_purposes()
        assert not (world.war_objectives or {}).get("Austria|France")


# ═══════════════════════════════════════════════════════════════════════
# FA-S17-18 / FA-S17-19 — the two client surfaces
# ═══════════════════════════════════════════════════════════════════════
class TestTheStandingBlockNamesItsSides:
    def test_the_formatter_renders_the_side_label(self):
        src = (GD / "utils.gd").read_text(encoding="utf-8")
        m = re.search(r"static func standing_lines\(.*?\n\treturn lines", src, re.S)
        assert m, "standing_lines moved"
        body = m.group(0)
        assert 'row.get("side_label", "")' in body
        assert 'side_note = " [" + side_label + "]"' in body
        # The row line must actually interpolate it.
        assert re.search(r'lines\.append\([^\n]*side_note[^\n]*standing', body), body

    def test_the_producer_stamps_the_key_the_formatter_reads(self):
        """The producer→consumer join, which is what the slice-9 lesson is
        about: a client fix reading a key nobody sets is production-dead."""
        src = (ROOT / "backend" / "game_logic" / "settlement_presentation.py"
               ).read_text(encoding="utf-8")
        m = re.search(r"def build_contribution_share_rows\(.*?\n(?=\ndef |\nclass )",
                      src, re.S)
        assert m, "build_contribution_share_rows moved"
        assert '"side_label": side_label_display(side)' in m.group(0)

    def test_the_war_panel_rows_come_from_that_builder(self):
        src = (ROOT / "backend" / "game_logic" / "war_status.py").read_text(
            encoding="utf-8")
        assert "build_contribution_share_rows" in src
        assert '"contribution_share": contribution.get("rows", [])' in src

    def test_the_cap_and_the_overflow_count_are_untouched(self):
        src = (GD / "utils.gd").read_text(encoding="utf-8")
        assert 'lines.append("Standing (top 5):")' in src
        assert 'war_data.get("contribution_overflow_count", 0)' in src


class TestTheRateIsNotPrintedBesideNotTicking:
    @staticmethod
    def _body():
        src = (GD / "war_detail_popup.gd").read_text(encoding="utf-8")
        m = re.search(r'bbcode \+= " \(" \+ active \+ ", \+" \+ str\(accumulated\)'
                      r'(.*?)\n\n', src, re.S)
        assert m, "the objective rate block moved"
        return m.group(1)

    def test_a_running_rate_still_prints_inline(self):
        body = self._body()
        assert 'if rate > 0 and bool(objective.get("ticking_active", false)):' in body
        assert 'bbcode += ", +" + str(rate) + "/turn"' in body

    def test_a_dormant_rate_says_what_would_start_it(self):
        body = self._body()
        assert 'if rate > 0 and not bool(objective.get("ticking_active", false)):' in body
        assert '/turn once it begins' in body

    def test_the_rate_is_never_printed_unconditionally(self):
        """The sensitivity arm: the defect WAS the bare `if rate > 0`."""
        body = self._body()
        assert not re.search(r"if rate > 0:\s*\n", body), body

    def test_the_producer_carries_ticking_active(self):
        src = (ROOT / "backend" / "game_logic" / "war_status.py").read_text(
            encoding="utf-8")
        assert '"ticking_active": bool(france_obj.get("ticking_active", False))' in src
