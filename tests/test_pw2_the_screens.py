"""Row PW "Plain Words", part 2 (November 18, 2026) — the rest of the screens.

What the second blind reading's readers still found unclear after part 1, and the screens the plan's "keep
going — all screens" named: the Cabinet's page, the peace table's last faces, a marshal's objection, a
letter that arrives, the war card's word, the first morning's "what now", the small lines of the log, and
the battle's dice lines. The backend's halves are pinned on behaviour, the client's on its source; the real
client is driven at the first player's own setup by `tests/test_dd_b_the_client_hands.py`.
"""

from __future__ import annotations

import pathlib
import re

import pytest

from backend.game_logic import battle_telling as T
from backend.game_logic import cabinet_rows as CR
from backend.game_logic import mailbox_payloads as MP
from backend.models.world_state import WorldState

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "godot-client" / "project-sovereign" / "scripts"


def _src(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


def _func(source: str, name: str) -> str:
    match = re.search(rf"^(?:static )?func {re.escape(name)}\(.*?(?=^\S|\Z)", source, re.S | re.M)
    assert match, f"no func {name}"
    return match.group(0)


# ═════════════════════════════════════════════════════════════════════════════
# The Cabinet
# ═════════════════════════════════════════════════════════════════════════════

class TestTheCabinetInPlainWords:
    WIZARD = _src(SCRIPTS / "diplomacy_wizard.gd")

    def test_what_moves_a_court_is_named_plainly(self):
        from backend.game_logic.diplomacy import _COMPONENT_LABELS as labels
        assert labels["base_disposition"] == "How willing they are to begin with"
        assert labels["relation_modifier"] == "Their relations with you"
        # (the review, PW2-R8: the term is the great power's BLOC pressing outward — the asker may be a
        # member of it; and the skill is the asker's envoy AGAINST theirs — against the asker it names theirs)
        assert labels["hegemony_target_mod"] == "Their fear of your side's power"
        assert labels["diplomat_skill_bonus"] == "Talleyrand's skill"
        from backend.game_logic.diplomacy import acceptance_term_label
        assert acceptance_term_label("diplomat_skill_bonus", 6) == "Talleyrand's skill"
        assert acceptance_term_label("diplomat_skill_bonus", -4) == "Their envoy's skill"
        assert labels["personality_modifier"] == "Their envoy's temper"
        for word in ("Hegemon", "bloc", "Base willingness", "Diplomat personality"):
            assert not any(word in label for label in labels.values()), word
        # ("MOST": the table lists the main things, not every term — three readers summed it against
        # Talleyrand's figure)
        assert ('const FACTORS_HEADING := "WHAT MOVES THEM MOST — each adds to, or takes from, their '
                'willingness to agree"') in self.WIZARD
        assert 'Utils.bb_table(["What weighs with them", "Effect"], factor_rows' in self.WIZARD

    def test_the_points_are_said_in_full(self):
        assert 'const DP_WORDS := "Diplomatic points (DP): %d"' in self.WIZARD
        assert self.WIZARD.count("dp_label.text = DP_WORDS % _dp_available") == 2
        assert 'dp_label.text = "DP: "' not in self.WIZARD

    def test_every_other_act_says_what_it_does(self):
        rows = [{"action": action} for action in (
            "mission_improve_relations", "mission_court", "mission_gather_intel", "declare_war",
            "send_ultimatum", "set_war_purpose", "guarantee_nation", "propose_open_borders")]
        rows.append({"action": "an_act_the_table_does_not_know"})
        out = CR.plain_rows(WorldState(), "France", "Prussia", rows)
        for row in out[:-1]:
            line = row["plain_line"]
            assert line.endswith(".") and len(line) > 30, row
            assert "group" not in row, "only the ways to end the war are grouped"
        assert "plain_line" not in out[-1]
        assert out[0]["plain_line"].startswith("Talleyrand works on their court: relations rise each turn")
        assert out[3]["plain_line"] == ("Go to war with them. Their allies may join, and Europe's alarm at "
                                        "you rises.")

    def test_a_line_says_what_the_act_does_and_no_more(self):
        """The review (PW2-R1, R2, R4): three lines promised more than the rule gives."""
        from backend.game_logic.diplomatic_dialogue import MISSION_EFFECTS
        from backend.game_logic.instruments import GUARANTEE_GRACE_TURNS
        rows = [{"action": action} for action in ("send_ultimatum", "guarantee_nation", "mission_gather_intel")]
        ultimatum, guarantee, intel = [r["plain_line"] for r in CR.plain_rows(WorldState(), "France", "Prussia", rows)]
        # a refused ultimatum starts no war: it gives the cause for one (`campaign_log`: "casus belli granted")
        assert "or refuse, which gives you a just cause for war" in ultimatum and "the war begins" not in ultimatum
        # nothing is automatic: the player has the grace to join, or the pledge is abandoned
        assert f"you have {GUARANTEE_GRACE_TURNS} turns to join that war" in guarantee
        assert "is at war with you" not in guarantee
        # the provinces the court holds when the mission ends, for the grant's five turns
        wait = MISSION_EFFECTS["GATHER_INTEL"]["duration"]
        assert intel == f"Send agents: after {wait} turns you see everything in the provinces they hold then, for 5 turns."
        src = (REPO / "backend" / "game_logic" / "diplomacy.py").read_text(encoding="utf-8")
        assert "grant_expiry = int(world.current_turn) + 5" in src, "the line's five turns are the grant's"
        assert "{" not in ultimatum + guarantee + intel, "every figure is filled from its own constant"

    def test_a_truce_becomes_a_peace_or_the_war_starts_again(self):
        """The review (PW2-R3): `armistice_expiry_exit` — the dictated peace, the courted peace, or the war
        resumes. No peace "still has to be signed before the truce runs out"."""
        from backend.game_logic.diplomacy import ARMISTICE_DURATION
        world = WorldState()
        world.diplomatic_states[world._make_diplo_key("France", "Austria")] = "WAR"
        row = CR.plain_rows(world, "France", "Austria", [{"action": "propose_armistice"}])[0]
        assert row["plain_name"] == "Ask for a truce"
        assert row["plain_line"] == (
            f"If they agree, the fighting stops for {ARMISTICE_DURATION} turns. When the truce runs out it "
            "becomes a peace if relations have mended enough — or if the loser is badly beaten with no help "
            "coming. If not, the war starts again.")

    def test_an_act_that_ends_the_war_always_wears_its_line_another_only_on_the_page(self):
        button = _func(self.WIZARD, "_add_action_button")
        assert ('var _wears_its_line: bool = str(action.get("group", "")) == "peace" or not '
                'Utils.explanations_folded()') in button
        assert 'if plain_line != "" and (Utils.compact_view() or not _wears_its_line):' in button

    def test_the_counsel_names_the_acts_as_their_buttons_read(self):
        counsel = _func(self.WIZARD, "plain_counsel")
        # (the review, PW2-R14) the names are the PAGE's own rows': the name a row wore -> the name it wears
        assert 'var plain := str((row as Dictionary).get("plain_name", ""))' in counsel
        assert 'var old := str((row as Dictionary).get("display_name", ""))' in counsel
        assert "renamed.sort_custom(func(a, b): return str(a[0]).length() > str(b[0]).length())" in counsel, (
            "the longer old name is replaced first")
        assert "out = out.replace(str(trio[0]), str(worn.get(str(trio[1]), words)))" in counsel, (
            "an act's row on this page names it — the separate peace's row reads \"Leave this war — …\"")
        assert 'RegEx.create_from_string("Open Settlement with (.+?) alone")' in counsel
        assert 'out = alone.sub(out, "Make peace — choose the terms — with $1 alone", true)' in counsel
        for old, act, new in (("Propose White Peace", "propose_white_peace", "Make peace with no terms"),
                              ("Propose Armistice", "propose_armistice", "Ask for a truce"),
                              ("Propose Peace", "propose_peace", "Offer peace to %s alone"),
                              ("Open Settlement", "", "Make peace — choose the terms")):
            assert f'["{old}", "{act}", "{new}"]' in self.WIZARD
        for old, new in (("The whole table", "Peace with all of them"),
                         ("the whole table", "peace with all of them")):
            assert f'["{old}", "{new}"]' in self.WIZARD, "a phrase in the counsel's sentences, in both cases"
        # the longer phrase is replaced first: "Propose White Peace" never becomes "Offer peace … White"
        acts = self.WIZARD[self.WIZARD.index("const COUNSEL_ACTS := ["):]
        assert acts.index('"Propose White Peace"') < acts.index('["Propose Peace"') < acts.index('["Open Settlement"')
        assert "(choose the terms)" not in self.WIZARD, "the button reads \"— choose the terms\""
        assert ('Utils.display_nation_name(str(data.get("nation", ""))), counsel_rows if counsel_rows is Array '
                'else [])') in self.WIZARD
        # the names the rows wear are the backend's own (`cabinet_rows.plain_rows`)
        world = WorldState()
        world.diplomatic_states[world._make_diplo_key("France", "Austria")] = "WAR"
        rows = CR.plain_rows(world, "France", "Austria", [
            {"action": "propose_peace", "display_name": "Propose Peace"},
            {"action": "propose_peace", "display_name": "Propose Separate Peace"},
            {"action": "open_settlement", "display_name": "Open Settlement with Austria alone",
             "addresses": ["Austria"], "addresses_display": "with Austria alone"}])
        assert rows[0]["plain_name"] == "Offer peace to Austria alone"
        assert rows[1]["plain_name"] == "Leave this war — peace with Austria alone"
        assert rows[2]["plain_name"] == "Make peace — choose the terms — with Austria alone"
        # the backend's own road names stand (every rule and pin reads them)
        from backend.game_logic.counsel import ROAD_LABELS
        assert ROAD_LABELS["send_peace"] == "Propose Peace"

    def test_the_lists_cue_keeps_its_row(self):
        cue = _func(self.WIZARD, "_update_more_below")
        assert "if not Utils.compact_view():" in cue
        assert "_more_below_keep_row()" in cue
        assert '_more_below.text = MORE_BELOW_WORDS if more else ""' in cue
        assert "_more_below.visible = more" in cue, "the short view keeps the old rule"
        # (the review, PW2-R15) the row's height is read from its own words EACH time — a Text size changed
        # in Settings is followed — and a page build keeps the row, without words
        keep = _func(self.WIZARD, "_more_below_keep_row")
        assert "_more_below.custom_minimum_size.y = _more_below.get_combined_minimum_size().y" in keep
        assert "_more_below_row" not in self.WIZARD.replace("_more_below_keep_row", "")
        clear = _func(self.WIZARD, "_clear_content_list")
        assert "if Utils.compact_view():" in clear and "_more_below_keep_row()" in clear


# ═════════════════════════════════════════════════════════════════════════════
# The peace table's last faces
# ═════════════════════════════════════════════════════════════════════════════

class TestThePeaceTableSaysWhoPaysWhom:
    POPUP = _src(SCRIPTS / "proposal_confirm_popup.gd")

    def test_a_gold_move_names_the_payer(self):
        from backend.game_logic.settlement_actions import _dial_face
        world = WorldState()
        scope = ["Austria", "Britain", "Russia"]
        paid = [{"type": "peace"}] + [
            {"type": "gold_indemnity", "from": "France", "to": c, "amount": 200} for c in scope]
        less = [{"type": "peace"}] + [
            {"type": "gold_indemnity", "from": "France", "to": c, "amount": 100} for c in scope]
        assert _dial_face(world, paid, less, proposer_leader="France", scope_courts=scope) == (
            "you pay each court 100 less gold")
        owed = [{"type": "peace"}, {"type": "gold_indemnity", "from": "Austria", "to": "France", "amount": 300}]
        more = [{"type": "peace"}, {"type": "gold_indemnity", "from": "Austria", "to": "France", "amount": 400}]
        assert _dial_face(world, owed, more, proposer_leader="France", scope_courts=["Austria"]) == (
            "Austria pays you 100 more gold")
        assert _dial_face(world, more, owed, proposer_leader="France", scope_courts=["Austria"]) == (
            "Austria pays you 100 less gold")
        assert _dial_face(world, [{"type": "peace"}], owed, proposer_leader="France",
                          scope_courts=["Austria"]) == "Austria pays you 300 more gold"

    def test_an_ally_who_leads_the_side_is_named_never_called_you(self):
        """The review (PW2-R5): the side's leader is not always the player."""
        from backend.game_logic.settlement_actions import _dial_face, _term_words
        world = WorldState()
        assert world.player_nation == "France"
        paid = [{"type": "gold_indemnity", "from": "Spain", "to": "Britain", "amount": 200}]
        less = [{"type": "gold_indemnity", "from": "Spain", "to": "Britain", "amount": 100}]
        assert _dial_face(world, paid, less, proposer_leader="Spain", scope_courts=["Britain"]) == (
            "Spain pays Britain 100 less gold")
        owed = [{"type": "gold_indemnity", "from": "Britain", "to": "Spain", "amount": 300}]
        more = [{"type": "gold_indemnity", "from": "Britain", "to": "Spain", "amount": 400}]
        assert _dial_face(world, owed, more, proposer_leader="Spain", scope_courts=["Britain"]) == (
            "Britain pays Spain 100 more gold")
        asked = [{"type": "territory_cede", "from": "Britain", "to": "Spain", "region": "Gibraltar"}]
        assert _dial_face(world, asked, [], proposer_leader="Spain", scope_courts=["Britain"]) == (
            "drops Spain's demand for Gibraltar")
        assert _term_words(world, paid[0], "Spain") == "gold Spain pays Britain"
        assert _term_words(world, owed[0], "Spain") == "gold Britain pays Spain"
        assert _term_words(world, {"type": "gold_per_turn", "from": "Spain", "to": "Britain"}, "Spain") == (
            "gold a turn Spain pays Britain")
        # the player's own table reads as it did
        assert _term_words(world, {"type": "gold_lump", "from": "France", "to": "Britain"}, "France") == (
            "gold you pay Britain")

    def test_the_review_wears_what_it_will_find(self):
        assert 'const REVIEW_WILL_SIGN := "they would all sign"' in self.POPUP
        assert 'const REVIEW_WILL_NOT_SIGN := "they will not sign it yet"' in self.POPUP
        show = _func(self.POPUP, "show_dialogue")
        assert 'if str(opt.get("action", "")) == "submit_settlement_for_review" and not Utils.compact_view():' in show
        assert ('(REVIEW_WILL_SIGN if bool(data.get("can_ratify", true)) else REVIEW_WILL_NOT_SIGN)') in show

    def test_the_peace_cards_two_labels(self):
        assert '"[b]Each court\'s peace[/b]", "What kind of peace each court would sign."' in self.POPUP
        assert '"[b]Yours by this treaty[/b]"' in self.POPUP
        assert "[b]Manner[/b]" not in self.POPUP and "[b]Titled[/b]" not in self.POPUP


# ═════════════════════════════════════════════════════════════════════════════
# A marshal's objection
# ═════════════════════════════════════════════════════════════════════════════

class TestAnObjectionSaysWhatEachAnswerDoes:
    DIALOG = _src(SCRIPTS / "objection_dialog.gd")

    def test_each_answer_says_what_it_does_under_its_name(self):
        for key, words in (("trust", "he does this instead"), ("insist", "he obeys your order"),
                           ("word", "he obeys · no trust lost"),
                           ("compromise", "a middle course"), ("cancel", "nothing happens")):
            assert f'"{key}": "{words}"' in self.DIALOG
            # (the part's own blind reading: a longer note ran past its cell and was cut at both ends)
            assert len(words) <= 24, words
        caption = _func(self.DIALOG, "_set_caption")
        assert "var does: String = _does_note(btn)" in caption
        assert 'if text != "" and does != "":' in caption, "an answer with no figures wears no note"
        # (the review, PW2-R12) an objection that carries no other order of his has no "this" to do instead
        note = _func(self.DIALOG, "_does_note")
        assert 'return ANSWER_DOES["trust"] if has_alternative else ""' in note
        strategic = _func(self.DIALOG, "_setup_strategic_buttons")
        assert strategic.index("has_alternative = true") < strategic.index(
            "_set_caption(trust_button, _caption_text(int(ap), int(trust)))"), "the note reads it: set first"
        # the answers keep their names: every road and pin reads them
        for face in ('"Proceed as Ordered"', '"By My Word"', '"Cancel the Order"'):
            assert face in self.DIALOG

    def test_a_price_is_in_actions_never_ap(self):
        figures = _func(self.DIALOG, "_caption_text")
        assert 'Utils.plural(ap, "action")' in figures and "%d AP" not in figures
        # (the review, PW2-R13) nor on an answer's face On the page: six faces, none says "AP"
        assert "%d AP" not in self.DIALOG
        assert self.DIALOG.count('"%s — %s, %+d trust" % [') == 3, "trust, insist, compromise"
        assert self.DIALOG.count('"%s, %+d trust" % [Utils.plural(int(ap), "action"), trust]') == 3, (
            "a strategic objection's three")
        assert "nothing spent" in self.DIALOG and "no AP, no trust spent" not in self.DIALOG

    def test_the_stakes_are_plain_sentences(self):
        from backend.game_logic import standing
        line = standing.insist_stake_line()
        assert line.startswith("Later, when the battle is fought — if you insisted and it is lost: "
                               "trust −5, authority −5;")
        assert "If you compromised:" in line and "under your insistence" not in line


# ═════════════════════════════════════════════════════════════════════════════
# A letter that arrives
# ═════════════════════════════════════════════════════════════════════════════

class TestALetterSaysItselfInThreeLines:
    def test_what_they_ask_and_what_each_answer_does(self):
        short = MP.letter_in_short({"type": "open_borders"}, "Prussia")
        assert short == {
            "ask": "Prussia asks: each side's armies may cross the other's land.",
            "accept": "Accept — it is signed at once.",
            "reject": "Reject — nothing is signed. Their court remembers the refusal.",
        }
        peace = MP.letter_in_short({"type": "peace"}, "the Ottoman Empire")
        assert peace["ask"].startswith("The Ottoman Empire asks: an end to the war between you")
        assert peace["accept"] == "Accept — the war with them ends on these terms."
        # (the review, PW2-R3: a truce becomes a peace at its end, or the war starts again)
        from backend.game_logic.diplomacy import ARMISTICE_DURATION
        truce = MP.letter_in_short({"type": "armistice_losing"}, "Austria")
        assert truce["ask"] == (f"Austria asks: a truce — the fighting stops for {ARMISTICE_DURATION} turns, "
                                "but the war is not over.")
        # one line, pointing at the letter's own expiry lines right below it: PC-F46 keeps "When it expires"
        # and "At expiry" above the fold on the first player's panel, and a longer line here pushed them under
        # (found by the suite's own driven pin, `test_uxr4_s15_pc_layout.py::TestPCF46`, at 5120 x 1440: three
        # lines here pushed "At expiry" under the fold — the truce's two answers stand on ONE line)
        assert truce["accept"] == (
            "Accept — the fighting stops at once (how it ends is written below). Reject — the war goes on.")
        assert truce["reject"] == "" and "must still be signed" not in truce["accept"]
        # a letter that would end a war, refused, leaves the war on
        assert MP.letter_in_short({"type": "peace"}, "Austria")["reject"] == (
            "Reject — the war goes on. Their court remembers the refusal.")

    def test_a_letter_with_its_own_register_says_its_own(self, monkeypatch):
        assert MP.letter_in_short({"type": "open_borders"}, "Prussia", is_counter_offer=True) == {}
        assert MP.letter_in_short({"type": "peace"}, "Austria", label_type="harsh_peace") == {}
        assert MP.letter_in_short({"type": "a_kind_the_table_does_not_know"}, "Austria") == {}
        monkeypatch.setattr(MP, "the_letter_says_itself_plainly", lambda: False)
        assert MP.letter_in_short({"type": "open_borders"}, "Prussia") == {}

    def test_the_popup_prints_it_above_the_treatys_own_words(self):
        popup = _src(SCRIPTS / "incoming_proposal_popup.gd")
        show = _func(popup, "show_proposal")
        assert show.index("bbcode += _in_short_block(data)") < show.index('bbcode += "[b]Proposes:[/b] %s\\n"')
        block = _func(popup, "_in_short_block")
        assert "[b]IN SHORT[/b]" in block and 'for key in ["accept", "reject"]:' in block
        notice = _src(SCRIPTS / "notification_bar.gd")
        assert "The letter waits in Envoys (top bar) — open it there to answer." in notice
        assert "diplomatic packet" not in notice


# ═════════════════════════════════════════════════════════════════════════════
# The war card, the first morning, the log's small lines
# ═════════════════════════════════════════════════════════════════════════════

class TestTheSmallLines:
    MAIN = _src(SCRIPTS / "main.gd")

    def test_the_war_card_says_its_word_of_the_war(self):
        panel = _src(SCRIPTS / "war_status_panel.gd")
        assert 'const WAR_STANDS := "The war: %s"' in panel
        assert "standing_label.text = WAR_STANDS % war_standing_word(score).to_lower()" in panel

    def test_the_first_morning_says_what_to_do_with_the_map(self):
        from backend.game_logic import dispatch
        assert dispatch.WHAT_NOW_LINE.startswith("What now: click a marshal, then click a province to send him")
        assert "press Make peace on its card at the top right" in dispatch.WHAT_NOW_LINE
        today = dispatch._build_first_morning_doors(WorldState(), "France")
        assert today["what_now"] == dispatch.WHAT_NOW_LINE
        shown = _func(self.MAIN, "_display_morning_dispatch")
        assert shown.index('var what_now = str(today.get("what_now", ""))') < shown.index(
            'var today_orders = today.get("orders", [])'), "said first, under TODAY"

    def test_the_logs_echoes_are_plain_and_said_once(self):
        assert "Peace talks: opening the table with %s" in self.MAIN
        assert "Opening settlement review for" not in self.MAIN
        assert "Opening the record of the peace with %s" in self.MAIN
        result = _func(self.MAIN, "_on_command_result")
        assert "if _said_notices.has(notice_text):" in result, "the same sentence is said once"

    def test_a_dropped_draft_is_said_plainly(self):
        world_src = (REPO / "backend" / "models" / "world_state.py").read_text(encoding="utf-8")
        assert 'f"Your unsigned peace draft with "' in world_src
        assert "unratified settlement draft with" not in world_src.replace(
            '(row PW part 2, plain words: "unratified settlement', "")
        offers = (REPO / "backend" / "game_logic" / "settlement_offers.py").read_text(encoding="utf-8")
        assert "'s request for {claim} lapsed with the \"" in offers.replace("\n", "") or \
            "request for {claim} lapsed with the " in offers
        assert "petition over {claim} lapses" not in offers

    def test_the_reports_link_says_where_it_goes(self):
        dialog = _src(SCRIPTS / "enemy_phase_dialog.gd")
        assert "]⌖ show on the map[/url]" in dialog
        waited = (REPO / "backend" / "game_logic" / "while_you_waited.py").read_text(encoding="utf-8")
        assert "no winner yet: the battle waits for your orders this turn" in waited


# ═════════════════════════════════════════════════════════════════════════════
# "AP" says what it is where the player meets it (the held-again blind reading)
# ═════════════════════════════════════════════════════════════════════════════

class TestThePriceTagsSayActions:
    """Two measurements beside the reading's bar: three readers of three read the general's card right only
    by inference, and "AP is never defined" stood on all three lists. The key stays (251 pins read it); the
    plain words ride beside it (golden rule 11). The vocabulary's retirement, the row PW2-D1, is CLOSED
    (November 19, 2026): every price tag now says "action(s)" (`TestPW2D1NoPriceTagSaysAP`)."""

    def test_the_generals_card_says_actions_left(self):
        card = _src(SCRIPTS / "selection_card.gd")
        figures = _func(card, "_figures_bbcode")
        assert ('var left := (str(_actions_left) + " left") if compact else '
                '(Utils.plural(_actions_left, "action") + " left")') in figures
        assert 'col.add_child(_measured_rich("Figures", _figures_bbcode(compact), 0.0))' in card

    def test_an_order_buttons_hover_says_its_two_numbers(self):
        """Four readers of four read "1 Hold · 2" right, and only by inference: the leading number (its
        key) and the trailing one (its price) are never labelled. The face keeps its room; the hover says
        them."""
        card = _src(SCRIPTS / "selection_card.gd")
        words = _func(card, "slot_words")
        assert 'out += " — free"' in words and 'out += " — costs " + Utils.plural(price, "action")' in words
        assert 'return out + " · key " + str(slot)' in words
        button = _func(card, "_slot_button")
        assert 'tip = slot_words(label, int(spec["price"]), slot)' in button
        assert button.index('tip = slot_words(') < button.index("var locked := bool(spec[\"locked\"])"), (
            "a locked order's reason follows its words")

    def test_the_province_panel_says_what_is_left_once(self):
        panel = _src(SCRIPTS / "region_panel.gd")
        assert "const AP_WORDS" not in panel and "_ap_words(" not in panel, "the AP gloss is retired (PW2-D1)"
        words = _func(panel, "_actions_left_words")
        assert ('if not (flat.contains(" action)") or flat.contains(" actions)")\n'
                '\t\t\tor flat.contains(" action \u00b7") or flat.contains(" actions \u00b7")):') in words, (
            "said only where a price tag is on the panel")
        assert 'var flat := shown.replace("\\u00a0", " ")' in words, "a chip binds its spaces (UXR3-83)"
        assert 'var left := int((_map_node.action_pools as Dictionary).get("military", 0))' in words
        assert '"]You have " + Utils.plural(left, "action") + " left this turn[/color]' in words
        # once: right under the forces' rows where they carry a tag, else under the march-here orders
        assert "var ap_under_forces := _actions_left_words(bbcode.substr(forces_from))" in panel
        assert "if not ap_said:\n\t\t\tbbcode += _actions_left_words(march)" in panel
        assert panel.count("_actions_left_words(") == 3, "its definition and its two places"

    def test_the_commission_line_says_an_admin_action(self):
        roster = _src(SCRIPTS / "marshal_management.gd")
        assert "(1 admin action + the candidate's price)" in roster and "1 admin AP" not in roster


# ═════════════════════════════════════════════════════════════════════════════
# The battle's dice lines, and who won
# ═════════════════════════════════════════════════════════════════════════════

class TestTheBattlesDiceAsSentences:
    ACTS = _src(SCRIPTS / "battle_acts.gd")

    def test_what_the_roll_did_is_a_sentence(self):
        lands = _func(self.ACTS, "plain_lands")
        assert "var diff: int = hits - average" in lands
        assert 'return "a strong roll: the attack hits %d%% harder than an average one" % diff' in lands
        assert 'return "a weak roll: the attack hits %d%% weaker than an average one" % -diff' in lands
        assert 'return "an average roll: the attack hits as hard as usual"' in lands
        assert "if diff >= 3:" in lands and "if diff <= -3:" in lands

    def test_the_days_luck_is_said_side_by_side(self):
        luck = _func(self.ACTS, "plain_luck")
        # (the review, PW2-R16: the row names two sides — the second goes without the verb, and the row is
        # no longer than the plate's others: "France fights 4% weaker · Austria 2% stronger")
        assert 'var verb := "fights " if fights else ""' in luck
        for words in ('"%s %s%d%% stronger" % [side, verb, pct]', '"%s %s%d%% weaker" % [side, verb, -pct]',
                      '"%s %sas usual" % [side, verb]'):
            assert words in luck
        line = _func(self.ACTS, "_luck_line")
        assert 'return "today\'s luck: %s · %s" % [' in line
        assert 'int(roll.get(right_key, 0)), false)]' in line, "the second side goes without the verb"
        assert "return _luck_told_plain(roll)" in line, (
            "under a verdict's cause the row says the roll's share and the luck's, and does not repeat the cause")
        told = _func(self.ACTS, "_luck_told_plain")
        assert 'return "the roll added %s to the attack · today\'s luck: %s for %s" % [' in told
        assert 'if not (str(host._data.get("player_side", "")) in ["attacker", "defender"]):' in told, (
            "a battle the player only watches names the side, never \"you\"")
        short = _func(self.ACTS, "_luck_short")
        assert "return _luck_told_plain(roll)" in short, "the short form (Text size 120 % and up) is plain too"

    def test_the_chips_row_says_what_the_corps_does(self):
        assert '"lead": "Send another corps to attack"' in self.ACTS

    def test_who_won_leads_the_cause(self):
        class Ctx:
            marshal = type("M", (), {"name": "Ney"})()
            enemy_marshal = type("M", (), {"name": "Mack"})()
            battle_result = {"victor": "Mack", "outcome": "defender_victory"}
        assert T.plain_verdict(Ctx(), True) == "You lost."
        assert T.plain_verdict(Ctx(), False) == "You won."
        Ctx.battle_result = {"victor": "", "outcome": "stalemate"}
        assert T.plain_verdict(Ctx(), True) == "No winner."
        Ctx.battle_result = {}
        assert T.plain_verdict(Ctx(), True) == ""
        day = (REPO / "backend" / "game_logic" / "battle_day.py").read_text(encoding="utf-8")
        assert 'return (f"{said} " if said else "") + f"Why: {why[0]}."' in day


# ═════════════════════════════════════════════════════════════════════════════
# PW2-D1 — CLOSED (November 19, 2026): no price a player acts on says "AP"
# ═════════════════════════════════════════════════════════════════════════════

def _code_of(line: str) -> str:
    """A GDScript line without its trailing comment (a '#' inside a string is no comment)."""
    quoted = False
    for at, char in enumerate(line):
        if char == '"' and (at == 0 or line[at - 1] != "\\"):
            quoted = not quoted
        elif char == "#" and not quoted:
            return line[:at]
    return line


def _ap_tags() -> list:
    """Every string literal of the client that prints an "AP" price tag — comments and docstrings aside;
    Help's own entry ("Action points (AP)") and the panel's "AP = actions" are the words beside the key."""
    found = []
    for path in sorted(SCRIPTS.glob("*.gd")) + sorted((SCRIPTS.parent / "scenes").glob("*.gd")):
        if path.name == "codex_terms.gd":
            continue
        source = re.sub(r'"""(?:.|\n)*?"""', "", _src(path))
        for line in source.splitlines():
            for literal in re.findall(r'"((?:[^"\\]|\\.)*)"', _code_of(line)):
                if re.search(r"(?<![A-Za-z])AP(?![A-Za-z])", literal) and "AP = actions" not in literal:
                    found.append(f"{path.name}: {literal}")
    return found


class TestPW2D1NoPriceTagSaysAP:
    def test_the_census_still_reads_a_tag_when_one_is_present(self):
        """The census's regex must keep seeing a price tag that says "AP" - else a clean census is blind."""
        for sample in (" AP)", " (2 AP)", "Hold (2 AP)", "Bernadotte · 1 AP", "1 Admin AP"):
            assert re.search(r"(?<![A-Za-z])AP(?![A-Za-z])", sample), sample
        assert not re.search(r"(?<![A-Za-z])AP(?![A-Za-z])", "Hold (2 actions)")

    def test_no_price_tag_says_ap(self):
        assert _ap_tags() == []
