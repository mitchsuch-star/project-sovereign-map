"""Row WO, slice 10 - "The Enemy-Direction Gate" (WO-13).

Landing record: docs/WEIRD_OUTCOMES_SPEC.md section 3 slice 10.

Three name-resolution seams in `backend/commands/executor.py` auto-corrected
a query onto a MARSHAL with no typo gate, while their region sibling
(`_fuzzy_match_region`) has been gated since WO-2. The fuzzy matcher scores
by partial ratio, which rewards a short word for being CONTAINED in a long
name, so on the shipped 1805 board twelve province names collapse:

    Bern      -> Bernadotte  100      Lorraine  -> Ney         80
    Leon      -> Napoleon    100      Maine     -> Ney         80
    Brunswick -> Brunswick   100 exact  Ukraine -> Ney         80
    Brittany  -> Ney          80      Oslo      -> Napoleon    75
    Champagne -> Ney          80      Rome      -> Armfelt     75
    Gascony   -> Ney          80
    Guyenne   -> Ney          80

Measured, not asserted, before a line was written:

  * The ambient 40-turn board hits it SEVENTEEN times, every one from
    `enemy_ai._execute_action` -> `_execute_attack`, and the consequence is
    a STALL. Britain's Iberian army stalled for TWELVE turns. Paget stood at Bearn from turn 17 to 28, adjacent to Gascony, and six times - turns 17, 19, 21, 23, 25, 27, every OTHER turn, because a failed action writes a 2-turn cooldown - his attack on that province was redirected to Ney, wherever Ney happened to be. A second corps, the artillerist Shrapnel, spent the alternate turns the same way. The seventeen collapses span turns 6-27 in two phases: six `Leon -> Napoleon` ordered from Lisbon, then eleven `Gascony -> Ney` from Bearn. Paget never took Gascony; on turn 29 he gave up and marched on Bordelais instead.
    The refusal names the province and prints another man's province beside
    it: "Paget cannot reach Gascony (Vienna) from Bearn! Range: 1,
    Distance: 8".

  * TWELVE of the twenty nations boot with no war-enemies at all, and for
    those the broad diplomatic check answers instead - it matches over every
    non-allied marshal and hands back a man the caller is at PEACE with, for
    auto-war-declaration. Reproduced by hand: a Prussian order to attack the
    province `Gascony` resolved to Ney, DECLARED WAR ON FRANCE, and cascaded
    Spain, Bavaria, Holland, the Kingdom of Italy and Switzerland in behind
    it. That makes WO-13 a P1, not the filed P2.

`Brunswick` is the one case the gate cannot close and is not meant to: a
live province AND a Prussian marshal, identical strings, so it never reaches
the fuzzy arm - the exact lookup at the head of each seam resolves it first.
That order is documented at the seams and pinned here as a known exception.

METHOD NOTE, inherited from slice 9's own P2: a text pin cannot protect
REACHABILITY. Where this slice protects a code path, the test drives the
real executor and observes the outcome; source scans are used only for the
census, and they go through `_code_only`/`_code_norm` so a comment naming
the fix cannot satisfy them.

Every test names the mutation that kills it.
"""

import ast
import contextlib
import io
import json
import os
import pathlib
import re
import subprocess
import sys
from pathlib import Path

import pytest

from backend.commands import executor as EX
from backend.commands import parser as P
from backend.commands.executor import CommandExecutor
from backend.commands.parser import _plausible_name_typo
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
EXECUTOR_PY = REPO / "backend" / "commands" / "executor.py"
SWEEP_METRICS_PY = REPO / "tests" / "test_combat_sweep_metrics.py"
SCENARIO_PATH = (REPO / "godot-client" / "project-sovereign" / "assets"
                 / "maps" / "europe_1805.json")

_DOCSTRING_HEADS = ('"""', "'''", 'r"""')

# The twelve boot-live collapses, measured on the shipped board. Only
# `Brunswick` survives the gate, and it survives on the EXACT arm.
BOOT_COLLAPSES = {
    "Bern": "Bernadotte", "Brittany": "Ney", "Brunswick": "Brunswick",
    "Champagne": "Ney", "Gascony": "Ney", "Guyenne": "Ney",
    "Leon": "Napoleon", "Lorraine": "Ney", "Maine": "Ney",
    "Oslo": "Napoleon", "Rome": "Armfelt", "Ukraine": "Ney",
}


def _read(path):
    return io.open(path, encoding="utf-8").read()


def _code_only(text: str) -> str:
    """`text` with comments and docstrings removed.

    Every guard this slice adds carries a comment naming the rule it
    implements, so a bare substring scan would find the prose and pass with
    the code deleted - the INERT shape this row keeps re-finding.
    """
    import tokenize
    out = []
    try:
        for tok in tokenize.generate_tokens(io.StringIO(text).readline):
            if tok.type == tokenize.COMMENT:
                continue
            if (tok.type == tokenize.STRING
                    and tok.line.strip().startswith(_DOCSTRING_HEADS)):
                continue
            out.append(tok.string)
    except (tokenize.TokenError, IndentationError):
        return text
    return chr(10).join(out)


def _code_norm(text: str) -> str:
    """`_code_only` with all whitespace squeezed out.

    `_code_only` emits one token per line, so a multi-token needle never
    matches it - a trap of the same shape, since the pin reads as passing.
    """
    return re.sub(r"\s+", "", _code_only(text))


def _suppress():
    return contextlib.redirect_stdout(io.StringIO())


@pytest.fixture(scope="module")
def world():
    """The shipped 1805 board, the one the defect was measured on."""
    with _suppress():
        return WorldState.from_scenario(str(SCENARIO_PATH))


@pytest.fixture(scope="module")
def ex():
    with _suppress():
        return CommandExecutor()


def _fresh_world():
    with _suppress():
        return WorldState.from_scenario(str(SCENARIO_PATH))


# ══════════════════════════════════════════════════════════════════
# 1. The enemy seam - a province stops becoming a marshal
# ══════════════════════════════════════════════════════════════════

class TestTheEnemySeam:

    def test_a_province_no_longer_resolves_to_an_enemy_marshal(self, ex, world):
        """Gascony is a province in south-west France. It is not Marshal Ney.

        Killed by: deleting the `_correction_survives` call in
        `_fuzzy_match_enemy`."""
        marshal, error = ex._fuzzy_match_enemy("Gascony", world, "Austria")
        assert marshal is None, (
            "a province name still resolves to a marshal")
        assert error is not None

    def test_the_refusal_names_real_enemies_and_never_guesses(self, ex, world):
        """CA8-28 one register over: ordinary words never become a marshal,
        not even as a guess. The message offers the actual enemy roster,
        which claims nothing about what `Gascony` meant.

        Killed by: reverting `_honest_alternatives` to
        `result["suggestions"]`, which is EMPTY on the auto-correct arm and
        printed "Available: none" on a board full of enemies."""
        _, error = ex._fuzzy_match_enemy("Gascony", world, "Austria")
        message = error["message"]
        assert "Did you mean" not in message, (
            "the refusal turned into a guess at a marshal's name")
        assert error["suggestions"], "the refusal named nobody at all"
        for name in error["suggestions"]:
            assert world.get_marshal(name) is not None, (
                f"{name!r} is not a marshal")

    def test_every_boot_collision_is_closed_except_the_exact_one(
            self, ex, world):
        """The census over the shipped board: of the twelve measured
        collapses, exactly one survives - and it survives on the EXACT arm.

        Killed by: any mutation that lets the fuzzy arm through."""
        survivors = {}
        for province, was in BOOT_COLLAPSES.items():
            marshal, _ = ex._fuzzy_match_enemy(province, world, "Austria")
            if marshal is not None:
                survivors[province] = marshal.name
        assert survivors == {"Brunswick": "Brunswick"}, (
            f"unexpected survivors: {survivors}")
        del was

    def test_the_lever_down_restores_the_collapse(self, ex, world, monkeypatch):
        """The attribution lever must genuinely restore the old behaviour -
        slice 9 shipped a lever whose own comment was false because a second
        code path sat outside it. This drives the real seam both ways.

        Killed by: freezing `ENEMY_DIRECTION_GATE_ACTIVE` at def time, or
        by hard-coding `_correction_survives` to return False."""
        monkeypatch.setattr(EX, "ENEMY_DIRECTION_GATE_ACTIVE", False)
        marshal, _ = ex._fuzzy_match_enemy("Gascony", world, "Austria")
        assert marshal is not None and marshal.name == "Ney", (
            "with the lever down the pre-slice collapse must return")


# ══════════════════════════════════════════════════════════════════
# 2. The freeze - the behaviour the seventeen ambient hits produced
# ══════════════════════════════════════════════════════════════════

def _british_corps_at(world, region, name="Paget", strength=18000):
    """A British marshal standing on `region`, at war with France."""
    from backend.models.marshal import Marshal
    marshal = Marshal(name=name, nation="Britain", location=region,
                      strength=strength, personality="aggressive")
    world.marshals[name] = marshal
    return marshal


class TestTheFrozenArmy:
    """Britain's Iberian army stalled because every order it gave named a
    province the resolver handed to a marshal elsewhere.

    ⚠ The shape was overstated in the first draft ("22 consecutive turns")
    and the review corrected it on measurement; `TestTheAmbientBoard` now
    pins the real split so it cannot drift back."""

    def _order(self, world, ex, marshal, target):
        with _suppress():
            return ex.execute({"command": {
                "marshal": marshal.name, "action": "attack",
                "target": target, "type": "specific"}},
                {"world": world, "executor": ex})

    def test_the_order_reaches_the_province_and_not_a_distant_marshal(self):
        """Killed by: deleting the enemy-seam gate."""
        world = _fresh_world()
        with _suppress():
            ex = CommandExecutor()
        marshal = _british_corps_at(world, "Bearn")
        ney = world.get_marshal("Ney")
        assert ney.location != "Gascony", (
            "fixture precondition: Ney must be somewhere else")
        result = self._order(world, ex, marshal, "Gascony")
        message = str(result.get("message") or "")
        assert ney.location not in message, (
            f"the order was still redirected to Ney at {ney.location}: "
            f"{message}")

    def test_with_the_lever_down_the_order_is_redirected_again(
            self, monkeypatch):
        """The measured defect, reproduced: the refusal names the province
        and prints another man's province beside it.

        Killed by: the same mutation as above (this arm proves the pin is
        about the gate, not about the fixture)."""
        world = _fresh_world()
        with _suppress():
            ex = CommandExecutor()
        monkeypatch.setattr(EX, "ENEMY_DIRECTION_GATE_ACTIVE", False)
        marshal = _british_corps_at(world, "Bearn")
        ney = world.get_marshal("Ney")
        result = self._order(world, ex, marshal, "Gascony")
        message = str(result.get("message") or "")
        assert ney.location in message, (
            "the pre-slice redirection did not reproduce; the fixture no "
            f"longer exercises the defect. message={message!r}")

    def test_esp_ev_4_never_guarded_this_in_either_direction(self):
        """Why a gate was needed at all - and the claim is stronger than
        the one I first wrote, which the mutation sweep exposed as
        imprecise.

        ESP-EV-4's `guessed_target_refusal` catches the PARSER substituting
        one real foe for the name the player typed. It cannot catch this
        defect, because the substitution here happens one layer DOWN: the
        target string is still `Gascony`, and the guard's first clause is
        `_named_in_raw(target)` - the player typed the word, so it grounds
        itself and the guard stands aside. Measured on both shapes below,
        with the resolution fully populated exactly as `_execute_attack`
        populates it.

        The AI shape additionally carries no `_raw_input` at all
        (`enemy_ai._execute_action` builds four keys), which short-circuits
        the guard at its second line - so the AI is doubly unprotected.

        Killed by: deleting the `_named_in_raw(target)` clause from
        `guessed_target_refusal` (the player arm then refuses), which is
        also the change that would make this slice's justification
        stale."""
        from backend.commands.combat_executor import guessed_target_refusal
        world = _fresh_world()
        marshal = _british_corps_at(world, "Bearn")
        ney = world.get_marshal("Ney")

        ai_command = {"marshal": marshal.name, "action": "attack",
                      "target": "Gascony", "type": "specific"}
        assert "_raw_input" not in ai_command
        assert guessed_target_refusal(
            world, marshal, ai_command, "Gascony",
            resolved_target=ney.name, enemy_candidates=(ney,)) is None, (
            "the AI path is guarded after all - re-read the slice's case")

        player_command = dict(ai_command,
                              _raw_input="Paget, attack Gascony")
        assert guessed_target_refusal(
            world, marshal, player_command, "Gascony",
            resolved_target=ney.name, enemy_candidates=(ney,)) is None, (
            "ESP-EV-4 guards the player here after all - re-read the case")


# ══════════════════════════════════════════════════════════════════
# 3. The absorber - and the war it started
# ══════════════════════════════════════════════════════════════════

class TestTheAbsorber:
    """`_broad_fuzzy_diplomatic_check` is not merely the place gate A
    re-routes to. It is independently reachable through the `not
    all_enemies` arm, which is the state twelve of the twenty nations boot
    in, and it returns a marshal the caller is at PEACE with, for
    auto-war-declaration."""

    def test_twelve_nations_boot_with_no_war_enemies(self, world):
        """The structural precondition. If this ever reads 0 the absorber's
        independent reachability argument needs re-checking.

        Killed by: nothing in this slice - it pins the board, and it is why
        gate B is not ceremony."""
        peaceful = [n for n in sorted(set([world.player_nation])
                                      | set(world.enemy_nations))
                    if not list(world.get_enemies_of_nation(n))]
        assert len(peaceful) == 12, peaceful
        assert "Prussia" in peaceful

    def test_the_absorber_refuses_a_province(self, ex, world):
        """Killed by: deleting the `_correction_survives` call in
        `_broad_fuzzy_diplomatic_check`."""
        assert ex._broad_fuzzy_diplomatic_check(
            world, "Prussia", "Gascony") is None

    def test_a_province_name_no_longer_declares_war(self):
        """The reproduction, on the real executor: a Prussian order to
        attack the PROVINCE Gascony used to resolve to Ney, declare war on
        France and cascade five more nations in.

        Killed by: deleting either the enemy-seam gate or the absorber
        gate."""
        world = _fresh_world()
        with _suppress():
            ex = CommandExecutor()
        prussian = world.get_marshal("Brunswick")
        ney = world.get_marshal("Ney")
        prussian.location = ney.location            # inside attack range
        assert world.get_diplomatic_state("Prussia", "France") == "PEACE"
        with _suppress():
            ex.execute({"command": {
                "marshal": prussian.name, "action": "attack",
                "target": "Gascony", "type": "specific"}},
                {"world": world, "executor": ex})
        assert world.get_diplomatic_state("Prussia", "France") == "PEACE", (
            "a province name dragged Prussia into war with France")

    def test_with_the_absorber_lever_down_the_war_is_declared_again(
            self, monkeypatch):
        """The re-route, demonstrated: gate the FIRST seam only and the
        absorber takes over and starts the war anyway. This is why slice 10
        gates both, and it is the eval's "gating :433 re-routes to :370"
        claim reproduced on the real path.

        Killed by: hard-coding `BROAD_DIPLOMATIC_GATE_ACTIVE` on."""
        world = _fresh_world()
        with _suppress():
            ex = CommandExecutor()
        monkeypatch.setattr(EX, "ENEMY_DIRECTION_GATE_ACTIVE", True)
        monkeypatch.setattr(EX, "BROAD_DIPLOMATIC_GATE_ACTIVE", False)
        prussian = world.get_marshal("Brunswick")
        prussian.location = world.get_marshal("Ney").location
        with _suppress():
            ex.execute({"command": {
                "marshal": prussian.name, "action": "attack",
                "target": "Gascony", "type": "specific"}},
                {"world": world, "executor": ex})
        assert world.get_diplomatic_state("Prussia", "France") == "WAR", (
            "the re-route did not reproduce - the absorber is no longer "
            "the path gate A falls into, and the two-gate argument needs "
            "re-deriving")

    def test_a_plausible_typo_still_reaches_the_armistice_block(self):
        """What the absorber is FOR must survive: a mistyped name for a
        marshal the caller is not at war with still produces the
        diplomatic error rather than an "unknown target" shrug.

        Killed by: gating the EXACT arm as well, or by replacing
        `_plausible_name_typo` with something stricter."""
        world = _fresh_world()
        with _suppress():
            ex = CommandExecutor()
        kutuzov = world.get_marshal("Kutuzov")
        world.diplomatic_states[
            world._make_diplo_key("France", kutuzov.nation)] = "ARMISTICE"
        marshal, error = ex._fuzzy_match_enemy("Kutuzof", world, "France")
        assert marshal is None
        assert "armistice" in str(error.get("message", "")).lower(), error


# ══════════════════════════════════════════════════════════════════
# 4. The fifth seam - the census the contract asked for
# ══════════════════════════════════════════════════════════════════

class TestTheFifthSeam:
    """`_fuzzy_match_marshal` carries the identical hole. The ambient board
    never exercises it (all 58 of its touches there are the EXACT string
    `Brunswick`), so it is measured inert on that harness and pinned by
    construction instead - the discipline slice 9's stake rider used."""

    def test_the_marshal_seam_refuses_a_province(self, ex, world):
        """Killed by: deleting the `_correction_survives` call in
        `_fuzzy_match_marshal`."""
        marshal, error = ex._fuzzy_match_marshal("Gascony", world)
        assert marshal is None, "a province still commands an army"
        assert "Did you mean" not in str(error.get("message"))

    def test_the_marshal_seam_lever_restores_the_collapse(
            self, ex, world, monkeypatch):
        """Killed by: freezing `MARSHAL_DIRECTION_GATE_ACTIVE`."""
        monkeypatch.setattr(EX, "MARSHAL_DIRECTION_GATE_ACTIVE", False)
        marshal, _ = ex._fuzzy_match_marshal("Gascony", world)
        assert marshal is not None and marshal.name == "Ney"

    def test_it_is_reachable_from_a_typed_order(self):
        """Not ceremony: the seam is what turns the marshal slot of a typed
        command into a man, so a province in that slot used to give Ney an
        order. Driven through the real executor.

        Killed by: deleting the marshal-seam gate."""
        world = _fresh_world()
        with _suppress():
            ex = CommandExecutor()
        ney = world.get_marshal("Ney")
        before = (ney.location, ney.fortified)
        with _suppress():
            result = ex.execute({"command": {
                "marshal": "Gascony", "action": "fortify",
                "type": "specific"}},
                {"world": world, "executor": ex})
        assert not result.get("success"), result
        assert (ney.location, ney.fortified) == before, (
            "an order addressed to a province was carried out by Ney")

    def test_an_ordinary_marshal_typo_still_commands(self, ex, world):
        """Killed by: replacing the gate with a blanket refusal."""
        marshal, _ = ex._fuzzy_match_marshal("Kutuzof", world)
        assert marshal is not None and marshal.name == "Kutuzov"


# ══════════════════════════════════════════════════════════════════
# 5. What must not change
# ══════════════════════════════════════════════════════════════════

class TestTheLegitimateCases:

    def test_an_exact_enemy_name_still_resolves(self, ex, world):
        """Killed by: applying the gate to the EXACT arm."""
        for name in ("Mack", "Kutuzov", "Moore"):
            marshal, _ = ex._fuzzy_match_enemy(name, world, "France")
            assert marshal is not None and marshal.name == name

    def test_a_plausible_enemy_typo_still_auto_corrects(self, ex, world):
        """`attack Kutuzof` must still find Kutuzov - the typo tolerance
        this seam exists for.

        Killed by: making `_correction_survives` return False
        unconditionally."""
        marshal, _ = ex._fuzzy_match_enemy("Kutuzof", world, "France")
        assert marshal is not None and marshal.name == "Kutuzov"

    def test_the_suggest_band_still_asks_about_a_visible_enemy(
            self, ex, world, monkeypatch):
        """The medium-confidence arm never went through the WO-13 typo gate
        and must still ask.

        ⚠ The first cut of this test was INERT and the review found it: it
        guarded its single assertion behind `if error.get("suggestion")`,
        which is False on its own fixture (`Kutz` reaches the low-score arm,
        not the suggest band), so it asserted nothing at all. It now uses a
        query that genuinely lands in the band, and asserts unconditionally.

        Killed by: moving the typo gate above the `suggest` branch, or
        dropping the branch."""
        def ask():
            _m, err = ex._fuzzy_match_enemy("La Mancha", world, None)
            return _m, dict(err or {})

        marshal, gated = ask()
        assert marshal is None
        assert gated.get("suggestion") == "Mack", gated
        assert "Did you mean 'Mack'?" in gated["message"]

        # And the sharp half: the WO-13 gate touches the AUTO-CORRECT arm
        # only, so the suggest band is byte-identical with the lever down.
        monkeypatch.setattr(EX, "ENEMY_DIRECTION_GATE_ACTIVE", False)
        _, ungated = ask()
        assert ungated == gated, (gated, ungated)

    def test_an_exact_armistice_target_still_blocks(self):
        """Killed by: gating `_check_diplomatic_block`'s exact lookup."""
        world = _fresh_world()
        with _suppress():
            ex = CommandExecutor()
        kutuzov = world.get_marshal("Kutuzov")
        world.diplomatic_states[
            world._make_diplo_key("France", kutuzov.nation)] = "ARMISTICE"
        marshal, error = ex._fuzzy_match_enemy("Kutuzov", world, "France")
        assert marshal is None
        assert error.get("diplomatic_block") == "armistice"

    def test_attacking_a_named_enemy_still_works_end_to_end(self):
        """The legitimate case, on the real path.

        Killed by: deleting the enemy seam's exact arm."""
        world = _fresh_world()
        with _suppress():
            ex = CommandExecutor()
        mack = world.get_marshal("Mack")
        ney = world.get_marshal("Ney")
        ney.location = mack.location
        with _suppress():
            result = ex.execute({"command": {
                "marshal": "Ney", "action": "attack", "target": "Mack",
                "type": "specific"}},
                {"world": world, "executor": ex})
        assert "Mack" in str(result.get("message") or ""), result


# ══════════════════════════════════════════════════════════════════
# 6. Brunswick - the documented, uncloseable exact collision
# ══════════════════════════════════════════════════════════════════

class TestBrunswick:

    def test_he_is_the_only_exact_collision_on_the_shipped_board(self, world):
        """Killed by: nothing in this slice. It is the pin that tells the
        next reader whether the exception is still a single named case or
        has quietly become a class."""
        collisions = sorted(r for r in world.regions if r in world.marshals)
        assert collisions == ["Brunswick"], collisions

    def test_a_typo_gate_is_powerless_over_him_by_construction(self):
        """Two facts, both required for "uncloseable" to be honest: the
        predicate says an identical string IS a plausible typo, and the
        exact arm runs before the fuzzy one anyway, so the gate is never
        even consulted.

        Killed by: `_plausible_name_typo` gaining an identity rejection -
        at which point this exception should be revisited, not patched."""
        assert _plausible_name_typo("Brunswick", "Brunswick") is True

    def test_the_enemy_seam_gives_the_marshal(self, ex, world):
        """The documented resolution order for the target register: a name
        that is both is taken as the MAN, because `attack Brunswick` names
        a foe.

        Killed by: adding a region-precedence rule to `_fuzzy_match_enemy`
        without updating this record."""
        marshal, _ = ex._fuzzy_match_enemy("Brunswick", world, "Austria")
        assert marshal is not None and marshal.nation == "Prussia"

    def test_the_region_seam_gives_the_province(self, ex, world):
        """The other half of the documented order: in the DESTINATION
        register the same string is the place."""
        region, _ = ex._fuzzy_match_region("Brunswick", world)
        assert region is not None and region.name == "Brunswick"

    def test_the_parser_addressee_refuses_him_by_name(self, world):
        """⚠ CONSCIOUSLY INVERTED, and the inversion IS the fix.

        This pin used to assert that `Brunswick, hold` resolves to nothing,
        because slice 2's carve-out ("a lead that is also a region name is
        never an enemy") ran BEFORE the enemy roster. The review measured
        what that bought: the address fell through to ordinary marshal
        resolution and **France fortified a Prussian marshal at Berlin**.
        `Mack` and `Kutuzov` were refused all along; only the
        province-named marshal escaped, so the one collision on the board
        punched the one hole in slice 2's own guard.

        The carve-out now runs AFTER the exact enemy roster: an ordinary
        place word is still never an address, and a real commander who
        happens to share a province name is refused by name.

        Killed by: putting the region carve-out back above the roster."""
        enemies = [m.name for m in world.marshals.values()
                   if m.nation != world.player_nation]
        regions = list(world.regions.keys())
        assert P._resolve_enemy_addressee(
            "Brunswick, hold", enemies, regions) == (
                "Brunswick", "exact", "Brunswick")
        # and the carve-out still does its own job
        for place in ("Vienna, hold", "Gascony, hold"):
            assert P._resolve_enemy_addressee(place, enemies, regions) is None

    def test_the_player_can_no_longer_command_him(self):
        """The behaviour the inversion buys, driven through the real parse
        path rather than the seam.

        Killed by: the same mutation."""
        world = _fresh_world()
        with _suppress():
            ex = CommandExecutor()
        prussian = world.get_marshal("Brunswick")
        before = bool(getattr(prussian, "fortified", False))
        enemies = [m.name for m in world.marshals.values()
                   if m.nation != world.player_nation]
        assert P._resolve_enemy_addressee(
            "Brunswick, fortify", enemies, list(world.regions.keys()))
        assert bool(getattr(prussian, "fortified", False)) is before
        del ex


# ══════════════════════════════════════════════════════════════════
# 7. The census - one predicate, no seam missed
# ══════════════════════════════════════════════════════════════════

def _marshal_yielding_seams():
    """Every function in executor.py that fuzzy-matches over a MARSHAL
    roster, found by AST rather than by name."""
    tree = ast.parse(_read(EXECUTOR_PY))
    found = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        body = ast.dump(node)
        if "match_with_context" not in body:
            continue
        found[node.name] = node
    # `_honest_alternatives` reads a finished result; it resolves nothing.
    found.pop("_honest_alternatives", None)
    return found


class TestTheCensus:

    def test_every_marshal_matching_seam_is_gated(self):
        """The contract asked for a census over the fifth seam. This is it,
        derived rather than listed: any function in executor.py that calls
        `match_with_context` must guard its auto-correct arm - the marshal
        seams with `_correction_survives`, the region seam with its own
        `_plausible_name_typo` (WO-2).

        Killed by: adding a fourth ungated seam, or deleting a guard."""
        seams = _marshal_yielding_seams()
        assert set(seams) == {
            "_fuzzy_match_marshal", "_fuzzy_match_region",
            "_broad_fuzzy_diplomatic_check", "_fuzzy_match_enemy",
        }, sorted(seams)
        for name, node in seams.items():
            guard = ("_plausible_name_typo" if name == "_fuzzy_match_region"
                     else "_correction_survives")
            # Must be CALLED, not merely named. The first cut of this pin
            # read `ast.dump(node)` for the guard's name and was INERT: each
            # seam imports its guard inside the function, so the name is in
            # the dump whether or not anything calls it - and the mutation
            # sweep proved it by replacing the region seam's call with
            # `bool(...)` and watching the pin pass.
            called = {c.func.id for c in ast.walk(node)
                      if isinstance(c, ast.Call)
                      and isinstance(c.func, ast.Name)}
            assert guard in called, (
                f"{name} matches names with no {guard} CALL")

    def test_one_predicate_stands_behind_all_three_gates(self):
        """One predicate behind the three FUZZY seams - and the wording
        matters, because the first draft of the production docstring said
        "a census can prove no seam was missed" full stop, and a review
        showed that is true of the auto-correct arms only. The EXACT
        marshal-first arm is six further sites and no typo gate can reach
        it; that arm is governed by the positional rule, pinned in
        `TestBrunswick`.

        Killed by: inlining the predicate at one seam, which is how the
        three drift apart."""
        code = _code_only(_read(EXECUTOR_PY))
        assert code.count("_correction_survives") == 4, (
            "expected one definition plus exactly three call sites")

    def test_each_gate_has_its_own_lever(self):
        """Three levers, not one, so the attribution can name which seam
        moved the board.

        Killed by: collapsing them into a single flag."""
        code = _code_norm(_read(EXECUTOR_PY))
        for lever in ("ENEMY_DIRECTION_GATE_ACTIVE",
                      "BROAD_DIPLOMATIC_GATE_ACTIVE",
                      "MARSHAL_DIRECTION_GATE_ACTIVE"):
            assert f"{lever}=True" in code, f"{lever} is not set True"
            assert code.count(lever) >= 2, (
                f"{lever} is declared but never read")

    def test_the_predicate_honours_its_lever(self):
        """Behaviour, not text: with the lever down every correction
        survives; with it up an implausible one does not.

        Killed by: ignoring `gate_active` inside `_correction_survives`."""
        assert EX._correction_survives("Gascony", "Ney", False) is True
        assert EX._correction_survives("Gascony", "Ney", True) is False
        assert EX._correction_survives("Kutuzof", "Kutuzov", True) is True


# ══════════════════════════════════════════════════════════════════
# 8. The harness - measured in a subprocess, never in-process
# ══════════════════════════════════════════════════════════════════

LEVER_NAMES = ("ENEMY_DIRECTION_GATE_ACTIVE", "BROAD_DIPLOMATIC_GATE_ACTIVE",
               "MARSHAL_DIRECTION_GATE_ACTIVE")

_LEVER_PRELUDE = """
import backend.commands.executor as _EX
for _name, _flag in zip(
        ("ENEMY_DIRECTION_GATE_ACTIVE", "BROAD_DIPLOMATIC_GATE_ACTIVE",
         "MARSHAL_DIRECTION_GATE_ACTIVE"), sys.argv[1]):
    setattr(_EX, _name, _flag == "1")
"""


def _spawn(probe, levers, marker):
    """Run `probe` in a hash-pinned child with the three levers set.

    THE LEVERS ARE SET IN THE CHILD, never by editing the source. The first
    cut of this helper rewrote `backend/commands/executor.py` for each arm
    and restored it afterwards, and that was wrong twice over:

      * it silently NO-OPPED once the mutation sweep had touched the file,
        because `pathlib.write_text` re-emits with `os.linesep`, the file
        became CRLF, and every LF-anchored pattern missed. The "ungated" arm
        then ran the shipped tree and the assertions compared the wrong
        world.
      * worse, and the reason it is gone rather than repaired: a test that
        writes to a production source file makes the WHOLE SUITE unsafe to
        run beside anything else. Measured, by accident: a concurrent reader
        caught the file mid-arm and `test_threat_series_is_the_standing_
        baseline` failed with the PRE-slice series.

    Slice 9's `_rebellion_turn` had the right idiom already - set the module
    global in the child - and this is it. It is equivalent because the seams
    read their lever at CALL time, which the sweep pins directly (the three
    "frozen at def time" mutations all kill).

    The ATTRIBUTION EXPERIMENT in the landing record is a different thing and
    did use real source edits, in a scratch driver, one arm at a time.
    """
    env = dict(os.environ)
    env.update(PYTHONHASHSEED="0", PYTHONPATH=str(REPO),
               SOVEREIGN_SEED="historical", LLM_MODE="mock")
    env.pop("SOVEREIGN_SCENARIO", None)
    env.pop("SOVEREIGN_MAP", None)
    env.pop("PYTHONIOENCODING", None)
    # STRICT, and the strictness is the point: the first cut took
    # ("False", "False", "False") from the call sites and every non-empty
    # string is truthy, so it set all three levers ON and reported the
    # gated board as the "ungated" arm. An instrument must refuse to
    # guess.
    assert len(levers) == 3 and all(isinstance(v, bool) for v in levers), (
        f"levers must be three booleans, got {levers!r}")
    flags = "".join("1" if value else "0" for value in levers)
    proc = subprocess.run(
        [sys.executable, "-c", "import sys\n" + _LEVER_PRELUDE + probe, flags],
        env=env, cwd=str(REPO), capture_output=True, text=True, timeout=900)
    assert proc.returncode == 0, proc.stdout[-2000:] + proc.stderr[-2000:]
    return json.loads(proc.stdout.split(marker)[-1].splitlines()[0])


def _run_ambient(levers):
    """The 40-turn ambient board under a named lever configuration, in a
    hash-pinned subprocess - the §5 discipline. An in-process run of the same
    forty turns is not reproducible and is worthless for these claims (slice
    9 measured turn 25 in-suite against 32 pinned)."""
    return _spawn(_AMBIENT_PROBE, levers, "WO10=")


_AMBIENT_PROBE = r'''
import json, random
from pathlib import Path
from backend.models.world_state import WorldState
from backend.commands.executor import CommandExecutor
from backend.game_logic.turn_manager import TurnManager
scen = Path("godot-client/project-sovereign/assets/maps/europe_1805.json")
world = WorldState.from_scenario(str(scen))
executor = CommandExecutor()
tm = TurnManager(world, executor=executor)
game_state = {"world": world, "executor": executor}
hits = []
def wrap(name, idx, kwname):
    orig = getattr(CommandExecutor, name)
    def patched(self, *a, **kw):
        q = a[idx] if len(a) > idx else kw.get(kwname)
        res = orig(self, *a, **kw)
        try:
            m = res[0] if (isinstance(res, tuple) and res
                           and res[0] is not None
                           and hasattr(res[0], "name")) else None
            if (m is not None and q and world.get_region(q) is not None
                    and str(q).lower() != m.name.lower()):
                hits.append([name, q, m.name])
        except Exception:
            pass
        return res
    setattr(CommandExecutor, name, patched)
wrap("_fuzzy_match_enemy", 0, "enemy_name")
wrap("_fuzzy_match_marshal", 0, "marshal_name")
wrap("_broad_fuzzy_diplomatic_check", 2, "enemy_name")
series = [int(world.threat_level)]
for turn in range(40):
    random.seed(10_000 + turn)
    tm.end_turn(game_state)
    series.append(int(world.threat_level))
print("WO10=" + json.dumps({"hits": hits, "series": series}))
'''


def _writes_to_repo_source(path: pathlib.Path) -> list:
    """Every `X.write_text/​write_bytes(...)` in `path` whose receiver `X` is a
    module constant bound to a path under `backend/` or `godot-client/`.

    AST, not a substring scan, and for a reason this row has paid for twice:
    `_code_only` emits ONE TOKEN PER LINE, so a first cut of this census that
    filtered lines containing "tmp" could never match anything and reported
    every fixture write in the suite as an offender.
    """
    # utf-8-sig: at least one test file in the suite carries a BOM, and
    # `ast.parse` rejects U+FEFF outright.
    tree = ast.parse(path.read_text(encoding="utf-8-sig"))
    source_names = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        dumped = ast.dump(node)
        if "backend" in dumped or "godot-client" in dumped:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    source_names.add(target.id)
    offenders = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not isinstance(func, ast.Attribute):
            continue
        if func.attr not in ("write_text", "write_bytes"):
            continue
        if isinstance(func.value, ast.Name) and func.value.id in source_names:
            offenders.append(f"{path.name}:{node.lineno} "
                             f"{func.value.id}.{func.attr}")
    return offenders


class TestNoTestWritesToProductionSource:
    """A census, because this slice shipped the hazard once and it is not the
    kind of thing a review looks for.

    The first cut of the ambient runner rewrote
    `backend/commands/executor.py` for each arm and restored it afterwards.
    That makes the WHOLE SUITE unsafe to run beside anything else, and it was
    caught by accident: a concurrent reader saw the file mid-arm and
    `test_ai_intent_assurance.py::TestArmAControl::
    test_threat_series_is_the_standing_baseline` failed with the PRE-slice
    series. Nothing in the suite had been asserting this.

    Measured at close: every other test that writes a file writes to a tmp
    fixture, so the suite-wide count is ZERO.
    """

    def test_this_file_writes_no_repository_source(self):
        """Killed by: reintroducing a source edit in this file."""
        assert _writes_to_repo_source(pathlib.Path(__file__)) == []

    def test_no_test_in_the_suite_writes_to_backend_or_the_client(self):
        """Killed by: any test gaining a write to a path constant that
        points at production source."""
        offenders = []
        for path in sorted((REPO / "tests").glob("test_*.py")):
            offenders += _writes_to_repo_source(path)
        assert offenders == [], offenders

    def test_the_census_can_see_an_offender(self):
        """The census's own sensitivity, proven rather than assumed - a
        clean result from a blind instrument is the UX23-B lesson.

        Killed by: any census that cannot detect the pattern it forbids."""
        probe = pathlib.Path(REPO) / "tests" / "__wo10_census_probe.py"
        probe.write_text(
            'import pathlib\n'
            'VICTIM = pathlib.Path("backend/commands/executor.py")\n'
            'def f():\n'
            '    VICTIM.write_bytes(b"")\n', encoding="utf-8")
        try:
            found = _writes_to_repo_source(probe)
        finally:
            probe.unlink()
        assert found and "VICTIM.write_bytes" in found[0], found


class TestTheSpawnHelperCannotLie:
    """The instrument that measures the arms must not be able to quietly
    measure the wrong one. Both failures below actually happened."""

    def test_it_refuses_string_flags(self):
        """`("False", "False", "False")` set all three levers ON, because
        every non-empty string is truthy - and the arms then compared the
        gated board to itself.

        Killed by: dropping the isinstance check in `_spawn`."""
        with pytest.raises(AssertionError):
            _spawn("print('WO10=' + '{}')", ("False",) * 3, "WO10=")

    def test_the_child_actually_receives_the_levers(self):
        """The prelude sets the module global in the CHILD; the seams read
        it at call time. Proven by asking the child what it sees, rather
        than by trusting the mechanism.

        Killed by: deleting the prelude, or passing the flags wrongly."""
        probe = ("import json\n"
                 "print('WO10L=' + json.dumps([_EX.ENEMY_DIRECTION_GATE_ACTIVE,"
                 " _EX.BROAD_DIPLOMATIC_GATE_ACTIVE,"
                 " _EX.MARSHAL_DIRECTION_GATE_ACTIVE]))")
        assert _spawn(probe, (False, True, False), "WO10L=") == [
            False, True, False]
        assert _spawn(probe, (True, True, True), "WO10L=") == [
            True, True, True]


class TestTheAmbientBoard:
    """The re-measured count the done-when hangs on. Slice 9 moved the
    board (Switzerland now rebels at 32, not 28), so the contract's "17x in
    40 turns" had to be re-taken; it reproduces exactly, because every one
    of the seventeen falls at turns 6-27, before slice 9's divergence.

    Re-measured again by FA slice 2 (September 4, 2026, "No Word Came"):
    a cornered French corps is no longer ground to dust across a phase, so
    Ney stood one turn longer — at Bohemia then Franconia, NORTH of Vienna,
    not "in the south" as the first note said (corrected by the slice-2
    review audit) — and the ungated board collapsed EIGHTEEN times, the
    twelfth `Gascony -> Ney` falling at turn 28.

    Re-measured a third time by the slice-2 REVIEW ROUND (September 4,
    2026, "The Word Is Owed"): the braked-corps HOLD forks the board at
    turn 22 and the eighteenth collapse is gone again — SEVENTEEN, the
    original six `Leon -> Napoleon` and eleven `Gascony -> Ney`, all at
    turns 6-27.

    Re-measured a fourth time by FA slice 4 (September 4, 2026, "The AI
    Reads the Board"): nine AI board-reading fixes fork the board at turn 4,
    and the UNGATED AI — which now presses its attacks instead of wasting
    them — hits the collision TWENTY-NINE times: five `Leon -> Napoleon`
    and twenty-four `Gascony -> Ney`. The gated board still collapses never,
    which is the contract; the counts here are the defect's measurement on
    today's board and move with it, as their docstrings say they must.

    Re-measured a fifth time by the slice-4 REVIEW ROUND (September 4,
    2026, "The Board Reads Back"): eight more AI board-reading fixes fork
    the board at turn 10 and the UNGATED AI hits the collision TWENTY-FIVE
    times — three `Leon -> Napoleon`, ten `Champagne -> Ney`, eight
    `Gascony -> Ney`, four `Maine -> Ney`: the ungated board now names TWO
    new provinces (Champagne, Maine) because a no-longer-parked British
    horse and an un-frozen Austrian corps press different fronts."""

    @pytest.fixture(scope="class")
    def ungated(self):
        return _run_ambient((False, False, False))

    @pytest.fixture(scope="class")
    def gated(self):
        return _run_ambient((True, True, True))

    def test_the_ungated_board_collapses_seventeen_times(self, ungated):
        """Killed by: nothing in this slice - it is the defect's own
        measurement, and it fails when the board changes under it, which is
        the warning the next slice needs."""
        seams = {}
        for name, _q, _m in ungated["hits"]:
            seams[name] = seams.get(name, 0) + 1
        assert seams == {"_fuzzy_match_enemy": 25}, seams  # 17 -> 18 -> 17 -> 29 -> 25 across FA slices 2, 2r, 4, 4r

    def test_all_seventeen_are_the_ai_naming_a_province(self, ungated):
        """Records WHICH provinces AND the split, so the shape cannot drift
        back to the overstated one: six `Leon -> Napoleon` and eleven
        `Gascony -> Ney`, spanning turns 6-27 in two phases.

        Killed by: nothing in this slice - it pins the defect's measured
        shape, and it fails when the board changes under it, which is the
        warning the next slice needs."""
        from collections import Counter
        pairs = Counter((q, m) for _s, q, m in ungated["hits"])
        assert dict(pairs) == {("Leon", "Napoleon"): 3,
                               ("Champagne", "Ney"): 10,
                               ("Gascony", "Ney"): 8,
                               ("Maine", "Ney"): 4}, pairs  # 6+11 -> 6+12 -> 6+11 -> 5+24 -> 3+10+8+4 across FA slices 2, 2r, 4, 4r

    def test_the_gated_board_collapses_never(self, gated):
        """The done-when line: the AI stops resolving `Gascony -> Ney`.

        Killed by: deleting any of the three gates."""
        assert gated["hits"] == [], gated["hits"]

    def test_the_ungated_arm_reproduces_the_prior_series(self, ungated):
        """Attribution arm 0. The levers are honest: with all three down
        the board reproduces the series recorded BEFORE this slice,
        byte-for-byte.

        Killed by: a change to the gates that is not actually behind the
        levers - the exact shape of slice 9's shipped P2.

        Re-recorded by FA slice 2 (September 4, 2026): that slice's own
        levers changed the board from index [29] on (its attribution is in
        `test_ai_intent_threat_migration.py`), so "the series before THIS
        slice" is now the pre-WO-10 series AS IT RUNS ON THE SLICE-2 BOARD
        — indices [0]-[28] were byte-identical to the original record.

        Re-recorded again by the slice-2 REVIEW ROUND (September 4, 2026):
        the braked-corps hold forks this arm at index [28] (68, was 69);
        indices [0]-[27] were byte-identical to the original record.

        Re-recorded again by FA slice 4 (September 4, 2026): the AI
        board-reading fixes fork EVERY arm at index [4], so "the series
        before THIS slice" is now the pre-WO-10 configuration AS IT RUNS ON
        THE SLICE-4 BOARD, and the byte-identity this pin can still prove
        against the original record is indices [0]-[3]. What it proves
        beyond that is the levers' honesty in the other direction: the
        gated arm (below) equals the standing BASELINE_SERIES exactly.

        Re-recorded again by FA slice 14 part 2d (September 6, 2026):
        `ELIMINATION_RELIEVES_THE_LORD` grants France a one-off -10 when
        KingdomOfItaly is eliminated out of its web at world turn 10, which
        forks BOTH arms at index [10] (here 58 -> 48). The gated arm's own
        fork is recorded in `test_ai_intent_threat_migration.py` with a
        six-arm attribution; this list is the same change seen from the
        ungated side, and indices [0]-[9] are byte-identical to the previous
        record."""
        assert ungated["series"] == [70, 68, 66, 64, 62, 68, 66, 64, 62, 60, 48, 45, 42, 39, 36, 33, 30, 27, 24, 21, 23, 20, 17, 19, 16, 3, 5, 2, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0]

    def test_the_gated_arm_is_the_recorded_baseline(self, gated):
        """Attribution arm ABC, joined to the pin the rest of the suite
        reads.

        Killed by: re-recording one and not the other."""
        from tests.test_ai_intent_threat_migration import BASELINE_SERIES
        assert gated["series"] == BASELINE_SERIES


class TestTheOtherHarness:

    def test_m1_m7_cannot_reach_these_seams(self):
        """Why M1-M7 are byte-identical WITHOUT re-record - structurally,
        stated rather than assumed: the sweep harness never resolves a name.

        Killed by: M1-M7 gaining a name-resolution path, at which point the
        byte-identity claim in the landing record must be re-measured."""
        code = _code_only(_read(SWEEP_METRICS_PY))
        for forbidden in ("fuzzy_match", "end_turn", "advance_turn"):
            assert forbidden not in code, (
                f"the M-harness now reaches {forbidden}")


# ══════════════════════════════════════════════════════════════════
# 9. The contract's own done-when line, and the "30"
# ══════════════════════════════════════════════════════════════════

class TestTheContractsThirty:
    """The contract says "the 30 boot-live collapse pairs refuse or clarify
    in the player direction". Measured, 30 is not a count of PAIRS and not
    a count of resolutions: it is the number of distinct provinces that
    NAME a marshal at all, counting the suggest band, which already
    clarified. What silently resolved was TWELVE, and in the player
    direction only THREE, because the collapsing names are French marshals
    and France is the player - `Gascony -> Ney` cannot happen to the
    player at all, only to a court for whom Ney is an enemy.

    So the done-when line is answered by measurement rather than by
    arithmetic: after the gate exactly one province still resolves in the
    player direction, and it is the documented exception.
    """

    def test_only_brunswick_still_resolves_in_the_player_direction(
            self, ex, world):
        """Killed by: deleting the enemy-seam gate (Bern and Rome return)."""
        resolved = {}
        for name in sorted(world.regions):
            marshal, _ = ex._fuzzy_match_enemy(name, world, None)
            if marshal is not None:
                resolved[name] = marshal.name
        assert resolved == {"Brunswick": "Brunswick"}, resolved

    def test_the_lever_down_restores_the_other_two(
            self, ex, world, monkeypatch):
        """Killed by: freezing the lever. Records WHICH two: `Bern` reached
        Brunswick (Bernadotte is French, so he is not on the player's
        candidate list and the ladder fell through to the Prussian at 75)
        and `Rome` reached Armfelt of Sweden."""
        monkeypatch.setattr(EX, "ENEMY_DIRECTION_GATE_ACTIVE", False)
        resolved = {}
        for name in sorted(world.regions):
            marshal, _ = ex._fuzzy_match_enemy(name, world, None)
            if marshal is not None:
                resolved[name] = marshal.name
        assert resolved == {"Bern": "Brunswick", "Brunswick": "Brunswick",
                            "Rome": "Armfelt"}, resolved

    def test_the_suggest_band_clarifies_only_about_what_we_can_see(
            self, ex, world):
        """The other half of the 30 never resolved - it asked. It must go on
        asking, but only about a marshal the asker can SEE.

        ⚠ RE-BLESSED, and the reason is the point. The first cut asserted
        `len(clarified) == 7` and never checked WHOM, so it certified a fog
        leak as correct behaviour: six of the seven named a corps France had
        never scouted (`Asturias → Castanos`, `Berry → Deroy`,
        `Karaman → Abdurrahman`, `Leon → ArchdukeCharles`, `Oran → Moore`,
        `Oslo → Moore`) while a test three classes below asserted the exact
        opposite rule about the same function. A count is not a check.

        Killed by: dropping `_display_candidates` from the `suggest` arm,
        which restores all seven."""
        clarified = {}
        for name in sorted(world.regions):
            marshal, error = ex._fuzzy_match_enemy(name, world, None)
            if marshal is None and error and error.get("suggestion"):
                clarified[name] = error["suggestion"]
        visible = {m.name for m in world.get_visible_enemies("France")}
        assert set(clarified.values()) <= visible, clarified
        assert clarified == {"La Mancha": "Mack"}, clarified

    def test_no_bench_marshal_can_mint_a_second_brunswick(self, world):
        """The exception must stay a single named case. Every name on the
        22-strong `marshal_pool` bench is checked against the live region
        keys, so a commissioned marshal can never create a second exact
        collision on this scenario - and if one is ever authored, this
        fails at authoring time rather than in someone's campaign.

        Killed by: authoring a bench marshal named after a province."""
        data = json.loads(SCENARIO_PATH.read_text(encoding="utf-8"))
        bench = set()
        for entries in data.get("marshal_pool", {}).values():
            if isinstance(entries, dict):
                bench |= set(entries.keys())
            elif isinstance(entries, list):
                for entry in entries:
                    bench.add(entry.get("name")
                              if isinstance(entry, dict) else entry)
        assert bench, "the bench is empty - the pin has stopped measuring"
        assert not (bench & set(world.regions)), sorted(bench & set(world.regions))


# ══════════════════════════════════════════════════════════════════
# 10. R5 - a refusal must not print an army nobody has seen
# ══════════════════════════════════════════════════════════════════

class TestTheRefusalDoesNotLeakFog:
    """Found by the review fleet, and it was introduced by this slice's own
    first cut: `_honest_alternatives` fell back to the seam's candidate
    list, which for the player is `world.get_enemy_marshals()` - omniscient
    by design (`world_state.py`, R5). Measured before the fix:

        Enemy 'Gascony' not found. Available: ArchdukeJohn, Castanos, Mack

    Castanos is a Spanish corps France has never scouted. A ranked list of
    hidden armies is free intelligence, which is what CA8-28 forbids one
    register over. The low-score arm leaked the same way BEFORE this slice
    (its `suggestions` come from the same roster), so both arms are filtered
    now, not just the new one.

    Resolution stays omniscient - combat must find a fogged marshal by name,
    and `test_fog_filtered_access` pins that. Only the message is filtered.
    """

    def _visible(self, world):
        """The visible set as the REFUSAL spells it. The refusal humanises
        (`ArchdukeJohn` -> `Archduke John`, CR-5's chokepoint), so a pin
        comparing raw roster keys reads a leak where there is none — which
        is exactly how this pin first went red."""
        from backend.display_names import humanize_entity_name
        return {humanize_entity_name(m.name)
                for m in world.get_visible_enemies("France")}

    def test_a_refused_auto_correct_names_only_visible_enemies(self, ex, world):
        """Killed by: passing `all_enemies` to `_honest_alternatives`
        instead of `_display_candidates(...)`."""
        _, error = ex._fuzzy_match_enemy("Gascony", world, None)
        visible = self._visible(world)
        assert error["suggestions"], "the refusal named nobody"
        assert set(error["suggestions"]) <= visible, (
            f"leaked {set(error['suggestions']) - visible}")
        assert "ArchdukeJohn" not in error["message"], (
            "the refusal printed a raw roster key: " + error["message"])

    def test_the_low_score_arm_is_filtered_too(self, ex, world):
        """The PRE-EXISTING half of the same leak: `Zorblax` printed
        "Available: Moore, Kutuzov, Armfelt", none of them visible.

        Killed by: filtering only the new arm - i.e. returning
        `result["suggestions"]` unfiltered from `_honest_alternatives`."""
        _, error = ex._fuzzy_match_enemy("Zorblax", world, None)
        visible = self._visible(world)
        assert set(error["suggestions"]) <= visible, (
            f"leaked {set(error['suggestions']) - visible}")

    def test_matching_itself_stays_omniscient(self, ex, world):
        """The other side of R5, and the line this slice must not cross:
        a FOGGED enemy is still resolvable by name, because combat is
        mechanics and mechanics are not fogged.

        Killed by: filtering the candidate list used for MATCHING."""
        from backend.display_names import humanize_entity_name
        hidden = [m for m in world.get_enemy_marshals()
                  if m.strength > 0
                  and humanize_entity_name(m.name) not in self._visible(world)]
        assert hidden, "fixture precondition: some enemy must be fogged"
        marshal, _ = ex._fuzzy_match_enemy(hidden[0].name, world, None)
        assert marshal is not None and marshal.name == hidden[0].name
        # The half that actually crosses the line, and the first cut of this
        # pin missed it: an EXACT name never reaches the matcher at all (the
        # head short-circuits), so filtering the MATCHING list left this
        # test green. A TYPO of a fogged enemy is the only form of the claim
        # the matcher participates in — a refuter proved it by applying the
        # mutation this docstring names and watching the test pass.
        typo, _ = ex._fuzzy_match_enemy("Kutuzof", world, None)
        assert typo is not None and typo.name == "Kutuzov"

    def test_the_filter_is_player_scoped(self, ex, world):
        """An AI court's list is not filtered - the fog store is the
        player's, and no enemy_ai site renders this string.

        Killed by: dropping the `from_nation != world.player_nation` arm."""
        # The names must survive UNFILTERED, including one that is on no
        # visibility list at all - the first cut used two French marshals,
        # who are visible to Austria through the player's own fog store, so
        # a mutation that filtered every nation passed anyway.
        assert EX._display_candidates(
            world, "Austria", ["Ney", "Nobody"]) == ["Ney", "Nobody"]
        assert EX._display_candidates(world, None, ["Nobody"]) == ["Nobody"]
        # BOTH directions. The first cut bound only the "filter everyone"
        # mutation; the "filter nobody" one — the direction that re-opens
        # the P1 — it could not see, and a refuter proved it by applying
        # exactly that mutation and watching this test pass.
        assert EX._display_candidates(
            world, world.player_nation, ["Ney", "Nobody"]) == []

    def test_the_filter_fails_CLOSED_when_the_fog_store_raises(
            self, ex, world, monkeypatch):
        """The `except` branch had no test at all, so the mutation that
        re-opens it (`return list(candidates)`) was INERT. On an R5 boundary
        an error must cost the player a message, never the fog.

        Killed by: returning `candidates` from the except branch."""
        def boom(_nation):
            raise RuntimeError("fog store unavailable")

        monkeypatch.setattr(world, "get_visible_enemies", boom)
        assert EX._display_candidates(
            world, world.player_nation, ["Ney", "Mack"]) == []

    def test_the_marshal_seam_offers_your_own_marshals(self, ex, world):
        """"Available" in the marshal register answers "which of YOUR
        marshals" - naming a foreign commander there is both unhelpful and
        a leak.

        Killed by: passing `all_marshals` unfiltered."""
        _, error = ex._fuzzy_match_marshal("Zorblax", world)
        for name in error["suggestions"]:
            assert world.get_marshal(name).nation == world.player_nation, name


# ══════════════════════════════════════════════════════════════════
# 11. A refused marshal query is answered in the marshal register
# ══════════════════════════════════════════════════════════════════

class TestTheCrossRegisterGuess:
    """A regression this slice introduced and the review measured:
    `Ney, attack Kutz` used to auto-correct to Kutuzov and answer, fog-
    honestly, "No intelligence on Kutuzov's position". Gated - and before
    this fix - it answered "Region 'Kutz' not found. Did you mean
    'Frankfurt'?": a guess in the WRONG register, which is CA8-28's own
    rule one seam over.

    `Kutz` is not a plausible typo of anything (four letters, so the limit
    is one edit, and `Kutz`->`Kutuzov` is three), which is exactly why the
    gate refuses it - and exactly why the answer must stay in the register
    the player was speaking.
    """

    def _attack(self, target, world=None, ex=None):
        if world is None:
            world = _fresh_world()
        if ex is None:
            with _suppress():
                ex = CommandExecutor()
        with _suppress():
            return ex.execute({"command": {
                "marshal": "Ney", "action": "attack", "target": target,
                "type": "specific"}}, {"world": world, "executor": ex})

    def test_a_refused_marshal_query_is_not_answered_with_a_province(self):
        """Killed by: dropping the `implausible_correction` clause from the
        region-suggestion branch in `_execute_attack`."""
        message = str(self._attack("Kutz").get("message") or "")
        assert "Did you mean" not in message, message
        assert "Enemy 'Kutz' not found" in message, message

    def test_a_genuine_province_typo_still_asks_about_the_province(self, ex):
        """The branch must not be disabled wholesale: a mistyped PROVINCE
        still gets its own register's question.

        ⚠ The first cut of this test was VACUOUS and the review measured it:
        `Venetia` never sets the marker at all (its enemy-seam action is
        `error`, not `auto_correct`), so the test passed whether or not the
        clause existed. The marker's value is asserted in BOTH directions
        now, so a matcher change cannot make it vacuous again.

        Killed by: removing the region-suggestion branch instead of
        conditioning it."""
        world = _fresh_world()
        _, safe = ex._fuzzy_match_enemy("Venetia", world, "France")
        assert not (safe or {}).get("refused_marshal_correction"), safe
        _, marked = ex._fuzzy_match_enemy("Kutz", world, "France")
        assert (marked or {}).get("refused_marshal_correction") is True, marked
        message = str(self._attack("Venetia").get("message") or "")
        assert "Did you mean" in message, message

    def test_a_province_that_resolves_still_wins_over_both(self, ex):
        """`Gascony` is a real province: it resolves, and neither register
        asks anything.

        Killed by: returning the enemy refusal before the region
        resolution."""
        message = str(self._attack("Gascony").get("message") or "")
        assert "Gascony" in message and "not found" not in message, message


# ══════════════════════════════════════════════════════════════════
# 12. The positional rule, stated once and true in both registers
# ══════════════════════════════════════════════════════════════════

class TestThePositionalRule:
    """The review found the record holding two contradictory rules, each
    calling itself "the WO-13 collision rule": slice 2 said the province
    wins, this slice's first draft said the marshal wins. They are the same
    rule read in two POSITIONS, and it is now written once, in
    `_correction_survives`'s docstring.

    The consequence the review feared - "the province Brunswick is
    unattackable by any typed command, forever" - conflates two causes and
    is measured false below: at boot France is at PEACE with Hanover, which
    is why nothing can enter it; at war, `move to Brunswick` takes it.
    """

    def test_the_rule_is_written_in_exactly_one_place(self):
        """Killed by: restating it per-seam, which is how the two
        contradictory versions came to exist."""
        code = _read(EXECUTOR_PY)
        assert code.count("THE NAME MEANS THE MAN") == 1
        assert code.count("THE PROVINCE IS REACHED BY A REGION-ONLY VERB") == 1
        # and the false first draft must not survive anywhere
        assert "ADDRESSEE position  -> the PROVINCE" not in code

    def test_move_reaches_the_province_when_the_law_allows(self):
        """The escape, driven: region-only verbs are never ambiguous.

        Killed by: making `move` resolve marshal-first."""
        world = _fresh_world()
        with _suppress():
            ex = CommandExecutor()
        world.diplomatic_states[
            world._make_diplo_key("France", "Hanover")] = "WAR"
        ney = world.get_marshal("Ney")
        ney.location = "Frankfurt"
        with _suppress():
            result = ex.execute({"command": {
                "marshal": "Ney", "action": "move", "target": "Brunswick",
                "type": "specific"}}, {"world": world, "executor": ex})
        assert result.get("success"), result
        assert ney.location == "Brunswick"

    def test_at_peace_the_refusal_is_about_diplomacy_not_the_collision(self):
        """Why the review's "unattackable forever" is overstated: at boot
        the province cannot be entered because France is at PEACE with
        Hanover, which is true of every Hanoverian province and has nothing
        to do with the name.

        Killed by: nothing in this slice - it pins the distinction the
        record makes."""
        world = _fresh_world()
        with _suppress():
            ex = CommandExecutor()
        ney = world.get_marshal("Ney")
        ney.location = "Frankfurt"
        with _suppress():
            result = ex.execute({"command": {
                "marshal": "Ney", "action": "move", "target": "Brunswick",
                "type": "specific"}}, {"world": world, "executor": ex})
        assert not result.get("success")
        assert "Hanover" in str(result.get("message") or "")

    def test_the_length_floor_is_harmless_because_exact_short_circuits(self):
        """`_plausible_name_typo` rejects any query under four characters,
        so it says a marshal's OWN name is not a plausible typo of itself.

        ⚠ The first cut of this test named a killer that CANNOT OCCUR, and a
        refuter proved it by applying that killer — moving the gate onto the
        exact arm — and watching the whole file stay green. The reason is
        the fact this test now pins instead: `_fuzzy_match_marshal`
        short-circuits on a case-insensitive `world.get_marshal` BEFORE the
        matcher is consulted, so the fuzzy `exact` action is unreachable at
        that seam and its `result["action"] == "exact"` disjunct is dead
        code. It is kept for symmetry with its two siblings — at the ENEMY
        seam the same disjunct IS reachable, through a lowercase name — and
        recorded here rather than deleted.

        Killed by: removing the head short-circuit, which is what actually
        makes the length floor harmless."""
        assert _plausible_name_typo("Ney", "Ney") is False
        world = _fresh_world()
        with _suppress():
            ex = CommandExecutor()
        seen = []
        original = ex.fuzzy_matcher.match_with_context

        def spy(query, candidates):
            seen.append(query)
            return original(query, candidates)

        ex.fuzzy_matcher.match_with_context = spy
        try:
            assert ex._fuzzy_match_marshal("Ney", world)[0] is not None
            assert seen == [], (
                "the matcher was consulted for an exact name, so the length "
                "floor is no longer harmless: " + repr(seen))
        finally:
            ex.fuzzy_matcher.match_with_context = original


# ══════════════════════════════════════════════════════════════════
# 13. The durable half - a new collision cannot be authored quietly
# ══════════════════════════════════════════════════════════════════

class TestTheValidatorRule:
    """The typo gate closes today's twelve by lexical accident, not because
    it knows `Gascony` is a place. Content grows: the 22-name recruitment
    bench already contributes `Oran -> Shrapnel` at score 75, and ES-7
    mints province-derived titles. The durable half is a validator rule.
    """

    def _validate(self):
        from backend.modding.validator import validate_scenario
        with _suppress():
            return validate_scenario(
                json.loads(SCENARIO_PATH.read_text(encoding="utf-8")))

    def test_the_shipped_scenario_still_passes(self):
        """WARNING, not error, deliberately: `europe_1805.json` ships the
        one collision and must keep booting.

        Killed by: `add_error` instead of `add_warning`."""
        assert self._validate().is_valid

    def test_it_names_brunswick(self):
        """Killed by: deleting the exact-collision arm."""
        messages = [w.message for w in self._validate().warnings]
        assert any("Brunswick" in m and "also a province" in m
                   for m in messages), messages

    def test_it_would_catch_a_new_typo_band_collision(self):
        """The arm that is inert on the shipped board and is the whole
        point: a marshal authored within a typed mistake of a province
        sails straight through the runtime gate.

        Killed by: deleting the typo-band arm."""
        from backend.modding.validator import validate_scenario
        data = json.loads(SCENARIO_PATH.read_text(encoding="utf-8"))
        data["marshals"]["Gascon"] = dict(
            data["marshals"]["Ney"], name="Gascon")
        with _suppress():
            result = validate_scenario(data)
        assert any("Gascon" in w.message and "typed mistake" in w.message
                   for w in result.warnings), [w.message for w in result.warnings]

    def test_it_names_a_colliding_BENCH_candidate_by_its_bench_path(self):
        """The `marshal_pool` arm had no test at all - deleting it was inert
        against the whole suite, because the shipped bench contributes
        nothing and the one test that mentioned the bench never called the
        validator.

        It also pins the PATH: a bench candidate reported as
        `marshals.<Name>` sends the author grepping for a key that does not
        exist.

        Killed by: deleting the pool arm, or hard-coding the `marshals.`
        path prefix."""
        from backend.modding.validator import validate_scenario
        data = json.loads(SCENARIO_PATH.read_text(encoding="utf-8"))
        data["marshal_pool"]["France"].append(
            dict(data["marshal_pool"]["France"][0], name="Gascogny"))
        with _suppress():
            result = validate_scenario(data)
        hits = [w for w in result.warnings if "Gascogny" in w.message]
        assert hits, [w.message for w in result.warnings]
        assert hits[0].path.startswith("marshal_pool.France["), hits[0].path

    def test_it_checks_the_map_the_scenario_actually_boots_into(self):
        """`from_scenario` resolves regions three ways; hardcoding the Europe
        registry made the rule MISS a mod colliding with its own province and
        FALSE-POSITIVE on a Europe name absent from that mod.

        Killed by: reverting to `create_europe_regions()` unconditionally."""
        from backend.modding.validator import validate_scenario
        own = {
            "scenario_schema_version": 1, "player_nation": "France",
            "regions": {"Wavre": {"name": "Wavre", "terrain": "plains",
                                  "region_type": "rural",
                                  "starting_controller": "France",
                                  "adjacent_regions": []}},
            "marshals": {"Wavre": {"name": "Wavre", "location": "Wavre",
                                   "strength": 1000,
                                   "personality": "aggressive"}},
        }
        with _suppress():
            hit = validate_scenario(own)
        assert any("Wavre" in w.message and "also a province" in w.message
                   for w in hit.warnings), [w.message for w in hit.warnings]

        foreign = dict(own)
        foreign["marshals"] = {"Brunswick": dict(
            own["marshals"]["Wavre"], name="Brunswick")}
        with _suppress():
            miss = validate_scenario(foreign)
        assert not any("also a province" in w.message
                       for w in miss.warnings), [w.message for w in miss.warnings]

    def test_a_malformed_scenario_is_reported_not_crashed(self):
        """A regression this slice introduced and the review caught: the
        block read `(data.get("marshals") or {}).keys()`, and `[] or {}`
        masks only the EMPTY list. `validate_scenario` is called from
        `WorldState.from_scenario`, so a malformed scenario raised
        `AttributeError` out of the BOOT path instead of being reported.

        Killed by: reverting either typed read to `or {}`."""
        from backend.modding.validator import validate_scenario
        for payload in ({"marshals": [{"name": "Ney"}]},
                        {"marshals": "nope"},
                        {"marshal_pool": ["x"]},
                        {"marshal_pool": "nope"},
                        {"marshal_pool": {"France": [{"name": 123}]}}):
            data = {"scenario_schema_version": 1, "player_nation": "France"}
            data.update(payload)
            with _suppress():
                validate_scenario(data)     # must not raise

    def test_the_name_checked_is_the_name_the_seam_matches_on(self):
        """The seam builds its candidate list from `marshal.name`, not from
        the dict key, so the validator must read the same string.

        Killed by: reverting to `set(data["marshals"].keys())`."""
        from backend.modding.validator import validate_scenario
        data = json.loads(SCENARIO_PATH.read_text(encoding="utf-8"))
        entry = dict(data["marshals"]["Ney"], name="Gascony")
        data["marshals"]["M1"] = entry
        with _suppress():
            result = validate_scenario(data)
        assert any("'Gascony' is also a province" in w.message
                   for w in result.warnings), [w.message for w in result.warnings]

    def test_the_bench_collapse_is_closed_at_runtime_too(self, monkeypatch):
        """`Oran -> Shrapnel` (75) is the THIRTEENTH collapse, contributed by
        the commissionable bench rather than the board — the case the whole
        validator section exists for.

        ⚠ The first cut of this test asserted `_plausible_name_typo("Oran",
        "Shrapnel") is False` and nothing else: a parser fact, not the
        runtime it named. The review proved it passed with every gate
        neutralised. It now commissions the man onto the board and drives
        the seam.

        Killed by: deleting the enemy-seam gate."""
        from backend.models.marshal import Marshal
        world = _fresh_world()
        with _suppress():
            ex = CommandExecutor()
        assert world.get_region("Oran") is not None
        world.marshals["Shrapnel"] = Marshal(
            name="Shrapnel", nation="Britain", location="London",
            strength=8000, personality="cautious")
        assert ex._fuzzy_match_enemy("Oran", world, "France")[0] is None
        assert ex._fuzzy_match_marshal("Oran", world)[0] is None
        monkeypatch.setattr(EX, "ENEMY_DIRECTION_GATE_ACTIVE", False)
        recovered, _ = ex._fuzzy_match_enemy("Oran", world, "France")
        assert recovered is not None and recovered.name == "Shrapnel"


# ══════════════════════════════════════════════════════════════════
# 14. The done-when, re-stated: is the AI frozen on the OTHER axis?
# ══════════════════════════════════════════════════════════════════

class TestTheAiIsNotFrozenInstead:
    """The review's sharpest question, and it deserved a measurement rather
    than an argument. A refused AI order is expensive on the wrong axis:
    `enemy_ai._record_failed_action` writes a 2-turn cooldown keyed on
    (marshal, ACTION TYPE) - not on the target - so refusing `Paget attack
    Gascony` would stop Paget attacking anything at all. That is the
    Paget-frozen-for-22-turns shape re-created one layer down, and it would
    be invisible to every test that only asserts a seam's return value.

    Measured over the same 40 ambient turns: the gate makes the AI LESS
    stuck, not more, because the orders now succeed.
    """

    @pytest.fixture(scope="class")
    def cooldowns(self):
        return {label: _run_ambient_cooldowns(levers)
                for label, levers in (("ungated", (False,) * 3),
                                      ("gated", (True,) * 3))}

    def test_the_gate_does_not_increase_failed_action_cooldowns(self, cooldowns):
        """Killed by: a gate that refuses instead of falling through to the
        region - the fall-through at `combat_executor.py` is what keeps this
        number down."""
        assert cooldowns["gated"] <= cooldowns["ungated"], cooldowns

    def test_it_measurably_decreases_them(self, cooldowns):
        """Recorded as a number so a future change that quietly re-freezes
        the AI shows up here: 31 -> 11 on the shipped board.

        Re-measured by FA slice 2 (September 4, 2026): 34 -> 16 on that
        slice's board — and the slice-2 review audit corrected the
        attribution: only TWO of the +6 ungated writes were the brakes'
        engaged fall-throughs; the rest was board divergence, including
        four "Cannot attack X — a coalition ally" refusals (a pre-existing
        AI targeting defect, filed FA-R1).

        Re-measured by the slice-2 REVIEW ROUND (September 4, 2026): 25 vs
        23. The engaged fall-through is gone (a braked corps HOLDS, writing
        nothing), and what remains on the GATED board is almost entirely
        DRILL refusals — fourteen of its twenty-three — a separate
        board-reading defect the round filed as FA-R2. The contract that
        survives is the first pin (the gate never increases the writes);
        "more than halves" was a fact about the slice-2 board, not a
        contract, and is retired here.

        Re-measured by FA slice 4 (September 4, 2026): 29 vs 7. FA-R2's
        fourteen refused drills are gone from the gated board (the rung
        reads `fortified` now), and the ungated board's twenty-nine
        collapses each write one — the gap the gate buys is wide again.

        Killed by: deleting the enemy-seam gate."""
        # Re-measured by the slice-4 REVIEW ROUND (September 4, 2026): 37 vs 4.
        # The gated board's seven survivors were six drilling-corps refusals
        # and one cavalry re-park (R1-5 / R1-7, both fixed); the ungated
        # board's twenty-five collisions plus the AI's other refusals write 37.
        assert cooldowns["ungated"] == 37, cooldowns  # 31 -> 34 -> 25 -> 29 -> 37 across slices
        assert cooldowns["gated"] == 4, cooldowns     # 11 -> 16 -> 23 -> 7 -> 4 across slices


_COOLDOWN_PROBE = r'''
import json, random
from pathlib import Path
from backend.models.world_state import WorldState
from backend.commands.executor import CommandExecutor
from backend.game_logic.turn_manager import TurnManager
from backend.ai import enemy_ai as EA
scen = Path("godot-client/project-sovereign/assets/maps/europe_1805.json")
world = WorldState.from_scenario(str(scen))
executor = CommandExecutor()
tm = TurnManager(world, executor=executor)
gs = {"world": world, "executor": executor}
writes = [0]
orig = EA.EnemyAI._record_failed_action
def rec(self, *a, **kw):
    writes[0] += 1
    return orig(self, *a, **kw)
EA.EnemyAI._record_failed_action = rec
for turn in range(40):
    random.seed(10_000 + turn)
    tm.end_turn(gs)
print("WO10C=" + json.dumps({"writes": writes[0]}))
'''


def _run_ambient_cooldowns(levers):
    return _spawn(_COOLDOWN_PROBE, levers, "WO10C=")["writes"]


# ══════════════════════════════════════════════════════════════════
# 15. The review round's own findings, pinned
# ══════════════════════════════════════════════════════════════════

class TestTheRefusalIsUsefulAndHonest:
    """Five things the review measured wrong with the first cut, each fixed
    and each pinned by driving the real seam."""

    def test_a_mistyped_marshal_is_asked_about_not_discarded(self, ex, world):
        """`_plausible_name_typo` requires the first letter to match, so a
        one-key slip on your OWN marshal refuses — and the first cut then
        threw the candidate away and printed a constant. Measured:
        `Nurat` (score 80) answered "Available: Ney, Davout, Soult", with
        Murat absent. The region seam's own idiom applies: demote to a
        QUESTION.

        Killed by: deleting the demotion arm in `_fuzzy_match_marshal`."""
        for typo, real in (("Nurat", "Murat"), ("avout", "Davout"),
                           ("Aoult", "Soult")):
            marshal, error = ex._fuzzy_match_marshal(typo, world)
            assert marshal is None, typo
            assert error.get("suggestion") == real, (typo, error)
            assert f"Did you mean '{real}'?" in error["message"]

    def test_a_province_is_still_never_asked_about_as_a_marshal(
            self, ex, world):
        """The discriminator that makes the demotion safe, and the reason it
        can exist here and not at the enemy seam: the world knows `Gascony`
        is a place.

        Killed by: dropping the `world.get_region(...) is None` clause."""
        marshal, error = ex._fuzzy_match_marshal("Gascony", world)
        assert marshal is None
        assert "Did you mean" not in error["message"], error

    def test_the_alternatives_are_ranked_not_truncated(self, ex, world):
        """The message was inverted against confidence: gibberish got the
        two nearest names and a near-miss got a constant.

        ⚠ The query matters and the first cut got it wrong — the sweep
        reported the ranking pin INERT because `Zorblax` takes the
        LOW-SCORE arm, whose `suggestions` list `match_with_context`
        populates, so `offered` is non-empty and the ranking branch never
        runs. `Kuzutov` is the shape that reaches it: a `suggest` whose
        match is not one of ours, so the fog-scoped arm declines it and the
        honest arm ranks OUR roster. Ranked it reads Soult, Murat, Davout;
        unranked it would read the roster's own order, Ney, Davout, Soult.

        Killed by: reverting `_honest_alternatives` to `allowed[:3]`."""
        _, error = ex._fuzzy_match_marshal("Kuzutov", world)
        assert error["suggestions"] == ["Soult", "Murat", "Davout"], error
        assert error["suggestions"][:3] != ["Ney", "Davout", "Soult"]
        # the low-score arm keeps its own (already-ranked) suggestions
        _, low = ex._fuzzy_match_marshal("Zorblax", world)
        assert low["suggestions"][:2] == ["Soult", "Murat"], low

    def test_a_prisoner_is_not_offered_as_available(self):
        """Three men in Austrian captivity were offered while five free
        marshals were not.

        Killed by: dropping the `captured_by` / strength clause."""
        world = _fresh_world()
        with _suppress():
            ex = CommandExecutor()
        for name in ("Ney", "Davout", "Soult"):
            captive = world.get_marshal(name)
            captive.strength = 0
            captive.captured_by = "Austria"
        _, error = ex._fuzzy_match_marshal("Zorblax", world)
        assert not ({"Ney", "Davout", "Soult"} & set(error["suggestions"])), error

    def test_the_marshal_suggest_arm_does_not_name_a_fogged_enemy(
            self, ex, world):
        """`Kuzutov` answered "Did you mean 'Kutuzov'?" about an unscouted
        Russian corps, from the sibling arm of a seam this slice had already
        filtered.

        Killed by: dropping `_display_candidates` from the marshal suggest
        arm."""
        _, error = ex._fuzzy_match_marshal("Kuzutov", world)
        assert "Kutuzov" not in str(error.get("message")), error
        assert error.get("suggestion") != "Kutuzov", error


class TestTheAutoAssignRouteJoinsTheSeam:
    """CR-6's bare `attack <x>` and auto-assign resolve through
    `_resolve_auto_assign_attacker`, which used a bare `get_enemy_by_name`
    — so it inherited neither the gate nor the register fix, and one player
    sentence got two different answers by route."""

    def _bare(self, target, world=None, ex=None):
        if world is None:
            world = _fresh_world()
        if ex is None:
            with _suppress():
                ex = CommandExecutor()
        with _suppress():
            return ex.execute({"command": {
                "action": "attack", "target": target,
                "type": "auto_assign_attack"}},
                {"world": world, "executor": ex})

    def test_the_bare_route_answers_in_the_marshal_register(self):
        """Measured before: named route "Enemy 'Kutz' not found…", bare
        route "Region 'Kutz' not found. Did you mean 'Frankfurt'?".

        Killed by: reverting the route to `get_enemy_by_name` alone, or
        dropping its `implausible_correction` clause."""
        message = str(self._bare("Kutz").get("message") or "")
        assert "Did you mean" not in message, message
        assert "Enemy 'Kutz' not found" in message, message

    def test_the_bare_route_is_case_insensitive_like_its_sibling(self):
        """`get_enemy_by_name` has no case fallback while the seam matches
        case-insensitively, so `attack mack` answered "Did you mean 'La
        Mancha'?" while `attack Mack` mustered.

        Killed by: reverting the route to `get_enemy_by_name` alone."""
        lower = str(self._bare("mack").get("message") or "")
        upper = str(self._bare("Mack").get("message") or "")
        assert "Mack" in lower and "La Mancha" not in lower, lower
        assert lower.split("—")[0] == upper.split("—")[0], (lower, upper)

    def test_a_destroyed_enemy_still_answers_honestly(self):
        """The regression the fix itself introduced and the suite caught:
        `_fuzzy_match_enemy` filters `strength > 0`, so routing through it
        FIRST lost PC15-4's "already been destroyed" answer.

        Killed by: removing the exact `get_enemy_by_name` probe above the
        fuzzy call."""
        world = _fresh_world()
        with _suppress():
            ex = CommandExecutor()
        mack = world.get_marshal("Mack")
        mack.strength = 0
        message = str(self._bare("Mack", world, ex).get("message") or "")
        assert "destroyed" in message.lower(), message


# ══════════════════════════════════════════════════════════════════
# 16. The two the SECOND refuter found that the eight lenses missed
# ══════════════════════════════════════════════════════════════════

class TestTheFallbackDoesNotReopenTheLeak:

    def test_an_emptied_roster_names_nobody_rather_than_everybody(self):
        """`or all_marshals` sat one line below the comment forbidding it,
        and re-opened the slice's own P1: with the player's roster emptied —
        reachable, since PC15-1's `destroy_marshal` pops marshals — the
        refusal fell back to the omniscient roster and printed
        "Available: ArchdukeJohn, Castanos, Mack", naming the same unscouted
        Spanish corps the review round quoted.

        Killed by: restoring the `or all_marshals` fallback."""
        world = _fresh_world()
        with _suppress():
            ex = CommandExecutor()
        for name in [m.name for m in list(world.marshals.values())
                     if m.nation == world.player_nation]:
            world.marshals.pop(name, None)
        _, error = ex._fuzzy_match_marshal("Nurat", world)
        assert error["suggestions"] == [], error
        assert "none" in error["message"], error


class TestTheTranspositionResidue:
    """The gate's real cost, named because no lens did until the second
    refuter's differential: `_plausible_name_typo`'s limit is ONE edit under
    six characters, so a double-transposition on a five-letter name refuses
    where it used to resolve. `Solut`/`Soutl` -> Soult, `Mruat`/`Muart` ->
    Murat, 383 flips over 2,636 generated variants.

    That is the documented contract, not a defect — but it must ASK rather
    than shrug, which is what the demotion buys."""

    def test_a_double_transposition_asks_rather_than_shrugs(self, ex, world):
        """Killed by: deleting the demotion arm in `_fuzzy_match_marshal`."""
        for typo, real in (("Solut", "Soult"), ("Mruat", "Murat"),
                           ("Muart", "Murat")):
            marshal, error = ex._fuzzy_match_marshal(typo, world)
            assert marshal is None, typo
            assert error.get("suggestion") == real, (typo, error)

    def test_the_gate_is_what_refuses_them(self, ex, world, monkeypatch):
        """The other half: with the lever down they resolve silently again,
        so the demotion is answering a real refusal rather than decorating
        one that never happens.

        Killed by: freezing `MARSHAL_DIRECTION_GATE_ACTIVE`."""
        monkeypatch.setattr(EX, "MARSHAL_DIRECTION_GATE_ACTIVE", False)
        marshal, _ = ex._fuzzy_match_marshal("Solut", world)
        assert marshal is not None and marshal.name == "Soult"


# ══════════════════════════════════════════════════════════════════
# 17. The seams UPSTREAM of the gate, which the census cannot see
# ══════════════════════════════════════════════════════════════════

class TestTheParserSeams:
    """`parser.py` has eleven `match_with_context` sites; the census in
    `TestTheCensus` is scoped to `executor.py` BY CONSTRUCTION and could
    never have seen them. Two of the eleven auto-corrected onto a marshal
    with no typo gate while their five siblings all gate:

      * the live-LLM marshal slot — measured, it rewrote SEVEN province
        names to "Ney" (Brittany, Champagne, Gascony, Guyenne, Lorraine,
        Maine, Ukraine);
      * the addressee scan in the meta-action branch — `"Gascony, charge"`
        bound marshal **Ney** at 0.55 confidence.

    The CR-0 guard above the second is written for exactly this ("'Hold
    Bern!' must not hijack Bernadotte") and fails on the 126-province board
    because `_get_known_regions` falls back to the **19-region legacy map**
    whenever the world does not arrive. Gating the arms fixes the
    consequence world-or-no-world; the plumbing question is recorded in the
    landing record rather than papered over.

    **Bounded honestly:** no downstream consequence could be exhibited —
    the marshal is discarded for all four reachable verbs and
    `command_history` records `marshal: null`, so CR-4 focus is not
    poisoned. This is the identical defect one layer up, fixed because it
    is the identical defect.
    """

    def _parse(self, text, world):
        from backend.commands.parser import CommandParser
        with _suppress():
            parser = CommandParser(use_real_llm=False)
            return parser.parse(text, {"world": world})

    def test_a_province_addressee_no_longer_binds_a_marshal(self):
        """Killed by: deleting the gate on the parser's addressee scan."""
        world = _fresh_world()
        result = self._parse("Gascony, charge", world)
        assert (result.get("command") or result).get("marshal") != "Ney", result

    def test_an_ordinary_addressee_typo_still_binds(self):
        """The gate must not cost the CR-2 did-you-mean flow its input.

        Killed by: making the parser gate refuse unconditionally."""
        world = _fresh_world()
        result = self._parse("Davout, charge", world)
        assert (result.get("command") or result).get("marshal") == "Davout", result

    def test_the_llm_marshal_slot_no_longer_rewrites_a_province(self):
        """Seam A, driven directly — the mock parse route reaches seam B
        (the addressee scan) and NOT this one, which is why the sweep
        reported its pin inert. Measured before: this arm rewrote seven
        province names to "Ney".

        Killed by: deleting the gate on the parser's LLM marshal slot."""
        from backend.commands.parser import CommandParser
        world = _fresh_world()
        with _suppress():
            parser = CommandParser(use_real_llm=False)
            out, err = parser._apply_fuzzy_matching(
                {"marshal": "Gascony", "action": "fortify", "target": None},
                "Gascony, fortify", world=world, game_state={"world": world})
        assert out.get("marshal") != "Ney", (out, err)
        assert (err or {}).get("kind") == "marshal_not_found", err

    def test_a_real_marshal_typo_still_survives_that_seam(self):
        """Killed by: making the parser gate refuse unconditionally."""
        from backend.commands.parser import CommandParser
        world = _fresh_world()
        with _suppress():
            parser = CommandParser(use_real_llm=False)
            out, err = parser._apply_fuzzy_matching(
                {"marshal": "Davout", "action": "fortify", "target": None},
                "Davout, fortify", world=world, game_state={"world": world})
        assert out.get("marshal") == "Davout", (out, err)
        assert err is None, err

    def test_the_seam_census_states_its_own_boundary(self):
        """The `executor.py` census is scoped by construction, and a reader
        must not mistake it for a whole-backend guarantee. This asserts the
        boundary is WRITTEN, and counts the parser's own gated sites so a
        new ungated one shows up as a number change.

        Killed by: removing the boundary sentence, or adding an ungated
        `match_with_context` to `parser.py`."""
        parser_src = _code_only(_read(REPO / "backend" / "commands" / "parser.py"))
        assert parser_src.count("match_with_context") == 10, (
            parser_src.count("match_with_context"))
        assert parser_src.count("_plausible_name_typo") >= 7


class TestWhatThePlayerActuallySees:
    """The question eight reviewers did not ask, and a refuter did: is the
    refusal reachable at all?

    Measured over the real `/command` route it is NOT reached by a typed
    province name — validation clears a target that is in neither register,
    and ESP-EV-4's `auto_resolved` arm then picks the nearest visible enemy
    and **discloses** the choice. So the fog fix and the register fix are
    defence in depth on a seam no typed sentence reaches today; the
    auto-assign route this slice wired through it is what makes it
    reachable, and an AI order reaches it seventeen times in forty turns.

    What these pins guarantee is the thing that matters to a player, and it
    is stronger than "the message is correct": **the typed path never
    silently attacks a man you did not name.** It either acts on the
    province, or it says whose army it is marching on instead.
    """

    @staticmethod
    def _client():
        import contextlib as _c
        from fastapi.testclient import TestClient
        from backend.commands.parser import CommandParser
        import backend.main as main_module

        @_c.contextmanager
        def _ctx():
            saved = (main_module.parser, main_module.world,
                     main_module.game_state, main_module.executor)
            with _suppress():
                main_module.parser = CommandParser(use_real_llm=False)
                main_module.world = _fresh_world()
                main_module.executor = CommandExecutor()
                main_module.game_state = {"world": main_module.world,
                                          "executor": main_module.executor}
                client = TestClient(main_module.app)
            try:
                yield client, main_module.world
            finally:
                (main_module.parser, main_module.world,
                 main_module.game_state, main_module.executor) = saved
        return _ctx()

    def _say(self, client, text):
        with _suppress():
            response = client.post("/command", json={"command": text})
        return str((response.json() or {}).get("message") or "")

    def test_no_typed_order_silently_attacks_an_unnamed_marshal(self):
        """The player-facing guarantee. Every province name the collapse
        used to eat is typed at the real endpoint; each answer must either
        concern that province or DISCLOSE the substitution by name.

        Killed by: deleting the enemy-seam gate (the answer then names a
        marshal with no disclosure)."""
        with self._client() as (client, world):
            for province in ("Gascony", "Bern", "Leon", "Oslo", "Rome",
                             "Ukraine", "Maine", "Brittany"):
                message = self._say(client, f"Ney, attack {province}")
                grounded = (province in message
                            or "named no foe our maps know" in message
                            or "already controlled" in message
                            or "not found" in message)
                assert grounded, (province, message[:200])

    def test_no_typed_REFUSAL_prints_a_raw_roster_key(self):
        """The humanisation, at the surface rather than at the seam.

        Scoped to REFUSALS deliberately. A first cut asserted no message may
        contain a raw key and went red on a SUCCESS line — *"moving toward
        ArchdukeJohn at Tyrol"* — which is a real camelCase leak but a
        pre-existing one, owned by NPC-12's open census of ~426
        enemy-reachable interpolations, not by this slice. The sweep's
        baseline gate caught it, which is what that gate is for.

        Killed by: reverting `_humanised` to `list(names)`."""
        with self._client() as (client, world):
            camel = [k for k in world.marshals if k != _humanise(k)]
            assert camel, "fixture precondition: some key needs humanising"
            checked = 0
            for text in ("attack Zorblax", "Zorblax, fortify",
                         "Zorblax, hold", "Kuzutov, fortify",
                         "Ney, attack Zorblax"):
                message = self._say(client, text)
                if not any(mark in message for mark in
                           ("not found", "Available:", "Did you mean",
                            "no Marshal", "does not answer to us",
                            "named no foe")):
                    continue
                checked += 1
                for key in camel:
                    assert key not in message, (text, key, message[:200])
            assert checked >= 3, ("too few typed refusals reached — the "
                                  "battery no longer exercises the surface")

    def test_the_seam_message_is_defence_in_depth_not_a_screen(self):
        """Recorded as a measurement rather than a claim: the `Available:`
        refusal is NOT produced by these typed orders. If this ever starts
        failing, the message became player-visible and its copy is then
        worth reviewing on its own.

        Killed by: nothing in this slice — it is the reachability finding,
        pinned so the next reader inherits the measurement."""
        with self._client() as (client, world):
            seen = [self._say(client, f"Ney, attack {q}")
                    for q in ("Gascony", "Kutz", "Zorblax")]
        assert not any("not found. Available:" in m for m in seen), seen


def _humanise(name):
    from backend.display_names import humanize_entity_name
    return humanize_entity_name(name)
