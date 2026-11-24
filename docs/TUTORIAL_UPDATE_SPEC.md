# Row TU — the tutorial brought up to date: the design

**Status:** design written November 23, 2026, before row TU opens (it runs after Sessions FR-1 and FR-2). Nothing is
built.
**Owner:** row TU (`docs/PRE_DEPLOY_PLAN.md` §2).
**By whose word:** the user's, November 23, 2026: "update tutorial so it reflects all updates we made".
**Tracked:** `docs/STATUS.md` ▶ NEXT UP.
**Behaviour test:** `tests/test_tu_the_tutorial_brought_up_to_date.py` — strict xfails on the stale lines, each
dropped in the commit that fixes it — then the driven plays of both lessons (§9).
**Done when:** §10. **Landing record:** §13, written at the landing.

**The rule of this row:** rewrite from the CODE as it stands after FR-1 and FR-2, never from
`docs/TUTORIAL_SCRIPT.md`. The script was last updated September 23, 2026, and its header still says "Eighteen cards".

---

## §0 The one call for the user, at TU's Plan Mode

**The School hides the desk.** `backend/game_logic/today.py` (~1046–1051) returns no desk on a lesson world. It asks
`tutorial_state.is_school_world`, which covers both `tutorial` and `tutorial_table`. The comment says the tutor card
names the one thing to do next, and a second list beside it would talk over the lesson.

- **Recommended: show the desk in the School from the card that teaches it, onward.** The card and the desk say the
  same next thing, so a new player meets the desk before the campaign, where it is always on.
- **The other road:** keep it hidden and teach it in words only. This is weaker: golden rule 9 — a lesson should not
  promise what it cannot show.
- **The Table keeps its own guide** (its seven cards are doors), unless the user rules otherwise.

## §1 What there is today (read November 23, 2026)

| Surface | Where | Size |
|---|---|---|
| The School of War (the Danube) | `scripts/tutorial_overlay.gd` STEPS (~129–411); mirror `backend/game_logic/tutorial_state.py` (~21–44); scenario `assets/maps/tutorial_1805.json` | 22 cards, gates 1–14 |
| The Table (the Peace of Pressburg) | `scripts/tutorial_table_steps.gd` (~31–118); mirror `TABLE_STEPS` in `tutorial_state.py` (~53–61); scenario `assets/maps/tutorial_table_1805.json` | 7 cards, gates 1–3 |
| Help & Keys | `scripts/codex_view.gd` (KEYS / TERMS / ORDERS); its data `scripts/codex_terms.gd`; the live key table from `Keys.actions()` | 62 terms; orders 22, tasks 6, bare commands 9, questions 8, fixed keys 25 |
| The first-open lines | `backend/game_logic/first_open.py`, `SCREENS` (~42–49) | 13 lines, ≤ 220 characters |
| The main menu | `scripts/main_menu.gd` (~460–461 the rows, ~860–879 the confirms, ~992 the first-time hint) | two lesson rows |
| The script | `docs/TUTORIAL_SCRIPT.md` | 492 lines |
| Play scripts and driver | `tools/playtest_scripts/tutorial_lesson.json`, `tutorial_lesson_trust.json`, `tutorial_table_lesson.json`; `tools/tutorial_overlay_harness.gd` | — |

**How the School works:**
- Every pass check is on the client: `tutorial_overlay.gd` ~1368–1566, fed by `observe` (~821), reading the reply's
  fields.
- The backend mirror is for display only (`tutorial_step_for` ~92, marked "approximate").
- A card not yet passed is released three ways:
  - by the catch-up, when the turn is more than one past its gate (~967);
  - by a refusal of the card's own suggested order (~1016);
  - by its Skip chip.
- A chip fills the command line and sends nothing.
- Two cards carry doors: VII (`cabinet:Austria`) and XVIII (`ledger:7`).

**The School's 22 cards today:**

| # | id, gate | Teaches | Passes when (`tutorial_overlay.gd`) |
|---|---|---|---|
| I | survey, 1 | Knowledge before orders; `economy` is free | any successful reply (`_pred_any_success`) |
| II | first_move, 1 | 4 command and 2 administrative actions; a march costs one; "march then attack"; "hold until relieved" | Senarmont is in Munich |
| III | first_end_turn, 1 | The enemy moves; the dispatch; the notice rail | the turn advanced |
| IV | objection, 2 | Bold / Careful / to the letter; a marshal pushes back | an objection is pending |
| V | objection_answer, 2 | Trust, Proceed as Ordered, Compromise; trust; defiance; "a hearing" | the objection resolved |
| VI | bombardment, 2 | Artillery fires one province away, never on the day it marched | a bombardment happened |
| VII | cabinet, 3 | The Cabinet (F1), a mission, diplomatic points, the Diplomatic Ledger | a mission is running |
| VIII | first_battle, 4 | The battle report; occupy Swabia (alt arms: running, lost, taken) | a battle report or conquest |
| IX | marshalate, 5 | The muster ("what if Ney attacks Mack"), the G card, trust, glory, feuds, envy, the Reward chip | turn 5 (a reading card) |
| X | strategic_order, 5 | Standing orders, arrows on the map, the T orders book, `.` for the next idle corps | Davout is in Swabia, Munich or Franconia |
| XI | capture, 6 | Take Bohemia; capitals have garrisons | a capture choice is pending |
| XII | capture_answer, 6 | PLUNDER / SECURE | the choice answered |
| XIII | recruit_build, 7 | Recruit and build (administrative actions) | the infantry pool fell |
| XIV | free_scout, 8 | The fog; scout | turn 9 |
| XV | free_stand, 9 | Terrain, fortify, supply | turn 10 |
| XVI | naval, 10 | The Wooden Wall: the Royal Navy, shut sea links, the Admiralty book, blockade, expeditions | turn 11 |
| XVII | congress, 11 | The Congress of Paris: 45 provinces by title | turn 12 |
| XVIII | laws, 12 | The Laws of State (T, then 8), the Staff, lapse, arrears | a law was enacted |
| XIX | on_his_own, 12 | "Ney, take Swabia on your own"; "Soult, hold Lorraine. If attacked, dig in." | any successful reply |
| XX | ask_him, 12 | Free questions to a marshal | any successful reply |
| XXI | free_books, 13 | The instruments: T, G, D, R, L, N, Alt, Esc, F1, the Reward chip, Design rows, missions | turn 14 |
| XXII | handoff, 14 | The lesson ends | never (the last card) |

## §2 Stale lines — each fixed by TU

1. **Card I** (`tutorial_overlay.gd` ~134): "Every command is TYPED into the line below…". Since row IC's Session 2,
   every simple order is a button (the selection card). Typing is for tasks, exact orders and questions.
2. **Card V** (~175): "…and at the bottom he asks for a hearing you must answer". The hearing's answer is now the task
   to prove himself (`trial.py`, row IC Session 2b). The same sentence's "act by his own judgement" means defiance and
   now collides with "on his own".
3. **Card XXI** (~397) repeats the Admiralty (card XVI teaches it) and names no surface from row IC. It is pinned by
   `tests/test_hc5_tutorial_names_fleet.py` and `tests/test_iq4_cabinet_visible.py`, which move with it.
4. **Cards XIX and XX** pass on any successful reply (`_pred_any_success`). Nothing checks that a task or a question
   was sent.
5. **The Table's cards against the live table:**

   | The card says (`tutorial_table_steps.gd`) | The live table says |
   |---|---|
   | II: "Austria's reads WILL SIGN"; "Russia holds out" (~47) | "Will sign"; "Will not sign…" / "Refusing:" (`proposal_confirm_popup.gd` ~1917, ~1931–1936, ~742) |
   | II: silent on THIS DEAL and on each court's buttons | THIS DEAL heads the page — You get / You give / Your allies get / give / keep (~1611–1640); each court row has "Ask more" / "Offer more" / "Leave out" (~707–714) |
   | II: the table opens by a door | in a campaign it opens from the war's card, "Make peace" (`war_status_panel.gd` ~576, `war_detail_popup.gd` ~1395) |
   | III: the chip "SEPARATE PEACE WITH AUSTRIA" | "Separate peace with Austria" (~676, ~3174) |
   | V: "MORE GENEROUS" (~83, ~91) | the rail says "Offer them more" (~746–747). Check the vassal chooser's own option first: `tests/test_tutorial_table_scenario.py` pins "MORE GENEROUS" and the play script clicks "More generous". |

6. **Help & Keys:**
   - the question "how many action points do I have" (`codex_terms.gd` ~157) — AP is retired (row PW part 3);
   - the order-grammar line (~94) and Enter's "Sends the order you typed" (~163) read typing as the only road.
   - Keep `codex_view.gd`'s "What you can tell a marshal — a task is typed" (~340): tasks are typed.
7. **`first_open.py`** (~4): the docstring's "Seven action screens". There are 13.
8. **`docs/TUTORIAL_SCRIPT.md`:**
   - "Last Updated: September 23, 2026" (~5);
   - "Eighteen cards" (~11);
   - the card-numbering note (~407): XIX the instruments, XX the end;
   - the Danube table (~366–405) has no row for On His Own or Ask Him;
   - "AP" (~20, 56–59, 136, 198, 216–217, 247–248, 369, 377);
   - the old nature names (~63, 86, 96, 103, 371; lower-case at ~21 and ~382);
   - typed-only teaching (~54 "Commands are typed, not clicked", ~67 "Type 'end turn'", ~68, ~165, ~378);
   - its Update Instructions (~487–492) are a one-line template.

**Checked and not stale:**
- No card says "AP" or uses the old nature names. Card IV says Bold / Careful / to the letter, pinned by
  `tests/test_ic15_the_screens.py`.
- "Grant Autonomy" appears nowhere.
- The first-open `task` line ("A task is typed, Sire…") is right: tasks are typed.

## §3 Taught nowhere — a new player meets each in the first hour

| What | Taught after TU by | Help entry today |
|---|---|---|
| The desk (THE PEACE / THE WAR / TO DECIDE) | a new card (§4), if §0's call is "show it"; Help | none |
| The End Turn list; the danger mark | card III; Help | none |
| The selection card's seven orders, keys 1–7, right-click cards, one click sends | cards I and II | key rows only (`codex_terms.gd` ~175–181) |
| The march-time colours on the map, and the strip's key under the card ("this turn · 1 turn · 2–3 turns · 4+ turns") | card II (FR-1's blind reading: guessed right, "but a guess") | the map's Key only (`map_key.gd`) |
| The marks on the marshal row (the dot beside each marshal) | card I or IX; Help | the chips' hovers only |
| The read-back (Taken / Not taken / Enter sends) | card I; Help | none |
| Take back; the map's Key | card XXI; Help | Take back (~78); the Key only as a key row |
| Orders to several corps, named armies, war goals, an army's task | card X | all four (~62, ~63, ~66, ~86) |
| Exact orders (if-thens) | card XIX | the tasks table (~131) |
| The task to prove himself | card V | Redemption (~72) |
| "Set him on his own" and "This turn: …" on his card | card XIX; Help | none ("on his own" survives only inside An army's task) |
| The voice and the portraits | card XX; Help | none |
| Battles in acts; a key battle's points (50,000 men and more); Berthier's reading | card VIII | the day's points (~40), Berthier's reading (~33) |
| A battle's bonuses multiply, and a defence is limited to +75 % (the report's "Defence limit" row) — FR-2's blind reading (`docs/audits/fr2_client/BLIND_READING_KEY.md`): every reader right in meaning, two answers still guessing at the arithmetic | card VIII; Help | none |
| THE ENEMY'S MOVES played on the map | card III | the enemy's moves (~48) |
| Authority (the chip, what spends it); the letters of state (the Correspondence) | card IX; Help | authority (~31); the Correspondence none |
| The war's page and what France learned of the enemy's plans (ON since November 23) | card XXI; Help | none |
| The Order of the Marshalate | card IX; Help | none |
| Settings (Explanations folded or on the page, text size, the read-back), saves (F5 / F9), Help & Keys itself | card XXI; Help | Settings none; saves only as key rows |

## §4 The card plan

TU refines this. Every card passes by doing what it teaches.

| Card | Keep / amend / new | What it must teach | How it passes |
|---|---|---|---|
| I The Situation | amend | the selection card and its buttons; typing is for tasks and questions; the read-back | as today, or one button pressed — TU decides by pressing |
| II The Army Marches | amend | the march by click (select Senarmont, click Munich, the order card), the typed form beside it; what an action is, in FR-1's words | as today (Senarmont in Munich — either road) |
| III The Day Closes | amend | the End Turn button and its list; THE ENEMY'S MOVES played on the map; the dispatch | as today |
| IV | keep | — | — |
| V | amend | the hearing's answer is the task to prove himself | as today |
| VI, VII | keep | re-read the Cabinet's first page after FR-1 (PW3-D1) | — |
| VIII First Blood | amend | the battle in acts; a key battle's points, told in words | as today |
| IX The Marshalate | amend | the Order of the Marshalate; authority, the chip | a reading card |
| X Standing Orders | amend | several corps at once, a named army, a war goal | as today (Davout's march) |
| XI–XVIII | keep | each re-read against the code | — |
| the desk | **new**, if §0 is "show it" | THE PEACE / THE WAR / TO DECIDE; pressing a row takes you there | the player presses a desk row |
| XIX On His Own | amend | "Set him on his own", "This turn: …" on his card, exact orders | only when a task is sent |
| XX Ask Him | amend | the voice and the portraits | only when a question is sent |
| XXI The Instruments | amend | Help & Keys, Take back, the map's Key, saves, Settings, the war's page and what we learned; the Admiralty repeat dropped | as today |
| XXII The Lesson Ends | keep | — | — |

**The Table:** cards II, III and V are reworded to the live table's words (§2, item 5). The others are re-read.

**Numbering:** a new card renumbers every later title (XIX → XX …), so the pins that read titles move together (§8).

## §5 Help & Keys

- **New entries**, in plain words, each checked against the code it names:
  - On his own;
  - The desk;
  - The End Turn list (and the danger mark);
  - The read-back;
  - The voice (a marshal's own words, and his portrait);
  - The Correspondence;
  - The Order of the Marshalate;
  - The war's page;
  - What we learned (of the enemy's plans);
  - Settings;
  - Saves;
  - Battle bonuses: they multiply, and a defence is limited to +75 % (row FR, Session FR-2's blind reading).
- **Amended:**
  - the "action points" question becomes "how many actions do I have";
  - the typed-only lines (~94, ~163).
- FR-1's key change (a pinned ledger's books on Alt+1–8) is already in Help after FR-1. Re-read it.

## §6 The first-open lines

- The 13 lines are re-read against the code, and the docstring is fixed.
- If the desk shows in the School (§0), the `desk` line's first showing moves into the lesson.
- The Danube's pre-set ids are re-read: `tutorial_1805.json` sets `first_opens` to `{cabinet, laws}`, pinned by
  `tests/test_first_open.py` (~424–432).

## §7 `docs/TUTORIAL_SCRIPT.md`

Rewritten from the code:
- both lessons, card by card (title, what it teaches, how it passes, its chip or door);
- the contents of Help & Keys;
- the first-open lines;
- real update instructions: which files and which pins move when a card changes (this doc's §8).

The phase 1–2 inventory tables are re-read, and "AP" and the old nature names go.

## §8 The pins that move — all together, in TU's commit

- **The School's shape:**
  - `tests/test_tutorial_unbreakable_2026_09_23.py` (~543 the card count; ~545–557 the order and the mirror;
    ~559–573 exact card phrases; ~251, ~263 the idle run to the hand-off);
  - `tests/test_rf4c_the_school_and_the_census.py` (~64 the count; ~66–70 the laws card);
  - `tests/test_fa_slice17_f_the_instrument_answers_2026_09_11.py` (~575 the mirror; ~596–601 step for turn);
  - `tests/test_ic13_every_man_his_own_line.py` (~565–587 the order after laws, titles XIX–XXII, gates, chips,
    predicates).
- **Card text:**
  - `tests/test_hc5_tutorial_names_fleet.py` (~26–71: card XXI's instruments, and `TUTORIAL_SCRIPT.md` must contain
    "HC-5" and "THE ADMIRALTY");
  - `tests/test_iq4_cabinet_visible.py` (~1439, "Five more instruments");
  - `tests/test_ic9b_the_trial.py` (~1639–1642, ~2125, the "on his own" census);
  - `tests/test_ic15_the_screens.py` (~78);
  - `tests/test_sr1_quick_wins.py` (~224);
  - `tests/test_cc5_the_war_table.py` (~545);
  - `tests/test_ddb_s13b_the_rulings.py` (~1018);
  - `tests/test_pc_rulings.py` (~4254);
  - `tests/test_fa_slice14c_the_school_sees_the_answer_2026_09_06.py` (~215–487);
  - `tests/test_tutorial_school_fixes_2026_08_08.py` (~292–303);
  - `tests/test_s14h_the_third_measure_rows.py` (~11024–11075, every coloured key line carries its Alt form).
- **Chips, scripts and the registry:**
  - `tests/test_fa_slice8_the_instrument_2026_09_02.py` (~994, the shipped id, gate and suggest against the play
    scripts);
  - `tests/test_tutorial_position7.py` (~434 every suggest mock-parses; ~488 the Table teaches no typed example);
  - `tests/test_wo_slice7_cabinet_door.py` (~650);
  - `tests/test_cn4_the_chip_honesty_census.py` (~1281–1286);
  - `tests/test_tutorial_registry.py` (~48–198);
  - `tests/test_fa_slice17_0_the_remnant_holds_no_ground_2026_09_11.py` (~66);
  - `tests/test_pc15_fix_slice_2026_08_15.py` (~47, ~56);
  - `tests/test_cr7_7_the_completer_teaches_both_forms.py` (~31).
- **The Table:** `tests/test_tutorial_table_scenario.py` (~313, ~444, ~451–452, ~488–500: the mirror, the count, the
  gates, the doors, "REASSURE", "MORE GENEROUS", the dates); `tests/test_tutorial_table_driven.py`.
- **Help, first-open and Settings:**
  - `tests/test_first_open.py` (~136–158 the 13 screens and each line's rules);
  - `tests/test_ui6_settings_tutor.py` (~63–99);
  - `tests/test_ui_gilt2_imperial_desk.py` (~419);
  - `tests/test_ui_gilt4_levers.py` (~92).
- **Layout:** `tests/test_uxr1_scale_fix.py` (~280–294), the `tests/test_uxr2*` family,
  `tests/test_uxr3_s12_part2.py` (~467).
- **This row's own pin:** `tests/test_tu_the_tutorial_brought_up_to_date.py`. Each strict xfail is dropped as its
  line is fixed.
- **The play scripts:** `tools/playtest_scripts/tutorial_lesson*.json`, `tutorial_table_lesson.json`.

## §9 Verify

- **Both lessons played in the real client**, at the user's setup (Interface Scale 1.8 on 5120 × 1377) and at the
  small window (2.0 on 1600 × 900):
  - every card passed by doing its thing;
  - the skip, refusal and catch-up roads still holding (`tools/tutorial_overlay_harness.gd` and the driven pins).
- **A blind reading of the finished lessons:** three fresh Explore readers. The key and its bar are written FIRST.
  The bar proposed here is all three readers right on at least nine of ten, sure or fairly sure; TU's Plan Mode may
  amend it before the reading, never after.
  1. How do you give a marshal a simple order?
  2. What is typing for?
  3. What does the desk tell you?
  4. What happens when you press End Turn?
  5. What does "on his own" mean, and what do your orders do to him?
  6. How is a great battle fought?
  7. What is authority for, and what spends it?
  8. What is an action, and what spends it?
  9. How do you take back an order?
  10. Where do you look up a word?
- **The sibling sweep:** every screen's first-open line and Help entry, read against the code.

## §10 Done when

- Every first-hour item (§3) is taught by a lesson or pointed to by Help.
- No stale line (§2) is left, and every strict xfail in this row's pin is dropped.
- Both lessons play end to end at both setups.
- The blind reading meets the bar written before it.
- The pins and the docs moved together (§8).
- **Records:**
  - `docs/STATUS.md` — the entry; ▶ NEXT UP → Session H;
  - `docs/SYSTEMS_REFERENCE.md` — a new section;
  - `docs/BUG_FIXES.md` — any defect found;
  - `docs/PRE_DEPLOY_PLAN.md` row TU;
  - `docs/NEXT_SESSION_PROMPT.md`;
  - this doc's §13.

## §11 The split line

If one session cannot hold it at the standard, it splits at a clean line:
- **first:** the School of War and Help & Keys;
- **second:** the Table, the first-open lines and `docs/TUTORIAL_SCRIPT.md`.

The session says which is done. A card is never half-shipped. Sizing, not pressure: nothing is cut without the
user's word.

## §12 What TU must re-read after FR-1 and FR-2

- **After FR-1:**
  - the number keys while a ledger is pinned (Alt+1–8);
  - the Cabinet's first page (PW3-D1 — card VII opens it);
  - the command line's row (IC2-N1 — Cabinet and End Turn stand on a row under the line; cards III and VII point at
    them);
  - the words "actions" (card II), the chips that write into your sentence (card I), and "titled provinces" (card
    XVII says "45 provinces by title").
- **After FR-2:**
  - any refusal a card quotes (finds 1, 2, 10);
  - the battle report's rows (find 3 — card VIII shows the report). New since FR-2: "Confidence in his orders", "Jealous lone attack", "Pride after proving himself", "Cavalry momentum (charged again today)" and "Defence limit (the bonuses multiply to +N%; the limit is +75%)";
  - what a bombardment scores (find 12 — card VI).

## §13 Landing record

*(Written by row TU at its landing.)*
