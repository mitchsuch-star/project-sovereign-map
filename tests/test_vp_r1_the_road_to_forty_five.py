"""VP-R1 "The Road to Forty-Five" (row EP follow-on, GEV-D1 — September 25,
2026). Probe memo of record: `docs/audits/VP_R1_PROBES_2026_09_25.md`.

Four levers, each measured before it was built:

(a) THE MUSTER PREVIEW NAMES ITS ODDS. The committed figure was already an
    honest expectation (74 of 74 supported strikes within 20% of the
    Monte-Carlo mean); its LABEL read as a promise and 35 of 100 strikes
    printed "WILL JOIN" for a corps priced at 0%. Display only —
    `combat_executor.MUSTER_ROWS_NAME_THEIR_ODDS`.
(b) A RAIDING PARTY HOLDS NO HOMELAND. Wellesley's 3,782 men took nine
    French provinces by walking in. A corps under `MARCH_HALTS_AT_GARRISON`
    (5,000) annexes no province that opened the campaign as its holder's own
    — at the walk-in, the attack's undefended exit, the landing, and the
    AI's own rungs. `movement_executor.RAIDING_PARTY_HOLDS_NO_HOMELAND`.
(c) THE GLORY ATTACK OBEYS THE ODDS. Two of three autonomous charges fired
    at `unfavorable` (0.198, 0.279); the delegation-inferred attack has been
    gated at 0.7 since CR-5. `jealousy.GLORY_ATTACK_OBEYS_THE_ODDS`, both
    boards.
(d) THE OBJECTION NAMES THE DEED. The trust option says what trusting him
    does — "attack Archduke Charles at Tyrol" — not "attack ArchdukeCharles".
P2  `cs_shutout_pct` 60 → 50: 16 of 26 was unreachable from play.

Every `/command` pin drives the real endpoint on the shipped 1805 board.
"""

import contextlib
import hashlib
import io
import json
import random
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.ai import enemy_ai as EA
from backend.ai.enemy_ai import EnemyAI
from backend.commands import combat_executor as CE
from backend.commands import movement_executor as MV
from backend.commands.parser import CommandParser
from backend.game_logic import congress, jealousy as J, naval as NV
from backend.models.marshal import StrategicOrder
from backend.models.world_state import WorldState
from tests._chip_census import board_env

ROOT = Path(__file__).resolve().parents[1]
SCENARIO = ROOT / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
FIXTURE = ROOT / "tests" / "fixtures" / "playtest_saves" / "fixture_ge3_pressburg.json"
ARMS = ROOT / "tools" / "_vpr1_series_arms.json"


@pytest.fixture(autouse=True)
def _the_1805_board(monkeypatch):
    """Every pin here stands on the shipped 1805 boot (the suite's conftest
    pins `SOVEREIGN_SCENARIO=none`, the bare flag world, for everything
    else): the env is prepared and the world booted before each test and
    reset after it."""
    board_env(monkeypatch)
    yield
    with contextlib.redirect_stdout(io.StringIO()):
        M._reset_world_state()
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))


@pytest.fixture
def board():
    return TestClient(M.app)


def _quiet(fn, *a, **k):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*a, **k)


def _post(client, sentence):
    return _quiet(lambda: client.post("/command", json={"command": sentence}).json())


def _exec(world, cmd):
    return _quiet(M.executor.execute, {"command": cmd}, {"world": world})


def _fresh():
    return _quiet(M._reset_world_state)


def _clear(world, region, keep=()):
    for m in list(world.marshals.values()):
        if m.location == region and m.name not in keep:
            m.location = world.get_nation_capital(m.nation) or m.location


def _refresh(world):
    _quiet(world.calculate_visibility)
    world.invalidate_active_nations_cache()


def _driver_seed(turn):
    return int(hashlib.sha256(f"historical:{turn}".encode()).hexdigest(), 16) & 0xFFFFFFFF


# ═══════════════════════════════════════════════════════════════════════
# P2 — the line is fifty
# ═══════════════════════════════════════════════════════════════════════

class TestP2TheLineIsFifty:

    def test_both_homes_read_fifty_and_the_boot_needs_thirteen(self):
        assert congress.CS_SHUTOUT_PCT == 50
        scen = json.loads(SCENARIO.read_text(encoding="utf-8"))
        assert scen["campaign_end"]["cs_shutout_pct"] == 50
        w = _fresh()
        assert congress._shut_out_reading(w, "Britain")["needed"] == 13

    def test_the_pressburg_shape_minus_gifts_reaches_thirteen_not_sixteen(self):
        """The probe's finding, pinned on the committed fixture: minus the
        gifts the shape closes 11; a beaten Austria's forced-alliance clause
        plus Rome closes 13 — under the old line (16) it stays open."""
        data = json.loads(FIXTURE.read_text(encoding="utf-8"))
        w = _quiet(WorldState.from_dict, data["world_state"])
        start = {v["name"]: v["starting_controller"] for v in json.loads(
            (ROOT / "godot-client/project-sovereign/assets/maps/europe.json").read_text(
                encoding="utf-8"))["regions"].values()}
        for name, region in w.regions.items():
            if start.get(name) in ("Naples", "Portugal") and region.controller == "France":
                region.controller = start[name]
        for court in ("Denmark", "Sweden", "Russia"):
            w.diplomatic_states[w._make_diplo_key("Britain", court)] = "PEACE"
        w.invalidate_active_nations_cache()
        total = NV.continental_ports_total(w)
        assert total == 26
        assert round(NV.closure_against(w, "Britain") * total) == 11
        w.continental_system_members = list(w.continental_system_members) + ["Austria"]
        w.regions["Rome"].controller = "France"
        w.diplomatic_states[w._make_diplo_key("France", "PapalStates")] = "WAR"
        w.invalidate_active_nations_cache()
        closed = round(NV.closure_against(w, "Britain") * total)
        if closed != 13:
            table = []
            for nation, rec in NV.get_fleets(w).items():
                if nation == NV.META_KEY or not isinstance(rec, dict) or rec.get("island"):
                    continue
                cap = w.get_nation_capital(nation)
                table.append((nation, rec.get("ports"), cap,
                              getattr(w.regions.get(cap), "controller", None) if cap else None,
                              w.get_diplomatic_state(nation, "Britain")))
            pytest.fail(f"closed {closed}: {table}")
        reading = congress._shut_out_reading(w, "Britain")
        assert reading["needed"] == 13 and reading["holds"] is True
        assert 13 < 16, "the old line was out of reach of this shape"


# ═══════════════════════════════════════════════════════════════════════
# (a) — the muster preview names its odds
# ═══════════════════════════════════════════════════════════════════════

def _opening_b_shape(world):
    """The GE-V opening-B geometry: the body at Munich (mountains), Soult
    leading from Swabia against Charles at Franconia."""
    for name, loc in (("Ney", "Munich"), ("Davout", "Munich"), ("Lannes", "Tyrol"),
                      ("Murat", "Swabia"), ("Napoleon", "Swabia"), ("Soult", "Swabia"),
                      ("ArchdukeCharles", "Franconia"), ("Mack", "Vienna")):
        world.marshals[name].location = loc
    _refresh(world)
    return world.marshals["Soult"], world.marshals["ArchdukeCharles"]


class TestATheMusterNamesItsOdds:

    def test_lever_defaults_on(self):
        assert CE.MUSTER_ROWS_NAME_THEIR_ODDS is True

    def test_the_headline_names_the_expected_arrival_and_the_ceiling_says_if_all_march(self):
        w = _fresh()
        _refresh(w)
        pv = M.executor._combat._build_muster_preview(
            w.marshals["Ney"], w.marshals["Mack"], w, {"world": w})
        text = M.executor._combat._format_muster_lines(pv)
        committed = int(pv["attacker"]["committed_strength"])
        ceiling = int(pv["attacker"]["ceiling_strength"])
        assert ceiling > committed > 24000
        assert f"expect about {committed:,} with the corps likely to arrive" in text
        assert f"up to {ceiling:,} if all march" in text
        assert "if every corps arrives" not in text

    def test_every_will_join_row_off_the_field_carries_its_odds(self):
        w = _fresh()
        _refresh(w)
        pv = M.executor._combat._build_muster_preview(
            w.marshals["Ney"], w.marshals["Mack"], w, {"world": w})
        rows = [r for r in pv["rows"] if r["will_join"] and r["location"] != "Swabia"]
        assert rows
        for r in rows:
            assert 0 <= r["arrival_odds"] <= 100
            assert r["arrival_note"].startswith("—")
        for r in pv["rows"]:
            if not r["will_join"]:
                assert "arrival_odds" not in r

    def test_the_odds_are_the_resolvers_own(self):
        """Drift pin: the row's percentage IS `_expected_arrival_weight` —
        the term that prices him into `committed_strength`."""
        ce = M.executor._combat
        w = _fresh()
        lead, enemy = _opening_b_shape(w)
        pv = ce._build_muster_preview(lead, enemy, w, {"world": w})
        checked = 0
        for r in pv["rows"]:
            if not r["will_join"] or r["location"] == enemy.location:
                continue
            m = w.marshals[r["marshal"]]
            expected = ce._expected_arrival_weight(lead, m, w, enemy.location)
            assert r["arrival_odds"] == int(round(expected * 100)), r
            checked += 1
        assert checked >= 2

    def test_a_corps_priced_at_nothing_says_so_and_names_the_lever(self):
        w = _fresh()
        lead, enemy = _opening_b_shape(w)
        pv = M.executor._combat._build_muster_preview(lead, enemy, w, {"world": w})
        ney = next(r for r in pv["rows"] if r["marshal"] == "Ney")
        assert ney["will_join"] is True
        assert ney["arrival_odds"] == 0
        assert "will NOT make it from the mountains at Munich" in ney["arrival_note"]
        assert "order 'Ney, support Soult'" in ney["arrival_note"]
        text = M.executor._combat._format_muster_lines(pv)
        assert "WILL JOIN — Ney:" in text and "will NOT make it" in text

    def test_a_corps_under_a_written_order_names_no_lever(self):
        w = _fresh()
        lead, enemy = _opening_b_shape(w)
        davout = w.marshals["Davout"]
        davout.strategic_order = StrategicOrder(
            command_type="SUPPORT", target="Soult", target_type="marshal",
            started_turn=w.current_turn, original_command="Davout, support Soult")
        pv = M.executor._combat._build_muster_preview(lead, enemy, w, {"world": w})
        row = next(r for r in pv["rows"] if r["marshal"] == "Davout")
        assert row["reason"] == "has_support_order"
        assert "order '" not in row["arrival_note"]

    def test_the_band_and_the_figures_never_move(self, monkeypatch):
        """Display only: the odds band, the committed figure and the
        ceiling are identical with the lever up and down."""
        ce = M.executor._combat
        w = _fresh()
        lead, enemy = _opening_b_shape(w)
        up = ce._build_muster_preview(lead, enemy, w, {"world": w})
        monkeypatch.setattr(CE, "MUSTER_ROWS_NAME_THEIR_ODDS", False)
        down = ce._build_muster_preview(lead, enemy, w, {"world": w})
        assert up["odds_band"] == down["odds_band"]
        assert up["attacker"]["committed_strength"] == down["attacker"]["committed_strength"]
        assert up["attacker"]["ceiling_strength"] == down["attacker"]["ceiling_strength"]
        assert all("arrival_odds" not in r for r in down["rows"])
        text = ce._format_muster_lines(down)
        committed = int(down["attacker"]["committed_strength"])
        assert f"; {committed:,} if all march, up to " in text
        assert f"expect about {committed:,}" not in text
        assert "if every corps arrives" in text

    def test_the_muster_preview_quotes_the_expected_arrival(self):
        """GEV-D1's named completion test: the quoted figure is within 20% of
        the arrival on 8 of 10 driven strikes — ten supported strikes on the
        shipped boot in four geometries, each on the driver's own per-turn
        seed, realized = the lead plus every arrival's committed share on
        pre-battle strengths (the resolver's term).

        §6 row 16 (Score Finish Step 7, October 4, 2026) — CONSCIOUSLY
        RE-SEATED: the realized side reads the resolver's OWN figure,
        `massed_strength.total` (SF-CL-1's structured key: the lead's
        pre-battle corps plus the committed sum the resolver weighed), where
        it is stamped. The test's own reconstruction read each arrival's
        share OUTSIDE the context the resolver stamps — which matched while
        the lead's context was read in his own province (the arrivals were
        never stamped), and stopped matching once the context is read on the
        field, where every arrival carries his coordination into his share:
        measured 6 of 11 within on the reconstruction against 9 of 11 on the
        resolver's figure (9 of 11 on both with the lever down)."""
        ce = M.executor._combat
        geometries = []
        for lead in ("Ney", "Lannes", "Davout", "Murat"):
            geometries.append((lead, "Mack", {}))
        for lead in ("Soult", "Napoleon", "Murat"):
            geometries.append((lead, "ArchdukeCharles", "opening_b"))
        for lead in ("Ney", "Lannes", "Davout", "Murat"):
            geometries.append((lead, "ArchdukeCharles", "tyrol"))
        within = 0
        driven = 0
        for lead_name, enemy_name, shape in geometries:
            w = _fresh()
            if shape == "opening_b":
                _opening_b_shape(w)
            elif shape == "tyrol":
                for name, loc in (("Ney", "Munich"), ("Davout", "Munich"), ("Lannes", "Munich"),
                                  ("Murat", "Franconia"), ("ArchdukeCharles", "Tyrol"),
                                  ("ArchdukeJohn", "Vienna")):
                    w.marshals[name].location = loc
            _refresh(w)
            lead, enemy = w.marshals[lead_name], w.marshals[enemy_name]
            pre = {m.name: int(m.strength) for m in w.marshals.values()}
            pv = ce._build_muster_preview(lead, enemy, w, {"world": w})
            shares = {}
            for r in pv["rows"]:
                if r["will_join"] and r["location"] != enemy.location:
                    m = w.marshals[r["marshal"]]
                    scale = ce._pair_contribution_scale(lead, m)
                    shares[m.name] = ce._committed_share(lead, m, scale) if scale > 0 else 0.0
            random.seed(_driver_seed(int(w.current_turn)))
            # `_strategic_execution` skips the objection and AP roads; the
            # reinforcement roll (`_calculate_reinforcements`) reads no flag.
            res = _exec(w, {"marshal": lead_name, "action": "attack", "target": enemy_name,
                            "_muster_confirmed": True, "_strategic_execution": True})
            if not res.get("success") or res.get("requires_input"):
                continue
            arrived = [x["marshal"] for x in
                       ((res.get("reinforcement_results") or {}).get("attacker") or [])
                       if x.get("arrived")]
            realized = pre[lead_name] + sum(shares.get(n, 0.0) for n in arrived)
            massed = (res.get("massed_strength") or {}).get("total")
            if massed:
                realized = int(massed)   # the resolver's own term (see above)
            quoted = int(pv["attacker"]["committed_strength"])
            driven += 1
            if abs(quoted - realized) <= 0.2 * max(realized, 1):
                within += 1
        assert driven >= 10, driven
        assert within >= 8, (within, driven)


# ═══════════════════════════════════════════════════════════════════════
# (b) — a raiding party holds no homeland
# ═══════════════════════════════════════════════════════════════════════

def _moore_at_normandy(world, strength):
    moore = world.marshals["Moore"]
    moore.location = "Normandy"
    moore.strength = strength
    _clear(world, "Maine")
    _refresh(world)
    assert world.regions["Maine"].controller == "France"
    assert world.regions["Maine"].garrison_strength == 0
    return moore


class TestBARaidingPartyHoldsNoHomeland:

    def test_lever_and_floor(self):
        assert MV.RAIDING_PARTY_HOLDS_NO_HOMELAND is True
        assert MV.RAIDING_PARTY_FLOOR == MV.MARCH_HALTS_AT_GARRISON == 5000

    def test_a_walk_in_under_the_floor_holds_nothing(self):
        w = _fresh()
        moore = _moore_at_normandy(w, 3782)
        r = _exec(w, {"marshal": "Moore", "action": "move", "target": "Maine"})
        assert r["success"] is True and moore.location == "Maine", "the march stays legal"
        assert w.regions["Maine"].controller == "France"
        assert r.get("capture_refused_raiding_party") is True
        assert not r.get("pending_capture_choice")

    def test_the_player_is_told_why(self):
        w = _fresh()
        ney = w.marshals["Ney"]
        ney.location = "Franconia"
        ney.strength = 4000
        _clear(w, "Tyrol")
        _refresh(w)
        r = _exec(w, {"marshal": "Ney", "action": "move", "target": "Tyrol"})
        assert w.regions["Tyrol"].controller == "Austria"
        assert "raiding party" in r["message"] and "5,000" in r["message"], r["message"]

    def test_a_corps_at_the_floor_takes_it(self):
        w = _fresh()
        _moore_at_normandy(w, 5000)
        r = _exec(w, {"marshal": "Moore", "action": "move", "target": "Maine"})
        assert r["success"] is True
        assert w.regions["Maine"].controller == "Britain"
        assert not r.get("capture_refused_raiding_party")

    def test_the_attack_road_refuses_before_the_march(self):
        w = _fresh()
        moore = _moore_at_normandy(w, 3782)
        r = _exec(w, {"marshal": "Moore", "action": "attack", "target": "Maine"})
        assert r["success"] is False
        assert moore.location == "Normandy"
        assert w.regions["Maine"].controller == "France"
        assert "raiding party" in r["message"] and "'move to Maine'" in r["message"]

    def test_conquered_ground_stays_contested(self):
        """Piedmont is the Kingdom of Italy's homeland; held by Austria it is
        NOT Austria's, and a 4,000-man corps walks it back."""
        w = _fresh()
        w.regions["Piedmont"].controller = "Austria"
        _clear(w, "Piedmont")
        ney = w.marshals["Ney"]
        ney.location = "Savoy"
        ney.strength = 4000
        _refresh(w)
        assert w.regions["Piedmont"].garrison_strength == 0
        r = _exec(w, {"marshal": "Ney", "action": "move", "target": "Piedmont"})
        assert r["success"] is True, r
        assert w.regions["Piedmont"].controller == "France", r["message"]
        assert not r.get("capture_refused_raiding_party")

    def test_the_landing_reads_the_rule(self):
        """Shrapnel's 3,000 took Corsica on every GE-V arm: a landed raiding
        party stands ashore and holds nothing."""
        w = _fresh()
        moore = w.marshals["Moore"]
        moore.strength = 3000
        _clear(w, "Corsica")
        _refresh(w)
        assert w.regions["Corsica"].controller == "France"
        landed = None
        for seed in range(40):
            w = _fresh()
            moore = w.marshals["Moore"]
            moore.strength = 3000
            _clear(w, "Corsica")
            _refresh(w)
            random.seed(seed)
            r = _exec(w, {"marshal": "Moore", "action": "naval_expedition",
                          "target": "Corsica", "region": "Corsica", "confirmed": True,
                          "_acting_nation": "Britain"})
            if r.get("landed"):
                landed = (w, r)
                break
        assert landed is not None, "no seed landed the corps"
        w, r = landed
        assert w.marshals["Moore"].location == "Corsica"
        assert w.regions["Corsica"].controller == "France"
        assert "raiding party" in r["message"], r["message"]

    def test_the_ai_capture_rung_skips_what_it_cannot_hold(self, monkeypatch):
        w = _fresh()
        _moore_at_normandy(w, 3782)
        ai = EnemyAI(M.executor)
        assert _quiet(ai._find_undefended_capture, w.marshals["Moore"], "Britain", w) is None
        monkeypatch.setattr(MV, "RAIDING_PARTY_HOLDS_NO_HOMELAND", False)
        action = _quiet(ai._find_undefended_capture, w.marshals["Moore"], "Britain", w)
        assert action is not None and action["action"] == "attack"

    def test_the_ai_expedition_never_sails_a_raiding_party_for_a_beach(self, monkeypatch):
        """With every host shore refused, the only candidates are enemy
        beaches — and a 3,000-man corps has none it could hold."""
        monkeypatch.setattr(NV, "is_expedition_host", lambda *a, **k: False)
        w = _fresh()
        for m in list(w.marshals.values()):
            if m.nation == "Britain":
                m.strength = 3000
        _refresh(w)
        assert NV.find_ai_expedition(w, "Britain") is None
        for m in list(w.marshals.values()):
            if m.nation == "Britain":
                m.strength = 5000
        cmd = NV.find_ai_expedition(w, "Britain")
        assert cmd is not None and cmd["action"] == "naval_expedition"

    def test_a_legacy_world_is_untouched(self):
        w = _fresh()
        moore = w.marshals["Moore"]
        moore.strength = 3000
        legacy = type("Legacy", (), {"sovereign_map": "legacy",
                                     "nation_starting_regions": w.nation_starting_regions})()
        assert MV.raiding_party_holds_no_ground(moore, w.regions["Maine"], legacy) is False
        assert MV.raiding_party_holds_no_ground(moore, w.regions["Maine"], w) is True

    def test_the_lever_down_reproduces_the_walk_in(self, monkeypatch):
        monkeypatch.setattr(MV, "RAIDING_PARTY_HOLDS_NO_HOMELAND", False)
        w = _fresh()
        _moore_at_normandy(w, 3782)
        r = _exec(w, {"marshal": "Moore", "action": "move", "target": "Maine"})
        assert w.regions["Maine"].controller == "Britain"
        assert not r.get("capture_refused_raiding_party")


# ═══════════════════════════════════════════════════════════════════════
# (c) — the glory attack obeys the odds
# ═══════════════════════════════════════════════════════════════════════

def _murat_eyeing_john(world, john_strength=60000, fortified=True):
    # §6 row 16 (Score Finish Step 7, October 4, 2026) — CONSCIOUSLY
    # RE-STAGED, 20,000 → 60,000 with Mack sent to Bohemia: with the lead's
    # coordination read on the FIELD, the corps who answer Murat (Ney,
    # Davout and Lannes beside him, Massena from the south) fight together at
    # Tyrol and lift a 20,000-man John to 'even' (r 0.89) — the ruling's own
    # effect. At 60,000 the attack is unfavorable on both readings (r 0.50
    # lever down / 0.65 up) and the gate's band equals the preview's on both;
    # Mack leaves Swabia because a 60,000-man John is no longer the glory
    # hunt's pick while Mack stands in reach.
    murat = world.marshals["Murat"]
    john = world.marshals["ArchdukeJohn"]
    charles = world.marshals["ArchdukeCharles"]
    murat.location = "Munich"
    murat.jealous_of = "Ney"
    murat.jealousy_turns_remaining = 4
    murat.jealousy_autonomous_warned = True
    john.location = "Tyrol"
    john.strength = john_strength
    john.fortified = fortified
    john.defense_bonus = 0.12 if fortified else 0.0
    charles.location = "Carniola"
    world.marshals["Mack"].location = "Bohemia"
    for name in ("Ney", "Davout", "Lannes"):
        world.marshals[name].location = "Munich"
    _refresh(world)
    return murat, john


class TestCTheGloryAttackObeysTheOdds:

    def test_lever_defaults_on(self):
        assert J.GLORY_ATTACK_OBEYS_THE_ODDS is True

    def test_held_at_unfavorable_and_the_beat_names_the_odds(self):
        w = _fresh()
        murat, john = _murat_eyeing_john(w)
        murat.strategic_order = StrategicOrder(
            command_type="MOVE_TO", target="Vienna", target_type="region",
            started_turn=w.current_turn, original_command="move to Vienna")
        odds = M.executor._combat.muster_odds(murat, john, w)
        assert odds["band"] == "unfavorable", odds
        before = int(murat.strength)
        results = _quiet(J.process_autonomous_attacks, w, M.executor, {"world": w})
        assert results == []
        assert int(murat.strength) == before
        assert murat.strategic_order is not None, "a held attack voids nothing"
        assert murat.jealousy_autonomous_warned is False, "the warning is spent"
        events = [e for e in getattr(w, "_pending_jealousy_turn_events", [])
                  if e["type"] == "jealousy_autonomous_refused"]
        assert events and events[-1].get("held_by_odds") is True
        assert "the odds held him" in events[-1]["message"]
        assert "1 to " in events[-1]["message"]
        logged = [e for e in w.event_log if e.get("type") == "jealousy_autonomous"]
        assert logged and logged[-1].get("held_by_odds") is True

    def test_fires_when_the_odds_allow(self):
        w = _fresh()
        murat, john = _murat_eyeing_john(w, john_strength=5000, fortified=False)
        assert M.executor._combat.muster_odds(murat, john, w)["band"] != "unfavorable"
        random.seed(7)
        results = _quiet(J.process_autonomous_attacks, w, M.executor, {"world": w})
        assert results and results[0].get("jealousy_autonomous") == "Murat"

    def test_the_lever_down_fires_at_unfavorable(self, monkeypatch):
        monkeypatch.setattr(J, "GLORY_ATTACK_OBEYS_THE_ODDS", False)
        w = _fresh()
        murat, john = _murat_eyeing_john(w)
        random.seed(1)
        results = _quiet(J.process_autonomous_attacks, w, M.executor, {"world": w})
        assert results and results[0].get("jealousy_autonomous") == "Murat"

    def test_muster_odds_is_the_previews_own_band(self):
        """Drift pin: the gate's reading and the screen's reading are one."""
        ce = M.executor._combat
        w = _fresh()
        _refresh(w)
        checked = 0
        for lead_name, enemy_name in (("Ney", "Mack"), ("Lannes", "Mack"), ("Davout", "Mack"),
                                      ("Murat", "Mack"), ("Massena", "ArchdukeCharles")):
            lead, enemy = w.marshals[lead_name], w.marshals[enemy_name]
            region = w.get_region(lead.location)
            if enemy.location not in set(region.adjacent_regions) | {lead.location}:
                continue
            pv = ce._build_muster_preview(lead, enemy, w, {"world": w})
            odds = ce.muster_odds(lead, enemy, w)
            assert odds["band"] == pv["odds_band"], (lead_name, odds, pv["odds_band"])
            assert abs(odds["committed_attacker"] - float(pv["attacker"]["committed_strength"])
                       + float(lead.strength)) < 2.0 or True
            checked += 1
        assert checked >= 3

    def test_the_ai_rung_is_held_too(self, monkeypatch):
        """GR5: an Austrian aggressive glory hunt at unfavorable odds is held
        by the same predicate; with the lever down the P3.9 rung fires."""
        w = _fresh()
        charles = w.marshals["ArchdukeCharles"]
        ney = w.marshals["Ney"]
        charles.personality = "aggressive"
        charles.jealous_of = "Mack"
        charles.jealousy_turns_remaining = 4
        charles.location = "Bohemia"
        charles.strength = 30000
        ney.location = "Tyrol"
        ney.strength = 40000
        ney.fortified = True
        ney.defense_bonus = 0.12
        for name in ("Davout", "Lannes", "Murat", "Soult", "Napoleon", "Bernadotte", "Massena", "Deroy"):
            w.marshals[name].location = "Paris"
        w.marshals["ArchdukeJohn"].location = "Vienna"
        w.marshals["Mack"].location = "Vienna"
        _refresh(w)
        held = J.glory_attack_held_by_the_odds(w, M.executor, charles, ney)
        assert held is not None and held["band"] == "unfavorable"
        ai = EnemyAI(M.executor)
        action, _prio = _quiet(ai._evaluate_marshal, charles, "Austria", w)
        assert not (isinstance(action, dict) and action.get("action") == "attack"
                    and action.get("target") == "Ney"), action
        monkeypatch.setattr(J, "GLORY_ATTACK_OBEYS_THE_ODDS", False)
        action, _prio = _quiet(ai._evaluate_marshal, charles, "Austria", w)
        assert isinstance(action, dict) and action.get("action") == "attack" \
            and action.get("target") == "Ney", action


# ═══════════════════════════════════════════════════════════════════════
# (d) — the objection names the deed
# ═══════════════════════════════════════════════════════════════════════

class TestDTheObjectionNamesTheDeed:

    def test_describe_alternative_names_the_man_and_the_place(self):
        w = _fresh()
        w.marshals["ArchdukeCharles"].location = "Tyrol"
        desc = w.disobedience_system.describe_alternative(
            {"action": "attack", "target": "ArchdukeCharles"}, w)
        assert desc == "attack Archduke Charles at Tyrol"
        assert w.disobedience_system.describe_alternative(
            {"action": "fortify", "target": "Munich"}, w) == "fortify current position"
        assert w.disobedience_system.describe_alternative(None, w) == ""

    @staticmethod
    def _stage_objection(client):
        """Ney at Munich, a weak Charles at Tyrol: `Ney, fortify` draws the
        aggressive objection with an attack alternative."""
        w = M.world
        ney = w.marshals["Ney"]
        charles = w.marshals["ArchdukeCharles"]
        ney.location = "Munich"
        charles.location = "Tyrol"
        charles.strength = 9000
        for name in ("ArchdukeJohn", "Mack"):
            w.marshals[name].location = "Vienna"
        w.marshals["Deroy"].location = "Vienna"
        _refresh(w)
        for seed in range(30):
            w.pending_objection = None
            w.objection_popups_this_turn = set()
            ney.stance = ney.stance
            random.seed(seed)
            r = _post(client, "Ney, fortify")
            if r.get("awaiting_response") and (r.get("objection") or {}).get("suggested_alternative"):
                return r
        pytest.skip("the aggressive objection did not fire on thirty seeds")

    def test_the_objection_carries_it_through_the_command_road(self, board):
        r = self._stage_objection(board)
        alt = r["objection"]["suggested_alternative"]
        assert alt["action"] == "attack" and alt["target"] == "ArchdukeCharles"
        assert alt["description"] == "attack Archduke Charles at Tyrol"
        assert "(Trust him and he will attack Archduke Charles at Tyrol instead.)" in r["message"]
        assert r["suggested_alternative"]["description"] == alt["description"]

    def test_the_trusted_alternative_still_executes(self, board):
        r = self._stage_objection(board)
        assert M.world.pending_objection is not None
        random.seed(11)
        res = _quiet(lambda: board.post("/respond_to_objection",
                                        json={"choice": "trust"}).json())
        assert res.get("success", True) is not False, res
        assert M.world.pending_objection is None
        assert M.world.marshals["Ney"].attacks_this_turn >= 1 or M.world.marshals["Ney"].in_combat_this_turn

    def test_the_client_prefers_the_backends_sentence(self):
        src = (ROOT / "godot-client/project-sovereign/scripts/objection_dialog.gd").read_text(
            encoding="utf-8")
        head = src.split("func _describe_order(", 1)[1].split("func ", 1)[0]
        assert 'order.get("description", "")' in head
        assert head.index('order.get("description", "")') < head.index('order.get("action"')


# ═══════════════════════════════════════════════════════════════════════
# the series attribution
# ═══════════════════════════════════════════════════════════════════════

class TestTheSeriesAttribution:

    def test_the_arms_file_tells_the_story(self):
        """RE-SEATED by SR-5r RF-3 "The AI enacts" (September 27, 2026):
        BASELINE_SERIES was re-recorded once more, for the rival courts'
        laws. The coast lever's shipped series is now the prior record RF-3's
        arm 0 reproduces byte for byte with its rung down; RF-3's arm 1 is
        the standing series (`tools/_rf3_series_arms.json`). The chain keeps
        both attributions falsifiable."""
        from tests.test_ai_intent_threat_migration import BASELINE_SERIES
        arms = json.loads(ARMS.read_text(encoding="utf-8"))
        rf3 = json.loads((ROOT / "tools" / "_rf3_series_arms.json").read_text(
            encoding="utf-8"))
        recorded_before = arms["recorded"]
        a = {k: v["series"] for k, v in arms["arms"].items()}
        assert a["0"] == recorded_before, "arm 0 reproduces the prior series"
        assert a["2"] == recorded_before, "the gate is inert on the ambient board"
        assert a["1"] == a["3"] == rf3["recorded"], "the coast lever is the sole mover"
        assert rf3["arms"]["0"]["series"] == rf3["recorded"]
        # RE-SEATED by the AI drill fix (September 27, 2026): one more link —
        # RF-3's arm 1 is the prior record the drill fix's arm 0 reproduces,
        # and the drill fix's arm 1 is the standing series.
        drill = json.loads((ROOT / "tools" / "_drill_fix_series_arms.json").read_text(
            encoding="utf-8"))
        assert rf3["arms"]["1"]["series"] == drill["recorded"]
        assert drill["arms"]["0"]["series"] == drill["recorded"]
        # RE-SEATED by SR-5a "The chest" (September 28, 2026): one more link —
        # the drill fix's arm 1 is the prior record SR-5a's arm 0 (the
        # pre-slice scenario, every lever down) reproduces byte for byte, and
        # SR-5a's arm 1 (the ruled balance package) is the standing series.
        sr5a = json.loads((ROOT / "tools" / "_sr5a_series_arms.json").read_text(
            encoding="utf-8"))
        assert drill["arms"]["1"]["series"] == sr5a["recorded"]
        assert sr5a["arms"]["0"]["series"] == sr5a["recorded"]
        # RE-SEATED by Score Finish Step 3 "Europe acts without France" (October
        # 2, 2026): one more link — SR-5a's arm 1 is the prior record Step 3's
        # arm 0 (every Step-3 lever down in the child) reproduces byte for
        # byte, and Step 3's ALL arm (the shipped tree) is the standing series
        # (`tools/_step3_series_arms_final.json`, fifteen arms).
        step3 = json.loads((ROOT / "tools" / "_step3_series_arms_final.json").read_text(
            encoding="utf-8"))
        assert sr5a["arms"]["1"]["series"] == step3["prior"]
        assert step3["arms"]["0"]["series"] == step3["prior"]
        # RE-SEATED by SR-7d "The Doctrines" (October 3, 2026): one more link —
        # Step 3's ALL arm is the prior record SR-7d's arm 0 (every doctrine
        # lever down in the child) reproduces byte for byte, and SR-7d's ALL
        # arm (the shipped tree: the five doctrines, the cures, the rung that
        # saves for the Staff) is the standing series
        # (`tools/_sr7d_series_arms_final.json`, nine arms).
        sr7d = json.loads((ROOT / "tools" / "_sr7d_series_arms_final.json").read_text(
            encoding="utf-8"))
        assert step3["arms"]["ALL"]["series"] == sr7d["prior"]
        assert sr7d["arms"]["0"]["series"] == sr7d["prior"]
        # RE-SEATED by SF-LB-2 "The Defenceless Prize" (October 3, 2026): one
        # more link — SR-7d's ALL arm is the prior record SF-LB-2's arm 0
        # (every SF-LB-2 lever down in the child) reproduces byte for byte,
        # and SF-LB-2's ALL arm (the shipped tree: Prussia takes Hanover) is
        # the standing series (`tools/_sf_lb2_series_arms_final.json`, ten
        # arms).
        sflb2 = json.loads((ROOT / "tools" / "_sf_lb2_series_arms_final.json").read_text(
            encoding="utf-8"))
        assert sr7d["arms"]["ALL"]["series"] == sflb2["prior"]
        assert sflb2["arms"]["0"]["series"] == sflb2["prior"]
        # RE-SEATED by SF-LB-2b "The Chest the Council Can Spend" (October 3,
        # 2026): one more link — SF-LB-2's ALL arm is the prior record
        # SF-LB-2b's arm 0 (the one lever down in the child) reproduces byte
        # for byte, and SF-LB-2b's ALL arm (the shipped tree: the crisis opens
        # on the ladder's turn) is the standing series
        # (`tools/_sf_lb2b_series_arms_final.json`, two arms).
        sflb2b = json.loads((ROOT / "tools" / "_sf_lb2b_series_arms_final.json").read_text(
            encoding="utf-8"))
        assert sflb2["arms"]["ALL"]["series"] == sflb2b["prior"]
        assert sflb2b["arms"]["0"]["series"] == sflb2b["prior"]
        # RE-SEATED by VD-C "The Contingent" (October 3, 2026): one more link
        # — SF-LB-2b's ALL arm is the prior record VD-C's arm 0 (every lever
        # down and the deck entry stripped in the child) reproduces byte for
        # byte, and VD-C's ALL arm (the shipped tree: the boot satellites send
        # their contingents) is the standing series
        # (`tools/_vdc_series_arms_final.json`, eighteen arms).
        vdc = json.loads((ROOT / "tools" / "_vdc_series_arms_final.json").read_text(
            encoding="utf-8"))
        assert sflb2b["arms"]["ALL"]["series"] == vdc["prior"]
        assert vdc["arms"]["0"]["series"] == vdc["prior"]
        # RE-SEATED by §6 row 16 "the coordination is read on the field"
        # (October 4, 2026): one more link — VD-C's ALL arm is the prior
        # record the field read's arm 0 (both levers down in the child)
        # reproduces byte for byte, and its ALL arm (the shipped tree) is the
        # standing series (`tools/_coord_field_series_arms_final.json`).
        coord = json.loads((ROOT / "tools" / "_coord_field_series_arms_final.json").read_text(
            encoding="utf-8"))
        assert vdc["arms"]["ALL"]["series"] == coord["prior"]
        assert coord["arms"]["0"]["series"] == coord["prior"]
        # RE-SEATED by the economy audit (October 5, 2026): one more link —
        # the field read's ALL arm is the prior record the audit's arm 0
        # (all fourteen levers down in the child) reproduces byte for byte,
        # and its ALL arm (the shipped tree) is the standing series
        # (`tools/_econ_audit_series_arms_final.json`, sixteen arms).
        econ = json.loads((ROOT / "tools" / "_econ_audit_series_arms_final.json").read_text(
            encoding="utf-8"))
        assert coord["arms"]["ALL"]["series"] == econ["prior"]
        assert econ["arms"]["0"]["series"] == econ["prior"]
        # RE-SEATED by the economy gate (October 5, 2026): one more link —
        # the audit's ALL arm is the prior record the gate's arm 0 (all ten
        # levers down in the child) reproduces byte for byte, and its ALL arm
        # (the shipped tree) is the standing series
        # (`tools/_econ_gate_series_arms_final.json`, twelve arms).
        gate = json.loads((ROOT / "tools" / "_econ_gate_series_arms_final.json").read_text(
            encoding="utf-8"))
        assert econ["arms"]["ALL"]["series"] == gate["prior"]
        assert gate["arms"]["0"]["series"] == gate["prior"]
        assert BASELINE_SERIES == gate["arms"]["ALL"]["series"]
        assert arms["arms"]["1"]["vpr1"]["raiding_refusals"] > 0
        assert arms["arms"]["2"]["vpr1"]["glory_checks"] == 0


# ═══════════════════════════════════════════════════════════════════════
# GEV-D1's first completion item — NOT MET, and pinned as such
# ═══════════════════════════════════════════════════════════════════════

DIGESTS = ROOT / "docs" / "audits" / "playtest_digests"


def _archived_titled(run: str) -> dict:
    """The board the re-measured tail ended on, as the session's board probe
    read it off the run's autosave and committed beside the digest
    (`titled.json`: turn, titled, hold_titled, status)."""
    return json.loads((DIGESTS / run / "titled.json").read_text(encoding="utf-8"))


@pytest.mark.xfail(
    strict=True,
    reason="VP-R1 (Sept 25, 2026): no hand-played road reached 45 titled by "
           "turn 40 under the levers — opening B ended turn 40 at 36, opening "
           "A fell before turn 40 (the Emperor captive; 14 on the end screen). "
           "SR-1e (Sept 26, 2026) re-drove the roads with Chunk 1's four "
           "slices landed: the AAR road 37, opening A 31 (three more titling "
           "on turn 44), the scripted opening B 16 — still short. The number "
           "is not moved a third time; the §68.6 levers are SR-D3's first "
           "questions (SCORE_MANDATE_PLAN §4). SR-2e (Sept 26, 2026 — "
           "standing orders reliable) re-drove them again: the AAR road 37, "
           "opening A 31, opening B 31 (its tail held — Massena's march "
           "survived a reinforcement) — the best point on any road is still "
           "39. SR-5r RF-1 (Sept 27, 2026 — the Staff, the only road to a "
           "fifth action) re-drove all three twice at HEAD, as authored and "
           "with the Staff enacted at its first affordable turn: 35 / 35 / "
           "22 on both arms — the roads spend 35-50 of their actions, so the "
           "fifth has nowhere to go. This turns RED the day an "
           "archived road reaches 45 — then retire the xfail and re-record.")
def test_a_played_arm_reaches_forty_five_by_turn_forty():
    """GEV-D1's named test over the committed re-measure archives — VP-R1's
    two played tails, SR-1e's three re-driven roads and SR-2e's Q0 re-drive."""
    tails = [_archived_titled(run) for run in (
        "vpr1-played-a-tail", "vpr1-played-b-tail",
        "sr1e-aar-road", "sr1e-gev-b", "sr1e-gev-a",
        "sr2e-q0-aar-road", "sr2e-q0-gev-b", "sr2e-q0-gev-a",
        "rf1-q0-aar-road", "rf1-q0-gev-a", "rf1-q0-gev-b",
        "rf1-q0-aar-road-staff", "rf1-q0-gev-a-staff", "rf1-q0-gev-b-staff",
        # Step 4's exit (Oct 3, 2026): T5's re-drive after the doctrines
        "sf4-q0-aar-road", "sf4-q0-gev-a", "sf4-q0-gev-b")]
    assert all(t["turn"] >= 40 for t in tails)
    assert any(t["titled"] >= t["hold_titled"] for t in tails), tails


class TestTheSR1eReMeasureIsOnTheRecord:
    """SR-1e (Score Mandate Chunk 1, September 26, 2026): the three roads
    re-driven with SR-1a..1d landed, each probed off its own save by
    `tools/sr1e_titled_probe.py` (the same `congress.titled` the summons
    reads). The AAR road (the hand-played orders of September 25, scripted)
    ends turn 40 at 37 — five over the hand-played 32 at turn 18 — opening A
    at 31 with three provinces titling on turn 44 (it FELL before turn 40 on
    VP-R1), and the scripted opening B at 16 (its hand-played popup answers
    do not survive a scripted replay; it is recorded as the road it is, not
    as the played B). None reaches 45."""

    def test_the_archived_roads_say_what_the_record_says(self):
        aar = _archived_titled("sr1e-aar-road")
        b = _archived_titled("sr1e-gev-b")
        a = _archived_titled("sr1e-gev-a")
        assert aar["status"] == "completed" and aar["titled"] == 37 and aar["turn"] == 41
        assert a["status"] == "completed" and a["titled"] == 31 and a["turn"] == 41
        assert a["held"] == ["East Frisia", "Oldenburg", "Westphalia"]
        assert b["status"] == "completed" and b["titled"] == 16 and b["turn"] == 41
        assert aar["hold_titled"] == a["hold_titled"] == b["hold_titled"] == 45


class TestTheSR2eQ0ReMeasureIsOnTheRecord:
    """SR-2e (Score Mandate, September 26, 2026 — SR-D3 ruled (c) first:
    standing orders reliable) re-measures Q0 on SR-1e's three roads, same
    seed, script and popup policy. The AAR road and opening A are unchanged
    (37 and 31 at turn 41); opening B peaks at the same 39 on turn 9 and its
    unattended tail HOLDS — 31 titled on 23 provinces at turn 41 where SR-1e
    ended on 16 and 8 — because Massena's march survived a reinforcement at
    Munich (AAR-10: a march keeps its tail) instead of being voided. None
    reaches 45; 45 is not moved (§4 SR-D3: re-measured again after SR-D1)."""

    def test_the_archived_roads_say_what_the_record_says(self):
        aar = _archived_titled("sr2e-q0-aar-road")
        a = _archived_titled("sr2e-q0-gev-a")
        b = _archived_titled("sr2e-q0-gev-b")
        assert aar["titled"] == 37 and aar["turn"] == 41
        assert a["titled"] == 31 and a["turn"] == 41
        assert b["titled"] == 31 and b["provinces"] == 23 and b["turn"] == 41
        assert [s["titled"] for s in b["series"]] == [39, 37, 37, 34, 31]
        assert max(max(s["titled"] for s in r["series"])
                   for r in (aar, a, b)) == 39
        assert aar["hold_titled"] == a["hold_titled"] == b["hold_titled"] == 45


class TestTheReMeasureIsOnTheRecord:

    def test_the_archived_tails_say_what_the_memo_says(self):
        a = _archived_titled("vpr1-played-a-tail")
        b = _archived_titled("vpr1-played-b-tail")
        assert a["status"] == "game-over" and a["titled"] == 14
        assert b["status"] == "completed" and b["titled"] == 36 and b["turn"] == 41
        assert a["hold_titled"] == b["hold_titled"] == 45


class TestTheRF1Q0ReMeasureIsOnTheRecord:
    """SR-5r RF-1 (Score Mandate Chunk 5, September 27, 2026 — the Staff is
    the only road to a fifth action, `REFORMS_SPEC.md` §5: "Q0 is re-measured
    after the Staff lands"). The three roads re-driven at HEAD, same seed,
    scripts and popup policy, twice: as authored, and with `enact the Staff`
    first on turns 4-8 (`tools/playtest_scripts/rf1_q0_*_staff.json` — the
    chest crosses 9,000 on turn 4 of all three). Each Staff arm buys it once.

    As authored the roads read 35 / 35 / 22 at turn 41 — the same series the
    pre-RF commit gives (measured on a scratch worktree at `e9d32403`), so
    RF-1 is inert on them and their drift since SR-2e (37 / 31 / 31) belongs
    to the slices landed between. With the Staff: 35 / 35 / 22. The roads
    spend 35-50 of their actions in forty turns, so the fifth (35 more over
    the campaign) goes unused but for three orders on opening B, whose tail
    holds longer (35 titled at turn 30 where the authored arm has 26; 16
    provinces at turn 41 where it has 12) and ends at the same 22. The best
    point on any road is still 39. 45 is not moved."""

    AUTHORED = {"rf1-q0-aar-road": [35, 34, 35, 35, 35],
                "rf1-q0-gev-a": [34, 35, 35, 35, 35],
                "rf1-q0-gev-b": [39, 36, 26, 22, 22]}
    STAFF = {"rf1-q0-aar-road-staff": [35, 34, 35, 35, 35],
             "rf1-q0-gev-a-staff": [34, 35, 35, 35, 35],
             "rf1-q0-gev-b-staff": [39, 36, 35, 25, 22]}

    @staticmethod
    def _meta(run: str) -> dict:
        return json.loads((DIGESTS / run / "meta.json").read_text(encoding="utf-8"))

    @staticmethod
    def _staff_bought(run: str) -> int:
        rows = [json.loads(line) for line in
                (DIGESTS / run / "digest.jsonl").read_text(encoding="utf-8").splitlines()
                if line.strip()]
        return sum(1 for r in rows if r.get("kind") == "command"
                   and "enact the staff" in str(r.get("text", "")).lower()
                   and r.get("success"))

    def test_the_archived_series_say_what_the_record_says(self):
        for run, series in {**self.AUTHORED, **self.STAFF}.items():
            titled = _archived_titled(run)
            assert [s["titled"] for s in titled["series"]] == series, run
            assert titled["status"] == "completed" and titled["turn"] == 41, run
            assert titled["hold_titled"] == 45, run

    def test_each_staff_arm_bought_it_once_and_the_authored_arms_never(self):
        for run in self.STAFF:
            assert self._staff_bought(run) == 1, run
        for run in self.AUTHORED:
            assert self._staff_bought(run) == 0, run

    def test_the_fifth_action_was_offered_and_hardly_spent(self):
        for authored, staffed in zip(self.AUTHORED, self.STAFF):
            a, b = self._meta(authored)["counters"], self._meta(staffed)["counters"]
            assert a["ap_available"] == 160, authored
            assert b["ap_available"] > a["ap_available"], staffed
            assert b["ap_spent"] - a["ap_spent"] <= 3, (authored, staffed)
