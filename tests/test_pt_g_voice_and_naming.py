"""Row PT, slice G — voice and naming.

Build spec: `docs/PLAYTEST_FIXES_SPEC.md` §2 PT-G.

* **G1** the enemy-voice rotation key is post-increment, so `bank[1]` is
  the default and every marquee enemy's authored OPENING line is
  structurally unreachable as an opening.
* **G2** `personality_ack` has no marshal term in its key.
* **G3** every marshal's FIRST petition is pinned to index 0, the bank
  then clamps forever, and the body has no bank at all.
* **G4** Talleyrand breaks his own Voice Bible on a blocking modal.
* **G5** raw internal keys in player prose, six places.
* **G6** the live-LLM fallback emits markdown into a BBCode terminal.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from backend.display_names import humanize_entity_name
from backend.game_logic import jealousy as J
from backend.game_logic.marshal_voice import personality_ack

from tests.conftest import MarshalFactory, WorldFactory

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "godot-client" / "project-sovereign" / "scripts"


# ═══════════════════════════════════════════════════════════════════════
# G1 — the first battle in a province opens on the first line
# ═══════════════════════════════════════════════════════════════════════

class TestTheRotationKeyIsZeroBased:
    def test_a_provinces_first_battle_uses_index_zero(self):
        """`compose_battle_name` is the counter's sole writer and runs
        twenty lines ABOVE the voice reads, so a bare read was
        POST-increment. On a 126-province map most provinces only ever see
        one battle: for a 2-line bank, index 1 IS the line. Archduke
        Charles said the same sentence in four of his five attacks."""
        from backend.commands.combat_executor import _voice_rotation_key

        world = WorldFactory.basic()
        world.battle_counts = {"Swabia": 1}
        assert _voice_rotation_key(world, "Swabia") == 0
        world.battle_counts["Swabia"] = 2
        assert _voice_rotation_key(world, "Swabia") == 1

    def test_it_never_goes_negative(self):
        from backend.commands.combat_executor import _voice_rotation_key

        world = WorldFactory.basic()
        world.battle_counts = {}
        assert _voice_rotation_key(world, "Nowhere") == 0

    def test_both_voices_read_the_same_helper(self):
        """The two sides were locked in phase and must stay so — they
        simply start where the banks were authored to start."""
        src = (REPO / "backend" / "commands"
               / "combat_executor.py").read_text(encoding="utf-8")
        assert src.count("_voice_rotation_key(world, target_location)") == 2
        assert "int(world.battle_counts.get(target_location, 0)))" not in src

    def test_the_authored_opening_line_is_now_reachable(self):
        """`enemy_voice.py:24-29` claims index 0 is pinned "by the
        deterministic rotation" — it was not."""
        from backend.game_logic.enemy_voice import pick_enemy_voice

        first = pick_enemy_voice("Mack", "cautious", "repelled_you",
                                 rotation_key=0)
        second = pick_enemy_voice("Mack", "cautious", "repelled_you",
                                  rotation_key=1)
        assert first and second and first != second


# ═══════════════════════════════════════════════════════════════════════
# G2 — two marshals do not say the same sentence back to back
# ═══════════════════════════════════════════════════════════════════════

class TestTheAckKeyKnowsWhoIsSpeaking:
    def test_two_marshals_on_one_turn_differ(self):
        """MEASURED on consecutive commands: Lannes then Ney, both "Good.
        An army rots standing still."; Davout and Bernadotte both "As
        ordered. I keep my flanks as I go." No marshal term existed
        anywhere in the key."""
        lannes = personality_ack("aggressive", "MOVE_TO", 4, 6,
                                 marshal_name="Lannes")
        ney = personality_ack("aggressive", "MOVE_TO", 4, 6,
                              marshal_name="Ney")
        assert lannes and ney and lannes != ney

    def test_the_same_marshal_still_rotates_across_turns(self):
        lines = {personality_ack("aggressive", "MOVE_TO", t, 6,
                                 marshal_name="Ney") for t in range(3)}
        assert len(lines) > 1

    def test_it_is_deterministic_across_processes(self):
        """`hash()` is salted per process in Python 3 — using it would
        make a marshal speak differently after a restart and the banks
        unpinnable. Pinned by VALUE, not by grepping for the word: a
        source check passes on any expression that merely avoids the
        token, and this one did (it read past the function into the
        banks)."""
        from backend.game_logic.marshal_voice import _name_key

        assert _name_key("Ney") == 2233738303
        assert _name_key("Lannes") == 841129242

    def test_the_key_actually_distributes(self):
        """Two earlier drafts did not, and both looked fine. A SUM of code
        points put "Lannes" and "Ney" on the same index; a `*31`
        polynomial collapsed BACK to that sum mod 3, because 31 is 1 mod 3
        — five of the six French marshals still shared a line."""
        roster = {"Ney": "aggressive", "Lannes": "aggressive",
                  "Murat": "aggressive", "Massena": "aggressive"}
        lines = {personality_ack(p, "MOVE_TO", 4, 6, marshal_name=n)
                 for n, p in roster.items()}
        assert len(lines) >= 3, (
            "four aggressive marshals ordered on one turn must not all "
            "say the same sentence")

    def test_the_literal_still_says_nothing(self):
        """W6-5 doctrine, not a gap."""
        assert personality_ack("literal", "MOVE_TO", 4, 6,
                               marshal_name="Soult") == ""

    def test_the_caller_passes_the_name(self):
        src = (REPO / "backend" / "commands"
               / "strategic_executor.py").read_text(encoding="utf-8")
        # Bounded by a fixed window, not by the first ")" — the argument
        # list contains `getattr(marshal, "personality", "")`, whose paren
        # truncates a naive split before the argument being pinned.
        call = src.split("_ack = personality_ack(")[1][:300]
        assert "marshal_name=marshal.name" in call


# ═══════════════════════════════════════════════════════════════════════
# G3 — the petition is not the same card twice
# ═══════════════════════════════════════════════════════════════════════

@pytest.fixture()
def board():
    ney = MarshalFactory.infantry(name="Ney", location="Belgium",
                                  strength=25000, personality="aggressive")
    murat = MarshalFactory.infantry(name="Murat", location="Paris",
                                    strength=21000, personality="aggressive")
    world = WorldFactory.with_marshals([ney, murat])
    world.actions_remaining = 4
    return world


def _petition_for(world, fires: int):
    ney, murat = world.marshals["Ney"], world.marshals["Murat"]
    ney.jealousy_history = {"Murat": list(range(1, fires + 1))}
    world.pending_marshal_petition = None
    J.queue_confrontation_petition(world, ney, murat, 1)
    return world.pending_marshal_petition


class TestThePetitionVaries:
    def test_the_body_is_not_one_hardcoded_string(self, board):
        """Murat's petition on turn 2 and Massena's on turn 7 were word
        for word identical in BOTH body and speaker_line."""
        bodies = {_petition_for(board, n)["body"] for n in (1, 2, 3)}
        assert len(bodies) == 3

    def test_the_spoken_line_no_longer_clamps(self, board):
        """It was `min`, not `%` — the 3rd, 4th and 10th audience all
        repeated the last line verbatim, forever."""
        lines = [_petition_for(board, n)["speaker_line"] for n in (3, 4, 5)]
        assert len(set(lines)) > 1

    def test_the_first_petition_still_opens_the_bank(self, board):
        first = _petition_for(board, 1)
        assert first["speaker_line"]
        assert first["body"].startswith("Sire,")

    def test_the_escalation_clause_still_rides(self, board):
        """The register that says "this is the SAME feud, grown worse" is
        carried by the body's clause, which is what frees the spoken line
        to cycle."""
        ney, murat = board.marshals["Ney"], board.marshals["Murat"]
        board.pending_marshal_petition = None
        J.queue_confrontation_petition(board, ney, murat, 2)
        assert "entrenched" in board.pending_marshal_petition["body"]

    def test_every_personality_has_a_bank(self):
        from backend.game_logic.jealousy import _PETITION_BODY

        for personality in ("aggressive", "cautious", "literal"):
            assert len(_PETITION_BODY[personality]) >= 3


# ═══════════════════════════════════════════════════════════════════════
# G4 — Talleyrand keeps his own Voice Bible
# ═══════════════════════════════════════════════════════════════════════

class TestTalleyrandKeepsHisRegister:
    def _warning(self):
        from backend.commands.executor import CommandExecutor

        world = WorldFactory.basic()
        key = world._make_diplo_key(world.player_nation, "Prussia")
        world.active_treaties[key] = {
            "type": "non_aggression",
            "nations": [world.player_nation, "Prussia"], "turn_created": 1,
        }
        world.diplomatic_states[key] = "NON_AGGRESSION"
        world.diplomatic_points = 5
        result = CommandExecutor()._diplomatic._execute_diplomatic_declare_war(
            {"target_nation": "Prussia", "action": "diplomatic_declare_war",
             "war_objective": "conquest"}, world)
        message = result.get("message", "")
        assert "Shall I proceed" in message, (
            "the fixture must actually raise the warning, or every pin "
            "below passes on the wrong sentence")
        return message

    def test_he_does_not_shout(self):
        """`DIPLOMAT_VOICE_BIBLE.md:36` lists exclamation marks under
        "Never says", and this was the only Talleyrand line in the game
        that shouted — on the highest-stakes sentence he speaks."""
        assert "Sire!" not in self._warning()

    def test_no_military_vocabulary_as_metaphor(self):
        """`:38` — no "strike", "crush", "annihilate". "shatter that
        commitment" was the breach."""
        message = self._warning().lower()
        for word in ("shatter", "strike", "crush", "annihilate"):
            assert word not in message

    def test_no_moral_absolute(self):
        """`:39` — he deals in consequences, not ethics. "mark us as
        oath-breakers in the eyes of Europe" is a verdict."""
        assert "oath-breakers" not in self._warning()

    def test_he_hedges_as_the_register_requires(self):
        """`:31-33` — "I would counsel", "Permit me to observe", "If I
        may"."""
        message = self._warning()
        assert any(h in message for h in ("permit me", "I would counsel",
                                          "If I may", "One could"))

    def test_he_still_names_the_stake_and_asks(self):
        """The warning's JOB is unchanged — two pins already required
        it."""
        message = self._warning().lower()
        assert "treaty" in message or "oath" in message
        assert "shall i proceed" in message

    def test_the_drifting_def1_lines_lost_the_commercial_idiom(self):
        """CA8-D4's third variants imported a modern commercial idiom into
        courts whose other two variants are period-formal — and the
        ledger/commerce register is specifically TALLEYRAND's per the
        Bible, so it was a cross-voice bleed as well as an anachronism."""
        src = (REPO / "backend" / "game_logic"
               / "diplomatic_templates.py").read_text(encoding="utf-8")
        for phrase in ("the bazaar is open",
                       "prefers investments to wagers",
                       "investments are best documented",
                       "finds the ledger unanimous"):
            assert phrase not in src


# ═══════════════════════════════════════════════════════════════════════
# G5 — raw internal keys in player prose
# ═══════════════════════════════════════════════════════════════════════

class TestNoRawKeysInProse:
    def test_berthiers_observations_are_humanized(self):
        """`battle_report.py` contained ZERO calls to
        `humanize_entity_name` — he said "ArchdukeCharles broke through
        Ney's prepared defenses" in his own mouth."""
        from backend.game_logic.battle_report import _pick_observation

        # A bank whose template actually carries {enemy} — a decisive
        # win. (`lost_costly` names only the marshal, so it would have
        # proved nothing.)
        observation = _pick_observation({
            "outcome": "attacker_victory",
            "attacker_nation": "France", "defender_nation": "Austria",
            "attacker": {"name": "Ney", "casualties": 1000,
                         "remaining": 19000, "forced_retreat": False},
            "defender": {"name": "ArchdukeCharles", "casualties": 9000,
                         "remaining": 12000, "forced_retreat": False},
            "attacker_original_strength": 20000,
            "defender_original_strength": 21000,
            "modifier_snapshot": {"attacker": [], "defender": []},
        }, "France")
        assert "{enemy}" not in observation
        assert "ArchdukeCharles" not in observation

    def test_no_observation_ever_prints_the_raw_key(self):
        """Swept over the bank rather than one draw: only two of the three
        `won_decisively` lines carry `{enemy}` at all, so a single seeded
        call can pass while the repair is absent."""
        import random as _r

        from backend.game_logic.battle_report import _pick_observation

        spaced = 0
        for seed in range(30):
            _r.seed(seed)
            observation = _pick_observation({
                "outcome": "attacker_victory",
                "attacker_nation": "France", "defender_nation": "Austria",
                "attacker": {"name": "Ney", "casualties": 1000,
                             "remaining": 19000, "forced_retreat": False},
                "defender": {"name": "ArchdukeCharles", "casualties": 9000,
                             "remaining": 12000, "forced_retreat": False},
                "attacker_original_strength": 20000,
                "defender_original_strength": 21000,
                "modifier_snapshot": {"attacker": [], "defender": []},
            }, "France")
            assert "ArchdukeCharles" not in observation
            spaced += int("Archduke Charles" in observation)
        assert spaced > 0, (
            "the sweep must actually exercise an {enemy} template, or it "
            "pins nothing")

    def test_the_mailbox_row_and_its_popup_agree(self):
        """The row read "Armistice Losing" while the popup for the SAME
        item read "Armistice"; `PROPOSAL_TYPE_DISPLAY` already mapped all
        four variants and simply was not imported."""
        from backend.models.dialogue_manager import _proposal_display

        assert _proposal_display("armistice_losing") == "Armistice"

    def test_the_mailbox_source_is_a_display_name(self):
        from backend.models.dialogue_manager import _nation_display

        assert _nation_display("PapalStates") != "PapalStates"

    def test_the_settlement_offer_names_the_war(self):
        """"the offered terms for war_1" reached THREE surfaces, while the
        module's own `_war_label_for_id` exists for exactly this."""
        src = (REPO / "backend" / "game_logic"
               / "settlement_offers.py").read_text(encoding="utf-8")
        assert "war_label=str(war_id)," not in src
        assert "war_label=_war_label_for_id(world, war_id)," in src

    def test_the_button_label_is_humanized(self):
        """A Button does not pass through `add_output`, so the terminal's
        own repair can never reach it."""
        from backend.commands.disobedience import _build_strategic_options

        marshal = MarshalFactory.infantry(name="Murat", location="Paris",
                                          strength=20000,
                                          personality="aggressive")
        options = _build_strategic_options(
            marshal, {"action": "pursue", "target": "ArchdukeCharles"},
            None, "Proceed", None, "HOLD")
        preferred = next(o for o in options if o["type"] == "preferred")
        assert "ArchdukeCharles" not in preferred["text"]
        assert "Archduke Charles" in preferred["text"]

    def test_one_more_province_is_singular(self):
        """`EMERGENT_DESIGN_MIN_LOST = 2`, so the commonest case is
        exactly one other province — and it rendered "Bohemia and 1 more
        provinces", in a modal."""
        src = (REPO / "backend" / "game_logic"
               / "emergent_designs.py").read_text(encoding="utf-8")
        block = src.split("_others = len(lost) - 1")[1].split("event = {")[0]
        assert "'s' if _others != 1" in block
        assert "more provinces" not in block

    def test_the_client_finally_has_a_marshal_humanizer(self):
        """There was NO marshal-name helper in `utils.gd` at all — nation
        keys were routed and marshal keys never were."""
        utils = (SCRIPTS / "utils.gd").read_text(encoding="utf-8")
        # The FULL signature, not a prefix: the sweep renamed it to
        # `humanize_entity_name_unused` and a prefix match let that
        # through — a helper nothing can call is not a helper.
        assert "static func humanize_entity_name(name: String) -> String:" in utils
        dialog = (SCRIPTS / "enemy_phase_dialog.gd").read_text(encoding="utf-8")
        assert "Utils.humanize_entity_name(" in dialog

    def test_the_enemy_phase_dialog_humanizes_at_extraction(self):
        """Six interpolation sites, ~84 raw renders in one campaign. Fixed
        ONCE where the names are read, so every interpolation inherits
        it."""
        src = (SCRIPTS / "enemy_phase_dialog.gd").read_text(encoding="utf-8")
        assert src.count("Utils.humanize_entity_name") >= 6
        assert 'var attacker_name = attacker.get("name", "Unknown")' not in src

    def test_the_backend_helper_is_the_model(self):
        """The client's copy must agree with the single source."""
        assert humanize_entity_name("ArchdukeCharles") == "Archduke Charles"
        assert humanize_entity_name("PapalStates") == "Papal States"


# ═══════════════════════════════════════════════════════════════════════
# G6 — the recovery prompt speaks the terminal's language
# ═══════════════════════════════════════════════════════════════════════

class TestTheRecoveryPromptForbidsMarkdown:
    def test_the_system_prompt_constrains_the_format(self):
        """Reachable only in `LLM_MODE=anthropic`, i.e. the shipping BYOK
        path, and `main.gd` renders `message` as BBCode with nothing
        stripping or escaping — so "*Adjusts spectacles nervously*"
        printed its asterisks."""
        from backend.ai.prompt_builder import build_berthier_recovery_prompt

        system, _user = build_berthier_recovery_prompt(
            "gibberish", {}, {"world": WorldFactory.basic()})
        lowered = system.lower()
        assert "markdown" in lowered
        for banned in ("asterisk", "backtick", "square bracket"):
            assert banned in lowered

    def test_the_prompt_is_not_fed_raw_camelcase_names(self):
        """It fed the model "- ArchdukeCharles (Austria) at Swabia" and
        then instructed it to echo "real marshal/enemy names" back."""
        from backend.ai.prompt_builder import _format_enemies

        formatted = _format_enemies({"enemies": {
            "ArchdukeCharles": {"location": "Swabia", "strength": 40000,
                                "nation": "Austria"}}})
        assert "ArchdukeCharles" not in formatted
        assert "Archduke Charles" in formatted


class TestTheReviewFleetRound:
    """Three raw renders the first cut left in blocks it had just fixed."""

    def test_the_casualty_summary_names_are_humanized(self):
        """`_fill` was routed and these three were not, so Berthier's
        observation said "Archduke Charles" and the casualty line under it
        said "ArchdukeCharles"."""
        from backend.game_logic.battle_report import generate_battle_report

        report = generate_battle_report({
            "outcome": "attacker_victory",
            "attacker_nation": "France", "defender_nation": "Austria",
            "attacker": {"name": "Ney", "casualties": 1000,
                         "remaining": 19000, "forced_retreat": False},
            "defender": {"name": "ArchdukeCharles", "casualties": 9000,
                         "remaining": 12000, "forced_retreat": False},
            "attacker_original_strength": 20000,
            "defender_original_strength": 21000,
            "modifier_snapshot": {"attacker": [], "defender": []},
        }, "France")
        assert report["casualty_summary"]["defender_name"] == "Archduke Charles"

    def test_the_enemy_dialog_humanizes_the_target_too(self):
        """`marshal_name` was humanized at :129 and `target` read raw at
        :131, then interpolated into every verb arm three lines later."""
        src = (SCRIPTS / "enemy_phase_dialog.gd").read_text(encoding="utf-8")
        assert 'var target = ai_action.get("target", "")' not in src
        assert 'var target = Utils.humanize_entity_name(' in src
