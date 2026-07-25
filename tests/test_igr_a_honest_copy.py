"""IGR-A — Honest copy.

Owner: `docs/INGAME_REVIEW_FIXES_SPEC.md` §2 (slice IGR-A, gate-free).
Evidence of record: `docs/audits/INGAME_REVIEW_2026_07_25.md`.

Four items, each a *rendering* defect the live in-game review walked into:

  A1  the war-entry hard blocks printed raw machine keys
      ("Spain cannot join against Prussia: no_participation_path.")
  A2  the confirm popup printed each political-context line twice
  A3  a NATION typed where a province belongs mis-resolved
      ("move to Austria" marched Ney to the Spanish coast)
  A4  releasing a vassal reported nothing at all

The 1805 fixtures are explicit: `tests/conftest.py` pins
`SOVEREIGN_SCENARIO=none` suite-wide, so a test written without one measures
the 19-region legacy map — where Bavaria/Saxony/Hanover ARE provinces — and
would pass while the shipped campaign stayed broken.
"""
import io
import os
from pathlib import Path

import pytest

from backend.campaign_log import (
    CAMPAIGN_LOG_TYPES,
    filter_campaign_log,
    format_event_oneliner,
)
from backend.commands.executor import CommandExecutor
from backend.commands.parser import CommandParser
from backend.display_names import (
    ALLY_ENTRY_BLOCK_DISPLAY,
    ally_entry_block_line,
    warnings_to_plain_text,
)
from backend.game_logic.vassal import RELEASE_COOLDOWN_TURNS, release_vassal
from backend.models.world_state import WorldState

SCENARIO = "godot-client/project-sovereign/assets/maps/europe_1805.json"
GODOT = Path("godot-client/project-sovereign")


def _world1805():
    prior = os.environ.pop("SOVEREIGN_SCENARIO", None)
    try:
        return WorldState.from_scenario(SCENARIO)
    finally:
        if prior is not None:
            os.environ["SOVEREIGN_SCENARIO"] = prior


@pytest.fixture
def world1805():
    return _world1805()


def _read_gd(name):
    return io.open(GODOT / "scripts" / name, encoding="utf-8").read()


# ══════════════════════════════════════════════════════════════════════════
# A1 — the hard-block vocabulary renders as prose
# ══════════════════════════════════════════════════════════════════════════

# The full vocabulary `get_ally_entry_hard_blocks` can emit. Four are live;
# the two suffixed war kinds are structurally unreachable from the only live
# producer (a court cannot be ALLIANCE and WAR on one symmetric key) but are
# named so a future producer cannot re-leak them.
_ALL_BLOCK_KEYS = [
    "armistice_cooldown_with_Prussia",
    "at_war_with_France",
    "direct_enemy_of_France",
    "anti_promiser_coalition_member",
    "hard_reject_posture",
    "no_participation_path",
]


class TestA1HardBlockCopy:
    @pytest.mark.parametrize("reason", _ALL_BLOCK_KEYS)
    def test_every_emittable_reason_renders_as_prose(self, reason):
        line = ally_entry_block_line(reason, "Spain", "Prussia", "France")
        assert "_" not in line, f"raw key leaked: {line}"
        assert reason not in line
        # A whole sentence, not a fragment glued after a colon.
        assert line.endswith(".") and line[0].isupper()
        assert len(line.split()) >= 6

    def test_unknown_key_gets_prose_not_title_case(self):
        """The trap: falling back to `_fallback_display_name` would render
        'No Participation Path' — the same leak wearing a hat."""
        line = ally_entry_block_line("some_future_reason", "Spain", "Prussia")
        assert "Some Future Reason" not in line
        assert "_" not in line
        assert line == "Spain cannot be brought into the war against Prussia."

    def test_dynamic_nation_suffix_matches_by_prefix(self):
        """Three kinds append a nation name, so an exact dict lookup misses."""
        for enemy in ("Prussia", "Russia", "Ottoman"):
            line = ally_entry_block_line(
                f"armistice_cooldown_with_{enemy}", "Spain", enemy)
            assert "armistice" in line.lower()
            assert "cannot be brought into the war" not in line

    def test_camelcase_nations_are_humanized(self):
        line = ally_entry_block_line(
            "no_participation_path", "PapalStates", "Ottoman", "France")
        assert "PapalStates" not in line and "Papal States" in line
        assert "Ottoman Empire" in line

    def test_the_shared_line_never_addresses_the_emperor(self):
        """The same helper feeds the campaign log, which is a third-person
        chronicle and contains zero 'Sire'. Talleyrand's voice is wrapped at
        a call site, never inside the shared sentence."""
        for reason in _ALL_BLOCK_KEYS:
            assert "Sire" not in ally_entry_block_line(reason, "Spain", "Prussia")

    def test_templates_are_not_registered_in_the_universal_translator(self):
        """`display()` returns a hit VERBATIM, so registering brace-bearing
        templates would ship a new leak. Same reason AMENDS_REFUSAL_DISPLAY is
        kept out."""
        from backend import display_names

        for table in display_names._CATEGORY_MAPS.values():
            assert table is not ALLY_ENTRY_BLOCK_DISPLAY
        for template in ALLY_ENTRY_BLOCK_DISPLAY.values():
            assert "{" in template  # they really are templates

    def test_the_live_producer_is_the_declaration_preview(self, world1805):
        """A1's 'done when' enumerates the live producers. Only
        `build_declaration_preview` builds opportunities in production —
        `ai_should_propose_bargain` / `ai_evaluate_war_entry` have no
        production callers, and `resolve_join_opportunity` none either."""
        executor = CommandExecutor()
        result = executor._execute_diplomatic_declare_war(
            {
                "target_nation": "Prussia",
                "action": "diplomatic_declare_war",
                "war_objective": "conquest",
                # Two clicks from boot: the STRONG Talleyrand objection fires
                # first (boot threat 85 > 50) and the ally-entry review is only
                # reachable past it. Without this the dialogue is EMPTY and a
                # leak test would pass vacuously.
                "confirmed_objection": True,
            },
            world1805,
        )
        dialogue = result.get("diplomatic_dialogue") or {}
        blocked = [w for w in dialogue.get("warnings", [])
                   if w.get("hard_block_reason")]
        assert blocked, "boot-reachable hard block expected (France|Spain ALLIANCE)"
        for warning in blocked:
            assert warning["hard_block_reason"] not in warning["text"]
            assert "_" not in warning["text"]
        for line in dialogue.get("proposal_terms_summary", []):
            assert "no_participation_path" not in line

    def test_the_machine_field_stays_raw(self, world1805):
        """The campaign-log arm re-renders from `hard_block_reason`, including
        out of OLD SAVES, and `ai_should_propose_bargain` does exact-literal
        membership tests on it. Prose-ifying it would be a rename."""
        executor = CommandExecutor()
        executor._execute_diplomatic_declare_war(
            {"target_nation": "Prussia", "action": "diplomatic_declare_war",
             "war_objective": "conquest", "confirmed_objection": True},
            world1805,
        )
        events = [e for e in world1805.event_log
                  if e.get("type") == "hard_block_surfaced"]
        assert events
        assert events[0]["hard_block_reason"] == "no_participation_path"
        assert events[0]["promiser"] == "France"

    def test_the_campaign_log_surface_is_actually_reachable(self, world1805):
        """The second surface was DEAD: `filter_campaign_log` had no branch for
        `hard_block_surfaced` and no default-include fallthrough, so the event
        never reached the overlay. A1 renders prose on BOTH surfaces, which
        means this one has to exist."""
        executor = CommandExecutor()
        executor._execute_diplomatic_declare_war(
            {"target_nation": "Prussia", "action": "diplomatic_declare_war",
             "war_objective": "conquest", "confirmed_objection": True},
            world1805,
        )
        visible = [e for e in filter_campaign_log(world1805.event_log, world1805)
                   if e.get("type") == "hard_block_surfaced"]
        assert visible, "hard_block_surfaced must survive the campaign-log filter"
        line = format_event_oneliner(visible[0])
        assert "no_participation_path" not in line
        assert "no participation path" not in line
        assert "Spain" in line and "Prussia" in line

    def test_no_new_event_type(self):
        """A1 is display-only — the log taxonomy must not move."""
        assert len(CAMPAIGN_LOG_TYPES) == 140


# ══════════════════════════════════════════════════════════════════════════
# A2 — "Political Context:" stops repeating itself
# ══════════════════════════════════════════════════════════════════════════

class TestA2NoDuplicatedPoliticalContext:
    def _declare_on_treaty_partner(self, world, target="Austria"):
        """The duplicating branch is the TREATY-warning one, which needs a
        live `active_treaties` entry — the boot France|Spain ALLIANCE has a
        diplomatic state but no treaty record, so it routes to the ally-entry
        review instead and would test the wrong producer."""
        player = world.player_nation
        key = world._make_diplo_key(player, target)
        world.active_treaties[key] = {
            "type": "alliance", "nations": [player, target], "turn_signed": 1,
        }
        world.diplomatic_states[key] = "ALLIANCE"
        world.diplomatic_points = 5
        executor = CommandExecutor()
        return executor._execute_diplomatic_declare_war(
            {"target_nation": target, "action": "diplomatic_declare_war",
             "war_objective": "conquest", "confirmed_objection": True},
            world,
        )

    def test_declare_war_confirm_ships_warnings_without_inlining_them(
            self, world1805):
        result = self._declare_on_treaty_partner(world1805)
        dialogue = result.get("diplomatic_dialogue") or {}
        assert dialogue.get("type") == "force_declare_war_confirmation"
        warnings = dialogue.get("warnings") or result.get("warnings") or []
        assert warnings, "the structured list is the surviving delivery"
        message = result.get("message", "")
        talleyrand = dialogue.get("talleyrand_text", "")
        for warning in warnings:
            text = warning.get("text", "")
            assert text
            assert text not in message, f"duplicated into message: {text}"
            assert text not in talleyrand, f"duplicated into prose: {text}"

    def test_the_base_prose_is_untouched(self, world1805):
        """Only the appended warning lines were dropped — Talleyrand still
        asks his question."""
        result = self._declare_on_treaty_partner(world1805)
        message = result.get("message", "").lower()
        assert "treaty" in message or "oath" in message
        assert "shall i proceed" in message

    def test_break_treaty_confirm_also_stops_inlining(self, world1805):
        player = world1805.player_nation
        key = world1805._make_diplo_key(player, "Austria")
        world1805.active_treaties[key] = {
            "type": "alliance", "nations": [player, "Austria"], "turn_signed": 1,
        }
        world1805.diplomatic_states[key] = "ALLIANCE"
        result = CommandExecutor()._diplomatic._execute_diplomatic_break(
            {"target_nation": "Austria"}, world1805)
        dialogue = result.get("diplomatic_dialogue") or {}
        assert dialogue.get("type") == "force_break_treaty_confirmation"
        warnings = result.get("warnings") or []
        assert warnings
        for warning in warnings:
            assert warning["text"] not in result.get("message", "")
            assert warning["text"] not in (dialogue.get("talleyrand_text") or "")

    def test_the_popup_cap_was_raised_at_every_site(self):
        """Three `mini(warnings.size(), N)` sites render this block, not one.
        With the inline copy gone the block is the ONLY surface, so a cap of 2
        would trade duplication for truncation."""
        source = _read_gd("proposal_confirm_popup.gd")
        assert "mini(warnings.size(), 2)" not in source
        assert source.count("mini(warnings.size(), 4)") == 3
        # Static pins from test_session8c_popups_notifications.py must survive.
        assert 'data.get("warnings", [])' in source
        assert "Political Context:" in source

    def test_break_treaty_confirm_is_a_known_dialogue_type(self):
        """It routed through the `_:` default arm while firing
        `push_warning("Unknown diplomatic_dialogue dtype")` on every fire — and
        that route now carries the only copy of the warnings."""
        assert "force_break_treaty_confirmation" in _read_gd("main.gd")

    def test_the_paradox_inline_survives_because_nothing_renders_it(self):
        """The one place the concatenation is load-bearing:
        `commitment_paradox_popup.gd` renders `message` and nothing else, and
        the popup payload carries no `warnings` key. Dropping it there would
        have silently deleted the reliability preview from the game."""
        popup = _read_gd("commitment_paradox_popup.gd")
        assert "warnings" not in popup
        source = io.open("backend/game_logic/diplomacy.py", encoding="utf-8").read()
        assert "warnings_to_plain_text(attacker_paradox_warnings" in source

    def test_warnings_to_plain_text_is_the_single_formatter(self):
        assert warnings_to_plain_text([]) == ""
        assert warnings_to_plain_text(None) == ""
        rows = [{"text": "One."}, {"text": ""}, {"text": "Two."}]
        assert warnings_to_plain_text(rows) == "One.\nTwo."
        assert warnings_to_plain_text(rows, separator=" ") == "One. Two."


# ══════════════════════════════════════════════════════════════════════════
# A3 — a nation typed where a province belongs
# ══════════════════════════════════════════════════════════════════════════

def _llm_game_state(world):
    """The production-shaped payload (mirrors `main.get_llm_game_state`).

    `map_data` is load-bearing: it is how the live nation roster reaches the
    mock parser, and the vassal-family nation targets resolve through it.
    """
    return {
        "turn": int(world.current_turn),
        "gold": int(world.gold),
        "marshals": {
            m.name: {"location": m.location, "strength": int(m.strength),
                     "morale": int(m.morale)}
            for m in world.get_player_marshals() if m.strength > 0
        },
        "enemies": {},
        "map_data": {
            name: {"controller": r.controller or "Neutral", "marshals": []}
            for name, r in world.regions.items()
        },
    }


def _order(world, text):
    parser = CommandParser(use_real_llm=False)
    game_state = _llm_game_state(world)
    game_state["world"] = world
    return CommandExecutor().execute(parser.parse(text, game_state, world), game_state)


class TestA3NationNamedAsRegion:
    @pytest.mark.parametrize("nation,province", [
        ("Austria", "Vienna"),
        ("Britain", "London"),
        ("Prussia", "Berlin"),
        ("Saxony", "Dresden"),
        ("Bavaria", "Munich"),
        ("Russia", "Ukraine"),
        ("Holland", "Amsterdam"),
    ])
    def test_the_answer_names_the_nations_own_provinces(self, nation, province):
        result = _order(_world1805(), f"Ney, move to {nation}")
        assert result["success"] is False
        message = result["message"]
        assert "is a nation, not a province" in message
        assert province in message

    @pytest.mark.parametrize("nation,wrong", [
        ("Austria", "Asturias"),
        ("Britain", "Brittany"),
    ])
    def test_the_wrong_province_march_is_dead(self, nation, wrong):
        """The two names that did not merely suggest badly — they EXECUTED a
        multi-province march to the wrong country."""
        result = _order(_world1805(), f"Ney, move to {nation}")
        assert result["success"] is False
        assert wrong not in result["message"]

    def test_the_typed_display_form_resolves_too(self):
        """A player reads 'Papal States' in the ledger and types that. The tag
        is `PapalStates`, and its demonym override used to NULL the order into
        a dead-end 'Where shall Ney march, Sire?'."""
        result = _order(_world1805(), "Ney, move to Papal States")
        assert "Papal States is a nation, not a province" in result["message"]
        assert "Rome" in result["message"]

    @pytest.mark.parametrize("name", ["Hanover", "Naples", "Normandy"])
    def test_a_word_that_is_also_a_province_stays_a_province(self, name):
        """The collision set is three, not one. The guard runs AFTER the
        exact-region check, so none of them is captured."""
        from backend.ai.nation_names import resolve_typed_nation

        world = _world1805()
        assert world.get_region(name) is not None
        assert resolve_typed_nation(name, world) is None
        result = _order(world, f"Ney, move to {name}")
        assert "is a nation, not a province" not in result.get("message", "")

    def test_an_ordinary_typo_still_gets_its_suggestion(self):
        """The falsifiable negative: the Sweep-5 movement passthrough must not
        be re-nulled, and unknown places keep the fuzzy answer."""
        result = _order(_world1805(), "Ney, move to Venetia")
        assert "Region 'Venetia' not found" in result["message"]
        assert "is a nation" not in result["message"]

    def test_the_attack_arm_names_the_court_too(self):
        """The spec claimed `attack Austria` 'refuses'. Measured, it only
        refused because Asturias happened to be empty — with an enemy standing
        there it staged a commit-able muster 1,500km away."""
        result = _order(_world1805(), "Ney, attack Austria")
        assert result["success"] is False
        assert "Austria is a nation, not a province" in result["message"]
        assert "Asturias" not in result["message"]

    def test_a_demonym_is_still_an_army_not_a_country(self):
        """The pre-existing rule must survive: 'the Austrians' names a force,
        so the target is dropped and the executor auto-targets."""
        parser = CommandParser(use_real_llm=False)
        world = _world1805()
        parsed = parser.parse(
            "Ney, attack the Austrians", _llm_game_state(world), world)
        command = parsed.get("command", parsed)
        assert command.get("target") in (None, "")

    def test_the_vassal_family_still_takes_nation_targets(self):
        """CR-0's carve-out: 'invest in Austria' must keep Austria, and the new
        guard must not intercept it."""
        parser = CommandParser(use_real_llm=False)
        world = _world1805()
        parsed = parser.parse("invest in austria", _llm_game_state(world), world)
        assert parsed["success"], parsed.get("error")
        assert parsed["command"]["action"] == "invest_vassal"
        assert parsed["command"]["target"] == "Austria"

    def test_the_shared_demonym_list_was_not_widened(self):
        """Widening `_nation_demonyms` would reclassify 'march to Saxony' as a
        GENERIC army order — a pin a previous adversarial review wrote for
        exactly this hazard. The nation predicate is a separate function."""
        from backend.ai.strategic_parser import (
            _nation_demonyms,
            detect_strategic_command,
        )

        world = _world1805()
        forms = set(_nation_demonyms(world))
        assert "austrian" in forms and "austria" not in forms
        result = detect_strategic_command("Ney, march to Saxony", "Ney", world)
        assert result is not None and result.get("target_type") != "generic"

    def test_a_nation_holding_nothing_gets_an_honest_arm(self):
        """`get_nation_regions` returns [] for a court holding nothing —
        without this branch the player reads 'theirs are .'.

        Reachable via a VASSAL, which `get_active_nations` keeps on the roster
        at zero provinces (a province-less non-vassal is eliminated and leaves
        the roster entirely, so the guard correctly never fires for it)."""
        from backend.ai.nation_names import nation_province_list

        world = _world1805()
        for name in list(world.get_nation_regions("Switzerland")):
            world.regions[name].controller = "France"
        world.invalidate_active_nations_cache()
        assert "Switzerland" in world.get_active_nations()
        assert nation_province_list("Switzerland", world) == []
        _, error = CommandExecutor()._fuzzy_match_region("Switzerland", world)
        assert error is not None
        assert "no province" in error["message"]
        assert "theirs are ." not in error["message"]

    def test_no_world_is_safe(self):
        """Parsers are built with no world in unit tests — same contract as
        `_is_nation_demonym`."""
        from backend.ai.nation_names import resolve_typed_nation

        assert resolve_typed_nation("Austria", None) is None
        assert resolve_typed_nation("", object()) is None


# ══════════════════════════════════════════════════════════════════════════
# A4 — releasing a vassal says what it cost
# ══════════════════════════════════════════════════════════════════════════

class TestA4VassalReleaseReport:
    def test_the_report_names_tribute_threat_cooldown_and_the_woken_deck(self):
        world = _world1805()
        threat_before = int(world.threat_by_target.get("France", 0))
        message = release_vassal(world, "KingdomOfItaly")["message"]

        assert "375 gold a turn" in message                      # tribute lost
        assert f"{threat_before} → " in message              # threat drop
        assert f"{RELEASE_COOLDOWN_TURNS} turns" in message       # cooldown
        assert "Risorgimento" in message                          # woken deck
        assert "Italy" in message                                 # the watcher
        assert "2 of 5 provinces held" in message
        assert "no longer answer France's call to arms" in message

    def test_the_threat_line_reports_the_real_delta_not_the_constant(self):
        """`reduce_threat` clamps at 0, so writing '-8' is a lie whenever the
        slot is already below 8."""
        world = _world1805()
        world.threat_by_target["France"] = 3
        message = release_vassal(world, "Holland")["message"]
        assert "3 → 0" in message
        assert int(world.threat_by_target["France"]) == 0

    def test_no_clause_fires_when_it_would_be_false(self):
        """Switzerland has NO agenda deck, no marshals, and the Continental
        System is empty at boot — three lies waiting for an unconditional
        report."""
        world = _world1805()
        message = release_vassal(world, "Switzerland")["message"]
        assert "design of their own" not in message
        assert "marshals return" not in message
        assert "Continental System" not in message
        assert "225 gold a turn" in message

    def test_the_liberation_arm_claims_no_threat_relief(self):
        """Both settlement callers pass reduce_threat_on_release=False and
        apply their own -8 afterwards, attributed to `liberation`."""
        world = _world1805()
        message = release_vassal(
            world, "Holland", reduce_threat_on_release=False)["message"]
        assert "alarm" not in message
        assert "→" not in message
        assert "337 gold a turn" in message

    def test_the_rebellion_arm_never_narrates_a_concession(self):
        """The pair goes to WAR, not PEACE, and no threat is relieved — the
        voluntary copy would be nonsense on it."""
        world = _world1805()
        world.vassals["Switzerland"]["lord"] = "Austria"
        result = release_vassal(world, "Switzerland", rebellion=True)
        message = result["message"]
        assert "released from vassalage" in message
        for forbidden in ("alarm", "call to arms", "stands a free court",
                          "gold a turn", "under the yoke"):
            assert forbidden not in message

    def test_the_forward_looking_claim_is_the_true_one(self):
        """Release does NOT end the vassal's other wars — only the lord-vassal
        pair. What is actually lost is the call to arms."""
        world = _world1805()
        assert world.get_diplomatic_state("Austria", "KingdomOfItaly") == "WAR"
        message = release_vassal(world, "KingdomOfItaly")["message"]
        assert world.get_diplomatic_state("Austria", "KingdomOfItaly") == "WAR"
        assert "call to arms" in message
        assert "at peace" not in message

    def test_the_snapshot_survives_the_mutations(self):
        """`original_nation` is delattr'd and `world.vassals[...]` is deleted
        before the report is built — the numbers must be captured first."""
        world = _world1805()
        marshal = next(iter(
            m for m in world.marshals.values() if m.nation == "France"))
        marshal.original_nation = "Holland"
        marshal.nation = "France"
        message = release_vassal(world, "Holland")["message"]
        assert marshal.name in message
        assert "marshals return to their own colours" in message
        assert not hasattr(marshal, "original_nation")


# ══════════════════════════════════════════════════════════════════════════
# Pre-push adversarial review (38 agents, find→2 refuters) — the four
# findings that survived refutation. Each one is a defect the first cut of
# IGR-A shipped, so each gets a pin.
# ══════════════════════════════════════════════════════════════════════════

# Every movement phrasing the strategic parser recognises. "move to" was the
# ONLY one the first cut guarded — the other ten built a real MOVE_TO order to
# Asturias, which is the entire defect A3 exists to kill.
_MOVEMENT_VERBS = [
    "move to", "march to", "advance to", "head to", "proceed to",
    "make for", "travel to", "push to", "deploy to", "relocate to",
    "journey to",
]


class TestReviewFixStrategicPathIsGuardedToo:
    @pytest.mark.parametrize("verb", _MOVEMENT_VERBS)
    def test_no_phrasing_marches_to_the_wrong_country(self, verb):
        world = _world1805()
        result = _order(world, f"Ney, {verb} Austria")
        assert result["success"] is False
        assert "Austria is a nation, not a province" in result["message"]
        assert "Asturias" not in result["message"]
        ney = world.get_marshal("Ney")
        order = getattr(ney, "strategic_order", None)
        assert getattr(order, "target", None) != "Asturias"
        assert ney.location == "Rhineland", "no step may be taken"

    def test_britain_too(self):
        world = _world1805()
        result = _order(world, "Ney, march to Britain")
        assert "Britain is a nation, not a province" in result["message"]
        assert "Brittany" not in result["message"]

    def test_a_real_province_still_takes_a_strategic_order(self):
        world = _world1805()
        result = _order(world, "Ney, march to Normandy")
        assert result["success"] is True
        assert getattr(world.get_marshal("Ney").strategic_order, "target", None) == "Normandy"

    def test_a_tag_that_is_its_own_demonym_is_a_court_not_a_generic_army(self):
        """`Ottoman` and `PapalStates` (-> "papal") collide with their own
        demonym overrides, so the strategic classifier called them GENERIC and
        sent the marshal at whichever enemy was nearest — an Austrian, on the
        boot board."""
        for typed in ("Ottoman", "Papal States"):
            world = _world1805()
            result = _order(world, f"Ney, march to {typed}")
            assert result["success"] is False
            assert "is a nation, not a province" in result["message"]
            assert getattr(world.get_marshal("Ney").strategic_order, "target", None) != "Swabia"

    def test_the_plural_demonym_stays_generic(self):
        """The falsifiable negative: "the Austrians" is still an army
        reference, and the CR-0 generic classification must not move."""
        from backend.ai.strategic_parser import detect_strategic_command

        world = _world1805()
        result = detect_strategic_command("Ney, pursue the Austrians", "Ney", world)
        assert result is not None
        assert result.get("target_type") == "generic"

    def test_the_copy_has_one_source(self):
        """Three seams answer this now (tactical chokepoint, strategic order
        builder, retreat fallback) — the sentence is written once."""
        from backend.ai.nation_names import nation_not_a_province_message

        world = _world1805()
        line = nation_not_a_province_message("Saxony", world)
        assert line == "Saxony is a nation, not a province. Name a province, Sire — theirs are Dresden."
        for module in ("backend/commands/executor.py",
                       "backend/commands/strategic_executor.py"):
            source = io.open(module, encoding="utf-8").read()
            assert "is a nation, not a province" not in source, (
                f"{module} re-types the sentence instead of calling the helper")


class TestReviewFixRetreatNamesTheCourt:
    def test_retreat_does_not_call_a_real_nation_an_unknown_province(self):
        """The retreat arm discards the error dict by design (a retreat must
        substitute, never refuse) — but it was telling the player that Austria
        "is not known to the staff"."""
        world = _world1805()
        _, error = CommandExecutor()._fuzzy_match_region("Austria", world)
        assert error["nation_named"] == "Austria"
        source = io.open("backend/commands/movement_executor.py", encoding="utf-8").read()
        assert 'reason = "that is a nation, not a province"' in source
        assert "_match_error" in source and 'get("nation_named")' in source


class TestReviewFixFormedCourtsAreNotDeadNamed:
    def test_a_formed_nation_is_named_by_its_new_name(self):
        """NA-6 §11.8 stage 3: no surface may show the dead name. Because this
        helper composes finished prose, the client's raw-tag override can
        never repair it downstream — so it must resolve through the
        formation-aware chokepoint itself."""
        from backend.game_logic.formations import formed_display_name

        world = _world1805()
        world.nation_formations = {
            "KingdomOfItaly": {"id": "risorgimento", "sponsor": "France", "turn": 3},
        }
        assert formed_display_name(world, "KingdomOfItaly") == "Italy"
        line = ally_entry_block_line(
            "no_participation_path", "KingdomOfItaly", "Ottoman", "France",
            world=world)
        assert "Italy" in line
        assert "Kingdom of Italy" not in line

    def test_without_a_world_it_falls_back_to_the_static_name(self):
        line = ally_entry_block_line(
            "no_participation_path", "KingdomOfItaly", "Ottoman")
        assert "Kingdom of Italy" in line


class TestReviewFixTheLogIsNotSpammed:
    def test_reopening_the_review_does_not_append_a_duplicate(self):
        """The review is re-openable. While the campaign-log branch was dead
        this was invisible; with the surface live an unguarded write is a NEW
        source of exactly the spam IGR-B exists to cure."""
        world = _world1805()
        executor = CommandExecutor()
        for _ in range(3):
            executor._execute_diplomatic_declare_war(
                {"target_nation": "Prussia", "action": "diplomatic_declare_war",
                 "war_objective": "conquest", "confirmed_objection": True},
                world,
            )
        events = [e for e in world.event_log
                  if e.get("type") == "hard_block_surfaced"]
        assert len(events) == 1, f"expected one line, got {len(events)}"

    def test_a_different_turn_records_again(self):
        """The guard is per-turn, not permanent — the same block next turn is
        news again."""
        world = _world1805()
        executor = CommandExecutor()
        executor._execute_diplomatic_declare_war(
            {"target_nation": "Prussia", "action": "diplomatic_declare_war",
             "war_objective": "conquest", "confirmed_objection": True}, world)
        world.current_turn += 1
        executor._execute_diplomatic_declare_war(
            {"target_nation": "Prussia", "action": "diplomatic_declare_war",
             "war_objective": "conquest", "confirmed_objection": True}, world)
        events = [e for e in world.event_log
                  if e.get("type") == "hard_block_surfaced"]
        assert len(events) == 2


# ══════════════════════════════════════════════════════════════════════════
# IGR-X1 — found in passing by the spec's verification fleet, routed
# "standalone; take before IGR-A" (docs/BUG_FIXES.md).
# ══════════════════════════════════════════════════════════════════════════

class TestX1RecoveryDestinationSurvivesSave:
    def test_clearing_the_recovery_lock_does_not_break_serialization(self):
        """`del marshal._recovery_destination` removed the attribute
        outright; `Marshal.to_dict` reads it directly, so the next save or
        autosave raised AttributeError."""
        world = _world1805()
        marshal = next(iter(world.marshals.values()))
        marshal._recovery_destination = "Vienna"

        source = io.open("backend/ai/enemy_ai.py", encoding="utf-8").read()
        assert "del marshal._recovery_destination" not in source

        marshal._recovery_destination = None
        assert marshal.to_dict()["_recovery_destination"] is None
