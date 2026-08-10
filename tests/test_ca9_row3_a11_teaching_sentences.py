"""CA9 row 3 / A11 — the sentences that teach the grievance system.

Audit record: `docs/audits/GRIEVANCE_REVISIT_INVESTIGATION_2026_08_09.md`,
item A11. The audit's finding was blunt: there is **no primer anywhere**,
and the one sentence in the product that states the causal rule is wrong
twice.

Four surfaces:

1. The ladder caption said *"glory, last 5 turns"* against a live
   `GLORY_WINDOW = 8` — stale since DR-2 lengthened it — and described
   envy as fixing on "the man below", when `JEALOUSY_RIVAL_MEMORY` makes
   it fix on a REMEMBERED rival. The number is now served by the backend
   and interpolated, so it cannot drift again.
2. *"reward them before they ask"* was false in both halves:
   `_threshold_for` reads relationship / idle / authority and has **no**
   satisfaction, expectation, estate or pension term, and the chip is
   gated shut until he has asked. Conscious flip of the R159 pin.
3. The marshal card printed "Ney: Professional" two lines under its own
   "GRIEVANCE: envious of Ney", because it iterated the RAW stored dict
   while every mechanical seam reads the derived getter.
4. `help` never used the words glory, jealousy, grievance, ladder or
   petition — while teaching the sibling ES-7 reward loop in ~24 lines.
   Its load-bearing sentence is that **gold cannot touch jealousy**.
"""

import io
import tokenize
from pathlib import Path

import pytest

from backend.commands.meta_executor import MetaExecutor
from backend.game_logic import jealousy as J
from backend.game_logic.marshal_overview import _build_relationships

from tests.conftest import MarshalFactory, WorldFactory

REPO = Path(__file__).resolve().parents[1]
GD = REPO / "godot-client" / "project-sovereign" / "scripts"


def _help_text() -> str:
    """The help body ONLY.

    `test_naval_ui_clarity.py:208` greps the whole of `meta_executor.py`,
    which a docstring or a comment can satisfy — the precedent is real but
    the assertion is loose. This slices the literal the player actually
    reads, so every pin below is binding on the product.
    """
    world = WorldFactory.basic()
    result = MetaExecutor(None)._execute_help({}, world)
    return result["message"]


def _strip_comments(src: str) -> str:
    out = []
    for tok in tokenize.generate_tokens(io.StringIO(src).readline):
        if tok.type != tokenize.COMMENT:
            out.append(tok.string)
    return "\n".join(out)


# ════════════════════════════════════════════════════════════════════════
# 1. The ladder caption
# ════════════════════════════════════════════════════════════════════════

class TestTheLadderCaptionStatesTheRealRule:
    def test_the_window_is_served_not_hardcoded(self):
        from fastapi.testclient import TestClient

        import backend.main as main_module
        client = TestClient(main_module.app)
        payload = client.get("/marshal_overview").json()
        assert payload["glory_window"] == J.GLORY_WINDOW

    def test_the_client_interpolates_it(self):
        src = (GD / "marshal_management.gd").read_text(encoding="utf-8")
        assert "cached_glory_window" in src
        assert 'response.get("glory_window"' in src
        assert "str(cached_glory_window)" in src

    def test_the_stale_number_is_gone(self):
        """The specific defect: a caption three turns adrift of the
        engine. No literal turn-count may sit in that sentence again."""
        src = (GD / "marshal_management.gd").read_text(encoding="utf-8")
        assert "glory, last 5 turns" not in src
        assert "last 8 turns" not in src, (
            "the window must be interpolated, not re-hardcoded at the "
            "value it happens to have today")

    def test_the_rival_memory_rule_is_stated(self):
        """Envy re-fixes on a REMEMBERED man, not on whoever stands one
        rung up this turn (`JEALOUSY_RIVAL_MEMORY`)."""
        src = (GD / "marshal_management.gd").read_text(encoding="utf-8")
        assert "keeps that rival while he stays above" in src
        assert "the man below" not in src

    def test_rival_memory_is_actually_on(self):
        """The caption is only true while the flag is. If this ever
        flips, the sentence must change with it."""
        assert J.JEALOUSY_RIVAL_MEMORY is True


# ════════════════════════════════════════════════════════════════════════
# 2. "reward them before they ask"
# ════════════════════════════════════════════════════════════════════════

class TestTheScreenNoLongerPointsAtGold:
    def test_the_false_sentence_is_gone(self):
        src = (GD / "marshal_management.gd").read_text(encoding="utf-8")
        assert "reward them before they ask" not in src, (
            "including in a comment — the R159 pin is a source grep, so a "
            "comment quoting the old line silently satisfies it")

    def test_the_replacement_names_the_real_division(self):
        src = (GD / "marshal_management.gd").read_text(encoding="utf-8")
        assert "only glory answers envy" in src

    def test_the_threshold_really_has_no_reward_term(self):
        """The claim the old sentence made, falsified at the source.

        Mutation-resistant: reads `_threshold_for` itself rather than
        asserting a doc sentence about it."""
        import inspect
        src = _strip_comments(inspect.getsource(J._threshold_for))
        for forbidden in ("expectation", "satisfaction", "dotation",
                          "pension", "estate", "trust"):
            assert forbidden not in src, (
                f"_threshold_for now reads {forbidden!r} — the help text "
                f"and the screen caption both claim gold cannot touch a "
                f"grievance, and would become lies")

    def test_rewarding_a_jealous_marshal_does_not_move_his_threshold(self):
        """The behavioural half. A rente and an estate change nothing
        about the grievance clock."""
        ney = MarshalFactory.infantry(name="Ney", location="Paris",
                                      personality="aggressive")
        murat = MarshalFactory.infantry(name="Murat", location="Paris",
                                        personality="aggressive")
        world = WorldFactory.with_marshals([ney, murat])
        before = J._threshold_for(world.marshals["Murat"],
                                  world.marshals["Ney"], authority=50)
        world.marshals["Murat"].pension = 500
        world.marshals["Murat"].dotation_regions = ["Swabia"]
        after = J._threshold_for(world.marshals["Murat"],
                                 world.marshals["Ney"], authority=50)
        assert before == after


# ════════════════════════════════════════════════════════════════════════
# 3. The card stops contradicting the engine on its own screen
# ════════════════════════════════════════════════════════════════════════

class TestTheCardReadsTheDerivedRelationship:
    @pytest.fixture()
    def pair(self):
        murat = MarshalFactory.infantry(name="Murat", location="Paris",
                                        personality="aggressive")
        ney = MarshalFactory.infantry(name="Ney", location="Paris",
                                      personality="aggressive")
        world = WorldFactory.with_marshals([murat, ney])
        world.marshals["Murat"].relationships["Ney"] = 0
        return world

    def test_a_live_grievance_shows_on_the_relationship_row(self, pair):
        world = pair
        murat = world.marshals["Murat"]
        rows = {r["name"]: r for r in _build_relationships(murat, world)}
        assert rows["Ney"]["value"] == 0
        assert rows["Ney"]["label"] == "Professional"

        murat.jealous_of = "Ney"
        rows = {r["name"]: r for r in _build_relationships(murat, world)}
        assert rows["Ney"]["value"] == -1, (
            "the card printed 'Professional' two lines under its own "
            "'GRIEVANCE: envious of Ney'")
        assert rows["Ney"]["label"] == "Rival"

    def test_the_card_agrees_with_the_mechanical_seam(self, pair):
        """The point of the fix: one number, read through the chokepoint
        every mechanic already reads."""
        world = pair
        murat = world.marshals["Murat"]
        murat.jealous_of = "Ney"
        rows = {r["name"]: r for r in _build_relationships(murat, world)}
        assert rows["Ney"]["value"] == murat.get_relationship("Ney")

    def test_the_hostile_floor_is_not_breached(self, pair):
        """A stored -2 stays -2 — the derived penalty is guarded on
        `value > -2`, so the card cannot invent a -3 label."""
        world = pair
        murat = world.marshals["Murat"]
        murat.relationships["Ney"] = -2
        murat.jealous_of = "Ney"
        rows = {r["name"]: r for r in _build_relationships(murat, world)}
        assert rows["Ney"]["value"] == -2
        assert rows["Ney"]["label"] == "Hostile"


# ════════════════════════════════════════════════════════════════════════
# 4. help teaches the system — and names what gold cannot do
# ════════════════════════════════════════════════════════════════════════

class TestHelpTeachesTheLadder:
    def test_the_vocabulary_exists_at_all(self):
        text = _help_text().lower()
        for word in ("glory", "grievance", "envy", "rival", "ladder"):
            assert word in text, f"help never says {word!r}"

    def test_the_load_bearing_sentence(self):
        """The audit measured players being pointed at gold for a problem
        gold cannot touch. This is the sentence that stops it."""
        text = _help_text()
        assert "ESTATES AND RENTES CANNOT TOUCH THIS" in text
        assert "only glory answers his envy" in text

    def test_the_window_agrees_with_the_constant(self):
        text = _help_text()
        assert f"last {J.GLORY_WINDOW} turns" in text

    def test_the_solo_bonus_is_stated_as_the_code_computes_it(self):
        """`combat_executor` stamps the +15% when
        `len(atk_participants) <= 1` — a count of a list that has already
        had derived-hostile marshals dropped. "with no marshal of yours
        counted on the field beside him" is that condition in English;
        "alone" alone would be wrong."""
        text = _help_text()
        assert "+15%" in text
        assert "no marshal of yours" in text and "counted on the field" in text

    def test_the_bonus_number_matches_the_constant(self):
        from backend.models.marshal import Marshal
        pct = int(round(Marshal.JEALOUSY_SOLO_ATTACK_BONUS * 100))
        assert f"+{pct}%" in _help_text()

    def test_all_three_resolution_predicates_are_named(self):
        text = _help_text()
        assert "shoulder to shoulder" in text      # cautious
        assert "meaningful contact" in text        # literal
        assert "a real foe" in text                # aggressive

    def test_the_defeat_and_out_bled_halves_are_included(self):
        text = _help_text()
        assert "outnumbered" in text and "no shame" in text
        assert "2-to-1" in text and "undecided" in text

    def test_the_cost_of_a_grievance_is_named(self):
        """The audit's headline invisible consequence: committed strength
        24,840 -> 0, win rate 7/8 -> 1/8, stated on no surface anywhere."""
        text = _help_text()
        assert "will not coordinate" in text
        assert "muster preview" in text
