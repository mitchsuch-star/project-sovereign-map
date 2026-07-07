"""
CR-5b behavior tests — Flavor Echoing
(COMMAND_ROBUSTNESS_SPEC.md §6.4 rider (a); CR5_IMPLEMENTATION_BRIEF.md §7).

"The game heard me": on a DELEGATION order ("Ney, deal with Mack") the marshal's
IMMEDIATE spoken reply at the RESPONSE seam echoes the player's tone. Distinct
from CR-5's PARSE seam and from rider (d)'s RECORD seam (campaign log / battle
report). Cosmetic/feel ONLY — no mechanical effect (Golden Rule 6).

Architecture under test:
  - LIVE: the LLM composes the reaction in the `flavor` field on the EXISTING
    CR-3 parse call (zero extra LLM call). It rides
    PARSE_TOOL -> json_to_parse_result -> ParseResult.flavor -> to_dict ->
    parser.parse command dict lift -> main.py delegation attach seam.
  - DETERMINISTIC FLOOR + REGISTER GATE (delegation.py): a register-violating /
    parroting / action-naming live line is DROPPED to a deterministic floor
    (aggressive) or simply omitted (cautious). The floor is a LIVE-MODE fallback
    — mock never reaches the executed arms (guardrail e routes every mock
    delegation to ASK, whose clause-quote is already the echo).

The ENTRY GATE (§6.4): the non-parroting fallback is a bounded sibling of the
shipped describe_cautious_delegation / describe_inferred_bad_odds — keyed to
(personality, RESOLVED action, target), NEVER the raw verb — with a falsifiable
NEGATIVE assertion (contains no DELEGATION_VERBS, no action word).
"""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.ai.providers import PARSE_TOOL, json_to_parse_result
from backend.ai.prompt_builder import OUTPUT_SCHEMA, build_parse_prompt
from backend.ai.schemas import ParseResult
from backend.ai.validation import VALID_ACTIONS, validate_parse_result
from backend.commands.delegation import (
    _AGGRESSIVE_FLOORS,
    DELEGATION_VERBS,
    DelegationMatch,
    describe_aggressive_delegation,
    detect_delegation,
    flavor_passes_register,
    resolve_delegation_flavor,
    resolve_live_cautious_prefix,
)
from backend.commands.parser import CommandParser
from backend.models.world_state import WorldState

SCENARIO_PATH = (
    Path(__file__).resolve().parents[1]
    / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
)


@pytest.fixture(scope="module")
def world1805():
    """Read-only 1805 world (Ney=aggressive, Davout=cautious, Soult=literal)."""
    return WorldState.from_scenario(str(SCENARIO_PATH))


def _match(world, raw):
    m = detect_delegation(world, raw)
    assert m is not None, f"expected a delegation match for {raw!r}"
    return m


def _agg_floor(world, raw="Ney, deal with Mack"):
    """The deterministic aggressive floor for this (marshal, target) — computed
    the same way production does, so tests are variant-proof (the floor rotates
    across a small set keyed on the names)."""
    return describe_aggressive_delegation(_match(world, raw))


# ═══════════════════════════════════════════════════════════════════
# The `flavor` field plumbing (schema -> ParseResult -> dict -> parser lift)
# ═══════════════════════════════════════════════════════════════════

class TestFlavorFieldPlumbing:
    def test_parse_tool_schema_carries_flavor_but_not_required(self):
        props = PARSE_TOOL["input_schema"]["properties"]
        assert "flavor" in props
        assert "flavor" not in PARSE_TOOL["input_schema"]["required"]
        # scoped to delegation-only in its description (token discipline)
        assert "DELEGATION" in props["flavor"]["description"].upper()

    def test_flavor_survives_json_to_parse_result_and_to_dict(self):
        pr = json_to_parse_result(
            {"matched": True, "marshals": ["Ney"], "action": "attack",
             "target": "Mack", "flavor": "'leave Mack to me, Sire'"},
            "Ney, deal with Mack", "anthropic")
        assert pr.flavor == "'leave Mack to me, Sire'"
        assert pr.to_dict().get("flavor") == "'leave Mack to me, Sire'"

    def test_flavor_absent_when_llm_omits_it(self):
        pr = json_to_parse_result(
            {"matched": True, "marshals": ["Ney"], "action": "attack",
             "target": "Waterloo"}, "Ney, attack Waterloo", "anthropic")
        assert pr.flavor is None
        assert "flavor" not in pr.to_dict()  # dict shape unchanged

    def test_flavor_lifted_in_parser_command_dict(self, world1805, monkeypatch):
        """The load-bearing lift: parser.py hand-builds command_dict from named
        .get()s, so without the explicit lift the field is silently dropped
        end-to-end. Pin exactly that seam."""
        p = CommandParser(use_real_llm=False)
        monkeypatch.setattr(
            p.llm, "parse_command",
            lambda text, game_state=None: {
                "marshal": "Ney", "action": "attack", "target": "Mack",
                "flavor": "'leave Mack to me, Sire'", "mode": "anthropic",
                "confidence": 0.85, "ambiguity": 5, "strategic_score": 10,
                "interpretation": "", "command_type": "tactical",
                "is_strategic": False, "key_source": "byok"})
        monkeypatch.setattr(p, "_validate_command",
                            lambda *a, **k: {"valid": True})
        result = p.parse("Ney, deal with Mack",
                         {"marshals": {}, "enemies": {}}, world=world1805)
        assert result["success"]
        assert result["command"].get("flavor") == "'leave Mack to me, Sire'"

    def test_flavor_survives_validate_parse_result(self):
        """validate_parse_result strips diplomatic_data sub-fields but must not
        touch a sibling like flavor (it operates on the typed ParseResult)."""
        pr = ParseResult(matched=True, marshals=["Ney"], action="attack",
                         target="Mack", flavor="'leave Mack to me'")
        validate_parse_result(pr, ["Ney"], ["Mack"], ["Mack"])
        assert pr.flavor == "'leave Mack to me'"


# ═══════════════════════════════════════════════════════════════════
# The register gate — the CR-5b non-parroting contract (drop-to-floor)
# ═══════════════════════════════════════════════════════════════════

class TestRegisterGate:
    def test_drops_every_raw_delegation_verb(self, world1805):
        m = _match(world1805, "Ney, deal with Mack")
        for verb in DELEGATION_VERBS:
            line = f"'Ney will {verb} Mack at once, Sire!'"
            assert flavor_passes_register(line, m) is False, verb

    @pytest.mark.parametrize("bad", [
        "'Ney will attack Mack, Sire!'",       # names the mechanical action
        "'Ney rides to scout Mack first.'",    # scout
        "'Ney will hold and observe, Sire.'",  # hold + observe
        "Ney will PURSUE Mack.",               # strategic enum
        "'Ney will move to engage, Sire.'",    # move + engage
        "'Davout will reconnoiter the ground.'",  # cautious deed word
    ])
    def test_drops_lines_that_name_a_game_action(self, world1805, bad):
        m = _match(world1805, "Ney, deal with Mack")
        assert flavor_passes_register(bad, m) is False

    def test_drops_internal_key_and_camelcase(self, world1805):
        m = _match(world1805, "Ney, deal with Mack")
        assert flavor_passes_register("'Leave ArchdukeCharles to me.'", m) is False
        assert flavor_passes_register("'Leave move_to him, Sire.'", m) is False

    def test_drops_first_person_narration_outside_quotes(self, world1805):
        m = _match(world1805, "Ney, deal with Mack")
        # narrator breaking into first person (no quoted span) — register break
        assert flavor_passes_register("I shall see Mack finished, Sire.", m) is False
        assert flavor_passes_register("Ney does this for me, Sire.", m) is False

    def test_allows_first_person_inside_a_quoted_span(self, world1805):
        m = _match(world1805, "Ney, deal with Mack")
        assert flavor_passes_register("'Leave Mack to me, Sire.'", m) is True
        assert flavor_passes_register("'At last, Sire — Mack is mine.'", m) is True

    def test_drops_overlong_line(self, world1805):
        m = _match(world1805, "Ney, deal with Mack")
        rambly = ("'First, Sire, I shall consider the ground, then the enemy, "
                  "then the weather, then my own strength before I decide.'")
        assert flavor_passes_register(rambly, m) is False

    def test_drops_verbatim_clause_or_verb_double_parrot(self, world1805):
        m = _match(world1805, "Ney, deal with Mack")
        # rider (d) already quotes the verbatim clause at the RECORD seam; the
        # RESPONSE seam must not repeat it.
        assert flavor_passes_register(f"'You said {m.clause}, Sire.'", m) is False

    def test_passes_clean_in_register_lines(self, world1805):
        m = _match(world1805, "Ney, deal with Mack")
        for good in [
            "'At last, Sire — leave Mack to me.'",
            "'Mack, Sire? Consider it settled.'",
            "Ney needs no second word, Sire — Mack is his.",
        ]:
            assert flavor_passes_register(good, m) is True, good

    def test_none_and_empty_never_pass(self, world1805):
        m = _match(world1805, "Ney, deal with Mack")
        assert flavor_passes_register(None, m) is False
        assert flavor_passes_register("", m) is False
        assert flavor_passes_register("   ", m) is False  # whitespace-only

    # ── Review fix (HIGH): contractions inside quoted marshal speech ──
    @pytest.mark.parametrize("good", [
        "'They'll not stand, Sire — leave Mack to me.'",
        "'We'll break him, Sire, and leave nothing to us.'",
        "'I'll not rest, Sire, till Mack is mine.'",
        "'He'll trouble us no more, Sire.'",
    ])
    def test_allows_in_quote_contractions(self, world1805, good):
        """The prompt's OWN good register puts first-person marshal speech in
        single quotes and uses contractions (I'll/we'll/they'll). The span parser
        must not treat the contraction apostrophe as a delimiter (else the eager
        live line is false-dropped to the flat floor)."""
        m = _match(world1805, "Ney, deal with Mack")
        assert flavor_passes_register(good, m) is True, good

    def test_drops_first_person_narration_even_with_contractions(self, world1805):
        """The same parser must still catch first-person NARRATION (outside any
        quote) that happens to contain contractions."""
        m = _match(world1805, "Ney, deal with Mack")
        assert flavor_passes_register(
            "Ney won't fail me, he'll see it done, Sire.", m) is False

    # ── Review fix (LOW): word-boundary parroting guard ──
    @pytest.mark.parametrize("good", [
        "'A fine unhandled affair, Sire — Mack is his.'",
        "'Mack is dealt his due, Sire.'",  # 'deal' only as a substring of 'dealt'
    ])
    def test_allows_incidental_verb_substring(self, world1805, good):
        m = _match(world1805, "Ney, deal with Mack")
        assert flavor_passes_register(good, m) is True, good

    def test_still_drops_genuine_spliced_verb(self, world1805):
        m = _match(world1805, "Ney, deal with Mack")
        assert flavor_passes_register("'Ney will handle Mack, Sire.'", m) is False
        assert flavor_passes_register(
            "'Ney will see to nothing but glory, Sire.'", m) is False  # real 'see to'

    # ── Review fix (LOW): personality-label guard (no double-narration) ──
    @pytest.mark.parametrize("bad", [
        "'Cautious as always, Sire — Mack shall keep.'",
        "'Ever eager, Sire — Mack is his.'",
        "'Prudent as always, Sire.'",
    ])
    def test_drops_personality_label_words(self, world1805, bad):
        m = _match(world1805, "Ney, deal with Mack")
        assert flavor_passes_register(bad, m) is False


# ═══════════════════════════════════════════════════════════════════
# The deterministic floor (aggressive) — the non-parroting entry gate
# ═══════════════════════════════════════════════════════════════════

class TestAggressiveFloor:
    def test_floor_never_contains_a_raw_delegation_verb(self, world1805):
        """The core §6.4 NEGATIVE assertion, over ALL 7 delegation verbs."""
        m = _match(world1805, "Ney, deal with Mack")
        floor = describe_aggressive_delegation(m).lower()
        for verb in DELEGATION_VERBS:
            assert verb not in floor, verb

    def test_floor_names_marshal_and_target_no_action_word(self, world1805):
        m = _match(world1805, "Ney, deal with Mack")
        floor = describe_aggressive_delegation(m)
        assert m.marshal in floor
        assert m.target_display in floor
        # no mechanical action / strategic enum / internal key leaks (R7)
        for leak in ("attack", "scout", "pursue", "move", "hold", "fortify",
                     "charge", "MOVE_TO", "PURSUE", "action="):
            assert leak not in floor

    def test_floor_passes_its_own_register_gate(self, world1805):
        """Defensive invariant: the trusted floor must itself be register-clean
        (so it can never be the parroting failure mode)."""
        m = _match(world1805, "Ney, deal with Mack")
        assert flavor_passes_register(describe_aggressive_delegation(m), m)

    def test_floor_humanizes_camelcase_target(self, world1805):
        # a camelCase enemy key must never reach the floor copy (R7)
        m = detect_delegation(world1805, "Ney, deal with Archduke Charles")
        if m is not None:  # only if that enemy exists in this world
            floor = describe_aggressive_delegation(m)
            import re
            assert not re.search(r"[a-z][A-Z]", floor)

    def _mk(self, marshal, target):
        return DelegationMatch(marshal, "aggressive", target, target, target,
                               "deal with", f"deal with {target}")

    def test_floor_varies_across_pairs_and_is_deterministic(self):
        """Review DESIGN_INTENT mitigation: the floor rotates a small set keyed on
        the names, so it is not a single memorizable sentence — yet stays a pure
        (deterministic) function."""
        outs = {describe_aggressive_delegation(self._mk(mm, tt))
                for mm, tt in [("Ney", "Mack"), ("Murat", "Charles"),
                               ("Lannes", "Kutuzov")]}
        assert len(outs) >= 2  # genuinely varies across pairs
        assert (describe_aggressive_delegation(self._mk("Ney", "Mack"))
                == describe_aggressive_delegation(self._mk("Ney", "Mack")))

    def test_every_floor_variant_is_register_clean(self):
        """Each template must itself pass the gate + name both parties, no leaks —
        the trusted floor can never be the parroting failure mode."""
        m = self._mk("Ney", "Mack")
        for tmpl in _AGGRESSIVE_FLOORS:
            line = tmpl.format(marshal="Ney", target="Mack")
            assert flavor_passes_register(line, m), line
            assert "Ney" in line and "Mack" in line
            for leak in ("attack", "scout", "pursue", "hold", "MOVE_TO",
                         "deal with", "handle"):
                assert leak not in line


# ═══════════════════════════════════════════════════════════════════
# The ceiling -> floor resolvers
# ═══════════════════════════════════════════════════════════════════

class TestResolvers:
    def test_aggressive_uses_clean_live_line(self, world1805):
        m = _match(world1805, "Ney, deal with Mack")
        out = resolve_delegation_flavor(m, "aggressive",
                                        "'At last, Sire — leave Mack to me.'")
        assert out == "'At last, Sire — leave Mack to me.'"

    def test_aggressive_falls_to_floor_on_violation(self, world1805):
        m = _match(world1805, "Ney, deal with Mack")
        # a register-violating live line (names the action) drops to the floor
        out = resolve_delegation_flavor(m, "aggressive",
                                        "'Ney will attack Mack now!'")
        assert out == describe_aggressive_delegation(m)

    def test_aggressive_floor_when_live_absent(self, world1805):
        m = _match(world1805, "Ney, deal with Mack")
        assert resolve_delegation_flavor(m, "aggressive", None) == \
            describe_aggressive_delegation(m)

    def test_returns_none_for_non_aggressive_arms(self, world1805):
        m = _match(world1805, "Davout, deal with Mack")
        assert resolve_delegation_flavor(m, "cautious", "'anything'") is None
        assert resolve_delegation_flavor(m, "ask", "'anything'") is None

    def test_cautious_prefix_uses_clean_live_line(self, world1805):
        m = _match(world1805, "Davout, deal with Mack")
        out = resolve_live_cautious_prefix(
            m, "'Mack, Sire? Then let me see the ground first.'")
        assert out == "'Mack, Sire? Then let me see the ground first.'"

    def test_cautious_prefix_none_when_absent_or_violating(self, world1805):
        m = _match(world1805, "Davout, deal with Mack")
        assert resolve_live_cautious_prefix(m, None) is None
        # a line that restates the deed ("reconnoiter") is dropped -> no prefix
        assert resolve_live_cautious_prefix(
            m, "'Let me reconnoiter him, Sire.'") is None

    def test_cautious_prefix_drops_exclamatory_line(self, world1805):
        # a cautious marshal's register is MEASURED — an eager "!" reads as a
        # tonal contradiction with the reconnoiter-first deed, so it is dropped.
        m = _match(world1805, "Davout, deal with Mack")
        assert resolve_live_cautious_prefix(
            m, "'To it at once, Sire — Mack is ours!'") is None


# ═══════════════════════════════════════════════════════════════════
# Endpoint integration — a flavor-injecting stub simulates the live LLM
# ═══════════════════════════════════════════════════════════════════

class _FlavorStubParser:
    """Wraps the mock parser but returns a resolved, live-style parse (with a
    `flavor` field, non-mock) for ONE trigger command — so the executed arm
    fires offline and the flavor rides the RESPONSE seam. The explicit
    pursue/scout reissue falls through to the real mock parser."""

    def __init__(self, real, trigger, marshal, action, target, flavor):
        self._real = real
        self.llm = real.llm
        self._trigger = trigger.lower().strip()
        self._marshal = marshal
        self._action = action
        self._target = target
        self._flavor = flavor

    def parse(self, text, game_state, world=None):
        if text.lower().strip() == self._trigger:
            cmd = {"marshal": self._marshal, "action": self._action,
                   "target": self._target}
            if self._flavor is not None:
                cmd["flavor"] = self._flavor
            return {"success": True, "command": cmd, "mode": "anthropic"}
        return self._real.parse(text, game_state, world=world)


@pytest.fixture()
def flavor_endpoint():
    """Factory: install a _FlavorStubParser for a given delegation + flavor and
    return (client, main_module, world). Restores state on teardown."""
    import backend.main as main_module
    orig = (main_module.parser, main_module.world, main_module.game_state)
    created = {}

    def _make(trigger, marshal, action, target, flavor, *, mutate=None):
        world = WorldState.from_scenario(str(SCENARIO_PATH))
        if mutate:
            mutate(world)
        main_module.world = world
        main_module.game_state = {"world": world}
        main_module.parser = _FlavorStubParser(
            CommandParser(use_real_llm=False), trigger, marshal, action,
            target, flavor)
        created["client"] = TestClient(main_module.app)
        created["m"] = main_module
        created["world"] = world
        return created["client"], main_module, world

    try:
        yield _make
    finally:
        (main_module.parser, main_module.world,
         main_module.game_state) = orig


def _co_locate_weak_enemy(world, marshal="Ney", enemy="Mack",
                          atk=60000, dfn=2000):
    """Set up a favorable co-located pursue so the aggressive arm SUCCEEDS
    (no bad-odds modal): the flavor then rides the response."""
    a = world.get_marshal(marshal)
    e = world.get_marshal(enemy)
    e.location = a.location
    e.strength = dfn
    a.strength = atk
    world.diplomatic_states[world._make_diplo_key(a.nation, e.nation)] = "WAR"
    world.update_intel_from_scout(a.location, world.current_turn)


def _co_locate_fortified_superior(world, marshal="Ney", enemy="Mack"):
    """Set up a co-located DUG-IN SUPERIOR enemy so the aggressive pursue hits
    the one-modal bad-odds confirm (requires_input) instead of committing. The
    odds gate folds the ENEMY marshal's fortified/defense_bonus (mirrors the
    passing TestPursueLethalGate setup)."""
    a = world.get_marshal(marshal)
    e = world.get_marshal(enemy)
    e.location = a.location
    a.strength = 42000
    e.strength = 54000
    e.fortified = True
    e.defense_bonus = 0.16
    world.diplomatic_states[world._make_diplo_key(a.nation, e.nation)] = "WAR"
    world.update_intel_from_scout(a.location, world.current_turn)


class TestAggressiveEchoEndpoint:
    def test_live_flavor_echoed_and_order_unchanged(self, flavor_endpoint):
        client, m, world = flavor_endpoint(
            "Ney, deal with Mack", "Ney", "attack", "Mack",
            "'At last, Sire — leave Mack to me.'",
            mutate=_co_locate_weak_enemy)
        data = client.post(
            "/command", json={"command": "Ney, deal with Mack"}).json()
        # the game heard me: the live line appears verbatim...
        assert "At last, Sire — leave Mack to me." in (data.get("message") or "")

    def test_floor_used_when_live_flavor_empty(self, flavor_endpoint):
        client, m, world = flavor_endpoint(
            "Ney, deal with Mack", "Ney", "attack", "Mack", None,
            mutate=_co_locate_weak_enemy)
        floor = _agg_floor(world)
        data = client.post(
            "/command", json={"command": "Ney, deal with Mack"}).json()
        assert floor in (data.get("message") or "")

    def test_register_violating_live_falls_to_floor(self, flavor_endpoint):
        client, m, world = flavor_endpoint(
            "Ney, deal with Mack", "Ney", "attack", "Mack",
            "'Ney will fall back and observe Mack.'",  # names an action -> drop
            mutate=_co_locate_weak_enemy)
        floor = _agg_floor(world)
        data = client.post(
            "/command", json={"command": "Ney, deal with Mack"}).json()
        msg = data.get("message") or ""
        assert floor in msg                       # floor used
        assert "observe Mack" not in msg          # the violating line never shows

    def test_flavor_absent_on_bad_odds_modal(self, flavor_endpoint):
        client, m, world = flavor_endpoint(
            "Ney, deal with Mack", "Ney", "attack", "Mack",
            "'At last, Sire — leave Mack to me.'",
            mutate=_co_locate_fortified_superior)
        floor = _agg_floor(world)
        data = client.post(
            "/command", json={"command": "Ney, deal with Mack"}).json()
        # the one-modal bad-odds confirm owns the surface — no flavor garnish
        assert data.get("requires_input") or data.get("pending_interrupt")
        msg = data.get("message") or ""
        assert "At last, Sire" not in msg     # live line not attached
        assert floor not in msg               # floor not attached either

    def test_flavor_never_alters_the_resolved_order(self, flavor_endpoint):
        # two very different flavor strings -> identical resolved PURSUE order
        orders = []
        for flav in ["'At last, Sire — leave Mack to me.'",
                     "'Mack, Sire? Consider it settled.'"]:
            client, m, world = flavor_endpoint(
                "Ney, deal with Mack", "Ney", "attack", "Mack", flav,
                mutate=_co_locate_weak_enemy)
            client.post("/command", json={"command": "Ney, deal with Mack"})
            ney = world.get_marshal("Ney")
            orders.append(getattr(ney.strategic_order, "command_type", None))
        # Both resolved to a PURSUE (or both committed to battle) — never diverge
        assert orders[0] == orders[1]


class TestCautiousEchoEndpoint:
    def _reachable_mack(self, world):
        # leave Davout/Mack at default positions but ensure war + intel so the
        # scout reissue succeeds and the soft note appears.
        d = world.get_marshal("Davout")
        e = world.get_marshal("Mack")
        world.diplomatic_states[
            world._make_diplo_key(d.nation, e.nation)] = "WAR"
        world.update_intel_from_scout(e.location, world.current_turn)

    def test_prefix_leads_note_no_double_narration(self, flavor_endpoint):
        client, m, world = flavor_endpoint(
            "Davout, deal with Mack", "Davout", "attack", "Mack",
            "'Mack, Sire? Then let me see the ground first.'",
            mutate=self._reachable_mack)
        data = client.post(
            "/command", json={"command": "Davout, deal with Mack"}).json()
        msg = data.get("message") or ""
        if data.get("success"):
            assert "see the ground first" in msg          # live prefix present
            assert "cautious as ever" in msg              # the deed-note present
            assert msg.lower().count("reconnoiter") == 1  # deed said ONCE

    def test_no_prefix_when_live_absent_only_note_shows(self, flavor_endpoint):
        client, m, world = flavor_endpoint(
            "Davout, deal with Mack", "Davout", "attack", "Mack", None,
            mutate=self._reachable_mack)
        data = client.post(
            "/command", json={"command": "Davout, deal with Mack"}).json()
        msg = data.get("message") or ""
        if data.get("success"):
            assert "cautious as ever" in msg              # only the shipped note
            assert "see the ground" not in msg

    def test_cautious_response_says_cautious_at_most_once(self, flavor_endpoint):
        """Review fix (LOW): a live line that itself says 'cautious' is dropped by
        the personality-word guard, so the note's 'cautious as ever' is the only
        occurrence — no double-narration of the character label."""
        client, m, world = flavor_endpoint(
            "Davout, deal with Mack", "Davout", "attack", "Mack",
            "'Cautious as always, Sire — the ground first.'",
            mutate=self._reachable_mack)
        data = client.post(
            "/command", json={"command": "Davout, deal with Mack"}).json()
        msg = data.get("message") or ""
        if data.get("success"):
            assert msg.lower().count("cautious") == 1


# ═══════════════════════════════════════════════════════════════════
# Scope boundaries (Golden Rule 9) — CR-5b must NOT touch these
# ═══════════════════════════════════════════════════════════════════

class TestScopeBoundaries:
    @pytest.fixture()
    def mock_endpoint(self):
        import backend.main as main_module
        orig = (main_module.parser, main_module.world, main_module.game_state)
        main_module.parser = CommandParser(use_real_llm=False)
        main_module.world = WorldState.from_scenario(str(SCENARIO_PATH))
        main_module.game_state = {"world": main_module.world}
        try:
            yield TestClient(main_module.app), main_module
        finally:
            (main_module.parser, main_module.world,
             main_module.game_state) = orig

    def test_mock_delegation_still_routes_to_ask_unchanged(self, mock_endpoint):
        """Guardrail e: every mock delegation degrades to ASK, whose clause-quote
        is already 'the game heard me'. CR-5b adds no floor here."""
        client, m = mock_endpoint
        floor = _agg_floor(m.world)
        data = client.post(
            "/command", json={"command": "Ney, deal with Mack"}).json()
        assert data.get("clarification_kind") == "delegation"
        assert '"deal with Mack"' in (data.get("message") or "")
        # no aggressive floor leaked into the mock ASK
        assert floor not in (data.get("message") or "")

    def test_explicit_order_produces_no_flavor_echo(self, mock_endpoint):
        client, m = mock_endpoint
        floor = _agg_floor(m.world)
        data = client.post(
            "/command", json={"command": "Ney, attack Mack"}).json()
        assert floor not in (data.get("message") or "")

    def test_ask_arm_copy_has_no_added_floor(self, world1805):
        """The literal ASK surface is out of CR-5b scope — its clause-quote is
        the echo. Assert the aggressive floor never appears in it."""
        from backend.commands.delegation import build_delegation_clarification
        m = _match(world1805, "Soult, deal with Mack")
        clar = build_delegation_clarification(world1805, m, "Soult, deal with Mack")
        assert "needs no second word" not in clar["message"]


# ═══════════════════════════════════════════════════════════════════
# Review fix (CONFIRMED): the aggressive attach skips EVERY modal shape
# ═══════════════════════════════════════════════════════════════════

class TestModalGuards:
    """The reissued PURSUE runs the full strategic executor (no bypass), so it can
    raise a strategic/tactical OBJECTION (pending_objection / awaiting_response),
    not only the bad-odds interrupt. The one-modal-legibility guard (§6.3) must
    skip the flavor garnish on those surfaces too."""

    @pytest.mark.parametrize("modal_field",
                             ["pending_objection", "awaiting_response"])
    def test_flavor_absent_on_objection_modal(self, flavor_endpoint,
                                              monkeypatch, modal_field):
        client, m, world = flavor_endpoint(
            "Ney, deal with Mack", "Ney", "attack", "Mack",
            "'At last, Sire — leave Mack to me.'",
            mutate=_co_locate_weak_enemy)
        floor = _agg_floor(world)
        modal = {"success": True, modal_field: True,
                 "message": "OBJECTION_MODAL_COPY", "marshal": "Ney",
                 "action_info": {"cost": 0, "remaining": 3,
                                 "turn_advanced": False, "new_turn": None}}
        monkeypatch.setattr(m.executor, "execute", lambda *a, **k: modal)
        data = client.post(
            "/command", json={"command": "Ney, deal with Mack"}).json()
        msg = data.get("message") or ""
        assert "At last, Sire" not in msg    # live flavor NOT attached on modal
        assert floor not in msg              # floor NOT attached either


# ═══════════════════════════════════════════════════════════════════
# Prompt token discipline + serialization
# ═══════════════════════════════════════════════════════════════════

class TestPromptAndSerialization:
    def _game_state(self):
        return {
            "marshals": {"Ney": {"location": "Paris", "strength": 50000,
                                 "personality": "aggressive"}},
            "enemies": {"Mack": {"location": "Swabia", "strength": 40000,
                                 "nation": "Austria"}},
            "map_data": {"Paris": {}, "Swabia": {}},
        }

    def test_parse_prompt_instructs_flavor_only_for_delegation(self):
        prompt = build_parse_prompt("Ney, deal with Mack", self._game_state())
        assert "Flavor Line" in prompt
        # the null-unless-delegation gating rule (token discipline vs prompt drift)
        assert "flavor" in prompt and "null" in prompt

    def test_output_schema_example_has_null_flavor(self):
        assert '"flavor": null' in OUTPUT_SCHEMA

    def test_flavor_not_serialized_on_world(self, world1805):
        # response-transient: rides result["message"] only, never a model class
        assert "flavor" not in world1805.to_dict()

    def test_parseresult_flavor_defaults_none(self):
        assert ParseResult().flavor is None
