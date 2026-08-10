"""CA9 row 3 / A14 — the petition modal renders the marshal.

Audit record: `docs/audits/GRIEVANCE_REVISIT_INVESTIGATION_2026_08_09.md`,
item A14 (Phase B).

The backend has set a `speaker` on every petition since v3.2 and **zero
`.gd` files ever read it**, so the flagship drama card arrived as an
unsigned staff memo. The audit's own observation is the design brief:
`war_weary` is the only petition that reads as drama, and the reason is
one clause — *"I have my duchy, Sire. Why do we march again?"* The man
speaks.

Authored in `jealousy.py`, NOT `marshal_voice.py`, whose banks are keyed
to five BATTLE situations with no consumer joining them to a petition.

Two things the memo explicitly ruled OUT and this slice does not do:
duplicate a stat block onto the card (the Generals screen owns the
character sheet — the lookup is unblocked instead), and add a portrait
(a separate layout slice: `portrait_locket.gd` is a shader-bearing
diorama Control, the card is a BBCode emitter).
"""

from pathlib import Path

import pytest

from backend.game_logic import jealousy as J

from tests.conftest import MarshalFactory, WorldFactory

REPO = Path(__file__).resolve().parents[1]
GD = REPO / "godot-client" / "project-sovereign" / "scripts"


@pytest.fixture()
def pair():
    ney = MarshalFactory.infantry(name="Ney", location="Paris",
                                  strength=30000, personality="aggressive")
    murat = MarshalFactory.infantry(name="Murat", location="Paris",
                                    strength=30000, personality="aggressive")
    world = WorldFactory.with_marshals([ney, murat], current_turn=4)
    return world, world.marshals["Ney"], world.marshals["Murat"]


class TestTheMarshalSpeaks:
    def test_the_confrontation_carries_his_words(self, pair):
        world, ney, murat = pair
        J.queue_confrontation_petition(world, ney, murat, 0)
        petition = world.pending_marshal_petition
        assert petition["speaker"] == "Ney"
        assert petition["speaker_line"].startswith('"')
        assert "Sire" in petition["speaker_line"]

    def test_he_names_the_man_he_resents(self, pair):
        world, ney, murat = pair
        ney.jealousy_history["Murat"] = [1]
        J.queue_confrontation_petition(world, ney, murat, 0)
        assert "Murat" in world.pending_marshal_petition["speaker_line"]

    def test_each_personality_has_its_own_voice(self, pair):
        world, ney, murat = pair
        lines = set()
        for personality in ("aggressive", "cautious", "literal"):
            ney.personality = personality
            lines.add(J.petition_speaker_line(ney, "Murat"))
        assert len(lines) == 3

    def test_a_second_audience_does_not_repeat_the_first(self, pair):
        """Indexed by the pair's lifetime fires, so the same man asking
        twice does not say the same words twice."""
        world, ney, _ = pair
        ney.jealousy_history["Murat"] = [1]
        first = J.petition_speaker_line(ney, "Murat")
        ney.jealousy_history["Murat"] = [1, 2]
        second = J.petition_speaker_line(ney, "Murat")
        assert first != second

    def test_it_is_deterministic(self, pair):
        """GR6: display only, no RNG — the same state says the same
        words, so a save/load or a re-render cannot change his mind."""
        world, ney, _ = pair
        ney.jealousy_history["Murat"] = [1, 2]
        assert J.petition_speaker_line(ney, "Murat") == \
            J.petition_speaker_line(ney, "Murat")

    def test_the_bank_does_not_run_off_the_end(self, pair):
        """A long feud must not IndexError on the tenth fire."""
        world, ney, _ = pair
        ney.jealousy_history["Murat"] = list(range(12))
        assert J.petition_speaker_line(ney, "Murat")

    def test_an_unknown_personality_is_silent_not_broken(self, pair):
        world, ney, _ = pair
        ney.personality = "balanced"      # a retired type (MC-4)
        assert J.petition_speaker_line(ney, "Murat") == ""

    def test_war_weary_keeps_the_line_that_made_it_work(self, pair):
        """It was ALREADY the only petition that read as drama. The clause
        moved out of the staff prose into the field the modal speaks, so
        every kind works the same way rather than this one being
        accidentally good."""
        world, ney, _ = pair
        petition = J.queue_war_weary_petition(
            world, ney, "Austria", {"action": "declare_war"})
        assert petition["kind"] == "war_weary"
        assert "I have my duchy, Sire" in petition["speaker_line"]
        # ...and it is no longer buried in the staff prose, where the
        # modal could not speak it.
        assert "I have my duchy" not in petition["body"]

    def test_the_rivalry_petition_speaks_too(self, pair):
        world, ney, murat = pair
        J.queue_rivalry_petition(world, ney, murat, -1)
        petition = world.pending_marshal_petition
        assert petition["kind"] == "rivalry_confrontation"
        assert petition.get("speaker_line")


class TestTheClientRendersHim:
    def test_the_card_reads_the_speaker(self):
        src = (GD / "marshal_petition_dialog.gd").read_text(encoding="utf-8")
        assert 'petition.get("speaker"' in src
        assert 'petition.get("speaker_line"' in src

    def test_his_words_come_before_the_staffs_summary(self):
        src = (GD / "marshal_petition_dialog.gd").read_text(encoding="utf-8")
        assert src.index('petition.get("speaker_line"') < \
            src.index('petition.get("body"')

    def test_the_body_floor_was_raised_for_the_extra_lines(self):
        """The scene authors BodyLabel at a bounded 120px with
        `scroll_active`, so two extra lines would push his own words out
        of view. Still BOUNDED, or `Utils.clamp_centered_panel` cannot
        shrink the panel at high Interface Scale."""
        src = (GD / "marshal_petition_dialog.gd").read_text(encoding="utf-8")
        assert "custom_minimum_size.y = 170.0" in src
        assert "clamp_centered_panel" in src


class TestTheLookupIsUnblockedNotDuplicated:
    def test_G_works_while_the_petition_is_up(self):
        src = (GD / "main.gd").read_text(encoding="utf-8")
        assert "_petition_allows_lookup()" in src
        # ...on the KEY_G branch specifically.
        g = src.index("if event.keycode == KEY_G:")
        assert "_petition_allows_lookup()" in src[g:g + 1200]

    def test_it_is_scoped_to_the_petition_and_not_typing(self):
        src = (GD / "main.gd").read_text(encoding="utf-8")
        fn = src[src.index("func _petition_allows_lookup"):]
        fn = fn[:fn.index("\n\n\n")] if "\n\n\n" in fn else fn
        assert "command_input.has_focus()" in fn
        assert "marshal_petition_dialog" in fn
        assert "visible" in fn

    def test_other_hotkeys_stay_blocked(self):
        """Only the lookup is unblocked. The card stays modal."""
        src = (GD / "main.gd").read_text(encoding="utf-8")
        for key in ("KEY_T", "KEY_D", "KEY_L"):
            i = src.index(f"if event.keycode == {key}:")
            window = src[i:i + 400]
            assert "_petition_allows_lookup" not in window, key

    def test_no_stat_block_is_duplicated_onto_the_card(self):
        """The memo's explicit instruction: the Generals card owns the
        character sheet."""
        src = (GD / "marshal_petition_dialog.gd").read_text(encoding="utf-8")
        for token in ("skills", "trust", "rally_tier", "admin_tier",
                      "skill_notes"):
            assert token not in src, token
