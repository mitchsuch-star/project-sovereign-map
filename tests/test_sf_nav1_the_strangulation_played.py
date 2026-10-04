"""Score Finish Step 6 "the chest and the sea" (October 4, 2026) — SF-NAV-1 "The
strangulation, played", SF-V6 (the descent arm's stale precondition), SF-V7
(the Charges forecast — an instrument defect), SF6-X1 (found playing the
descent arm).

* SF6-X1 — a confirmed sea expedition left the marshal's standing order
  standing: Oudinot, landed at Munster, "marches to Ulster. 7 regions to
  Normandy" — the march that brought him to the yard walked him off his own
  beachhead.
* SF-V6 — the descent arm commissioned Oudinot on loop 3 behind three keels
  and the treasury could not bear it; every later line named a man who did
  not exist.
* SF-V7 — the forecast Charges of Empire equal the bill to the gold on a
  turn whose end fights no battle; the "one tick low" reading compared the
  quote with the NEXT turn's forecast (the `/ledger` read after an end turn),
  never with what was billed. The one gap the game owns — the enemy phase's
  battles, fought before the bill is drawn — the reader names.
* SF-NAV-1 — the arm and its probe.

Every behaviour pin drives the real path on the shipped 1805 board and flips
with its lever where it has one.
"""

from __future__ import annotations

import json
import pathlib
import random
import sys

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.commands import naval_executor as NE
from backend.commands.parser import CommandParser
from backend.models.marshal import StrategicOrder

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
SCRIPTS = ROOT / "tools" / "playtest_scripts"
SCENARIO = ROOT / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"


@pytest.fixture
def shipped(monkeypatch):
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    M._reset_world_state()
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    return TestClient(M.app), M.world


def post(client, command):
    return client.post("/command", json={"command": command}).json()


# ═══════════════════════ SF6-X1 — sailing ends the standing order ═══════════════════════

def _embarkable(world):
    """Lannes trimmed to the transports' lift, standing at the Normandy yard
    under a standing march — the descent arm's shape."""
    lannes = world.marshals["Lannes"]
    lannes.strength = 5000
    lannes.location = "Normandy"
    lannes.strategic_order = StrategicOrder(
        command_type="MOVE_TO", target="Brittany", target_type="region",
        started_turn=int(world.current_turn), original_command="march to Brittany",
        path=["Brittany"])
    return lannes


class TestSailingEndsTheStandingOrder:
    def test_a_confirmed_expedition_clears_the_march(self, shipped):
        client, world = shipped
        lannes = _embarkable(world)
        r = post(client, "land Lannes in Munster confirmed")
        assert r.get("success") is not False, r.get("message")
        assert lannes.strategic_order is None

    def test_the_quote_leaves_the_march(self, shipped):
        client, world = shipped
        lannes = _embarkable(world)
        r = post(client, "land Lannes in Munster")
        assert r.get("state") == "awaiting_clarification" or "drawn up" in r.get("message", "")
        assert lannes.strategic_order is not None
        assert lannes.strategic_order.target == "Brittany"

    def test_lever_down_the_march_survives_the_crossing(self, shipped, monkeypatch):
        client, world = shipped
        lannes = _embarkable(world)
        monkeypatch.setattr(NE, "SAILING_ENDS_THE_STANDING_ORDER", False)
        post(client, "land Lannes in Munster confirmed")
        assert lannes.strategic_order is not None


# ═══════════════════════ SF-V7 — the quote is the bill ═══════════════════════

class TestTheChargesQuoteIsTheBill:
    """The bill is drawn on the same pre-income chest the quote reads. The one
    gap the game owns is the end turn's own battles: the enemy phase fights
    before the income phase draws the bill, so a battle there moves the chest
    (its Butcher's Bill) and the campaign's dead (the pensions term) after the
    quote was read — measured on the boot board with the enemy phase's dice
    seeded, 633 quoted against 673 billed after a 267-gold Butcher's Bill and
    seven more points of pensions."""

    def _end_turn_bill(self, client, world):
        from backend.game_logic import ledger as L
        eco = L._build_economy(world, world.player_nation)
        quoted = (int(eco.get("state_charges", 0) or 0), int(eco.get("laws", 0) or 0))
        random.seed(10_000)   # the enemy phase's dice — the M7 per-turn re-seed idiom
        r = post(client, "end turn")
        ends = [e for e in (r.get("events") or [])
                if isinstance(e, dict) and e.get("type") == "turn_end"]
        assert ends, "the end turn carried no turn_end event"
        applied = (int(ends[0].get("state_charges", 0) or 0),
                   int(ends[0].get("laws", 0) or 0))
        return quoted, applied, int(ends[0].get("materiel", 0) or 0)

    def test_a_battle_free_end_turn_bills_the_quote_to_the_gold(self, shipped):
        client, world = shipped
        from backend.game_logic.diplomacy import set_diplomatic_state
        for court in list(world.get_nations_at_war_with(world.player_nation)):
            set_diplomatic_state(world, world.player_nation, court, "PEACE", "test")
        assert not world.get_nations_at_war_with(world.player_nation)
        world.gold = 20000   # well above the hoard floor, so the Charges draw
        quoted, applied, materiel = self._end_turn_bill(client, world)
        assert quoted[0] > 0, "no Charges drawn — the pin would prove nothing"
        assert materiel == 0, "a battle in the end turn — the pin would prove nothing"
        assert applied == quoted

    def test_the_boot_war_end_turn_fights_before_the_bill(self, shipped):
        """The boot board at war: the enemy phase fights, the Butcher's Bill is
        paid inside the end turn, and the bill moves off the quote — the case
        the reader EXPLAINS rather than passes."""
        client, world = shipped
        world.gold = 20000
        quoted, applied, materiel = self._end_turn_bill(client, world)
        assert materiel > 0
        assert applied != quoted

    def test_the_driver_records_the_applied_bill(self, tmp_path):
        from tools import playtest_driver as driver
        meta = {"name": "t", "seed": "historical", "llm": "mock",
                "transport": "in-process", "policy": {}}
        digest = driver.Digest(tmp_path, meta)
        response = {"events": [{"type": "turn_end", "old_turn": 7, "new_turn": 8,
                                "state_charges": 1234, "laws": 56, "materiel": 78}]}
        digest.applied_bill(response)
        digest.applied_bill(response)   # once per ended turn
        rows = [json.loads(line) for line in
                (tmp_path / "digest.jsonl").read_text(encoding="utf-8").splitlines()
                if line.strip()]
        rows = [r for r in rows if r.get("kind") == "applied_bill"]
        assert rows == [{"kind": "applied_bill", "turn": 7, "charges": 1234,
                         "laws": 56, "materiel": 78}]


class TestTheC3Rule:
    """`economy_c3_verdict` — rows are (turn, quoted charges, applied, quoted
    laws, applied, materiel)."""

    def _verdict(self, rows):
        from tools import _score_probes as P
        return P.economy_c3_verdict(rows)

    def test_battle_free_turns_that_match_pass(self):
        v = self._verdict([(3, 400, 400, 120, 120, 0), (4, 410, 410, 120, 120, 0)])
        assert v["measured"] is True and v["pass"] is True, v

    def test_a_battle_free_mismatch_fails(self):
        v = self._verdict([(3, 400, 400, 120, 120, 0), (4, 410, 450, 120, 120, 0)])
        assert v["pass"] is False and "mismatches on battle-free turns" in v["evidence"]

    def test_a_laws_mismatch_fails_too(self):
        v = self._verdict([(3, 400, 400, 120, 140, 0)])
        assert v["pass"] is False

    def test_a_fought_turn_is_explained_not_failed(self):
        v = self._verdict([(3, 400, 400, 120, 120, 0), (4, 633, 673, 0, 0, 268)])
        assert v["pass"] is True and "explained by the end turn's own battles" in v["evidence"]
        assert "268" in v["evidence"]

    def test_only_fought_turns_prove_nothing(self):
        v = self._verdict([(4, 633, 673, 0, 0, 268), (5, 640, 640, 0, 0, 90)])
        assert v["measured"] is False


# ═══════════════════════ SF-V6 — the descent arm stages its landing ═══════════════════════

class TestTheDescentArmStagesItsLanding:
    def _loops(self):
        d = json.loads((SCRIPTS / "naval_descent.json").read_text(encoding="utf-8"))
        return {int(k): v for k, v in d["turns"].items()}

    def test_the_purse_is_spared_before_the_commission(self):
        loops = self._loops()
        commission = min(k for k, v in loops.items()
                         if any(line.startswith("commission ") for line in v))
        assert commission >= 4, "France's boot purse cannot bear a commission sooner"
        spends = ("build ships", "recruit ", "commission ", "buy substitutes")
        for k in range(1, commission):
            assert not any(line.startswith(spends) for line in loops.get(k, [])), k

    def test_the_corps_marches_to_a_french_yard_and_sails_next(self):
        loops = self._loops()
        commission = min(k for k, v in loops.items()
                         if any(line.startswith("commission ") for line in v))
        march = next(line for line in loops[commission] if "march to" in line)
        yard = march.rsplit("march to", 1)[1].strip()
        navies = json.loads(SCENARIO.read_text(encoding="utf-8"))["navies"]
        assert yard in navies["France"]["dockyards"]
        assert any(line.startswith("land ") for line in loops[commission + 1])


class TestTheSeaArmReachesAYard:
    """SF6-X2 (found by Step 6's exit): the SEA arm's road to the Bordelais
    yard crossed Britain's Peninsula corps once the board drifted, so Oudinot
    reached the yard after both landing lines (naval F2: SCRIPT PRECONDITION).
    The arm marches him to a yard one march from Paris, where he is raised."""

    def _loops(self):
        d = json.loads((SCRIPTS / "sr_exit_chunk5_sea.json").read_text(encoding="utf-8"))
        return {int(k): v for k, v in d["turns"].items()}

    def test_the_march_before_the_landing_is_to_a_yard_beside_paris(self, shipped):
        _client, world = shipped
        loops = self._loops()
        land = min(k for k, v in loops.items() if any(line.startswith("land ") for line in v))
        marches = [line for k in range(1, land) for line in loops.get(k, [])
                   if line.startswith("Oudinot, march to")]
        assert marches, "the arm never marches Oudinot to a yard"
        yard = marches[-1].rsplit("march to", 1)[1].strip()
        navies = json.loads(SCENARIO.read_text(encoding="utf-8"))["navies"]
        assert yard in navies["France"]["dockyards"]
        assert yard in world.regions["Paris"].adjacent_regions   # one march: he arrives that loop
        commission = min(k for k, v in loops.items()
                         if any(line.startswith("commission Oudinot") for line in v))
        assert commission < land - 1, "he must stand at the yard a full turn before the quote"


# ═══════════════════════ SF-NAV-1 — the arm and its probe ═══════════════════════

class TestTheStrangulationArm:
    def _script(self):
        return json.loads((SCRIPTS / "sf_nav1_strangulation.json").read_text(encoding="utf-8"))

    def test_the_emperor_stays_out_of_the_fighting(self):
        lines = [line for v in self._script()["turns"].values() for line in v]
        assert not any(line.startswith("Napoleon,") for line in lines)

    def test_the_normandy_beach_is_held(self):
        lines = [line for v in self._script()["turns"].values() for line in v]
        assert "Lannes, march to Normandy" in lines and "Lannes, fortify" in lines

    def test_the_benchmark_keeps_the_war_with_britain_alone(self):
        from tools import score_run as sr
        for name in ("NAV1-H", "NAV1-A", "NAV1-M"):
            argv = sr.ARMS[name]["argv"]
            assert "--decline-from" in argv
            assert argv[argv.index("--decline-from") + 1] == "Britain,Portugal,PapalStates,Naples"
            assert "--save-at" in argv

    def test_the_probe_reads_a_run(self, tmp_path, shipped):
        _client, world = shipped
        from backend.save_manager import save_game
        (tmp_path / "saves").mkdir()
        for t in (1, 2):
            world.current_turn = t
            save_game(world, filepath=tmp_path / "saves" / f"arm_t{t}.json")
        (tmp_path / "digest.md").write_text(
            "## Turn 2 — Early October 1805\n"
            "  - POPUP diplomatic_dialogue: Britain, armistice_losing #9 → reject\n",
            encoding="utf-8")
        from tools import sf_nav1_strangulation_probe as probe
        result = probe.probe(str(tmp_path))
        assert [r["turn"] for r in result["rows"]] == [1, 2]
        assert result["summary"]["peak_closed"] == 10   # the boot System, 10 of 26
        assert result["summary"]["holds_turns"] == []
        assert result["summary"]["britain_envoys"][0]["turn"] == 2
        assert result["summary"]["britain_envoys"][0]["kind"] == "armistice"


class TestTheNavalC3ReaderSeesTheCapture:
    def test_the_capture_question_counts_as_munster_falling(self, tmp_path):
        from tools import score_run as sr
        (tmp_path / "meta.json").write_text(json.dumps({"status": "completed"}), encoding="utf-8")
        (tmp_path / "digest.jsonl").write_text("", encoding="utf-8")
        (tmp_path / "digest.md").write_text(
            "# digest\n\n## Turn 5 — Late November 1805\n"
            "- CMD `land Oudinot in Munster with 5,000 men` → ✓ The expedition is drawn up, Sire: "
            "Oudinot with 5,000 men, Normandy to Munster. The transports slip past unseen 75 times in "
            "100. What moves the odds: a won diversion first (25 in 100) → 95.\n"
            "  - POPUP capture_choice[capture]: Munster, Oudinot → secure\n",
            encoding="utf-8")
        arm = sr.Arm(tmp_path)
        verdict = sr.r_naval_C3({"DESC": arm}, {})
        assert verdict["pass"] is True, verdict
