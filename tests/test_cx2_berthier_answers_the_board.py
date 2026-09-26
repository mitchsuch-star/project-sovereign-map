"""CX-2 — "BERTHIER ANSWERS THE BOARD".

Row CX ("The Hand on the Keyboard"). Owning spec:
`docs/COMMAND_EXPERIENCE_SPEC.md` §3.2.

THE FINDING
===========
Asking a question is the one thing the typed road can do that no chip can
ever do. Measured against the twelve questions a player actually asks (row CX
recon, 152 driven rows on the shipped 1805 board):

    TWO were answered. TEN were not, and eight of the ten were answered by
    nothing at all, in any phrasing.

Every one of the ten returned the SAME **12,717-character COMMAND
REFERENCE** — which, measured, contains the words `status`, `where is`,
`who holds` and `how many men` **zero times**. The desk that could have
answered four of them was unreachable from the only surface the game hands a
lost player.

And the same blindness sat one layer out, in the copy the player reads at the
exact moment the parser has failed them. `_berthier_mock_response` hardcoded
three courts by name — *"propose peace with Prussia"*, *"Talleyrand, propose
alliance with Austria"*, *"declare war on Prussia"*. On the shipped 1805 boot
**France is at PEACE with Prussia**, so the game's own recovery advice was an
act of war against a neutral — fifty-two lines below `_hostile_first`, the
guard FA-80(c) added to stop precisely that for the ATTACK templates and
which the diplomatic ones never inherited. Worse: all three name a road the
shipped client REDIRECTS (`main.gd::_redirect_diplomatic_command`, ruling
G1), so the recovery text taught a sentence that cannot be sent.

WHAT THIS SLICE BUILDS
======================
* **Nine new board kinds** on the desk — treasury, war score, at-war-with, a
  court's design, a march's reach, an attack's muster, what may be built,
  what a thing costs, and what can be ordered at all. Each reads the SEAM THE
  MECHANIC READS (`_build_economy`, `get_war_score_for`, `get_active_agenda`,
  `find_path(passable_for=…)`, `_build_muster_preview` + its own renderer,
  `region.can_build`, the levy pricer), so a quoted figure is the applied
  figure and the two cannot drift. That is the row's central finding stated
  as code: *the chips are priced and the typed verbs are blind* — this is
  where the typed road stops being blind.
* **`backend/ai/counsel.py`** — ONE board-derived source for "what can I do",
  read by the desk's `options` kind, by Berthier's shrug and by the router,
  so the three can never propose an order another would refuse.
* **The router** — a question the desk cannot take gets a sentence, the
  surface that holds the answer, and the orders that would be carried out,
  instead of the manual.

MEASURED: 41 of 41 driven questions are answered, **0 walls** (was 10 of 12
walls on the user's own twelve).

PINS FLIPPED CONSCIOUSLY, each with its reason on the row
=========================================================
* corpus `how-is-the-war-going` (`help` → `status`) — the manual holds no war
  score.
* corpus `parseneg-can-i-attack-mack` and `i-question-still-help` (`help` →
  `status`, scoped to 1805, with legacy twins added) and
  `test_fa_slice7…::test_guidance_and_feasibility_keep_the_command_reference`
  (split in two) — all on ruling **R7's own re-open condition**: *"A
  question-answering Berthier is CR-6's to build; when it exists, it replaces
  the `help` route, not the guard."*
* `question_desk`'s module docstring, whose "feasibility stays on the COMMAND
  REFERENCE" paragraph is now false and is CORRECTED IN PLACE rather than
  deleted.
"""

import io
import contextlib

import pytest

from backend.ai import counsel as C
from backend.ai import question_desk as QD


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


@pytest.fixture(scope="module")
def board():
    from backend.ai.parser_eval import build_world
    with _quiet():
        return build_world("1805")


@pytest.fixture
def ask():
    """Drive `POST /command` on a FRESH 1805 board and return the reply."""
    from fastapi.testclient import TestClient
    from backend.ai.parser_eval import build_world
    from backend.commands.parser import CommandParser
    import backend.main as main_module

    saved = (main_module.parser, main_module.world, main_module.game_state)

    def _ask(text):
        with _quiet():
            world = build_world("1805")
            main_module.world = world
            main_module.game_state = {"world": world}
            main_module.parser = CommandParser(use_real_llm=False)
            client = TestClient(main_module.app)
            before = world.actions_remaining
            response = client.post("/command", json={"command": text}).json()
        _ask.world = world
        _ask.ap = (before, world.actions_remaining)
        return response

    yield _ask
    (main_module.parser, main_module.world, main_module.game_state) = saved


COMMAND_REFERENCE = "COMMAND REFERENCE"


# ═══════════════════════════════════════════════════════════════════════════
# The twelve the user named
# ═══════════════════════════════════════════════════════════════════════════

class TestTheTwelveQuestions:
    """Each of these is driven end to end. The assertion is not "it says
    something" — it is that the answer contains a FIGURE OR A NAME the board
    actually holds, and that the manual is not what came back."""

    TWELVE = [
        ("where is Ney", ("Rhineland", "24,000")),
        ("can Ney reach Vienna", ("Vienna", "Rhineland")),
        ("who is winning", ("War score", "Austria")),
        ("what happens if I attack Mack", ("MUSTER", "Nothing has been ordered")),
        ("should I attack", ("cannot answer", "What I CAN do")),
        ("why did that fail", ("campaign log",)),
        ("what can I build here", ("Rhineland", "300g")),
        ("how much is a battalion", ("gold", "infantry")),
        ("what does Austria want", ("Austria", "Redeem Italy")),
        ("am I at war with Prussia", ("Prussia", "Peace")),
        ("how many men does Davout have", ("26,000", "Rhineland")),
        ("what's my income", ("treasury", "Net")),
    ]

    @pytest.mark.parametrize("text,needles", TWELVE)
    def test_it_is_answered_and_not_walled(self, ask, text, needles):
        response = ask(text)
        message = response.get("message") or ""
        assert COMMAND_REFERENCE not in message, (text, len(message))
        assert len(message) < 2000, (text, len(message))
        for needle in needles:
            assert needle.lower() in message.lower(), (text, needle, message[:300])

    @pytest.mark.parametrize("text,_needles", TWELVE)
    def test_asking_never_costs_an_action(self, ask, text, _needles):
        response = ask(text)
        assert ask.ap[0] == ask.ap[1], (text, ask.ap)
        assert not response.get("battle_report"), text

    def test_none_of_the_twelve_returns_the_manual(self, ask):
        """The headline, stated once as a count so it cannot be lost in a
        parametrize list: ten of these twelve used to return 12,717
        characters of command reference."""
        walls = [text for text, _ in self.TWELVE
                 if COMMAND_REFERENCE in (ask(text).get("message") or "")]
        assert walls == [], walls


# ═══════════════════════════════════════════════════════════════════════════
# The answers come from the seam the MECHANIC reads
# ═══════════════════════════════════════════════════════════════════════════

class TestShownIsApplied:

    def test_the_muster_is_the_attack_s_own_string(self, ask, board):
        """"what happens if I attack Mack" prints `_format_muster_lines` of
        `_build_muster_preview` — the SAME renderer the order itself uses, so
        the question and the order can never give two accounts of one field."""
        from backend.commands.executor import CommandExecutor
        with _quiet():
            combat = CommandExecutor()._combat
            preview = combat._build_muster_preview(
                board.get_marshal("Ney"), board.get_marshal("Mack"),
                board, {"world": board})
            expected = combat._format_muster_lines(preview)
        message = ask("what happens if I attack Mack").get("message") or ""
        # The preview is fog- and roster-dependent, so the pin is on the
        # HEADER line, which both must carry verbatim.
        header = expected.splitlines()[0]
        assert header in message, (header, message[:400])

    def test_the_build_list_is_the_build_gate(self, ask, board):
        """Every option comes through `region.can_build`, the single gate, so
        the desk cannot advertise something the executor refuses."""
        from backend.models.region import BUILDING_TYPES, can_build
        message = ask("what can I build here").get("message") or ""
        region = board.get_region("Rhineland")
        for key, spec in BUILDING_TYPES.items():
            verdict = can_build(board, region, key, "France")
            ok = verdict[0] if isinstance(verdict, (tuple, list)) else bool(verdict)
            word = key.replace("_", " ")
            if ok:
                assert word in message, (word, message)
                assert f"{int(spec['gold_cost']):,}g" in message, (word, message)

    def test_the_treasury_figures_are_the_ledger_s(self, ask, board):
        from backend.game_logic.ledger import _build_economy
        with _quiet():
            economy = _build_economy(board, "France")
        message = ask("what's my income").get("message") or ""
        assert f"{int(economy['treasury']):,}" in message
        assert f"{int(economy['income']):,}" in message
        assert f"{int(economy['net']):,}" in message

    def test_the_war_score_is_the_canonical_helper_s(self, ask, board):
        from backend.game_logic.diplomacy import get_war_score_for
        message = ask("who is winning").get("message") or ""
        score = int(get_war_score_for(board, "France", "Austria") or 0)
        assert f"{score:+d}" in message, message

    def test_the_reach_answer_obeys_the_movement_law(self, ask, board):
        """`find_path(passable_for=…)` — the road he would be ALLOWED to
        walk, not the one the map draws."""
        message = ask("can Ney reach Vienna").get("message") or ""
        lawful = board.find_path("Rhineland", "Vienna", passable_for="France")
        if lawful:
            assert " -> ".join(lawful) in message, message
        else:
            assert "not lawfully" in message.lower() or "no road" in message.lower()


# ═══════════════════════════════════════════════════════════════════════════
# The shrug stops teaching a war on a neutral
# ═══════════════════════════════════════════════════════════════════════════

class TestTheShrugTeachesWhatWorks:

    def _shrugs(self, ask, samples=30):
        """`random.choice` picks one of three templates, so the pin samples."""
        return {(ask("xyzzy foobar").get("message") or "") for _ in range(samples)}

    def test_no_shrug_proposes_a_war_on_a_court_we_are_at_peace_with(self, ask):
        for message in self._shrugs(ask):
            assert "declare war" not in message.lower(), message
            assert "Prussia" not in message, message

    def test_no_shrug_teaches_a_road_the_client_redirects(self, ask):
        """Ruling G1 retired the typed diplomatic verbs as a player surface.
        The recovery copy went on teaching them for a year."""
        for message in self._shrugs(ask):
            for forbidden in ("propose peace with", "propose alliance with",
                              "declare war on"):
                assert forbidden not in message.lower(), (forbidden, message)

    def test_every_shrug_names_the_cabinet_as_a_door(self, ask):
        for message in self._shrugs(ask):
            assert "F1" in message and "Cabinet" in message, message

    def test_the_orders_a_shrug_proposes_are_orders_that_work(self, ask, board):
        """An order named in the shrug must be one `what_can_i_do` produced,
        which is the list the executor's own probes built."""
        with _quiet():
            legal = set(C.what_can_i_do(board, "France", limit=4))
        assert legal, "the counsel produced nothing on the boot board"
        quoted = set()
        for message in self._shrugs(ask):
            for line in legal:
                if line in message:
                    quoted.add(line)
        assert quoted, (legal, "no shrug quoted a legal order")


# ═══════════════════════════════════════════════════════════════════════════
# The router
# ═══════════════════════════════════════════════════════════════════════════

class TestTheRouter:

    def test_an_unanswerable_question_is_short_and_names_a_surface(self, ask):
        message = ask("why did that fail").get("message") or ""
        assert COMMAND_REFERENCE not in message
        assert len(message) < 900, len(message)
        assert "campaign log" in message
        assert "press L" in message

    def test_the_router_offers_orders_that_would_be_carried_out(self, ask):
        message = ask("should I attack").get("message") or ""
        assert "What I CAN do today" in message
        assert "F1" in message

    def test_the_router_still_points_at_the_manual(self, ask):
        message = ask("should I attack").get("message") or ""
        assert "help" in message.lower()

    def test_a_syntax_question_keeps_the_manual(self, ask):
        """"how do I attack?" asks about the game's GRAMMAR, and the
        reference genuinely is the answer. Unchanged."""
        for text in ("how do I attack?", "how does recruiting work?"):
            assert COMMAND_REFERENCE in (ask(text).get("message") or ""), text


# ═══════════════════════════════════════════════════════════════════════════
# Levers, fog and the counsel's own contract
# ═══════════════════════════════════════════════════════════════════════════

class TestTheLevers:

    def test_the_board_lever_returns_the_desk_to_five_kinds(self, ask):
        original = QD.THE_DESK_ANSWERS_THE_BOARD
        try:
            QD.THE_DESK_ANSWERS_THE_BOARD = False
            assert COMMAND_REFERENCE in (ask("what's my income").get("message") or "")
            # …and the five older kinds are untouched by the lever.
            assert "Rhineland" in (ask("where is Ney").get("message") or "")
        finally:
            QD.THE_DESK_ANSWERS_THE_BOARD = original

    def test_the_desk_lever_still_governs_everything(self, ask):
        original = QD.QUESTION_DESK_ACTIVE
        try:
            QD.QUESTION_DESK_ACTIVE = False
            for text in ("where is Ney", "what's my income", "should I attack"):
                assert COMMAND_REFERENCE in (ask(text).get("message") or ""), text
        finally:
            QD.QUESTION_DESK_ACTIVE = original

    def test_the_counsel_lever_restores_the_hardcoded_shrug(self, ask):
        original = C.COUNSEL_IS_DERIVED_FROM_THE_BOARD
        try:
            C.COUNSEL_IS_DERIVED_FROM_THE_BOARD = False
            assert C.what_can_i_do(None, "France") == []
            # The shrug falls back to its own first_marshal/first_enemy pair
            # rather than breaking.
            message = ask("xyzzy foobar").get("message") or ""
            assert message
            assert "declare war" not in message.lower()
        finally:
            C.COUNSEL_IS_DERIVED_FROM_THE_BOARD = original


class TestTheCounselIsHonest:

    def test_it_never_proposes_a_march_the_executor_would_refuse(self, board):
        """Asked of `MovementExecutor.move_refusal_probe`, the pure single
        source the objection battery already consults (the PF-4 idiom)."""
        from backend.commands.movement_executor import MovementExecutor
        with _quiet():
            lines = C.what_can_i_do(board, "France", limit=6)
        marches = [line for line in lines if ", march to " in line]
        for line in marches:
            who, _, where = line.partition(", march to ")
            marshal = board.get_marshal(who.strip())
            assert marshal is not None, line
            region = board.get_region(where.strip())
            assert region is not None, line
            refusal = MovementExecutor.move_refusal_probe(
                board, marshal, region, where.strip())
            assert refusal is None, (line, refusal)

    def test_it_never_proposes_an_attack_on_a_court_we_are_at_peace_with(self, board):
        """FA-80(c)'s rule, which the diplomatic templates never inherited."""
        with _quiet():
            lines = C.what_can_i_do(board, "France", limit=6)
        for line in lines:
            if ", attack " not in line:
                continue
            _, _, foe = line.partition(", attack ")
            enemy = board.get_marshal(foe.strip())
            if enemy is None:
                continue
            assert board.is_at_war("France", enemy.nation), line

    def test_it_never_names_an_enemy_the_player_cannot_see(self, board):
        """Golden Rule 5: the counsel reads `get_visible_enemies`, never the
        omniscient roster."""
        with _quiet():
            lines = C.what_can_i_do(board, "France", limit=6)
            visible = {m.name for m in board.get_visible_enemies("France")}
        from backend.display_names import humanize_entity_name
        shown = {humanize_entity_name(name) for name in visible} | visible
        attacks = [line for line in lines if ", attack " in line]
        assert attacks, ("no attack line on the boot board — the pin would "
                         "pass vacuously", lines)
        for line in attacks:
            _, _, foe = line.partition(", attack ")
            assert foe.strip() in shown, (line, sorted(shown))

    def test_it_never_proposes_a_diplomatic_verb(self, board):
        """The Cabinet is the door (ruling G1). The counsel names the door and
        never a sentence the client would redirect."""
        with _quiet():
            lines = C.what_can_i_do(board, "France", limit=6)
        for line in lines:
            lowered = line.lower()
            for verb in ("declare war", "propose", "alliance", "invest in",
                         "autonomy", "cede", "guarantee", "sponsor",
                         "buy off", "vassal"):
                assert verb not in lowered, (verb, line)

    def test_the_pointer_table_never_invents_a_screen(self):
        """Every pointer names a surface with a real key. A wrong pointer is
        worse than no pointer."""
        for topic in ("economy", "marshals", "diplomacy", "courts", "orders"):
            pointer = C.surface_pointer(topic)
            assert pointer, topic
            assert ("press" in pointer.lower() or "click" in pointer.lower()), (
                topic, pointer)
        assert C.surface_pointer("no-such-topic") is None


# ═══════════════════════════════════════════════════════════════════════════
# THE SWEEP'S OWN FINDINGS — the guards pinned on a board where they BITE
# ═══════════════════════════════════════════════════════════════════════════
# Six of this slice's first pins came back INERT, and every one was the same
# mistake: measured on the BOOT board, where the guard has nothing to refuse.
#
#   * `region.can_build` permits all five buildings at Rhineland, so removing
#     the gate changed nothing.
#   * the nearest visible enemy at boot is Mack, a court we ARE at war with,
#     so removing the at-war filter changed nothing.
#   * the extra marshals an omniscient roster adds are all out of reach, so
#     swapping the fog source changed nothing.
#   * the levy is SHUT at boot (France is 59,000 over the force limit), so
#     the priced levy line never rendered and its pin never ran.
#
# A guard is pinned where it bites. These stage the board.

class TestTheGuardsWhereTheyBite:

    def _staged(self):
        from backend.ai.parser_eval import build_world
        with _quiet():
            return build_world("1805")

    def test_the_build_gate_is_read_where_it_REFUSES(self):
        """A town has zero building slots (`BUILDING_SLOT_LIMITS`), so the
        gate refuses everything there. If the desk stopped asking the gate it
        would advertise five buildings on ground that can hold none."""
        from backend.models.region import (BUILDING_SLOT_LIMITS,
                                           BUILDING_TYPES, can_build)
        world = self._staged()
        shut = None
        for name, region in world.regions.items():
            if getattr(region, "controller", None) != "France":
                continue
            if BUILDING_SLOT_LIMITS.get(getattr(region, "region_type", ""), 0):
                continue
            shut = name
            break
        assert shut, "no slot-less French province on the boot board"
        # The gate itself agrees this is the refusing case.
        for key in BUILDING_TYPES:
            verdict = can_build(world, world.get_region(shut), key, "France")
            ok = verdict[0] if isinstance(verdict, (tuple, list)) else bool(verdict)
            assert not ok, (shut, key)
        answer = QD._answer_can_build(world, "France", shut) or ""
        assert "Nothing can be built" in answer, (shut, answer)
        for key in BUILDING_TYPES:
            assert f"{int(BUILDING_TYPES[key]['gold_cost']):,}g" not in answer, (
                shut, key, answer)

    def test_the_counsel_refuses_a_visible_court_at_peace(self):
        """⚠ MEASURED AND CORRECTED: the at-war filter is REDUNDANT TODAY, and
        the pin says so rather than pretending otherwise.

        `get_visible_enemies` reads `get_enemies_of_nation`, which is already
        AT-WAR scoped (`world_state.py`, "Only returns marshals whose nation
        is AT WAR"), so a court at peace can never reach the counsel through
        it — which is why the first version of this pin came back INERT from
        the mutation sweep: staging Deroy of Bavaria beside Mack did not put
        him in the list at all.

        The filter is kept as defence in depth, because the counsel names a
        target the player will be told to attack and the cost of an upstream
        widening is a proposed war on a neutral — FA-80(c)'s exact defect.
        It is therefore pinned at the FUNCTION, by handing the counsel a
        roster the upstream helper would not have produced.
        """
        world = self._staged()
        neutral = next((m for m in world.marshals.values()
                        if m.nation != "France" and m.strength > 0
                        and not world.is_at_war("France", m.nation)), None)
        assert neutral, "no neutral commander on the boot board"
        ours = world.get_player_marshals()[0]
        neutral.location = ours.location

        saved = type(world).get_visible_enemies
        try:
            type(world).get_visible_enemies = lambda self, nation: [neutral]
            with _quiet():
                lines = C.what_can_i_do(world, "France", limit=6)
            assert all(f", attack {neutral.name}" not in line for line in lines), (
                neutral.name, lines)

            # …and with the filter gone it WOULD be proposed, so the
            # assertion above is about the filter and not about the board.
            at_war = C._at_war_with
            try:
                C._at_war_with = lambda *_a, **_k: True
                with _quiet():
                    loose = C.what_can_i_do(world, "France", limit=6)
                assert any(f", attack {neutral.name}" in line for line in loose), (
                    neutral.name, loose)
            finally:
                C._at_war_with = at_war
        finally:
            type(world).get_visible_enemies = saved

    def test_the_counsel_reads_the_FOG_and_not_the_roster(self):
        """Staged: an at-war enemy standing beside us on ground we have NOT
        scouted. The omniscient roster names him; `get_visible_enemies` does
        not; the counsel must follow the fog."""
        from backend.models.intel import UNKNOWN
        world = self._staged()
        hidden = None
        for marshal in world.marshals.values():
            if marshal.nation == "France" or marshal.strength <= 0:
                continue
            if world.is_at_war("France", marshal.nation):
                hidden = marshal
                break
        assert hidden, "no hostile commander on the boot board"
        ours = world.get_player_marshals()[0]
        ours.location = hidden.location
        world.get_region_intel(hidden.location).visibility = UNKNOWN
        with _quiet():
            visible = {m.name for m in world.get_visible_enemies("France")}
            omniscient = {m.name for m in world.get_enemies_of_nation("France")}
        assert hidden.name in omniscient, hidden.name
        assert hidden.name not in visible, (hidden.name, sorted(visible))

        with _quiet():
            lines = C.what_can_i_do(world, "France", limit=6)
        assert all(f", attack {hidden.name}" not in line for line in lines), (
            hidden.name, lines)

    def test_the_levy_line_is_PRICED_where_the_levy_is_open(self):
        """The levy is SHUT at boot — France stands 59,000 over the force
        limit — so the priced line never renders there and its first pin
        never ran. Staged open by standing a corps down."""
        from backend.game_logic.ledger import _build_economy
        world = self._staged()
        # Two things shut it at boot: the force limit, and the fact that no
        # corps of ours stands within reach of the depot. Open both.
        marshals = list(world.get_player_marshals())
        for marshal in marshals[1:]:
            marshal.strength = 1
        marshals[0].location = world.get_nation_capital("France")
        with _quiet():
            levy = (_build_economy(world, "France") or {}).get("levy") or {}
        assert levy.get("recipient_in_range"), levy
        with _quiet():
            lines = C.economy_counsel(world, "France", limit=3)
        priced = [line for line in lines if line.startswith("recruit infantry in ")]
        assert priced, lines
        line = priced[0]
        # CRT-7 / DESK-2 (SR-3a part (ii), Sept 26 2026) — FLIPPED
        # CONSCIOUSLY: the line quotes `economy_executor.recruit_quote`, the
        # figure the ORDER charges, not the ledger's headline levy. The two
        # differed on this very board (450g for 10,000 in the ledger against
        # 518g for 10,000 under Ney from the executor) — which is the row's
        # finding, that the counsel's staged levy line charged more than it
        # quoted. Shown = applied now; the ledger's headline is pinned
        # elsewhere as the ledger's.
        from backend.commands.economy_executor import recruit_quote
        with _quiet():
            quote = recruit_quote(world, world.get_nation_capital("France"),
                                  "infantry", "France")
        assert quote.get("ok"), quote
        assert f"{int(quote['price']):,}g" in line, (line, quote)
        assert f"{int(quote['amount']):,} men" in line, (line, quote)
        assert str(quote["recipient"]) in line, (line, quote)

    def test_the_board_answer_is_actually_reached(self):
        """`answer_board_question` returning None does NOT fall back to the
        manual — it falls to "I cannot say, Sire" — so a pin that only
        forbids the COMMAND REFERENCE cannot see it. This one asserts the
        content."""
        world = self._staged()
        question = QD.classify_board_question(
            "what's my income", nations=["Austria"])
        assert question and question["kind"] == "treasury"
        answer = QD.answer_board_question(world, question) or ""
        assert "treasury holds" in answer, answer
        assert "Net" in answer, answer
