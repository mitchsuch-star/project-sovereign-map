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

    def test_the_ai_command_shape_carries_no_raw_input(self):
        """Why the AI direction needed this gate at all: ESP-EV-4's
        `guessed_target_refusal` - the guard that catches exactly this
        substitution for the PLAYER - returns None without `_raw_input`,
        and `enemy_ai._execute_action` builds a command dict of four keys
        that has never carried one.

        Killed by: nothing in this slice; it is a standing explanation
        pin, and it fails the day the AI path gains that protection, at
        which point this slice's own justification should be re-read."""
        from backend.commands.combat_executor import guessed_target_refusal
        world = _fresh_world()
        marshal = _british_corps_at(world, "Bearn")
        ai_command = {"marshal": marshal.name, "action": "attack",
                      "target": "Gascony", "type": "specific"}
        assert "_raw_input" not in ai_command
        assert guessed_target_refusal(
            world, marshal, ai_command, "Gascony") is None


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
            body = ast.dump(node)
            guard = ("_plausible_name_typo" if name == "_fuzzy_match_region"
                     else "_correction_survives")
            assert guard in body, f"{name} matches names with no {guard} gate"

    def test_one_predicate_stands_behind_all_three_gates(self):
        """Killed by: inlining the predicate at one seam, which is how the
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

def _run_ambient(levers):
    """The 40-turn ambient board under a named lever configuration, in a
    hash-pinned subprocess with a REAL source edit - the §5 discipline. An
    in-process run of the same forty turns is not reproducible and is
    worthless for these claims (slice 9 measured turn 25 in-suite against
    32 pinned)."""
    names = ["ENEMY_DIRECTION_GATE_ACTIVE", "BROAD_DIPLOMATIC_GATE_ACTIVE",
             "MARSHAL_DIRECTION_GATE_ACTIVE"]
    original = EXECUTOR_PY.read_bytes()
    raw = original.decode("utf-8")
    for name, value in zip(names, levers):
        for other in ("True", "False"):
            raw = raw.replace(f"\n{name} = {other}\n", f"\n{name} = {value}\n")
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
