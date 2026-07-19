"""July 18, 2026 playtest sweep — the "give them hell" command family.

REPORTED (verbatim): *"when i say ney give them hell he doesnt do anything it
just give options then i said ney gives charlkes hell and a popup appeared."*

Both halves were real, and they were the SAME defect seen from two angles:

  (a) "give ... hell" was unrecognized by every parse layer — not in the fast
      parser's keyword chain, not in the delegation verb allowlist, not in the
      golden corpus. It fell to the live LLM, which freelanced.
  (b) The two phrasings then diverged at the ESP-EV-4 guessed-target guard,
      which sat AFTER the range-check block. The range check returns early with
      a strategic PURSUE, so a guessed target that happened to be out of range
      marched off unguarded and opened a bad-odds popup over an enemy the
      player had never named, while a target that grounded nothing hit the
      guard and got a flat terminal refusal that offered nothing to answer.

The investigation swept the same two families for siblings. This file pins the
whole set. Sibling UI-side fixes are pinned in test_ui_visual_foundation.py.
"""

import os
import re
from pathlib import Path

import pytest

from backend.ai.attack_vocabulary import (
    BATTLE_VERBS, IDIOM_FILLER_WORDS, mentions_attack, targeting_anchor_words,
)
from backend.ai.llm_client import LLMClient
from backend.ai.parser_eval import build_world
from backend.commands.clarification import interpret_clarification_answer
from backend.commands.context_carryover import resolve_context_references
from backend.commands.executor import CommandExecutor
from backend.commands.parser import CommandParser


@pytest.fixture(scope="module")
def mock_client():
    return LLMClient()


@pytest.fixture(scope="module")
def parser():
    return CommandParser(use_real_llm=False)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _action(mock_client, text):
    return mock_client._parse_with_mock(text, None).action


# ═══════════════ 1. THE REPORTED IDIOM (and its whole family) ═══════════════


class TestColloquialAttackVocabulary:
    """Every idiomatic "destroy the enemy" phrasing a player plausibly types
    used to resolve to action="unknown" and produce a Berthier shrug."""

    @pytest.mark.parametrize("utterance", [
        "Ney, give them hell",          # the reported input
        "Ney, gives Charles hell",      # the reported second input
        "Ney, giving them hell",
        "Ney, crush Mack",
        "Ney, smash them",
        "Ney, destroy the Austrians",
        "Ney, engage Mack",
        "Ney, assault Vienna",
        "Ney, storm the heights",
        "Ney, rout them",
        "Ney, defeat Mack",
        "Ney, ambush them",
        "Soult, give battle",           # copy the game itself prints
        "bring Mack to battle",
        "Ney, no quarter",
        "Ney, show them no mercy",
        "Ney, put them to the sword",
        "Ney, wipe them out",
        "Ney, cut them down",
        "Ney, have at them",
        "Ney, fall upon Mack",
        "Ney, finish him",
        "Ney, take the fight to Mack",
    ])
    def test_idiom_resolves_to_attack(self, mock_client, utterance):
        assert _action(mock_client, utterance) == "attack"

    @pytest.mark.parametrize("utterance", [
        "Ney, capture Vienna",
        "Ney, seize Vienna",
        "Ney, occupy Vienna",           # the one that always worked
    ])
    def test_capture_verbs_resolve_to_attack(self, mock_client, utterance):
        assert _action(mock_client, utterance) == "attack"

    @pytest.mark.parametrize("utterance,expected", [
        # DELIBERATE EXCLUSIONS — each is load-bearing, see attack_vocabulary.
        ("the warden watches", "unknown"),          # corpus negative pin
        ("Grouchy, support Ney until battle won", "move"),   # SUPPORT family
        ("secure and hold vienna", "hold"),         # HOLD family
        ("give them autonomy", "change_autonomy"),  # vassal family
        ("Ney, march to Paris", "move"),            # move family
        ("Ney, advance to Vienna", "move"),
        ("Ney, take Vienna", "unknown"),            # "take" stays excluded
    ])
    def test_deliberate_exclusions_hold(self, mock_client, utterance, expected):
        assert _action(mock_client, utterance) == expected

    def test_ride_down_needs_an_object_to_be_an_attack(self, mock_client):
        """"ride them down" is an attack; "ride down to Naples" is a march.
        The idiom is object-anchored so the two cannot collide."""
        assert _action(mock_client, "Ney, ride them down") == "attack"
        assert _action(mock_client, "Ney, ride down to Naples") != "attack"

    def test_pursue_family_keeps_its_own_branch(self, mock_client):
        """The new branch sits AFTER the pursue block, so the strategic PURSUE
        upgrade and its until-destroyed condition are untouched."""
        result = mock_client._parse_with_mock(
            "Grouchy, pursue Wellington until destroyed", None)
        assert result.action == "attack"
        assert "destroy" in "pursue Wellington until destroyed"  # the collision


class TestSilentlyWrongActions:
    """Worse than a shrug: phrasings that hit an unrelated substring keyword
    and returned confidence 0.9 — above the LLM-fallback gate, so live mode
    could never correct them. The marshal did the wrong thing and spent the AP."""

    @pytest.mark.parametrize("utterance", [
        "Ney, cover the retreat",
        "Ney, screen the withdrawal",
        "Ney, protect the rear",
        "Ney, cover our retreat",
    ])
    def test_screening_no_longer_orders_a_retreat(self, mock_client, utterance):
        assert _action(mock_client, utterance) != "retreat"

    def test_a_real_retreat_still_retreats(self, mock_client):
        assert _action(mock_client, "Ney, retreat") == "retreat"
        assert _action(mock_client, "Ney, fall back") == "retreat"

    @pytest.mark.parametrize("utterance", [
        "Ney, fix bayonets",
        "Ney, restore order in Vienna",
        "Ney, restore discipline",
        "Ney, restore morale",
    ])
    def test_abstract_restore_is_not_masonry(self, mock_client, utterance):
        assert _action(mock_client, utterance) != "repair"

    def test_a_real_repair_still_repairs(self, mock_client):
        assert _action(mock_client, "Ney, repair the fort at Ulm") == "repair"
        assert _action(mock_client, "Ney, restore the walls at Ulm") == "repair"


class TestMovementPhrasings:
    """"head FOR Vienna" shrugged while "head TO Vienna" marched — a one-word
    difference the player cannot see is significant."""

    @pytest.mark.parametrize("utterance", [
        "Ney, head for Vienna",
        "Ney, ride for Vienna",
        "Ney, set off for Vienna",
        "Ney, set out for Vienna",
        "Ney, make haste to Vienna",
        "Ney, take your corps to Ulm",
        "Ney, bring your men to Vienna",
    ])
    def test_destination_phrasings_move(self, mock_client, utterance):
        assert _action(mock_client, utterance) == "move"

    def test_support_family_is_not_shadowed(self, mock_client):
        """The possessive-object pattern must not swallow the reinforce family."""
        assert _action(mock_client, "send reinforcements to Davout") == "move"
        assert _action(mock_client, "Grouchy, support Ney") == "move"


class TestScoutVerbsThePrintedCopyUses:
    def test_observe_parses(self, mock_client):
        assert _action(mock_client, "Soult, observe Mack") == "scout"

    def test_bare_watch_is_not_a_scout(self, mock_client):
        """A bare "watch" would swallow "build a watchtower" and the corpus's
        negative pin "the warden watches"."""
        assert _action(mock_client, "build a watchtower in Bavaria") == "build"
        assert _action(mock_client, "the warden watches") == "unknown"


# ═══════════════ 2. THE VOCABULARY IS A SINGLE SOURCE ══════════════════════


class TestVocabularySingleSource:
    def test_anchor_set_is_a_superset_of_the_routed_verbs(self):
        """The regression that made the whole family invisible: the CR-4 anchor
        set listed smash/crush/destroy/engage/assault/storm/rout, none of which
        the parser could route. So "Ney, crush him" resolved the pronoun
        perfectly and STILL shrugged. Deriving both from one vocabulary makes
        this true by construction."""
        anchors = targeting_anchor_words()
        for verb in BATTLE_VERBS:
            assert verb in anchors, f"{verb} routes but cannot anchor a pronoun"

    def test_every_battle_verb_actually_routes(self, mock_client):
        for verb in BATTLE_VERBS:
            assert mentions_attack(f"ney, {verb} mack"), verb

    def test_resolved_pronoun_command_then_parses(self, mock_client):
        """End-to-end: carryover rewrites the pronoun, and the rewritten
        command is now something the parser can act on."""
        world = build_world("legacy")
        world.command_history = [{
            "action": "attack", "marshal": "Ney", "target": "Wellington",
            "turn": 1,
        }]
        resolved = resolve_context_references("Ney, crush him", world)
        assert resolved["kind"] == "rewrite"
        assert "Wellington" in resolved["command"]
        assert _action(mock_client, resolved["command"]) == "attack"


class TestGiveIsDitransitive:
    """"give" cannot be a bare pronoun anchor: in "give them hell" the pronoun
    is the enemy, but in "give them autonomy" it is a vassal NATION."""

    def _world_with_history(self):
        world = build_world("legacy")
        world.command_history = [{
            "action": "attack", "marshal": "Ney", "target": "Wellington",
            "turn": 1,
        }]
        return world

    def test_combat_idiom_resolves_the_pronoun(self):
        resolved = resolve_context_references("Ney, give them hell",
                                             self._world_with_history())
        assert resolved["kind"] == "rewrite"
        assert "Wellington" in resolved["command"]

    @pytest.mark.parametrize("utterance", [
        "give them autonomy",
        "give them more autonomy",
        "give them back their land",
        "give them an ultimatum",
    ])
    def test_vassal_senses_are_left_alone(self, utterance):
        """An enemy marshal name injected into the vassal slot would corrupt the
        order UPSTREAM of the parser guard that exists to prevent exactly that."""
        resolved = resolve_context_references(utterance, self._world_with_history())
        assert "Wellington" not in str(resolved.get("command", utterance))


# ═══════════════ 3. NO FABRICATED PROVINCES ════════════════════════════════


class TestIdiomWordsNeverBecomeProvinces:
    """"hell" auto-corrected into the province *Algiers*, which then rode into
    Berthier's live recovery prompt as a fact the Emperor had stated — so his
    suggested rephrasing could name a province 1,500km from the marshal."""

    @pytest.mark.parametrize("world_name", ["legacy", "1805"])
    def test_give_them_hell_invents_no_target(self, parser, world_name):
        world = build_world(world_name)
        result = parser.parse("Ney, give them hell", None, world)
        target = (result.get("command") or {}).get("target")
        assert target is None or target in world.regions or target in world.marshals, (
            f"fabricated target {target!r} from a semantically empty word")

    def test_unparseable_input_reports_no_partial_target(self, parser):
        """A failed parse has no action to hang a target on; scanning anyway
        fabricated the province that was fed to Berthier as fact."""
        world = build_world("legacy")
        result = parser.parse("Ney, make it so", None, world)
        assert not result.get("success")
        assert not result.get("partial_target")

    def test_idiom_filler_covers_the_reported_word(self):
        assert "hell" in IDIOM_FILLER_WORDS


# ═══════════════ 4. THE GUESSED-TARGET GUARD ═══════════════════════════════


class TestGuardRunsBeforeTheLethalBranches:
    """The reported divergence. The guard sat AFTER the range-check block,
    which returns early with a strategic PURSUE — so an out-of-range guessed
    target marched off unguarded."""

    def _world(self):
        world = build_world("legacy")
        world.opening_attack_guidance_shown = True
        return world

    def test_out_of_range_guess_is_caught_not_converted_to_pursue(self):
        world = self._world()
        executor = CommandExecutor()
        ney = world.marshals["Ney"]
        # Pick an enemy the marshal cannot reach this turn, so the range check
        # would previously have claimed the order first.
        distant = next(
            (e for e in world.get_enemy_marshals()
             if e.strength > 0 and e.location != ney.location), None)
        assert distant is not None
        result = executor.execute({"command": {
            "marshal": "Ney", "action": "attack", "target": distant.name,
            "type": "specific",
            "_raw_input": "Ney, attack Venetia",
        }}, {"world": world})
        # Must NOT have become a strategic order behind the player's back.
        assert result.get("strategic_type") != "PURSUE"
        assert getattr(ney, "strategic_order", None) is None
        assert "will not charge at a guess" in str(result.get("message", ""))

    def test_unresolvable_name_is_disclosed_not_silently_substituted(self):
        """Found by the July 18, 2026 LIVE probe, then CORRECTED by the
        pre-commit adversarial review — both halves matter.

        The probe: "Ney, give Charles hell" and "Ney, attack Venetia" both
        MUSTERED AGAINST MACK. Neither name resolved (Charles was fogged;
        Venetia is not a province), so the parse handed down target=None,
        auto-targeting picked the nearest enemy, and the substitution was
        silent.

        The first cut made that ASK. The review proved that wrong: the set of
        words a player may use to describe a foe is not enumerable, so a guard
        keyed on a filler denylist bounces ordinary delegations — "attack the
        weakest enemy", "attack the enemy vanguard", "attack the British army"
        would all have hit a popup.

        The contract is therefore DISCLOSURE, not refusal: the order proceeds
        and names the foe it chose. No legitimate order is ever blocked, and
        no substitution is ever silent.
        """
        world = self._world()
        executor = CommandExecutor()
        result = executor.execute({"command": {
            "marshal": "Ney", "action": "attack", "target": None,
            "type": "specific",
            "_raw_input": "Ney, attack Venetia",
        }}, {"world": world})
        assert result.get("state") != "awaiting_clarification", (
            "an engine-picked target must not be refused — that bounces "
            "ordinary delegations")
        assert "named no foe our maps know" in str(result.get("message", "")), (
            "the substitution must be disclosed, never silent")

    @pytest.mark.parametrize("raw", [
        "Ney, attack the weakest enemy",
        "Ney, attack the enemy vanguard",
        "Ney, attack the British army",
        "Ney, attack the enemy in front of you",
        "Ney, attack the rest",
        "Ney, attack anyone nearby",
    ])
    def test_descriptive_delegations_are_never_blocked(self, raw):
        """The regression the review caught before it shipped. None of these
        names a foe our maps know, and none of their adjectives is on any
        filler list — but every one of them is an ordinary delegation and must
        engage rather than bounce to a popup."""
        world = self._world()
        executor = CommandExecutor()
        result = executor.execute({"command": {
            "marshal": "Ney", "action": "attack", "target": None,
            "type": "specific", "_raw_input": raw,
        }}, {"world": world})
        assert result.get("state") != "awaiting_clarification", raw
        assert "will not charge at a guess" not in str(result.get("message", "")), raw

    def test_parser_substitution_still_asks(self):
        """The ORIGINAL ESP-EV-4 case is unchanged: when the PARSER produced a
        concrete foe and the player's words ground none of it, that is one real
        enemy silently swapped for another, and it must still ask."""
        world = self._world()
        executor = CommandExecutor()
        enemy = next(e for e in world.get_enemy_marshals() if e.strength > 0)
        result = executor.execute({"command": {
            "marshal": "Ney", "action": "attack", "target": enemy.name,
            "type": "specific", "_raw_input": "Ney, attack Venetia",
        }}, {"world": world})
        assert result.get("state") == "awaiting_clarification"
        assert result.get("clarification_kind") == "attack_target"

    def test_clarification_labels_carry_no_internal_keys(self):
        """R7: the option LABEL is player-facing copy. `target` and `command`
        stay raw so the reissue resolves; both forms ride `aliases` so a player
        who types back what he READ resolves by design, not by luck."""
        world = self._world()
        executor = CommandExecutor()
        enemy = next(e for e in world.get_enemy_marshals() if e.strength > 0)
        result = executor.execute({"command": {
            "marshal": "Ney", "action": "attack", "target": enemy.name,
            "type": "specific", "_raw_input": "Ney, attack Venetia",
        }}, {"world": world})
        for option in result["options"]:
            assert not re.search(r"[a-z][A-Z]", option["label"]), (
                f"camelCase key leaked into player copy: {option['label']!r}")
            assert option["label"] in " ".join(option["aliases"]) or any(
                option["label"].startswith(a) for a in option["aliases"]), (
                "the printed label must be answerable as typed")

    def test_guard_still_stands_down_on_a_delegated_target(self):
        """Bare/auto attacks resolved their target deterministically — the game
        picked it, so it is never a guess (the CR-6 exemption)."""
        world = self._world()
        executor = CommandExecutor()
        result = executor.execute({"command": {
            "marshal": "Ney", "action": "attack", "target": None,
            "type": "specific",
            "_raw_input": "Ney, attack the nearest enemy",
        }}, {"world": world})
        assert "will not charge at a guess" not in str(result.get("message", ""))

    def test_idiom_reads_as_delegation_not_as_a_guess(self):
        """"Ney, give them hell" names no foe, so it is a DELEGATED attack —
        the guard must not refuse it as though "hell" were a guessed province."""
        world = self._world()
        executor = CommandExecutor()
        ney = world.marshals["Ney"]
        nearby = next((e for e in world.get_enemy_marshals() if e.strength > 0), None)
        assert nearby is not None
        result = executor.execute({"command": {
            "marshal": "Ney", "action": "attack", "target": nearby.name,
            "type": "specific",
            "_raw_input": "Ney, give them hell",
        }}, {"world": world})
        assert "will not charge at a guess" not in str(result.get("message", ""))
        assert ney is world.marshals["Ney"]


class TestGuardRefusalIsAnswerable:
    """The other half of the report: the refusal printed a list and offered
    nothing to click or type back, while the phrasing that happened to ground a
    name opened a popup. Same intent, two surfaces, one of them a dead end."""

    def test_refusal_is_a_clarification_with_reissue_commands(self):
        world = build_world("legacy")
        world.opening_attack_guidance_shown = True
        executor = CommandExecutor()
        enemy = next(e for e in world.get_enemy_marshals() if e.strength > 0)
        result = executor.execute({"command": {
            "marshal": "Ney", "action": "attack", "target": enemy.name,
            "type": "specific",
            "_raw_input": "Ney, attack Venetia",
        }}, {"world": world})
        assert result["state"] == "awaiting_clarification"
        assert result["clarification_kind"] == "attack_target"
        assert result["options"]
        for option in result["options"]:
            assert option["command"].startswith("Ney, attack ")

    def test_printed_choice_resolves_when_typed_back(self):
        world = build_world("legacy")
        world.opening_attack_guidance_shown = True
        executor = CommandExecutor()
        enemy = next(e for e in world.get_enemy_marshals() if e.strength > 0)
        result = executor.execute({"command": {
            "marshal": "Ney", "action": "attack", "target": enemy.name,
            "type": "specific",
            "_raw_input": "Ney, attack Venetia",
        }}, {"world": world})
        answer = interpret_clarification_answer(
            {"options": result["options"]}, result["options"][0]["target"])
        assert answer.get("command", "").startswith("Ney, attack ")


# ═══════════════ 5. DELEGATION LAST NAMES ══════════════════════════════════


class TestDelegationResolvesShortNames:
    """"Ney, deal with Charles" lost the delegation entirely (a generic
    Berthier shrug) while "deal with ArchdukeCharles" produced the correct
    CR-5 ASK — same marshal, same verb, same enemy, two surfaces."""

    def test_last_name_resolves(self):
        from backend.commands.delegation import detect_delegation
        world = build_world("1805")
        charles = world.marshals.get("ArchdukeCharles")
        if charles is None or charles.strength <= 0:
            pytest.skip("scenario has no ArchdukeCharles")
        match = detect_delegation(world, "Ney, deal with Charles")
        assert match is not None
        assert match.target == "ArchdukeCharles"

    def test_full_name_still_wins_over_the_token(self):
        from backend.commands.delegation import detect_delegation
        world = build_world("1805")
        if "ArchdukeCharles" not in world.marshals:
            pytest.skip("scenario has no ArchdukeCharles")
        match = detect_delegation(world, "Ney, deal with Archduke Charles")
        assert match is not None
        assert match.target == "ArchdukeCharles"
        # R7: no camelCase key ever reaches player copy.
        assert "ArchdukeCharles" not in match.target_display

    def test_last_name_resolves_at_the_parse_seam_too(self):
        """Follow-up (same day): fixing the delegation path alone was not
        enough. "Ney, attack Charles" — the same surname, the ordinary attack
        verb — still resolved to NOTHING, and because the idiom now scores 0.9
        the live LLM no longer gets a chance to rescue it. Both seams draw from
        one uniqueness map now."""
        from backend.ai.parser_eval import build_llm_game_state
        from backend.models.intel import FULL

        world = build_world("1805")
        charles = world.marshals.get("ArchdukeCharles")
        if charles is None:
            pytest.skip("scenario has no ArchdukeCharles")
        world.get_region_intel(charles.location).visibility = FULL
        state = build_llm_game_state(world)
        parser_ = CommandParser(use_real_llm=False)
        for utterance in ("Ney, attack Charles", "Ney, give Charles hell"):
            result = parser_.parse(utterance, state, world)
            target = (result.get("command") or {}).get("target")
            assert target == "ArchdukeCharles", f"{utterance!r} -> {target!r}"

    def test_a_title_is_not_a_surname(self):
        """The golden corpus caught this. ArchdukeCharles is FOGGED at the 1805
        boot, which left "archduke" uniquely owned by ArchdukeJohn among the
        VISIBLE enemies — so a first cut that admitted any unique token
        resolved "attack archduke charles" to the WRONG Archduke. Titles
        identify a rank; surnames identify a man."""
        from backend.ai.llm_client import unique_name_tokens

        tokens = unique_name_tokens(["ArchdukeJohn", "Mack", "Brunswick"])
        assert "archduke" not in tokens, (
            "a leading title must never stand in for a man, even when it is "
            "unique among the currently-visible enemies")
        assert tokens.get("john") == "ArchdukeJohn"
        assert tokens.get("brunswick") == "Brunswick"

    def test_shared_surname_is_declined(self):
        from backend.ai.llm_client import unique_name_tokens

        tokens = unique_name_tokens(["ArchdukeCharles", "PrinceCharles", "Mack"])
        assert "charles" not in tokens, (
            "a surname shared by two commanders must resolve to neither")

    def test_ambiguous_token_is_declined_not_guessed(self):
        """"archduke" belongs to more than one Archduke — the matcher must keep
        today's behavior (no match) rather than silently picking one."""
        from backend.commands.delegation import detect_delegation
        world = build_world("1805")
        archdukes = [m for m in world.get_enemy_marshals()
                     if m.strength > 0 and "Archduke" in m.name]
        if len(archdukes) < 2:
            pytest.skip("scenario has fewer than two Archdukes")
        match = detect_delegation(world, "Ney, deal with the archduke")
        assert match is None or match.target in {m.name for m in archdukes}


# ═══════════════ 6. BERTHIER NEVER RECITES INTERNAL IDS ════════════════════


class TestBerthierRecoveryVocabulary:
    def test_mock_template_has_no_raw_action_ids(self, mock_client):
        """The live prompt was fixed for this leak in the F5 pass; the mock
        template was not, so mock mode still printed "attack, break_square,
        build, cancel, change_autonomy, charge" — underscores and all."""
        from backend.ai.prompt_builder import recovery_action_vocabulary
        for style in ("typed", "narrated"):
            vocabulary = recovery_action_vocabulary(style)
            assert vocabulary
            for verb in vocabulary:
                assert "_" not in verb, f"raw internal id leaked: {verb}"

    def test_meta_and_debug_verbs_are_hidden(self):
        from backend.ai.prompt_builder import recovery_action_vocabulary
        vocabulary = " ".join(recovery_action_vocabulary("typed")).lower()
        for hidden in ("cheat", "debug", "unknown"):
            assert hidden not in vocabulary

    def test_recovery_message_leads_with_useful_verbs(self, mock_client):
        message = mock_client._berthier_mock_response(
            "Ney, make it so",
            {"marshals": {"Ney": {}}, "enemies": {"Wellington": {}}},
            {"recognized_marshal": "Ney"},
        )
        assert "break_square" not in message
        assert "change_autonomy" not in message


# ═══════════════ 7. THE CORPUS GATE ════════════════════════════════════════


def test_new_idioms_are_pinned_in_the_golden_corpus():
    """CLAUDE.md new-action checklist step 12 / CR-1: the eval harness is the
    standing regression gate, so the idiom family must be represented in it."""
    import json
    path = os.path.join(os.path.dirname(__file__), "data",
                        "parser_golden_corpus.json")
    with open(path, encoding="utf-8") as handle:
        corpus = json.load(handle)
    utterances = " ".join(e.get("utterance", "") for e in corpus["entries"]).lower()
    for idiom in ("hell", "crush", "capture", "head for", "cover the retreat"):
        assert idiom in utterances, f"corpus has no row for {idiom!r}"


# ═══════════════ 8. THE "generic" TARGET — WHY IT FAILED IN LLM MODE ═══════
#
# Follow-up, July 19, 2026. The fast-parser fix made "give them hell" resolve
# without the LLM — which fixed the symptom but never answered the question
# actually asked: why did it fail IN LIVE MODE?
#
# Probing the live model directly (bypassing the 0.7 gate) showed the LLM was
# RIGHT. It returned action=attack, target="generic", ambiguity 65 — correctly
# saying "attack, but you named no foe I can resolve". It invented nothing.
#
# The break was downstream, and it was a three-layer contract failure:
#   - prompt_builder INSTRUCTS the model to emit "generic" for a vague order
#     ("If you cannot determine the specific region, set target to 'generic'")
#   - PARSE_TOOL advertises it, and _extract_valid_targets BLESSES it
#   - ...and the tactical executor REJECTED it: "Unknown target: generic",
#     "Region 'generic' not found."
#
# The strategic executor had handled the whole sentinel family all along. The
# tactical path never learned. Since vagueness is exactly what sends a command
# to the LLM, EVERY vague live command shared the fault.


class TestGenericTargetSentinel:
    """The sentinel the prompt asks for must not die at the executor."""

    def test_sentinels_normalize_to_none(self):
        from backend.ai.generic_targets import normalize_target
        for sentinel in ("generic", "the enemy", "enemy", "enemies", "them",
                         "whoever", "nearest", "closest", "someone"):
            assert normalize_target(sentinel) is None, sentinel

    def test_real_targets_pass_through(self):
        from backend.ai.generic_targets import normalize_target
        for real in ("Mack", "Vienna", "Swabia", "ArchdukeCharles"):
            assert normalize_target(real) == real

    def test_the_prompt_still_asks_for_the_sentinel(self):
        """If the prompt ever stops teaching "generic", this normalization is
        dead weight — and if it keeps teaching it while the executor forgets
        again, we are back to the original bug. Pin the pair together."""
        from backend.ai import prompt_builder
        src = _read(Path(prompt_builder.__file__))
        assert '"generic"' in src or "'generic'" in src, (
            "the parse prompt must still instruct the model to answer a vague "
            "order with the generic sentinel")

    def test_strategic_and_tactical_share_one_sentinel_set(self):
        """The two paths disagreed about what "no target" means, and the
        tactical side lost. One source now."""
        from backend.commands import strategic_executor
        src = _read(Path(strategic_executor.__file__))
        assert "is_generic_target" in src
        assert "GENERIC_TARGETS = {" not in src, (
            "the strategic path must consume the shared set, not a private copy")

    @pytest.mark.parametrize("action", ["attack", "move", "scout"])
    def test_a_vague_order_no_longer_dead_ends(self, action):
        """Before: attack -> "Unknown target: generic"; move/scout ->
        "Region 'generic' not found". All three were un-actionable."""
        world = build_world("1805")
        world.opening_attack_guidance_shown = True
        result = CommandExecutor().execute({"command": {
            "marshal": "Ney", "action": action,
            "target": "generic", "type": "specific",
            "_raw_input": "Ney, give them hell",
        }}, {"world": world})
        message = str(result.get("message") or "")
        assert "Unknown target" not in message, message
        assert "'generic' not found" not in message, message

    def test_parser_normalizes_before_dispatch(self):
        """The normalization lives at the parser seam, so it protects every
        action at once rather than per-executor."""
        from backend.ai.parser_eval import build_llm_game_state

        world = build_world("1805")
        state = build_llm_game_state(world)
        parsed = CommandParser(use_real_llm=False).parse(
            "Ney, attack the enemy", state, world)
        if parsed.get("success"):
            assert (parsed.get("command") or {}).get("target") != "generic"


class TestMoveWithoutDestinationAsks:
    """The same shape, one action over. An attack with no target auto-resolves
    to the nearest enemy; a move CANNOT — there is no nearest destination — so
    it dead-ended on "Move order requires a destination", which is true,
    unhelpful and un-actionable. It asks now."""

    def test_move_with_no_destination_raises_a_clarification(self):
        world = build_world("1805")
        result = CommandExecutor().execute({"command": {
            "marshal": "Ney", "action": "move", "target": None,
            "type": "specific",
            "_raw_input": "Ney, take up a better position",
        }}, {"world": world})
        assert result.get("state") == "awaiting_clarification"
        assert result.get("clarification_kind") == "move_destination"
        assert result["options"], "must offer somewhere to go"

    def test_the_offered_destinations_are_reachable_neighbours(self):
        world = build_world("1805")
        ney = world.marshals["Ney"]
        neighbours = set(world.get_region(ney.location).adjacent_regions)
        result = CommandExecutor().execute({"command": {
            "marshal": "Ney", "action": "move", "target": None,
            "type": "specific", "_raw_input": "Ney, reposition",
        }}, {"world": world})
        for option in result["options"]:
            assert option["target"] in neighbours, (
                f"{option['target']} is not adjacent — a one-step move cannot "
                f"reach it")
            assert option["command"] == f"Ney, move to {option['target']}"

    def test_labels_carry_no_internal_keys(self):
        world = build_world("1805")
        result = CommandExecutor().execute({"command": {
            "marshal": "Ney", "action": "move", "target": None,
            "type": "specific", "_raw_input": "Ney, reposition",
        }}, {"world": world})
        for option in result["options"]:
            assert not re.search(r"[a-z][A-Z]", option["label"]), option["label"]

    def test_automated_strategic_hops_never_ask(self):
        """A per-hop step of a standing order is the ENGINE moving him. There
        is nobody at the keyboard to answer a question."""
        from backend.commands.movement_executor import MovementExecutor
        import inspect
        src = inspect.getsource(MovementExecutor._execute_move)
        branch = src.split("if not target:", 1)[1]
        # Up to the clarification call — the stand-down must come FIRST.
        head = branch.split("build_move_destination_clarification", 1)[0]
        assert "strategic_execution" in head, (
            "the no-destination branch must stand down for automated hops "
            "BEFORE it tries to ask the player a question")
