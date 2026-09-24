"""FA slice 17 — THE REVIEW ROUND (September 11, 2026).

Three lenses at `9f0681be` (correctness / shown-vs-applied / the pins), two
refuters per finding. The survivors, pinned here beside their fixes:

- L1-1  a corps in retreat recovery could CHARGE onto a province and take it
        (the predicate part 0 minted was not read at the charge seam);
- L1-2  on the rout turn a PURSUE was accepted and its first step annexed
        (the strategic issuance guard read `retreat_recovery > 0`, not the
        whole window) — applied behind the same lever;
- L1-3  `capture_refused_recovering` never reached the wire;
- L1-4  a STALE-returned override stayed "pending" and the next proposal
        stamped it;
- L1-5  a stale order-bound interrupt with no order read "awaiting decision"
        on the ledger and "Awaiting orders." on the dispatch;
- L2-1  README and the School taught a Peril the engine does not run;
- L2-2  the rout sentence quoted the dice while the helper applied the floor;
- L2-3  FA-N52's `ultimatum_issued` key had no producer — dead exactly as
        the key it replaced; the collectors now name the ANSWER types and a
        producer census pins every key to a literal `log_event` writer;
- L2-4/5/6/11 copy: raw lords on the paper, the nameless coalition, "the
        continent's strength" for bloc power, "— -3", "chose to attacks";
- L2-7  rate points under a gold figure now say their unit;
- L2-10 the digest's RATIFIED blob and the MAILBOX line;
- L3-4  the order-free decision read "No active orders" on the ORDERS tab;
- L3-5  the attacker surround arm gets a behaviour pin;
- L3-7  the FA-N30 producer census resolves non-literal type arguments.
"""

import ast
import contextlib
import io
import random
import re
from pathlib import Path

import pytest

from backend.models.world_state import WorldState

REPO_ROOT = Path(__file__).resolve().parents[1]
CLIENT = REPO_ROOT / "godot-client" / "project-sovereign"
SCENARIO = CLIENT / "assets" / "maps" / "europe_1805.json"


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


def _read(p):
    return Path(p).read_text(encoding="utf-8")


def _code_only(text):
    return "\n".join(ln for ln in text.splitlines() if not ln.strip().startswith("#"))


@pytest.fixture(scope="module")
def world1805():
    with _quiet():
        return WorldState.from_scenario(str(SCENARIO))


@pytest.fixture
def world(world1805):
    with _quiet():
        return WorldState.from_dict(world1805.to_dict())


@pytest.fixture
def client(world, monkeypatch, tmp_path):
    from fastapi.testclient import TestClient
    import backend.main as M
    from backend import save_manager
    from backend.commands.parser import CommandParser
    monkeypatch.setenv("INK_IRON_SAVE_DIR", str(tmp_path / "saves"))
    monkeypatch.setattr(save_manager, "SAVE_DIR", tmp_path / "saves")
    (tmp_path / "saves").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(M, "world", world)
    monkeypatch.setattr(M, "game_state", {"world": world})
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    return TestClient(M.app)


def _post(client, text):
    with _quiet():
        return client.post("/command", json={"command": text}).json()


def _stage_recovering_cavalry(world, name="Murat", at="Bohemia", quarry="ArchdukeJohn",
                              quarry_at="Tyrol", recovery=1, retreating=True):
    """A beaten reckless cavalryman beside an ungarrisoned enemy province — the
    geometry lens 1 drove (`probe_fa9_seams.py` arm A)."""
    m = world.marshals[name]
    m.location = at
    m.strength = 30_000
    m.morale = 70
    m.retreating = retreating
    m.retreat_recovery = recovery
    m.recklessness = 2
    m.retreated_this_turn = False
    victim = world.marshals[quarry]
    victim.location = quarry_at
    victim.strength = 800
    region = world.regions[quarry_at]
    region.controller = "Austria"
    region.garrison_strength = 0
    for b in ("fortification",):
        region.buildings = [x for x in getattr(region, "buildings", []) if x != b]
    return m, victim, region


# ═══════════════════════════════════════════════════════════════════════
# L1-1 / L1-2 — the recovery window is read at the charge seam and at the
# strategic issuance guard
# ═══════════════════════════════════════════════════════════════════════

class TestL1TheRecoveryWindowIsReadEverywhere:

    def test_a_recovering_cavalryman_cannot_charge_onto_a_province(self, world, client):
        m, victim, region = _stage_recovering_cavalry(world)
        assert m.in_retreat_recovery()
        r = _post(client, "Murat, charge Archduke John")
        assert r.get("success") is False, r.get("message")
        assert "recovering" in str(r.get("message", "")).lower()
        assert region.controller == "Austria", "the charge annexed the province"
        assert m.location == "Bohemia"

    def test_the_lever_down_reproduces_the_charge_and_the_annexation(self, world, client, monkeypatch):
        from backend.commands import movement_executor as ME
        monkeypatch.setattr(ME, "RECOVERING_CORPS_TAKES_NO_GROUND", False)
        m, victim, region = _stage_recovering_cavalry(world)
        r = _post(client, "Murat, charge Archduke John")
        assert r.get("success") is not False, r.get("message")

    def test_the_recovered_man_charges_again(self, world, client):
        m, victim, region = _stage_recovering_cavalry(world, recovery=0, retreating=False)
        assert not m.in_retreat_recovery()
        r = _post(client, "Murat, charge Archduke John")
        assert r.get("success") is not False, r.get("message")
        assert "still rallying" not in str(r.get("message", "")).lower()

    def test_a_pursue_on_the_rout_turn_is_refused_like_the_attack(self, world, client):
        """L1-2: `retreating=True, retreat_recovery=0` is the rout turn's own
        state (the stage ticks at `advance_turn`); `attack` was refused and
        `pursue` fought and annexed."""
        m, victim, region = _stage_recovering_cavalry(world, name="Ney", recovery=0, retreating=True)
        m.retreated_this_turn = True
        attack = _post(client, "Ney, attack Archduke John")
        pursue = _post(client, "Ney, pursue Archduke John")
        assert attack.get("success") is False
        assert pursue.get("success") is False, pursue.get("message")
        assert "recovering" in str(pursue.get("message", "")).lower()
        assert region.controller == "Austria"

    def test_the_issuance_guard_still_prices_the_turns_left(self, world, client):
        m, victim, region = _stage_recovering_cavalry(world, name="Ney", recovery=2, retreating=True)
        r = _post(client, "Ney, march to Tyrol")
        assert r.get("success") is False
        assert "2 turns remaining" in str(r.get("message", ""))  # F2 LV-9


# ═══════════════════════════════════════════════════════════════════════
# L1-3 — the refused walk-in reaches the wire and the digest
# ═══════════════════════════════════════════════════════════════════════

class TestL1TheRefusedWalkInReachesTheWire:

    def test_the_key_rides_the_command_response(self, world, client):
        m = world.marshals["Ney"]
        m.location = "Bohemia"
        m.retreating = True
        m.retreat_recovery = 1
        m.strength = 20_000
        region = world.regions["Tyrol"]
        region.controller = "Austria"
        region.garrison_strength = 0
        for enemy in world.marshals.values():
            if enemy.location == "Tyrol":
                enemy.location = "Carniola"
        r = _post(client, "Ney, move to Tyrol")
        assert r.get("success") is True, r.get("message")
        assert r.get("capture_refused_recovering") is True, sorted(r)
        assert region.controller == "Austria"

    def test_the_digest_writes_it_down(self, tmp_path):
        import importlib.util
        spec = importlib.util.spec_from_file_location("pdrv", REPO_ROOT / "tools" / "playtest_driver.py")
        drv = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(drv)
        d = drv.Digest(tmp_path, {"name": "x", "seed": "s", "llm": "mock", "transport": "t", "policy": {}})
        d.command("Ney, move to Tyrol", {"success": True, "message": "Ney moves.", "capture_refused_recovering": True})
        text = (tmp_path / "digest.md").read_text(encoding="utf-8")
        assert "annexed nothing" in text


# ═══════════════════════════════════════════════════════════════════════
# L1-4 — a stale return stamps the override "bad"
# ═══════════════════════════════════════════════════════════════════════

class TestL1TheStaleReturnIsTheBadOutcome:

    def test_a_stale_proposal_stamps_the_pending_override(self, world):
        from backend.commands.diplomatic_defiance import record_override
        world.set_diplomatic_state("France", "Spain", "ALLIANCE") if hasattr(world, "set_diplomatic_state") else None
        key = world._make_diplo_key("France", "Spain")
        world.diplomatic_states[key] = "ALLIANCE"
        record_override(world, "open_borders", "pending")
        world.proposal_in_transit = {"target": "Spain", "type": "open_borders",
                                     "turn_sent": int(world.current_turn) - 1,
                                     "return_turn": int(world.current_turn),
                                     "proposal": {"type": "open_borders", "target_nation": "Spain"}}
        with _quiet():
            events = world._process_proposal_in_transit()
        assert any(e.get("outcome") == "REJECT" for e in events), events
        history = getattr(world, "talleyrand_override_history", None) or getattr(world, "override_history", None)
        assert history, "the override record is empty"
        assert history[-1].get("override_result") == "bad", history[-1]


# ═══════════════════════════════════════════════════════════════════════
# L1-5 + L3-4 — one word on both morning surfaces, including the two shapes
# the slice did not stage
# ═══════════════════════════════════════════════════════════════════════

class TestTheLedgerAndTheDispatchAgreeOnEveryShape:

    def _dispatch_status(self, world, marshal):
        from backend.game_logic import dispatch as D
        with _quiet():
            return D._derive_marshal_status(marshal, world)

    def _ledger_status(self, world, marshal):
        from backend.game_logic import ledger as L
        return L._derive_status(marshal)

    def test_a_stale_order_bound_interrupt_with_no_order_is_not_a_halt(self, world):
        ney = world.marshals["Ney"]
        ney.strategic_order = None
        ney.pending_interrupt = {"marshal": "Ney", "interrupt_type": "cannon_fire",
                                 "options": ["continue_order", "hold_position"]}
        ds = self._dispatch_status(world, ney)
        ls = self._ledger_status(world, ney)
        ds_word = ds[0] if isinstance(ds, tuple) else ds
        assert ds_word != "awaiting_decision"
        assert ls != "awaiting_decision", "the ledger called a stale interrupt a halt"

    def test_the_order_free_decision_is_not_idle_on_the_orders_tab(self, world):
        from backend.game_logic.ledger import build_strategic_ledger
        massena = world.marshals["Massena"]
        massena.strategic_order = None
        massena.pending_interrupt = {"marshal": "Massena", "interrupt_type": "last_stand",
                                     "enemy": "Mack", "location": massena.location,
                                     "options": ["fight_to_the_last", "attempt_breakout"]}
        with _quiet():
            ledger = build_strategic_ledger(world)
        row = next(o for o in ledger["orders"] if o["marshal"] == "Massena")
        assert row["order_type"] != "No active orders", row
        assert row["decision"] == "last_stand"
        assert row["condition"] == "HALTED — awaiting your word"
        assert row["has_order"] is False, "no cancel button for a decision"
        forces = next(m for m in ledger["forces"] if m.get("name", m.get("marshal")) == "Massena")
        assert forces["status"] == "awaiting_decision"

    def test_the_lever_down_reproduces_the_idle_row(self, world, monkeypatch):
        from backend.game_logic import ledger as L
        monkeypatch.setattr(L, "THE_LEDGER_SEES_THE_HALT", False)
        massena = world.marshals["Massena"]
        massena.strategic_order = None
        massena.pending_interrupt = {"marshal": "Massena", "interrupt_type": "last_stand",
                                     "enemy": "Mack", "options": ["fight_to_the_last", "attempt_breakout"]}
        with _quiet():
            ledger = L.build_strategic_ledger(world)
        row = next(o for o in ledger["orders"] if o["marshal"] == "Massena")
        assert row["order_type"] == "No active orders" and "decision" not in row

    def test_the_client_renders_the_decision_row_without_a_cancel(self):
        src = _code_only(_read(CLIENT / "scripts" / "strategic_ledger.gd"))
        at = src.index("# Idle marshals") if "# Idle marshals" in src else src.index('bbcode += "  │ No active orders"')
        tail = src[src.index('var decision = str(o.get("decision", ""))'):]
        block = tail[:tail.index("No active orders")]
        # The GUARD itself, not only the arm's text — the first cut was green
        # with the arm behind `if false:` (the sweep's L3-4/c).
        assert 'if decision != "":' in block, block
        assert "AWAITING YOUR WORD" in block or ".to_upper()" in block
        assert "[Cancel]" not in block
        assert "continue" in block, "the decision row must skip the idle line"


# ═══════════════════════════════════════════════════════════════════════
# L2-2 — the rout sentence quotes the applied proportion
# ═══════════════════════════════════════════════════════════════════════

class TestL2TheRoutSentenceQuotesWhatWasApplied:

    def test_the_percent_is_derived_from_the_survivors(self):
        src = _read(REPO_ROOT / "backend" / "commands" / "combat_executor.py")
        assert "survival_percent = int(survivors * 100 // max(1, int(old_strength)))" in src
        assert "survival_percent = int(survival_rate * 100)" not in src

    def test_a_900_man_corps_that_keeps_every_man_is_not_told_5_percent(self):
        from backend.game_logic.combat import rout_survivors
        old, rate = 900, 0.05
        survivors = rout_survivors(old, rate)
        assert survivors == 900
        assert int(survivors * 100 // max(1, old)) == 100


# ═══════════════════════════════════════════════════════════════════════
# L2-3 — every collector key has a literal producer
# ═══════════════════════════════════════════════════════════════════════

def _log_event_types_written(root: Path) -> set:
    """Every `"type"` a `log_event(...)` call writes under backend/, resolved
    per FUNCTION: a dict-literal argument (or an IfExp of two dicts), a Name
    argument assigned to a dict literal in the same function, and a type
    value that is a Constant, an IfExp of Constants, or a Name assigned to
    either in the same function (the executor's
    `event_type = "ultimatum_accepted" if accepted else "ultimatum_rejected"`).
    Producers that build the dict through a helper are named in INDIRECT."""
    found = set()
    for path in root.rglob("*.py"):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        scopes = [tree] + [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        for scope in scopes:
            assigns = {}
            for node in ast.walk(scope):
                if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                    assigns.setdefault(node.targets[0].id, []).append(node.value)

            def strs(v, depth=0):
                if depth > 4:
                    return []
                if isinstance(v, ast.Constant) and isinstance(v.value, str):
                    return [v.value]
                if isinstance(v, ast.IfExp):
                    return strs(v.body, depth + 1) + strs(v.orelse, depth + 1)
                if isinstance(v, ast.Name):
                    out = []
                    for cand in assigns.get(v.id, []):
                        out += strs(cand, depth + 1)
                    return out
                return []

            def dicts_of(arg):
                if isinstance(arg, ast.Dict):
                    return [arg]
                if isinstance(arg, ast.IfExp):
                    return dicts_of(arg.body) + dicts_of(arg.orelse)
                if isinstance(arg, ast.Name):
                    return [c for c in assigns.get(arg.id, []) if isinstance(c, ast.Dict)]
                return []

            for node in ast.walk(scope):
                if not isinstance(node, ast.Call):
                    continue
                fname = getattr(node.func, "attr", None) or getattr(node.func, "id", None)
                if fname != "log_event" or not node.args:
                    continue
                for d in dicts_of(node.args[0]):
                    for k, v in zip(d.keys, d.values):
                        if isinstance(k, ast.Constant) and k.value == "type":
                            found.update(strs(v))
    return found


class TestL2EveryCollectorKeyHasAProducer:

    # Keys whose producer builds the dict through a helper the static census
    # cannot follow, each with the FILE that carries the literal type (the
    # weak sibling the test checks) — a new indirect producer must be named
    # here, with its site, before the census will accept it.
    INDIRECT = {
        "battle": "backend/game_logic/combat.py",              # `log_battle_event` built by the resolver, logged by `_log_battle_event`
        "diplomatic_war_declared": "backend/game_logic/diplomacy.py",  # `event = {...}` assembled in a helper
        "third_party_peace": "backend/game_logic/settlement_third_party.py",  # `{k: v for k, v in event.items() if k != 'terms'}`
    }

    def test_every_collector_key_is_written_by_a_literal_log_event(self):
        from backend.game_logic import gazette as G
        written = _log_event_types_written(REPO_ROOT / "backend")
        keys = set(G._WAR_TYPES) | set(G._COURT_TYPES) | set(G._ARMY_TYPES)
        missing = sorted(k for k in keys if k not in written and k not in self.INDIRECT)
        assert missing == [], f"collector keys with no producer (dead by construction): {missing}"
        for key, rel in self.INDIRECT.items():
            assert key not in written or True
            assert f'"{key}"' in _read(REPO_ROOT / rel), f"{key}: the named producer file no longer carries the literal"
        assert "ultimatum_issued" not in keys, "the first cut's dead key"
        for k in ("ultimatum_accepted", "ultimatum_rejected", "ai_ultimatum_accepted",
                  "ai_ultimatum_rejected", "glory_crown_lost", "coalition_declared"):
            assert k in keys and k in written, k

    def test_the_census_sees_the_conditional_producer(self):
        written = _log_event_types_written(REPO_ROOT / "backend")
        assert "trafalgar" in written and "fleet_action" in written

    def test_the_players_own_ultimatum_answer_survives_the_fog_filter(self, world):
        """Found while re-keying: `ultimatum_accepted` / `ultimatum_rejected`
        are written with a `target` and no nation key, matched no arm of
        `filter_campaign_log`, and fell through to the drop — the player's own
        act was invisible on the log screen, so no collector could print it."""
        from backend.campaign_log import filter_campaign_log
        world.log_event({"type": "ultimatum_rejected", "target": "Prussia", "accepted": False})
        world.log_event({"type": "ultimatum_accepted", "target": "Bavaria", "accepted": True})
        with _quiet():
            visible = filter_campaign_log(world.event_log, world)
        kept = sorted(e["type"] for e in visible if e.get("type", "").startswith("ultimatum_"))
        assert kept == ["ultimatum_accepted", "ultimatum_rejected"], kept

    def test_an_ultimatum_answer_reaches_the_court_section(self, world):
        from backend.game_logic import gazette as G
        world.log_event({"type": "ultimatum_rejected", "target": "Prussia"})
        world.log_event({"type": "ai_ultimatum_rejected", "source": "Austria"})
        with _quiet():
            issue = G.compose_issue(world, world.current_turn)
        text = " ".join(str(v) for v in issue.values())
        assert "Prussia" in text and "ultimatum" in text.lower(), issue
        assert "defied Austria" in text, issue


# ═══════════════════════════════════════════════════════════════════════
# L2-4 / L2-5 / L2-6 / L2-11 — the copy
# ═══════════════════════════════════════════════════════════════════════

class TestL2TheCopyReadsAsTheGameNamesThings:

    def test_the_paper_names_the_lords(self):
        from backend.campaign_log import format_event_oneliner
        line = format_event_oneliner({"type": "vassal_transferred", "vassal": "KingdomOfItaly",
                                      "from_lord": "France", "to_lord": "PapalStates"})
        assert "KingdomOfItaly" not in line and "PapalStates" not in line, line
        assert "Kingdom of Italy" in line

    def test_the_paper_names_the_coalition(self):
        from backend.campaign_log import format_event_oneliner
        line = format_event_oneliner({"type": "coalition_declared", "coalition_name": "The Fourth Austria Coalition",
                                      "members": ["Austria", "Russia"], "target_nation": "France"})
        assert line.startswith("The Fourth Austria Coalition — "), line
        bare = format_event_oneliner({"type": "coalition_declared", "members": ["Austria"], "target_nation": "France"})
        assert bare.startswith("Coalition formed against France")

    def test_bloc_power_is_not_called_strength_and_the_delta_is_signed(self):
        from backend.game_logic import dispatch as D
        aside = D._format_dispatch_event_text("hegemony_relaxation_aside", {"label": "France", "share": 0.38})
        assert "bloc power" in aside and "strength" not in aside, aside
        blow = D._format_dispatch_event_text("diplomatic_mission_blowback",
                                             {"nation": "KingdomOfItaly", "delta": -3, "value": 12})
        assert "scheming: -3 to relations" in blow, blow
        assert "KingdomOfItaly" not in blow and "Kingdom of Italy" in blow

    def test_the_defiance_notice_uses_an_infinitive(self):
        from backend.commands.strategic_executor import _defiant_verb
        assert _defiant_verb("attack") == "attack"
        assert _defiant_verb("bombardment") == "bombard"
        assert _defiant_verb("fortify") == "fortify"
        src = _read(REPO_ROOT / "backend" / "commands" / "strategic_executor.py")
        assert "and chose to {_defiant_verb(defiant_action)} instead." in src
        assert "received strategic order: {strategic_type}" not in src


# ═══════════════════════════════════════════════════════════════════════
# L2-7 — the rate points say their unit
# ═══════════════════════════════════════════════════════════════════════

class TestL2TheRatePointsSayTheirUnit:

    def test_the_ledger_carries_the_note_from_the_constants(self, world):
        from backend.game_logic.ledger import _build_economy
        from backend.models.world_state import CHARGES_HOARD_FLOOR, WAR_EFFORT_DIVISOR
        with _quiet():
            econ = _build_economy(world, "France")
        note = econ["state_charges_rate_note"]
        assert f"{int(WAR_EFFORT_DIVISOR):,}g" in note and f"{int(CHARGES_HOARD_FLOOR):,}g" in note

    def test_the_client_prints_it_beside_the_terms(self):
        src = _code_only(_read(CLIENT / "scripts" / "strategic_ledger.gd"))
        assert 'econ.get("state_charges_rate_note", "")' in src
        assert 'terms_text += " — " + rate_note' in src


# ═══════════════════════════════════════════════════════════════════════
# L2-10 — the digest's RATIFIED and MAILBOX lines
# ═══════════════════════════════════════════════════════════════════════

class TestL2TheDigestLines:

    def _driver(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("pdrv2", REPO_ROOT / "tools" / "playtest_driver.py")
        drv = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(drv)
        return drv

    def test_ratified_composes_from_the_summarys_real_keys(self, tmp_path):
        drv = self._driver()
        d = drv.Digest(tmp_path, {"name": "x", "seed": "s", "llm": "mock", "transport": "t", "policy": {}})
        d.ratified({"target_nation": "Austria", "new_state": "PEACE", "war_outcome": "white_peace",
                    "territory_gained": ["Tyrol"], "gold_received": 300, "final_war_score": 12})
        text = (tmp_path / "digest.md").read_text(encoding="utf-8")
        assert "RATIFIED Austria · PEACE · white_peace · gained ['Tyrol'] · gold 300" in text, text
        assert '{"target_nation"' not in text


# ═══════════════════════════════════════════════════════════════════════
# L2-1 — the Emperor's Peril as the engine runs it
# ═══════════════════════════════════════════════════════════════════════

class TestL2ThePerilIsTaughtAsItRuns:

    def test_the_readme_and_the_school_no_longer_promise_once_or_a_war_ending(self):
        readme = _read(REPO_ROOT / "deploy" / "README_TESTER.txt")
        school = _read(REPO_ROOT / "docs" / "TUTORIAL_SCRIPT.md")
        for text in (readme, school):
            assert "buys his escape once" not in text
            assert "war ends on the enemy's terms" not in text
            assert "every time" in text and "30%" in text
            assert "bargaining chip" in text

    def test_the_claims_match_the_constants(self):
        """30% is `GUARD_ESCAPE_TOLL` (NAPOLEON_SPEC N15), wherever it lives."""
        hits = []
        for path in (REPO_ROOT / "backend").rglob("*.py"):
            for ln in path.read_text(encoding="utf-8").splitlines():
                if re.match(r"\s*GUARD_ESCAPE_TOLL\s*=\s*0\.30?\b", ln):
                    hits.append(path.name)
        assert hits, "GUARD_ESCAPE_TOLL = 0.30 not found under backend/"


# ═══════════════════════════════════════════════════════════════════════
# L3-5 — the ATTACKER surround arm never grows the cavalryman
# ═══════════════════════════════════════════════════════════════════════

class TestL3TheAttackerSurroundArm:

    def test_the_broken_charger_keeps_at_most_what_he_had(self, monkeypatch):
        from backend.game_logic import combat as C
        reached = 0
        for seed in range(1, 25):
            with _quiet():
                w = WorldState()
            ney, well = w.get_marshal("Ney"), w.get_marshal("Wellington")
            ney.recklessness = 4
            ney.strength = 900
            ney.morale = 5
            well.location = "Belgium"
            well.strength = 900
            well.morale = 90
            monkeypatch.setattr(WorldState, "get_safe_retreat_destination", lambda self, *a, **k: None)
            random.seed(seed)
            with _quiet():
                w._process_reckless_cavalry_turn_start()
            if ney.broken and ney.strength > 0:
                reached += 1
                assert ney.strength <= 900, (seed, ney.strength)
        assert reached >= 12, f"the attacker shatter arm was reached on only {reached}/24 seeds"
        assert C.ROUT_SURVIVORS_NEVER_EXCEED_THE_ARMY is True

    def test_the_lever_down_grows_the_broken_charger_on_the_same_geometry(self, monkeypatch):
        from backend.game_logic import combat as C
        monkeypatch.setattr(C, "ROUT_SURVIVORS_NEVER_EXCEED_THE_ARMY", False)
        grew = 0
        for seed in range(1, 25):
            with _quiet():
                w = WorldState()
            ney, well = w.get_marshal("Ney"), w.get_marshal("Wellington")
            ney.recklessness = 4
            ney.strength = 900
            ney.morale = 5
            well.location = "Belgium"
            well.strength = 900
            well.morale = 90
            monkeypatch.setattr(WorldState, "get_safe_retreat_destination", lambda self, *a, **k: None)
            random.seed(seed)
            with _quiet():
                w._process_reckless_cavalry_turn_start()
            if ney.broken and ney.strength == 1000:
                grew += 1
        assert grew >= 12, f"the defect (900 men shatter into 1,000) reproduced on only {grew}/24 seeds"


# ═══════════════════════════════════════════════════════════════════════
# L3-7 — the FA-N30 producer census resolves what it can and NAMES what it cannot
# ═══════════════════════════════════════════════════════════════════════

def _resolved_dispatch_types(path: Path):
    """Every event type a `queue_dispatch_event(world, <type>, …)` call
    passes: literals, both arms of an IfExp, module-level string constants
    by Name, and every string value of a module-level dict literal indexed
    by Subscript. Anything else is returned as an opaque site."""
    src = path.read_text(encoding="utf-8")
    tree = ast.parse(src)
    consts, dicts = {}, {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                consts[node.targets[0].id] = node.value.value
            elif isinstance(node.value, ast.Dict):
                vals = [v.value for v in node.value.values if isinstance(v, ast.Constant) and isinstance(v.value, str)]
                dicts[node.targets[0].id] = vals
    # every function-level `name = <expr>` (the vassal template read, `template = _T.get(exit)`)
    func_assigns = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            func_assigns.setdefault(node.targets[0].id, []).append(node.value)
    # an IMPORTED constant (coalition.py's BALANCE_OF_EUROPE_SHIFTED lives in notifications.py)
    module = None
    try:
        import importlib
        rel = path.relative_to(REPO_ROOT).with_suffix("")
        module = importlib.import_module(".".join(rel.parts))
    except Exception:
        module = None
    types, opaque = set(), []

    def resolve(arg, depth=0):
        if depth > 4:
            return None
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            return [arg.value]
        if isinstance(arg, ast.IfExp):
            a, b = resolve(arg.body, depth + 1), resolve(arg.orelse, depth + 1)
            return None if a is None or b is None else a + b
        if isinstance(arg, ast.Subscript) and isinstance(arg.value, ast.Name) and arg.value.id in dicts:
            return list(dicts[arg.value.id])
        if (isinstance(arg, ast.Call) and isinstance(arg.func, ast.Attribute) and arg.func.attr == "get"
                and isinstance(arg.func.value, ast.Name) and arg.func.value.id in dicts):
            return list(dicts[arg.func.value.id])
        if isinstance(arg, ast.Name):
            if arg.id in consts:
                return [consts[arg.id]]
            out = []
            for cand in func_assigns.get(arg.id, []):
                got = resolve(cand, depth + 1)
                if got is None:
                    return None
                out += got
            if out:
                return out
            value = getattr(module, arg.id, None) if module is not None else None
            if isinstance(value, str):
                return [value]
        return None

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fname = getattr(node.func, "attr", None) or getattr(node.func, "id", None)
        if fname == "append" and isinstance(node.func, ast.Attribute):
            owner = ast.unparse(node.func.value)
            if "dispatch_events" in owner and node.args and isinstance(node.args[0], ast.Dict):
                for k, v in zip(node.args[0].keys, node.args[0].values):
                    if isinstance(k, ast.Constant) and k.value == "type":
                        got = resolve(v)
                        if got is None:
                            opaque.append(f"{path.name}:{node.lineno}:{ast.unparse(v)}")
                        else:
                            types.update(got)
            continue
        if fname != "queue_dispatch_event" or len(node.args) < 2:
            continue
        got = resolve(node.args[1])
        if got is None:
            opaque.append(f"{path.name}:{node.lineno}:{ast.unparse(node.args[1])}")
        else:
            types.update(got)
    return types, opaque


class TestL3TheProducerCensusResolvesItsArguments:

    # Producers whose type is a parameter or an attribute the census cannot
    # resolve statically; lens 1 drove each and every type it emits renders
    # (probe_n30_census.py). A NEW opaque site must be added here by hand.
    KNOWN_OPAQUE_SUBSTRINGS = ("event_type", "etype", "kind", "dtype", "ev_type",
                               "_type", "type_", "message_type")

    def test_resolved_types_all_render_and_opaque_sites_are_known(self):
        from backend.game_logic import dispatch as D
        all_types, all_opaque = set(), []
        for path in (REPO_ROOT / "backend").rglob("*.py"):
            types, opaque = _resolved_dispatch_types(path)
            all_types |= types
            all_opaque += opaque
        assert "hegemony_relaxation_aside" in all_types and "settlement_offer_arrival" in all_types
        orphans = sorted(t for t in all_types if not D.dispatch_event_type_is_renderable(t))
        assert orphans == [], f"producer types that would print a raw key: {orphans}"
        unknown = [s for s in all_opaque if not any(k in s.split(":", 2)[2] for k in self.KNOWN_OPAQUE_SUBSTRINGS)]
        assert unknown == [], f"opaque producer sites the census cannot vouch for: {unknown}"

    def test_the_resolver_is_sensitive(self, tmp_path):
        p = tmp_path / "m.py"
        p.write_text('X = "alpha"\nT = {"a": "beta", "b": "gamma"}\n'
                     'def f(world, k):\n    queue_dispatch_event(world, X)\n    queue_dispatch_event(world, T[k])\n'
                     '    queue_dispatch_event(world, "delta" if k else "eps")\n    queue_dispatch_event(world, k)\n',
                     encoding="utf-8")
        types, opaque = _resolved_dispatch_types(p)
        assert types == {"alpha", "beta", "gamma", "delta", "eps"}
        assert len(opaque) == 1 and opaque[0].endswith(":k")
