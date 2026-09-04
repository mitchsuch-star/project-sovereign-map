"""
Command Executor for Project Sovereign
Executes parsed commands against game state with region conquest

Includes Disobedience System (Phase 2):
- Checks for marshal objections before executing orders
- Handles major objections by pausing execution for player choice
- Updates vindication tracker after battles

TODO (Future): Multi-Army Battles
- Support 3+ marshals vs 2+ enemies in same region
- Multi-step commands (e.g., "Ney and Davout, attack Wellington")
- Combined strength calculations with command bonuses
- Coordinated attacks with flanking bonuses
"""
import re

from typing import Dict, List, Optional, Tuple
from backend.ai.generic_targets import is_generic_target
from backend.ai.nation_names import (
    nation_not_a_province_message,
    nation_province_list,
    resolve_typed_nation,
)
from backend.models.world_state import WorldState
from backend.models.marshal import Stance
from backend.game_logic.combat import CombatResolver
from backend.utils.fuzzy_matcher import FuzzyMatcher
# V2a Objection System imports
from backend.commands.objection_v2 import (
    ConcernLevel, evaluate_situation, apply_mood_variance,
    get_trust_tier, get_objection_tone, get_insist_penalty,
    calculate_trust_gain, COMPROMISE_TRUST_GAIN,
    concern_to_legacy_severity,
)


from backend.commands.combat_executor import CombatExecutor, friendly_fire_refusal
from backend.commands.strategic_executor import StrategicExecutor
from backend.commands.diplomatic_executor import DiplomaticExecutor
from backend.commands.vassal_executor import VassalExecutor
from backend.commands.capture_executor import CaptureExecutor
from backend.commands.economy_executor import EconomyExecutor
from backend.commands.tactical_executor import TacticalExecutor
from backend.commands.movement_executor import MovementExecutor
from backend.commands.naval_executor import NavalExecutor
from backend.commands.meta_executor import MetaExecutor, _filter_tactical_events_by_fog, ADMIN_ACTIONS

# CA9-N5: a pending objection blocked EVERYTHING, including asking what
# is going on. These five are pure reads — they mutate no state, cost no
# AP, and their executors are marked `free_action` — so a marshal
# standing on his dignity may not also stop the Emperor from reading the
# intelligence report that would decide the argument. Deliberately NOT
# the `free_actions` list at :653: that one holds diplomacy and vassal
# verbs, which mutate.
OBJECTION_FREE_READS = frozenset({
    "status", "help", "economy", "treasury", "finances",
})

# Combat methods delegated to CombatExecutor (R10A+R10B backward compat)
_COMBAT_DELEGATED = {
    # R10A: Combat execution
    '_execute_attack', '_execute_bombardment', '_execute_glorious_charge',
    '_execute_charge', '_execute_form_square', '_execute_break_square',
    'respond_to_glorious_charge', '_resolve_garrison_combat',
    '_post_combat_pipeline', '_handle_forced_retreat',
    '_apply_forced_retreat_or_break', '_distribute_casualties',
    '_get_casualty_participants', '_apply_battle_effects_to_region',
    '_log_battle_event', '_process_combat_notifications',
    '_attempt_region_capture', '_apply_plunder', '_apply_secure',
    '_get_ai_capture_choice', '_apply_ai_capture_choice',
    # R10B: Coordination system
    '_count_unit_types', '_get_combined_arms_bonus',
    '_calculate_per_ally_coordination', '_count_adjacent_allies',
    '_calculate_coordination_context', '_has_dedicated_support',
    '_is_reinforcement_eligible', '_calculate_arrival_score',
    '_calculate_reinforcements', '_clear_coordination_fields',
    '_calculate_overwatch',
    # R10B: Auto-dispatch combat methods
    '_execute_general_attack', '_execute_general_attack_combat',
    '_execute_auto_assign_attack', '_execute_auto_assign_bombardment',
    '_execute_general_retreat', '_execute_general_defensive',
}

# Strategic methods delegated to StrategicExecutor (R11 backward compat)
_STRATEGIC_DELEGATED = {
    '_generate_mild_concern_message', '_generate_objection_message',
    '_resolve_generic_target', '_find_nearest_enemy', '_build_clarification',
    '_execute_strategic_command', '_handle_strategic_objection_response',
    '_handle_first_step_blocked', '_execute_cancel',
    '_handle_strategic_objection_from_endpoint',
}

# Diplomatic methods delegated to DiplomaticExecutor (R11 backward compat)
_DIPLOMATIC_DELEGATED = {
    '_execute_diplomatic', '_execute_diplomatic_proposal',
    '_execute_diplomatic_mission', '_execute_diplomatic_feasibility',
    '_execute_diplomatic_advisory', '_execute_diplomatic_break',
    '_execute_diplomatic_downgrade', '_execute_diplomatic_declare_war',
    '_execute_diplomatic_ultimatum', '_apply_diplomatic_trust_reactions',
    'handle_diplomatic_dialogue_response', 'handle_diplomatic_objection_response',
    '_process_dialogue_choice',
    '_copy_guidance_context', '_build_gold_step', '_build_ap_step',
    '_build_confirm_step', '_handle_accept_ai_proposal',
    '_handle_reject_ai_proposal', '_handle_counter_ai_proposal',
}

# Vassal methods delegated to VassalExecutor (R13A backward compat)
_VASSAL_DELEGATED = {
    '_execute_invest_vassal', '_execute_change_autonomy',
    '_execute_make_vassal', '_execute_release_vassal',
}

# Capture methods delegated to CaptureExecutor (R13A backward compat)
_CAPTURE_DELEGATED = {
    'handle_capture_choice',
}

# Economy methods delegated to EconomyExecutor (R13A backward compat)
_ECONOMY_DELEGATED = {
    '_execute_economy', '_execute_recruit', '_execute_garrison',
    '_execute_build', '_execute_build_watchtower', '_execute_repair',
    '_calculate_recruit_cost', '_extract_building_type',
}

# Tactical methods delegated to TacticalExecutor (R13A backward compat)
_TACTICAL_DELEGATED = {
    '_execute_defend', '_execute_wait', '_execute_drill',
    '_execute_fortify', '_auto_break_square', '_execute_unfortify',
    '_get_stance_change_cost', '_execute_stance_change', '_execute_restrain',
}

# Movement methods delegated to MovementExecutor (R13B backward compat)
_MOVEMENT_DELEGATED = {
    '_has_depot_supply_bonus', '_calculate_movement_attrition',
    '_execute_move', '_execute_scout', '_execute_auto_assign_scout',
    '_execute_retreat_action',
}

# Meta methods delegated to MetaExecutor (R13B backward compat)
_META_DELEGATED = {
    '_execute_end_turn', '_apply_grouchy_ambiguity_buff',
    '_execute_status', '_execute_help',
    '_execute_debug', '_execute_cheat',
    'handle_objection_response', '_execute_post_objection',
}


# Module-level functions (_action_display_name, _proposal_display_name,
# _filter_tactical_events_by_fog) moved to meta_executor.py (R13B)


# ═══════════════ WO-13 — THE ENEMY-DIRECTION GATE ═══════════════
# Three name-resolution seams in this file auto-corrected a query into a
# MARSHAL with no typo gate at all, while their region sibling
# (`_fuzzy_match_region`, the WO-2 backstop) has been gated since August
# 2026. The fuzzy matcher scores by partial ratio, which rewards a short
# word for being CONTAINED in a long name, so on the shipped 1805 board
# twelve province names collapse onto marshals — `Bern` -> Bernadotte and
# `Leon` -> Napoleon at a full score of 100, `Gascony`/`Guyenne`/`Maine`/
# `Brittany`/`Champagne`/`Lorraine`/`Ukraine` -> Ney at 80, `Oslo` ->
# Napoleon and `Rome` -> Armfelt at 75.
#
# What that cost, measured on the 40-turn ambient board:
#   * Britain's Iberian army STALLED FOR TWELVE TURNS. Paget stood at
#     Bearn from turn 17 to 28, adjacent to Gascony, and six times — turns
#     17, 19, 21, 23, 25, 27, every OTHER turn, because a failed action
#     writes a 2-turn cooldown — his attack on that province was redirected
#     to Ney, wherever Ney happened to be, and refused as out of range:
#     "Paget cannot reach Gascony (Vienna) from Bearn! Range: 1, Distance:
#     8" names the province and prints another man's location beside it. A
#     second corps, the artillerist Shrapnel, spent the alternate turns the
#     same way. The seventeen collapses span turns 6–27 in two phases: six
#     `Leon → Napoleon` ordered from Lisbon, then eleven `Gascony → Ney`
#     from Bearn. Paget never took Gascony; on turn 29 he gave up and
#     marched on Bordelais instead.
#     (⚠ The first draft of this comment said "FROZEN for 22 consecutive
#     turns", which was the SPAN of all seventeen collapses read as one
#     marshal's ordeal. Two marshals, two provinces, two phases. Corrected
#     on measurement.)
#   * Twelve of the twenty nations boot with NO war-enemies at all, and
#     for those the broad diplomatic check answers instead — it matches
#     over every non-allied marshal and hands back a man the caller is at
#     PEACE with, for auto-war-declaration. Reproduced: a Prussian order
#     to attack the province `Gascony` resolved to Ney, DECLARED WAR ON
#     FRANCE, and cascaded Spain, Bavaria, Holland, the Kingdom of Italy
#     and Switzerland in behind it.
#
# The gate is the project's own `_plausible_name_typo`, applied exactly as
# the region backstop applies it: an auto-correct that does not look like
# a typed mistake is not a match. An implausible correction FALLS THROUGH
# to the honest not-found arm rather than returning a suggestion, because
# a guess at a marshal's name is the same defect one register over
# (CA8-28: ordinary English never becomes a province, not even as a
# guess) — and because falling through keeps the armistice path below it
# reachable for corrections that ARE plausible.
#
# `Brunswick` is the ONE case this cannot close and is not meant to: it is
# a live province AND a Prussian marshal, identical strings, so it never
# reaches the fuzzy arm at all — the exact lookup at the head of each seam
# resolves it first. That resolution order is documented at each seam and
# pinned; it is a recorded exception, not an oversight.
#
# Three levers rather than one, so the BASELINE_SERIES attribution can
# name which seam moved the board. False restores the pre-slice
# RESOLUTION byte-identically (the HOST_RULE_ACTIVE idiom) — which is what
# the attribution measures, since a refusal message never feeds the series.
# It does NOT restore the pre-slice MESSAGE: `_display_candidates` (R5) and
# the own-roster/prisoner filter sit outside all three levers on purpose,
# because a fog leak must not be switchable. Stated precisely because the
# first draft of this comment said "the pre-slice behaviour", and a review
# measured the difference. Not a config surface.
# Landing record: docs/WEIRD_OUTCOMES_SPEC.md §3 slice 10.
ENEMY_DIRECTION_GATE_ACTIVE = True
BROAD_DIPLOMATIC_GATE_ACTIVE = True
MARSHAL_DIRECTION_GATE_ACTIVE = True


def _correction_survives(query: str, match: Optional[str],
                         gate_active: bool) -> bool:
    """WO-13 — True when a fuzzy auto-correct onto a MARSHAL may stand.

    ONE predicate behind all three FUZZY seams, so a census can prove no
    fuzzy seam was missed. `gate_active` is the seam's own flip lever:
    False restores the ungated behaviour for the attribution experiment.

    Scope, stated because the first draft of this docstring overclaimed
    and a review caught it: this covers the auto-correct arms ONLY. The
    exact marshal-first arm is six further sites — `_check_diplomatic_block`
    and the heads of `_fuzzy_match_enemy` and `_fuzzy_match_marshal` in this
    file, `StrategicExecutor`'s two PURSUE resolvers, and
    `CombatExecutor._resolve_auto_assign_attacker` — and no typo gate can
    reach them, because an identical string IS a plausible typo. That arm is
    governed by the POSITIONAL rule below, not by this predicate. (Named,
    not numbered: the first draft cited line numbers and four of the six
    were already stale by the time it shipped — in a slice whose own commit
    message corrects the contract for stale line numbers.)

    THE POSITIONAL RULE for a name that is both a province and a marshal
    (`Brunswick`, and on the shipped board only `Brunswick`) — stated once,
    here, because writing it per-seam is how two contradictory versions of
    it came to exist:

        THE NAME MEANS THE MAN wherever a man can be meant. As an
        ADDRESSEE ("Brunswick, hold") he is a foreign commander and is
        refused by name, exactly as `Mack` and `Kutuzov` are. As a TARGET
        ("attack Brunswick") he is the quarry.

        THE PROVINCE IS REACHED BY A REGION-ONLY VERB — `move to
        Brunswick`, which can mean nothing else and is therefore never
        ambiguous.

    ⚠ The first draft of this rule said "ADDRESSEE position -> the
    PROVINCE. 'Brunswick, hold' is a garrison order." Both halves were
    false: there is no province-addressee route at all, and what the
    addressee carve-out actually bought was that FRANCE COULD FORTIFY A
    PRUSSIAN MARSHAL AT BERLIN — the one collision on the board punching
    the one hole in WO slice 2's guard. It is fixed at
    `parser._resolve_enemy_addressee`, where the exact enemy roster now
    outranks the region carve-out.

    Both halves are pinned. The durable half is `modding/validator.py`,
    which refuses to let a scenario author a NEW collision — the typo gate
    closes today's twelve by lexical accident (different first letters,
    large edit distance), not because it knows `Gascony` is a place.
    """
    if not gate_active:
        return True
    from backend.commands.parser import _plausible_name_typo
    return _plausible_name_typo(query or "", match or "")


def _humanised(names: List[str]) -> List[str]:
    """Roster keys as the player reads them (`ArchdukeJohn` -> `Archduke
    John`), through the chokepoint CR-5 created for exactly this."""
    from backend.display_names import humanize_entity_name
    return [humanize_entity_name(name) for name in names]


def _honest_alternatives(result: Dict, candidates: List[str],
                         query: str = "") -> List[str]:
    """The names to offer when nothing resolved.

    `match_with_context` populates `suggestions` only on its low-score
    arm; an auto-correct the WO-13 gate refuses arrives with an EMPTY
    list, which printed "Available: none" on a board full of enemies.
    Naming the real candidates is honest and is not a guess — it makes no
    claim that the query meant any of them.

    `candidates` must ALREADY be the display-safe list — see
    `_display_candidates`. Both arms are filtered here, not just the new
    one: the low-score arm's `suggestions` come from the same omniscient
    roster and leaked the same way before this slice.
    """
    allowed = list(candidates)
    permitted = {name.lower() for name in allowed}
    offered = [name for name in (result.get("suggestions") or [])
               if name.lower() in permitted]
    # HUMANISED at the end, never at the start: `_display_candidates` and
    # the `offered` filter both compare against RAW roster keys, so
    # humanising earlier breaks the comparison (measured — the fog pin went
    # red on "Archduke John" not being in a set of raw names). CR-5's
    # post-completion audit created `humanize_entity_name` for the
    # identical defect one register over; this refusal printed the raw key,
    # "Available: ArchdukeJohn, Mack".
    if offered:
        return _humanised(offered[:3])
    if query:
        # RANK, never truncate. `match_with_context` returns an EMPTY
        # `suggestions` list on the auto-correct arm by design, so a refused
        # near-miss fell through to `allowed[:3]` — a constant. Measured, and
        # it inverted the message against confidence: gibberish ("Zorblax",
        # score 0) got the two nearest names while "Nurat" (score 80) was
        # answered "Available: Ney, Davout, Soult" with Murat absent.
        matcher = FuzzyMatcher()
        allowed = sorted(
            allowed, key=lambda name: -matcher._get_best_score(query, name))
    return _humanised(allowed[:3])


def _display_candidates(world, from_nation: Optional[str],
                        candidates: List[str]) -> List[str]:
    """R5 — the names a refusal may PRINT, as opposed to match against.

    Resolution stays omniscient by design (combat must find a fogged
    marshal by name; `test_fog_filtered_access` pins it). The message
    must not be, and it was: the enemy seam's candidate list is
    `world.get_enemy_marshals()`, which returns every non-French marshal
    with no visibility filter, so "Enemy 'Gascony' not found. Available:
    ArchdukeJohn, Castanos, Mack" named Castanos — a Spanish corps France
    had never scouted. A ranked list of hidden armies is free
    intelligence, which is what CA8-28 forbids one register over.

    Only the PLAYER's own messages are filtered: an AI caller never
    renders this string (no enemy_ai site reads `message` beyond a 60-char
    stdout print), and the fog store is the player's, so filtering an AI
    nation's list would apply the wrong fog to nobody's benefit.
    """
    if world is None or from_nation != getattr(world, "player_nation", None):
        return list(candidates)
    try:
        visible = {m.name.lower() for m in world.get_visible_enemies(from_nation)}
    except Exception:
        # FAIL CLOSED. The first cut returned `candidates` here — the
        # omniscient roster, i.e. exactly the list this function exists to
        # stop printing. On an R5 boundary an error must cost the player a
        # helpful message, never cost them the fog.
        return []
    return [name for name in candidates if name.lower() in visible]


class CommandExecutor:
    """
    Executes validated commands and returns results.
    Handles smart command routing based on game state.
    """

    # Class-level constants delegated from CombatExecutor (R10A backward compat)
    ARTILLERY_CASUALTY_FACTOR = CombatExecutor.ARTILLERY_CASUALTY_FACTOR
    PLUNDER_INCOME_MULTIPLIER = CombatExecutor.PLUNDER_INCOME_MULTIPLIER

    # Class-level constants delegated from EconomyExecutor (R13A backward compat)
    GARRISON_DETACHMENT_SIZE = EconomyExecutor.GARRISON_DETACHMENT_SIZE
    GARRISON_MIN_MARSHAL_STRENGTH = EconomyExecutor.GARRISON_MIN_MARSHAL_STRENGTH
    GARRISON_MAX_PER_NATION = EconomyExecutor.GARRISON_MAX_PER_NATION
    WATCHTOWER_GOLD_COST = EconomyExecutor.WATCHTOWER_GOLD_COST
    WATCHTOWER_BUILD_TIME = EconomyExecutor.WATCHTOWER_BUILD_TIME

    def __init__(self):
        """Initialize the command executor."""
        self.combat_resolver = CombatResolver()
        self.fuzzy_matcher = FuzzyMatcher()
        # WO slice 17 review round: the HOLD-sally flag `execute()` stamps
        # per command, initialised rather than left to `getattr` defaults —
        # it now suppresses capture as well as the advance, so a stale True
        # would be a stand-off, not a mere no-advance.
        self._current_sortie = False
        self._combat = CombatExecutor(self)
        self._strategic = StrategicExecutor(self)
        self._diplomatic = DiplomaticExecutor(self)
        self._vassal = VassalExecutor(self)
        self._capture = CaptureExecutor(self)
        self._economy = EconomyExecutor(self)
        self._tactical = TacticalExecutor(self)
        self._movement = MovementExecutor(self)
        self._naval = NavalExecutor(self)
        self._meta = MetaExecutor(self)
        print("Command Executor initialized")

    def __getattr__(self, name):
        """Delegate methods to sub-executors (R10A/R11/R13A backward compat)."""
        if name in _COMBAT_DELEGATED and '_combat' in self.__dict__:
            return getattr(self._combat, name)
        if name in _STRATEGIC_DELEGATED and '_strategic' in self.__dict__:
            return getattr(self._strategic, name)
        if name in _DIPLOMATIC_DELEGATED and '_diplomatic' in self.__dict__:
            return getattr(self._diplomatic, name)
        if name in _VASSAL_DELEGATED and '_vassal' in self.__dict__:
            return getattr(self._vassal, name)
        if name in _CAPTURE_DELEGATED and '_capture' in self.__dict__:
            return getattr(self._capture, name)
        if name in _ECONOMY_DELEGATED and '_economy' in self.__dict__:
            return getattr(self._economy, name)
        if name in _TACTICAL_DELEGATED and '_tactical' in self.__dict__:
            return getattr(self._tactical, name)
        if name in _MOVEMENT_DELEGATED and '_movement' in self.__dict__:
            return getattr(self._movement, name)
        if name in _META_DELEGATED and '_meta' in self.__dict__:
            return getattr(self._meta, name)
        raise AttributeError(f"'{type(self).__name__}' has no attribute '{name}'")

    def _fuzzy_match_marshal(self, marshal_name: str, world: WorldState) -> Tuple[Optional[object], Optional[Dict]]:
        """
        Try to find marshal with fuzzy matching for typo tolerance.

        Returns:
            Tuple of (marshal_object, error_dict)
            - If exact match or auto-correct: (marshal, None)
            - If suggestion or error: (None, error_dict)
        """
        # Try exact match first
        marshal = world.get_marshal(marshal_name)
        if marshal:
            return (marshal, None)

        # Get all marshal names for fuzzy matching (player + enemy)
        all_marshals = list(world.marshals.keys())

        if not all_marshals:
            return (None, {
                "success": False,
                "message": "No marshals available"
            })

        # Try fuzzy match
        result = self.fuzzy_matcher.match_with_context(marshal_name, all_marshals)

        # WO-13 gate (the "fifth seam"): an EXACT name always stands - that
        # is the documented resolution order for `Brunswick`, who is a
        # Prussian marshal and a province at once. An auto-correct must look
        # like a typed mistake or it is not a match, and falls to the honest
        # arm below.
        if (result["action"] == "exact"
                or (result["action"] == "auto_correct"
                    and _correction_survives(marshal_name,
                                             result.get("match"),
                                             MARSHAL_DIRECTION_GATE_ACTIVE))):
            # Exact match or plausible-typo correction - use corrected name
            marshal = world.get_marshal(result["match"])
            return (marshal, None)
        elif (result["action"] == "suggest"
                and _display_candidates(
                    world, world.player_nation, [result.get("match") or ""])
                + [n for n in [result.get("match") or ""]
                   if world.get_marshal(n) is not None
                   and world.get_marshal(n).nation == world.player_nation]):
            # Medium confidence - ask for confirmation. R5: only about one of
            # OUR marshals, or an enemy we can actually see. `Kuzutov` used
            # to answer "Did you mean 'Kutuzov'?" about an unscouted Russian
            # corps, from a seam whose sibling arm filters.
            return (None, {
                "success": False,
                "message": f"Marshal '{marshal_name}' not found. Did you mean '{result['match']}'?",
                "suggestion": result["match"],
                "score": int(result["score"] * 100)
            })
        else:
            # Low confidence, or an auto-correct the WO-13 gate refused.
            # "Available" here answers "which of YOUR marshals" — naming a
            # foreign commander would be both unhelpful and a fog leak, and
            # a man in enemy captivity is not available to be ordered
            # (`captured_by` + strength, the predicate `parser`
            # and `economy_executor` already share).
            own = [name for name in all_marshals
                   if (world.get_marshal(name).nation == world.player_nation
                       and not getattr(world.get_marshal(name),
                                       "captured_by", "")
                       and world.get_marshal(name).strength > 0)]
            # NO `or all_marshals` fallback. It re-opened the exact leak
            # this slice landed to close, one line below the comment
            # forbidding it: with the player's roster emptied — reachable,
            # since PC15-1's `destroy_marshal` pops marshals — the refusal
            # fell back to the omniscient roster and printed
            # "Available: ArchdukeJohn, Castanos, Mack", naming the same
            # unscouted Spanish corps the review round quoted as its P1.
            # An empty list reads "Available: none", which is honest.
            # WO-13: a refused auto-correct that is NOT a place name is an
            # ordinary mistyped marshal, and the region seam's own idiom
            # applies — demote it to a QUESTION rather than throwing the
            # candidate away. `Nurat` asks about Murat; `Gascony` does not
            # ask about Ney, because the world says Gascony is a province.
            # That discriminator is exactly what the runtime lacked and it
            # is in hand here.
            if (result["action"] == "auto_correct"
                    and world.get_region(marshal_name) is None
                    and (result.get("match") or "") in own):
                return (None, {
                    "success": False,
                    "message": (f"Marshal '{marshal_name}' not found. "
                                f"Did you mean '{result['match']}'?"),
                    "suggestion": result["match"],
                    "refused_marshal_correction": True,
                    "score": int(result["score"] * 100)
                })
            alternatives = _honest_alternatives(result, own, marshal_name)
            suggestions_text = ", ".join(alternatives) if alternatives else "none"
            return (None, {
                "success": False,
                "message": f"Marshal '{marshal_name}' not found. Available: {suggestions_text}",
                "suggestions": alternatives
            })

    def _fuzzy_match_region(self, region_name: str, world: WorldState,
                            near: Optional[str] = None) -> Tuple[Optional[object], Optional[Dict]]:
        """
        Try to find region with fuzzy matching for typo tolerance.

        `near` (PC15-13): the ordering marshal's own province, when the
        caller knows it. Only the LOW-confidence branch reads it — when
        string distance has nothing real to offer ('Alsace' → "Wales,
        Balearics, Ulster"), the honest answer is the roads that actually
        lead out of {near}, not the closest-spelled name on the map.

        Returns:
            Tuple of (region_object, error_dict)
            - If exact match or auto-correct: (region, None)
            - If suggestion or error: (None, error_dict)
        """
        # Try exact match first
        region = world.get_region(region_name)
        if region:
            return (region, None)

        # IGR-A3: the player named a NATION, not a province. Answer with that
        # court's own provinces instead of the nearest-scoring place name —
        # "Austria" used to auto-correct to Asturias and march the corps to
        # the Spanish coast, and "Saxony" answered "Did you mean 'Savoy'?".
        # This sits at the single chokepoint all seven callers reach, so
        # move / scout / retreat / attack / bombard all inherit it.
        typed_nation = resolve_typed_nation(region_name, world)
        if typed_nation:
            return (None, {
                "success": False,
                "message": nation_not_a_province_message(typed_nation, world),
                "nation_named": typed_nation,
                "suggestions": nation_province_list(typed_nation, world)[:3],
            })

        # Get all region names for fuzzy matching
        all_regions = list(world.regions.keys())

        if not all_regions:
            return (None, {
                "success": False,
                "message": "No regions available"
            })

        # Try fuzzy match
        from backend.commands.parser import (
            _MIN_FUZZY_TARGET_LEN, _plausible_name_typo,
        )

        result = self.fuzzy_matcher.match_with_context(region_name, all_regions)
        # WO-45 (slice 12): a query under the fuzzy-target floor is never
        # answered with a guess, on EITHER refusing arm — the matcher's
        # short-name bands (SHORT_NAME_AUTO_CORRECT 70 / SUGGEST 50, on
        # partial_ratio) let `Nye` reach `Ukraine` as an implausible
        # auto-correct, which the WO-2 arm below then offered as a question.
        _too_short = len((region_name or "").strip()) < _MIN_FUZZY_TARGET_LEN

        if result["action"] == "exact" or result["action"] == "auto_correct":
            # WO-2 backstop: the parser's arms are typo-gated, but this
            # executor chokepoint auto-corrected over ALL regions ungated —
            # gate the parser alone and `move to the Moon` still marched ten
            # provinces to Morocco. An auto-correct that does not look like
            # a typed mistake becomes a QUESTION, never a march.
            if (result["action"] == "auto_correct"
                    and not _plausible_name_typo(
                        region_name, result.get("match") or "")):
                if _too_short:
                    return (None, {
                        "success": False,
                        "message": f"Region '{region_name}' not found.",
                        "implausible_correction": True,
                    })
                return (None, {
                    "success": False,
                    "message": (f"Region '{region_name}' not found. "
                                f"Did you mean '{result['match']}'?"),
                    "suggestion": result["match"],
                    # The strategic-phrase seam swallows THIS error class
                    # (CA8-28: "the pass" must not print Nassau even as a
                    # guess) while native suggest-band errors keep flowing
                    # ("Venetia" → "Did you mean 'Vienna'?" is helpful).
                    "implausible_correction": True,
                    "score": int(result["score"] * 100)
                })
            # Exact match or plausible-typo correction - use corrected name
            region = world.get_region(result["match"])
            return (region, None)
        elif result["action"] == "suggest" and not _too_short:
            # Medium confidence - ask for confirmation
            return (None, {
                "success": False,
                "message": f"Region '{region_name}' not found. Did you mean '{result['match']}'?",
                "suggestion": result["match"],
                "score": int(result["score"] * 100)
            })
        elif result["action"] == "suggest":
            # WO-45 (slice 12): `Ney, attack Nye` answered "Did you mean
            # 'Ukraine'?" — for a query of four characters or fewer the
            # matcher drops to SHORT_NAME_SUGGEST = 50 and switches to
            # partial_ratio, so a three-letter string reaches the suggest
            # band against almost anything. CA8-28's rule one length-band
            # over: a name the game cannot justify is not offered as a
            # guess. The floor is the SAME `_MIN_FUZZY_TARGET_LEN` the WO-2
            # and WO-13 gates read; the matcher itself is untouched (its
            # blast radius is every name lookup in the game).
            return (None, {
                "success": False,
                "message": f"Region '{region_name}' not found.",
            })
        else:
            # Low confidence - show suggestions
            # PC15-13: when string distance has nothing real ('Alsace' →
            # Wales/Balearics/Ulster) and the caller told us where the
            # marshal STANDS, name the roads out of his province instead —
            # geographic sense over spelling distance.
            near_region = world.get_region(near) if near else None
            if near_region is not None:
                roads = [r for r in getattr(near_region, "adjacent_regions", [])
                         if world.get_region(r) is not None][:4]
                if roads:
                    return (None, {
                        "success": False,
                        "message": (
                            f"Region '{region_name}' not found. From "
                            f"{near_region.name} the roads lead to: "
                            f"{', '.join(roads)}."),
                        "suggestions": roads,
                    })
            suggestions_text = ", ".join(result["suggestions"][:3]) if result["suggestions"] else "none"
            return (None, {
                "success": False,
                "message": f"Region '{region_name}' not found. Nearby: {suggestions_text}",
                "suggestions": result["suggestions"]
            })

    def _make_diplomatic_error(self, world: WorldState, from_nation: str, target_marshal) -> Optional[Dict]:
        """Return diplomatic block error dict if target is in armistice/non-war, else None.
        For non-armistice non-war states, returns the marshal to allow auto-war-declaration."""
        diplo_state = world.get_diplomatic_state(from_nation, target_marshal.nation)
        if diplo_state == "ARMISTICE":
            diplo_key = world._make_diplo_key(from_nation, target_marshal.nation)
            turns_left = int(world.armistice_cooldowns.get(diplo_key, 1))
            return {
                "success": False,
                "message": f"Cannot attack {target_marshal.name} — armistice with {target_marshal.nation} ({turns_left} turns remaining).",
                "diplomatic_block": "armistice",
            }
        return None  # Non-armistice non-war: let auto-war-declaration handle

    def _check_diplomatic_block(self, world: WorldState, from_nation: str, enemy_name: str):
        """Exact-name lookup ignoring war status. Returns (None, error) or (marshal, None) or None."""
        marshal = world.get_marshal(enemy_name)
        if marshal and marshal.nation != from_nation and marshal.strength > 0:
            error = self._make_diplomatic_error(world, from_nation, marshal)
            if error:
                return (None, error)
            # Found but not at war and not armistice — return marshal for auto-war-declaration
            return (marshal, None)
        return None

    def _broad_fuzzy_diplomatic_check(self, world: WorldState, from_nation: str, enemy_name: str):
        """Fuzzy match against ALL non-allied marshals for diplomatic context errors."""
        all_non_allied = [m.name for m in world.marshals.values()
                          if m.nation != from_nation and m.strength > 0]
        if not all_non_allied:
            return None
        result = self.fuzzy_matcher.match_with_context(enemy_name, all_non_allied)
        # WO-13 gate. This seam is not merely the place the first gate
        # re-routes to - it is independently reachable above (`not
        # all_enemies`), which is the state TWELVE of the twenty nations
        # boot in, and it hands back a marshal the caller is at PEACE with
        # for auto-war-declaration. Ungated, a Prussian order to attack the
        # province `Gascony` resolved to Ney and declared war on France.
        if (result["action"] == "exact"
                or (result["action"] == "auto_correct"
                    and _correction_survives(enemy_name,
                                             result.get("match"),
                                             BROAD_DIPLOMATIC_GATE_ACTIVE))):
            matched = world.get_marshal(result["match"])
            if matched:
                error = self._make_diplomatic_error(world, from_nation, matched)
                if error:
                    return (None, error)
                if not world.is_at_war(from_nation, matched.nation):
                    return (matched, None)  # Let auto-war-declaration handle
        return None

    def _fuzzy_match_enemy(self, enemy_name: str, world: WorldState, attacker_nation: str = None) -> Tuple[Optional[object], Optional[Dict]]:
        """
        Try to find enemy marshal with fuzzy matching for typo tolerance.

        TODO (1805): At 80+ regions, fuzzy matching should be filtered by known
        marshals (from intel store) — player typing "attack Kutuzov" when Kutuzov
        was never scouted should fail or warn. On 13 regions this is acceptable
        since players know all marshal names. See FOG_OF_WAR_SPEC.md §5.1.

        Args:
            enemy_name: Name of the target marshal
            world: WorldState instance
            attacker_nation: Optional nation of the attacker. If provided, finds
                           enemies of that nation. If None, uses player perspective.

        Returns:
            Tuple of (marshal_object, error_dict)
            - If exact match or auto-correct: (marshal, None)
            - If suggestion or error: (None, error_dict)
        """
        # Try exact match first
        if attacker_nation:
            # Nation-aware lookup (for enemy AI)
            enemy = world.get_enemy_by_name_for_nation(enemy_name, attacker_nation)
            all_enemies = [m.name for m in world.get_enemies_of_nation(attacker_nation)]
        else:
            # Player-centric lookup (original behavior)
            enemy = world.get_enemy_by_name(enemy_name)
            all_enemies = [m.name for m in world.get_enemy_marshals() if m.strength > 0]

        if enemy:
            return (enemy, None)

        # PT-4 FIX: Secondary search ignoring war status — target may exist
        # but not be at war (armistice/peace). Gives diplomatic error instead
        # of confusing "Unknown target".
        from_nation = attacker_nation or world.player_nation
        diplomatic_block = self._check_diplomatic_block(world, from_nation, enemy_name)
        if diplomatic_block:
            return diplomatic_block

        if not all_enemies:
            # Also try broad fuzzy match before giving up
            broad_block = self._broad_fuzzy_diplomatic_check(world, from_nation, enemy_name)
            if broad_block:
                return broad_block
            return (None, {
                "success": False,
                "message": "No enemies available"
            })

        # Try fuzzy match against war-enemies first
        result = self.fuzzy_matcher.match_with_context(enemy_name, all_enemies)

        # WO-13 gate. An EXACT name always stands (`attack Brunswick` reaches
        # the Prussian marshal - the documented collision order). An
        # auto-correct must look like a typed mistake; an implausible one
        # falls to the low-confidence arm below, which still consults the
        # broad diplomatic check - so an armistice target that IS a plausible
        # typo is still caught - and then answers honestly instead of
        # attacking a man the caller never named.
        if (result["action"] == "exact"
                or (result["action"] == "auto_correct"
                    and _correction_survives(enemy_name,
                                             result.get("match"),
                                             ENEMY_DIRECTION_GATE_ACTIVE))):
            # Exact match or plausible-typo correction - use corrected name
            if attacker_nation:
                enemy = world.get_enemy_by_name_for_nation(result["match"], attacker_nation)
            else:
                enemy = world.get_enemy_by_name(result["match"])
            return (enemy, None)
        elif (result["action"] == "suggest"
                and _display_candidates(world, from_nation,
                                        [result.get("match") or ""])):
            # Medium confidence - ask for confirmation. R5: only about a
            # marshal the asker can SEE. This is the third arm of this seam
            # that prints a name and the review found it was the one
            # `_display_candidates` did not cover — `attack Leon` would have
            # answered "Did you mean 'ArchdukeCharles'?" about a corps France
            # has never scouted, while the arm fourteen lines below, on the
            # same query class, names only the two it can see.
            # `strategic_executor` already scopes the identical question for
            # PURSUE ("a ranked guess at a hidden army is free intelligence").
            # A fogged suggestion falls through to the filtered `else`.
            return (None, {
                "success": False,
                "message": f"Enemy '{enemy_name}' not found. Did you mean '{result['match']}'?",
                "suggestion": result["match"],
                "score": int(result["score"] * 100)
            })
        else:
            # PT-4 FIX: Before giving up, try broad fuzzy match for diplomatic context
            broad_block = self._broad_fuzzy_diplomatic_check(world, from_nation, enemy_name)
            if broad_block:
                return broad_block
            # Low confidence, or an auto-correct the WO-13 gate refused
            alternatives = _honest_alternatives(
                result, _display_candidates(world, from_nation, all_enemies),
                enemy_name)
            suggestions_text = ", ".join(alternatives) if alternatives else "none"
            return (None, {
                "success": False,
                "message": f"Enemy '{enemy_name}' not found. Available: {suggestions_text}",
                "suggestions": alternatives,
                # WO-13: tells the caller this refusal is a REFUSED MARSHAL
                # query, so it answers in the marshal register rather than
                # handing the question to the region seam's guess — `Kutz`
                # used to reach Kutuzov and now must not become "Did you
                # mean 'Frankfurt'?".
                # Its own key, deliberately: `implausible_correction` was
                # already taken by the WO-2 REGION demotion and means
                # something different there, and `strategic_executor`
                # SWALLOWS errors carrying that one. Two meanings on one key
                # is a collision waiting for the next reader.
                "refused_marshal_correction": (
                    result["action"] == "auto_correct"),
            })

    def _attack_target_beyond_range(self, marshal, target, world) -> bool:
        """PF-4: True when an explicit attack `target` resolves to a location
        the marshal cannot reach this turn (distance > movement_range).

        Reuses the SAME resolution + distance primitive `_execute_attack` uses
        (`_fuzzy_match_enemy` / `_fuzzy_match_region` -> `world.get_distance` vs
        `marshal.movement_range`) — it does NOT re-derive any range math. Used
        to skip a wasted, trust-costing objection over an order that
        `_execute_attack` will instead auto-upgrade to a strategic PURSUE (which
        raises its own, semantically-correct strategic objection), hard-fail as
        artillery, or reject as unreachable.

        Returns False for a bare/None target (nearest-enemy auto-target is left
        to `_execute_attack`) and for an unresolvable target (so the unknown-
        target error still surfaces) — the gate is strictly about reachability.
        """
        loc = self._attack_target_location(target, marshal, world)
        if not loc:
            return False
        return world.get_distance(marshal.location, loc) > marshal.movement_range

    def _attack_target_location(self, target, marshal, world):
        """Shared PF-4 / TUT-F6b resolver: where an explicit attack `target`
        points (enemy's location, else region name), via the SAME primitives
        `_execute_attack` uses. None for a bare or unresolvable target."""
        if not target:
            return None
        enemy_by_name, _ = self._fuzzy_match_enemy(target, world, marshal.nation)
        if enemy_by_name is not None:
            return enemy_by_name.location
        region, _ = self._fuzzy_match_region(target, world)
        return region.name if region is not None else None

    def _auto_end_turn_defer_notice(self, world) -> str:
        """WO-22 — why the turn must NOT auto-advance, in the player's words.

        AP exhaustion auto-calls end_turn so the enemy phase is never skipped.
        That auto-advance used to defer for exactly one reason (unanswered
        envoys) while the TYPED ``end turn`` refuses for several — and the
        loudest of those, an unanswered plunder/secure question, was the one
        it crossed. A last-AP attack that took a province auto-advanced
        straight past the question; the enemy phase could retake the
        province; and the answer then died on `handle_capture_choice`'s
        holder re-validation ("the question has lapsed") with the plunder
        gold — `income x 4` — forfeited in silence.

        The capture question is named FIRST because it is the one with money
        on it and the one the player is looking at. Both reasons are stated
        when both apply: a notice that hides the second reason sends the
        player to end the turn explicitly and be refused again.

        LOAD-BEARING: after this defer the player has 0 AP in BOTH pools and
        the pending-choice block at the head of ``execute`` refuses every
        command, ``end turn`` included. The only exit is answering, and that
        exit is safe solely because neither answer route runs through
        ``execute``: the typed router in ``main.py`` fires before it, and
        ``POST /capture_choice`` never touches it. Route a capture answer
        through ``execute`` and this defer becomes a soft-lock with no way
        out — pinned in test_wo_slice15_capture_question_holds.py.

        Deliberately NOT carrying the typed block's ``_strategic_execution``
        exemption: a strategic hop costs no AP, so it cannot reach this
        branch, and importing the carve-out would be a condition that never
        fires today and re-opens WO-22 the day that changes.

        Returns "" when nothing defers the advance.
        """
        reasons = []
        pending = getattr(world, "pending_capture_choice", None)
        if pending:
            # The stage-aware restatement, from the ONE source the refusal
            # and stale-answer paths already speak through — no fourth copy
            # of the question, and the price travels with it.
            reasons.append(
                "All actions are spent, but "
                + self._capture._pending_prompt(pending)
            )
        if world.dialogue_manager.has_current_turn_offers():
            reasons.append(
                "All actions are spent, but unanswered envoys remain. "
                "Review them or end the turn explicitly to let them lapse."
            )
        return " ".join(reasons)

    # FA-22. The marshal-LESS command types a dropped addressee degrades
    # into. Every one of them picks somebody, or acts army-wide, without the
    # player naming who — which is correct for a BARE order and wrong the
    # moment the player did name someone.
    _MARSHAL_LESS_TYPES = (
        "general_attack", "auto_assign_attack", "general_retreat",
        "auto_assign_scout", "auto_assign_bombardment",
    )
    # An addressee is only unbound if it is not itself an ORDER. This is what
    # keeps "attack Bern, then hold your positions" working: its pre-comma
    # phrase is "attack Bern", which names a verb, so nobody was addressed.
    _ADDRESSEE_IS_AN_ORDER_RE = re.compile(
        r"\b(?:attack|assault|engage|storm|charge|bombard|retreat|withdraw"
        r"|fall\s+back|move|march|advance|scout|reconnoitre|reconnoiter"
        r"|hold|defend|fortify|entrench|drill|wait|halt|stop|cancel|recruit"
        r"|raise|build|repair|garrison|blockade|guard|secure|pursue|chase"
        r"|support|reinforce|declare|propose|demand|end|status|help)\b",
        re.IGNORECASE,
    )

    def _unbound_addressee(self, command: Dict, parsed_command: Dict,
                           world) -> Optional[str]:
        """The phrase the player addressed, when the roster cannot bind it.

        Returns None for every command that is not of the marshal-less
        family, for a BARE order (no comma), and whenever the pre-comma
        phrase names a live player marshal or is itself an order.
        """
        if command.get("type") not in self._MARSHAL_LESS_TYPES:
            return None
        if command.get("marshal"):
            return None
        raw = str(parsed_command.get("raw_input")
                  or command.get("raw_input") or "")
        head, sep, _tail = raw.partition(",")
        if not sep:
            return None
        phrase = head.strip().strip("'\"").strip()
        if phrase.lower().startswith("the "):
            phrase = phrase[4:].strip()
        if not phrase or len(phrase) > 40:
            return None
        if self._ADDRESSEE_IS_AN_ORDER_RE.search(phrase):
            return None
        words = {w.lower() for w in re.findall(r"[A-Za-z'-]+", phrase)}
        if not words:
            return None
        player = getattr(world, "player_nation", None)
        for name, marshal in (getattr(world, "marshals", {}) or {}).items():
            if getattr(marshal, "nation", None) != player:
                continue
            if name.lower() in phrase.lower() or words & {
                    w.lower() for w in re.findall(r"[A-Za-z'-]+", name)}:
                return None
        return phrase

    def execute(self, parsed_command: Dict, game_state: Dict) -> Dict:
        """Execute a command against the current game state."""
        # Clear transient square-break notification (set by _auto_break_square)
        self._pending_square_break_msg = ""

        world: WorldState = game_state.get("world")

        if not world:
            return {
                "success": False,
                "message": "Error: No world state available"
            }

        # July 19, 2026 — collapse the "no specific target" sentinels to None
        # at the LAST gate as well as the first (the parser seam already does
        # it). Defence in depth is warranted here specifically: the original
        # defect WAS one layer assuming another had handled "generic", and any
        # caller that builds a command dict without going through the parser
        # would otherwise reach an executor that rejects the very value the
        # parse prompt asks the model to produce. Both paths already treat a
        # missing target as "resolve it for me", so this only ever converts a
        # dead end into that behaviour.
        for _scope in (parsed_command, parsed_command.get("command")):
            if isinstance(_scope, dict) and _scope.get("target") is not None \
                    and is_generic_target(_scope.get("target")):
                _scope["target"] = None

        # C3: Clear auto-advance flag when player takes any non-end-turn action.
        # This allows "end turn" to work normally on subsequent turns after auto-advance.
        action = parsed_command.get("action", "")
        if action != "end_turn" and hasattr(world, '_auto_advanced_to_turn'):
            world._auto_advanced_to_turn = 0

        # ════════════════════════════════════════════════════════════
        # AI-EXECUTION CONTEXT (July 2026 AI audit): commands originating
        # from the enemy phase / AI admin phase / autonomous marshals must
        # never be gated on the PLAYER's pending dialogues or AP pools, and
        # must never trigger the player's auto-end-turn (AI admin builds
        # were draining the player's admin pool and could recursively
        # end_turn mid-enemy-phase). Detection: the _autonomous_execution
        # flag, an _acting_nation other than the player, or a command
        # marshal belonging to another nation.
        # ════════════════════════════════════════════════════════════
        _early_command = parsed_command.get("command", {})
        is_ai_command = bool(_early_command.get("_autonomous_execution"))
        _acting_nation = _early_command.get("_acting_nation")
        if _acting_nation and _acting_nation != world.player_nation:
            is_ai_command = True
        if not is_ai_command and _early_command.get("marshal"):
            _early_m = world.get_marshal(_early_command.get("marshal"))
            if _early_m and _early_m.nation != world.player_nation:
                is_ai_command = True

        # ============================================================
        # DISOBEDIENCE CHECK: Is there a pending objection?
        # (Player-originated commands only — the enemy AI never answers
        # the player's pending dialogues.)
        # ============================================================

        if (world.pending_objection is not None and not is_ai_command
                and _early_command.get("action") not in OBJECTION_FREE_READS):
            from backend.commands.dialogue_routing import format_answer_words
            objecting = world.pending_objection.get("marshal", "A marshal")
            # CA9 review round: this read `alternative`, a key NO
            # producer in backend/ ever writes — both objection sites write
            # `suggested_alternative` + `compromise`. So the sentence could
            # structurally never name 'compromise', while
            # `handle_objection_response` accepts it whenever either key is
            # set: the popup showed a COMPROMISE button and the very next
            # blocked command said "Reply 'trust' or 'insist'." Read the
            # SAME predicate the validator uses, so shown == accepted.
            _choices = ["trust", "insist"]
            if (world.pending_objection.get("suggested_alternative")
                    or world.pending_objection.get("compromise")
                    or world.pending_objection.get("alternative")):
                _choices.append("compromise")
            return {
                "success": False,
                # CA9-N5: the block names the words that clear it. They were
                # already in `choices` below and the sentence omitted them —
                # so the player was told to "settle the objection" with no
                # way to learn how, and the block ate every order until they
                # guessed. shown = offered, from the one list.
                "message": (
                    f"{objecting} awaits your answer, Sire — settle the "
                    f"objection before issuing new orders. Reply "
                    f"{format_answer_words(_choices)}."),
                "awaiting_response": True,
                "objection": world.pending_objection,
                "choices": _choices,
            }

        # ============================================================
        # CAPTURE CHOICE CHECK (Phase 6.2.E): Plunder or Secure?
        # ============================================================
        # PF-3 review fix: a per-hop STRATEGIC-EXECUTION move (an automated march
        # step, not a new player command) must not be blocked here — otherwise a
        # PF-3 move-capture on one hop sets pending_capture_choice and halts the
        # marshal's remaining hops AND every later marshal's continuing order the
        # same turn. Mirrors the is_ai_command exemption; the choice is still set
        # and surfaces to the player in the turn response's popup passthrough.
        _strat_exec = bool(parsed_command.get("command", {}).get("_strategic_execution"))
        if (world.pending_capture_choice is not None and not is_ai_command
                and not _strat_exec):
            _pending = world.pending_capture_choice
            if _pending.get("stage") == "estate":
                # W6-8: the estate stage blocks with its own question.
                _block_msg = (
                    f"You must decide the fate of Marshal "
                    f"{_pending.get('estate_holder', '?')}'s estate at "
                    f"{_pending.get('region', '?')} first! "
                    f"Choose 'confiscate' or 'respect'.")
            else:
                # IGR-X8: the stage-1 block used to be unpriced and nameless
                # ("the captured region") while its estate sibling named
                # holder and region — restate through the same priced sentence
                # every other stage-1 surface uses (one home, world_state).
                from backend.models.world_state import capture_choice_prompt
                _block_msg = ("You must decide how to handle the captured "
                              "region first!"
                              + capture_choice_prompt(_pending))
            return {
                "success": False,
                "message": _block_msg,
                "pending_capture_choice": True,
                "capture_data": _pending
            }

        # ============================================================
        # DIPLOMATIC DIALOGUE CHECK (Phase 8 Session 3, PL-27 Session 2)
        # PL-27: Only HARD-STOP dialogues (commitment_paradox, alias: alliance_paradox,
        # force_declare_war_confirmation) block ALL commands.
        # Soft-stop dialogues (incoming_proposal, counter_offer, etc.)
        # allow ordinary commands through. Dialogue responses are
        # routed BEFORE executor.execute() in main.py's command
        # endpoint. If adding new dialogue response types, update the
        # keyword list in main.py (_DIALOGUE_RESPONSE_KEYWORDS).
        # ============================================================
        command = parsed_command.get("command", {})
        action = command.get("action", "unknown")

        # PL-27: Only hard-stop dialogues block commands (cheat always
        # bypasses; AI-originated commands too — a hard-stop promoted
        # before/during the enemy phase must not zero out every AI nation's
        # turn and poison their failed-action cooldowns)
        if world.dialogue_manager.is_hard_stop() and action != "cheat" and not is_ai_command:
            dialogue = world.pending_diplomatic_dialogue
            option_labels = [f"[{i+1}] {o['label']}" for i, o in enumerate(dialogue.get("options", []))]
            options_text = "  ".join(option_labels)
            target = dialogue.get('target_nation', 'a foreign power')
            return {
                "success": False,
                "message": (
                    f"An incoming diplomatic matter from {target} requires your attention first. "
                    f"Your command has been held — resolve the diplomatic response before issuing other orders. "
                    f"Options: {options_text}  "
                    f"(Use /respond_to_diplomatic_dialogue to handle it via API.)"
                ),
                "awaiting_diplomatic_response": True,
                "diplomatic_dialogue": dialogue,
            }

        # ════════════════════════════════════════════════════════════
        # META-COMMANDS: save/load — no AP cost, bypass all checks
        # Handled before marshal resolution, AP checks, objection checks.
        # ════════════════════════════════════════════════════════════
        if action == "meta_command":
            raw_cmd = (command.get("raw_command") or parsed_command.get("raw_command", "")).strip()
            cmd_lower = raw_cmd.lower()
            if cmd_lower.startswith("save"):
                save_name = raw_cmd[4:].strip() or f"Save - Turn {world.current_turn}"
                from backend.save_manager import save_game
                result = save_game(world, save_name=save_name)
                return {**result, "new_state": game_state}
            elif cmd_lower == "load":
                from backend.save_manager import list_saves
                saves = list_saves()
                save_list = "\n".join(
                    f"  {s['filename']}: {s['metadata'].get('save_name', '?')} (Turn {s['metadata'].get('turn', '?')})"
                    for s in saves
                ) or "  No saves found."
                return {
                    "success": True,
                    "message": f"Available saves:\n{save_list}\n\nUse the load menu to load a save.",
                    "new_state": game_state,
                    "show_load_dialog": True
                }
            # Unknown meta command — fall through to normal processing

        # ════════════════════════════════════════════════════════════
        # STRATEGIC FIELDS PROPAGATION: Copy strategic flags into command dict
        # so they survive objection storage (original_order = command)
        # and can be used for post-objection routing
        # ════════════════════════════════════════════════════════════
        if parsed_command.get("is_strategic"):
            command["is_strategic"] = True
            command["strategic_type"] = parsed_command.get("strategic_type")

        # ════════════════════════════════════════════════════════════
        # STRATEGIC EXECUTION FLAG (Phase 5.2-C)
        # When set, skip action cost + objections (marshal's own decision)
        # ════════════════════════════════════════════════════════════
        is_strategic_execution = command.get("_strategic_execution", False)
        is_sortie = command.get("_sortie", False)
        self._current_sortie = is_sortie  # Expose to _execute_attack

        # ============================================================
        # ACTION ECONOMY: Check if player has actions remaining
        # ============================================================

        # Actions don't apply to status queries or help
        # retreat is FREE (costs 0 actions - strategic withdrawal)
        # debug is FREE (for testing abilities)
        # economy/treasury/finances are FREE information commands (Phase 6.2.G)
        # R72: Vassal commands (invest_vassal, change_autonomy, make_vassal) are free — they cost DP/gold, not military AP
        free_actions = ["status", "help", "end_turn", "unknown", "retreat", "wait", "debug", "cheat", "economy", "treasury", "finances", "break_square", "diplomatic_proposal", "diplomatic_mission", "diplomatic_feasibility", "diplomatic_advisory", "diplomatic_error", "diplomatic_break", "diplomatic_downgrade", "diplomatic_declare_war", "diplomatic_ultimatum", "invest_vassal", "change_autonomy", "make_vassal", "release_vassal", "grant_region_to_vassal", "make_amends", "propose_common_peace", "propose_white_peace", "request_terms", "sponsor_design", "buy_off_design", "guarantee_nation"]

        # Check if action costs points
        action_costs_point = action not in free_actions

        # Strategic execution is always free (cost paid upfront when order issued)
        if is_strategic_execution:
            action_costs_point = False

        # Check if this is a player action (enemy AI has separate action budget)
        # July 2026 AI audit: the AI-execution context covers marshal-less AI
        # commands too (admin builds carry _acting_nation, no marshal — they
        # were gating on and DRAINING the player's admin AP pool)
        is_player_action_check = not is_ai_command
        early_marshal_name = command.get("marshal")
        if early_marshal_name:
            early_marshal = world.get_marshal(early_marshal_name)
            if early_marshal and early_marshal.nation != world.player_nation:
                is_player_action_check = False  # Enemy AI - skip player action check

        # Track whether this is an admin action (uses admin AP pool)
        is_admin_action = action in ADMIN_ACTIONS and is_player_action_check

        # ════════════════════════════════════════════════════════════
        # COUNTER-PUNCH AP WAIVER (Phase 2.8 repair)
        # A cautious marshal who wins a defence earns a FREE attack, and the
        # notification tells the player to "use it THIS turn". He earns it in
        # the ENEMY phase and reaches for it once the turn's own AP is spent —
        # which is exactly the state the two AP pre-gates below refused. The
        # waiver existed only INSIDE `combat_executor._execute_attack`, ~200
        # lines past the gate that stopped the command ever getting there, and
        # was honoured only by the post-execution charge. So the free attack
        # worked while AP remained (invisibly, correctly) and was impossible at
        # 0 AP — the one state in which "free" means anything.
        # GR5: `is_player_action_check` is False for an enemy marshal, so the
        # AI's counter-punch skipped both gates and always worked.
        #
        # Scope: a NAMED marshal only. A bare "attack" is resolved to a marshal
        # further down (:874), after this gate, so there is no one to ask here;
        # the notification names the marshal, and the pin in
        # tests/test_counter_punch_ap_gate.py records that boundary as
        # deliberate rather than leaving it open.
        #
        # This waives only the PRE-gates. Whether the action is actually
        # charged still rides `free_action`, which `_execute_attack` stamps
        # only when it truly consumed the counter-punch — so a waiver that
        # turns out not to apply cannot hand out a free action.
        # A STRATEGIC order is excluded. `pursue` parses to `action == "attack"`
        # with `is_strategic` set, and it costs 2 AP for a standing order, not
        # 1 for a strike — the counter-punch pays for the strike and nothing
        # else. Waiving the gate for it let `Davout, pursue Wellington` at 0 AP
        # attach a standing PURSUE and march him a province while the response
        # said "Not enough actions! Need 2, have 0", with `cancel` costing an
        # AP the player did not have. (Caught by the review round on 4b09e59 —
        # a regression this fix introduced, not a pre-existing one.)
        counter_punch_waiver = False
        counter_punch_snapshot = None
        if (action == "attack" and early_marshal_name
                and is_player_action_check):
            _cp_marshal = world.get_marshal(early_marshal_name)
            if _cp_marshal is not None and _cp_marshal.has_counter_punch():
                # SNAPSHOT UNCONDITIONALLY. The counter-punch is an
                # action-economy resource and obeys the same rule as AP —
                # spent only when the strike is actually thrown — and
                # `_execute_attack` clears the flag at its head, ~3,000 lines
                # above its last exit. That is true whether or not the gate
                # below is waived, so the restore must not be conditional on
                # the waiver. (It was, briefly; the review round caught an
                # out-of-range attack burning the strike with the waiver off.)
                counter_punch_snapshot = (
                    _cp_marshal,
                    int(getattr(_cp_marshal, "counter_punch_turns", 0)))
                # The WAIVER is narrower than the snapshot, on two counts.
                #   * Not a strategic order. `pursue` also parses to
                #     `action == "attack"`, but costs 2 AP for a STANDING
                #     ORDER, which the counter-punch does not pay for.
                #     Waiving it let `Davout, pursue Wellington` at 0 AP
                #     attach the order and march him a province while the
                #     response read "Not enough actions! Need 2, have 0" —
                #     and `cancel` costs an AP the player did not have.
                #   * Only a strike he can throw THIS turn. An out-of-range
                #     attack does not fight: it degrades into an approach
                #     march or a PURSUE clarification, and waiving those
                #     would buy free MOVEMENT at 0 AP, repeatably, since the
                #     strike is restored when no blow lands. Same PF-4
                #     predicate that already skips a wasted objection over
                #     exactly these degradations.
                if (not parsed_command.get("is_strategic")
                        and not self._attack_target_beyond_range(
                            _cp_marshal, command.get("target"), world)):
                    counter_punch_waiver = True

        if action_costs_point and is_player_action_check and not counter_punch_waiver:
            if is_admin_action:
                # Admin actions use admin AP pool
                if world.admin_actions_remaining < 1:
                    return {
                        "success": False,
                        "message": f"No administrative actions remaining this turn. (Military commands: {int(world.actions_remaining)} remaining)",
                        "actions_remaining": int(world.actions_remaining),
                        "action_summary": world.get_action_summary()
                    }
            else:
                # Military/tactical actions use CP pool
                # Determine how many actions this command needs
                required_actions = world.get_action_cost(action)
                if (not is_strategic_execution and
                        parsed_command.get("is_strategic") and
                        parsed_command.get("strategic_type")):
                    # Strategic commands cost 2 (1 for literal personality;
                    # NP-1: 1 for the sovereign — the Emperor does not
                    # persuade himself, NAPOLEON_SPEC §4.2)
                    # NP-V: single source on the marshal (GR1).
                    marshal_for_cost = world.get_marshal(command.get("marshal", ""))
                    required_actions = (marshal_for_cost.strategic_order_ap()
                                        if marshal_for_cost else 2)

                if world.actions_remaining < required_actions:
                    return {
                        "success": False,
                        "message": f"Not enough actions! Need {required_actions}, have {world.actions_remaining}.",
                        "actions_remaining": int(world.actions_remaining),
                        "action_summary": world.get_action_summary()
                    }

        # ============================================================
        # OCCUPATION BLOCKING CHECK (Phase 6.2.F)
        # Marshals securing a fortress can only status/help/end_turn/wait/retreat
        # ============================================================
        if early_marshal_name and not is_strategic_execution:
            occ_marshal = world.get_marshal(early_marshal_name) if early_marshal_name else None
            if occ_marshal and getattr(occ_marshal, 'occupation_region', None):
                allowed_during_occupation = {"status", "help", "end_turn", "wait", "retreat", "economy", "treasury", "finances"}
                if action not in allowed_during_occupation:
                    return {
                        "success": False,
                        "message": f"{occ_marshal.name} is securing the fortress at {occ_marshal.occupation_region}. "
                                   f"Only wait, retreat, or end turn allowed during occupation."
                    }

        # ============================================================
        # FORTIFIED CHECK (universal — applies to strategic execution too)
        # A fortified marshal physically cannot move or attack.
        # ============================================================
        if is_strategic_execution and action in ['attack', 'move']:
            strat_marshal_name = command.get("marshal")
            if strat_marshal_name:
                strat_marshal = world.get_marshal(strat_marshal_name)
                if strat_marshal and getattr(strat_marshal, 'fortified', False):
                    return {
                        "success": False,
                        "message": f"{strat_marshal_name} is fortified at {strat_marshal.location} and cannot {action}. "
                                  f"Order 'unfortify' first to make the army mobile.",
                        "fortified": True,
                        "suggestion": f"Try: '{strat_marshal_name}, unfortify' to abandon fortified position"
                    }

        # ════════════════════════════════════════════════════════════
        # CR-6 / S5-D1: BARE-ATTACK GATING (blessed CR-6 mini-gate, July 16,
        # 2026). A player "attack" with no marshal named (general_attack /
        # auto_assign_attack) auto-picked a marshal into a REAL battle,
        # skipping CR-2 clarification, the W6-4 muster gate, and the objection
        # gate — the most ambiguous lethal order had the fewest safeguards.
        # Resolve the marshal HERE (after the AP pre-check, before the
        # objection block) so the picked marshal flows through the SAME
        # named-attack pipeline everyone else does:
        #   (a) >1 commandable marshal in enemy contact for a bare "attack" →
        #       "Which marshal shall lead the attack, Sire?" (single-contact
        #       keeps the instant pick);
        #   (b) the rewritten named attack carries `command`, so the W6-4
        #       muster preview + bad-odds gate arm;
        #   (c) action="attack" + a resolved marshal → the objection block
        #       below evaluates the auto-picked marshal like any named order.
        # GR5: AI / strategic-execution / autonomous callers never issue these
        # command types and are guarded out regardless.
        # ════════════════════════════════════════════════════════════
        # ════════════════════════════════════════════════════════════
        # FA-22: AN ADDRESSEE THE ROSTER CANNOT BIND IS A REFUSAL, NOT A
        # LICENCE TO PICK SOMEBODY ELSE.
        #
        # Two gaps let a NAMED addressee fall through to the marshal-less
        # family: `ADDRESS_TOKEN_RE` captures one word, so "the Iron Marshal,"
        # and "Prince of Moskowa," never reach the did-you-mean; and a
        # single-word addressee that merely RESEMBLES a region is skipped as
        # "might be a target" ("Berthier" fuzzy-matches Bern at 75). Either
        # way `marshal` is None, the command degrades, and CR-6's resolver
        # names the nearest marshal — who then fights a real battle in the
        # same response.
        #
        # Measured on the 1805 boot: "the Iron Marshal, attack Mack",
        # "Berthier, attack Mack", "Prince of Moskowa, attack Mack" and
        # "the cavalry, attack Mack" ALL sent SOULT, with a battle report.
        # And it is wider than the row: "Berthier, retreat" ran a WHOLE-ARMY
        # retreat — eight marshals, 2,270 men, ZERO AP, no confirm — while
        # "Ney, retreat" costs none.
        #
        # This gates only the marshal-LESS family, and only when the player
        # actually addressed someone. A BARE command is untouched, so CR-6's
        # blessed instant pick and the bare general retreat both stand.
        _unbound = self._unbound_addressee(command, parsed_command, world)
        if (_unbound
                and not is_ai_command
                and not is_strategic_execution
                and not command.get("_autonomous_execution")):
            return {
                "success": False,
                "message": (
                    f"There is no '{_unbound}' in the order of battle, Sire. "
                    f"Whom did you intend?"),
                "kind": "marshal_not_found",
                "new_state": world,
            }

        if (command.get("type") in ("general_attack", "auto_assign_attack")
                and not is_ai_command
                and not is_strategic_execution
                and not command.get("_autonomous_execution")):
            _auto = self._combat.resolve_auto_attack(
                command, world,
                raw_input=parsed_command.get("raw_input", ""))
            if _auto["kind"] == "clarify":
                return _auto["response"]
            elif _auto["kind"] == "named":
                # The auto-pick chose the marshal; from here the order is
                # indistinguishable from a typed "<marshal>, attack <enemy>".
                command["type"] = "specific"
                command["action"] = "attack"
                command["marshal"] = _auto["marshal"]
                command["target"] = _auto["target"]
                command["_auto_assigned"] = True
                command["_auto_assign_explanation"] = _auto.get("explanation", "")
                action = "attack"
            # "passthrough": leave the command untouched — the existing general/
            # auto-assign executor handles move-toward / no-enemies / errors.

        # ============================================================
        # DISOBEDIENCE SYSTEM: Check for marshal objection
        # ============================================================

        # Track mild objections to prepend to result message
        mild_message = None

        # Only check objection for orders that involve a marshal
        marshal_name = command.get("marshal")
        command_type = command.get("type", "specific")

        # Determine if this order should trigger objection check
        # Note: fortify added for aggressive marshals who object to defensive preparation
        # Note: stance_change added for personality conflicts with stance orders
        # Note: retreat added for aggressive marshals who object to fleeing
        # Note: drill, wait, hold added - aggressive marshals object to these (especially with enemy nearby)
        objection_actions = ["attack", "defend", "move", "scout", "recruit", "fortify", "stance_change", "retreat", "drill", "wait", "hold", "form_square"]

        # Phase M: Strategic commands use strategic objection, not tactical
        is_strategic_command = parsed_command.get("is_strategic", False)

        # NP-1 (NAPOLEON_SPEC §4.2): the sovereign never objects — skip the
        # whole evaluation (objection_v2's head guard is the belt; this is
        # the seam the spec names, and it saves the evaluation call).
        _obj_marshal = world.get_marshal(marshal_name) if marshal_name else None
        _is_sovereign_order = bool(
            _obj_marshal and getattr(_obj_marshal, "is_sovereign", False))

        should_check_objection = (
            action in objection_actions and
            marshal_name is not None and
            not _is_sovereign_order and
            not is_strategic_execution and  # Phase 5.2-C: marshal can't object to own decision
            not is_strategic_command and  # Phase M: strategic objection handled separately
            # July 2026 AI audit: an autonomous marshal executing his OWN
            # AI-decided action can neither object to himself nor be blocked
            # by the "cannot command autonomous marshal" gate below — that
            # gate made the entire autonomy feature a no-op (every decided
            # action bounced off the player-facing refusal)
            not command.get("_autonomous_execution")
        )

        if should_check_objection:
            marshal = world.get_marshal(marshal_name)
            if marshal and marshal.nation == world.player_nation:
                # ═══════════════════════════════════════════════════════════
                # AUTONOMOUS CHECK: Cannot command autonomous marshals (Phase 2.5)
                # Autonomous marshals use Enemy AI decision tree at turn start.
                # Player cannot issue orders until autonomy period ends.
                # ═══════════════════════════════════════════════════════════
                if getattr(marshal, 'autonomous', False) and not is_strategic_execution:
                    reason = getattr(marshal, 'autonomy_reason', 'granted autonomy')
                    turns = marshal.autonomy_turns

                    # Build performance summary
                    wins = getattr(marshal, 'autonomous_battles_won', 0)
                    losses = getattr(marshal, 'autonomous_battles_lost', 0)
                    captures = getattr(marshal, 'autonomous_regions_captured', 0)

                    perf_parts = []
                    if wins > 0:
                        perf_parts.append(f"{wins} battle{'s' if wins != 1 else ''} won")
                    if losses > 0:
                        perf_parts.append(f"{losses} battle{'s' if losses != 1 else ''} lost")
                    if captures > 0:
                        perf_parts.append(f"{captures} region{'s' if captures != 1 else ''} captured")

                    if perf_parts:
                        perf_str = f" ({', '.join(perf_parts)})"
                    else:
                        perf_str = ""

                    return {
                        "success": False,
                        "message": f"{marshal_name} is acting independently{perf_str}. {turns} turn{'s' if turns != 1 else ''} remaining.",
                        "autonomous": True,
                        "autonomy_turns": turns,
                        "autonomy_reason": reason,
                        "performance": {
                            "battles_won": wins,
                            "battles_lost": losses,
                            "regions_captured": captures
                        }
                    }

                # ═══════════════════════════════════════════════════════════
                # FA-16 (slice 2, Sept 4 2026): A CORNERED MARSHAL'S QUESTION
                # IS ANSWERED, NOT MARCHED PAST.
                #
                # `clear_order_bound_interrupt` promises that a last stand is
                # "never dropped" — and it kept that promise, while every
                # other order simply EXECUTED over the standing question:
                # measured, "Ney, move to Lorraine" marched a cornered Ney
                # away with his ask still parked, and "Ney, march to Vienna"
                # hit first-step contact and OVERWROTE the ask with a
                # `contact_bad_odds` question (the third destroyer, beside
                # cancel and destroy). The player owes him one of two words;
                # until it is given, no other order reaches him. `cancel` is
                # exempt (FA-N13's graceful arm names the question instead).
                # ═══════════════════════════════════════════════════════════
                # (No `cancel` or `_strategic_execution` exemption is needed
                # here: this block sits under `should_check_objection`, which
                # already excludes strategic execution and strategic commands
                # — the sweep measured both clauses INERT, and the two pins
                # in test_fa_slice2 hold the path structurally instead.)
                _standing_ask = getattr(marshal, 'pending_interrupt', None)
                if (isinstance(_standing_ask, dict)
                        and _standing_ask.get("interrupt_type") == "last_stand"):
                    from backend.commands.strategic import (
                        STANDALONE_DECISION_LIVENESS_ACTIVE)
                    if STANDALONE_DECISION_LIVENESS_ACTIVE:
                        return {
                            "success": False,
                            "no_action_cost": True,
                            "last_stand_pending": True,
                            "message": (
                                f"{marshal.name} is cornered at {marshal.location} "
                                f"and awaits your word, Sire — 'fight to the last' "
                                f"or 'attempt a breakout'. No other order can reach "
                                f"him until you decide."),
                        }

                # ═══════════════════════════════════════════════════════════
                # STRATEGIC OVERRIDE CHECK (Phase 5.2-C)
                # Override commands silently cancel active strategic orders
                # Non-override commands execute alongside strategic orders
                # ═══════════════════════════════════════════════════════════
                if marshal.in_strategic_mode and not is_strategic_execution:
                    strategic_override_actions = [
                        "attack", "move", "defend", "fortify", "drill", "retreat"
                    ]
                    if action in strategic_override_actions:
                        old_order = marshal.strategic_order
                        marshal.strategic_order = None
                        # Clear holding_position if HOLD was active
                        if old_order and old_order.command_type == "HOLD":
                            marshal.holding_position = False
                            marshal.hold_region = ""
                        # TUT-F4a (Aug 8 2026): an interrupt raised BY this
                        # order dies WITH it — a stale one hijacks the very
                        # next command naming this marshal (main.py's
                        # interrupt route) and answers it with "no active
                        # strategic order". Standalone decisions
                        # (last_stand, muster_confirm) are preserved.
                        # NPC-2: single source. This block used to be the
                        # only copy of the rule, and it sits inside a branch
                        # that excludes strategic commands — see
                        # `clear_order_bound_interrupt`'s docstring.
                        from backend.commands.strategic import (
                            clear_order_bound_interrupt)
                        clear_order_bound_interrupt(marshal)
                        print(f"[STRATEGIC] {marshal.name}'s strategic order "
                              f"cancelled by player {action} command")

                # ═══════════════════════════════════════════════════════════
                # DRILLING CHECK: Cannot order while drilling/drill-locked
                # Also blocks stance_change during any drilling state
                # (Skipped for strategic execution — executor handles state)
                # ═══════════════════════════════════════════════════════════
                is_drilling = getattr(marshal, 'drilling', False) or getattr(marshal, 'drilling_locked', False)
                if is_drilling and not is_strategic_execution:
                    # Drilling-locked blocks ALL orders
                    if getattr(marshal, 'drilling_locked', False):
                        return {
                            "success": False,
                            "message": f"{marshal_name} is locked in drill exercises and cannot receive orders. "
                                      f"Training completes turn {marshal.drill_complete_turn}.",
                            "drilling_locked": True,
                            "complete_turn": int(marshal.drill_complete_turn)
                        }
                    # Regular drilling blocks stance_change
                    if action == 'stance_change':
                        return {
                            "success": False,
                            "message": f"{marshal_name} is engaged in drill exercises and cannot change stance.",
                            "drilling": True,
                            "suggestion": "Wait for drill to complete, or cancel with different orders."
                        }

                # ═══════════════════════════════════════════════════════════
                # FORTIFIED CHECK: Cannot move or attack while fortified
                # ═══════════════════════════════════════════════════════════
                if getattr(marshal, 'fortified', False) and action in ['attack', 'move']:
                    return {
                        "success": False,
                        "message": f"{marshal_name} is fortified at {marshal.location} and cannot {action}. "
                                  f"Order 'unfortify' first to make the army mobile.",
                        "fortified": True,
                        "suggestion": f"Try: '{marshal_name}, unfortify' to abandon fortified position"
                    }

                # ═══════════════════════════════════════════════════════════
                # DEFEND NO-OP: Already defensive + fortified = no action needed
                # Pre-validated here to avoid showing an objection then telling
                # the player the action is pointless.
                # ═══════════════════════════════════════════════════════════
                if action == 'defend' and getattr(marshal, 'stance', None) == Stance.DEFENSIVE and getattr(marshal, 'fortified', False):
                    return {
                        "success": False,
                        "message": f"{marshal_name} is already defending and fortified at {marshal.location}. No further defensive action needed.",
                    }

                # ═══════════════════════════════════════════════════════════
                # RETREAT STATE: Simplified - No personality objections during recovery
                # Certain actions blocked, others allowed without objection dialog
                # ═══════════════════════════════════════════════════════════
                if getattr(marshal, 'retreating', False) and not is_strategic_execution:
                    # Command-aware remaining turns (MC gate Q3 — was a phantom
                    # constant-3 attribute that never counted down)
                    recovery_turns = -(-(3 - getattr(marshal, 'retreat_recovery', 0))
                                       // marshal.get_rally_stages_per_turn())

                    # Actions allowed during retreat (no objections, just execute)
                    allowed_during_retreat = ['move', 'wait', 'recruit', 'retreat']

                    # Stance changes: defensive/neutral allowed, aggressive blocked
                    if action == 'stance_change':
                        target_stance = (command.get('target_stance') or command.get('target') or '').lower()
                        if target_stance in ['aggressive', 'attack', 'offense']:
                            return {
                                "success": False,
                                "message": f"{marshal_name} is recovering from retreat and cannot adopt aggressive stance. "
                                          f"Recovery: {recovery_turns} turn(s) remaining.",
                                "retreating": True,
                                "recovery_turns": recovery_turns
                            }
                        # Defensive/neutral stance allowed - skip objection check
                        should_check_objection = False

                    # Block attack, fortify, drill, scout during retreat
                    elif action in ['attack', 'fortify', 'drill', 'scout']:
                        action_display = action.replace('_', ' ')
                        return {
                            "success": False,
                            "message": f"{marshal_name} is recovering from retreat and cannot {action_display}. "
                                      f"Recovery: {recovery_turns} turn(s) remaining.",
                            "retreating": True,
                            "recovery_turns": recovery_turns
                        }

                    # Defend action during retreat - convert to defensive posture, no objection
                    elif action == 'defend':
                        # Allow defend but skip objection - marshal is already in survival mode
                        should_check_objection = False

                    # All other allowed actions - skip objection check entirely
                    elif action in allowed_during_retreat:
                        should_check_objection = False

                # ═══════════════════════════════════════════════════════════
                # BROKEN STATE: Army shattered from surrounded forced retreat
                # Can ONLY recruit - all other actions blocked for 4 turns
                # ═══════════════════════════════════════════════════════════
                if getattr(marshal, 'broken', False):
                    recovery_stage = getattr(marshal, 'broken_recovery', 0)
                    # Command-aware remaining turns (MC gate Q3)
                    turns_remaining = -(-(4 - recovery_stage)
                                        // marshal.get_rally_stages_per_turn())

                    # ONLY recruit is allowed when broken
                    if action != 'recruit':
                        return {
                            "success": False,
                            "message": f"[BROKEN] {marshal_name}'s army is BROKEN and scattered! "
                                      f"Only recruitment is possible while rebuilding. "
                                      f"Recovery: {turns_remaining} turn(s) remaining.",
                            "broken": True,
                            "broken_recovery": recovery_stage,
                            "turns_remaining": turns_remaining
                        }
                    else:
                        # Recruit is allowed - skip objection check
                        should_check_objection = False

                # ═══════════════════════════════════════════════════════════
                # ALREADY-DEFENDED CHECK - Validation BEFORE objection
                # Don't fire objection for defend when already fortified
                # ═══════════════════════════════════════════════════════════
                current_stance = getattr(marshal, 'stance', None)
                if action == 'defend' and current_stance == Stance.DEFENSIVE:
                    if getattr(marshal, 'fortified', False):
                        current_bonus = int(getattr(marshal, 'defense_bonus', 0) * 100)
                        return {
                            "success": False,
                            "message": f"{marshal.name} is already defending and fortified at {marshal.location} (+{current_bonus}% defense). "
                                      f"No further defensive action needed.",
                        }

                # ═══════════════════════════════════════════════════════════
                # ALREADY-IN-STANCE CHECK - Validation BEFORE objection
                # No point objecting to a stance change that's a no-op.
                # ═══════════════════════════════════════════════════════════
                if action == 'stance_change' and current_stance:
                    target_stance_raw = (command.get('target_stance') or command.get('target') or '').lower()
                    stance_map = {
                        "neutral": Stance.NEUTRAL, "defensive": Stance.DEFENSIVE,
                        "defense": Stance.DEFENSIVE, "defend": Stance.DEFENSIVE,
                        "aggressive": Stance.AGGRESSIVE, "attack": Stance.AGGRESSIVE,
                        "offense": Stance.AGGRESSIVE,
                    }
                    target = stance_map.get(target_stance_raw)
                    if target and current_stance == target:
                        return {
                            "success": False,
                            "message": f"{marshal.name} is already in {current_stance.value.upper()} stance."
                        }

                # ═══════════════════════════════════════════════════════════
                # AGGRESSIVE STANCE CHECK - Validation BEFORE objection
                # Cannot fortify or drill while in aggressive stance
                # ═══════════════════════════════════════════════════════════
                if current_stance and current_stance.value == "aggressive":
                    blocked_while_aggressive = ['fortify', 'drill']
                    if action in blocked_while_aggressive:
                        return {
                            "success": False,
                            "message": f"{marshal_name} cannot {action} while in AGGRESSIVE stance. "
                                      f"The troops are ready to attack, not dig trenches!",
                            "stance": "aggressive",
                            "suggestion": f"Change stance first: '{marshal_name} defensive' or '{marshal_name} neutral'"
                        }

                # ═══════════════════════════════════════════════════════════
                # FORTIFY-WHILE-ENGAGED CHECK - Validation BEFORE objection
                # Mirrors _execute_fortify's own gate. Live playthrough:
                # Massena (engaged at Milan) objected to fortify, the player
                # INSISTED through the drama, and only then did execution
                # fail on the engagement — the exact objection-then-failure
                # shape the bypass hierarchy exists to prevent.
                # ═══════════════════════════════════════════════════════════
                if action == 'fortify':
                    _engaged_here = [
                        m for m in world.marshals.values()
                        if m.location == marshal.location
                        and m.nation != marshal.nation
                        and m.strength > 0
                        and world.is_at_war(marshal.nation, m.nation)
                    ]
                    if _engaged_here:
                        return {
                            "success": False,
                            "message": f"{marshal.name} cannot fortify while engaged with enemy forces! "
                                      f"Enemy present: {', '.join(e.name for e in _engaged_here)}. "
                                      f"Attack or retreat first."
                        }

                # ═══════════════════════════════════════════════════════════
                # ALREADY-FORTIFIED CHECK - Validation BEFORE objection
                # Objection evaluation must run AFTER action validation —
                # no point objecting to an action that would fail anyway.
                # ═══════════════════════════════════════════════════════════
                if action == 'fortify' and getattr(marshal, 'fortified', False):
                    current_bonus = int(getattr(marshal, 'defense_bonus', 0) * 100)
                    return {
                        "success": False,
                        "message": f"{marshal.name} is already fortified at {marshal.location} (+{current_bonus}% defense)."
                    }

                # ═══════════════════════════════════════════════════════════
                # ALREADY-DRILLING CHECK - Validation BEFORE objection
                # Same principle: don't object to a redundant drill order.
                # ═══════════════════════════════════════════════════════════
                if action == 'drill' and (getattr(marshal, 'drilling', False) or getattr(marshal, 'drilling_locked', False)):
                    return {
                        "success": False,
                        "message": f"{marshal.name} is already engaged in drill exercises."
                    }

                # ═══════════════════════════════════════════════════════════
                # RETREAT DANGER CHECK - Validation BEFORE objection (BUG-010)
                # Cannot retreat if not actually in danger
                # ═══════════════════════════════════════════════════════════
                if action == 'retreat':
                    if not world.is_in_danger(marshal_name):
                        return {
                            "success": False,
                            "message": f"{marshal_name} is not in danger. No retreat necessary.",
                            "suggestion": "Use 'move' to reposition instead."
                        }

                # ═══════════════════════════════════════════════════════════
                # FORM_SQUARE PRE-VALIDATION — BEFORE objection
                # Aggressive infantry only — cavalry (Ney) blocked by pre-validation. Future 1805 marshals.
                # ═══════════════════════════════════════════════════════════
                if action == 'form_square':
                    if getattr(marshal, 'square_formation', False):
                        return {
                            "success": False,
                            "message": f"{marshal.name} is already in square formation."
                        }
                    if getattr(marshal, 'cavalry', False):
                        return {
                            "success": False,
                            "message": f"{marshal.name}'s cavalry cannot form an infantry square!"
                        }
                    if getattr(marshal, 'artillery', False):
                        return {
                            "success": False,
                            "message": f"{marshal.name}'s artillery cannot form an infantry square!"
                        }

                # ═══════════════════════════════════════════════════════════
                # FRIENDLY-TARGET CHECK — Validation BEFORE objection
                # An order to attack a named marshal of our OWN nation, an ally,
                # or a vassal must never reach the objection / war-declaration
                # machinery (it would stage a war against our own ally). Only
                # marshal-name targets are resolved here — region-name targets
                # (which may host both friend and foe) are validated deeper in
                # combat_executor's war-declaration backstop.
                # ═══════════════════════════════════════════════════════════
                if action in ('attack', 'charge', 'bombard'):
                    _target = command.get('target')
                    _target_marshal = world.get_marshal(_target) if _target else None
                    if _target_marshal is not None:
                        _refusal = friendly_fire_refusal(
                            world, marshal, _target_marshal.nation)
                        if _refusal is not None:
                            return _refusal

                # ═══════════════════════════════════════════════════════════
                # PF-4: ATTACK REACHABILITY — Validation BEFORE objection
                # An out-of-range 'attack <enemy>' is not a tactical fight — it
                # becomes a strategic PURSUE (its own objection), an artillery
                # hard-fail, or a 'cannot reach' error, all inside
                # _execute_attack. Firing the TACTICAL objection here would make
                # the player pay a trust-costing INSIST on an order that never
                # engages. Skip it (leave _execute_attack in full control) when
                # the target is resolvable but out of movement range. Scoped to
                # 'attack': charge/bombard are deliberately NOT in
                # objection_actions (they never raise a tactical objection), so
                # they need no reachability gate here.
                # ═══════════════════════════════════════════════════════════
                if action == 'attack' and self._attack_target_beyond_range(
                        marshal, command.get('target'), world):
                    should_check_objection = False

                # ═══════════════════════════════════════════════════════════
                # TUT-F6: MOVE REFUSAL PRE-CHECK — Validation BEFORE objection
                # (Aug 8 2026 live report: "the general objects even if the
                # command can't be executed.") A cautious marshal objected to
                # a distant march, the player answered the modal, and the
                # move was then refused (engaged / AP / enemy at the
                # destination). The SAME pure probe _execute_move returns its
                # refusals from runs here; any refusal suppresses the
                # objection so the canonical refusal message surfaces
                # immediately — no condition is duplicated, no message moves.
                # Resolution mirrors _execute_move (_fuzzy_match_region);
                # unresolvable targets fall through untouched.
                # ═══════════════════════════════════════════════════════════
                if action == 'move' and should_check_objection \
                        and command.get('target'):
                    _mv_region, _mv_error = self._fuzzy_match_region(
                        command.get('target'), world)
                    if _mv_error is None and _mv_region is not None:
                        from backend.commands.movement_executor import (
                            MovementExecutor)
                        if MovementExecutor.move_refusal_probe(
                                world, marshal, _mv_region,
                                _mv_region.name) is not None:
                            should_check_objection = False

                # ═══════════════════════════════════════════════════════════
                # TUT-F6b (PF-4 sibling): an in-range attack the naval
                # crossing gate will refuse (covered water on the reach) must
                # not raise a bad-odds objection first — the refusal lives at
                # the combat seam and stays there; this only suppresses the
                # wasted objection. Dormant in one truthiness read on
                # fleet-less worlds.
                # ═══════════════════════════════════════════════════════════
                if action == 'attack' and should_check_objection \
                        and getattr(world, "fleets", None):
                    _atk_loc = self._attack_target_location(
                        command.get('target'), marshal, world)
                    if _atk_loc and _atk_loc != marshal.location:
                        from backend.game_logic.naval import (
                            crossing_check_reach)
                        if not crossing_check_reach(
                                world, marshal.nation, marshal.location,
                                _atk_loc)["allowed"]:
                            should_check_objection = False

                # ═══════════════════════════════════════════════════════════
                # RECKLESSNESS STANCE CHECK — Validation BEFORE objection
                # High recklessness blocks defensive/neutral stance changes.
                # Must run before objection so mood variance can't escalate
                # a MILD objection to MODERATE and bypass the real block.
                # ═══════════════════════════════════════════════════════════
                if action == 'stance_change' and getattr(marshal, 'is_reckless_cavalry', False):
                    target_stance_raw_reck = (command.get('target_stance') or command.get('target') or '').lower()
                    can_use, block_reason = marshal.can_use_stance(target_stance_raw_reck)
                    if not can_use:
                        return {
                            "success": False,
                            "message": block_reason,
                            "recklessness": getattr(marshal, 'recklessness', 0)
                        }

                # ═══════════════════════════════════════════════════════════
                # AP PRE-CHECK — Validation BEFORE objection
                # If the player doesn't have enough AP, fail immediately.
                # Without this, an objection fires and then "proceed" fails
                # with an AP error, which is confusing.
                # ═══════════════════════════════════════════════════════════
                if (action_costs_point and is_player_action_check
                        and not counter_punch_waiver):
                    required_ap = 1  # Default cost
                    if action == 'stance_change':
                        target_stance_raw_ap = (command.get('target_stance') or command.get('target') or '').lower()
                        stance_map_ap = {
                            "neutral": Stance.NEUTRAL, "defensive": Stance.DEFENSIVE,
                            "defense": Stance.DEFENSIVE, "defend": Stance.DEFENSIVE,
                            "aggressive": Stance.AGGRESSIVE, "attack": Stance.AGGRESSIVE,
                            "offense": Stance.AGGRESSIVE,
                        }
                        target_stance_ap = stance_map_ap.get(target_stance_raw_ap)
                        if target_stance_ap:
                            required_ap = self._get_stance_change_cost(current_stance, target_stance_ap)
                    if required_ap > 0 and world.actions_remaining < required_ap:
                        cost_str = f" ({required_ap} action{'s' if required_ap > 1 else ''})" if required_ap > 1 else ""
                        return {
                            "success": False,
                            "message": f"Not enough actions remaining{cost_str}. "
                                      f"{world.actions_remaining} action{'s' if world.actions_remaining != 1 else ''} left.",
                            "actions_remaining": int(world.actions_remaining),
                            "action_summary": world.get_action_summary()
                        }

                # ═══════════════════════════════════════════════════════════
                # SKIP OBJECTION if flag was cleared (e.g., by retreat state)
                # ═══════════════════════════════════════════════════════════
                if should_check_objection:
                    # ═══════════════════════════════════════════════════════════
                    # V2a OBJECTION SYSTEM
                    # Deterministic ConcernLevel evaluation with mood variance
                    # ═══════════════════════════════════════════════════════════

                    # Evaluate concern level using V2 system
                    # NOTE: game_state (method param) already has {"world": world, ...}
                    # V2 evaluators extract world via _get_world(game_state)
                    base_concern = evaluate_situation(marshal, action, command, game_state)

                    # V2b Step 14b: Vindication escalation/de-escalation (+1 or -1 max)
                    # Ordering: base trigger → vindication shift → mood variance
                    # NONE never escalates (no fake objections about orders marshal is fine with)
                    # MILD never drops below MILD (even discredited marshal still grumbles)
                    vindication_shifted = base_concern
                    v_score = getattr(marshal, 'vindication_score', 0)
                    if v_score > 0 and base_concern != ConcernLevel.NONE:
                        # Positive vindication → escalate +1 (marshal proven right, bolder)
                        new_val = min(base_concern.value + 1, ConcernLevel.EXTREME.value)
                        vindication_shifted = ConcernLevel(new_val)
                    elif v_score < 0 and base_concern != ConcernLevel.NONE:
                        # Negative vindication → de-escalate -1 ("boy who cried wolf")
                        new_val = max(base_concern.value - 1, ConcernLevel.MILD.value)
                        vindication_shifted = ConcernLevel(new_val)

                    concern = apply_mood_variance(vindication_shifted)

                    # V2b: Update last_objection_turn for any concern (including MILD)
                    if base_concern != ConcernLevel.NONE:
                        marshal.last_objection_turn = world.current_turn

                    # Get trust tier for consequence scaling
                    trust_tier = get_trust_tier(marshal.trust.value)

                    if concern == ConcernLevel.NONE:
                        # No objection - proceed with execution
                        pass

                    elif concern == ConcernLevel.MILD:
                        # MILD: Flavor text in turn log, order executes
                        # Max 1 MILD per marshal per turn
                        if marshal.name not in [c.get("marshal") for c in world.mild_concerns_this_turn]:
                            # Generate mild flavor message
                            mild_message = self._generate_mild_concern_message(marshal, action, command)
                            world.mild_concerns_this_turn.append({
                                "marshal": marshal.name,
                                "message": mild_message,
                                "concern_level": "MILD",
                                "action": action,
                            })
                        # Continue with execution

                    else:
                        # MODERATE, STRONG, EXTREME: Popup with choices
                        # Per-marshal cap: max 1 popup per marshal per turn
                        if marshal.name in world.objection_popups_this_turn:
                            # Already had popup this turn - downgrade to MILD
                            if marshal.name not in [c.get("marshal") for c in world.mild_concerns_this_turn]:
                                mild_message = self._generate_mild_concern_message(marshal, action, command)
                                world.mild_concerns_this_turn.append({
                                    "marshal": marshal.name,
                                    "message": mild_message,
                                    "concern_level": "MILD",
                                    "action": action,
                                    "downgraded_from": concern.name,
                                })
                        else:
                            # Show popup - mark marshal as having had popup this turn
                            world.objection_popups_this_turn.add(marshal.name)

                            # V2a: Generate alternatives directly (no V1 severity calc)
                            suggested_alt = world.disobedience_system._generate_alternative(
                                marshal, command, world
                            )
                            compromise_action = world.disobedience_system._find_compromise(
                                marshal, command, suggested_alt, world
                            )

                            # ═══════════════════════════════════════════════════
                            # MASTER RULE #2: Exhaust → MILD demotion
                            # If alternatives are empty/identical/same-as-original,
                            # demote to MILD. Never show popup with fake choices.
                            # ═══════════════════════════════════════════════════
                            def _actions_match(a, b):
                                """Check if two action dicts describe the same action."""
                                if a is None or b is None:
                                    return a is None and b is None
                                a_act = a.get('action', '').lower()
                                b_act = b.get('action', '').lower()
                                if a_act != b_act:
                                    return False
                                a_tgt = (a.get('target_stance') or a.get('target', '')).lower()
                                b_tgt = (b.get('target_stance') or b.get('target', '')).lower()
                                return a_tgt == b_tgt

                            should_demote = False

                            # No preferred alternative at all
                            if suggested_alt is None:
                                should_demote = True

                            # Preferred == original (Trust button does what Insist does)
                            elif _actions_match(suggested_alt, command):
                                should_demote = True

                            # Preferred == compromise (two identical buttons)
                            elif _actions_match(suggested_alt, compromise_action):
                                should_demote = True

                            if should_demote:
                                # Fallback exhausted — demote to MILD
                                # Never show popup with identical options.
                                world.objection_popups_this_turn.discard(marshal.name)
                                if marshal.name not in [c.get("marshal") for c in world.mild_concerns_this_turn]:
                                    mild_message = self._generate_mild_concern_message(marshal, action, command)
                                    world.mild_concerns_this_turn.append({
                                        "marshal": marshal.name,
                                        "message": mild_message,
                                        "concern_level": "MILD",
                                        "action": action,
                                        "demoted_from": concern.name,
                                    })
                                # Continue with execution (no popup)
                            else:
                                # Alternatives are valid and distinct — show popup
                                tone = get_objection_tone(trust_tier)
                                insist_penalty = get_insist_penalty(trust_tier)
                                legacy_severity = concern_to_legacy_severity(concern)

                                # Generate message based on tone
                                message = self._generate_objection_message(marshal, action, command, concern, tone)

                                # ES-7 (S7) cosmetic legibility tag (spec
                                # §0.6.2): an eroding marshal's objection
                                # reads as a man frayed by neglect. Display
                                # copy only — never affects routing (GR6).
                                from backend.game_logic.dotation import is_eroding
                                if is_eroding(marshal, world):
                                    message += (" (His loyalty is frayed by "
                                                "neglect — his victories remain "
                                                "unrewarded.)")

                                # V2 scaled trust values. WO-D9: damped at
                                # the QUOTE so the figure on the button is the
                                # figure the marshal is paid.
                                from backend.models.authority import (
                                    damp_objection_trust_gain,
                                    objection_trust_modifier,
                                )
                                trust_gain = damp_objection_trust_gain(
                                    world, calculate_trust_gain(concern, trust_tier))

                                objection = {
                                    # V2 fields
                                    "type": "major_objection",
                                    "concern_level": concern.name,
                                    "trust_tier": trust_tier.name,
                                    "tone": tone,
                                    "insist_penalty": insist_penalty,
                                    "trust_gain": trust_gain,
                                    "compromise_gain": COMPROMISE_TRUST_GAIN,
                                    # WO-D12: the dialog cannot explain a
                                    # figure it cannot see. Display-only —
                                    # 1.0 whenever nothing is damped.
                                    "trust_gain_modifier": (
                                        objection_trust_modifier(world)),
                                    # Backward compat fields
                                    "severity": legacy_severity,
                                    "message": message,
                                    "marshal": marshal.name,
                                    "personality": marshal.personality,
                                    "original_order": command,
                                    # Alternatives generated by personality-specific logic
                                    "suggested_alternative": suggested_alt,
                                    "compromise": compromise_action,
                                }

                                # Store pending objection
                                world.pending_objection = objection

                                return {
                                    "success": True,
                                    "awaiting_response": True,
                                    "pending_objection": True,  # CRITICAL for AP skip logic
                                    "state": "awaiting_player_choice",
                                    "message": message,
                                    "objection": objection,
                                    "choices": ["trust", "insist", "compromise"] if objection.get("suggested_alternative") else ["trust", "insist"],
                                    "marshal": marshal_name,
                                    "personality": marshal.personality,
                                    "concern_level": concern.name,
                                    "tone": tone,
                                    "severity": legacy_severity,
                                    "trust": int(marshal.trust.value),
                                    "trust_label": marshal.trust.get_label(),
                                    "vindication": world.vindication_tracker.get_vindication_data(marshal_name).get("score", 0),
                                    "authority": int(world.authority_tracker.authority),
                                    "suggested_alternative": objection.get("suggested_alternative"),
                                    "compromise": objection.get("compromise")
                                }

        # ============================================================
        # STRATEGIC BONUSES: Apply morale/trust/combat bonuses (Phase 5)
        # Only for player actions, only in non-mock mode
        # ============================================================

        # Define combat actions that get strategic_combat_bonus
        COMBAT_ACTIONS = ["attack", "charge"]

        # Check if we should apply bonuses
        mode = parsed_command.get("mode", "mock")
        strategic_score = parsed_command.get("strategic_score", 0)

        # Only apply for non-mock, player actions with a marshal
        if mode != "mock" and is_player_action_check and marshal_name:
            marshal = world.get_marshal(marshal_name)
            if marshal and marshal.nation == world.player_nation:
                from backend.ai.feedback import apply_strategic_bonuses
                is_combat_action = action in COMBAT_ACTIONS
                apply_strategic_bonuses(marshal, strategic_score, is_combat_action)

        # ============================================================
        # GROUCHY AMBIGUITY COMBAT BUFF (Phase 5.2)
        # Literal marshals get combat bonuses from clear orders
        # ============================================================
        ambiguity = parsed_command.get("ambiguity", 50)
        if is_player_action_check and marshal_name:
            marshal_obj = world.get_marshal(marshal_name)
            if marshal_obj and getattr(marshal_obj, 'personality', '') == 'literal':
                self._meta._apply_grouchy_ambiguity_buff(marshal_obj, ambiguity, strategic_score, action)

        # ════════════════════════════════════════════════════════════
        # CLARIFICATION GATE (Phase 5.2-C — Grouchy)
        # Literal personality + high ambiguity + strategic = clarification popup
        # "You wish me to pursue Blucher (nearest enemy), Sire?"
        # ════════════════════════════════════════════════════════════
        if not is_strategic_execution and marshal_name:
            cl_marshal = world.get_marshal(marshal_name)
            if cl_marshal and getattr(cl_marshal, 'personality', '') == 'literal':
                cl_ambiguity = parsed_command.get("ambiguity", 5)
                cl_is_strategic = parsed_command.get("is_strategic", False)
                if cl_ambiguity > 60 and cl_is_strategic:
                    interpreted = parsed_command.get("interpreted_target")
                    reason = parsed_command.get("interpretation_reason", "unclear")
                    alternatives = parsed_command.get("alternatives", [])
                    strategic_type = parsed_command.get("strategic_type", "unknown")

                    # CR-2: options carry the full reissue command so the
                    # popup and typed answers resolve identically
                    from backend.commands.clarification import strategic_reissue_command

                    options = []
                    if interpreted:
                        options.append({
                            "label": f"Yes, {interpreted}",
                            "value": "confirm",
                            "target": interpreted,
                            "command": strategic_reissue_command(
                                cl_marshal.name, strategic_type, interpreted),
                        })
                    for alt in alternatives[:2]:
                        options.append({
                            "label": f"No, {alt}",
                            "value": "specify",
                            "target": alt,
                            "command": strategic_reissue_command(
                                cl_marshal.name, strategic_type, alt),
                        })
                    if interpreted:
                        options.append({
                            "label": "Proceed as ordered",
                            "value": "confirm",
                            "target": interpreted,
                            "command": strategic_reissue_command(
                                cl_marshal.name, strategic_type, interpreted),
                        })
                    # Note: popup adds its own "Cancel Order" button — don't duplicate

                    if strategic_type == "PURSUE":
                        cl_msg = f"You wish me to pursue {interpreted}, Sire?"
                    elif strategic_type == "SUPPORT":
                        cl_msg = f"You wish me to support {interpreted}, Sire?"
                    elif strategic_type == "MOVE_TO":
                        cl_msg = f"You wish me to march to {interpreted}, Sire?"
                    elif strategic_type == "HOLD":
                        cl_msg = f"You wish me to hold {interpreted}, Sire?"
                    else:
                        cl_msg = f"I understand {interpreted}, Sire. Is this correct?"

                    return {
                        "success": True,
                        "free_action": True,
                        "state": "awaiting_clarification",
                        "type": "clarification",
                        "strategic_type": strategic_type,
                        "marshal": cl_marshal.name,
                        "original_command": command.get("raw_command", ""),
                        "message": cl_msg,
                        "interpreted_target": interpreted,
                        "interpretation_reason": reason,
                        "alternatives": alternatives,
                        "options": options,
                        "action_summary": world.get_action_summary(),
                        "game_state": world.get_filtered_game_state_summary()
                    }

        # ════════════════════════════════════════════════════════════
        # STRATEGIC COMMAND INTERCEPTION (Phase 5.2)
        # If parser detected a strategic command, create StrategicOrder
        # on the marshal and execute first step immediately.
        # ════════════════════════════════════════════════════════════
        if (not is_strategic_execution and
                parsed_command.get("is_strategic") and
                parsed_command.get("strategic_type")):
            strategic_result = self._strategic._execute_strategic_command(parsed_command, command, game_state)
            if strategic_result is not None:
                # Strategic command handled — set result and flow to action economy
                result = strategic_result
                # Jump past normal routing to action economy
                # (Python doesn't have goto, so we use a flag)
                _skip_routing = True
            else:
                _skip_routing = False
        else:
            _skip_routing = False

        # ============================================================
        # Continue with normal command routing
        # ============================================================

        if _skip_routing:
            pass  # Already have result from strategic handler
        # Handle special actions first
        elif action == "status":
            result = self._meta._execute_status(command, game_state)
        elif action == "help":
            result = self._meta._execute_help(command, game_state)
        elif action == "recruit":
            result = self._economy._execute_recruit(command, game_state)
        elif action == "recruit_marshal":
            result = self._economy._execute_recruit_marshal(command, game_state)
        elif action == "build":
            result = self._economy._execute_build(command, game_state)
        elif action == "repair":
            result = self._economy._execute_repair(command, game_state)
        elif action in ("economy", "treasury", "finances"):
            result = self._economy._execute_economy(command, game_state)
        elif action == "garrison":
            result = self._economy._execute_garrison(command, game_state)
        elif action == "grant_dotation":
            # W6-1 (BUG-CA-3): the raw text rides along so the executor can
            # detect a live-LLM-guessed region the player never named.
            result = self._economy._execute_grant_dotation(
                command, game_state,
                raw_text=parsed_command.get("raw_input") or "")
        elif action == "grant_pension":
            # ES-7 second pass (§0.6.8): the rente — treasury pension, face
            # auto-sized to the marshal's current gap in-executor.
            result = self._economy._execute_grant_pension(command, game_state)
        elif action == "revoke_pension":
            result = self._economy._execute_revoke_pension(command, game_state)
        elif action == "end_turn":
            result = self._meta._execute_end_turn(command, game_state)
        # ════════════════════════════════════════════════════════════
        # TACTICAL STATE ACTIONS (Phase 2.6)
        # ════════════════════════════════════════════════════════════
        elif action == "drill":
            result = self._tactical._execute_drill(command, game_state)
        elif action == "fortify":
            result = self._tactical._execute_fortify(command, game_state)
        elif action == "unfortify":
            result = self._tactical._execute_unfortify(command, game_state)
        elif action == "form_square":
            result = self._combat._execute_form_square(command, game_state)
        elif action == "break_square":
            result = self._combat._execute_break_square(command, game_state)
        # ════════════════════════════════════════════════════════════
        # STANCE SYSTEM (Phase 2.7)
        # ════════════════════════════════════════════════════════════
        elif action == "stance_change":
            result = self._tactical._execute_stance_change(command, game_state)
        # ════════════════════════════════════════════════════════════
        # CHEAT COMMANDS (Phase 8 Session 8A)
        # ════════════════════════════════════════════════════════════
        elif action == "cheat":
            result = self._meta._execute_cheat(command, game_state)
        # ════════════════════════════════════════════════════════════
        # DEBUG COMMANDS (Phase 2.8) - Must be before command_type routing
        # ════════════════════════════════════════════════════════════
        elif action == "debug":
            result = self._meta._execute_debug(command, game_state)
        # ════════════════════════════════════════════════════════════
        # CAVALRY RECKLESSNESS SYSTEM (Phase 3)
        # ════════════════════════════════════════════════════════════
        elif action == "charge":
            result = self._combat._execute_charge(command, game_state)
        elif action == "restrain":
            result = self._tactical._execute_restrain(command, game_state)
        elif action == "cancel":
            result = self._strategic._execute_cancel(command, game_state)
        # ════════════════════════════════════════════════════════════
        # DIPLOMATIC COMMANDS (Phase 8 Session 3)
        # ════════════════════════════════════════════════════════════
        elif action in ("diplomatic_proposal", "diplomatic_mission",
                        "diplomatic_feasibility", "diplomatic_advisory",
                        "diplomatic_error", "diplomatic_break",
                        "diplomatic_downgrade", "diplomatic_declare_war",
                        "diplomatic_ultimatum",
                        # B-B7 Make Amends — spec §8.6.1
                        "make_amends",
                        # WB-C explicit bargain repudiation (WAR_BARGAIN_SPEC §C).
                        # Missing here since it landed: the parser routed it
                        # (llm_client._parse_repudiate_bargain), validation
                        # passed it, and diplomatic_executor has dispatched it
                        # all along — but this tuple never listed it, so every
                        # "repudiate the bargain with Austria" fell through to
                        # the unknown-action tail and died as
                        # "Unknown command", in BOTH mock and live mode.
                        "repudiate_bargain"):
            result = self._diplomatic._execute_diplomatic(command, game_state)
        # WPS-A: Set war purpose (defensive war objective, 0 AP)
        elif action == "set_war_purpose":
            result = self._diplomatic._execute_set_war_purpose(command, game_state)
        # Imperial Settlement (WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC §11)
        elif action == "propose_common_peace":
            result = self._diplomatic._execute_propose_common_peace(command, game_state)
        elif action == "request_terms":
            result = self._diplomatic._execute_request_terms(command, game_state)
        # SETTLEMENT_UI_CLEANUP_SPEC v0.28 G2-Slice-W1 White Peace Affordance —
        # distinct labeled action staging settlement_confirm with white_peace=true.
        elif action == "propose_white_peace":
            result = self._diplomatic._execute_propose_white_peace(command, game_state)
        # ════════════════════════════════════════════════════════════
        # VASSAL COMMANDS (Phase 8 Session 5)
        # ════════════════════════════════════════════════════════════
        elif action == "invest_vassal":
            result = self._vassal._execute_invest_vassal(command, game_state)
        elif action == "change_autonomy":
            result = self._vassal._execute_change_autonomy(command, game_state)
        elif action == "make_vassal":
            result = self._vassal._execute_make_vassal(command, game_state)
        elif action == "release_vassal":
            result = self._vassal._execute_release_vassal(command, game_state)
        elif action == "grant_region_to_vassal":
            result = self._vassal._execute_grant_region_to_vassal(command, game_state)
        # ════════════════════════════════════════════════════════════
        # AI-2b D5 COUNTER-INSTRUMENTS (AI_INTENT_SPEC §6 D5)
        # ════════════════════════════════════════════════════════════
        elif action == "sponsor_design":
            result = self._diplomatic._execute_sponsor_design(command, game_state)
        elif action == "buy_off_design":
            result = self._diplomatic._execute_buy_off_design(command, game_state)
        elif action == "guarantee_nation":
            result = self._diplomatic._execute_guarantee_nation(command, game_state)
        # ════════════════════════════════════════════════════════════
        # NAVAL COMMANDS (DEF-5 "The Wooden Wall", NAVAL_SPEC §9)
        # ════════════════════════════════════════════════════════════
        elif action == "build_fleet":
            result = self._naval._execute_build_fleet(command, game_state)
        elif action == "set_fleet_posture":
            result = self._naval._execute_set_fleet_posture(command, game_state)
        elif action == "naval_expedition":
            result = self._naval._execute_naval_expedition(command, game_state)
        elif action == "naval_diversion":
            result = self._naval._execute_naval_diversion(command, game_state)
        # Route to appropriate handler
        elif command_type == "specific":
            # ESP-EV-4: the raw text rides on the command dict so the attack
            # path's guessed-target guard can compare the parse against the
            # player's own words (transient — command dicts never serialize).
            if isinstance(command, dict) and "_raw_input" not in command:
                command["_raw_input"] = parsed_command.get("raw_input") or ""
            result = self._execute_specific(command, game_state)
        elif command_type == "general_attack":
            result = self._combat._execute_general_attack(command, game_state)
        elif command_type == "auto_assign_attack":
            result = self._combat._execute_auto_assign_attack(command, game_state)
        elif command_type == "auto_assign_bombardment":
            result = self._combat._execute_auto_assign_bombardment(command, game_state)
        elif command_type == "auto_assign_scout":
            result = self._movement._execute_auto_assign_scout(command, game_state)
        elif command_type == "general_retreat":
            result = self._combat._execute_general_retreat(command, game_state)
        elif command_type == "general_defensive":
            result = self._combat._execute_general_defensive(command, game_state)
        else:
            result = {
                "success": False,
                "message": f"Unknown command type: {command_type}"
            }

        # An attack that never threw the strike must not spend the
        # counter-punch. `_execute_attack` clears the flag at its head, ~3,000
        # lines and ~55 returns above its last exit, and several of those
        # exits report `success: True` while no blow is struck: the war-purpose
        # staging popup, the PURSUE clarification, the approach march, the
        # opening-attack guidance, the muster confirm.
        #
        # FAIL-CLOSED BY CONSTRUCTION. The list below is of outcomes that
        # certainly did NOT fight; everything else is assumed to have fought.
        # Missing an entry therefore reproduces the old behaviour (the strike
        # is spent) and can never mint a repeatable free attack, which is the
        # failure mode worth guarding against. Classifying all 55 exits the
        # other way round was tried and is not safely reviewable.
        if counter_punch_snapshot is not None:
            _cp_holder, _cp_turns = counter_punch_snapshot
            _res = result if isinstance(result, dict) else {}
            _no_strike = (
                not _res.get("success", False)
                or _res.get("requires_input")            # muster confirm
                or _res.get("pending_interrupt")
                or _res.get("awaiting_diplomatic_response")
                or _res.get("war_purpose_popup")         # war purpose staged
                or _res.get("opening_attack_guidance")   # a briefing, not a blow
                or _res.get("occupation_started")        # walked in unopposed
                # Aug 30, 2026 review: writing a standing order is not
                # throwing a punch. An `attack` on an out-of-range enemy
                # auto-upgrades to a strategic PURSUE, and this block read the
                # successful ORDER as a strike delivered: it burned the
                # cautious marshal's hard-won free attack AND stamped
                # `free_action` on the result, so the 2-AP standing order was
                # issued for nothing. Both halves wrong in the same breath —
                # the reward spent, and the price waived.
                or _res.get("strategic_order")
                or _res.get("state") == "awaiting_clarification"
            )
            if _no_strike:
                _cp_holder.counter_punch_available = True
                _cp_holder.counter_punch_turns = _cp_turns
            elif not (_res.get("free_action") or _res.get("no_action_cost")):
                # The strike WAS thrown on a counter-punch, but this exit
                # forgot to say so — the garrison assault and the
                # auto-bombardment kill both resolve without stamping it, so
                # the player paid an action for a free attack, and one of them
                # printed "This attack costs NO actions" while doing it.
                # Stamped here, where the fact is known, rather than at four
                # more exits that can drift apart again.
                result["free_action"] = True
                result["counter_punch_used"] = True

        # ============================================================
        # ACTION ECONOMY: Consume action ONLY if command succeeded
        # ============================================================

        # Only consume action if:
        # 1. Command succeeded
        # 2. Action costs a point (not free)
        # 3. Marshal belongs to player nation (enemy AI has separate action budget)
        action_result = {"turn_advanced": False, "new_turn": None, "action_cost": 0}

        # Determine if this is a player action (should consume from player's action budget)
        # July 2026 AI audit: AI-execution context (marshal-less admin
        # builds, autonomous marshals) must never consume player pools
        is_player_action = not is_ai_command
        marshal_name = command.get("marshal")
        if marshal_name:
            executing_marshal = world.get_marshal(marshal_name)
            if executing_marshal and executing_marshal.nation != world.player_nation:
                is_player_action = False  # Enemy AI action - don't consume player actions

        # Check if this action is free (counter-punch, etc.)
        is_free_action = result.get("free_action", False) or result.get("no_action_cost", False)

        # CRITICAL: Don't consume AP for pending_objection (Phase M) - AP consumed
        # when player responds, not when objection triggers
        if result.get("success", False) and action_costs_point and is_player_action and not is_free_action and not result.get("pending_objection"):
            if is_admin_action:
                # Admin actions consume from admin AP pool, not CP
                world.use_admin_action()
                # Auto-end turn when BOTH pools are exhausted
                both_exhausted = (world.actions_remaining <= 0 and world.admin_actions_remaining <= 0)
                action_result = {"turn_advanced": False, "new_turn": None, "action_cost": 1, "should_end_turn": both_exhausted}
            else:
                # Check for variable action cost (stance_change returns this)
                variable_cost = result.get("variable_action_cost")
                if variable_cost is not None:
                    # Variable costs (stance: 0-2, strategic upgrades: 1-2)
                    if variable_cost > 0:
                        if world.actions_remaining < variable_cost:
                            # Safety net — should be caught by pre-checks above
                            return {
                                "success": False,
                                "message": f"Not enough actions! Need {variable_cost}, have {world.actions_remaining}.",
                                "actions_remaining": int(world.actions_remaining),
                                "action_summary": world.get_action_summary()
                            }
                        for _ in range(variable_cost):
                            action_result = world.use_action(action)
                    else:
                        # Free transition (returning to neutral)
                        action_result = {"turn_advanced": False, "new_turn": None, "action_cost": 0}
                else:
                    # NOW consume the action (after validation passed)
                    action_result = world.use_action(action)
        elif is_free_action:
            # Free action (counter-punch) - don't consume action point
            action_result = {"turn_advanced": False, "new_turn": None, "action_cost": 0, "should_end_turn": False}
            print("  [FREE ACTION] Counter-punch or similar - no action consumed")

        # Add action info to result
        result["action_info"] = {
            "cost": action_result.get("action_cost", 0),
            "remaining": world.actions_remaining,
            "turn_advanced": action_result.get("turn_advanced", False),
            "new_turn": action_result.get("new_turn")
        }

        # EXPLICIT: For pending_objection (Phase M), ensure cost shows 0
        # AP is consumed when player responds, not when objection triggers
        if result.get("pending_objection"):
            result["action_info"]["cost"] = 0

        result["action_summary"] = world.get_action_summary()

        # Jealousy v3.2 (spec §7): ANY successful player order to a marshal
        # warned of an impending autonomous attack calls the attack off for
        # this cycle (the jealousy itself persists). Skips the autonomous
        # re-issue itself (_jealousy_autonomous) and objection waits.
        # PT-F5: an order that REACHED him stands him down — including one
        # he objected to. The `pending_objection` exclusion meant the
        # marshal most likely to be warned (aggressive, jealous, and so
        # the likeliest to object) was the one the stand-down could not
        # reach. A REFUSED order still does not count, and the warning's
        # copy no longer promises that it does: nothing reached him.
        if (is_player_action and marshal_name
                and not command.get("_jealousy_autonomous")
                and (result.get("success")
                     or result.get("pending_objection"))):
            _warned_marshal = world.get_marshal(marshal_name)
            if _warned_marshal is not None:
                from backend.game_logic.jealousy import (
                    cancel_autonomous_warning_on_order,
                )
                _stand_down = cancel_autonomous_warning_on_order(
                    world, _warned_marshal)
                if _stand_down:
                    result["message"] = (result.get("message", "")
                                         + "\n" + _stand_down)

        # FIX: Prepend mild objection message if there was one.
        # Creative audit July 19 2026: the two strings were butted together with
        # no separator, so the player read "Massena bristles at the retreat order
        # but obeys.Massena retreats from Milan". The mild lines all end in a
        # full stop, so a single space is the right join.
        if mild_message and result.get("success"):
            _rest = result.get("message", "")
            result["message"] = (f"{mild_message} {_rest}".rstrip()
                                 if _rest else mild_message)
            result["mild_objection"] = True

        # CR-6 / S5-D1: a bare "attack" rewritten to a named attack carries its
        # auto-pick provenance. Tag events so the UI still marks them
        # auto-assigned, and prepend the selection note to a RESOLVED battle
        # only — a muster/objection interrupt already names the marshal in its
        # own copy (an objection returns earlier and never reaches here).
        if command.get("_auto_assigned") and isinstance(result, dict):
            for _ev in (result.get("events") or []):
                if isinstance(_ev, dict):
                    _ev["auto_assigned"] = True
            _expl = command.get("_auto_assign_explanation")
            if (_expl and result.get("message")
                    and not result.get("requires_input")
                    and not result.get("pending_glorious_charge")
                    and result.get("state") not in (
                        "awaiting_player_choice", "awaiting_clarification")):
                result["message"] = _expl + result["message"]

        # ESP-EV-4 disclosure (July 18, 2026 adversarial review). The player
        # named something specific, it grounded nothing, and the ENGINE picked
        # the nearest visible enemy instead. Refusing a delegation like that was
        # a regression — the words a player might use to describe a foe are not
        # enumerable — so the order proceeds and the substitution is DISCLOSED
        # rather than made silently. Same prepend shape and same suppression set
        # as the _auto_assigned note above: an interrupt or clarification
        # already owns its copy.
        _disclosure = command.get("_target_disclosure")
        if (_disclosure and isinstance(result, dict) and result.get("message")
                and not result.get("requires_input")
                and not result.get("pending_glorious_charge")
                and result.get("state") not in (
                    "awaiting_player_choice", "awaiting_clarification")):
            result["message"] = _disclosure + "\n\n" + result["message"]

        # Prepend square-break notification if auto-break fired (Session 67 fix)
        if self._pending_square_break_msg and result.get("success") and result.get("message"):
            result["message"] = self._pending_square_break_msg + "\n" + result["message"]
            self._pending_square_break_msg = ""  # Consume

        # ════════════════════════════════════════════════════════════
        # AUTO-END TURN: When actions exhausted, call end_turn properly
        # This ensures enemy AI processes its turn (was being skipped before!)
        # Must mirror _execute_end_turn() data capture — see P0-1/2/3 audit.
        # ════════════════════════════════════════════════════════════
        should_auto_end_turn = action_result.get("should_end_turn", False) and is_player_action
        _defer_notice = self._auto_end_turn_defer_notice(world) if should_auto_end_turn else ""
        if _defer_notice:
            if result.get("message"):
                result["message"] = f"{result['message']} {_defer_notice}"
            else:
                result["message"] = _defer_notice
            should_auto_end_turn = False

        if should_auto_end_turn:
            from backend.game_logic.turn_manager import TurnManager

            # Capture data BEFORE advance_turn() clears it (same as _execute_end_turn)
            saved_mild_concerns = [c.copy() for c in world.mild_concerns_this_turn]
            saved_gold_spent = world.gold_spent_this_turn.copy()

            # Mirror _execute_end_turn's F6/PT-C4 measurement window (Aug 2026
            # health-check audit): snapshot the treasury and open the materiel
            # window BEFORE turn processing, so this banner's Net is the TRUE
            # measured change with an `Other` residual — not a partial
            # component sum that omitted trade/tribute/treaty/admin (it
            # understated Net by 605g at the 1805 boot).
            treasury_before_turn = world.nation_gold.get(world.player_nation, 0)
            world.materiel_spent_this_turn = {}

            turn_manager = TurnManager(world, executor=self)
            turn_result = turn_manager.end_turn(game_state)

            # C3: Stamp that auto-advance processed this turn.
            # Blocks a subsequent "end turn" command from double-advancing.
            # Cleared when any non-end-turn action is taken on the new turn.
            world._auto_advanced_to_turn = world.current_turn

            # Update result with turn end info
            result["action_info"]["turn_advanced"] = True
            result["action_info"]["new_turn"] = turn_result.get("next_turn")

            # Add enemy phase results to the response (popup dialog, no terminal text)
            if turn_result.get("enemy_phase"):
                result["enemy_phase"] = turn_result["enemy_phase"]

            # Tactical events — absorbed into Morning Dispatch's TURN EVENTS section
            tactical_events = turn_result.get("tactical_events", [])
            # FINAL-7: Filter by fog (auto-advance path)
            tactical_events = _filter_tactical_events_by_fog(tactical_events, world)
            if tactical_events:
                result["tactical_events"] = tactical_events
                # Hoist battle_report from tactical events (auto-charge) to result level
                for te in tactical_events:
                    if te.get("battle_report"):
                        result["battle_report"] = te["battle_report"]
                        break
                # WO-41 §6b: this path hoisted battle_report and never the
                # redemption, unlike its end-turn sibling — a last-AP turn
                # advance that tripped a cavalry/fortify redemption latched
                # the marshal and dropped the audience with no save involved.
                # Same shared rule; main.py stamps `state` at the boundary.
                from backend.commands.disobedience import hoist_tactical_redemption
                _auto_redemption = hoist_tactical_redemption(tactical_events)
                if _auto_redemption:
                    result["redemption_event"] = _auto_redemption

            # Add strategic reports — CRITICAL: without this, strategic popups
            # (hold battles, movement progress) never appear in Godot when the
            # turn auto-advances from actions being exhausted.
            if turn_result.get("strategic_reports"):
                result["strategic_reports"] = turn_result["strategic_reports"]
            # PT-F1: the auto-advance mirror had the identical hole — it
            # reads a fixed key set off `turn_result` and this was not in
            # it, so a player whose last AP ends the turn would have lost
            # the battle just as thoroughly.
            if turn_result.get("jealousy_attacks"):
                result["jealousy_attacks"] = turn_result["jealousy_attacks"]

            # Add Independent Command Report (Phase 2.5) — was missing on auto-advance
            if turn_result.get("show_independent_command_report"):
                result["show_independent_command_report"] = True
                result["independent_command_report"] = turn_result.get("independent_command_report", [])

            # Include saved mild concerns (captured before advance_turn cleared them)
            if saved_mild_concerns:
                result["mild_concerns"] = saved_mild_concerns

            # Build turn_end financial event (same as _execute_end_turn)
            nation = world.player_nation
            # EB review [1]: prefer the APPLIED income-phase result (the
            # transient _advance_turn_internal cache) — recomputing here
            # read the POST-income treasury, so the Charges of Empire
            # figure shown was never the one charged.
            income_data = (getattr(world, "_income_phase_results", None) or {}).get(nation) \
                or world.calculate_turn_income(nation)
            # Prefer the APPLIED upkeep breakdown (rides the phase result) —
            # a recompute reads post-_update_bankruptcy state, off by half
            # the upkeep on a bankruptcy-flip turn (Aug 2026 audit).
            upkeep_data = income_data.get("upkeep_data") \
                or world.calculate_turn_upkeep(nation)
            treasury = world.nation_gold.get(nation, 0)
            income_val = income_data["income"]
            upkeep_val = upkeep_data["total"]
            # ES-2 (S6): occupation is its own Net component (income is gross)
            occupation_val = int(income_data.get("occupation", 0))
            # EC-W1/EC-W2 (review finding #6a): the war-coupling components
            # were missing from this auto-advance banner's net — it overstated
            # Net on every wartime last-AP advance. Infrastructure had the
            # same pre-existing gap; all three folded in.
            contributions_val = int(income_data.get("contributions", 0))
            # EB-1: the Charges of Empire (absorbs EC-W2's War Effort)
            state_charges_val = int(income_data.get("state_charges", 0))
            # EB-5a/EB-2: the positive components ride the banner too
            requisitions_val = int(income_data.get("requisitions", 0))
            overseas_val = int(income_data.get("overseas", 0))
            infrastructure_val = int(income_data.get("infrastructure", 0))
            # EB review [2]: the Admiralty bill was the one applied-net
            # component this banner's formula omitted (its meta sibling
            # reconciles it) — the banner overstated Net by 90g on every
            # wartime auto-advance at the naval boot.
            admiralty_val = int(income_data.get("admiralty", 0))
            # ES-7 (S7): estate redirect is its own Net component too
            dotation_val = int(income_data.get("dotation_skim", 0))
            # ES-7 second pass (§0.6.8): the rente bill
            rente_val = int(income_data.get("rente_cost", 0))
            spent_val = saved_gold_spent.get(nation, 0)
            # DEF-5 naval: the blockade's trade suspension — its meta sibling
            # carries it; this banner omitted it (Aug 2026 audit).
            blockade_val = 0
            if getattr(world, "fleets", None):
                from backend.game_logic.naval import blockade_trade_loss
                blockade_val = int(blockade_trade_loss(world).get(nation, 0))
            # PT-C4: the Butcher's Bill charged inside this window.
            materiel_val = int(getattr(world, "materiel_spent_this_turn", {})
                               .get(nation, 0))
            # F6 formula (Aug 2026 health-check audit — mirrors
            # _execute_end_turn): Net is the MEASURED treasury change, and
            # `Other` is the reconciling residual (trade, tribute, treaty
            # clauses, admin bonus). The old partial component sum was
            # neither the measured delta nor the ledger's Net.
            net_val = treasury - treasury_before_turn
            other_val = net_val - (income_val + requisitions_val + overseas_val
                                   - occupation_val - contributions_val
                                   - state_charges_val - dotation_val
                                   - rente_val - infrastructure_val
                                   - admiralty_val - blockade_val - upkeep_val
                                   - materiel_val)
            bk_turns = int(world.nation_bankruptcy_turns.get(nation, 0))
            turn_end_event = {
                "type": "turn_end",
                "old_turn": int(turn_result.get("turn_ended", world.current_turn - 1)),
                "new_turn": int(turn_result.get("next_turn", world.current_turn)),
                "income": int(income_val),
                "occupation": int(occupation_val),
                "contributions": int(contributions_val),
                "requisitions": int(requisitions_val),
                "overseas": int(overseas_val),
                "state_charges": int(state_charges_val),
                "dotation_skim": int(dotation_val),
                "rente_cost": int(rente_val),
                "admiralty": int(admiralty_val),
                "blockade": int(blockade_val),
                "materiel": int(materiel_val),
                "infrastructure": int(infrastructure_val),
                "upkeep": int(upkeep_val),
                "other": int(other_val),
                "spent": int(spent_val),
                "net": int(net_val),
                "treasury": int(treasury),
                "bankruptcy_turns": bk_turns,
            }
            existing_events = result.get("events", [])
            result["events"] = [turn_end_event] + existing_events + turn_result.get("events", [])

            # Append financial summary to message
            net_sign = "+" if net_val >= 0 else ""
            spent_str = f" | Spent: {spent_val}g" if spent_val > 0 else ""
            occupation_str = f" | Occupation: -{occupation_val}g" if occupation_val > 0 else ""
            contributions_str = f" | Contributions: -{contributions_val}g" if contributions_val > 0 else ""
            requisitions_str = f" | Requisitions: +{requisitions_val}g" if requisitions_val > 0 else ""
            overseas_str = f" | Overseas: +{overseas_val}g" if overseas_val > 0 else ""
            state_charges_str = f" | Charges of Empire: -{state_charges_val}g" if state_charges_val > 0 else ""
            infrastructure_str = f" | Infrastructure: -{infrastructure_val}g" if infrastructure_val > 0 else ""
            admiralty_str = f" | Admiralty: -{admiralty_val}g" if admiralty_val > 0 else ""
            dotation_str = f" | Dotations: -{dotation_val}g" if dotation_val > 0 else ""
            rente_str = f" | Rentes: -{rente_val}g" if rente_val > 0 else ""
            blockade_str = f" | Blockade: -{blockade_val}g" if blockade_val > 0 else ""
            materiel_str = f" | Materiel: -{materiel_val}g" if materiel_val > 0 else ""
            other_str = ""
            if other_val != 0:
                other_str = f" | Other: {'+' if other_val >= 0 else ''}{other_val}g"
            # ES-3 (S5): surface the over-limit surcharge inside the upkeep figure
            surcharge_val = int(upkeep_data.get("surcharge", 0))
            surcharge_str = f" (incl. {surcharge_val}g over-limit)" if surcharge_val > 0 else ""
            result["message"] = result.get("message", "") + f"\n\nIncome: {income_val}g{requisitions_str}{overseas_str}{occupation_str}{contributions_str}{state_charges_str}{dotation_str}{rente_str}{infrastructure_str}{admiralty_str}{blockade_str}{materiel_str}{other_str} | Upkeep: -{upkeep_val}g{surcharge_str} | Net: {net_sign}{net_val}g{spent_str} | Treasury: {treasury:,}g"
            if bk_turns > 0:
                result["message"] += f"\nWARNING: Bankrupt for {bk_turns} turn{'s' if bk_turns > 1 else ''}!"

            # Phase 6.2.F: Occupation may complete during turn resolution
            if world.pending_capture_choice:
                result["pending_capture_choice"] = True
                result["capture_data"] = world.pending_capture_choice

            # Check victory/defeat
            if turn_result.get("victory_check", {}).get("game_over"):
                result["game_over"] = True
                result["victory"] = turn_result["victory_check"].get("result")

            # Morning Dispatch — Berthier's turn-start briefing (Phase 6.5, auto-advance path)
            from backend.game_logic.dispatch import build_morning_dispatch
            lapsed_offers = turn_result.get("lapsed_offers", [])
            if lapsed_offers:
                result["lapsed_offers"] = lapsed_offers
            result["morning_dispatch"] = build_morning_dispatch(
                world, tactical_events, lapsed_offers=lapsed_offers
            )

            # Autosave at start of new turn (auto-advance path, mirrors _execute_end_turn)
            from backend.save_manager import autosave
            autosave_result = autosave(world)
            if not autosave_result["success"]:
                print(f"Autosave warning: {autosave_result['message']}")

        return result

    def _execute_specific(self, command: Dict, game_state: Dict) -> Dict:
        """Execute a specific order (marshal and action both specified)."""
        marshal_name = command.get("marshal")
        action = command.get("action")
        # PF-3: an automated per-hop strategic march step carries this flag; the
        # move-capture auto-secures instead of popping a per-hop popup.
        is_strategic_execution = command.get("_strategic_execution", False)
        target = command.get("target")

        world: WorldState = game_state.get("world")

        if not world:
            return {
                "success": False,
                "message": "Error: No world state available"
            }

        # Use fuzzy matching for marshal lookup
        marshal, error = self._fuzzy_match_marshal(marshal_name, world)
        if error:
            return error

        # Handle different actions
        if action == "attack":
            # W6-4: the command dict rides along so the muster-preview gate
            # can distinguish a direct player attack from AI/strategic/
            # confirmed re-issues (every other caller passes command=None).
            # ESP-EV-4: `execute` stashed the raw text on this dict, so the
            # guessed-target guard can tell a typed name from a live-LLM
            # substitution.
            return self._combat._execute_attack(
                marshal, target, world, game_state, command=command)
        elif action == "defend":
            return self._tactical._execute_defend(marshal, world, game_state)
        elif action == "hold":
            # V2-58: "hold" routes to defend (tactical). Strategic HOLD (2 AP)
            # is handled by strategic parser. Grouchy Immovable is in strategic HOLD path.
            return self._tactical._execute_defend(marshal, world, game_state)
        elif action == "wait":
            # Wait is a free action - marshal passes turn
            return self._tactical._execute_wait(marshal, world, game_state)
        elif action == "move":
            # ESP-EV-4 family: the raw typed order rides through so a
            # substituted destination is NAMED (never silently honored).
            return self._movement._execute_move(
                marshal, target, world, game_state,
                raw_input=(command.get("_raw_input")
                           if isinstance(command, dict) else None),
                strategic_execution=is_strategic_execution)
        elif action == "scout":
            return self._movement._execute_scout(marshal, target, world, game_state)
        elif action == "retreat":
            # W6-1 (BUG-CA-2): a stated destination ("retreat to Rhineland")
            # rides through — honored when legal, named when substituted.
            return self._movement._execute_retreat_action(
                marshal, world, game_state, target=target)
        elif action == "drill":
            return self._tactical._execute_drill(command, game_state)
        elif action == "fortify":
            return self._tactical._execute_fortify(command, game_state)
        elif action == "unfortify":
            return self._tactical._execute_unfortify(command, game_state)
        elif action == "form_square":
            return self._combat._execute_form_square(command, game_state)
        elif action == "break_square":
            return self._combat._execute_break_square(command, game_state)
        elif action == "stance_change":
            return self._tactical._execute_stance_change(command, game_state)
        elif action == "cheat":
            return self._meta._execute_cheat(command, game_state)
        elif action == "debug":
            return self._meta._execute_debug(command, game_state)
        else:
            return {
                "success": False,
                "message": f"Unknown action: {action}"
            }

    # Economy/garrison/building/repair delegated to EconomyExecutor (R13A)
    # Tactical state actions (drill/fortify/unfortify/square/stance) delegated to TacticalExecutor (R13A)
    # Stance/restrain delegated to TacticalExecutor (R13A)
    # _execute_cancel delegated to StrategicExecutor (R11)
    # Movement/scout/retreat delegated to MovementExecutor (R13B)
    # _handle_strategic_objection_from_endpoint delegated to StrategicExecutor (R11)

    # Capture choice delegated to CaptureExecutor (R13A)
    # Diplomatic methods delegated to DiplomaticExecutor (R11)
    # Objection/defiance handling delegated to MetaExecutor (R13B)
    # Cheat commands delegated to MetaExecutor (R13B)
    # _execute_end_turn, _execute_status, _execute_help delegated to MetaExecutor (R13B)
    # _execute_debug delegated to MetaExecutor (R13B)

