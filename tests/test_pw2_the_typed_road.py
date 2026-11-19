"""Row PW "Plain Words", part 2 (November 18, 2026) — the typed road forgives a slipped key.

The first player's own tries at the province he could not take: "ney ttack vienna" and "tatck" were read
as nothing; "attack" on a mistyped Carniola asked for a FOE called "Carolina"; "end the war" answered
"which nation should I direct this proposal to?". And GRD-16 (ruled November 17, 2026): a marshal's name
one slip off is answered with the nearest of the player's OWN marshals.

Nothing here spends anything: a repaired verb is read back before it is sent (the line's readback), and
every ask is free.
"""

from __future__ import annotations

import pathlib
import re
from types import SimpleNamespace

import pytest

from backend.ai import llm_client as L
from backend.commands import proper_name as PN
from backend.models.world_state import WorldState

REPO = pathlib.Path(__file__).resolve().parents[1]


class TestAVerbWithASlippedKeyIsRead:
    def test_the_first_playtests_own_slips(self):
        assert L._verb_for_typo("ttack", set()) == "attack"      # the first letter dropped
        assert L._verb_for_typo("tatck", set()) == "attack"      # the closed table: two edits
        assert L._SHORT_TYPO_TABLE["tatck"] == "attack"

    def test_the_older_readings_stand(self):
        assert L._verb_for_typo("attak", set()) == "attack"      # one edit, the verb's own first letter
        assert L._verb_for_typo("mve", set()) == "move"          # the telegraph table
        assert L._verb_for_typo("atack", set()) == "attack"

    def test_a_slip_on_the_first_letter_needs_a_verb_of_five_letters(self):
        assert L._verb_for_typo("narch", set()) == "march"
        # a four-letter verb is too short to read a first-letter slip into
        for word in ("nove", "bold", "cold"):
            assert L._verb_for_typo(word, set()) is None, word

    def test_a_name_a_verb_and_a_real_word_are_never_read(self):
        assert L._verb_for_typo("attack", set()) is None, "a verb already"
        assert L._verb_for_typo("ttack", {"ttack"}) is None, "a roster, province or nation form"
        stop = next(iter(L._TYPO_STOPLIST))
        assert L._verb_for_typo(stop, set()) is None, "a stoplisted real word"
        assert L._verb_for_typo("xyzzy", set()) is None

    def test_a_real_word_one_first_letter_slip_from_a_verb_is_never_read(self):
        """The review (PW2-R6): every English word one edit ON the first letter from a verb of five letters
        or more — the letter dropped ("arch"), another in its place ("parch", "larch", "mortify", "lombard"),
        one set before it ("pretreat")."""
        for word in ("arch", "larch", "parch", "mortify", "lombard", "pretreat"):
            assert word in L._TYPO_STOPLIST, word
            assert L._verb_for_typo(word, set()) is None, word
        # the slips the rule was built for still read
        assert L._verb_for_typo("ttack", set()) == "attack" and L._verb_for_typo("narch", set()) == "march"
        assert L._verb_for_typo("etreat", set()) == "retreat"

    def test_both_arms_read_through_the_one_rule(self):
        src = (REPO / "backend" / "ai" / "llm_client.py").read_text(encoding="utf-8")
        body = src[src.index("def repair_leading_verb_typo("):src.index("def _askable_enemy_names(")]
        assert body.count("_verb_for_typo(") == 2, "the verb position and the verb after an unmarked address"


class TestANameOneSlipFromAProvinceIsAskedBack:
    def _world(self, *names):
        return SimpleNamespace(regions={name: object() for name in names})

    def test_the_letters_in_another_order(self):
        """The first playtest: "Carolina" for Carniola."""
        assert PN.near_province(self._world("Carniola", "Vienna", "Tyrol"), "Carolina") == "Carniola"

    def test_within_two_edits(self):
        world = self._world("Carniola", "Vienna", "Bohemia")
        assert PN.near_province(world, "Carnola") == "Carniola"
        assert PN.near_province(world, "Bohemai") == "Bohemia"

    def test_none_when_nothing_or_more_than_one_fits(self):
        assert PN.near_province(self._world("Carniola", "Vienna"), "Zorglub") is None
        assert PN.near_province(self._world("Carniola", "Carnioli"), "Carniolo") is None
        assert PN.near_province(self._world("Tyrol"), "Tirol") == "Tyrol"     # five letters is the floor
        assert PN.near_province(self._world("Ulm", "Lyon"), "Ulmm") is None, "names under five letters are not guessed"

    def test_the_ask_names_the_province_and_the_order_to_give_again(self):
        src = (REPO / "backend" / "commands" / "proper_name.py").read_text(encoding="utf-8")
        assert 'if not lead and verb == "attack" and _near_miss(world, name, viewer) is None:' in src, (
            "a near miss of a FOE in sight is offered first; and (the review, PW2-R7) only an ATTACK takes a "
            "province — a charge and a bombardment name a foe and keep their own ask")
        assert re.search(r'did you mean the "\s*\n\s*f"province of \{province\}\? Say \'\{again\}\'\."', src)
        ask = src[src.index("province = near_province(world, name)"):][:700]
        assert '"variable_action_cost": 0' in ask and '"success": False' in ask


class TestGRD16TheNearestOfYourOwnMarshals:
    def test_a_one_slip_name_finds_him(self):
        world = WorldState()
        assert PN.nearest_own_marshal(world, "Nay") == "Ney"
        assert PN.nearest_own_marshal(world, "nye") == "Ney"          # a transposition
        assert PN.nearest_own_marshal(world, "Davoust") == "Davout"

    def test_never_a_foe_and_never_a_guess(self):
        world = WorldState()
        foe = next(m for m in world.marshals.values() if m.nation != world.player_nation)
        assert PN.nearest_own_marshal(world, foe.name[:-1]) is None, "a foe's name one slip off is not offered"
        assert PN.nearest_own_marshal(world, "Zorglub") is None
        assert PN.nearest_own_marshal(world, "Ne") is None, "two letters are no name"
        assert PN.nearest_own_marshal(world, "Ney") is None, "his own name is not a slip"

    def test_a_short_name_must_begin_as_his_does(self):
        """The review (PW2-R7): "Hey, attack Mack" was answered "did you mean Ney?"."""
        world = WorldState()
        for word in ("Hey", "Key", "Bey", "Rey"):
            assert PN.nearest_own_marshal(world, word) is None, word
        assert PN.nearest_own_marshal(world, "Nay") == "Ney" and PN.nearest_own_marshal(world, "Neu") == "Ney"

    def test_the_refusal_offers_him_and_spends_nothing(self):
        src = (REPO / "backend" / "commands" / "executor.py").read_text(encoding="utf-8")
        block = src[src.index("_near = (nearest_own_marshal(world, _unbound)"):][:620]
        assert "did you mean {_near}?" in block and "Say '{_near}, {_again}'." in block
        assert '"kind": "marshal_not_found"' in src[src.index("_near = (nearest_own_marshal(world, _unbound)"):][:900]

    def test_the_whole_road_played_and_its_seam(self, monkeypatch):
        """`Nay, attack Mack` through the parser and the executor: the answer names Ney and the order to
        give again, and nothing is spent. The seam down: the bare refusal, as before the row."""
        from backend.commands import executor as X
        from backend.commands.executor import CommandExecutor
        from backend.commands.parser import CommandParser

        def ask(text):
            world = WorldState()
            before = int(world.actions_remaining)
            parsed = CommandParser(use_real_llm=False).parse(text, {"world": world})
            result = CommandExecutor().execute(parsed, {"world": world})
            assert int(world.actions_remaining) == before, "an unbound name spends nothing"
            return str(result.get("message") or "")

        said = ask("Nay, attack Mack")
        assert "There is no 'Nay' in the order of battle, Sire — did you mean Ney?" in said, said
        assert "Say 'Ney, attack Mack'." in said, said
        assert X.a_marshal_typo_is_offered_the_nearest_own_name() is True
        monkeypatch.setattr(X, "a_marshal_typo_is_offered_the_nearest_own_name", lambda: False)
        bare = ask("Nay, attack Mack")
        assert "did you mean" not in bare and "There is no 'Nay' in the order of battle" in bare, bare


class TestEndTheWarPointsAtTheButton:
    @pytest.mark.parametrize("text", ["end the war", "I want peace", "make peace"])
    def test_the_answer_is_make_peace(self, text):
        from backend.commands.parser import CommandParser
        parsed = CommandParser(use_real_llm=False).parse(text, {"world": WorldState()})
        blob = str(parsed)
        assert "press Make peace on the war's card" in blob and "Cabinet (F1)" in blob, blob[:600]
        assert "which nation should I direct" not in blob
