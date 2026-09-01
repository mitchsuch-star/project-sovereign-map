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
    a FREEZE. Britain's Paget stood at Bearn, adjacent to Gascony, and for
    twenty-two consecutive turns his attack on that province was redirected
    to Ney - in Vienna, eight provinces away - and refused as out of range:
    "Paget cannot reach Gascony (Vienna) from Bearn! Range: 1, Distance: 8"
    names the province and prints another man's location beside it.

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
    """Britain's Iberian army stood still for 22 turns because every order
    it gave named a province the resolver handed to a marshal elsewhere."""

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

    def test_the_suggest_band_is_untouched(self, ex, world):
        """The medium-confidence arm never went through the gate and must
        still ask.

        Killed by: moving the gate above the `suggest` branch."""
        marshal, error = ex._fuzzy_match_enemy("Kutz", world, "France")
        if marshal is None and error and error.get("suggestion"):
            assert "Did you mean" in error["message"]

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

    def test_the_parser_addressee_gives_the_province(self, world):
        """Slice 2's precedent, unchanged: a lead token that is also a
        region name is never an enemy addressee.

        Killed by: deleting slice 2's region carve-out in
        `_resolve_enemy_addressee`."""
        resolved = P._resolve_enemy_addressee(
            "Brunswick, hold",
            [m.name for m in world.marshals.values()
             if m.nation != world.player_nation],
            list(world.regions.keys()))
        assert not resolved, resolved


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


def _rewrite_levers(source: str, levers) -> str:
    """`source` with the three levers set, line-ending agnostic.

    The first cut of this helper matched on `"\n{name} = {other}\n"` against
    the raw file bytes. That worked until the mutation sweep touched
    `executor.py` - `pathlib.write_text` re-emits with `os.linesep`, so the
    file became CRLF, every pattern missed, and the helper SILENTLY set
    nothing: the "ungated" arm ran the gated tree and the tests below
    compared the wrong world. A lever-setter that can quietly do nothing is
    the same class of instrument failure as an inert pin, so it now
    normalises first and the caller asserts the edit landed.
    """
    text = source.replace("\r\n", "\n")
    for name, value in zip(LEVER_NAMES, levers):
        for other in ("True", "False"):
            text = text.replace(f"\n{name} = {other}\n",
                                f"\n{name} = {value}\n")
    for name, value in zip(LEVER_NAMES, levers):
        assert f"\n{name} = {value}\n" in text, (
            f"lever {name} was not set to {value} - the rewrite no-opped")
    return text


def _run_ambient(levers):
    """The 40-turn ambient board under a named lever configuration, in a
    hash-pinned subprocess with a REAL source edit - the §5 discipline. An
    in-process run of the same forty turns is not reproducible and is
    worthless for these claims (slice 9 measured turn 25 in-suite against
    32 pinned)."""
    original = EXECUTOR_PY.read_bytes()
    raw = _rewrite_levers(original.decode("utf-8"), levers)
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = "0"
    env["PYTHONPATH"] = str(REPO)
    env["SOVEREIGN_SEED"] = "historical"
    env["LLM_MODE"] = "mock"
    env.pop("SOVEREIGN_SCENARIO", None)
    env.pop("SOVEREIGN_MAP", None)
    env.pop("PYTHONIOENCODING", None)
    try:
        EXECUTOR_PY.write_bytes(raw.encode("utf-8"))
        proc = subprocess.run(
            [sys.executable, "-c", _AMBIENT_PROBE],
            env=env, cwd=str(REPO), capture_output=True, text=True,
            timeout=600)
    finally:
        EXECUTOR_PY.write_bytes(original)
    assert proc.returncode == 0, proc.stdout[-2000:] + proc.stderr[-2000:]
    blob = proc.stdout.split("WO10=")[-1].splitlines()[0]
    return json.loads(blob)


_AMBIENT_PROBE = r'''
import json, random, sys
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
sys.stderr.write("done\n")
print("WO10=" + json.dumps({"hits": hits, "series": series}))
'''


class TestTheLeverRewrite:
    """The instrument that measures the arms must not be able to lie."""

    def test_the_rewrite_refuses_to_no_op_on_crlf(self):
        """Found by accident, and it is the reason this pin exists: the
        mutation sweep re-emits `executor.py` with `os.linesep`, so the
        file becomes CRLF and an LF-anchored replace matches nothing. The
        arms then run the SHIPPED tree while claiming to be ungated.

        Killed by: dropping the newline normalisation, or the assertion."""
        body = "\n".join(f"{name} = True" for name in LEVER_NAMES)
        source = ("# header\n\n" + body + "\n\n# tail\n"
                  ).replace("\n", "\r\n")
        assert "\r\r\n" not in source
        rewritten = _rewrite_levers(source, ("False", "False", "False"))
        for name in LEVER_NAMES:
            assert f"\n{name} = False\n" in rewritten

    def test_the_rewrite_raises_when_a_lever_is_missing(self):
        """Killed by: deleting the verification loop."""
        with pytest.raises(AssertionError):
            _rewrite_levers("nothing to see here\n", ("False",) * 3)


class TestTheAmbientBoard:
    """The re-measured count the done-when hangs on. Slice 9 moved the
    board (Switzerland now rebels at 32, not 28), so the contract's "17x in
    40 turns" had to be re-taken; it reproduces exactly, because every one
    of the seventeen falls at turns 6-27, before slice 9's divergence."""

    @pytest.fixture(scope="class")
    def ungated(self):
        return _run_ambient(("False", "False", "False"))

    @pytest.fixture(scope="class")
    def gated(self):
        return _run_ambient(("True", "True", "True"))

    def test_the_ungated_board_collapses_seventeen_times(self, ungated):
        """Killed by: nothing in this slice - it is the defect's own
        measurement, and it fails when the board changes under it, which is
        the warning the next slice needs."""
        seams = {}
        for name, _q, _m in ungated["hits"]:
            seams[name] = seams.get(name, 0) + 1
        assert seams == {"_fuzzy_match_enemy": 17}, seams

    def test_all_seventeen_are_the_ai_naming_a_province(self, ungated):
        """Killed by: nothing - it records WHICH provinces, so a future
        board change is legible rather than merely different."""
        assert {(q, m) for _s, q, m in ungated["hits"]} == {
            ("Leon", "Napoleon"), ("Gascony", "Ney")}

    def test_the_gated_board_collapses_never(self, gated):
        """The done-when line: the AI stops resolving `Gascony -> Ney`.

        Killed by: deleting any of the three gates."""
        assert gated["hits"] == [], gated["hits"]

    def test_the_ungated_arm_reproduces_the_prior_series(self, ungated):
        """Attribution arm 0. The levers are honest: with all three down
        the board reproduces the series recorded BEFORE this slice,
        byte-for-byte.

        Killed by: a change to the gates that is not actually behind the
        levers - the exact shape of slice 9's shipped P2."""
        assert ungated["series"] == [
            70, 68, 66, 64, 72, 73, 74, 80, 78, 76, 74, 72, 70, 71, 72, 70,
            68, 66, 69, 67, 65, 83, 81, 79, 77, 75, 73, 71, 69, 66, 63, 50,
            47, 44, 41, 38, 35, 32, 29, 26, 23]

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

    def test_the_suggest_band_still_clarifies(self, ex, world):
        """The other half of the 30 never resolved - it asked, and must go
        on asking.

        Killed by: making the gate refuse the `suggest` arm too."""
        clarified = [name for name in sorted(world.regions)
                     if (lambda pair: pair[0] is None and pair[1]
                         and pair[1].get("suggestion"))(
                             ex._fuzzy_match_enemy(name, world, None))]
        assert len(clarified) == 7, clarified

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
        return {m.name for m in world.get_visible_enemies("France")}

    def test_a_refused_auto_correct_names_only_visible_enemies(self, ex, world):
        """Killed by: passing `all_enemies` to `_honest_alternatives`
        instead of `_display_candidates(...)`."""
        _, error = ex._fuzzy_match_enemy("Gascony", world, None)
        visible = self._visible(world)
        assert error["suggestions"], "the refusal named nobody"
        assert set(error["suggestions"]) <= visible, (
            f"leaked {set(error['suggestions']) - visible}")

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
        hidden = [m for m in world.get_enemy_marshals()
                  if m.strength > 0 and m.name not in self._visible(world)]
        assert hidden, "fixture precondition: some enemy must be fogged"
        marshal, _ = ex._fuzzy_match_enemy(hidden[0].name, world, None)
        assert marshal is not None and marshal.name == hidden[0].name

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

    def test_a_genuine_province_typo_still_asks_about_the_province(self):
        """The branch must not be disabled wholesale: a mistyped PROVINCE
        still gets its own register's question.

        Killed by: removing the region-suggestion branch instead of
        conditioning it."""
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
        assert code.count("ADDRESSEE position") == 1
        assert code.count("TARGET position") == 1

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

    def test_the_length_floor_would_unaddress_a_short_marshal(self):
        """A hazard the review found, harmless today and pinned so it stays
        harmless: `_plausible_name_typo` rejects any query under four
        characters, so it says a marshal's OWN name is not a plausible typo
        of itself. That is fine only because the gate never guards the
        EXACT arm.

        Killed by: moving the gate onto the exact arm - at which point Ney
        becomes unaddressable and this fails, loudly, naming the reason."""
        assert _plausible_name_typo("Ney", "Ney") is False
        world = _fresh_world()
        with _suppress():
            ex = CommandExecutor()
        assert ex._fuzzy_match_marshal("Ney", world)[0] is not None


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

    def test_the_bench_collapse_is_closed_at_runtime_too(self, ex, world):
        """`Oran -> Shrapnel` (75) is the 13th collapse, contributed by the
        commissionable bench rather than the board.

        Killed by: deleting the enemy-seam gate."""
        assert _plausible_name_typo("Oran", "Shrapnel") is False


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
                for label, levers in (("ungated", ("False",) * 3),
                                      ("gated", ("True",) * 3))}

    def test_the_gate_does_not_increase_failed_action_cooldowns(self, cooldowns):
        """Killed by: a gate that refuses instead of falling through to the
        region - the fall-through at `combat_executor.py` is what keeps this
        number down."""
        assert cooldowns["gated"] <= cooldowns["ungated"], cooldowns

    def test_it_measurably_decreases_them(self, cooldowns):
        """Recorded as a number so a future change that quietly re-freezes
        the AI shows up here: 31 -> 11 on the shipped board.

        Killed by: deleting the enemy-seam gate."""
        assert cooldowns["ungated"] == 31, cooldowns
        assert cooldowns["gated"] == 11, cooldowns


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
    original = EXECUTOR_PY.read_bytes()
    raw = _rewrite_levers(original.decode("utf-8"), levers)
    env = dict(os.environ)
    env.update(PYTHONHASHSEED="0", PYTHONPATH=str(REPO),
               SOVEREIGN_SEED="historical", LLM_MODE="mock")
    env.pop("SOVEREIGN_SCENARIO", None)
    env.pop("SOVEREIGN_MAP", None)
    env.pop("PYTHONIOENCODING", None)
    try:
        EXECUTOR_PY.write_bytes(raw.encode("utf-8"))
        proc = subprocess.run([sys.executable, "-c", _COOLDOWN_PROBE],
                              env=env, cwd=str(REPO), capture_output=True,
                              text=True, timeout=600)
    finally:
        EXECUTOR_PY.write_bytes(original)
    assert proc.returncode == 0, proc.stdout[-2000:] + proc.stderr[-2000:]
    return json.loads(proc.stdout.split("WO10C=")[-1].splitlines()[0])["writes"]
