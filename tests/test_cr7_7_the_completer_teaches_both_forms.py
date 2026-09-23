"""CR-7-7 — "The completer and the School teach both forms."

Build contract: `docs/audits/COMPOUND_CONDITIONAL_COMMANDS_2026_09_20.md`
§CR-7-7. Measured before a line was written (September 22, 2026):
`_MARSHAL_VERBS` was 12 rows with no `then` and no condition slot; `for 3
turns` and `until … arrives` appeared nowhere in `main.gd`; the help text
had no compound or conditional row.

THE FOUNDING RULE — the game must not offer a sentence it cannot read — and
the contract's finding that the existing CX-3 pin could not enforce it: it
sampled the marshal's OWN province, which is precisely the input under
which a silent substitution is invisible, and its executor census asserted
on message substrings, never on `success`. The repaired pin below drives
every offered line through the REAL executor on a province the marshal is
NOT standing in, and was shown RED against the `garrison` row first — that
row is exempted with its dated reason (the substitution is CX-R2's, the
next slice of the queue), and the exemption is proved earned rather than
assumed.
"""

import contextlib
import io
import os
import re

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN_GD = os.path.join(REPO_ROOT, "godot-client", "project-sovereign", "scripts", "main.gd")
TUTOR_GD = os.path.join(REPO_ROOT, "godot-client", "project-sovereign", "scripts",
                        "tutorial_overlay.gd")


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


def _gd_source(path=MAIN_GD):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def _gd_table(name):
    """A `const NAME := [ ... ]` array-of-arrays out of main.gd (the CX-3
    reader: the close bracket is the one at depth 0)."""
    source = _gd_source()
    start = source.index(f"const {name} := [")
    open_at = source.index("[", start)
    depth = 0
    end = None
    for i in range(open_at, len(source)):
        if source[i] == "[":
            depth += 1
        elif source[i] == "]":
            depth -= 1
            if depth == 0:
                end = i
                break
    assert end is not None, name
    rows = re.findall(r"\[([^\]]*)\]", source[open_at + 1:end])
    return [[part.strip().strip('"') for part in row.split(",")] for row in rows]


def _execute(text, stage=None):
    """The REAL endpoint on a FRESH 1805 board (the CX-3 idiom). ``stage``
    may prepare the board first (fortify a corps before `unfortify`; move the
    enemy off before `drill`) — a precondition met is not a substitution."""
    from fastapi.testclient import TestClient
    from backend.ai.parser_eval import build_world
    from backend.commands.parser import CommandParser
    import backend.main as main_module
    with _quiet():
        world = build_world("1805")
        main_module.world = world
        main_module.game_state = {"world": world}
        main_module.parser = CommandParser(use_real_llm=False)
        client = TestClient(main_module.app)
        if stage:
            stage(world, client)
        reply = client.post("/command", json={"command": text}).json()
    return reply, world


def _parse(text):
    from backend.ai.parser_eval import build_llm_game_state, build_world
    from backend.commands.parser import CommandParser
    with _quiet():
        world = build_world("1805")
        state = build_llm_game_state(world)
        return CommandParser(use_real_llm=False).parse(text, state, world=world)


# The board facts every line below is filled with: Ney (aggressive) and
# Davout (cautious) both stand at Rhineland; Swabia is adjacent and Mack
# stands in it; Lorraine is adjacent, French, and empty of enemies.
MARSHAL_FOR = {"march to": "Ney", "move to": "Ney", "hold": "Davout"}
ENEMY = "Mack"
OTHER = "Ney"
REGION_NOT_HIS = {"then attack": "Swabia", "until": "Lorraine",
                  "for 3 turns": "Lorraine", "until relieved": "Lorraine"}


def _compose(entry):
    verb, cont, slot = entry
    marshal = MARSHAL_FOR[verb]
    region = REGION_NOT_HIS[cont]
    base = f"{marshal}, {verb} {region}"
    if slot == "E":
        return base + f" {cont} {ENEMY}"
    if slot == "M":
        return base + f" {cont} {OTHER} arrives"
    return base + f" {cont}"


class TestTheContinuationsAreReadable:

    def test_the_table_has_the_two_forms(self):
        table = _gd_table("_CONTINUATIONS")
        assert ["march to", "then attack", "E"] in table
        assert ["hold", "until", "M"] in table
        assert ["hold", "for 3 turns", ""] in table
        assert len(table) == 5, table

    @pytest.mark.parametrize("entry", _gd_table("_CONTINUATIONS"))
    def test_every_offered_line_parses_and_executes(self, entry):
        line = _compose(entry)
        parsed = _parse(line)
        assert parsed.get("success"), (line, parsed.get("error"))
        if entry[1] == "then attack":
            assert parsed.get("strategic_type") == "MOVE_TO" and parsed.get("attack_on_arrival") is True
            assert parsed.get("dropped_sequel") is None
        else:
            assert parsed.get("strategic_type") == "HOLD"
            assert parsed.get("strategic_condition"), line
        reply, world = _execute(line)
        assert reply.get("success") is True, (line, reply.get("message"))
        marshal = world.get_marshal(MARSHAL_FOR[entry[0]])
        assert marshal.strategic_order is not None, line

    def test_the_offer_is_wired_into_the_slot_walk(self):
        body = _gd_source()
        walk = body[body.index("func _add_verb_or_target"):]
        walk = walk[:walk.index("\nfunc ", 10)]
        assert "_add_continuations(marshal, rest, out, seen)" in walk
        cont = body[body.index("func _add_continuations"):body.index("func _add_verb_or_target")]
        # CX-R2: the attack is drawn nearest the destination and the awaited
        # marshal nearest the ground held — `_enemy_offers` /
        # `_marshal_offers` in place of the alphabetical rosters.
        assert "_enemy_offers(ground)" in cont and "_marshal_offers(ground, key)" in cont
        assert '" arrives"' in cont
        # Never on a half-typed target — BOTH branches guard it, and each
        # guard is pinned by its own lines (the sweep found a loose census
        # satisfied by the hold branch alone while the march branch offered
        # `then attack` on "Ney, march to Swa"). CX-R2 adds the reach: a
        # head his lawful road does not reach is no head at all. Driven by
        # `tests/test_cx_r2_the_offer_is_reachable.py` (`TestTheContinuations`)
        # as well.
        assert ("\t\t\tif not _is_region_name(head_target):\n\t\t\t\tcontinue\n"
                "\t\t\tground = _canonical_region(head_target)\n"
                "\t\t\tif ground == here or not reach.has(ground):\n\t\t\t\tcontinue\n"
                "\t\t\tbase = marshal + \", \" + verb + \" \" + ground") in cont
        assert "if head_target != \"\" and not _is_region_name(head_target):\n\t\t\t\tcontinue" in cont
        assert "if ground != here and not reach.has(ground):\n\t\t\t\t\tcontinue" in cont


class TestTheRepairedVerbTablePin:
    """Every `_MARSHAL_VERBS` line, on a province the marshal is NOT in."""

    # The garrison exemption this pin carried (dated September 22, 2026) is
    # RETIRED by CX-R2 (September 23, 2026): the completer's `garrison` slot
    # is "H" — the province he STANDS in, the only one the executor has ever
    # garrisoned — and `_execute_garrison` now refuses a named province that
    # is not his instead of substituting it. The row runs below on a board
    # with room under the cap; the substitution is pinned refused below.
    EXEMPT = {}

    @staticmethod
    def _adjacent_not_his(world, marshal_name):
        marshal = world.get_marshal(marshal_name)
        for name in sorted(world.regions[marshal.location].adjacent_regions):
            region = world.regions[name]
            if (region.controller == world.player_nation
                    and not world.get_enemies_in_region(name, world.player_nation)):
                return name
        raise AssertionError("no adjacent friendly province")

    @staticmethod
    def _stage_for(verb):
        """The state a no-target verb needs, met on the board FIRST — an
        honest precondition refusal ("not currently fortified", "enemy
        forces nearby") is the executor telling the truth, not the silent
        substitution this pin exists to catch."""
        if verb == "unfortify":
            return lambda world, client: client.post(
                "/command", json={"command": "Davout, fortify"})
        if verb == "garrison":
            def room_under_the_cap(world, _client):
                # The boot keeps exactly three garrisons — the cap.
                flanders = world.get_region("Flanders")
                flanders.garrison_strength = 0
                flanders.garrison_detachment = False
            return room_under_the_cap
        if verb == "drill":
            def clear_the_neighbourhood(world, _client):
                for enemy in list(world.get_enemy_marshals()):
                    if enemy.location in ("Swabia", "Bern", "Munich", "Nassau",
                                          "Frankfurt", "Brabant", "Gelderland"):
                        enemy.location = "Vienna"
                world.invalidate_active_nations_cache()
            return clear_the_neighbourhood
        return None

    @pytest.mark.parametrize("entry", _gd_table("_MARSHAL_VERBS"))
    def test_the_line_executes_on_a_province_he_is_not_in(self, entry):
        verb, slot, action = entry
        if verb in self.EXEMPT:
            pytest.skip(self.EXEMPT[verb])
        from backend.ai.parser_eval import build_world
        with _quiet():
            world = build_world("1805")
        marshal = "Davout" if verb in ("hold", "fortify", "defend", "drill", "unfortify") else "Ney"
        if slot in ("R", "S"):
            target = "Swabia"
        elif slot == "A":
            target = self._adjacent_not_his(world, marshal)
        elif slot == "H":
            # The one province this slot may name: his own (CX-R2).
            target = world.get_marshal(marshal).location
        elif slot == "E":
            target = ENEMY
        elif slot == "M":
            target = "Ney" if marshal != "Ney" else "Davout"
        else:
            target = ""
        line = f"{marshal}, {verb}" + (f" {target}" if target else "")
        parsed = _parse(line)
        assert parsed.get("success") and parsed["command"]["action"] == action, (line, parsed)
        reply, _world = _execute(line, stage=self._stage_for(verb))
        assert reply.get("success") is True, (line, reply.get("message"))

    def test_the_retired_exemption_names_no_substitution(self):
        """What the exemption covered: a garrison named on a province he is
        NOT standing in. With room under the cap it is now refused with the
        road to it — never quietly left at his feet — and nothing is
        detached."""
        reply, world = _execute("Ney, garrison Lorraine",
                                stage=self._stage_for("garrison"))
        assert reply.get("success") is False, reply.get("message")
        assert "March him to Lorraine first" in reply.get("message", "")
        assert world.get_region("Rhineland").garrison_strength == 0

    def test_the_exemption_is_not_a_wildcard(self):
        table = {row[0] for row in _gd_table("_MARSHAL_VERBS")}
        assert set(self.EXEMPT) <= table
        assert self.EXEMPT == {}, "CX-R2 retired the last exemption"


class TestTheManualAndTheSchool:

    @staticmethod
    def _help_body():
        from backend.commands.meta_executor import MetaExecutor
        from backend.ai.parser_eval import build_world
        with _quiet():
            world = build_world("1805")
            return MetaExecutor(None)._execute_help({}, world)["message"]

    def test_the_help_teaches_both_forms(self):
        body = self._help_body()
        assert "TWO ORDERS IN ONE LINE" in body
        assert '"Ney, march to Swabia then attack Mack"' in body
        assert '"Davout, hold Lorraine until Ney arrives"' in body
        assert "there is no queue" in body

    @pytest.mark.parametrize("phrase,check", [
        ("Ney, march to Swabia then attack Mack", lambda r, w: w.get_marshal("Ney").strategic_order is not None),
        ("Davout, hold Lorraine until Ney arrives", lambda r, w: w.get_marshal("Davout").strategic_order.condition.until_marshal_arrives == "Ney"),
        ("Ney, scout Swabia, then fortify", lambda r, w: r.get("relay_command") == "Ney, fortify"),
    ])
    def test_every_quoted_phrasing_does_what_the_manual_says(self, phrase, check):
        reply, world = _execute(phrase)
        assert reply.get("success") is True, (phrase, reply.get("message"))
        assert check(reply, world), (phrase, reply.get("message"))

    def test_the_school_names_the_forms(self):
        src = _gd_source(TUTOR_GD)
        step = src[src.index('"id": "first_move"'):src.index('"id": "first_end_turn"')]
        assert "then attack" in step and "until Ney arrives" in step

    def test_a_player_can_reach_both_forms_from_completions_alone(self):
        """The keystroke script, as the table's own contract: typing a
        complete march offers `then attack <E>`; typing a complete hold
        offers `until <M> arrives`. Both offered lines execute (above)."""
        table = _gd_table("_CONTINUATIONS")
        by_verb = {}
        for verb, cont, slot in table:
            by_verb.setdefault(verb, []).append((cont, slot))
        assert ("then attack", "E") in by_verb["march to"]
        assert ("until", "M") in by_verb["hold"]
