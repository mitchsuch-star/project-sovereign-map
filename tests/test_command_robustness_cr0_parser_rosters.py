"""
CR-0 behavior tests — parser rosters derive from the LIVE world.

COMMAND_ROBUSTNESS_SPEC.md slice CR-0 (P0 defect, BUG_FIXES.md July 2, 2026):
on the shipped 1805 boot, 5 of 7 French marshals (Soult, Lannes, Murat,
Bernadotte, Massena) could not be commanded by typed text because
parser.valid_marshals / known_regions and the mock parser's marshal + target
extraction were hardcoded to the retired 4-marshal / 19-region legacy world.

Contract under test (both worlds + cold fallback):
  1. Live player-marshal roster: every French 1805 marshal is commandable.
  2. Live region roster: 126-province names parse + fuzzy-correct.
  3. Mock target ladder: live enemies/regions extracted from game_state,
     incl. camelCase alias forms ("archduke charles" -> ArchdukeCharles).
  4. Exact enemy names are never fuzzy-rewritten into regions
     ("Mack" must not become "La Mancha").
  5. Cold parses (no world/game_state) keep the EXACT legacy fallback
     behavior (~490 existing tests depend on it).
  6. Nation-keyed vassal keyword forms work with live nations
     ("invest in bavaria") — and the legacy forms now work at all
     (the marshal word-scan previously choked on "invest"/"release").
  7. Legacy world with world= passed behaves as before.
"""

from pathlib import Path

import pytest

from backend.commands.parser import CommandParser
from backend.models.world_state import WorldState

SCENARIO_PATH = (
    Path(__file__).resolve().parents[1]
    / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
)


# ═══════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════

@pytest.fixture(scope="module")
def world1805():
    """Read-only module world — the shipped 126-province 1805 campaign."""
    return WorldState.from_scenario(str(SCENARIO_PATH))


@pytest.fixture(scope="module")
def legacy_world():
    """Read-only legacy 19-region fixture world (Ney/Davout/Grouchy/Drouot)."""
    return WorldState(player_nation="France")


@pytest.fixture(scope="module")
def parser():
    return CommandParser(use_real_llm=False)


def _llm_game_state(world):
    """Mirrors backend.main.get_llm_game_state() (main.py:148) EXACTLY,
    including the R5/V2-5 fog filter on enemies — tests run against the
    production-shaped payload (fogged enemies are absent from the dict and
    must be rescued by parser.py's world-side pass)."""
    from backend.models.intel import FULL, PARTIAL, VISIBILITY_PRIORITY
    marshals = {
        m.name: {"location": m.location, "strength": int(m.strength),
                 "morale": int(m.morale)}
        for m in world.get_player_marshals() if m.strength > 0
    }
    enemies = {}
    for m in world.get_enemy_marshals():
        if m.strength > 0:
            vis = world.get_region_intel(m.location).visibility
            if VISIBILITY_PRIORITY.get(vis, 0) >= VISIBILITY_PRIORITY[PARTIAL]:
                enemies[m.name] = {
                    "location": m.location,
                    "strength": int(m.strength) if vis == FULL else "unknown",
                    "nation": m.nation,
                }
    map_data = {
        name: {"controller": r.controller or "Neutral", "marshals": []}
        for name, r in world.regions.items()
    }
    return {"turn": int(world.current_turn), "gold": int(world.gold),
            "marshals": marshals, "enemies": enemies, "map_data": map_data}


@pytest.fixture(scope="module")
def gs1805(world1805):
    return _llm_game_state(world1805)


@pytest.fixture(scope="module")
def gs_legacy(legacy_world):
    return _llm_game_state(legacy_world)


# ═══════════════════════════════════════════════════════════════════
# 1. The P0: all seven 1805 French marshals are commandable
# ═══════════════════════════════════════════════════════════════════

FRENCH_1805 = ["Ney", "Davout", "Soult", "Lannes", "Murat", "Bernadotte", "Massena"]
BROKEN_FIVE = ["Soult", "Lannes", "Murat", "Bernadotte", "Massena"]


class Test1805MarshalRoster:

    @pytest.mark.parametrize("marshal", FRENCH_1805)
    def test_every_french_marshal_parses(self, parser, world1805, gs1805, marshal):
        result = parser.parse(f"{marshal}, defend", gs1805, world=world1805)
        assert result["success"], f"'{marshal}, defend' failed: {result.get('error')}"
        assert result["command"]["marshal"] == marshal
        assert result["command"]["action"] == "defend"

    def test_soult_attack_mack(self, parser, world1805, gs1805):
        """The exact probe command from BUG_FIXES.md."""
        result = parser.parse("Soult, attack Mack", gs1805, world=world1805)
        assert result["success"], result.get("error")
        assert result["command"]["marshal"] == "Soult"
        assert result["command"]["action"] == "attack"
        assert result["command"]["target"] == "Mack"

    def test_marshal_title_form(self, parser, world1805, gs1805):
        """'Marshal Soult' (capital M) — the old regex was case-sensitive
        on 'marshal' and never matched the standard typed form."""
        result = parser.parse("Marshal Soult, attack Mack", gs1805, world=world1805)
        assert result["success"], result.get("error")
        assert result["command"]["marshal"] == "Soult"

    def test_lannes_move_to_swabia(self, parser, world1805, gs1805):
        result = parser.parse("Lannes, move to Swabia", gs1805, world=world1805)
        assert result["success"], result.get("error")
        assert result["command"]["marshal"] == "Lannes"
        assert result["command"]["target"] == "Swabia"

    def test_massena_hold_milan(self, parser, world1805, gs1805):
        result = parser.parse("Massena, hold Milan", gs1805, world=world1805)
        assert result["success"], result.get("error")
        assert result["command"]["marshal"] == "Massena"
        assert result["command"]["target"] == "Milan"

    def test_marshal_typo_autocorrects_to_1805_name(self, parser, world1805, gs1805):
        """Fuzzy matching runs against the LIVE roster."""
        result = parser.parse("Soutl, attack Mack", gs1805, world=world1805)
        if result["success"]:
            assert result["command"]["marshal"] == "Soult"
        else:
            # A suggest-level match is acceptable — but it must suggest the
            # live 1805 name, not the legacy roster.
            assert "Soult" in (result.get("error") or "") + (result.get("suggestion") or "")

    def test_error_suggestions_list_live_roster(self, parser, world1805, gs1805):
        """A genuinely unknown marshal errors with 1805 names, not
        'Davout, Drouot, Grouchy' (the shipped-boot failure mode)."""
        result = parser.parse("Wittgenstein, attack Mack", gs1805, world=world1805)
        assert not result["success"]
        text = (result.get("error") or "") + " " + (result.get("suggestion") or "")
        assert "Grouchy" not in text and "Drouot" not in text
        assert any(name in text for name in BROKEN_FIVE + ["Ney", "Davout"])


# ═══════════════════════════════════════════════════════════════════
# 2. Live regions: parse + fuzzy-correct 126-province names
# ═══════════════════════════════════════════════════════════════════

class Test1805Regions:

    def test_europe_region_parses_as_target(self, parser, world1805, gs1805):
        result = parser.parse("Ney, scout Franconia", gs1805, world=world1805)
        assert result["success"], result.get("error")
        assert result["command"]["target"] == "Franconia"

    def test_europe_region_typo_corrects(self, parser, world1805, gs1805):
        result = parser.parse("Ney, move to Swabbia", gs1805, world=world1805)
        assert result["success"], result.get("error")
        assert result["command"]["target"] == "Swabia"

    def test_strategic_order_to_europe_region(self, parser, world1805, gs1805):
        result = parser.parse("Ney, march to Vienna", gs1805, world=world1805)
        assert result["success"], result.get("error")
        assert result.get("is_strategic") is True
        assert result["command"]["target"] == "Vienna"


# ═══════════════════════════════════════════════════════════════════
# 3. Mock target ladder derives from game_state
# ═══════════════════════════════════════════════════════════════════

class TestMockTargetLadder:

    def test_live_enemy_extracted(self, parser, world1805, gs1805):
        """Marshal-less command: 'attack Mack' auto-assigns with the live
        enemy as target (previously target=None on 1805)."""
        result = parser.parse("attack Mack", gs1805, world=world1805)
        assert result["success"], result.get("error")
        assert result["command"]["marshal"] is None
        assert result["command"]["target"] == "Mack"
        assert result["command"]["type"] == "auto_assign_attack"

    def test_camelcase_enemy_alias(self, parser, world1805, gs1805):
        """'archduke john' (typed with a space) finds the camelCase
        scenario key ArchdukeJohn via the fog-visible enemies dict."""
        result = parser.parse("attack archduke john", gs1805, world=world1805)
        assert result["success"], result.get("error")
        assert result["command"]["target"] == "ArchdukeJohn"

    def test_fogged_enemy_rescued_by_world_pass(self, parser, world1805, gs1805):
        """ArchdukeCharles is FOGGED at boot (absent from the R5-filtered
        enemies dict) — the parse must still resolve him through the
        legacy alias ladder + parser.py's omniscient world-side pass."""
        assert "ArchdukeCharles" not in gs1805["enemies"]
        result = parser.parse("attack archduke charles", gs1805, world=world1805)
        assert result["success"], result.get("error")
        assert result["command"]["target"] == "ArchdukeCharles"

    def test_bare_command_europe_region(self, parser, world1805, gs1805):
        """The ORIGINAL BUG_FIXES entry: bare 'scout <Europe region>' fell
        to Berthier recovery instead of auto_assign_scout."""
        result = parser.parse("scout Franconia", gs1805, world=world1805)
        assert result["success"], result.get("error")
        assert result["command"]["type"] == "auto_assign_scout"
        assert result["command"]["target"] == "Franconia"

    def test_exact_enemy_not_rewritten_to_region(self, parser, world1805, gs1805):
        """Fuzzy region correction must not clobber an exact enemy name
        ('Mack' fuzzy-matched to 'La Mancha' before the CR-0 fix)."""
        result = parser.parse("Davout, attack Mack", gs1805, world=world1805)
        assert result["success"], result.get("error")
        assert result["command"]["target"] == "Mack"

    def test_marshal_name_punctuation_not_fuzzy_drifted(self, parser, world1805, gs1805):
        """'Bernadotte,' (with comma) must not fuzzy-drift into region
        'Bern' during target extraction."""
        result = parser.parse("Bernadotte, defend", gs1805, world=world1805)
        assert result["success"], result.get("error")
        assert result["command"]["marshal"] == "Bernadotte"
        assert result["command"]["target"] is None


# ═══════════════════════════════════════════════════════════════════
# 4. Nation-keyed vassal keyword forms
# ═══════════════════════════════════════════════════════════════════

class TestVassalNationKeywords:

    def test_invest_in_live_nation(self, parser, world1805, gs1805):
        result = parser.parse("invest in bavaria", gs1805, world=world1805)
        assert result["success"], result.get("error")
        assert result["command"]["action"] == "invest_vassal"

    def test_release_live_nation(self, parser, world1805, gs1805):
        result = parser.parse("release naples", gs1805, world=world1805)
        assert result["success"], result.get("error")
        assert result["command"]["action"] == "release_vassal"

    def test_legacy_invest_form_now_parses(self, parser):
        """Pre-existing bug (probe-verified on unmodified code): the marshal
        word-scan choked on 'invest' before P8-1's nation keywords could
        matter. Cold parse must now succeed."""
        result = parser.parse("invest in saxony")
        assert result["success"], result.get("error")
        assert result["command"]["action"] == "invest_vassal"

    def test_legacy_release_form_now_parses(self, parser):
        result = parser.parse("release saxony")
        assert result["success"], result.get("error")
        assert result["command"]["action"] == "release_vassal"


# ═══════════════════════════════════════════════════════════════════
# 5. Cold-parse fallback: EXACT legacy behavior preserved
# ═══════════════════════════════════════════════════════════════════

class TestColdParseFallback:

    def test_fallback_seed_is_legacy_roster(self, parser):
        assert sorted(parser.valid_marshals) == ["Davout", "Drouot", "Grouchy", "Ney"]

    def test_legacy_command_parses_cold(self, parser):
        result = parser.parse("Ney, attack Wellington")
        assert result["success"], result.get("error")
        assert result["command"]["marshal"] == "Ney"
        assert result["command"]["target"] == "Wellington"

    def test_1805_marshal_rejected_cold(self, parser):
        """Without a live world the 1805 names must NOT resolve — cold
        parses keep the legacy fallback (mirrors TestParserMarshalList)."""
        result = parser.parse("Murat, attack Wellington")
        assert not result["success"]

    def test_mock_parser_cold_keeps_legacy_marshals(self):
        from backend.ai.llm_client import LLMClient
        client = LLMClient(use_real_api=False)
        result = client.parse_command("Ney, attack Wellington")
        assert result.get("marshal") == "Ney"
        result = client.parse_command("Soult, attack Wellington")
        assert result.get("marshal") != "Soult"


# ═══════════════════════════════════════════════════════════════════
# 6. Legacy world with world= passed: unchanged behavior
# ═══════════════════════════════════════════════════════════════════

class TestLegacyWorldUnchanged:

    def test_legacy_full_parse(self, parser, legacy_world, gs_legacy):
        result = parser.parse("Ney, attack Wellington", gs_legacy, world=legacy_world)
        assert result["success"], result.get("error")
        assert result["command"]["marshal"] == "Ney"
        assert result["command"]["target"] == "Wellington"

    def test_legacy_region_typo_still_corrects(self, parser, legacy_world, gs_legacy):
        result = parser.parse("Ney, move to bordeuex", gs_legacy, world=legacy_world)
        assert result["success"], result.get("error")
        assert result["command"]["target"] == "Bordeaux"

    def test_1805_marshal_rejected_on_legacy_world(self, parser, legacy_world, gs_legacy):
        """Murat exists only in the 1805 roster — on the legacy world he
        must still be rejected, with legacy suggestions."""
        result = parser.parse("Murat, attack Wellington", gs_legacy, world=legacy_world)
        assert not result["success"]

    def test_live_roster_derivation_legacy(self, parser, legacy_world):
        names = parser._get_player_marshals(legacy_world)
        assert sorted(names) == ["Davout", "Drouot", "Grouchy", "Ney"]

    def test_live_roster_derivation_1805(self, parser, world1805):
        names = parser._get_player_marshals(world1805)
        assert sorted(names) == sorted(FRENCH_1805)

    def test_live_region_derivation_1805(self, parser, world1805):
        names = parser._get_known_regions(world1805)
        assert len(names) == 126
        assert "Swabia" in names and "Franconia" in names


# ═══════════════════════════════════════════════════════════════════
# 7. Strategic nationality classification (live demonyms)
# ═══════════════════════════════════════════════════════════════════

class TestStrategicNationalities:

    def test_pursue_the_austrians_is_generic(self, world1805):
        """'pursue the austrians' must classify as a generic target, not
        title-case into a fake region 'The Austrians'."""
        from backend.ai.strategic_parser import detect_strategic_command
        result = detect_strategic_command(
            "Lannes, pursue the austrians", "Lannes", world1805)
        assert result is not None
        assert result.get("target_type") == "generic"

    def test_legacy_nationality_literals_survive(self, legacy_world):
        from backend.ai.strategic_parser import detect_strategic_command
        result = detect_strategic_command(
            "Ney, pursue the prussians", "Ney", legacy_world)
        assert result is not None
        assert result.get("target_type") == "generic"

    def test_march_to_saxony_is_not_generic(self, world1805):
        """Adversarial-review regression: 'saxon' (Saxony's demonym) must
        NOT substring-fire inside the place name 'Saxony' — 'march to
        Saxony' is a region-shaped order (it may fail at execution since
        Saxony has no same-named province), never a silent generic
        redirect to the nearest enemy."""
        from backend.ai.strategic_parser import detect_strategic_command
        result = detect_strategic_command(
            "Ney, march to Saxony", "Ney", world1805)
        assert result is not None
        assert result.get("target_type") != "generic"

    def test_demonym_overrides_cover_irregular_live_nations(self, world1805):
        """Holland/Hesse/PapalStates/KingdomOfItaly derive real demonyms
        (the default -n/-ian rule mangles them)."""
        from backend.ai.strategic_parser import _nation_demonyms
        forms = set(_nation_demonyms(world1805))
        assert "dutch" in forms
        assert "hessian" in forms
        assert "papal" in forms
        assert "italian" in forms
        # And the regular rule still yields the majors
        assert "austrians" in forms and "russians" in forms


# ═══════════════════════════════════════════════════════════════════
# 8. Adversarial-review regressions (July 3, 2026 verify pass)
# ═══════════════════════════════════════════════════════════════════

class TestMarshalHonorificGuard:
    """The case-tolerant '[Mm]arshal <Name>' regex must never capture an
    ENEMY commander as the executing marshal."""

    def test_attack_marshal_mack_targets_mack(self, parser, world1805, gs1805):
        result = parser.parse("Attack Marshal Mack", gs1805, world=world1805)
        assert result["success"], result.get("error")
        assert result["command"]["marshal"] is None
        assert result["command"]["target"] == "Mack"
        assert result["command"]["type"] == "auto_assign_attack"

    def test_cold_attack_marshal_blucher(self, parser):
        """Cold-parse invariant: 'Attack Marshal Blucher' resolves Blucher
        as the target via the legacy enemy fallback set."""
        result = parser.parse("Attack Marshal Blucher")
        assert result["success"], result.get("error")
        assert result["command"]["marshal"] is None
        assert result["command"]["target"] == "Blucher"

    def test_player_honorific_still_binds(self, parser, world1805, gs1805):
        result = parser.parse("Marshal Bernadotte, hold", gs1805, world=world1805)
        assert result["success"], result.get("error")
        assert result["command"]["marshal"] == "Bernadotte"


class TestPunctuatedTargets:
    """Punctuation must be stripped BEFORE the existing-target/known-name
    skip checks — punctuated targets were falling into marshal fuzzy."""

    @pytest.mark.parametrize("cmd", ["Attack Mack!", "Attack Mack."])
    def test_punctuated_enemy_target(self, parser, world1805, gs1805, cmd):
        result = parser.parse(cmd, gs1805, world=world1805)
        assert result["success"], result.get("error")
        assert result["command"]["target"] == "Mack"

    def test_hold_bern_does_not_hijack_bernadotte(self, parser, world1805, gs1805):
        """'Bern' scores partial_ratio 100 against 'Bernadotte' — the
        known-region guard must keep it a target, not an executing
        marshal."""
        result = parser.parse("Hold Bern!", gs1805, world=world1805)
        assert result["success"], result.get("error")
        assert result["command"]["marshal"] is None
        assert result["command"]["target"] == "Bern"

    def test_trailing_clause_does_not_hijack(self, parser, world1805, gs1805):
        """The pre-fix defect was a SILENT parse success executing under
        marshal=Bernadotte. A clarification-style failure on the unknown
        word 'then' is acceptable (unknown-word handling is CR-2 scope);
        silently hijacking Bernadotte is not."""
        result = parser.parse("attack Bern, then hold your positions",
                              gs1805, world=world1805)
        if result["success"]:
            assert result["command"]["marshal"] is None
            assert result["command"]["target"] == "Bern"


class TestPositionAwareTargets:
    """_match_known_name must be position-aware ('to X' wins, then the
    earliest match) — not longest-name-wins."""

    def test_move_to_paris_via_champagne(self, parser, world1805, gs1805):
        result = parser.parse("Ney, move to Paris via Champagne",
                              gs1805, world=world1805)
        assert result["success"], result.get("error")
        assert result["command"]["target"] == "Paris"

    def test_move_from_burgundy_to_paris(self, parser, world1805, gs1805):
        result = parser.parse("Ney, move from Burgundy to Paris",
                              gs1805, world=world1805)
        assert result["success"], result.get("error")
        assert result["command"]["target"] == "Paris"


class TestEnemyTypoPrecedence:
    """Enemy AUTO-correct must beat region auto-correct: an edit-distance-1
    typo of an enemy name must not become a far-away region."""

    def test_mach_corrects_to_mack_not_la_mancha(self, parser, world1805, gs1805):
        result = parser.parse("Davout, attack Mach", gs1805, world=world1805)
        assert result["success"], result.get("error")
        assert result["command"]["target"] == "Mack"

    def test_legacy_region_typo_precedence_unchanged(self, parser, legacy_world, gs_legacy):
        """'bordeuex' still region-corrects (no enemy is close)."""
        result = parser.parse("Ney, move to bordeuex", gs_legacy, world=legacy_world)
        assert result["success"], result.get("error")
        assert result["command"]["target"] == "Bordeaux"


class TestMultiwordRegionTargets:
    """Words of an already-extracted multiword target must be skipped
    individually by the marshal word-scan."""

    def test_attack_east_prussia(self, parser, world1805, gs1805):
        result = parser.parse("attack East Prussia", gs1805, world=world1805)
        assert result["success"], result.get("error")
        assert result["command"]["marshal"] is None
        assert result["command"]["target"] == "East Prussia"

    def test_scout_white_russia(self, parser, world1805, gs1805):
        result = parser.parse("scout White Russia", gs1805, world=world1805)
        assert result["success"], result.get("error")
        assert result["command"]["target"] == "White Russia"

    def test_hyphenated_region_parses(self, parser, world1805, gs1805):
        result = parser.parse("Lannes, move to Franche-Comte",
                              gs1805, world=world1805)
        assert result["success"], result.get("error")
        assert result["command"]["target"] == "Franche-Comte"

    def test_hyphenated_region_spaced_form(self, parser, world1805, gs1805):
        """Typed without the hyphen: 'franche comte' still finds the
        canonical hyphenated key."""
        result = parser.parse("Lannes, move to franche comte",
                              gs1805, world=world1805)
        assert result["success"], result.get("error")
        assert result["command"]["target"] == "Franche-Comte"


class TestVassalNationTargets:
    """Nation-keyed vassal commands must carry the NATION as target —
    never fuzzy-drift into a region ('Austria' → 'Asturias')."""

    def test_invest_in_austria_targets_austria(self, parser, world1805, gs1805):
        result = parser.parse("invest in austria", gs1805, world=world1805)
        assert result["success"], result.get("error")
        assert result["command"]["action"] == "invest_vassal"
        assert result["command"]["target"] == "Austria"

    def test_release_naples_targets_naples(self, parser, world1805, gs1805):
        result = parser.parse("release naples", gs1805, world=world1805)
        assert result["success"], result.get("error")
        assert result["command"]["action"] == "release_vassal"
        assert result["command"]["target"] == "Naples"

    def test_camelcase_nation_spaced_form(self, parser, world1805, gs1805):
        """'papal states' (typed with a space) resolves the camelCase
        nation key PapalStates."""
        result = parser.parse("invest in papal states", gs1805, world=world1805)
        assert result["success"], result.get("error")
        assert result["command"]["action"] == "invest_vassal"
        assert result["command"]["target"] == "PapalStates"

    def test_cold_invest_in_saxony_keeps_target(self, parser):
        """Legacy cold parse: Saxony (region name == nation name) still
        arrives as the target via the word-scan."""
        result = parser.parse("invest in saxony")
        assert result["success"], result.get("error")
        assert result["command"]["action"] == "invest_vassal"
        assert result["command"]["target"] == "Saxony"


class TestGameStateShapeHardening:
    """Non-canonical game_state shapes must never crash the parser."""

    @pytest.mark.parametrize("weird_gs", [
        {"enemies": ["Wellington"], "map_data": {}},
        {"enemies": {"Wellington": "Brussels"}, "map_data": {}},
        {"marshals": ["Ney"], "enemies": None, "map_data": "oops"},
        {"world": object()},
    ])
    def test_weird_game_state_shapes_do_not_crash(self, parser, weird_gs):
        result = parser.parse("Ney, attack Wellington", weird_gs)
        assert result["success"], result.get("error")
        assert result["command"]["marshal"] == "Ney"

    def test_game_state_without_world_uses_same_roster(self, parser, gs1805):
        """A parse with the LLM game_state but NO world must validate
        against the same roster the mock extracted from — 'Soult' must
        not be rejected against the legacy fallback."""
        result = parser.parse("Soult, attack Mack", gs1805, world=None)
        assert result["success"], result.get("error")
        assert result["command"]["marshal"] == "Soult"


class TestMultiMarshalAndStrategicRosters:
    """parse_multiple and the strategic marshal-target fuzzy path use the
    live rosters."""

    def test_parse_multiple_1805_names(self, parser, world1805, gs1805):
        results = parser.parse_multiple("Soult and Lannes, attack Mack",
                                        gs1805, world=world1805)
        assert len(results) == 2
        marshals = {r["command"]["marshal"] for r in results if r["success"]}
        assert marshals == {"Soult", "Lannes"}

    def test_strategic_pursue_1805_enemy(self, parser, world1805, gs1805):
        result = parser.parse("Soult, pursue Kutuzov", gs1805, world=world1805)
        assert result["success"], result.get("error")
        assert result.get("is_strategic") is True
        assert result.get("strategic_type") == "PURSUE"
        assert result["command"]["target"] == "Kutuzov"
