"""FA-S16-D3 (FA-44) — "The Scale of a Battle".

Berthier told the player *"Even the favorable ground could not save Massena,
Sire"* about an exchange of one casualty against fifty-eight.
`_pick_observation` had no scale gate at any priority.

⚠ **The ruling is not "add a floor" — it is "stop having a fourth opinion."**
The row's own `fix_shape` proposes a SECOND absolute 1,000 for a question a
landed sibling already answers at 500, and that sibling carries a written
dissent. What shipped instead extracts `diplomacy.record_battle`'s bare
`1000` into a named home both readers share: the floor count goes **3 → 2**,
and the engine can no longer score a day at zero while the narrator calls it
a grievous defeat.

⚠ **The shape is PER-ARM, not positional, and that was measured.** A
`we_lost and total < FLOOR` early return placed at priority 3.5 — the
obvious build — reds a standing behaviour pin
(`TestCavalryOverrunAttacker::test_defender_cavalry_counter_different_template`,
total 350) and re-buries PT-D4's rout arm, turning *"his men are scattered"*
into *"there was no battle to speak of"* about a day on which a corps broke.
The gate is therefore applied to the five GRAVITY verdicts only. Every arm
that reports a mechanical STATE is deliberately untouched.
"""

import ast
import inspect
import pathlib
import random
import re

import pytest

from backend.game_logic import battle_report, battle_scale, diplomacy, dispatch

REPO = pathlib.Path(__file__).resolve().parents[1]


def _code(src: str) -> str:
    """Source with comments AND docstrings stripped.

    Slice 13's lesson, three times over: a census that matches the prose
    explaining a guard stays green when the guard is deleted.
    """
    tree = ast.parse(src)
    drop = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                             ast.AsyncFunctionDef)):
            body = getattr(node, "body", None)
            if (body and isinstance(body[0], ast.Expr)
                    and isinstance(body[0].value, ast.Constant)
                    and isinstance(body[0].value.value, str)):
                for ln in range(body[0].lineno, body[0].end_lineno + 1):
                    drop.add(ln)
    out = []
    for i, line in enumerate(src.split("\n"), start=1):
        if i in drop:
            continue
        out.append(line.split("#")[0])
    return "\n".join(out)


def _battle(atk_cas, def_cas, *, def_terrain=0, atk_terrain=0,
            def_original=None, atk_original=20000, outcome="attacker_victory",
            **extra):
    """FA-44's own geometry by default: France defending, favourable ground."""
    d = {
        "outcome": outcome,
        "attacker_nation": "Austria",
        "attacker": {"name": "ArchdukeCharles", "casualties": atk_cas},
        "defender": {"name": "Massena", "casualties": def_cas},
        "attacker_original_strength": atk_original,
        "defender_original_strength": (def_original if def_original is not None
                                       else def_cas),
        "modifier_snapshot": {
            "attacker": ([{"label": "Terrain", "type": "bonus",
                           "value": atk_terrain}] if atk_terrain else []),
            "defender": ([{"label": "Terrain", "type": "bonus",
                           "value": def_terrain}] if def_terrain else []),
        },
    }
    d["defender"].update(extra)
    return d


def _arm_is_gated(bank: str) -> bool:
    """Is the arm returning `bank` guarded by the scale predicate?

    ⚠ AST, not a character window. My first cut looked back 300 characters
    from the bank name and reported the ROUT arm as gated — it was seeing
    the `_at_scale` belonging to `lost_costly`, the arm directly above it.
    A census must count the thing, not a string near it (slice 3's lesson).
    """
    fn = ast.parse(inspect.getsource(battle_report._pick_observation).lstrip())
    target = None
    for node in ast.walk(fn):
        if isinstance(node, ast.Constant) and node.value == bank:
            target = node
            break
    assert target is not None, f"{bank} is not returned anywhere"

    # every `if` whose body lexically contains the return
    for node in ast.walk(fn):
        if isinstance(node, ast.If):
            lo, hi = node.body[0].lineno, node.body[-1].end_lineno
            if lo <= target.lineno <= hi:
                if "_at_scale" in ast.dump(node.test):
                    return True
    return False


def _lines(battle, n=120, nation="France"):
    seen = set()
    for s in range(n):
        random.seed(s)
        seen.add(battle_report._pick_observation(battle, nation))
    return seen


# ═══════════════════════════════════════════════════════════════════════════
# The row's own case, in both lever positions
# ═══════════════════════════════════════════════════════════════════════════

class TestTheRowsOwnCase:

    def test_the_verdict_is_gone(self):
        """One casualty against fifty-eight, on ground worth +20."""
        for line in _lines(_battle(1, 58, def_terrain=20)):
            assert "favorable ground" not in line
            assert "superior ground" not in line
            assert "hills were ours" not in line

    def test_a_skirmish_says_it_was_a_skirmish(self):
        got = _lines(_battle(1, 58, def_terrain=20))
        assert got, "the sampler produced nothing"
        assert all(re.search(r"skirmish|Hardly an engagement|Scarcely an action",
                             line) for line in got), got

    def test_the_lever_reproduces_the_pre_fix_sentence(self, monkeypatch):
        """⚠ The FALSE arm must reproduce the defect VERBATIM, or the lever
        is not a lever — it is a different bug."""
        monkeypatch.setattr(battle_scale, "SKIRMISH_GATE_ACTIVE", False)
        got = _lines(_battle(1, 58, def_terrain=20))
        assert any("Even the favorable ground could not save Massena, Sire."
                   in line for line in got), got

    def test_the_same_shape_at_scale_still_draws_the_verdict(self):
        """The gate must bite on SIZE, not on the terrain arm. A real battle
        lost on favourable ground keeps its verdict."""
        got = _lines(_battle(3000, 5000, def_terrain=20, def_original=20000))
        assert any("ground" in line or "hills" in line for line in got), got
        assert not any("skirmish" in line for line in got), got


# ═══════════════════════════════════════════════════════════════════════════
# One number, in a home neither reader owns
# ═══════════════════════════════════════════════════════════════════════════

class TestOneFloorTwoReaders:

    def test_the_war_score_and_the_narrator_read_the_same_object(self,
                                                                 monkeypatch):
        """⚠ THE DRIFT PIN, and the reason `from ... import` is forbidden.

        Move the constant in its OWN home and both readers must move. A
        from-import binds a copy: measured, patching the owner leaves the
        consumer reading 1000, and this pin is unsatisfiable against it.
        """
        monkeypatch.setattr(battle_scale, "MIN_BATTLE_CASUALTIES", 999_999)
        assert diplomacy.battle_scale.MIN_BATTLE_CASUALTIES == 999_999
        assert battle_report.battle_scale.MIN_BATTLE_CASUALTIES == 999_999
        # …and it is not merely visible, it is CONSULTED: a 10,000-casualty
        # battle now falls under the moved floor and draws the skirmish line.
        got = _lines(_battle(4000, 6000, def_terrain=20, def_original=20000))
        assert all("skirmish" in ln or "Hardly" in ln or "Scarcely" in ln
                   for ln in got), got

    def test_the_war_score_gate_is_the_extracted_literal(self):
        """`record_battle` must return early below the floor and record above
        it — driven, not read."""
        src = _code(inspect.getsource(diplomacy.record_battle))
        assert "battle_scale.is_a_battle" in src
        assert "< 1000" not in src, "the bare literal survived the extraction"

    def test_neither_reader_binds_a_copy(self):
        """A `from backend.game_logic.battle_scale import ...` anywhere in
        either reader defeats the drift pin above without redding it."""
        for mod in (diplomacy, battle_report):
            src = _code(inspect.getsource(mod))
            assert "from backend.game_logic.battle_scale import" not in src
            assert "from backend.game_logic import battle_scale" in src

    def test_the_floor_count_went_down_not_up(self):
        """⚠ FLIPPED CONSCIOUSLY from slice 16c's
        `test_no_third_casualty_floor_was_minted`, which asserted the string
        `MIN_CASUALTIES = 1000` was absent from `battle_report`. That pin
        would now pass VACUOUSLY — the constant lives in a third module and
        is spelled differently — so it is replaced by a census of the actual
        outcome: WO-16's 500 is untouched and untuned, and there is exactly
        ONE absolute 1,000 in the tree where there were two."""
        assert dispatch.OWN_MAULED_MIN_CASUALTIES == 500
        assert battle_scale.MIN_BATTLE_CASUALTIES == 1000
        # the narrator does not carry a floor of its own
        br_src = _code(inspect.getsource(battle_report))
        assert not re.search(r"MIN_[A-Z_]*CASUALTIES\s*=", br_src)
        # nor does the rules module
        dp_src = _code(inspect.getsource(diplomacy))
        assert not re.search(r"MIN_[A-Z_]*CASUALTIES\s*=", dp_src)

    def test_the_home_is_neutral(self):
        """It lives in neither reader because neither imports the other — a
        module-level edge from the display module to the 9.5k-line rules
        module would be the first cycle of its kind."""
        src = _code(pathlib.Path(
            "backend/game_logic/battle_scale.py").read_text(encoding="utf-8"))
        assert "import diplomacy" not in src
        assert "import battle_report" not in src

    def test_the_fourth_answer_is_named_on_the_record(self):
        """⚠ A `MIN_CASUALTIES` grep cannot find
        `_pick_bombardment_observation`'s 3% FRACTION — the fourth answer to
        the same question, in the same file as the third. The next reader
        must not conclude there were only two."""
        doc = battle_scale.__doc__ or ""
        assert "_pick_bombardment_observation" in doc
        assert "3%" in doc or "FRACTION" in doc
        # and it is still there, unchanged — this build does not touch it
        bomb = _code(inspect.getsource(
            battle_report._pick_bombardment_observation))
        assert "0.03" in bomb


# ═══════════════════════════════════════════════════════════════════════════
# The gate is per-arm. Every mechanical STATE survives it.
# ═══════════════════════════════════════════════════════════════════════════

class TestAStateClaimSurvivesTheGate:
    """⚠ These are the reason the positional shape was rejected. Measured:
    a `we_lost and total < FLOOR` return at priority 3.5 short-circuits all
    of them, and the full suite goes 20,943 passed / 1 FAILED."""

    def test_a_rout_below_the_floor_still_says_so(self):
        """PT-D4 landed this arm five slices ago and said in the code why. A
        corps that broke did not have 'no battle to speak of'."""
        got = _lines(_battle(1, 58, forced_retreat=True))
        assert got
        assert all(re.search(r"driven from the field|corps broke|line gave way",
                             ln) for ln in got), got

    def test_the_cavalry_pin_geometry_is_untouched(self):
        """The exact shape that reds under the positional build: total 350,
        France defending, enemy cavalry over our guns."""
        b = _battle(50, 300, def_original=3000)
        b["cavalry_counter_message"] = "Cavalry overran artillery!"
        got = _lines(b)
        assert any(re.search(
            r"cavalry|swept|horsemen|overran|defenseless|gun line", ln)
            for ln in got), got

    def test_a_destroyed_fort_is_reported_at_any_scale(self):
        b = _battle(1, 58, def_original=5000, outcome="attacker_victory")
        b["fort_destroyed"] = True
        got = _lines(b)
        assert got  # whatever arm answers, it is not silenced into default
        assert not any("Nothing unusual to report" in ln for ln in got), got


# ═══════════════════════════════════════════════════════════════════════════
# The five gated arms, named individually
# ═══════════════════════════════════════════════════════════════════════════

class TestTheFiveGravityArms:

    @pytest.mark.parametrize("arm", [
        "lost_terrain_disadvantage", "lost_despite_terrain",
        "won_heavy_casualties", "lost_narrow_no_drill", "lost_costly",
    ])
    def test_each_gated_arm_carries_the_predicate(self, arm):
        """A census — WITH behavioural siblings above and below it, because a
        census alone cannot tell you the predicate is reachable."""
        assert _arm_is_gated(arm), f"{arm} is ungated"

    def test_the_costly_victory_is_gated_too(self):
        """⚠ Rider (i). 9 of 9 archived `won_heavy_casualties` lines are
        sub-floor, median 292. Leaving the win side ungated re-creates FA-44
        facing the other way, so it is gated — stated here rather than left
        to be rediscovered."""
        got = _lines(_battle(58, 1, def_original=20000, atk_original=100,
                             outcome="defender_victory"), nation="Austria")
        assert not any("costly" in ln.lower() or "dearly" in ln.lower()
                       for ln in got), got

    @pytest.mark.parametrize("arm", ["routed", "cavalry_overran_artillery",
                                     "artillery_caught_moving",
                                     "overwatch_repelled",
                                     "lost_fort_overrun"])
    def test_each_state_arm_is_deliberately_ungated(self, arm):
        assert not _arm_is_gated(arm), (
            f"{arm} reports a mechanical state and must fire at any scale")

    def test_the_census_can_tell_the_two_apart(self):
        """Sensitivity arm. Without it the pair above passes on any census
        that always answers the same way."""
        assert _arm_is_gated("lost_costly")
        assert not _arm_is_gated("routed")
        assert not _arm_is_gated("stalemate")


# ═══════════════════════════════════════════════════════════════════════════
# The copy
# ═══════════════════════════════════════════════════════════════════════════

class TestTheCopy:

    def test_it_speaks_to_scale_and_never_to_consequence(self):
        """A 58-man remnant may well have been annihilated. The line must
        stay true if it was — so it may not claim the corps is intact, or
        that losses were light, or that anyone got away."""
        for line in battle_report._OBSERVATIONS["skirmish"]:
            low = line.lower()
            assert "intact" not in low
            assert "light" not in low
            assert "escaped" not in low and "withdrew" not in low

    def test_it_interpolates_nothing_outside_the_whitelist(self):
        """⚠ `_fill` substitutes marshal/enemy/ally/failed_ally/relationship/
        coordination_bonus/arrival_score/artillery/failed_was. A `{n}` — which
        the row's own prescribed copy uses — renders the braces on screen."""
        allowed = {"marshal", "enemy", "ally", "failed_ally", "relationship",
                   "coordination_bonus", "arrival_score", "artillery",
                   "failed_was"}
        for line in battle_report._OBSERVATIONS["skirmish"]:
            for token in re.findall(r"\{(\w+)\}", line):
                assert token in allowed, token
        # …and drive it, because a whitelist test passes on a bank nobody
        # renders.
        for rendered in _lines(_battle(1, 58, def_terrain=20)):
            assert "{" not in rendered and "}" not in rendered

    def test_the_default_did_not_become_the_loss_verdict(self):
        """The free option — no bank at all, fall through to 'A standard
        affair' — was measured (239 archived lines would collapse into it)
        and DECLINED. This pin is the record of that choice."""
        assert "skirmish" in battle_report._OBSERVATIONS
        assert len(battle_report._OBSERVATIONS["skirmish"]) >= 3
        for line in _lines(_battle(1, 58, def_terrain=20)):
            assert "standard affair" not in line


# ═══════════════════════════════════════════════════════════════════════════
# The stated limits
# ═══════════════════════════════════════════════════════════════════════════

class TestWhatTheGateDoesNotCover:

    def test_the_coordination_family_is_out_of_scope_and_says_so(self):
        """⚠ Seventy archived sub-floor lines are coordination-family lines
        sited ABOVE every candidate gate — including "even together, the
        field could not be held" at a total of ONE. A record that claims the
        gate covers the sub-floor population is wrong by a fifth."""
        doc = battle_scale.__doc__ or ""
        assert "coordination" in doc.lower()
        src = _code(inspect.getsource(battle_report._pick_observation))
        # they are genuinely above the terminal arm, not merely claimed to be
        assert src.index("coordination_hostile_forced") < src.index("skirmish")

    def test_the_third_party_limit_is_stated(self):
        """`we_lost` is computed against `player_nation`, so France 'loses'
        a third-party battle whenever the attacker wins. Pre-existing — but
        the record may not claim universal coverage."""
        doc = battle_scale.__doc__ or ""
        assert "player_nation" in doc
        assert "third-party" in doc or "third party" in doc

    def test_wo16s_dissent_is_untouched(self):
        """This build does not tune 500 and does not reuse it. Reading a
        one-sided constant against a two-sided total would give it two
        referents a factor of two apart."""
        assert dispatch.OWN_MAULED_MIN_CASUALTIES == 500
        src = _code(inspect.getsource(battle_report._pick_observation))
        assert "OWN_MAULED_MIN_CASUALTIES" not in src
        doc = battle_scale.__doc__ or ""
        assert "dissent" in doc.lower()


# ═══════════════════════════════════════════════════════════════════════════
# The ruling is on the record
# ═══════════════════════════════════════════════════════════════════════════

class TestTheRulingIsRecorded:

    def test_the_gate_block_records_the_decision(self):
        gate = (REPO / "docs" / "DESIGN_REFINEMENT.md").read_text(
            encoding="utf-8")
        block = gate[gate.index("### FA-S16-D3"):]
        block = block[:block.index("### FA-S16-D4")]
        assert "RULED" in block
        assert "BUG_FIXES.md" in block, "the ruling must name its landing record"

    def test_the_row_is_closed_and_names_what_shipped(self):
        rows = (REPO / "docs" / "BUG_FIXES.md").read_text(encoding="utf-8")
        line = [ln for ln in rows.split("\n")
                if re.match(r"^(> )?\| \*\*FA-44\*\* \|", ln)]
        assert line, "FA-44's row has gone missing"
        assert "NOT BUILT" not in line[0]
        assert "FA-S16-D3" in line[0]
