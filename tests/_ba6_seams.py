"""Row BA, session BA-6 — "the last word" — and row MC — "Mon Cousin", the
Order of the Marshalate (November 17, 2026): the session's seams, held DOWN.

Every change of the session sits behind a named zero-argument FUNCTION in the
module it gates (`tools/playtest_driver.py --seam MODULE:NAME=EXPR`; no
levers). This list is the session OFF: with every row down the game, the
table and the record are the commit before (`fdd4756f`), and a board recorded
before the session replays under the rules it was recorded under
(`tests/_oct27_seams.py` folds these rows in, as it folds BA-5's).

    TELL      BA-6's rows that move no number of the game: BA5-X16 (a defeat
              that cost a fifth of the corps is not called narrow), BA5-X17 (a
              card's men of ours are men in reach), BA6-X1 (a day decided for
              neither is kept as drawn), the levers' risk and stakes (every
              word says what it risks; the free words their stakes), GRD-17's
              objection voices (each aggressive marshal in his own words),
              GRD-2 (a declaration of war rides the morning always), GRD-5
              (an envoy's letter names its kind on the rail), GRD-30 (a
              recruit-morale law says a training ground voids it); the
              review's BA6-R6 (a defiance names the order in words) and
              BA6-R8 (a bond's move is told only of the player's court).

    RESERVE6  `battle_day.the_attacker_pursues` — the reserve in the form
              BA-5's data pointed to (only the side that attacked in the
              deciding clash pursues, with its own unspent points). Down: no
              pursuit for a point kept. CLOSED: it failed the rule written
              before its data (`tools/_ba6_reserve_rule_2026_11_17.json`,
              pick null — 22 of 23 pursuits fell on a French corps), so it
              stays DOWN in the game (`BA6_CLOSED`); up is the measured arm.

    MC0       `marshal.the_bond_writes_the_stored_view` — R0: the relationship
              writer reads and writes the STORED view.

    MCBOOK    the book of incidents (with its causes on every surface), the
              banked renown, the order of precedence (and the captives kept in
              it), an audience naming its cause and its quiet answer saying
              what follows (GRD-17), the attack card naming the court
              beforehand — what the court SAYS and remembers.

    MCSEEDS   `precedence.the_seeds_read_as_of_1805` — three enmities read as
              they stood in 1805 (Rivals, -1; down: Hostile, -2).

    MCBONDS   the two-way bonds: brothers in arms, the shared defeat, the
              rescue, the silence, an old quarrel cooling, serving under a
              junior.

    MCRANK    the titles of victory (the player's and the courts'), the claim,
              the account.

    PEACE     BA-5's ruling 1, built as it pre-decided once the ambient
              annexation line read above 0 (BA6-X8): T3-6's law of peace
              reaches a third court's ground (a province the holder took from
              the ceder outside what it may keep goes back to the ceder).

    SILENCE   `precedence.a_silence_is_remembered_when_pressed` — the court
              count's find: the Auerstedt rule reads its own namesake (a Hostile
              comrade's silence is remembered when the lead was hard pressed,
              won or not). Last on the ladder, so every arm before it reads as
              the measure before the build read it.

    GRD       the design rows ruled under the delegation that move a number:
              GRD-31 (a cautious marshal who defies a pursuit fortifies).
              (GRD-17's voices and GRD-2's public declarations are TELL's.)

    WS        the weak-spot review's two battle-pipeline rows: WS-13 (the odds
              of a battle are the men each side put on the field) and WS-15 (an
              attack that struck no blow puts back the drill, the
              counter-punch and the square, on every road).
"""
from __future__ import annotations

BD = "backend.game_logic.battle_day"
BT = "backend.game_logic.battle_telling"
P = "backend.game_logic.precedence"

BA6_SEAMS_BY_ROW = {
    "TELL": [
        "backend.game_logic.battle_report:a_dear_defeat_is_not_a_narrow_one=False",
        "backend.commands.order_quotes:a_cards_men_are_men_in_reach=False",
        f"{BD}:a_ruin_is_kept_as_drawn=False",
        f"{BT}:a_word_says_what_it_risks=False",
        "backend.commands.strategic_executor:each_aggressive_man_objects_in_his_own_voice=False",
        "backend.game_logic.diplomacy:a_declaration_of_war_is_public=False",
        "backend.game_logic.ai_diplomacy:an_envoy_names_his_letter=False",
        "backend.game_logic.reforms:a_law_says_where_it_is_void=False",
        "backend.commands.strategic_executor:a_defiance_names_the_order_in_words=False",
        "backend.campaign_log:a_bond_is_told_only_of_our_court=False",
    ],
    "RESERVE6": [f"{BD}:the_attacker_pursues=False"],
    "MC0": ["backend.models.marshal:the_bond_writes_the_stored_view=False"],
    "MCBOOK": [
        f"{P}:the_book_keeps_its_incidents=False",
        f"{P}:a_marshal_banks_his_renown=False",
        f"{P}:the_order_of_precedence_stands=False",
        f"{P}:an_audience_names_its_cause=False",
        f"{P}:the_card_names_the_court=False",
    ],
    "MCSEEDS": [f"{P}:the_seeds_read_as_of_1805=False"],
    "MCBONDS": [
        f"{P}:brothers_in_arms=False",
        f"{P}:a_shared_defeat_sours=False",
        f"{P}:a_rescue_mends=False",
        f"{P}:a_silence_is_remembered=False",
        f"{P}:old_quarrels_cool=False",
        f"{P}:serving_under_a_junior_rankles=False",
    ],
    "GRD": [
        "backend.commands.defiance:a_cautious_man_defies_a_pursuit_by_fortifying=False",
    ],
    "WS": [
        "backend.commands.combat_executor:outnumbered_is_read_on_the_field=False",
        "backend.commands.combat_executor:a_refused_attack_spends_nothing=False",
    ],
    "MCRANK": [
        f"{P}:titles_of_victory=False",
        f"{P}:ai_courts_confer_titles=False",
        f"{P}:a_marshal_claims_his_due=False",
        f"{P}:an_account_follows_a_joint_defeat=False",
    ],
    # last on the ladder, so the arms before it read as the session's final
    # measure read them (its chain predates the build)
    "PEACE": ["backend.game_logic.game_end:a_peace_evacuates_a_third_courts_ground=False"],
    "SILENCE": [f"{P}:a_silence_is_remembered_when_pressed=False"],
}

BA6_SEAMS_DOWN = [spec for row in BA6_SEAMS_BY_ROW for spec in BA6_SEAMS_BY_ROW[row]]

# The seam the game holds DOWN (returns False): the reserve's second form,
# closed by its rule. Every other row is UP in the game.
BA6_CLOSED = [f"{BD}:the_attacker_pursues"]
