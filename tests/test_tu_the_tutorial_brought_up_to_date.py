"""Row TU — the tutorial brought up to date (the user's word of November 23, 2026:
"update tutorial so it reflects all updates we made").

The design is `docs/TUTORIAL_UPDATE_SPEC.md`; the row is `docs/PRE_DEPLOY_PLAN.md`
§2 row TU, after row FR's two sessions and before Session H. Golden rule 9 asks a
behaviour test of work left for a later session: these strict xfails read the
stale lines the design names (§2) and the first-hour surfaces Help & Keys lacks
(§3, §5). Each one turns red the day row TU fixes its line — drop its xfail in
that commit. The lessons' real behaviour tests (both lessons played in the real
client at both setups, every card passed by doing its thing) land with row TU.
"""

import pathlib
import re

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "godot-client" / "project-sovereign" / "scripts"
OVERLAY = SCRIPTS / "tutorial_overlay.gd"
CODEX = SCRIPTS / "codex_terms.gd"
SCRIPT_DOC = REPO / "docs" / "TUTORIAL_SCRIPT.md"

_OPEN_TU = ("row TU (docs/TUTORIAL_UPDATE_SPEC.md) — the tutorial brought up to date; "
            "owner row TU, after row FR's Sessions FR-1 and FR-2")


def _card(card_id: str) -> str:
    """One School card's block of `tutorial_overlay.gd` STEPS, by its id."""
    src = OVERLAY.read_text(encoding="utf-8")
    i = src.index("const STEPS")
    j = src.index("\n]", i)
    for block in src[i:j].split("\n\t{")[1:]:
        found = re.search(r'"id":\s*"([a-z_]+)"', block)
        if found and found.group(1) == card_id:
            return block
    raise AssertionError(f"no card {card_id!r} in the School's STEPS")


def _help_titles() -> list:
    """The titles of Help & Keys' TERMS entries, lower-cased."""
    src = CODEX.read_text(encoding="utf-8")
    i = src.index("const TERMS")
    j = src.index("\n]", i)
    return [t.lower() for t in re.findall(r'^\t\["([^"]+)",', src[i:j], flags=re.M)]


class TestTheRowsOwnStartingState:
    """Not xfails: they hold the row's reading of today true, so a strict xfail
    below can only flip for the reason it names."""

    def test_the_cards_the_design_names_stand(self):
        for card_id in ("survey", "objection_answer", "on_his_own", "ask_him"):
            assert '"body":' in _card(card_id)

    def test_help_has_its_terms_table(self):
        assert len(_help_titles()) >= 60


class TestTULessonsTeachTheGameAsItIs:

    @pytest.mark.xfail(strict=True, reason=_OPEN_TU)
    def test_card_one_no_longer_says_every_command_is_typed(self):
        """§2.1: every simple order is a button since row IC's Session 2;
        typing is for tasks, exact orders and questions."""
        assert "Every command is TYPED" not in _card("survey")

    @pytest.mark.xfail(strict=True, reason=_OPEN_TU)
    def test_card_five_names_the_task_to_prove_himself(self):
        """§2.2: the hearing's answer is the task to prove himself (trial.py)."""
        assert "prove himself" in _card("objection_answer")

    @pytest.mark.xfail(strict=True, reason=_OPEN_TU)
    @pytest.mark.parametrize("card_id", ["on_his_own", "ask_him"])
    def test_on_his_own_and_ask_him_pass_only_by_doing_what_they_teach(self, card_id):
        """§2.4: XIX and XX pass on any successful reply today; each passes only
        when a task, or a question, was sent."""
        assert '"advance": "_pred_any_success"' not in _card(card_id)

    @pytest.mark.xfail(strict=True, reason=_OPEN_TU)
    @pytest.mark.parametrize("words", ["on his own", "desk", "end turn", "read-back"])
    def test_help_and_keys_names_the_first_hours_new_surfaces(self, words):
        """§5: Help & Keys gains an entry for each (titles read case-blind)."""
        assert any(words in title or words.replace("-", " ") in title for title in _help_titles())

    @pytest.mark.xfail(strict=True, reason=_OPEN_TU)
    def test_help_and_keys_says_a_battles_bonuses_multiply(self):
        """§3, §5 (row FR, Session FR-2's blind reading: every reader right in
        meaning, but two answers still guessed why a defence cut from +81% to
        +75% reads -3%): Help & Keys says that a battle's bonuses multiply and
        that a defence is limited to +75%."""
        src = CODEX.read_text(encoding="utf-8")
        i = src.index("const TERMS")
        j = src.index("\n]", i)
        assert any("multipl" in line.lower() and "+75" in line for line in src[i:j].splitlines())

    @pytest.mark.xfail(strict=True, reason=_OPEN_TU)
    def test_the_script_is_rewritten_from_the_code(self):
        """§2.8: `docs/TUTORIAL_SCRIPT.md` says "Eighteen cards" and "AP"."""
        text = SCRIPT_DOC.read_text(encoding="utf-8")
        assert "Eighteen cards" not in text
        assert not re.search(r"\bAP\b", text)
