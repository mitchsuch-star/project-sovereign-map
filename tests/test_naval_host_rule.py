"""NV-4 THE HOST RULE + NV-5 THE AI'S NAVAL LIFE (DEF-5, docs/NAVAL_SPEC.md
§4.1a / §6) — the August 2, 2026 user-gated pass.

The gate question was "does Normandy make sense for England to land at, and
how do we abstract them entering on Portugal IRL?" and the answer built
here is the HOST RULE: an army does not march onto a defended coast. The
crossing gate now reads the far SHORE as well as the water, so the two
doors onto hostile soil are the two history used — a ≤15,000-man expedition
that can be caught at sea, or a fleet action that clears the covering
squadron. Landing where a host receives you (Portugal, 1808) was never
gated, and is how Britain's army reaches the Continent at all.

Measured defects this file pins closed (16-turn ambient probe, historical
seed, the tools/ai_v_sweep.py idiom):
  * Moore walked 30,000 men onto French soil at Normandy on turn 1 — TWICE
    the transports' cap — and stood in Berry by turn 2.
  * `naval_expedition` was therefore strictly dominated: nobody rolls odds
    with 15k when 30k marches for free.
  * A blockaded Spain laid a keel EVERY turn forever (30 → 44 sail by turn
    16, ~70 by turn 40) for +2.5 effective points.
  * Two AI rungs — P4.5 undefended capture and P4.25 garrison assault —
    were missed by NV-2's candidate threading entirely, so the council
    re-ordered a barred crossing every other turn for the whole run.
"""
import os

import pytest

from backend.ai.enemy_ai import EnemyAI
from backend.commands.executor import CommandExecutor
from backend.game_logic import naval
from backend.models.world_state import WorldState

SCENARIO = os.path.join(
    "godot-client", "project-sovereign", "assets", "maps", "europe_1805.json")


@pytest.fixture(scope="module")
def _booted():
    return WorldState.from_scenario(SCENARIO)


@pytest.fixture()
def world(_booted):
    return WorldState.from_dict(_booted.to_dict())


@pytest.fixture()
def ai():
    return EnemyAI(CommandExecutor())


def _game_state(world):
    return {"world": world}


# ═══════════════════════════════════════════════════════════════════════
# §4.1a — the rule itself
# ═══════════════════════════════════════════════════════════════════════

class TestTheHostRule:
    def test_the_predicate_reads_the_shore_not_the_mover(self, world):
        """`is_hostile_shore` is the ONE reading of "opposed": own soil, an
        ally's soil and a neutral's soil are all hosts."""
        assert naval.is_hostile_shore(world, "Britain", "Normandy") is True
        assert naval.is_hostile_shore(world, "Britain", "Flanders") is True
        assert naval.is_hostile_shore(world, "Britain", "Lisbon") is False
        assert naval.is_hostile_shore(world, "Britain", "London") is False
        # ...and it is symmetric, because it is one predicate (GR5).
        assert naval.is_hostile_shore(world, "France", "London") is True
        assert naval.is_hostile_shore(world, "France", "Normandy") is False

    def test_a_defended_coast_refuses_the_march(self, world):
        verdict = naval.crossing_check(world, "Britain", "London", "Normandy")
        assert verdict["allowed"] is False
        assert verdict["verdict"] == "landing"

    def test_the_refusal_names_a_door_that_exists(self, world):
        """§10's standing rule — refusal copy states present-tense facts and
        points at live verbs only. Both answers it gives are real: the
        transports (with their real cap quoted) and breaking the fleet."""
        message = naval.crossing_check(
            world, "Britain", "London", "Normandy")["message"]
        assert f"{naval.EXPEDITION_MAX_TROOPS:,}" in message
        assert "transports" in message
        assert "Normandy" in message
        # Never a feature reference or a "not yet" — the §10 copy scan.
        for banned in ("coming soon", "not yet implemented", "future"):
            assert banned not in message.lower()

    def test_the_ratio_arm_still_wins_when_it_bites(self, world):
        """Precedence: a mover the WATER has already turned back hears the
        stronger, truer refusal — the host rule can only ever change the
        verdict for someone who already commands the sea. That is what
        keeps the blast radius to the one case it was built for."""
        verdict = naval.crossing_check(world, "France", "Normandy", "London")
        assert naval.is_hostile_shore(world, "France", "London") is True
        assert verdict["verdict"] == "shut"      # not "landing"
        assert verdict["coverer"] == "Britain"

    def test_uncontested_water_is_an_administrative_ferry(self, world):
        """The rule's own escape hatch, and why it is not a wall."""
        assert naval.crossing_check(
            world, "Britain", "London", "Normandy")["verdict"] == "landing"
        naval.get_fleet(world, "France")["ships"] = 0
        after = naval.crossing_check(world, "Britain", "London", "Normandy")
        assert after["allowed"] is True

    def test_a_window_waives_it(self, world):
        """§5.3 — drawing the enemy off station IS the moment the army
        crosses. The Descent would be unwinnable if the host rule outlived
        the window it exists alongside."""
        naval.get_fleet(world, "France")["window_turns"] = 2
        verdict = naval.crossing_check(world, "France", "Normandy", "London")
        assert verdict["verdict"] != "landing"

    def test_a_beachhead_is_supplied_by_sea(self, world):
        """Once the shore is OURS the link is ours: the host rule gates the
        first landing, never the reinforcement of one that succeeded. The
        Lines of Torres Vedras, not a one-shot raid."""
        assert naval.crossing_check(
            world, "Britain", "London", "Normandy")["verdict"] == "landing"
        world.regions["Normandy"].controller = "Britain"
        world.invalidate_active_nations_cache()
        after = naval.crossing_check(world, "Britain", "London", "Normandy")
        assert after["allowed"] is True

    def test_the_executor_seam_carries_the_refusal(self, world):
        """The player meets the same rule at the movement seam, with the
        PF-8 structured flag a strategic march reads."""
        british = world.get_marshals_by_nation("Britain")
        marshal = british[0]
        marshal.location = "London"
        world._build_marshal_index()
        executor = CommandExecutor()
        result = executor._movement._execute_move(
            marshal, "Normandy", world, _game_state(world))
        assert result["success"] is False
        assert result.get("blocked_naval") == "France"


class TestTheCrossingsBoard:
    def test_the_board_reads_the_players_own_direction(self, world):
        """NV-4 made the gate directional, so the Crossings board must
        evaluate the way the player would actually travel — outward from
        the end we hold — or it reports the wrong shore."""
        verdicts = naval.link_verdicts(world)
        key = "|".join(sorted(["London", "Normandy"]))
        assert key in verdicts
        # France holds Normandy, so France's direction is Normandy → London.
        assert verdicts[key]["from_region"] == "Normandy"
        assert verdicts[key]["to_region"] == "London"

    def test_a_defended_shore_is_not_reported_as_a_lost_sea(self, world):
        """The line must not say SHUT — the water is ours. A player who
        reads a naval defeat that never happened builds the wrong fleet."""
        world.player_nation = "Britain"
        report = naval.build_admiralty_report(world)
        lines = [c["line"] for c in report["crossings"]
                 if c["verdict"] == "landing"]
        assert lines, "Britain's own board should show a defended shore"
        assert any("DEFENDED SHORE" in ln for ln in lines)
        assert not any("SHUT" in ln for ln in lines)


# ═══════════════════════════════════════════════════════════════════════
# §6 — NV-5, the AI's naval life
# ═══════════════════════════════════════════════════════════════════════

class TestTheExpeditionRung:
    def test_britain_is_penned_in_and_knows_it(self, world):
        """Britain holds no province with a land border onto a court it is
        at war with — its army reaches the war only by sea. France, at war
        along its whole eastern frontier, is not penned."""
        assert naval.nation_is_penned_in(world, "Britain") is True
        assert naval.nation_is_penned_in(world, "France") is False

    def test_the_council_sails_for_a_host_not_a_beach(self, world):
        """THE ANSWER TO THE GATE QUESTION. Britain's expedition targets
        Lisbon — a shore that will receive it and that borders the war —
        rather than storming Normandy. Measured live: `expedition_landed`
        at Lisbon on turn 11 of the ambient run, then Galicia → Asturias →
        Bordelais by turn 15. Mondego Bay, 1808."""
        british = world.get_marshals_by_nation("Britain")
        marshal = british[0]
        marshal.location = "London"          # a controlled dockyard
        marshal.strength = 12000             # inside the transports' lift
        world._build_marshal_index()
        order = naval.find_ai_expedition(world, "Britain")
        assert order is not None
        assert order["action"] == "naval_expedition"
        assert order["_acting_nation"] == "Britain"
        assert world.regions[order["target"]].controller == "Portugal"

    def test_a_host_must_actually_be_a_friend(self, world):
        """No army walks onto an indifferent neutral's soil. The shipped
        board reads exactly right through this filter: Portugal 40 and
        Naples 30 receive an army, Denmark/Hanover/Sardinia at 0 do not."""
        assert naval._is_expedition_host(world, "Britain", "Portugal") is True
        assert naval._is_expedition_host(world, "Britain", "Naples") is True
        assert naval._is_expedition_host(world, "Britain", "Denmark") is False
        assert naval._is_expedition_host(world, "Britain", "France") is False

    def test_the_council_reads_the_same_odds_the_player_is_quoted(self, world):
        """GR5 + IGR-E's shown=applied: the rung consults
        `expedition_slip_odds`, the one function the confirm dialog quotes
        and the resolver rolls against. A corps is never risked below the
        council's own floor."""
        british = world.get_marshals_by_nation("Britain")
        marshal = british[0]
        marshal.location = "London"
        marshal.strength = 12000
        world._build_marshal_index()
        order = naval.find_ai_expedition(world, "Britain")
        quote = naval.expedition_slip_odds(
            world, "Britain", order["target"], 12000)
        assert quote["odds"] >= naval.AI_EXPEDITION_MIN_ODDS

    def test_an_army_that_can_march_does_not_sail(self, world):
        """The rung is a door for the penned, not a teleporter. Give
        Britain a continental foothold with a land border onto the war and
        the council stops embarking."""
        world.regions["Normandy"].controller = "Britain"
        world.invalidate_active_nations_cache()
        assert naval.nation_is_penned_in(world, "Britain") is False
        assert naval.find_ai_expedition(world, "Britain") is None

    def test_a_corps_too_big_for_the_transports_stays_home(self, world):
        """Moore's 30,000 are over the lift, so Britain's expeditionary
        force is built from the corps that fit — which is why the home
        army sat in London through the ambient run, as it did until 1808."""
        for marshal in world.get_marshals_by_nation("Britain"):
            marshal.location = "London"
            marshal.strength = naval.EXPEDITION_MAX_TROOPS + 1
        world._build_marshal_index()
        assert naval.find_ai_expedition(world, "Britain") is None


class TestTheBuildCeiling:
    def test_the_establishment_is_recorded_at_boot(self, world):
        assert naval.get_fleet(world, "Spain")["established"] == 30
        assert naval.get_fleet(world, "Britain")["established"] == 100

    def test_the_council_stops_at_the_ceiling(self, world):
        """Measured: Spain's endless program now halts at 45 sail on turn
        18 and stays there, against 44-and-climbing at turn 16 before."""
        assert naval.ai_fleet_ceiling(world, "Spain") == 45
        world.nation_gold["Spain"] = 50_000
        assert naval.find_ai_build_fleet(world, "Spain", 50_000) is not None
        naval.get_fleet(world, "Spain")["ships"] = 45
        assert naval.find_ai_build_fleet(world, "Spain", 50_000) is None

    def test_a_naval_program_never_starves_the_army(self, world):
        """The reserve is a decision value, not a mechanic — the player's
        own brakes (gold, the rate cap, yards held) are untouched."""
        thin = naval.AI_FLEET_TREASURY_RESERVE * naval.SHIP_COST
        assert naval.find_ai_build_fleet(world, "Spain", thin) is None
        assert naval.find_ai_build_fleet(world, "Spain", thin + 1) is not None
        # The player at the same purse is refused for gold alone, by the
        # executor, at the real price — never by the council's reserve.
        assert naval.check_build_fleet(world, "Spain") is None

    def test_a_legacy_fleet_without_the_field_inherits_its_own_size(self, world):
        """Saves predate `established`; an older campaign gets a ceiling at
        its current size, never 0."""
        rec = naval.get_fleet(world, "Spain")
        del rec["established"]
        rec["ships"] = 40
        assert naval.ai_fleet_ceiling(world, "Spain") == 60


class TestTheRepairedCandidateFilters:
    """The two rungs NV-2's threading missed. Both were issuing orders the
    executor then refused — 20+ logged turn-backs across a 22-turn run,
    now 2 (the genuine mid-phase-change case the log line exists for)."""

    def test_undefended_capture_reads_the_crossing_gate(self, world, ai):
        british = world.get_marshals_by_nation("Britain")
        marshal = british[0]
        marshal.location = "London"
        world._build_marshal_index()
        world.regions["Normandy"].garrison_strength = 0
        assert ai._find_undefended_capture(marshal, "Britain", world) is None
        # Control: clear the covering fleet and the same rung offers it.
        naval.get_fleet(world, "France")["ships"] = 0
        offered = ai._find_undefended_capture(marshal, "Britain", world)
        assert offered is not None and offered["target"] == "Normandy"

    def test_garrison_assault_reads_the_crossing_gate(self, world, ai):
        british = world.get_marshals_by_nation("Britain")
        marshal = british[0]
        marshal.location = "London"
        marshal.strength = 30000
        marshal.artillery = False
        world._build_marshal_index()
        assert world.regions["Normandy"].garrison_strength == 12000
        assert ai._find_garrison_attack(marshal, "Britain", world) is None
        naval.get_fleet(world, "France")["ships"] = 0
        offered = ai._find_garrison_attack(marshal, "Britain", world)
        assert offered is not None and offered["target"] == "Normandy"


class TestTheContinentalSystemIsHonest:
    def test_the_boot_closure_declares_itself_inert(self, world):
        """38.5% closure against a 40% first notch: the headline was true
        and did nothing, with no way to tell from the surface."""
        world.player_nation = "France"
        cs = naval.build_admiralty_report(world)["continental_system"]
        assert cs["target"] == "Britain"
        assert cs["tier"] == 0
        assert cs["closure_pct"] == 38
        assert cs["next_tier_pct"] == 40
        assert cs["ports_to_next_tier"] >= 1

    def test_the_next_notch_is_a_reachable_count(self, world):
        """The figure has to be actionable: close that many more of the
        Continent's ports and the tier really does turn over."""
        world.player_nation = "France"
        cs = naval.build_admiralty_report(world)["continental_system"]
        needed = cs["ports_to_next_tier"]
        total = naval.continental_ports_total(world)
        closed_now = cs["closure_pct"] / 100.0 * total
        assert naval.cs_closure_tier((closed_now + needed) / total) >= 1
