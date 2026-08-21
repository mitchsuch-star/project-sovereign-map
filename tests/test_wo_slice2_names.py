"""WO slice 2 — "The Names" (WEIRD_OUTCOMES_SPEC §3 slice 2).

WO-1 + WO-2: the two P1s are one defect on two name registers — *the player
names a thing and the game acts on something else.*

* **WO-1** — naming an ENEMY marshal as the ADDRESSEE executed the order on
  the FRENCH army: the CR-1 demotion (`parser.py` `_apply_fuzzy_matching`)
  stripped the recognised enemy addressee to a target reference, and the
  marshal-less classification routed the bare verb army-wide. `Kutuzov,
  retreat` moved 8 corps including Napoleon; `Mack, attack Vienna` sent the
  whole army at Swabia; `Kutuzov, scout Swabia` made Soult scout. The fix:
  an enemy name in the LEADING (addressee) position refuses by name, for
  all verbs, in voice — while the demotion survives for target-position
  extraction (`attack Kutuzov` keeps working, pinned below).

* **WO-2** — the two ungated `auto_correct` arms of the target precedence
  ladder + the strategic-marshal sibling + the executor's
  `_fuzzy_match_region` backstop promoted partial-ratio junk into real
  places and marched there: `Avalon→Leon` (a 2-AP standing order eight
  provinces into Spain), `Moon→Moore`, `Hell→Hohenlohe`. All four now carry
  the project's own `_plausible_name_typo` gate, exactly as their gated
  siblings do; a gated-out backstop correction becomes a QUESTION, never a
  march. Plausible typos (`Swabai`, `viena`) still march.
"""

from pathlib import Path

import pytest

from backend.commands.executor import CommandExecutor
from backend.commands.parser import CommandParser
from backend.models.world_state import WorldState

SCENARIO_PATH = (
    Path(__file__).resolve().parents[1]
    / "godot-client" / "project-sovereign" / "assets" / "maps"
    / "europe_1805.json"
)


@pytest.fixture(scope="module")
def world1805():
    return WorldState.from_scenario(str(SCENARIO_PATH))


@pytest.fixture(scope="module")
def parser():
    return CommandParser(use_real_llm=False)


def _llm_game_state(world):
    """Production-shaped game_state (mirrors main.get_llm_game_state incl.
    the fog filter) — same helper the CR-0 roster tests use."""
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


# ═══════════════════════════════════════════════════════════════════
# WO-1 — the enemy addressee refuses by name
# ═══════════════════════════════════════════════════════════════════

class TestEnemyAddresseeRefuses:
    @pytest.mark.parametrize("command", [
        "Kutuzov, retreat",
        "Kutuzov retreat",          # no comma — byte-identical behaviour
        "Mack, retreat",
        "Moore, retreat",
        "Kutuzov, defend",
    ])
    def test_enemy_addressee_refuses_all_verbs(self, parser, world1805,
                                               gs1805, command):
        result = parser.parse(command, gs1805, world=world1805)
        assert result["success"] is False, (
            f"'{command}' must refuse — it executed army-wide before WO-1")
        assert result.get("kind") == "enemy_addressee", result
        assert "does not answer" in result["error"]

    def test_mack_attack_vienna_refuses(self, parser, world1805, gs1805):
        """The measured horror: `Mack, attack Vienna` sent the whole French
        army at Swabia. It refuses now."""
        result = parser.parse("Mack, attack Vienna", gs1805, world=world1805)
        assert result["success"] is False
        assert result.get("kind") == "enemy_addressee"
        assert "Mack" in result["error"]

    def test_enemy_scout_no_longer_reassigns(self, parser, world1805, gs1805):
        """`Kutuzov, scout Swabia` used to make SOULT scout via the
        demotion + auto-assign sibling."""
        result = parser.parse("Kutuzov, scout Swabia", gs1805,
                              world=world1805)
        assert result["success"] is False
        assert result.get("kind") == "enemy_addressee"

    def test_refusal_names_the_side(self, parser, world1805, gs1805):
        result = parser.parse("Mack, retreat", gs1805, world=world1805)
        assert "Austria" in result["error"], result["error"]
        result = parser.parse("Kutuzov, retreat", gs1805, world=world1805)
        assert "Russia" in result["error"], result["error"]

    def test_honorific_form_refuses_too(self, parser, world1805, gs1805):
        result = parser.parse("Marshal Kutuzov, retreat", gs1805,
                              world=world1805)
        assert result["success"] is False
        assert result.get("kind") == "enemy_addressee"

    def test_enemy_typo_addressee_refuses(self, parser, world1805, gs1805):
        """An edit-distance addressee typo still resolves to the enemy and
        refuses by the resolved name."""
        result = parser.parse("Kutuzof, retreat", gs1805, world=world1805)
        assert result["success"] is False
        assert result.get("kind") == "enemy_addressee"
        assert "Kutuzov" in result["error"]


class TestDemotionLegitimateCasePinned:
    """The CR-1 demotion's legitimate case MUST survive: an enemy name in
    TARGET position is a target reference."""

    def test_attack_enemy_still_targets(self, parser, world1805, gs1805):
        result = parser.parse("attack Mack", gs1805, world=world1805)
        assert result["success"], result.get("error")
        assert result["command"]["target"] == "Mack"
        assert result["command"]["marshal"] is None

    def test_addressed_pursue_still_targets(self, parser, world1805, gs1805):
        result = parser.parse("Soult, pursue Kutuzov", gs1805,
                              world=world1805)
        assert result["success"], result.get("error")
        assert result["command"]["target"] == "Kutuzov"

    def test_bare_retreat_still_army_wide(self, parser, world1805, gs1805):
        """The bare verb keeps its army-wide form — WO-1 removes the enemy
        ADDRESSEE route into it, not the form itself."""
        result = parser.parse("retreat", gs1805, world=world1805)
        assert result["success"], result.get("error")
        assert result["command"]["type"] == "general_retreat"

    def test_invented_name_guard_unchanged(self, parser, world1805, gs1805):
        """PC15-4's sibling stays byte-identical: an INVENTED addressee gets
        the not-found refusal, never the enemy refusal."""
        result = parser.parse("Zorblax, retreat", gs1805, world=world1805)
        assert result["success"] is False
        assert result.get("kind") != "enemy_addressee"


# ═══════════════════════════════════════════════════════════════════
# WO-2 — the typo gates
# ═══════════════════════════════════════════════════════════════════

class TestParserTargetGates:
    def test_avalon_not_rewritten_to_leon(self, parser, world1805, gs1805):
        """The parser must not silently rewrite Avalon→Leon (first letters
        differ — not a typo shape)."""
        result = parser.parse("Ney, move to Avalon", gs1805, world=world1805)
        target = (result.get("command") or {}).get("target")
        assert target != "Leon", (
            "Avalon must not auto-correct to Leon at the parse seam")

    def test_plausible_typo_still_marches(self, parser, world1805, gs1805):
        result = parser.parse("Ney, move to Swabai", gs1805, world=world1805)
        assert result["success"], result.get("error")
        assert result["command"]["target"] == "Swabia"

    def test_strategic_marshal_junk_not_bound(self, parser, world1805,
                                              gs1805):
        """'Mars' must not bind to a real commander through the
        strategic-marshal arm (first letters differ from 'Damas')."""
        result = parser.parse("Ney, pursue Mars", gs1805, world=world1805)
        target = (result.get("command") or {}).get("target")
        assert target != "Damas"


class TestGuardBoundaries:
    """The Aug-21 review round's false-positive boundaries: narration
    leads, common-word comma-typo binds, and the player roster's right of
    first refusal on typo'd addresses."""

    @pytest.mark.parametrize("command,should_parse", [
        # Narration lead + explicit player addressee — the pre-guard parse
        # was fully correct and must survive.
        ("Mack is at Swabia, Ney attack him", True),
        ("Mack holds Ulm, Ney attack him", True),
        ("Kutuzov approaches, fortify", None),   # not refused as enemy
        ("Mack has surrendered, march on Vienna", None),
    ])
    def test_narration_leads_are_not_addresses(self, parser, world1805,
                                               gs1805, command,
                                               should_parse):
        result = parser.parse(command, gs1805, world=world1805)
        assert result.get("kind") != "enemy_addressee", (
            f"'{command}' is narration, not an address: {result.get('error')}")
        if should_parse:
            assert result["success"], result.get("error")

    def test_common_word_comma_lead_never_binds_enemy(self, parser,
                                                      world1805, gs1805):
        """'More, cavalry to the front' must never become Moore — the
        typo arm screens ordinary English (_NON_TARGET_WORDS)."""
        result = parser.parse("More, cavalry to the front", gs1805,
                              world=world1805)
        assert result.get("kind") != "enemy_addressee", result

    def test_player_roster_gets_first_refusal_on_typo(self, parser,
                                                      world1805, gs1805):
        """'Mark, attack Vienna' belongs to the CR-2 did-you-mean flow
        (Murat), never to an enemy refusal (Mack)."""
        result = parser.parse("Mark, attack Vienna", gs1805, world=world1805)
        assert result.get("kind") != "enemy_addressee", result

    def test_typo_addressee_still_refuses_when_unambiguous(self, parser,
                                                           world1805,
                                                           gs1805):
        result = parser.parse("Kutuzof, retreat", gs1805, world=world1805)
        assert result.get("kind") == "enemy_addressee"

    def test_suggestion_names_the_intel_road(self, parser, world1805,
                                             gs1805):
        result = parser.parse("Mack, retreat", gs1805, world=world1805)
        assert "where is Mack" in (result.get("suggestion") or "")


@pytest.fixture()
def wire_1805():
    """Real /command surface on the 1805 boot (the PC15 endpoint idiom —
    the module-global world/parser/executor swapped and restored)."""
    from fastapi.testclient import TestClient

    from backend.commands.executor import CommandExecutor
    import backend.main as main_module

    saved = (main_module.parser, main_module.world,
             main_module.game_state, main_module.executor)
    main_module.parser = CommandParser(use_real_llm=False)
    main_module.world = WorldState.from_scenario(str(SCENARIO_PATH))
    main_module.game_state = {"world": main_module.world}
    main_module.executor = CommandExecutor()
    try:
        yield TestClient(main_module.app), main_module
    finally:
        (main_module.parser, main_module.world,
         main_module.game_state, main_module.executor) = saved


class TestReviewFindingsOnTheWire:
    """The Aug-21 review fleet's three holes, pinned at the surface that
    exposed them — the parser-level tests above were green while the wire
    swallowed or bypassed the refusal."""

    def test_refusal_reaches_the_wire_verbatim(self, wire_1805):
        """P1: the refusal carried candidates=[] so the CR-2 arm skipped it
        and the generic Berthier recovery replaced it — the by-name refusal
        was production-dead on /command."""
        client, m = wire_1805
        before = {x.name: x.location for x in m.world.get_player_marshals()}
        resp = client.post("/command",
                           json={"command": "Kutuzov, retreat"}).json()
        assert resp.get("success") is False
        assert "does not answer to us" in (resp.get("message") or ""), resp
        assert "Kutuzov" in resp["message"]
        after = {x.name: x.location for x in m.world.get_player_marshals()}
        assert before == after, "no French corps may move on a refusal"

    def test_vassal_family_addressee_refuses(self, wire_1805):
        """P1: the vassal-family early-return discarded the enemy addressee
        and EXECUTED — 'Kutuzov, grant Holland more autonomy' permanently
        cut Holland's tribute."""
        client, m = wire_1805
        resp = client.post(
            "/command",
            json={"command": "Kutuzov, grant Holland more autonomy"}).json()
        assert resp.get("success") is False
        assert "does not answer to us" in (resp.get("message") or ""), resp

    def test_diplomatic_addressee_refuses(self, wire_1805):
        """P2: the diplomatic early-return ran before the guard — 'Mack,
        declare war on Prussia' staged the war-purpose ceremony."""
        client, m = wire_1805
        resp = client.post(
            "/command",
            json={"command": "Mack, declare war on Prussia"}).json()
        assert resp.get("success") is False
        assert "does not answer to us" in (resp.get("message") or ""), resp

    def test_unaddressed_diplomacy_still_works(self, wire_1805):
        """Control: the guard must not touch ordinary diplomacy."""
        client, m = wire_1805
        resp = client.post(
            "/command",
            json={"command": "improve relations with Prussia"}).json()
        assert "does not answer to us" not in (resp.get("message") or "")


class TestExecutorBackstopGate:
    """executor._fuzzy_match_region — the live backstop: gate the parser
    alone and `move to the Moon` still marched ten provinces to Morocco."""

    @pytest.fixture(scope="class")
    def executor(self):
        return CommandExecutor()

    def test_implausible_correction_becomes_question(self, executor,
                                                     world1805):
        region, error = executor._fuzzy_match_region("Avalon", world1805)
        assert region is None
        assert error is not None
        assert "Avalon" in error["message"]

    def test_moon_does_not_march_to_morocco(self, executor, world1805):
        region, error = executor._fuzzy_match_region("Moon", world1805)
        assert region is None or region.name != "Morocco"

    def test_plausible_typos_still_correct(self, executor, world1805):
        region, error = executor._fuzzy_match_region("Swabai", world1805)
        assert region is not None and region.name == "Swabia"
        region, error = executor._fuzzy_match_region("viena", world1805)
        assert region is not None and region.name == "Vienna"

    def test_exact_names_unchanged(self, executor, world1805):
        region, error = executor._fuzzy_match_region("Swabia", world1805)
        assert region is not None and region.name == "Swabia"
