"""FA slice 17, part e — "The Square and the Survivors" (FA-N57, N70, N55,
N64, N69, N71 + FA-N32).

The rest of REPRO_L's square/combat family plus the two render-parity rows
and the one row in the slice that changes COMBAT state:

* FA-N57 — the "is in square formation" advisory read the LIVE attribute
  1,142 lines after the auto-break had already cleared it: production-dead
  since Session 67. It now reads the PRE-break state and says the
  consequence (the square is GONE), because the old sentence's two clauses
  are both false once he has broken square.
* FA-N70 (+ the unfiled third site REPRO_L found) — the raw order enum
  ("Strategic order (MOVE_TO) cancelled", "defied your order to MOVE_TO")
  routed through the R7 single source.
* FA-N55 — the enemy-phase dialog scaled an int percent by 100 a second
  time: "Fort degraded: 2000% -> 1000%". Client-only, four reads.
* FA-N64 — the override payoff was undeliverable twice: the only writer
  recorded "override" while the only reader matched "good"/"bad", and the
  key it landed on was read by no .gd. The outcome is stamped where the
  proposal RESOLVES, and both dispatch renderers print it.
* FA-N69 / FA-N71 — the dispatch re-read screen dropped DIPLOMATIC STATUS
  and COALITION THREAT, and nobody rendered WAR PURPOSE at all. One
  source-census parity pin (full-line comments stripped) forbids the class.
* FA-N32 — the auto-charge combat copy never got the July-6 survivor clamp:
  a 900-man corps "shattered" to 1,000. ONE pure helper, three sites, a
  flip lever, and a forced-surround behaviour arm — the ONLY row here that
  can move an AI decision; the series attribution is on the record.

⚠ Two lessons this file's first cut taught: a `.gd` "comment stripper" that
splits on `#` also guts every `[color=#…` bbcode string (it emptied the
renderer text and the parity pin passed vacuously in the other direction);
and the surround arm is only REACHED at ~1:1 odds — at 12,000 vs 900 the
defender is annihilated before it, and a lever-down control "did not
reproduce" for the wrong reason.
"""

import contextlib
import io
import pathlib
import random
import re

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend import save_manager
from backend.commands import diplomatic_defiance as DDF
from backend.commands import strategic_executor as SE
from backend.commands.parser import CommandParser
from backend.display_names import action_display_name
from backend.game_logic import combat as C
from backend.game_logic.dispatch import build_morning_dispatch
from backend.models.marshal import StrategicOrder
from backend.models.world_state import WorldState

REPO = pathlib.Path(__file__).resolve().parents[1]
SCENARIO = str(REPO / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json")
GD = REPO / "godot-client" / "project-sovereign" / "scripts"


def _quiet(fn, *a, **k):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*a, **k)


def _world():
    return _quiet(WorldState.from_scenario, SCENARIO)


def _legacy():
    return _quiet(WorldState, player_nation="France")


def _strip_gd_comments(src: str) -> str:
    """Drop FULL-LINE comments only. An inline `#` split would also gut every
    `[color=#…` bbcode string, which is most of a renderer's text."""
    return "\n".join(line for line in src.splitlines() if not line.lstrip().startswith("#"))


@pytest.fixture
def client(monkeypatch, tmp_path):
    """A real `/command` surface on a fresh 1805 boot, saves sandboxed."""
    monkeypatch.setenv("INK_IRON_SAVE_DIR", str(tmp_path / "saves"))
    monkeypatch.setattr(save_manager, "SAVE_DIR", tmp_path / "saves")
    world = _world()
    monkeypatch.setattr(M, "world", world)
    monkeypatch.setattr(M, "game_state", {"world": world})
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    return TestClient(M.app), world


def _post(client, text):
    with contextlib.redirect_stdout(io.StringIO()):
        return client.post("/command", json={"command": text}).json()


# ═══════════════════════════════════════════════════════════════════════
# FA-N57 — the advisory reads the state BEFORE the break
# ═══════════════════════════════════════════════════════════════════════

class TestFAN57TheSquareAdvisorySpeaks:

    def test_levers_default_on(self):
        assert SE.SQUARE_ADVISORY_READS_THE_PRE_BREAK_STATE is True
        assert C.ROUT_SURVIVORS_NEVER_EXCEED_THE_ARMY is True
        assert DDF.OVERRIDE_OUTCOME_IS_STAMPED_AT_RESOLUTION is True

    def test_a_support_order_from_square_names_the_broken_square(self, client):
        c, w = client
        soult = w.get_marshal("Soult")
        soult.square_formation = True
        r = _post(c, "Soult, support Ney")
        assert r.get("success"), r.get("message")
        msg = r.get("message", "")
        assert "Berthier" in msg and "broken square" in msg.lower() and "gone" in msg.lower(), msg
        assert "cannot march to reinforce" not in msg, "the old sentence's false clause"
        assert soult.square_formation is False

    def test_no_square_no_advisory(self, client):
        c, w = client
        w.get_marshal("Soult").square_formation = False
        r = _post(c, "Soult, support Ney")
        assert r.get("success"), r.get("message")
        assert "Berthier" not in r.get("message", "") or "square" not in r.get("message", "").lower()

    def test_the_lever_down_is_silent(self, monkeypatch, client):
        """⚠ Slice 16c's square-break NOTICE ("[Square broken — …]") prints
        regardless; the ADVISORY is Berthier's sentence, and that is what
        the lever silences."""
        monkeypatch.setattr(SE, "SQUARE_ADVISORY_READS_THE_PRE_BREAK_STATE", False)
        c, w = client
        w.get_marshal("Soult").square_formation = True
        r = _post(c, "Soult, support Ney")
        assert r.get("success"), r.get("message")
        msg = r.get("message", "")
        assert "has broken square to take up" not in msg, "the advisory must be dead with the lever down"
        assert "in square formation" not in msg, "and the old dead sentence must not resurrect on the live attribute"


# ═══════════════════════════════════════════════════════════════════════
# FA-N70 + the third site — no raw enum in player copy
# ═══════════════════════════════════════════════════════════════════════

class TestFAN70NoRawEnumInPlayerCopy:

    @pytest.mark.parametrize("cmd,word", [("MOVE_TO", "march"), ("HOLD", "hold"),
                                          ("SUPPORT", "support"), ("PURSUE", "pursue")])
    def test_form_square_names_the_cancelled_order_in_english(self, client, cmd, word):
        c, w = client
        davout = w.get_marshal("Davout")
        davout.strategic_order = StrategicOrder(
            command_type=cmd, target="Mack" if cmd == "PURSUE" else "Munich",
            target_type="marshal" if cmd == "PURSUE" else "region",
            started_turn=1, original_command="x", path=["Munich"])
        r = _post(c, "Davout, form square")
        assert r.get("success"), r.get("message")
        msg = r.get("message", "")
        assert cmd not in msg, msg
        assert word in msg.lower() and "cancelled" in msg, msg

    def test_the_helper_reads_both_vocabularies(self):
        assert SE.order_verb_display("MOVE_TO") == "march"
        assert SE.order_verb_display("PURSUE") == "pursue"
        assert SE.order_verb_display("HOLD") == "hold"
        assert SE.order_verb_display("attack") == action_display_name("attack"), (
            "a plain action still reads through ACTION_DISPLAY")

    def test_the_defiance_notice_and_the_square_message_read_the_helper(self):
        se = (REPO / "backend" / "commands" / "strategic_executor.py").read_text(encoding="utf-8")
        assert "defied your order to {order_verb_display(strategic_type)}" in se
        ce = (REPO / "backend" / "commands" / "combat_executor.py").read_text(encoding="utf-8")
        assert 'f" Strategic order ({old_order.command_type}) cancelled."' not in ce
        assert "order_verb_display(old_order.command_type)" in ce

    def test_no_player_sentence_interpolates_a_raw_command_type(self):
        """Census over the executors and game logic: no PLAYER f-string prints
        `…command_type` bare. Debug prints (`[STRATEGIC] …`) and the
        unreachable "Unknown strategic command" error are not player copy."""
        bad = []
        for path in list((REPO / "backend" / "commands").glob("*.py")) + list((REPO / "backend" / "game_logic").glob("*.py")):
            src = path.read_text(encoding="utf-8")
            # Review round (L3-8): `strategic_type` is the same enum one frame up.
            for m in re.finditer(r'f"([^"\n]*\{(?:(?:old_order|order)\.command_type|strategic_type)\}[^"\n]*)"', src):
                literal = m.group(1)
                # Debug prints open with a bracketed tag, sometimes indented
                # (`  [DEFIANCE] …`) — review round L3-8 widened the regex and
                # the indent slipped past `startswith`.
                if literal.lstrip().startswith("[") or "Unknown strategic command" in literal:
                    continue
                bad.append((path.name, literal[:80]))
        assert bad == [], bad


# ═══════════════════════════════════════════════════════════════════════
# FA-N55 — the fort percent is scaled once
# ═══════════════════════════════════════════════════════════════════════

class TestFAN55TheFortPercentIsScaledOnce:

    def test_every_producer_writes_an_int_percent(self):
        """Producer half, as a census over the two producer files: every
        `fortification_old`/`fort_old` write wraps `int(… * 100)`. (The
        behaviour is already pinned at 25 / 16 / 12 by the fort-degradation
        suites; this pins the SHAPE the client relies on.)"""
        for rel in ("backend/game_logic/combat.py", "backend/commands/combat_executor.py"):
            src = (REPO / rel).read_text(encoding="utf-8")
            writes = re.findall(r'"(?:fortification_old|fort_old)":\s*([^,\n]+)', src)
            assert writes, rel
            for expr in writes:
                expr = expr.strip()
                if expr == "fortification_old":
                    # The ONE raw-fraction write: the dict fed to
                    # `generate_bombardment_report` (Berthier's report is
                    # computed on the fraction by design — REPRO_L's
                    # "do NOT divide in the backend" is about this feed).
                    continue
                if "battle_result.get(" in expr:
                    continue  # a copy of an already-int result field
                assert "int(" in expr and "* 100" in expr, (rel, expr)

    def test_the_client_never_rescales(self):
        src = _strip_gd_comments((GD / "enemy_phase_dialog.gd").read_text(encoding="utf-8"))
        offenders = [ln.strip() for ln in src.splitlines() if "fort" in ln and "* 100" in ln]
        assert offenders == [], offenders
        assert 'event.get("fortification_old", 0)' in src and 'event.get("fort_old", 0)' in src, (
            "the reads must still exist — the pin is about the SCALE, not about deleting the arms")


# ═══════════════════════════════════════════════════════════════════════
# FA-N64 — the override's outcome is stamped where it resolves
# ═══════════════════════════════════════════════════════════════════════

class TestFAN64TheOverrideOutcomeIsDelivered:

    def _in_transit(self, w, target, ptype, snapshot):
        from backend.game_logic import diplomacy as DIP
        w.talleyrand_override_history = [{"proposal_type": ptype, "override_result": "pending",
                                          "turn": int(w.current_turn)}]
        w.proposal_in_transit = {
            "target": target,
            "proposal": {"type": ptype, "proposer_nation": "France", "target_nation": target,
                         "demands": [], "sweeteners": []},
            "turn_sent": int(w.current_turn) - 1, "dp_cost": 2,
            "acceptance_snapshot": snapshot, "diplomatic_state_at_send": "PEACE",
        }
        w.talleyrand_state = "IN_TRANSIT"
        return DIP

    def test_the_send_site_records_pending_not_a_verdict(self):
        src = (REPO / "backend" / "commands" / "diplomatic_executor.py").read_text(encoding="utf-8")
        calls = re.findall(r'record_override\(world, proposal_type, "([a-z_]+)"\)', src)
        assert calls == ["pending"], calls

    def test_an_accepted_and_ratified_override_is_good_news(self, monkeypatch):
        w = _world()
        assert w.get_diplomatic_state("France", "Prussia") == "PEACE"
        # `_ratify_treaty` checks the relation requirement for a player treaty;
        # the boot relation is below a pact's floor, so lift it — the pin is
        # about the VERDICT, not about Prussia's mood.
        w.nation_relations[w._make_diplo_key("France", "Prussia")] = 80
        DIP = self._in_transit(w, "Prussia", "non_aggression", 80)
        monkeypatch.setattr(DIP, "calculate_acceptance",
                            lambda proposal, world, **k: {"outcome": "ACCEPT", "score": 80, "feedback": ""})
        _quiet(w._process_proposal_in_transit)
        assert w.get_diplomatic_state("France", "Prussia") == "NON_AGGRESSION", "the treaty must have signed"
        assert w.talleyrand_override_history[-1]["override_result"] == "good"
        note = DDF.get_override_dispatch_note(w)
        assert note and "pessimistic" in note.lower()
        d = _quiet(build_morning_dispatch, w)
        assert d.get("talleyrand_override_note") == note

    def test_agreed_in_principle_but_unratified_is_bad_news(self, monkeypatch):
        """ACCEPT that cannot ratify (a pact with a court we are at WAR
        with) is re-stamped bad — the failed-ratification arm."""
        w = _world()
        assert w.get_diplomatic_state("France", "Austria") == "WAR"
        DIP = self._in_transit(w, "Austria", "non_aggression", 80)
        monkeypatch.setattr(DIP, "calculate_acceptance",
                            lambda proposal, world, **k: {"outcome": "ACCEPT", "score": 80, "feedback": ""})
        _quiet(w._process_proposal_in_transit)
        assert w.talleyrand_override_history[-1]["override_result"] == "bad"

    def test_a_rejected_override_is_bad_news(self, monkeypatch):
        w = _world()
        DIP = self._in_transit(w, "Prussia", "non_aggression", 5)
        monkeypatch.setattr(DIP, "calculate_acceptance",
                            lambda proposal, world, **k: {"outcome": "REJECT", "score": 5, "feedback": ""})
        _quiet(w._process_proposal_in_transit)
        assert w.talleyrand_override_history[-1]["override_result"] == "bad"
        note = DDF.get_override_dispatch_note(w)
        assert note and "prescient" in note.lower()

    def test_a_pending_or_legacy_entry_is_not_reported(self):
        w = _world()
        for legacy in ("pending", "override"):
            w.talleyrand_override_history = [{"proposal_type": "peace", "override_result": legacy,
                                              "turn": int(w.current_turn)}]
            assert DDF.get_override_dispatch_note(w) is None

    def test_the_lever_down_leaves_the_verdict_unwritten(self, monkeypatch):
        monkeypatch.setattr(DDF, "OVERRIDE_OUTCOME_IS_STAMPED_AT_RESOLUTION", False)
        w = _world()
        DIP = self._in_transit(w, "Prussia", "non_aggression", 80)
        monkeypatch.setattr(DIP, "calculate_acceptance",
                            lambda proposal, world, **k: {"outcome": "ACCEPT", "score": 80, "feedback": ""})
        _quiet(w._process_proposal_in_transit)
        assert w.talleyrand_override_history[-1]["override_result"] == "pending", "the defect: never rewritten"
        assert DDF.get_override_dispatch_note(w) is None

    def test_both_renderers_print_the_note(self):
        for name in ("main.gd", "dispatch_view.gd"):
            src = _strip_gd_comments((GD / name).read_text(encoding="utf-8"))
            assert '"talleyrand_override_note"' in src, name


# ═══════════════════════════════════════════════════════════════════════
# FA-N69 + FA-N71 — every key one renderer reads, the other reads too
# ═══════════════════════════════════════════════════════════════════════

class TestFAN69N71RendererParity:

    # Keys the producer writes that are DELIBERATELY not rendered by the
    # dispatch re-read screen, each with its reason.
    ALLOWLIST = {
        "turn_limit_warning",       # main.gd-only by design: sandbox worlds never end (EC-6)
        "talleyrand_discovery",     # delivered as the sabotage-discovery POPUP + a dispatch event + a rail notice
        "talleyrand_redemption",    # PL-23 deleted the trust system; written only as None
    }

    @staticmethod
    def _producer_keys():
        src = (REPO / "backend" / "game_logic" / "dispatch.py").read_text(encoding="utf-8")
        return set(re.findall(r'dispatch\["([a-z_]+)"\]\s*=', src))

    def test_the_census_sees_the_conditional_keys(self):
        keys = self._producer_keys()
        for k in ("war_objectives", "talleyrand_override_note", "coalition_status", "talleyrand_report"):
            assert k in keys, k

    def test_the_stripper_keeps_bbcode_strings(self):
        """The first cut split on `#` and emptied every `[color=#…` line."""
        kept = _strip_gd_comments('\tbbcode += "[color=#" + Utils.COLOR_INFO + "]x[/color]"\n\t# a comment\n')
        assert "[color=#" in kept and "a comment" not in kept

    def test_every_key_main_reads_the_view_reads(self):
        keys = self._producer_keys()
        main = _strip_gd_comments((GD / "main.gd").read_text(encoding="utf-8"))
        view = _strip_gd_comments((GD / "dispatch_view.gd").read_text(encoding="utf-8"))
        main_reads = {k for k in keys if f'"{k}"' in main}
        # Review round (L3-1): the WAR PURPOSE read itself, not only its header
        # — a main.gd that stopped reading `war_objectives` behind a dead
        # header was green.
        assert {"talleyrand_report", "coalition_status", "war_objectives",
                "talleyrand_override_note"} <= main_reads
        missing = sorted(k for k in main_reads - self.ALLOWLIST if f'"{k}"' not in view)
        assert missing == [], f"dispatch_view.gd drops keys main.gd renders: {missing}"

    def test_no_producer_key_is_unrendered_everywhere(self):
        keys = self._producer_keys()
        main = _strip_gd_comments((GD / "main.gd").read_text(encoding="utf-8"))
        view = _strip_gd_comments((GD / "dispatch_view.gd").read_text(encoding="utf-8"))
        orphans = sorted(k for k in keys - self.ALLOWLIST if f'"{k}"' not in main and f'"{k}"' not in view)
        assert orphans == [], f"keys the producer writes and no renderer reads: {orphans}"

    def test_the_view_renders_status_threat_and_purpose(self):
        view = _strip_gd_comments((GD / "dispatch_view.gd").read_text(encoding="utf-8"))
        for needle in ("DIPLOMATIC STATUS", "COALITION THREAT", "WAR PURPOSE"):
            assert needle in view, needle
        main = _strip_gd_comments((GD / "main.gd").read_text(encoding="utf-8"))
        assert "WAR PURPOSE" in main

    def test_the_war_purpose_producer_still_composes_the_row(self):
        """Producer control so the renderer pin cannot be satisfied by breaking the builder."""
        w = _world()
        from backend.game_logic.diplomacy import create_war_objective
        key = w._make_diplo_key("France", "Austria")
        w.war_objectives = {key: {"France": create_war_objective(
            "conquest", "France", "Austria", ["Vienna"], int(w.current_turn))}}
        d = _quiet(build_morning_dispatch, w)
        rows = d.get("war_objectives") or []
        assert rows and "Austria" in rows[0]["text"] and "Vienna" in rows[0]["text"], d.get("war_objectives")


# ═══════════════════════════════════════════════════════════════════════
# FA-N32 — a rout never leaves more men than the army had
# ═══════════════════════════════════════════════════════════════════════

class TestFAN32ARoutNeverLeavesMoreMenThanItHad:

    def test_the_pure_helper(self):
        assert C.rout_survivors(900, 0.05) == 900, "a sub-1000 army keeps at most what it had"
        assert C.rout_survivors(20000, 0.05) == 1000, "the flat floor still binds above it"
        assert C.rout_survivors(40000, 0.10) == 4000
        assert C.rout_survivors(0, 0.10) == 0

    def test_the_helper_lever_down_reproduces_the_net_gain(self, monkeypatch):
        monkeypatch.setattr(C, "ROUT_SURVIVORS_NEVER_EXCEED_THE_ARMY", False)
        assert C.rout_survivors(900, 0.05) == 1000, "the defect: 900 men shatter into 1,000"

    def test_all_three_sites_read_the_helper(self):
        ws = (REPO / "backend/models/world_state.py").read_text(encoding="utf-8")
        ce = (REPO / "backend/commands/combat_executor.py").read_text(encoding="utf-8")
        for bare in ("max(1000, int(enemy.strength * survival_rate))",
                     "max(1000, int(marshal.strength * survival_rate))",
                     "min(old_strength, max(1000, int(old_strength * survival_rate)))"):
            assert bare not in ws and bare not in ce, bare
        assert ws.count("rout_survivors(") >= 2 and "rout_survivors(" in ce

    def _surround(self, monkeypatch, defender_strength=900):
        """Ney (reckless cavalry, legacy fixture) auto-charges Wellington, who
        has NO retreat — the arm the clamp exists for. ~1:1 odds so the
        defender is beaten, not annihilated (12,000 vs 900 never reaches it)."""
        w = _legacy()
        ney, well = w.get_marshal("Ney"), w.get_marshal("Wellington")
        ney.recklessness = 4
        ney.strength = 1200
        well.location = "Belgium"
        well.strength = defender_strength
        well.morale = 20
        monkeypatch.setattr(WorldState, "get_safe_retreat_destination", lambda self, *a, **k: None)
        return w, ney, well

    def test_the_auto_charge_arm_never_grows_the_defender(self, monkeypatch):
        reached = 0
        for seed in range(1, 13):
            w, ney, well = self._surround(monkeypatch)
            random.seed(seed)
            _quiet(w._process_reckless_cavalry_turn_start)
            if well.broken and well.strength > 0:
                reached += 1
                assert well.strength <= 900, (seed, well.strength)
        assert reached >= 6, f"the shatter arm was reached on only {reached}/12 seeds — the pin is vacuous"

    def test_the_lever_down_reproduces_the_gain_on_the_same_seeds(self, monkeypatch):
        monkeypatch.setattr(C, "ROUT_SURVIVORS_NEVER_EXCEED_THE_ARMY", False)
        grew = 0
        for seed in range(1, 13):
            w, ney, well = self._surround(monkeypatch)
            random.seed(seed)
            _quiet(w._process_reckless_cavalry_turn_start)
            if well.broken and well.strength == 1000:
                grew += 1
        assert grew >= 6, f"the defect reproduced on only {grew}/12 seeds"
