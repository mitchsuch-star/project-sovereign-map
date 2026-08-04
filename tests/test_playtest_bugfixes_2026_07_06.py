"""Regression tests for the July 6 2026 playtest bug audit.

Covers the fixes landed after a France/1805 play session + multi-agent code
audit. Each test maps to a finding id (F1a, F1b, ...) from the after-action
report. Integration-heavy fixes (economy net, proposal cap, ZoC block) are
exercised where a light fixture suffices; the rest are pinned at the unit seam.
"""

from backend.commands.combat_executor import CombatExecutor
from backend.commands.strategic import _carry_combat_fields, _COMBAT_PASSTHROUGH_FIELDS
from backend.campaign_log import format_event_oneliner
from backend.ai.llm_client import LLMClient
from backend.ai.strategic_parser import _classify_target, _clean_target_text
from backend.commands.meta_executor import _filter_tactical_events_by_fog


# ── F1a: the coordinated casualty line names the ARMY, not the man ──
#
# CONSCIOUSLY FLIPPED by CA8-1 (creative audit, Aug 4 2026). F1a originally
# rewrote the corps total DOWN to the primary's distributed share; that made
# the terminal disagree with the campaign log by up to 15x on every
# coordinated battle (`Ney 13` vs `197`). F1a's real finding — that the whole
# corps' losses must not be attributed to one man personally — is preserved
# by naming the army instead. See _rewrite_primary_casualties' docstring.

class TestF1aPrimaryCasualties:
    def test_tactical_line_attributes_corps_total_to_the_army(self):
        desc = ("Ney holds the line. Casualties: Ney 8,141, Mack 3,431. "
                "Both armies remain in the field.")
        out = CombatExecutor._rewrite_primary_casualties(
            desc, "Ney", 8141, 2171, "Mack", 3431, 3431)
        # The figure is the whole-army total the campaign log prints...
        assert "Ney's army 8,141" in out
        # ...and it is no longer claimed as one man's personal loss.
        assert "Casualties: Ney 8,141" not in out
        # defender fielded one corps (raw == share) — Mack line intact
        assert "Mack 3,431" in out
        assert "Mack's army" not in out

    def test_decisive_victory_suffered_template_attributed_to_the_army(self):
        desc = ("Ney decisively defeats Mack! Mack's army is destroyed. "
                "Ney suffered 8,141 casualties.")
        out = CombatExecutor._rewrite_primary_casualties(
            desc, "Ney", 8141, 2171, "Mack", 0, 0)
        assert "Ney's army suffered 8,141 casualties" in out
        assert "Ney suffered 8,141" not in out

    def test_solo_battle_unchanged(self):
        # raw == share for both sides → description untouched
        desc = "Casualties: Massena 3,405, ArchdukeJohn 3,462."
        out = CombatExecutor._rewrite_primary_casualties(
            desc, "Massena", 3405, 3405, "ArchdukeJohn", 3462, 3462)
        assert out == desc


# ── F1b: strategic "attack anyway" path carries combat extras ──

class TestF1bCarryCombatFields:
    def test_reinforcement_messages_carried(self):
        inner = {
            "reinforcement_messages": ["Davout's forces arrived to reinforce Ney!"],
            "battle_report": {"x": 1},
            "message": "inner",
            "not_allowlisted": "drop me",
        }
        out = _carry_combat_fields({"message": "outer"}, inner)
        assert out["reinforcement_messages"] == inner["reinforcement_messages"]
        assert out["battle_report"] == {"x": 1}
        assert out["message"] == "outer"          # not overwritten
        assert "not_allowlisted" not in out

    def test_missing_fields_are_noop(self):
        out = _carry_combat_fields({"message": "m"}, {"message": "x"})
        assert out == {"message": "m"}

    def test_reinforcement_messages_is_allowlisted(self):
        assert "reinforcement_messages" in _COMBAT_PASSTHROUGH_FIELDS


# ── F9: campaign log maps the real combat outcome vocabulary (never "draw") ──

class TestF9BattleOutcomeLabels:
    def _line(self, outcome):
        return format_event_oneliner({
            "type": "battle", "attacker": "Ney", "defender": "Mack",
            "attacker_nation": "France", "defender_nation": "Austria",
            "location": "Swabia", "outcome": outcome,
            "attacker_casualties": 6917, "defender_casualties": 3431,
        })

    def test_defender_tactical_victory_not_draw(self):
        line = self._line("defender_tactical_victory")
        assert "draw" not in line.lower()
        assert "Mack" in line

    def test_attacker_victory_labeled(self):
        assert "draw" not in self._line("attacker_victory").lower()
        assert "Ney" in self._line("attacker_victory")

    def test_stalemate_labeled(self):
        assert "stalemate" in self._line("stalemate").lower()

    def test_mutual_destruction_labeled(self):
        assert "mutual" in self._line("mutual_destruction").lower()


# ── F4: "recruit reinforcements" routes to recruit, not a destination-less move ──

class TestF4RecruitRouting:
    def setup_method(self):
        self.client = LLMClient(use_real_api=False)

    def _action(self, text):
        return self.client._parse_with_mock(text, None).action

    def test_recruit_reinforcements(self):
        assert self._action("recruit reinforcements") == "recruit"

    def test_addressed_recruit_reinforcements(self):
        assert self._action("Soult, recruit reinforcements") == "recruit"

    def test_raise_conscripts_to_reinforce_lines(self):
        # recruit intent wins over the trailing figurative "reinforce our lines"
        assert self._action("raise fresh conscripts to reinforce our lines") == "recruit"

    def test_bare_reinforce_still_support(self):
        # a genuine support order (no recruit verb) stays a move → SUPPORT
        assert self._action("reinforce Ney") == "move"


# ── F3: trailing qualifier is trimmed from a support/move target ──

class TestF3TargetQualifierTrim:
    def test_with_clause_trimmed(self):
        assert _clean_target_text("soult with fresh troops") == "soult"

    def test_using_clause_trimmed(self):
        assert _clean_target_text("davout using the cavalry") == "davout"

    def test_plain_target_untouched(self):
        assert _clean_target_text("Bohemia") == "Bohemia"


# ── F2 / deixis: figurative & self-location phrasings classify generic, not region ──

class TestF2DeixisClassifyGeneric:
    def _type(self, world, text):
        return _classify_target(text, None, world)["target_type"]

    def test_figurative_and_deixis_are_generic(self, world):
        for phrase in ("our lines", "here", "there", "the ranks", "the line"):
            assert self._type(world, phrase) == "generic", phrase

    def test_real_region_still_region(self, world):
        # a genuine unknown place name still resolves region-like (unchanged path)
        assert self._type(world, "Bordeaux") == "region"


# ── Fog: location-less enemy tactical events are dropped from the player feed ──

class TestFogLocationlessEnemyDrop:
    def test_enemy_locationless_fortify_dropped(self, world):
        enemy = {"type": "fortify_strengthened", "nation": "Russia",
                 "marshal": "Kutuzov", "defense_bonus": 6, "message": "x"}
        player = {"type": "fortify_strengthened", "nation": world.player_nation,
                  "marshal": "SomeMarshal", "message": "y"}
        out = _filter_tactical_events_by_fog([enemy, player], world)
        assert enemy not in out          # fogged enemy state leak closed
        assert player in out             # player event still shown

    def test_locationless_system_event_kept(self, world):
        sysev = {"type": "capital_proximity_alert", "capital": "Paris",
                 "enemy": "Brunswick", "message": "z"}
        out = _filter_tactical_events_by_fog([sysev], world)
        assert sysev in out              # no marshal/nation → player-neutral, kept
