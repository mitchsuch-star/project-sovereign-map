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
