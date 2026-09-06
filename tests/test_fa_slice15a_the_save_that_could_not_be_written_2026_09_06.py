"""FA slice 15 (part a) — "THE SAVE THAT COULD NOT BE WRITTEN".

**FA-S15-1 (P1)**, found while measuring slice 15, plus the two rows about
tests that cannot fail: **FA-91** (the serialization gate is blind to the
field classes that have actually bitten) and **FA-N34** (the client gate's
pins assert words in a source file).

Landing record: the boxed SLICE 15 (part a) block in `docs/BUG_FIXES.md`
§Final Whole-Game Audit.
"""

import ast
import contextlib
import io
import pathlib

from backend import save_manager
from backend.game_logic.vassal import release_vassal
from backend.models.world_state import WorldState

REPO = pathlib.Path(__file__).resolve().parents[1]
EUROPE = str(REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
             / "europe_1805.json")


def _boot():
    with contextlib.redirect_stdout(io.StringIO()):
        return WorldState.from_scenario(EUROPE)


def _assimilated_world():
    """A satellite with an assimilated contingent — a corps that flies the
    LORD's flag and remembers whose it was. That is the ONLY state in which
    the defect fires, which is why a probe on the bare boot board misses it:
    no French vassal has an assimilated corps at turn 1.
    """
    world = _boot()
    corps = world.get_marshal("Soult")
    corps.original_nation = "Holland"
    return world, corps


class TestReleasingAVassalDoesNotBreakEverySaveForever:
    """FA-S15-1. `release_vassal` did `delattr(marshal, 'original_nation')`
    while `Marshal.to_dict` reads `self.original_nation` BARE.

    It is IGR-X1's pattern exactly (`del marshal._recovery_destination`), and
    the two sibling restore loops in the same file already wrote `= None`.
    One site was missed, and nothing could see it: the serialization gate
    reads the object as CONSTRUCTED, so a field that is declared, serialized
    and then deleted at runtime is invisible to it.
    """

    def test_the_marshal_still_serializes(self):
        world, corps = _assimilated_world()
        with contextlib.redirect_stdout(io.StringIO()):
            assert release_vassal(world, "Holland")["success"] is True
        assert corps.nation == "Holland"
        assert corps.to_dict()["original_nation"] is None

    def test_the_world_still_serializes(self):
        world, _ = _assimilated_world()
        with contextlib.redirect_stdout(io.StringIO()):
            release_vassal(world, "Holland")
        assert world.to_dict()["marshals"]["Soult"]["original_nation"] is None

    def test_the_save_actually_writes(self, tmp_path, monkeypatch):
        """The player-visible half. `save_game` swallows the AttributeError
        into `success: False` with the message in a field nobody reads, so
        the campaign simply stops being saveable and never says so."""
        monkeypatch.setenv("INK_IRON_SAVE_DIR", str(tmp_path))
        world, _ = _assimilated_world()
        with contextlib.redirect_stdout(io.StringIO()):
            release_vassal(world, "Holland")
            saved = save_manager.save_game(world, "fa_s15_1", tmp_path / "s.json")
            auto = save_manager.autosave(world)
        assert saved["success"] is True, saved["message"]
        assert auto["success"] is True, auto["message"]

    def test_the_round_trip_survives(self):
        world, _ = _assimilated_world()
        with contextlib.redirect_stdout(io.StringIO()):
            release_vassal(world, "Holland")
            restored = WorldState.from_dict(world.to_dict())
        assert restored.get_marshal("Soult").nation == "Holland"
        assert restored.get_marshal("Soult").original_nation is None

    def test_the_field_is_cleared_not_deleted(self):
        """The intent of the original code is kept — a released marshal is
        nobody's client any more — but expressed the way every other restore
        loop in `vassal.py` expresses it."""
        source = (REPO / "backend" / "game_logic" / "vassal.py").read_text(
            encoding="utf-8")
        code = "\n".join(ln for ln in source.split("\n")
                         if not ln.strip().startswith("#"))
        assert "delattr(marshal, 'original_nation')" not in code
        assert "marshal.original_nation = None" in code


class TestTheGateCanNowSeeADeletedField:
    """FA-91. The rule "if it exists on the object, it must serialize" reads
    the object as constructed and is structurally blind to a field that is
    deleted at runtime. The new AST census closes that class."""

    @staticmethod
    def _census():
        from tests.test_serialization_enforcement import (
            TestASerializedFieldIsNeverDeleted as T)
        return T

    def test_the_census_is_green_at_head(self):
        self._census()().test_no_serialized_field_is_deleted_anywhere_in_the_backend()

    def test_the_census_would_have_caught_the_p1(self):
        """⚠ The pin that matters. Re-introduce the exact shape in a scratch
        AST and the census must name it."""
        T = self._census()()
        deleted = dict(T._deleted_attribute_names())
        deleted["original_nation"] = ["vassal.py:2154"]
        from backend.models.marshal import Marshal
        reads = T._bare_self_reads_in_to_dict(Marshal)
        assert "original_nation" in reads
        assert set(deleted) & reads, (
            "the census cannot see the shape it exists for")

    def test_the_census_reads_real_deletions(self):
        """Sensitivity: an AST walk that finds nothing is green about
        nothing."""
        found = self._census()()._deleted_attribute_names()
        assert found
        assert "relationship_with_lord" in found

    def test_getattr_is_the_exempt_idiom(self):
        """A field that MAY be deleted must be read defensively, and the
        census must not punish the safe form.

        ⚠ It calls the PRODUCTION helper. The first cut re-implemented the
        walk inline and so executed no census code at all — a pin that could
        not have noticed if the exemption were removed. Measured by the
        slice-15 review round: patching the real helper to raise left it
        green.
        """
        T = self._census()

        class _Safe:
            def to_dict(self):
                return {"a": getattr(self, "a", None)}

        class _Unsafe:
            def to_dict(self):
                return {"a": self.a}

        assert T._bare_self_reads_in_to_dict(_Safe) == set()
        # …and the same helper DOES see the bare form, so the empty set above
        # is the exemption working and not the walk finding nothing.
        assert T._bare_self_reads_in_to_dict(_Unsafe) == {"a"}


class TestTheClientGatePinsCannotBeSatisfiedByProse:
    """FA-N34. Three pins asserted that keywords do (or do not) appear in a
    GDScript function body. None could fail for the right reason, and one
    failed for the wrong one — it reddened on a COMMENT, and production
    source had been bent around it."""

    @staticmethod
    def _gate_body():
        src = (REPO / "godot-client" / "project-sovereign" / "scripts"
               / "main.gd").read_text(encoding="utf-8")
        body = src[src.index("func _is_end_turn_phrasing("):]
        return body[:body.index("func _execute_end_turn():")]

    def test_the_vacuous_pins_are_gone(self):
        review = (REPO / "tests" / "test_review_2026_08_30.py").read_text(
            encoding="utf-8")
        for dead in ("def test_the_client_speaks_the_parsers_vocabulary",
                     "def test_the_helper_claims_every_phrasing_the_parser_accepts",
                     "def test_an_ordinary_command_is_not_swallowed"):
            assert dead not in review, dead

    def test_the_binding_pin_is_the_one_that_survives(self):
        """It EVALUATES both gates against a fixture list instead of grepping
        for words, and its negatives are the real question."""
        from tests.test_fa_slice1_the_two_words_2026_09_02 import (
            TestTheClientGateSpeaksTheSameVocabulary as T)
        fixtures = dict(T.FIXTURES)
        assert fixtures["Davout, fortify until next turn"] is False
        assert fixtures["Ney, attack Mack next turn"] is False
        assert fixtures["end turn"] is True
        for command, expected in T.FIXTURES:
            assert T._client_gate(command) is expected, command

    def test_production_prose_is_free_again(self):
        """The gate's comment had to avoid naming an order verb because a
        Python pin grepped for one. That constraint is retired, and this
        asserts the retirement is real rather than merely intended."""
        # ⚠ It must NOT assert the comment SAYS "attack". The first cut did,
        # and that re-created FA-N34's own defect inverted — a Python pin
        # binding a GDScript comment's wording, so an editor tidying the
        # comment reds a test about parsing. What is asserted instead is what
        # the retirement MEANS: the verb may appear anywhere in the body
        # without changing the gate's answer.
        from tests.test_fa_slice1_the_two_words_2026_09_02 import (
            TestTheClientGateSpeaksTheSameVocabulary as T)
        assert T._client_gate("Ney, attack Mack next turn") is False
        assert T._client_gate("end turn") is True
        body = self._gate_body()
        commented = body + "\n# attack recruit fortify\n"
        assert self._needles(body) == self._needles(commented), (
            "a comment changed the gate's needles — the trap is back")

    @staticmethod
    def _needles(body):
        """The literals the gate actually compares against, comments stripped
        — the same shape slice 1's evaluator derives."""
        import re
        code = "\n".join(line for line in body.split("\n")
                         if not line.strip().startswith("#"))
        return sorted(set(re.findall(r'"([^"]+)"', code)))
