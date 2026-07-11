"""
MC-2b — administration WIRED: "The Intendance" (MC exit review, July 11, 2026).

Contract: MARSHAL_CONTENT_PASS_SPEC.md §4 (the MC-2b owner row) — admin
consumed at the recruit seam at code-verified numbers, the card row restored,
and the memo-§3 reserved administration values landed live in europe_1805.json.

Mechanic (single source marshal.py, the Rally pattern):
- administration >= 8 (INTENDANCE_THRIFTY_ADMIN): recruits cost 15% less
- administration <= 3 (INTENDANCE_WASTEFUL_ADMIN): recruits cost 15% more
- administration 4-7: byte-identical baseline

Seam: economy_executor._calculate_recruit_cost applies the modifier LAST,
inside the same Europe-scoped nation-pricing block as the W6-11 war multiplier
(N1: the legacy fixture world's economy pins must not move). The AI pays the
same price through the same helper (GR5).
"""

import json
from pathlib import Path

import pytest

from backend.ai.parser_eval import build_world
from backend.ai.validation import VALID_ACTIONS
from backend.commands.executor import CommandExecutor
from backend.game_logic.marshal_overview import build_marshal_overview
from backend.models.marshal import Marshal
from backend.models.world_state import WorldState


@pytest.fixture()
def world():
    return build_world("1805")


# Memo-§3 reserved administration values, landed live at MC-2b.
ADMIN_TABLE = {
    "Ney": 3, "Davout": 8, "Soult": 7, "Lannes": 4, "Murat": 2,
    "Bernadotte": 7, "Massena": 3, "Deroy": 5, "Mack": 7,
    "ArchdukeCharles": 8, "ArchdukeJohn": 4, "Kutuzov": 4, "Buxhowden": 4,
    "Moore": 8, "Brunswick": 5, "Hohenlohe": 4, "Armfelt": 5, "Damas": 4,
    "Frederick": 7, "Castanos": 4, "Abdurrahman": 4,
}

THRIFTY = {"Davout", "ArchdukeCharles", "Moore"}
WASTEFUL = {"Ney", "Murat", "Massena"}


def make_admin_marshal(admin, name="Test", nation="France",
                       location="Rhineland", cavalry=False):
    m = Marshal(name=name, location=location, strength=30000,
                personality="cautious", nation=nation, spawn_location=location)
    m.skills["administration"] = admin
    m.cavalry = cavalry
    return m


def make_europe_world(*marshals, player="France", at_peace=True):
    w = WorldState(player_nation=player, sovereign_map="europe")
    if at_peace:
        # The bare flag world boots with the legacy war seed — strip it so
        # "peacetime" pricing means what it says.
        for key in [k for k, v in w.diplomatic_states.items() if v == "WAR"]:
            del w.diplomatic_states[key]
    for m in marshals:
        w.marshals[m.name] = m
    return w


def prep_region(world, name, controller, stability=100):
    region = world.get_region(name)
    region.controller = controller
    region.stability = stability
    return region


# ════════════════════════════════════════════════════════════════════════
# Authored values: the reserved memo-§3 column is live on the 1805 roster
# ════════════════════════════════════════════════════════════════════════

class TestAuthoredAdminValues:
    @pytest.mark.parametrize("name", sorted(ADMIN_TABLE))
    def test_marshal_boots_with_authored_admin(self, world, name):
        assert world.get_marshal(name).skills["administration"] == \
            ADMIN_TABLE[name], name

    def test_roster_admin_mean_in_band(self):
        # Memo §3 balance frame: per-skill roster means 4.95-5.10.
        mean = sum(ADMIN_TABLE.values()) / len(ADMIN_TABLE)
        assert 4.95 <= mean <= 5.10, f"admin mean {mean:.3f} out of band"

    def test_tier_membership_exact(self, world):
        for name in ADMIN_TABLE:
            m = world.get_marshal(name)
            mod = m.get_recruit_cost_modifier()
            if name in THRIFTY:
                assert mod == pytest.approx(0.85), name
            elif name in WASTEFUL:
                assert mod == pytest.approx(1.15), name
            else:
                assert mod == 1.0, name

    def test_admin_survives_serialization(self, world):
        davout = world.get_marshal("Davout")
        restored = Marshal.from_dict(davout.to_dict())
        assert restored.skills["administration"] == 8
        assert restored.get_recruit_cost_modifier() == pytest.approx(0.85)


# ════════════════════════════════════════════════════════════════════════
# Single source: marshal.get_recruit_cost_modifier boundaries
# ════════════════════════════════════════════════════════════════════════

class TestModifierSingleSource:
    @pytest.mark.parametrize("admin,expected", [
        (10, 0.85), (9, 0.85), (8, 0.85),   # thrifty tier
        (7, 1.0), (5, 1.0), (4, 1.0),       # baseline, byte-identical
        (3, 1.15), (2, 1.15), (1, 1.15),    # wasteful tier
    ])
    def test_tier_boundaries(self, admin, expected):
        m = make_admin_marshal(admin)
        assert m.get_recruit_cost_modifier() == pytest.approx(expected)

    def test_default_skills_marshal_is_baseline(self):
        m = Marshal(name="Plain", location="Rhineland", strength=10000,
                    personality="cautious", nation="France",
                    spawn_location="Rhineland")
        assert m.get_recruit_cost_modifier() == 1.0

    def test_constants_are_the_blessed_numbers(self):
        # In-band tunable; a change here is a tuning decision, not drift.
        assert Marshal.INTENDANCE_THRIFTY_ADMIN == 8
        assert Marshal.INTENDANCE_WASTEFUL_ADMIN == 3
        assert Marshal.INTENDANCE_COST_SWING == pytest.approx(0.15)


# ════════════════════════════════════════════════════════════════════════
# The recruit-cost seam: code-verified numbers (contract wording)
# ════════════════════════════════════════════════════════════════════════

class TestRecruitCostSeam:
    def _cost(self, world, region, marshal=None, nation="France",
              base_cost=200):
        return CommandExecutor()._economy._calculate_recruit_cost(
            region, world, base_cost=base_cost, nation=nation,
            marshal=marshal)

    def test_peacetime_thrifty_170_wasteful_230(self):
        thrifty = make_admin_marshal(8, name="Thrifty")
        wasteful = make_admin_marshal(3, name="Wasteful")
        w = make_europe_world(thrifty, wasteful)
        region = prep_region(w, "Rhineland", "France")
        assert self._cost(w, region) == 200                      # no marshal
        assert self._cost(w, region, thrifty) == 170             # int(200*0.85)
        assert self._cost(w, region, wasteful) == 230            # int(200*1.15)

    def test_war_pricing_composes_before_intendance(self):
        # W6-11 x3 first, intendance LAST on the composed price.
        thrifty = make_admin_marshal(8, name="Thrifty")
        wasteful = make_admin_marshal(3, name="Wasteful")
        w = make_europe_world(thrifty, wasteful)
        region = prep_region(w, "Rhineland", "France")
        w.diplomatic_states["France|Britain"] = "WAR"
        assert self._cost(w, region) == 600                      # 200*3
        assert self._cost(w, region, thrifty) == 510             # int(600*0.85)
        assert self._cost(w, region, wasteful) == 690            # int(600*1.15)

    def test_legacy_world_is_untouched(self):
        # N1: the modifier lives inside the Europe pricing block — a legacy
        # world prices recruits exactly as before even for an admin-8 marshal.
        w = WorldState(player_nation="France")
        davout = w.get_marshal("Davout")           # legacy fixture admin 8
        assert davout.skills["administration"] == 8
        region = w.get_region("Paris")
        cost = CommandExecutor()._economy._calculate_recruit_cost(
            region, w, base_cost=200, nation="France", marshal=davout)
        assert cost == int(200 * 0.75)              # capital discount only

    def test_result_is_int(self):
        thrifty = make_admin_marshal(8, name="Thrifty")
        w = make_europe_world(thrifty)
        region = prep_region(w, "Rhineland", "France")
        assert isinstance(self._cost(w, region, thrifty, base_cost=333), int)


# ════════════════════════════════════════════════════════════════════════
# End-to-end through _execute_recruit on the shipped 1805 campaign
# ════════════════════════════════════════════════════════════════════════

class TestRecruitEndToEnd:
    def _recruit(self, world, name):
        world.nation_gold.setdefault("France", 0)
        world.nation_gold["France"] = max(world.nation_gold["France"], 20000)
        return CommandExecutor()._economy._execute_recruit(
            {"marshal": name}, {"world": world})

    def test_davout_prices_15_under_ney_at_same_region(self, world):
        # Both boot at Rhineland, both infantry: the same composed base, so
        # the intendance is the entire difference (shown = applied).
        executor = CommandExecutor()
        region = world.get_region("Rhineland")
        base = executor._economy._calculate_recruit_cost(
            region, world, base_cost=200, nation="France", marshal=None)

        r_davout = self._recruit(world, "Davout")
        assert r_davout["success"] is True, r_davout["message"]
        assert r_davout["events"][0]["gold_cost"] == int(round(base * 0.85))
        assert r_davout["events"][0]["intendance_pct"] == -15
        assert "Davout's intendance: -15%" in r_davout["message"]

        world2 = build_world("1805")
        r_ney = self._recruit(world2, "Ney")
        assert r_ney["success"] is True, r_ney["message"]
        assert r_ney["events"][0]["gold_cost"] == int(round(base * 1.15))
        assert r_ney["events"][0]["intendance_pct"] == 15
        assert "Ney's intendance: +15%" in r_ney["message"]

    def test_standard_admin_shows_no_intendance_note(self, world):
        r = self._recruit(world, "Soult")            # admin 7 — baseline
        assert r["success"] is True, r["message"]
        assert r["events"][0]["intendance_pct"] == 0
        assert "intendance" not in r["message"]

    def test_gr5_ai_recruit_dict_pays_the_same_price(self, world):
        # The AI recruit action dict carries into the SAME seam: enemy
        # Moore (admin 8) prices his levies thrifty too.
        world.nation_gold["Britain"] = 20000
        world.manpower_pools.setdefault("Britain", {}).setdefault(
            "infantry", 0)
        world.manpower_pools["Britain"]["infantry"] = max(
            world.manpower_pools["Britain"]["infantry"], 50000)
        r = CommandExecutor()._economy._execute_recruit(
            {"marshal": "Moore"}, {"world": world})
        assert r["success"] is True, r["message"]
        assert r["events"][0]["intendance_pct"] == -15
        assert "Moore's intendance: -15%" in r["message"]


# ════════════════════════════════════════════════════════════════════════
# The card: row restored + tier note (shown = applied)
# ════════════════════════════════════════════════════════════════════════

class TestCardRestored:
    def _cards(self, world):
        return {c["name"]: c for c in build_marshal_overview(world)}

    def test_administration_row_and_note_present(self, world):
        cards = self._cards(world)
        for name, card in cards.items():
            assert "administration" in card["skills"], name
            assert isinstance(card["skills"]["administration"], int), name
            assert "administration" in card["skill_notes"], name

    def test_davout_thrifty_note(self, world):
        card = self._cards(world)["Davout"]
        assert card["admin_tier"] == "thrifty"
        assert "15%" in card["admin_note"]

    def test_murat_wasteful_note(self, world):
        card = self._cards(world)["Murat"]
        assert card["admin_tier"] == "wasteful"
        assert "15%" in card["admin_note"]

    def test_soult_standard_empty_note(self, world):
        card = self._cards(world)["Soult"]
        assert card["admin_tier"] == "standard"
        assert card["admin_note"] == ""

    def test_note_swing_derives_from_the_constant(self, world):
        # Single source: the displayed percentage IS the applied constant.
        swing = int(round(Marshal.INTENDANCE_COST_SWING * 100))
        card = self._cards(world)["Davout"]
        assert f"{swing}%" in card["admin_note"]


# ════════════════════════════════════════════════════════════════════════
# Scope boundary: no new player verb (golden-corpus contract check)
# ════════════════════════════════════════════════════════════════════════

class TestNoNewVerb:
    def test_no_new_action_added(self):
        # The Intendance rides the existing recruit verb; MC-2b adds no
        # parser surface, so the CR-1 corpus gains no new coverage burden.
        assert "recruit" in VALID_ACTIONS
        assert "intendance" not in VALID_ACTIONS
        assert "administration" not in VALID_ACTIONS

    def test_recruit_corpus_coverage_exists(self):
        corpus_path = (Path(__file__).parent / "data"
                       / "parser_golden_corpus.json")
        corpus = json.loads(corpus_path.read_text(encoding="utf-8"))
        entries = corpus["entries"] if isinstance(corpus, dict) else corpus
        actions = {(e.get("expected") or {}).get("action")
                   for e in entries if isinstance(e, dict)}
        assert "recruit" in actions
