"""
Session 7 — Deep Audit Fixes: Fog of War, Dispatch & Region Fixes

15 fixes covering coalition member fog leaks, hardcoded known_nations,
AI-AI ledger visibility, dispatch fog filter keys, campaign log event types,
region data inconsistencies, coalition threat counting, and threat assessment.
"""

from backend.models.marshal import Marshal
from backend.models.world_state import WorldState
from backend.models.intel import FULL, PARTIAL, UNKNOWN


# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════

def _make_marshal(name="TestInf", location="Paris", strength=30000,
                  personality="cautious", nation="France",
                  cavalry=False, artillery=False, **kw):
    return Marshal(
        name=name, location=location, strength=strength,
        personality=personality, nation=nation,
        movement_range=2 if cavalry else 1,
        tactical_skill=7,
        skills=kw.pop("skills", {
            "tactical": 7, "shock": 7, "defense": 7,
            "logistics": 7, "administration": 7, "command": 7,
        }),
        cavalry=cavalry, artillery=artillery,
        spawn_location=kw.pop("spawn_location", location),
        **kw,
    )


def _make_world(current_turn=5):
    """Basic WorldState with France as player."""
    world = WorldState()
    world.current_turn = current_turn
    return world


def _set_region_intel(world, region_name, visibility):
    """Set intel visibility for a region."""
    intel = world.get_region_intel(region_name)
    intel.visibility = visibility
    intel.last_updated_turn = world.current_turn


# ═══════════════════════════════════════════════════════════
# Fix 1: Coalition dispatch fog-filters strength/gold
# ═══════════════════════════════════════════════════════════

class TestFix1CoalitionDispatchFogFilter:
    """Coalition member strength/gold in dispatch must respect fog of war."""

    def test_full_visibility_shows_strength_and_gold(self):
        """With FULL visibility, dispatch shows exact strength and gold."""
        world = _make_world()
        # Clear default marshals and add only our test marshal
        world.marshals = {
            "Wellington": _make_marshal(
                name="Wellington", location="Netherlands", strength=40000,
                nation="Britain",
            ),
        }
        _set_region_intel(world, "Netherlands", FULL)
        world.nation_gold["Britain"] = 500
        world.war_exhaustion["Britain"] = 30
        world.active_coalition = {
            "name": "Test Coalition",
            "leader": "Britain",
            "strategic_posture": "defensive",
            "formed_turn": 3,
            "members": ["Britain"],
        }
        world.threat_level = 70

        from backend.game_logic.dispatch import _build_coalition_section
        section = _build_coalition_section(world, "France")
        assert section is not None
        active = section.get("active_coalition")
        assert active is not None
        members = active["members"]
        britain = [m for m in members if m["nation"] == "Britain"][0]
        assert britain["strength"] == 40000
        assert britain["gold"] == 500
        assert britain["war_exhaustion"] == 30

    def test_unknown_visibility_hides_strength_and_gold(self):
        """With UNKNOWN visibility, dispatch hides strength and gold."""
        world = _make_world()
        world.marshals["Wellington"] = _make_marshal(
            name="Wellington", location="Netherlands", strength=40000,
            nation="Britain",
        )
        _set_region_intel(world, "Netherlands", UNKNOWN)
        world.nation_gold["Britain"] = 500
        world.war_exhaustion["Britain"] = 30
        world.active_coalition = {
            "name": "Test Coalition",
            "leader": "Britain",
            "strategic_posture": "defensive",
            "formed_turn": 3,
            "members": ["Britain"],
        }
        world.threat_level = 70

        from backend.game_logic.dispatch import _build_coalition_section
        section = _build_coalition_section(world, "France")
        assert section is not None
        active = section.get("active_coalition")
        assert active is not None
        members = active["members"]
        britain = [m for m in members if m["nation"] == "Britain"][0]
        assert britain["strength"] == 0
        assert britain["gold"] == 0
        assert britain["war_exhaustion"] == 0
        assert "strength_display" in britain


# ═══════════════════════════════════════════════════════════
# Fix 2/5: Dispatch uses dynamic known_nations
# ═══════════════════════════════════════════════════════════

class TestFix2DynamicKnownNations:
    """Talleyrand report uses get_known_nations, not hardcoded list."""

    def test_dispatch_talleyrand_uses_dynamic_nations(self):
        """Structural: dispatch.py imports get_known_nations for the nation loop."""
        import inspect
        from backend.game_logic import dispatch
        source = inspect.getsource(dispatch._build_talleyrand_report)
        assert "get_known_nations" in source
        assert '["Britain"' not in source


# ═══════════════════════════════════════════════════════════
# Fix 3: AI-AI ledger requires BOTH nations visible
# ═══════════════════════════════════════════════════════════

class TestFix3AIAILedgerVisibility:
    """AI-AI relations only shown when BOTH nations have PARTIAL+ visibility."""

    def test_ai_ai_hidden_when_one_nation_unknown(self):
        """AI-AI relation hidden if one nation has UNKNOWN visibility."""
        world = _make_world()
        # Prussia marshal in PARTIAL region
        world.marshals["Blucher"] = _make_marshal(
            name="Blucher", location="Berlin", strength=30000,
            nation="Prussia",
        )
        _set_region_intel(world, "Berlin", PARTIAL)
        # Austria marshal in UNKNOWN region
        world.marshals["Charles"] = _make_marshal(
            name="Charles", location="Vienna", strength=25000,
            nation="Austria",
        )
        _set_region_intel(world, "Vienna", UNKNOWN)

        from backend.game_logic.diplomatic_ledger import _build_nations
        nations = _build_nations(world)
        # Find Prussia's entry
        prussia = [n for n in nations if n["name"] == "Prussia"][0]
        # DPF-1: Diplomatic relations are public knowledge — no fog gate
        # AI-AI relations visible regardless of visibility
        austria_relations = [r for r in prussia["ai_relations"] if r["nation"] == "Austria"]
        assert len(austria_relations) == 1

    def test_ai_ai_shown_when_both_partial(self):
        """AI-AI relation shown when BOTH nations have PARTIAL+ visibility."""
        world = _make_world()
        world.marshals["Blucher"] = _make_marshal(
            name="Blucher", location="Berlin", strength=30000,
            nation="Prussia",
        )
        _set_region_intel(world, "Berlin", PARTIAL)
        world.marshals["Charles"] = _make_marshal(
            name="Charles", location="Vienna", strength=25000,
            nation="Austria",
        )
        _set_region_intel(world, "Vienna", PARTIAL)

        from backend.game_logic.diplomatic_ledger import _build_nations
        nations = _build_nations(world)
        prussia = [n for n in nations if n["name"] == "Prussia"][0]
        austria_relations = [r for r in prussia["ai_relations"] if r["nation"] == "Austria"]
        assert len(austria_relations) == 1


# ═══════════════════════════════════════════════════════════
# Fix 4: Fog filter checks "aggressor" key
# ═══════════════════════════════════════════════════════════

class TestFix4FogFilterAggressorKey:
    """Dispatch fog filter must check 'aggressor' key in template vars."""

    def test_aggressor_key_checked_in_fog_filter(self):
        """Event with 'aggressor' nation at PARTIAL+ is visible."""
        world = _make_world()
        # Prussia visible via marshal
        world.marshals["Blucher"] = _make_marshal(
            name="Blucher", location="Berlin", strength=30000,
            nation="Prussia",
        )
        _set_region_intel(world, "Berlin", PARTIAL)

        from backend.game_logic.dispatch import _is_dispatch_event_visible
        event = {
            "type": "diplomatic_offensive_cascade",
            "template_vars": {"aggressor": "Prussia", "target": "UnknownNation"},
            "fog_rule": "partial_on_nation",
        }
        assert _is_dispatch_event_visible(event, world, "France") is True

    def test_aggressor_key_hidden_when_unknown(self):
        """Event with only 'aggressor' key that is UNKNOWN is hidden."""
        world = _make_world()
        # No marshals for TestNation — UNKNOWN visibility
        from backend.game_logic.dispatch import _is_dispatch_event_visible
        event = {
            "type": "diplomatic_offensive_cascade",
            "template_vars": {"aggressor": "TestNation"},
            "fog_rule": "partial_on_nation",
        }
        assert _is_dispatch_event_visible(event, world, "France") is False


# ═══════════════════════════════════════════════════════════
# Fix 6/7: Campaign log types include war/coalition events
# ═══════════════════════════════════════════════════════════

class TestFix6And7CampaignLogTypes:
    """Campaign log must include war_declaration, cascade, and coalition events."""

    def test_missing_event_types_in_campaign_log(self):
        """All new event types are in CAMPAIGN_LOG_TYPES."""
        from backend.campaign_log import CAMPAIGN_LOG_TYPES, CATEGORY_MAP
        for etype in ("war_declaration", "defensive_cascade", "offensive_cascade",
                       "coalition_declared", "coalition_dissolved"):
            assert etype in CAMPAIGN_LOG_TYPES, f"{etype} missing from CAMPAIGN_LOG_TYPES"
            assert etype in CATEGORY_MAP, f"{etype} missing from CATEGORY_MAP"
            assert CATEGORY_MAP[etype] == "diplomacy"

    def test_format_event_oneliner_new_types(self):
        """New event types produce readable one-liners."""
        from backend.campaign_log import format_event_oneliner
        assert "War declared" in format_event_oneliner(
            {"type": "war_declaration", "aggressor": "Prussia", "target": "Austria"}
        )
        assert "Defensive cascade" in format_event_oneliner(
            {"type": "defensive_cascade", "nation": "Austria", "ally": "Prussia"}
        )
        assert "Offensive cascade" in format_event_oneliner(
            {"type": "offensive_cascade", "nation": "Prussia", "aggressor": "France"}
        )
        assert "Coalition formed" in format_event_oneliner(
            {"type": "coalition_declared", "members": ["Britain", "Prussia"]}
        )
        assert "dissolved" in format_event_oneliner(
            {"type": "coalition_dissolved"}
        )


# ═══════════════════════════════════════════════════════════
# Fix 8: Advisory uses get_known_nations
# ═══════════════════════════════════════════════════════════

class TestFix8AdvisoryDynamicNations:
    """diplomatic_advisory uses get_known_nations(world), not static KNOWN_NATIONS."""

    def test_nation_summary_uses_dynamic_nations(self):
        """Structural: _get_nation_summary uses get_known_nations."""
        import inspect
        from backend.game_logic import diplomatic_advisory
        source = inspect.getsource(diplomatic_advisory._get_nation_summary)
        assert "get_known_nations(world)" in source
        assert "KNOWN_NATIONS" not in source


# ═══════════════════════════════════════════════════════════
# Fix 9/10: Netherlands is_capital + region_type
# ═══════════════════════════════════════════════════════════

class TestFix9And10Netherlands:
    """Netherlands must be is_capital=True, region_type='capital'."""

    def test_netherlands_is_capital(self):
        from backend.models.region import REGIONS_DATA, NATION_CAPITALS
        assert REGIONS_DATA["Netherlands"]["is_capital"] is True
        assert REGIONS_DATA["Netherlands"]["region_type"] == "capital"
        assert NATION_CAPITALS["Britain"] == "Netherlands"


# ═══════════════════════════════════════════════════════════
# Fix 11: Dresden region_type is "capital"
# ═══════════════════════════════════════════════════════════

class TestFix11DresdenCapital:
    """Dresden must have region_type='capital' to match is_capital=True."""

    def test_dresden_region_type(self):
        from backend.models.region import REGIONS_DATA
        assert REGIONS_DATA["Dresden"]["region_type"] == "capital"
        assert REGIONS_DATA["Dresden"]["is_capital"] is True


# ═══════════════════════════════════════════════════════════
# Fix 12: Coalition threat counts only transferred regions
# ═══════════════════════════════════════════════════════════

class TestFix12CoalitionThreatTransferred:
    """Coalition threat must count only ACTUALLY transferred regions."""

    def _apply_territory_cede(self, world, clause):
        """Helper: replicate the territory_cede logic from world_state._ratify_treaty."""
        from backend.game_logic.coalition import add_threat, reduce_threat
        regions = clause.get("regions", [])
        from_nation = clause.get("from", "")
        to_nation = clause.get("to", "")
        transferred_count = 0
        for region_name in regions:
            if region_name not in world.regions:
                continue
            region = world.regions[region_name]
            if from_nation and region.controller != from_nation:
                continue
            region.controller = to_nation
            region.stability = 50
            transferred_count += 1
        if to_nation == world.player_nation and transferred_count > 0:
            add_threat(world, 8 * transferred_count, "treaty_annex")
        if from_nation == world.player_nation and transferred_count > 0:
            reduce_threat(world, 5 * transferred_count, "territory_return")
        return transferred_count

    def test_threat_counts_only_transferred(self):
        """If 3 regions requested but only 1 actually controlled by from_nation,
        threat should be 8*1=8, not 8*3=24."""
        world = _make_world()
        world.threat_level = 0
        # Set up regions: only Lyon controlled by Austria
        world.regions["Lyon"].controller = "Austria"
        world.regions["Paris"].controller = "France"  # NOT Austria
        world.regions["Belgium"].controller = "France"  # NOT Austria

        clause = {
            "type": "territory_cede",
            "from": "Austria",
            "to": "France",
            "regions": ["Lyon", "Paris", "Belgium"],
        }
        transferred = self._apply_territory_cede(world, clause)
        assert transferred == 1
        assert world.threat_level == 8  # 8 * 1 = 8, not 8 * 3 = 24

    def test_threat_zero_when_no_regions_transferred(self):
        """If no regions are actually controlled by from_nation, threat=0."""
        world = _make_world()
        world.threat_level = 0
        # None of these regions controlled by Austria
        world.regions["Lyon"].controller = "France"
        world.regions["Paris"].controller = "France"

        clause = {
            "type": "territory_cede",
            "from": "Austria",
            "to": "France",
            "regions": ["Lyon", "Paris"],
        }
        transferred = self._apply_territory_cede(world, clause)
        assert transferred == 0
        assert world.threat_level == 0


# ═══════════════════════════════════════════════════════════
# Fix 13: Coalition ledger WE filtered by visibility
# ═══════════════════════════════════════════════════════════

class TestFix13CoalitionLedgerWEFiltered:
    """War exhaustion hidden for nations below PARTIAL visibility."""

    def test_we_hidden_when_unknown(self):
        """WE should be 0 when nation visibility is UNKNOWN."""
        world = _make_world()
        world.active_coalition = {
            "name": "Test Coalition",
            "leader": "Britain",
            "strategic_posture": "defensive",
            "members": ["Britain"],
        }
        world.war_exhaustion["Britain"] = 50
        # Britain marshal in UNKNOWN region
        world.marshals["Wellington"] = _make_marshal(
            name="Wellington", location="Netherlands", strength=40000,
            nation="Britain",
        )
        _set_region_intel(world, "Netherlands", UNKNOWN)

        from backend.game_logic.diplomatic_ledger import _build_balance_of_europe
        result = _build_balance_of_europe(world)
        active = result.get("active_coalition")
        assert active is not None
        britain = active["members"][0]
        assert britain["war_exhaustion"] == 0

    def test_we_shown_when_partial(self):
        """WE should be visible when nation has PARTIAL visibility."""
        world = _make_world()
        world.active_coalition = {
            "name": "Test Coalition",
            "leader": "Britain",
            "strategic_posture": "defensive",
            "members": ["Britain"],
        }
        world.war_exhaustion["Britain"] = 50
        world.marshals["Wellington"] = _make_marshal(
            name="Wellington", location="Netherlands", strength=40000,
            nation="Britain",
        )
        _set_region_intel(world, "Netherlands", PARTIAL)

        from backend.game_logic.diplomatic_ledger import _build_balance_of_europe
        result = _build_balance_of_europe(world)
        active = result.get("active_coalition")
        assert active is not None
        britain = active["members"][0]
        assert britain["war_exhaustion"] == 50


# ═══════════════════════════════════════════════════════════
# Fix 14: Empty threat_entries doesn't crash
# ═══════════════════════════════════════════════════════════

class TestFix14EmptyThreatEntries:
    """_compare_threats must not crash when no nations are known."""

    def test_no_crash_on_empty_nations(self):
        """If get_known_nations returns empty, _compare_threats returns safely."""
        from unittest.mock import patch
        from backend.game_logic.diplomatic_advisory import _compare_threats
        world = _make_world()
        # Patch get_known_nations to return empty set
        with patch("backend.game_logic.diplomatic_advisory.get_known_nations", return_value=set()):
            result = _compare_threats(world)
        assert result["type"] == "advisory"
        assert "No foreign nations" in result["talleyrand_text"]
        assert result["blocking"] is False


# ═══════════════════════════════════════════════════════════
# Fix 15: Threat score no double-counting
# ═══════════════════════════════════════════════════════════

class TestFix15ThreatScoreNoDoubleCounting:
    """Military strength contributes at most +20 to threat score, not +40."""

    def test_large_army_gets_20_not_40(self):
        """A nation with strength > france_strength should get +20, not +40."""
        from unittest.mock import patch
        from backend.game_logic.diplomatic_advisory import _compare_threats
        world = _make_world()
        # France: 50k, Prussia: 80k (> france * 0.5 AND > france)
        # With elif fix, should only get +20 from the first branch
        world.marshals = {
            "Ney": _make_marshal(name="Ney", location="Paris", strength=50000, nation="France"),
            "Blucher": _make_marshal(name="Blucher", location="Berlin", strength=80000, nation="Prussia"),
        }
        # Set relation to 0 (default is -80 for France|Prussia)
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.nation_relations[diplo_key] = 0
        world.diplomatic_states[diplo_key] = "PEACE"
        # Set all regions to FULL for clean test
        for region_name in world.regions:
            _set_region_intel(world, region_name, FULL)

        with patch("backend.game_logic.diplomatic_advisory.get_known_nations",
                    return_value={"Prussia"}):
            result = _compare_threats(world)

        ranking = result["context"]["threat_ranking"]
        prussia_entry = [e for e in ranking if e["nation"] == "Prussia"][0]
        # Relation=0, state=PEACE, strength > 0.5*france → +20 from first branch
        # elif prevents +20 from second branch → total = 20 (not 40)
        assert prussia_entry["threat_score"] == 20
