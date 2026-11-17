"""Row BA, session BA-5 — "the finish" (November 16–17, 2026): the session's
seams, held DOWN.

Every change of the session sits behind a named zero-argument FUNCTION in the
module it gates (`tools/playtest_driver.py --seam MODULE:NAME=EXPR`; no
levers). This list is the session OFF: with every row down the game, the
table and the record are the commit before (`1b5bc533`), and a board recorded
before the session replays under the rules it was recorded under
(`tests/_oct27_seams.py` folds these rows in, as it folds BA-4's).

    D1        `battle_day.our_table_reads_the_day_as_our_clash_left_it` — when
              his clash follows ours on the table, our clash's tableau carries
              the day as it stood before he answered; down: the day after his
              answer (his purse a point short, his word told, his clash's
              result under the title — before "His answer" was pressed).

    TELL      the rows that move no number of the game, together — the arm
              that must read exactly as the arm before it in every number:
              `battle_telling.the_day_tells_its_clashes` (under the title the
              day's own toll; one line a clash, with what told),
              `battle_telling.a_word_says_what_it_does` (every chip carries
              its consequence), `battle_telling.the_table_reads_him`
              (Berthier's reading of his next word, three states),
              `battle_telling.the_close_names_what_told` (the close says whom
              the toll favoured, what told, what kind of day it was) and
              `battle_telling.a_verdict_names_what_told` (a battle's own
              table says under its headline what told; the clash that decides
              a day names itself) — and Berthier's own line for it:
              `battle_report.a_rout_won_on_points_has_left_the_field` (an
              enemy a clash won on points drove from the field is not "still
              in the field").

    FIRST     `battle_day.the_first_days_line_stands_on_its_first_table` — the
              first day's own line (BA-4) stays on the table that showed it:
              once the client has drawn it (`POST /first_open`) each open day
              is marked as it stood, and a later table of the day does not
              say it again; down: on every table of the turn (a day is fought
              inside one turn: every table of a campaign's first day carried
              it).

    TRUCE     `diplomacy.a_truce_names_the_ground_it_would_title` — ruling 1:
              a truce whose forecast ends in a signed peace names the
              provinces that signature would title; down: the heading as it
              was ("what each side holds is titled by the signature").

    RESERVE   `battle_day.the_reserve_pursues` — the rule the user ticked
              ("Build it; the rule picks"): when a clash decides a day the
              victor's unspent points, less the loser's, each cost the beaten
              lead `battle_day.reserve_pursuit()` men more. **PARKED: it is
              DOWN in the game** (`BA5_PARKED`) — the rule written before its
              data picked none of its three values (of the men it took, about
              nine in ten were ours). Up is the measured arm
              (`tools/_ba5_measure.py`, arms R<n>); this row keeps it down on
              a replayed board whatever the tree says.

    NEWS      `battle_news.a_great_battle_names_its_commanders` - ruling 5 as
              the user's tick changed it ("Name the commanders"): the news of a
              GREAT battle abroad names its two commanders, a great assault the
              man who led it; down: crowns only, as BA-4 had it. Never a figure
              either way.

    DAYS      `battle_day.a_marshal_keeps_his_days` - the user's tick ("A
              marshal's days"): a pitched battle our marshal led is kept on his
              own record (`Marshal.days`, the last six) for his card on the
              Generals screen; no rule of the game reads it. Down: nothing is
              kept and a save is as it was.

    ONEDAY    `battle_day.a_lead_holds_his_day_as_the_battle_began` - BA5-X1,
              found by pressing ruling 9's card in the real client: "one day a
              lead" is read as the lead stood when the battle began (his own
              advance from a second clash had made his first day read dead, and
              the second battle then opened a day its card had promised it
              would not); the card says what winning it does to the first day,
              and that day's close says he marched from it. Down: BA-4's
              reading.

    GROUND    `battle_diorama.the_table_shows_its_ground` - the user's tick
              ("The ground on the table"): a tableau's payload carries the
              terrain of its province and the table draws it on the felt
              under the men. Down: no such key, a bare felt.

    ROUT      `battle_script.a_rout_is_one_this_battle_made` - the session's
              review (a defect older than the row): a corps is told as
              breaking only where THIS battle drove it off; one that had
              retreated earlier in the turn and then held was told "his line
              breaks". Down: the turn's retreat flag alone. Moves no number.

    OWNWAY    `battle_day.a_words_battle_is_its_own_clash` - the session's
              review: the running word is the battle only where it is fought
              against the day's enemy (or, his word, the day's lead); an
              objection answered "his own way" against another corps fights a
              battle of its own — no clash of the day, no Guard's shock on that
              corps, no reserve counted. Down: every battle fought while a
              word runs is the word's. It can move a number on that one road.
"""

BA5_SEAMS_BY_ROW = {
    "D1": [
        "backend.game_logic.battle_day:our_table_reads_the_day_as_our_clash_left_it=False",
    ],
    "TELL": [
        "backend.game_logic.battle_telling:the_day_tells_its_clashes=False",
        "backend.game_logic.battle_telling:a_word_says_what_it_does=False",
        "backend.game_logic.battle_telling:the_table_reads_him=False",
        "backend.game_logic.battle_telling:the_close_names_what_told=False",
        "backend.game_logic.battle_telling:a_verdict_names_what_told=False",
        "backend.game_logic.battle_report:a_rout_won_on_points_has_left_the_field=False",
    ],
    "FIRST": [
        "backend.game_logic.battle_day:the_first_days_line_stands_on_its_first_table=False",
    ],
    "TRUCE": [
        "backend.game_logic.diplomacy:a_truce_names_the_ground_it_would_title=False",
    ],
    "RESERVE": [
        "backend.game_logic.battle_day:the_reserve_pursues=False",
    ],
    "NEWS": [
        "backend.game_logic.battle_news:a_great_battle_names_its_commanders=False",
    ],
    "DAYS": [
        "backend.game_logic.battle_day:a_marshal_keeps_his_days=False",
    ],
    "ONEDAY": [
        "backend.game_logic.battle_day:a_lead_holds_his_day_as_the_battle_began=False",
    ],
    "GROUND": [
        "backend.game_logic.battle_diorama:the_table_shows_its_ground=False",
    ],
    "ROUT": [
        "backend.game_logic.battle_script:a_rout_is_one_this_battle_made=False",
    ],
    "OWNWAY": [
        "backend.game_logic.battle_day:a_words_battle_is_its_own_clash=False",
    ],
}

BA5_SEAMS_DOWN = [spec for row in BA5_SEAMS_BY_ROW for spec in BA5_SEAMS_BY_ROW[row]]

# Seams of the session that are DOWN in the game as shipped: built, measured, and
# not armed (the reserve failed its own rule; `BATTLE_DIORAMA_SPEC.md` §15.23).
BA5_PARKED = ["backend.game_logic.battle_day:the_reserve_pursues"]
