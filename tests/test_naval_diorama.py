"""NV-7 — THE NAVAL DIORAMA (DEF-5 §10 row NV-D4, re-opened and built at the
August 2, 2026 user gate: "a battle screen like for battles?").

A fleet action was one line of terminal text, which is a poor fate for the
only battle in this game that can end a war in an afternoon. It now plays on
the same tableau the land battles get, in the same payload shape, rendered
by the same scene.

The mapping is the model, not a metaphor: a CONTINGENT is a pooled navy
(§4.4's resolver already bleeds every fleet that pooled on a side, so its
own per-nation loss dict IS the order of battle), COMMITTED is sail of the
line, CASUALTIES are ships taken or sunk, and the ARM is `ship`.
"""
import os

import pytest

from backend.game_logic import battle_diorama
from backend.game_logic import naval
from backend.game_logic import naval_diorama
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
def trafalgar(world):
    """The historical shape, on the shipped board: France's Combined Fleet
    brought to action by Britain's."""
    return naval.resolve_fleet_action(world, "France", "Britain",
                                      context="diversion")


class TestTheTableauIsBuiltAtTheResolver:
    def test_every_fleet_action_carries_its_picture(self, trafalgar):
        """Built at the ONE seam every fleet action passes through, so no
        caller can produce an action with no tableau — the BD §14.1 lesson
        (a link that drew dead because the stash lived somewhere else)."""
        assert trafalgar["naval_diorama"]

    def test_the_diversion_failure_hands_it_up(self, world):
        """The Trafalgar arm proper: the diversion caught coming home."""
        outcome = naval.resolve_diversion(world, "France")
        if outcome.get("window"):
            pytest.skip("this seed's diversion succeeded — no action fought")
        assert outcome["naval_diorama"]
        assert outcome["naval_diorama"]["context"] == "diversion"


class TestTheOrderOfBattle:
    def test_a_contingent_is_a_pooled_navy(self, trafalgar):
        """France's line is the Combined Fleet — Villeneuve, Gravina and
        Verhuell standing together, exactly as they did."""
        payload = trafalgar["naval_diorama"]
        nations = {c["nation"] for c in payload["attacker"]["contingents"]}
        assert "France" in nations
        assert {"Spain", "Holland"} & nations, (
            "the pooled allies must appear as their own squadrons")
        for contingent in payload["attacker"]["contingents"]:
            assert contingent["arm"] == "ship"

    def test_the_admiral_is_the_name_on_the_locket(self, trafalgar):
        payload = trafalgar["naval_diorama"]
        assert "Villeneuve" in {c["name"]
                                for c in payload["attacker"]["contingents"]}
        assert "Nelson" in {c["name"]
                            for c in payload["defender"]["contingents"]}

    def test_the_line_of_battle_is_the_pre_battle_strength(self, world):
        """The resolver has already applied the losses by the time the
        builder runs, so `committed` must be reconstructed as live+lost —
        otherwise the tableau shows the survivors as the order of battle."""
        before = int(naval.get_fleet(world, "France")["ships"])
        result = naval.resolve_fleet_action(world, "France", "Britain")
        after = int(naval.get_fleet(world, "France")["ships"])
        assert after < before, "this fixture needs France to actually lose sail"
        france = [c for c in result["naval_diorama"]["attacker"]["contingents"]
                  if c["nation"] == "France"][0]
        assert france["committed"] == before
        assert france["remaining"] == after
        assert france["casualties"] == before - after

    def test_the_totals_are_the_sum_of_the_line(self, trafalgar):
        for side in ("attacker", "defender"):
            payload = trafalgar["naval_diorama"][side]
            assert payload["casualties_total"] == sum(
                c["casualties"] for c in payload["contingents"])
            assert payload["committed_total"] == sum(
                c["committed"] for c in payload["contingents"])

    def test_a_squadron_that_is_mauled_strikes_her_colours(self):
        """`routed` is what topples a piece on the tableau — so the loss
        threshold has to be a real reading of "she struck", not a fraction
        picked to make something move."""
        assert naval_diorama._squadron(
            "Spain", 30, 12, False, "Gravina")["status"] == "routed"
        assert naval_diorama._squadron(
            "Britain", 100, 4, True, "Nelson")["status"] == "engaged"
        assert naval_diorama._squadron(
            "Naples", 5, 5, True, "")["status"] == "destroyed"


class TestTheRegister:
    def test_the_players_defeat_is_a_defeat(self, world, trafalgar):
        """§7 Q6 (the BD framing rule): the player's line is the near side
        and a loss reads as a gut-punch, not a mirrored enemy triumph."""
        assert world.player_nation == "France"
        payload = trafalgar["naval_diorama"]
        assert payload["player_side"] == "attacker"
        assert payload["victor"] == "Britain"
        assert payload["register"] == "defeat"

    def test_a_third_party_action_is_watched_not_suffered(self, world):
        """Fleet counts and postures are PUBLIC by the §9 recorded ruling
        (period newspapers printed orders of battle), so an action France
        is not in is watchable — in the observer register."""
        payload = naval.resolve_fleet_action(
            world, "Britain", "Denmark")["naval_diorama"]
        assert payload["player_side"] is None
        assert payload["register"] == "observer"

    def test_a_victory_reads_as_one(self, world):
        world.player_nation = "Britain"
        result = naval.resolve_fleet_action(world, "France", "Britain")
        assert result["naval_diorama"]["register"] == "triumph"


class TestTheCopy:
    def test_the_verdict_states_the_cost_in_hulls(self, trafalgar):
        payload = trafalgar["naval_diorama"]
        lost = payload["attacker"]["casualties_total"]
        assert f"{lost} sail lost" in payload["observation"]

    def test_the_loser_is_told_what_it_means(self, trafalgar):
        """A naval defeat's consequence is the crossing gate — say so, or
        the player reads a scoreline instead of a strategic fact."""
        assert "crossings" in trafalgar["naval_diorama"]["observation"]

    def test_the_plate_does_not_say_action_twice(self, trafalgar):
        """The waters ride the subtitle (§4.4 names an action by its
        combatants), so the plate must not repeat them: the first cut read
        "The Great Fleet Action — the France–Britain action"."""
        payload = trafalgar["naval_diorama"]
        assert payload["battle_name"].lower().count("action") == 1
        assert payload["waters"]

    def test_no_raw_nation_tag_reaches_the_prose(self, trafalgar):
        """R7 at the tableau: "the France line" is the wart this same pass
        already fixed once, in the crossing refusal."""
        observation = trafalgar["naval_diorama"]["observation"]
        assert "France line" not in observation
        assert "French line" in observation


class TestBothSurfacesOpen:
    def test_a_fleet_action_always_earns_the_screen(self, trafalgar):
        """There are exactly two ways to cause one (§4.4) and both stake a
        campaign on it — so unlike a land raid, neither predicate narrows."""
        payload = trafalgar["naval_diorama"]
        assert payload["significant"] is True
        assert payload["dramatic"] is True

    def test_the_payload_is_shaped_like_the_land_tableau(self, trafalgar):
        """One scene renders both, so the contract IS the shape."""
        payload = trafalgar["naval_diorama"]
        for key in ("battle_name", "turn", "outcome", "victor", "register",
                    "significant", "dramatic", "attacker", "defender",
                    "observation", "player_side", "region_conquered"):
            assert key in payload, f"the shared scene reads {key}"
        assert payload["register"] in ("triumph", "defeat", "grim", "observer")
        allowed = ("engaged", "routed", "destroyed") + \
            battle_diorama.ABSENT_STATUSES
        for side in ("attacker", "defender"):
            for contingent in payload[side]["contingents"]:
                for key in ("name", "nation", "arm", "committed",
                            "casualties", "remaining", "status", "lead"):
                    assert key in contingent
                assert contingent["status"] in allowed

    def test_the_field_is_never_conquered_at_sea(self, trafalgar):
        assert trafalgar["naval_diorama"]["region_conquered"] is False
        assert trafalgar["naval_diorama"]["region"] == ""

    def test_the_response_allowlist_carries_it(self):
        """A payload the /command response drops is a tableau that never
        opens — the most common wiring gap in this project."""
        import backend.main as main_module
        assert "naval_diorama" in main_module._COMMAND_RESULT_SIMPLE_FIELDS


class TestTheShipPieceExists:
    def test_all_four_layers_ship_in_both_facings(self):
        """The tableau renders `ship` through WarTablePiece's texture path,
        and a missing sprite silently falls back to infantry — a naval
        action would quietly show ranks of foot."""
        pieces = os.path.join("godot-client", "project-sovereign", "assets",
                              "ui", "pieces")
        for layer in ("shadow", "base", "coat", "body"):
            for facing in ("l", "r"):
                path = os.path.join(pieces, f"ship_{layer}_{facing}.png")
                assert os.path.exists(path), path
                assert os.path.getsize(path) > 0

    def test_the_client_knows_ship_is_a_valid_arm(self):
        gd = os.path.join("godot-client", "project-sovereign", "scenes",
                          "war_table_piece.gd")
        with open(gd, encoding="utf-8") as handle:
            source = handle.read()
        assert '"ship"' in source.split("VALID_ARMS")[1].split("]")[0]

    def test_the_generator_owns_the_ship(self):
        """The sprites are derived, not hand-placed pixels — the U4
        contract. If the generator loses the arm the art is unreproducible."""
        with open(os.path.join("tools", "gen_war_table_pieces.py"),
                  encoding="utf-8") as handle:
            source = handle.read()
        assert "def build_ship(" in source
        assert '"ship": build_ship' in source

    def test_the_map_never_draws_a_ship(self):
        """Q1(a) keeps the naval model to one national fleet record, so
        there is nothing on the map for a ship standee to BE — the U5
        display-only `arm` field must never carry it."""
        with open(os.path.join("backend", "models", "marshal.py"),
                  encoding="utf-8") as handle:
            assert '"ship"' not in handle.read()


class TestTheEnemyPhaseCarriesTheSea:
    def test_the_stash_scans_the_naval_key_too(self):
        """The enemy-phase stash originally read only , so
        a fleet action fought in the enemy phase (the player's fleet
        intercepting an AI expedition, an AI diversion caught) could never
        auto-play. The passthrough itself was already safe —
        _build_visible_enemy_phase strips only  — so the gap was
        purely the client scan. Static source pin, the U5 idiom."""
        import os
        gd = os.path.join("godot-client", "project-sovereign", "scripts",
                          "main.gd")
        with open(gd, encoding="utf-8") as handle:
            source = handle.read()
        stash = source.split("func _stash_diorama")[1].split("func ")[0]
        assert 'action.get("naval_diorama")' in stash
        assert 'action.get("battle_diorama")' in stash
