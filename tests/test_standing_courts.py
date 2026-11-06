"""AU-4 "the courts' flip" (docs/AUTHORITY_CURRENCY_SPEC.md §5.7, §4.1 reading
16, the record §6.7) and AU-19 at its head.

- AU-19: a capital is lost only by its defender, when it falls in the battle
  — a lost assault on a capital, or a lost field at a capital that holds, is
  a field (−5 only when the loser outnumbered).
- AU-4 (the row): `group_orders.authority_of` reads the one reader for a
  court — the table's figure, 60 for a court missing from it, never 75.
- The courts' writes, the player's own rules, built behind
  `standing.courts_move()` (arm AUC) — FLIPPED UP by the user's "Flip, flat
  grip" (November 6, 2026; the record §6.8): a field's
  writes for every court in it (AI against AI included, the player's side
  never touched), a garrison stormed or repulsed, the auto-charge mirror's own
  rules, a court's Bulletin (+4, no repayment — a court keeps no ring), the
  courts' cooldowns in the tracker's `held`.
- A court proclaims only on its own eve of battle: the courts' rung asks a
  latched offer's latch bit, and the march is read from the lord's own sight.
- AU-5 DECIDED by the same word: every court's grip keeps the flat 75 — its
  books are not read; the reason is written beside
  `authority.GRIP_ENEMY_COURT_BASE` and the measured alternative's seam (AUG)
  is gone with the decision.
- The Nations row: the court's figure and its term in the diplomatic points.
"""
from __future__ import annotations

import contextlib
import copy
import io
import json
import os
from pathlib import Path

import pytest

from backend.game_logic import standing as ST
from tests.conftest import MarshalFactory

REPO = Path(__file__).resolve().parents[1]
SCENARIO = REPO / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
FIXTURE = REPO / "tests" / "fixtures" / "affairs_block.json"


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


def _war_world():
    from tests.test_r1_pipeline_enforcement import _setup_war_world
    with _quiet():
        return _setup_war_world()


def _pipeline(world, **ctx):
    from backend.commands.executor import CommandExecutor
    from tests.test_r1_pipeline_enforcement import _make_basic_ctx
    with _quiet():
        return CommandExecutor()._post_combat_pipeline(_make_basic_ctx(world, **ctx), world)


def _courts_up(monkeypatch):
    monkeypatch.setattr(ST, "courts_move", lambda *a, **k: True)


@pytest.fixture(scope="module")
def boot():
    os.environ.setdefault("LLM_MODE", "mock")
    from backend.models.world_state import WorldState
    with _quiet():
        return WorldState.from_scenario(str(SCENARIO))


@pytest.fixture
def w(boot):
    return copy.deepcopy(boot)


# ═══════════════════════════════════════════════════════════════════════════
# AU-19 — a capital is lost only by its defender, when it falls
# ═══════════════════════════════════════════════════════════════════════════

class TestAU19ACapitalIsLostByItsDefender:
    def test_a_lost_assault_on_an_enemy_capital_is_a_field(self):
        """Ney outnumbered at Berlin and repulsed: no "the capital at Berlin,
        lost" (it was never France's) — and no field lost, Ney did not
        outnumber them (it booked −5 before AU-19)."""
        world = _war_world()
        world.marshals["Ney"].location = "Berlin"
        before = world.authority_tracker.authority
        _pipeline(world, battle_region="Berlin", outcome="defender_victory", attacker_won=False,
                  defender_won=True, pre_battle_attacker_strength=20000, pre_battle_defender_strength=50000,
                  conquered=False)
        assert world.authority_tracker.authority == before
        assert "capital_lost" not in [m.get("key") for m in world.authority_tracker.moves]

    def test_a_lost_defence_of_a_capital_that_falls_is_a_capital_lost(self):
        world = _war_world()
        ney, bluecher = world.marshals["Ney"], world.marshals["Bluecher"]
        ney.location, bluecher.location = "Paris", "Belgium"
        before = world.authority_tracker.authority
        _pipeline(world, attacker=bluecher, defender=ney, defender_nation="France", battle_region="Paris",
                  outcome="attacker_victory", attacker_won=True, defender_won=False,
                  pre_battle_attacker_strength=50000, pre_battle_defender_strength=20000, conquered=True)
        assert world.authority_tracker.authority == before - 5
        assert world.authority_tracker.moves[-1]["key"] == "capital_lost"
        assert world.authority_tracker.moves[-1]["cause"] == "the capital at Paris, lost"

    def test_a_lost_field_at_a_capital_that_holds_is_a_field(self):
        world = _war_world()
        ney, bluecher = world.marshals["Ney"], world.marshals["Bluecher"]
        ney.location = "Paris"
        before = world.authority_tracker.authority
        _pipeline(world, attacker=bluecher, defender=ney, defender_nation="France", battle_region="Paris",
                  outcome="attacker_victory", attacker_won=True, defender_won=False,
                  pre_battle_attacker_strength=50000, pre_battle_defender_strength=20000, conquered=False)
        assert world.authority_tracker.authority == before            # outnumbered, and Paris holds
        ney.strength = 60000
        _pipeline(world, attacker=bluecher, defender=ney, defender_nation="France", battle_region="Paris",
                  outcome="attacker_victory", attacker_won=True, defender_won=False,
                  pre_battle_attacker_strength=50000, pre_battle_defender_strength=60000, conquered=False)
        assert world.authority_tracker.moves[-1]["key"] == "field_lost"   # outnumbering: the field's −5

    def test_one_named_rule_for_the_player_and_the_courts(self):
        world = _war_world()
        assert ST.capital_lost_by(world, "France", "Paris", True, True) is True        # defended, fallen
        assert ST.capital_lost_by(world, "France", "Paris", True, False) is False      # defended, holds
        assert ST.capital_lost_by(world, "France", "Berlin", False, False) is False    # an assault repulsed
        assert ST.capital_lost_by(world, "France", "Belgium", True, True) is False     # no capital
        src = (REPO / "backend" / "commands" / "combat_executor.py").read_text(encoding="utf-8")
        assert "capital_lost = _standing.capital_lost_by(world, player_nation, battle_region," in src
        assert "if cap_reg.controller != player_nation:" not in src
        # held down (arm AUF, the front page's replay): the old rule, by its lambda
        from tests._standing_seams import STANDING_SEAMS_BY_ROW, parse
        _module, _name, expr = parse(STANDING_SEAMS_BY_ROW["AUF"][0])
        old = eval("lambda *a, **k: " + expr, {})
        assert old(world, "France", "Berlin", False, False) is True                    # the 248 bookings
        assert old(world, "France", "Paris", True, True) is False


# ═══════════════════════════════════════════════════════════════════════════
# AU-4 (the row) — the one reader
# ═══════════════════════════════════════════════════════════════════════════

class TestAU4TheOneReader:
    def test_a_court_reads_its_table_and_a_missing_court_reads_sixty(self):
        from backend.commands import group_orders as G
        world = _war_world()
        world.nation_authority["Prussia"] = 45
        assert G.authority_of(world, "Prussia") == 45 == ST.standing_of(world, "Prussia")
        world.nation_authority.pop("Saxony", None)
        assert G.authority_of(world, "Saxony") == ST.COURT_DEFAULT == 60
        assert G.authority_of(world) == world.authority_tracker.authority        # the player's own tracker


# ═══════════════════════════════════════════════════════════════════════════
# The courts' writes — the player's rules, behind `courts_move()`
# ═══════════════════════════════════════════════════════════════════════════

def _ai_war_world():
    world = _war_world()
    charles = MarshalFactory.infantry(name="Charles", location="Vienna", strength=20000, nation="Austria")
    world.marshals["Charles"] = charles
    world.diplomatic_states["|".join(sorted(["Austria", "Prussia"]))] = "WAR"
    world.nation_authority.update({"Austria": 50, "Prussia": 50})
    return world


class TestTheCourtsField:
    def test_the_users_word_flipped_it(self, monkeypatch):
        """The user's "Flip, flat grip" (November 6, 2026): the courts' writes
        are up by default, and arm AUC (`courts_move` held down) is the tree AU-4
        part 1 left — re-pinned consciously from `test_parked_until_the_users_word`."""
        assert ST.courts_move() is True
        world = _ai_war_world()
        ST.courts_battle(world, "Vienna", "Prussia", "Austria", True, False, 10000, 30000)
        assert (world.nation_authority["Prussia"], world.nation_authority["Austria"]) == (55, 45)
        monkeypatch.setattr(ST, "courts_move", lambda *a, **k: False)        # arm AUC
        assert ST.courts_battle(world, "Vienna", "Prussia", "Austria", True, False, 10000, 30000) == 0
        assert (world.nation_authority["Prussia"], world.nation_authority["Austria"]) == (55, 45)

    def test_ai_against_ai_both_sides_and_the_player_untouched(self, monkeypatch):
        _courts_up(monkeypatch)
        world = _ai_war_world()
        france = world.authority_tracker.authority
        # Prussia outnumbered and the victor; Austria outnumbering and beaten; no laurel (3,000 v 4,000)
        moved = ST.courts_battle(world, "Saxony", "Prussia", "Austria", True, False, 10000, 30000,
                                 atk_cas=3000, def_cas=4000)
        assert world.nation_authority["Prussia"] == 55 and world.nation_authority["Austria"] == 45
        assert moved == 0 and world.authority_tracker.authority == france
        ST.courts_battle(world, "Saxony", "France", "Austria", False, True, 50000, 20000)
        assert world.authority_tracker.authority == france                 # the player's side is the pipeline's

    def test_the_sovereign_s_hand_and_the_capitals(self, monkeypatch):
        _courts_up(monkeypatch)
        world = _ai_war_world()
        lead = world.marshals["Charles"]
        lead.personality = "sovereign"                  # `Marshal.is_sovereign` reads the personality
        # Austria storms Berlin (a capital) at even numbers under its sovereign: +5 taken, +2 the hand
        ST.courts_battle(world, "Berlin", "Austria", "Prussia", True, False, 20000, 20000, conquered=True,
                         atk_lead=lead)
        assert world.nation_authority["Austria"] == 57
        assert world.nation_authority["Prussia"] == 45                      # the defender's capital fell: −5
        # the auto-charge mirror's own rules: no capital lost there
        world.nation_authority["Prussia"] = 50
        ST.courts_battle(world, "Berlin", "Austria", "Prussia", True, False, 20000, 20000, conquered=True,
                         lost_capitals=False)
        assert world.nation_authority["Prussia"] == 50
        # a beaten sovereign: −5 the hand
        ST.courts_battle(world, "Saxony", "Austria", "Prussia", False, True, 10000, 30000, atk_lead=lead)
        assert world.nation_authority["Austria"] == 57 + 5 - 5             # the field won above, then the hand lost

    def test_a_court_s_bulletin_and_its_cooldown_in_the_tracker_s_held(self, monkeypatch):
        _courts_up(monkeypatch)
        world = _ai_war_world()
        world.current_turn = 10
        # a laurel: Prussia's dead at most half Austria's, a battle's size
        ST.courts_battle(world, "Saxony", "Prussia", "Austria", True, False, 30000, 30000,
                         atk_cas=2000, def_cas=9000)
        assert world.nation_authority["Prussia"] == 50 + ST.BULLETIN_AMOUNT
        assert world.authority_tracker.held["last:Prussia|bulletin"] == 10
        ST.courts_battle(world, "Saxony", "Prussia", "Austria", True, False, 30000, 30000,
                         atk_cas=2000, def_cas=9000)
        assert world.nation_authority["Prussia"] == 54                     # inside its three turns
        world.current_turn = 13
        assert ST.bulletin(world, "Prussia", "Saxony", 2000, 9000) == (ST.BULLETIN_AMOUNT, 0)   # no repayment

    def test_a_court_s_te_deum_keeps_its_twelve_turns(self, monkeypatch):
        _courts_up(monkeypatch)
        world = _ai_war_world()
        world.current_turn = 20
        assert ST.regrow(world, "Austria", 4, "te_deum", "te_deum", every=ST.TE_DEUM_EVERY) == 4
        world.current_turn = 25
        assert ST.regrow(world, "Austria", 4, "te_deum", "te_deum", every=ST.TE_DEUM_EVERY) == 0
        assert world.authority_tracker.held["last:Austria|te_deum"] == 20
        assert "last:te_deum" not in world.authority_tracker.held           # the player's own key untouched

    def test_a_garrison_stormed_and_repulsed(self, monkeypatch):
        _courts_up(monkeypatch)
        world = _ai_war_world()
        berlin = world.get_region("Berlin")
        assert ST.courts_garrison(world, "Austria", berlin, 10000, 15000, True) == 10      # odds and a capital
        assert ST.courts_garrison(world, "Austria", berlin, 20000, 15000, False) == -5    # with the numbers
        assert ST.courts_garrison(world, "France", berlin, 10000, 15000, True) == 0       # never the player

    def test_the_pipeline_writes_the_courts_side_of_an_ai_field(self, monkeypatch):
        world = _ai_war_world()
        bluecher, charles = world.marshals["Bluecher"], world.marshals["Charles"]
        ctx = dict(attacker=bluecher, defender=charles, defender_nation="Austria", battle_region="Saxony",
                   outcome="attacker_victory", attacker_won=True, defender_won=False,
                   attacker_casualties=3000, defender_casualties=4000,
                   pre_battle_attacker_strength=10000, pre_battle_defender_strength=30000, conquered=False)
        monkeypatch.setattr(ST, "courts_move", lambda *a, **k: False)        # arm AUC: AU-4 part 1's tree
        _pipeline(world, **ctx)
        assert (world.nation_authority["Prussia"], world.nation_authority["Austria"]) == (50, 50)
        monkeypatch.undo()                                                   # the flip: the default
        _pipeline(world, **ctx)
        assert (world.nation_authority["Prussia"], world.nation_authority["Austria"]) == (55, 45)

    def test_the_call_sites_are_one_line_and_the_mirror_keeps_its_rules(self):
        src = (REPO / "backend" / "commands" / "combat_executor.py").read_text(encoding="utf-8")
        assert src.count("_court_standing.courts_battle(") == 1
        assert src.count("_standing.courts_garrison(") == 2
        mirror = (REPO / "backend" / "models" / "world_state.py").read_text(encoding="utf-8")
        assert mirror.count("_court_standing.courts_battle(") == 1 and "lost_capitals=False)" in mirror


# ═══════════════════════════════════════════════════════════════════════════
# AU-20 — the courts' Decree is paid in authority (found at the flip)
# ═══════════════════════════════════════════════════════════════════════════

class TestAU20TheCourtsDecreePaysInAuthority:
    """AU-20 (BUG_FIXES.md §AU, found by the flip's suite run, November 6,
    2026): the rung's order carries `currency: "authority"` where a court's
    gold refuses its reserve bar; the AI's admin step dropped it, so the
    executor decreed in gold, under that bar, the court's authority unmoved."""

    def test_the_admin_command_carries_the_rungs_currency(self, w, monkeypatch):
        from types import SimpleNamespace
        from backend.ai.enemy_ai import EnemyAI
        picks = [{"action": "decree_edict", "target": "the_remounts", "currency": "authority"}]
        monkeypatch.setattr(EnemyAI, "_pick_admin_action",
                            lambda self, nation, world, ap, skip=None: picks.pop() if picks else None)
        seen = []
        ai = EnemyAI(SimpleNamespace(execute=lambda c, g: seen.append(dict(c["command"])) or {"success": True}))
        with _quiet():
            ai.execute_admin_phase("Austria", w, {"world": w})
        assert seen and seen[0]["currency"] == "authority" and seen[0]["_acting_nation"] == "Austria"

    def test_the_court_pays_its_floors_not_its_purse(self, w):
        from backend.commands.executor import CommandExecutor
        from backend.game_logic import affairs as AF
        w.nation_gold["Austria"], w.nation_authority["Austria"] = 2_000, 60
        assert AF.find_ai_edict(w, "Austria", 2_000, 2) == {"action": "decree_edict", "target": "the_remounts",
                                                            "currency": "authority"}   # under the gold bar
        with _quiet():
            result = CommandExecutor().execute(
                {"command": {"action": "decree_edict", "target": "the_remounts", "currency": "authority",
                             "_acting_nation": "Austria", "type": "specific"}}, {"world": w})
        assert result["success"], result.get("message")
        assert (w.nation_gold["Austria"], w.nation_authority["Austria"]) == (2_000, 57)
        row = [ev for ev in w.event_log if ev.get("type") == "moment" and ev.get("nation") == "Austria"][-1]
        assert row["line"] == "Austria decrees the Remounts for 8 turns (3 authority)"


class TestTheFlipsRecord:
    """The flip's record (`tools/_standing_courts_flip.py` → `tools/_standing_courts_flip.json`,
    AUTHORITY_CURRENCY_SPEC.md §6.8.2): the parked tree, the courts up as the
    review measured them (AU-20 in the tree) and the flip as shipped, on the
    59 measured runs. Seeded paths, not laws — the figures are the record's;
    the pins read the shape of the difference."""

    def test_the_courts_decree_in_authority_only_on_the_flipped_tree(self):
        rec = json.loads((REPO / "tools" / "_standing_courts_flip.json").read_text(encoding="utf-8"))
        assert rec["runs_measured"] >= 55
        assert rec["court_decrees_in_authority"]["parked"] == rec["court_decrees_in_authority"]["reviewed"] == 0
        assert rec["court_decrees_in_authority"]["flipped"] > 0
        moves = rec["court_moves_by_cause"]
        assert set(moves["parked"]) == {"law"}                         # parked: the courts' laws alone
        for cause in ("field_won", "field_lost", "bulletin", "capital_stormed", "assault_repulsed", "te_deum"):
            assert moves["flipped"].get(cause, 0) > 0, cause            # the courts take the player's rules
        assert moves["flipped"]["law"] < moves["reviewed"]["law"] < moves["parked"]["law"]

    def test_the_rig_carries_the_flip_and_its_find(self):
        rec = json.loads((REPO / "tools" / "_standing_courts_flip.json").read_text(encoding="utf-8"))
        rig = rec["rig"]
        assert rig["AUC"]["first_divergence_vs_prior"] is None          # the courts held down: part 1's tree
        assert rig["AUD"]["first_divergence_vs_prior"] == 10            # AU-20 held down: the review's tree
        assert rig["ALL"]["first_divergence_vs_prior"] == 16


# ═══════════════════════════════════════════════════════════════════════════
# A court proclaims only on its own eve of battle
# ═══════════════════════════════════════════════════════════════════════════

class TestTheCourtsProclamation:
    def _court_board(self, w, monkeypatch, latch):
        from backend.game_logic import affairs as AF
        from backend.game_logic import moments as MO
        w.moments = MO.from_block(json.loads(FIXTURE.read_text(encoding="utf-8")))
        aff = w.moments["block"]["affairs"]
        aff["deck"] = [e for e in aff["deck"] if e.get("id") == "the_proclamation"]
        w.__dict__.pop("_affairs_memo", None)
        _courts_up(monkeypatch)
        monkeypatch.setattr(AF, "_enemy_within_a_march", lambda world, lord: ("Ney", "Swabia") if latch else None)
        w.nation_authority["Austria"] = 60
        return AF

    def test_a_court_at_war_with_no_enemy_near_never_proclaims(self, w, monkeypatch):
        AF = self._court_board(w, monkeypatch, latch=False)
        assert AF.find_ai_edict(w, "Austria", 0, 1) is None

    def test_on_its_eve_of_battle_the_court_proclaims_in_authority(self, w, monkeypatch):
        AF = self._court_board(w, monkeypatch, latch=True)
        assert AF.find_ai_edict(w, "Austria", 0, 1) == {"action": "decree_edict", "target": "the_proclamation",
                                                         "currency": "authority"}

    def test_the_march_is_read_from_the_lord_s_own_sight(self, w, monkeypatch):
        """On the 1805 board Napoleon is the one sovereign in the field, so a
        court's march reads None before any sight — no court proclaims there
        (§6.7 reading 5); a staged Austrian sovereign reads its own live sight."""
        from backend.game_logic import affairs as AF
        assert AF._enemy_within_a_march(w, "Austria") is None          # no Austrian sovereign in the field
        lead = next(m for m in w.marshals.values() if m.nation == "Austria")
        lead.personality = "sovereign"
        seen = []
        monkeypatch.setattr(type(w), "get_visible_enemies", lambda self, n: seen.append(("fog", n)) or [])
        monkeypatch.setattr(type(w), "get_live_visible_enemies", lambda self, n: seen.append(("live", n)) or [])
        AF._enemy_within_a_march(w, "France")
        AF._enemy_within_a_march(w, "Austria")
        assert ("fog", "France") in seen and ("live", "Austria") in seen
        assert ("fog", "Austria") not in seen


# ═══════════════════════════════════════════════════════════════════════════
# AU-5 — the grip: DECIDED, the flat 75 kept with its reason
# ═══════════════════════════════════════════════════════════════════════════

class TestAU5TheGrip:
    def test_the_flat_75_kept_with_its_reason(self, w):
        """AU-5 DECIDED by the user's "Flip, flat grip" (November 6, 2026): a
        court's grip keeps the flat base whatever its books — the reason is
        written beside `authority.GRIP_ENEMY_COURT_BASE`; the alternative (the
        books read relative to the boot, seam AUG, and the gate's direct read)
        is removed with its decision, its measure kept as the record —
        re-pinned consciously from `test_down_the_flat_75_up_the_books_relative_to_the_boot`."""
        from backend.models import authority as AUTH
        assert AUTH.GRIP_ENEMY_COURT_BASE == 75
        assert not hasattr(AUTH, "court_grip_base") and not hasattr(ST, "court_grip_reads_books")
        grips = []
        for figure in (25, 30, 60, 95):
            w.nation_authority["Austria"] = figure
            grips.append(AUTH.get_imperial_grip(w, "Austria"))
        assert len(set(grips)) == 1, grips                                  # the books are not read
        src = (REPO / "backend" / "models" / "authority.py").read_text(encoding="utf-8")
        assert 'DECIDED at the courts\' flip by the user\'s "Flip, flat' in src
        assert "coalition's leadership" in src and "bites nowhere" in src
        review = json.loads((REPO / "tools" / "_standing_courts_au4.json").read_text(encoding="utf-8"))
        assert set(review["courts_mean_end"]) == {"shipped", "flat", "grip"}   # the three grips measured


# ═══════════════════════════════════════════════════════════════════════════
# The Nations row and the seams
# ═══════════════════════════════════════════════════════════════════════════

class TestTheNationsRowAndTheSeams:
    def test_the_row_carries_the_figure_and_its_dp_term(self, w):
        from backend.game_logic import diplomatic_ledger as DL
        from backend.game_logic.diplomacy import authority_dp_bonus, calculate_dp
        assert [authority_dp_bonus(a) for a in (100, 60, 59, 45, 30, 29, 0)] == [1, 1, 0, 0, 0, -1, -1]
        assert calculate_dp(None, 60, True) == 4 and calculate_dp(None, 29, True) == 2
        w.nation_authority["Austria"] = 25
        assert DL._authority_row("Austria", w) == {"figure": 25, "dp": -1}
        with _quiet():
            ledger = DL.build_diplomatic_ledger(w)
        rows = {r["name"]: r for r in ledger["nations"]}
        assert rows["Austria"]["authority"] == {"figure": 25, "dp": -1}
        assert rows["Prussia"]["authority"]["figure"] == w.nation_authority["Prussia"]

    def test_the_client_says_the_term_only_when_it_is_not_zero(self):
        src = (REPO / "godot-client" / "project-sovereign" / "scripts" / "diplomatic_ledger.gd").read_text(
            encoding="utf-8")
        assert 'var auth_row = n.get("authority")' in src
        assert '" (+" + str(auth_dp) + " diplomatic point a turn)"' in src
        assert '" (−" + str(-auth_dp) + " diplomatic point a turn)"' in src

    def test_the_seam_and_its_arm(self):
        """The flip (November 6, 2026): AUC holds the courts down on its arm; the
        rig's AUC+ arms are retired (ALL is that arm) and AU-5's AUG with its
        decision — re-pinned consciously from `test_the_two_seams_and_their_arms`."""
        from tests._standing_seams import STANDING_SEAMS_BY_ROW
        assert STANDING_SEAMS_BY_ROW["AUC"] == ["backend.game_logic.standing:courts_move=False"]
        assert "AUG" not in STANDING_SEAMS_BY_ROW
        assert ST.courts_move() is True
        rig = (REPO / "tools" / "_standing_series_arms.py").read_text(encoding="utf-8")
        assert "UP_ARMS: dict = {}" in rig and "court_grip_reads_books" not in rig and "AUGD" not in rig
