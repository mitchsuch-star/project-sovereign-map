# The Command Feel — are typed orders still annoying, and can enough be done by clicking? (October 16, 2026)

**The ask (October 16, 2026):** *"look into if written commands are less annoying and enough can be done for clicking, just the ease and fun and value of the command system and addons."*

**Routing:** a read-only review. Nothing under `backend/`, `godot-client/` or `tests/` was touched. The one new file beside this memo is the drive's script, `tools/playtest_scripts/cmd_feel_2026_10_16.json`; its digest is at `tools/playtest_runs/cmdfeel/digest.md` (uncommitted run output). Candidate rows are listed in §8 and are **not filed** — filing and the build are the user's call. The prior rulings this memo touches are named in §9.

---

## 0. The short answer

**Less annoying — yes, measurably, and for the right reasons.** On the seventh blind set the keyless parser reads 98.0 % of 300 fresh orders right by hand with 0 executed-other-than-meant (`docs/audits/UNREHEARSED_CENSUS_2026_10_11_SEVENTH.md`); a miss never costs an action point; a misspelt province is corrected and said, a misspelt marshal is refused with the roster, a nation typed for a province is answered with the province list; a verb-less line (`Davout, Swabia`) is read as the march; the completer saves a measured 31–40 % of keystrokes; parse-and-execute takes 45–230 ms in-process keyless. The CC-0/CC-1 fixes closed the two worst client holes (a click no longer destroys a draft; `e` no longer ends the turn mid-draft).

**What is still annoying is not the parser. It is what happens around the line** — and every item below was reproduced on the shipped board, not read:

1. **There is no group order.** `everyone fortify`, `all marshals march to Swabia`, `all corps fortify` and even the documented collective `everyone converge on Swabia` each answer *"Which marshal shall …, Sire?"* and let the player pick **one**. Fortify and unfortify are 15.3 % of everything a scripted France issues; a player who wants the army dug in types it eight times.
2. **Every question the game asks takes the keyboard away.** The objection, clarification and interrupt modals have no key handling at all and the command line is disabled beneath them, so each is a trip to the mouse. In the eight-turn drive the orders raised seven of them (3 objections, 3 clarifications, 1 interrupt): about one per turn.
3. **A typed diplomatic order is a dead end.** `propose peace with Austria` is intercepted by the client (ruling G1) and answered with *"Matters of state are conducted at the table"* and a link. The backend reads the sentence perfectly and the wizard already has `open_for_nation()`; the sentence could open the Cabinet at the court and the row, pre-filled, still priced and still confirmed.
4. **A refusal names its remedy and does not offer it.** *"Ney is fortified … Try: 'Ney, unfortify'"* is text; the ↳ offer slot CC-0 built sits empty beside it. Five of the drive's eleven refusals were this shape.
5. **The arrival tail is forgotten.** `Soult, march to Franche-Comte then fortify` is read, the tail is held back (*"Give it when he arrives"*), and on arrival Soult reports *"I await further instruction."* CC-4's `arrival_verb` already owns this; it is the part of row CC with the most typed-road value per session.

> **The user's three calls on reading this memo (October 16, 2026):** *"diplomacy should be screens and objections should be popups, how would AP handle if you moved 6 marshals needs more thought!"* — so **CF-3 is STRUCK** (diplomacy is conducted on screens; ruling G1 stands; the typed pointer is the designed answer), **CF-2 is STRUCK as a defect** (objections are popups by design; the mouse trip is the surface, not a flaw), and **CF-1 WAITS on an action-point ruling** before anything is built — §10 carries the thought.

**Enough by clicking — not yet, and the plan already knows it.** After CC-2 a click turn can march, support, attack, scout, fortify, drill, recruit, build and repair. It still cannot hold, fall back or garrison, cannot select a corps, and cannot give a group order. CC-3 (select, click, Enter) and CC-5 (the war table: arrows, the idle key, Ctrl-click groups) close the first two; the third chip trio is a small addition in the CN-4 pattern. **CC-2's March here row has already fired the re-open condition of the CX §2 ruling** (*"if a proactive movement affordance is ever added to the click road … this ruling is re-opened"*), so "the typed road wins the turn" is no longer a standing fact and should be re-read when CC-3 lands.

---

## 1. Method, and what was not done

- **The code read.** The typed road end to end (`backend/commands/parser.py` 4,023 lines, `backend/ai/llm_client.py` 5,019, `strategic_parser.py`, `clause_guards.py`, `relay.py`, `clarification.py`, `validation.py`, `question_desk.py`, `order_quotes.py`); the client's line and its add-ons (`main.gd` — the completer at `_build_completions` / `_accept_suggestion`, the history walk, `_line_insert_name`, `_offer_beside_line`, `_fill_pending_relay`, `_redirect_diplomatic_command`, `_cabinet_control_for`); the click road (`region_panel.gd` chips and the CC-2 quote rows, `marshal_management.gd` chips, `diplomacy_wizard.gd`, the hotkeys in `main.gd` and `top_bar.gd`); the popups (`popup_base.gd`, `objection_dialog.gd`, `clarification_popup.gd`, `interrupt_popup.gd`).
- **The records.** `docs/COMMAND_EXPERIENCE_SPEC.md` (row CX: the gate ruling §2, the model ruling §4, the predictor §5, the deferred table §7), `docs/audits/cx_recon_2026_09_19/two_roads.md` (38 intents on both roads), `docs/COMMAND_ROBUSTNESS_SPEC.md` §2, `docs/audits/UNREHEARSED_CENSUS_2026_10_11_SEVENTH.md`, `docs/SYSTEMS_REFERENCE.md` §121 (CC-2), the CC plan (`~/.claude/plans/sorted-yawning-clover.md`) and `PRE_DEPLOY_PLAN.md` §2 S13c, `BUG_FIXES.md` §CC, `tools/defect_census.py --open`.
- **The drive.** `tools/playtest_driver.py --script tools/playtest_scripts/cmd_feel_2026_10_16.json --turns 8 --fresh --name cmdfeel` — 33 typed lines plus 8 end turns through the real `POST /command`, keyless, seed `historical`, objection policy `trust`, clarification policy `first`. The lines were written to be a player's mix: plain orders, questions, typos, a nation for a province, group shapes, a compound, a contingency, a multi-name attack, a Cabinet verb, a verb-less line.
- **The probes.** Twenty-eight more lines through `TestClient` on fresh boards (group shapes, the three-name relay, the refusal-with-remedy shape, the cost question, hold / retreat / garrison / square), with the response's `relay_command` / `dropped_sequel` / `relay_kind` fields read, and the wall-clock per line.
- **Not done.** No Godot client was run and no screen was captured — every client claim is read from the `.gd` source and from the committed CC-0/CC-1/CC-2 pins (`tests/test_cc_click_and_command.py`, `tests/test_cc2_march_here.py`). No human typed anything; the drive is a scripted proxy, as every command census in this repository is (`COMMAND_EXPERIENCE_SPEC.md` §0's caveat). The keyed road was not exercised (the model is consulted on a measured 3.4 % of real play, CX §4). **The one judgement this memo cannot make for the user is CX-D3, the completer's FEEL** — the spec leaves it to "the user, in a played session", and that verdict is still unrecorded.

---

## 2. What the typed road is worth today — the value and the fun

The things only the line can do, each exercised in the drive:

| the line | what came back |
|---|---|
| `can Davout reach Vienna` | *"Yes, Sire — Davout can reach Vienna from Swabia in 3 turns: Swabia -> Franconia -> Bohemia -> Vienna. Mack stands on the road at Bohemia — the march will meet him there."* (free) |
| `where is Mack` | *"Mack of Austria was last reported at Bohemia, 1 turn ago; we have no fresher word."* — fog-honest, free |
| `why` | the parse trace of the last line (DD-0's instrument), free |
| `Ney, attack Mack` (Mack across the border) | the MUSTER first — who marches, who will not and why, the odds band — then the battle; Berthier's line *"the corps marched apart and arrived together"* |
| `Lannes, hold Lorraine` | *"I would rather attack than sit idle."* — the marshal's character, and three answers |
| `Lannes, move to Swabia and attack Mack` | *"We march. Pity whatever slows us."* — the flavour echo |
| `Soult, move to Lorrain` | corrected and said: *"Our maps read Lorraine as the province nearest your order, Sire."* |
| `Davout marhc to Bavaria` | *"Bavaria is a nation, not a province. Name a province, Sire — theirs are Franconia, Munich, Swabia."* |
| `Davout, Swabia` | read as the march (*"Davout is already in Swabia"*) |
| `Murat, if Mack advances fall back to Bohemia` | refused honestly as a contingency the game cannot hold — and CC-4 owns the grammar |

**Speed.** 45–230 ms per line in-process keyless (the slow end is a battle); the parser is never the wait. **Cost of a miss.** Not one refusal, near-miss or shrug charged an action point — the drive and the probes agree with `two_roads.md` §3a. **Keystrokes.** The completer (`<Marshal>, <verb> <target>`, the roster chosen by the verb, Tab accepts, never sends) and the prefix-filtered history were measured at 31.7 % and 39.7 % saved over 1,416 archived commands (CX §5); `Davout, march to Swabia` is seven keys with it on. **Safety.** A question never orders (CX-1, 684 cases); an unknown name never binds (CX-R1); a chip sends the same string a player would type, through the same `/command` road, so the rules live in one place.

**Fun, honestly judged.** The fun is real and it is in exactly three places: the marshals answering in character, the desk answering the board in a sentence, and the muster saying what will happen before it happens. None of that is reachable by a chip, and all three worked in the drive. The parser's own moments of grace — the nation-for-province reply, the corrected province said aloud, the verb-less march — are the "the game heard me" feeling the pillar is built on.

---

## 3. The eight-turn drive — what each line got back

Of 41 lines (33 orders and questions, 8 end turns): **30 ✓, 11 ✗**. The eleven refusals by cause: fortified-cannot (5 — the driver's own doing: its clarification policy picked Ney at the group question on turn 2, so Ney stood fortified from then on; the shape is the point, not the count), the border law (`Bernadotte, go to Nassau` — Hesse at peace, honest), the levy's reach rule (`recruit infantry in Paris` — the chip fails identically), the nation-for-province (good reply), the unarmed charge (good reply), the contingency (honest), `drill the guard` on a fortified corps. Questions raised BY the orders: 3 objections, 3 clarifications (all three the group shape), 1 strategic interrupt. Two shrugs: `what can Ney do` and nothing else — the desk's open rows SFR-H8 … H14 are this class and remain owned.

The lines that mattered most for the verdict:

| line | what happened | reading |
|---|---|---|
| `everyone fortify` · `all marshals march to Swabia` · `fortify everyone` | *"Which marshal shall carry out this order, Sire?"* — one choice | **no group order exists** (§4 CF-1) |
| `Ney, Davout and Soult attack Mack` | the muster seated Davout and Soult ("WILL JOIN"); one battle | multi-name ATTACK is already right — the corps system is the group verb for battle |
| `Ney and Davout, fortify` | Ney fortifies; `relay_command: "Davout, fortify"` fills the line for the player's Enter | two names cost two Enters — fine |
| `Ney, Davout and Soult, fortify` | Ney objects; Davout's order waits behind the question; **Soult's is dropped with a note** | three names, one is lost — the relay carries one tail (§4 CF-1) |
| `Soult, march to Franche-Comte then fortify` | read; tail held: *"Give it when he arrives"*; on arrival *"I await further instruction"* | the player must remember (§4 CF-5, CC-4's) |
| `Ney, atack Mack` (fortified) | *"… cannot attack. Order 'unfortify' first"* — and the probe's form adds *"Try: 'Ney, unfortify'"* | the remedy is named, never offered (§4 CF-4) |
| `Talleyrand, propose peace to Austria` | the driver bypasses the client: terms prepared, a confirm, 3 DP, Austria's answer next turn | in the client this line is intercepted and NOT sent (§4 CF-3) |
| `what would it cost to march Davout to Vienna` | the manual's generic sentence about marches | the desk has `march_quote()` since CC-2 and does not print from it (§4 CF-7) |

---

## 4. The annoyances, ranked — each reproduced, each with its smallest honest fix

**CF-1 — There is no group order (P2).** `everyone fortify`, `all marshals fortify`, `all corps fortify`, `everyone, fortify` and `everyone converge on Swabia` each raise the one-marshal clarification (`clarification.py:195-222` builds one option per candidate and no "all of them"). The collective address the parser DOES read needs a listed roster in front of the collective word (`parser.py::_split_collective_address`, SF-CMD-1 W3: `Ney, Davout, Soult: everyone converge on Swabia`), and even then it hands the SECOND name to the relay and names the third as needing its own order — the relay carries exactly one tail by design (`relay.py` rule 6: "nothing is queued"). So the shape a player types most for the army's commonest order has no road. **The fix is already planned under another name:** CC-5's group card sends N lines "through one sequencer over `_send_order`" that stops at the first objection, refusal or popup and reports "2 of 3 sent". Make the typed collective address — `everyone`, `all`, `all corps`, `every marshal`, and a bare name list of three or more — produce the SAME sequencer payload, so the typed road and Ctrl-click share one road (Rule 5's spirit, one executor). Nothing new in the backend: each line is an ordinary `/command`. Owner suggestion: CC-5, at its head, with a pin that `everyone fortify` on the boot board fortifies every corps the state allows and names each refusal.

**CF-2 — The game's questions take the keyboard away (P2).** `objection_dialog.gd`, `clarification_popup.gd` and `interrupt_popup.gd` extend `CanvasLayer` directly, carry no `_input`, no `KEY_`, no shortcut and no `grab_focus`; `main.gd` disables the line under every modal (`set_input_enabled(false)`). `popup_base.gd:39-47` gives ONLY Esc, and only to popups that define an `esc_control()`, and its own docstring states the rule that governs the fix: *"must never be answered by a reflex keypress: the rightmost cannon-fire option is `hold_position` at −3 trust and a cancelled order."* That rule is right and the fix must keep it: **numbered keys, never Enter.** Each button shows its digit (`1 Trust him`, `2 Proceed as ordered`, `3 Compromise`), the digit answers, Enter and Space do nothing, and the keys are live only while that modal is the top of `dialog_manager`. A reflex Enter cannot fire a cannon; a deliberate `2` can. The clarification's options already carry `command` strings, so a digit there is exactly the click. Size: a client-only slice, one helper on the three scripts, a harness scenario per popup. Owner suggestion: a CC part (it is the command road's own flow), or S15's UXR-4 head if the user wants it read at the monitor first.

**CF-3 — A typed diplomatic order dead-ends at a pointer (P2, the user's ruling G1 to re-read).** `main.gd::_redirect_diplomatic_command` intercepts the whole Cabinet family on the typed path and prints *"Matters of state are conducted at the table, Sire … In the Cabinet: F1 → Austria → Propose Peace … ⚜ Take your seat at the table (F1)"*. The reasons G1 was ruled still hold — the Cabinet is priced and confirmed, a typed proposal would commit DP on a sentence — but the refusal is now the only place in the game where a correctly read order goes nowhere. `_cabinet_control_for` already resolves the court AND the row; `diplomacy_wizard.gd::open_for_nation(nation)` already opens at step 2; `_on_action_selected(action_id, payload)` is the row's own click. **The fix keeps G1's letter and loses the dead end:** the typed sentence opens the Cabinet at the court with the row pre-selected (after the preview loads), still priced, still confirmed by the same button — the line becomes a shortcut into the table rather than a sign pointing at it. The `bid for <court>, <N> gold` exception (DDB-10) shows the pattern is already accepted for one verb. Nothing is sent that the wizard would not send. Owner suggestion: a half-session client slice; needs the user's word because G1 is theirs.

**CF-4 — The refusal names its remedy and does not offer it (P3).** *"Ney is fortified at Rhineland and cannot attack. Order 'unfortify' first to make the army mobile. Try: 'Ney, unfortify'"* — the sentence is right; the response carries no `relay_command`, so the ↳ offer slot (CC-0's `_offer_beside_line`, Tab takes it, never sends) stays empty and the player retypes. Measured: five of the drive's eleven refusals and the fortified / squared / drilling / defensive family in `state_probe.order_state_refusal`. **Fix:** a `remedy_command` field on refusals whose remedy is a single verb the state probe already knows (`unfortify`, `break square`, the stance change), ridden by the client exactly as `relay_command` is, and — the half that makes it worth it — the ORIGINAL order re-offered beside the line once the remedy has gone out (one transient on the world, the `_pending_relay` pattern, cleared at the turn boundary). Two Tabs and two Enters instead of two retypes. Owner suggestion: a CC part, beside CC-4's "contradiction suggests the legal order", which is the same idea for compounds.

**CF-5 — The arrival tail is forgotten (P3 — OWNED, CC-4).** `then fortify` on a march is held as kind `moment` and the arrival report says *"I await further instruction."* The note is honest and the player still has to remember. CC-4's `arrival_verb` (march … then fortify / hold / drill / defend, paid once, executed by `_handle_move_to_arrival`) is the fix. **Recorded here only to rank it:** of row CC's three remaining parts, CC-4 is the one whose value lands on the TYPED road, and its head (CC-X6 the dropped then-attack tail, CC-X7 Compromise losing the condition) holds the row's only open P2. Nothing to add.

**CF-6 — The click road still cannot say hold, fall back or garrison (P3).** The own-marshal row of the province panel offers Fortify / Unfortify / Drill / Scout and the co-located Attack (`region_panel.gd:846-900`, each dimmed with the executor's reason when refused — the CN-4 pattern), and CC-2 added March here / Support / Attack rows with their quotes. Three verbs a player gives every campaign have no chip anywhere: `hold` (2 AP, the standing guard), `retreat` / `fall back` (free), `garrison` (2 AP, the 3-garrison cap). CC-3 and CC-5 do not add them. **Fix:** a Hold · Fall back · Garrison trio on the own-marshal row in the CN-4 pattern — offered only where `order_refusals` has no reason, priced on the label as the levy chips are, sent as the literal string. Owner suggestion: CC-3's panel work, or a ten-line follow-on.

**CF-7 — The cost question answers the manual, not the board (P3).** `what would it cost to march Davout to Vienna` → *"A march … is a standing order of 2 actions (1 for a literal marshal or the Emperor) …"*. True, generic, and the game has had Davout's exact road, AP and turns in `order_quotes.march_quote()` since CC-2 — the desk's reach answer already prints from it (CC-2's byte-identical pin). **Fix:** the `cost` kind, when the sentence names a marshal and a province, answers from the same quote (*"2 actions and 3 turns, Sire — Swabia -> Franconia -> Bohemia -> Vienna; Mack stands on the road"*). One builder, as CC-2 ruled. This is a sibling of SFR-H8 (the march-time question reading the wrong province) and belongs with it.

**CF-8 — `what can Ney do` gets the shrug (P3 — the open SFR-H class).** The desk has an `options` kind (`counsel.py`, "what can I do") that answers for the army; the per-marshal form falls through to *"I cannot answer that from the dispatches."* It is the same seam as SFR-H4 (*"Could Soult drill his corps today?"*) and `state_probe.order_refusals` already knows, verb by verb, what Ney cannot do and why. Fold into SFR-H4's fix: the per-marshal options answer lists the verbs that stand and names each refused one with its reason.

**CF-9 — The three-name address drops the third (P3, folds into CF-1).** Noted in §3; the sequencer closes it.

---

## 5. The click road after CC-2 — what a turn looks like, and what parts 2–4 buy

**A click turn today** (read from the `.gd` and the CC-2 record, not from a screen): click a province → the panel; MARCH HERE rows for every corps elsewhere (`Soult · 2 AP · 3 turns`, the contact and "replaces his march" notes, "he may object"), SUPPORT rows for a corps standing there, ATTACK rows for a seen enemy (within reach `attack`, beyond it `march … then attack`); Fortify / Unfortify / Drill / Scout on the own-marshal row; Recruit by arm, Build, Watchtower, Repair, the dockyard and the landing on the province; Negotiate into the Cabinet. End Turn by button. Every chip is priced or dimmed with its reason, and every chip sends the typed string — "a chip removes naming risk, never gate risk" (CX §1) still holds, now for movement too.

**What a click turn still cannot do:** hold, fall back, garrison (CF-6); any order to a corps you have not located on the map first; a group order; cancelling a standing order (the Orders tab's Cancel, three steps away); the tactical specials (charge, bombard, form square, restrain). And the hunt: below zoom 1.1 only nation labels draw (`map_label_layer.gd`), so "you need not know the spelling" costs a zoom first.

**The remaining parts, by value per session (one session each):**

| part | buys for the CLICK road | buys for the TYPED road | note |
|---|---|---|---|
| **CC-3** select, click, Enter + drag | the movement gesture the CX §2 ruling said was missing — a corps, a destination, a confirm card with the quote | nothing directly (CC-1 already clicks names into the line) | the one that makes "enough by clicking" true for the ordinary turn |
| **CC-5** the war table | order arrows with Cancel / Change, the idle-marshal key, **Ctrl-click group orders through one sequencer** | **the same sequencer carries `everyone fortify`** (CF-1) if the typed collective address is routed to it | the cheapest place to close the typed road's biggest hole |
| **CC-4** chained orders | — | `arrival_verb` (CF-5), the contingency, CC-X6/X7 at its head | the typed road's own part; highest risk, the plan says so |

The plan's order (CC-3 → CC-5 → CC-4) is right. The one amendment this memo recommends is that CC-5's sequencer be specified as the owner of the typed collective address, not only of Ctrl-click — one road for both inputs, which is the row's own invariant ("every click order travels the same `/command` road as typed text").

---

## 6. What is NOT annoying — and must not be "fixed"

- **Spelling.** Provinces are corrected and the correction is said; marshals are refused with the roster (an honest refusal, chosen over a guess — a guess once sent Soult into a battle, CX-1); the completer fills the name after one or two letters. Leave it.
- **The marshals' objections.** Three in eight turns is the pillar working, not friction. The fix is CF-2's keys, not fewer objections.
- **The muster pause at bad odds, the strategic interrupt.** Priced, reversible, free to cancel. Leave them.
- **The border law and the levy's reach rule.** The board's own refusals, said in the executor's words. The chip fails the same way, which is the correct design.
- **Latency.** Not a factor keyless; keyed, the model is consulted on 3.4 % of lines.
- **The end-turn warning on unused actions.** One extra Enter when it matters; CC-X3 made every sender disarm it.

---

## 7. The verdict, in the user's three words

- **Ease.** The LINE is easy now: the parser reads what a player means at 98 % by hand, misses cost nothing, and the completer makes an order seven keys. The FLOW around the line is not: group orders, the mouse trip at every question, the Cabinet dead end, the retype after a refusal, the forgotten tail. All five are in the client or one field away from it; none needs a parser change.
- **Fun.** The typed road's fun is intact and specific — character, the desk, the muster — and the click road cannot replace it. The CC row is adding clicking BESIDE typing, which is the right shape; the risk to watch is that a confirm card on every map gesture (D4) makes the click road feel slower than the line it was meant to spare. CC-3's Mode C walk should time a march by drag against the same march typed with the completer.
- **Value.** The chips are priced and the line is now priced too where it matters (the muster, the reach answer, the March here quote). Value is highest where the two roads share one source — and lowest where they do not: the cost question (CF-7) and the per-marshal "what can he do" (CF-8) are the last two typed questions still answering from the manual.

---

## 8. The candidate rows (NOT filed — the user's call)

| id | P | what | smallest fix | size | owner suggestion |
|---|---|---|---|---|---|
| CF-1 | P2 | no group order (`everyone fortify` picks one marshal; the three-name list drops the third) | route the typed collective address to CC-5's sequencer; the one-marshal clarification gains an "All of them" option that does the same — **WAITS on the AP ruling of §10 (the user, October 16, 2026: "needs more thought")** | inside CC-5 | row CC, CC-5's head, after the ruling |
| CF-2 | — | ~~objection / clarification / interrupt modals answer only to the mouse~~ **STRUCK October 16, 2026 — the user: "objections should be popups"; the modal is the designed surface** | — | — | — |
| CF-3 | — | ~~a typed Cabinet verb dead-ends at a pointer~~ **STRUCK October 16, 2026 — the user: "diplomacy should be screens"; G1 stands and the pointer to the Cabinet is the answer** | — | — | — |
| CF-4 | P3 | a refusal names its remedy and does not offer it | `remedy_command` rides the ↳ offer; the original order is re-offered after the remedy sends | 0.5 session | row CC, beside CC-4's contradiction suggestion |
| CF-5 | P3 | the arrival tail is forgotten on arrival | CC-4's `arrival_verb` | owned | CC-4 (no change) |
| CF-6 | P3 | no Hold / Fall back / Garrison chip anywhere | the trio on the own-marshal row, CN-4 pattern, priced, dimmed with the reason | small | CC-3's panel work |
| CF-7 | P3 | the march-cost question answers the manual, not the quote | the `cost` kind prints from `march_quote()` when a marshal and a province are named | small | with SFR-H8 |
| CF-8 | P3 | `what can Ney do` → the shrug | the per-marshal options answer from `order_refusals` | small | with SFR-H4 |
| CF-9 | P3 | the three-name address drops the third | folds into CF-1 | — | CF-1 |

Every row above was reproduced on the shipped 1805 boot through the real `POST /command` or read at a named line; none is a claim from memory. The conservative fixes (CF-2, CF-4, CF-6, CF-7, CF-8) change no mechanic and no ruling. CF-1 is a routing of planned work. CF-3 re-reads a user ruling and is proposed, not recommended over the user's head.

---

## 9. The rulings this memo touches

- **CX §2 "The click road wins the catalogue. The typed road wins the turn."** Its stated re-open condition — a proactive movement affordance on the click road — was met by CC-2's March here row on October 15, 2026 and will be met in full by CC-3. The ruling's headline no longer holds as written; its deeper finding ("the chips are priced, the typed verbs are blind") has been largely closed by CX-2 and CC-2, with CF-7 and CF-8 the residue. Recommendation: re-read and re-record the ruling at CC-3's landing, not before.
- **G1 (the Cabinet is the only door).** Untouched by anything here unless the user takes CF-3; CF-3 keeps the door and the price and removes only the dead end.
- **CX-D3 (the completer's feel).** Still the user's, still unrecorded. This memo cannot supply it.
- **CX-D1 (a proactive movement affordance)** is CC-3 by another name; the spec's §7 row should point at row CC when CC-3 lands.
- **popup_base's "never a reflex keypress" rule.** Untouched — CF-2 is struck.
- **The user's calls of October 16, 2026** (on reading): diplomacy is conducted on screens (CF-3 struck, G1 stands); objections are popups (CF-2 struck); a group order is not built until its action-point road is ruled (§10).

---

## 10. The action-point question for a group order — the thought the user asked for

*"How would AP handle if you moved 6 marshals — needs more thought."* It does, and none of it is a parser matter.

**The facts the ruling has to respect.**
- **The pool is 4 military actions a turn** (`world_state.py` `max_actions_per_turn`; `calculate_max_actions` = 4 + `bonus_actions` + the Staff), plus 2 administrative. The Staff law (France's Grand Quartier Général, 9,000 gold and 300 a turn, mid-campaign) is **the only road to a fifth** — `REFORMS_SPEC.md` §5, SR-D3's ruling.
- **The prices** (`Marshal.strategic_order_ap`, `_action_costs`): a standing march / pursue / hold is **2** (1 for a literal marshal or the sovereign); **SUPPORT is 1 for every marshal** — SR-2e priced it so on purpose: *"a corps that marches to its colleague's guns, made cheap enough to use"*; the tactical verbs (move to a neighbour, attack, fortify, unfortify, drill, scout) are **1**, and a fortify from an aggressive stance pays **1 more** for the stance change; garrison is 2.
- **What the army already does for nothing:** the **muster** — when one marshal attacks, every eligible adjacent corps marches to the guns at no AP (`combat_executor._calculate_reinforcements`, the Grouchy rule for literal men, the arrival roll), and the drive's first battle seated four corps beside Ney for one action; co-location earns the coordination bonus after two turns at no AP (`MULTI_MARSHAL_SPEC.md`).
- **The asymmetry is designed:** AI rosters are 1–3 corps on 2–4 actions; France fields 8 corps on 4. "The action-point gap is France's problem; the Staff is France's answer" (`REFORMS_SPEC.md` §5).

**So six marches cost 12 actions — three turns of the whole pool — and six fortifies 6 to 12.** A group order cannot make that cheaper without changing the economy, and the four readings below differ exactly on whether it should.

| | the reading | what it costs the design | who it touches |
|---|---|---|---|
| **A** | **A convenience, priced as the sum.** `everyone march to Swabia` is six ordinary lines; the card (or the line's reply) shows the sum against the pool BEFORE anything goes out — *"12 actions for six marches, 4 in hand: name two, or the first two go"* — and the sequencer sends in the order named, stops at the pool's edge and says who did not go. | **Nothing.** No price moves; each line is an ordinary `/command`; the AI is untouched (Rule 5 holds trivially). It is what the CC-5 plan already wrote ("the summed AP checked against the pool"). The group order is then worth most on the cheap verbs — four fortifies, four supports, scouts — and as the one place the whole turn's spend is read at once. | row CC only |
| **B** | **Lead and follow, at today's prices.** The first name marches at 2; every other name FOLLOWS him at SUPPORT's 1 — Ney marches, Davout and Soult follow = 4, three corps on one order, the whole pool. | **A new meaning for SUPPORT** (today it is "march to his battle when he fights", not "walk where he walks"), or a new `FOLLOW` standing order — a backend order type with its own arrival, objection and save fields. Three corps a turn instead of two. | row CC + the strategic-order owner |
| **C** | **An army order at a flat price.** One price (say 3) moves any number of corps to one destination: *"the Grande Armée marches"* — the Ulm manoeuvre in one line. | **The end of the pool as the pacing device.** The whole army moves every turn for less than two marches cost today; SR-D3's 4-against-8 asymmetry disappears; the AI (same executor) needs the same verb or falls behind; every series re-measures. Not a command-road slice — an economy ruling. | Score Mandate / the economy |
| **D** | **The army order as the Staff's power.** C, but only once the Staff law is in force — historically Berthier's staff is precisely what let the Grande Armée move as one. The opening keeps the choice; the mid-campaign reform buys tempo rather than one point. | The strongest reading thematically, and it re-prices the Staff: today it is "+1 action for every court at one price" (`REFORMS_SPEC.md` Q5, GR5); "the army moves as one" is worth far more to France than to a 2-corps court, which the spec's own asymmetry argument half-expects. Needs the Reforms owner's ruling and an AI arm that uses it. | the Reforms spec |

> **RULED AND BUILT, October 17, 2026 (S13f "AO — the army order").** The user, on reading: *"i like the army moving as one after getting tech, you could also technically have them all pursue a friendly unit before then it just cost more. all army orders should only work if napoleons authority is high enough too"*, then *"make decisions and code it make it work well"*. The ladder built: A as the floor (the fan-out, priced as the sum, pausing behind a member's objection and going on when answered), FOLLOW as the pre-Staff road (a SUPPORT that stands, SUPPORT's price), and D as the Staff's second power (one order at 2 actions for the Emperor's column within two provinces of the sovereign, under the authority gate — 70 carries, 50–69 a doubter refuses, below 50 the fan-out). The record is `REFORMS_SPEC.md` §5a; the rules `SYSTEMS_REFERENCE.md` §125; the pins `tests/test_ao_the_army_order.py`. The paragraph below is the recommendation as it stood before the ruling.

**The recommendation:** **build A under CC-5 as the plan says**, with the sum shown before the send and the one-marshal clarification gaining an "All of them" option that does the same thing. A changes no number and makes the economy legible in one place, which is where the "six marshals" question first becomes visible to the player. If two marches a turn then feels too slow in play, **B is the cheap next step** (one order type, the price SR-2e already set). **C and D are not row CC's to decide** — they are an economy ruling with a series re-measure, and D is the historically fuller option with real costs, offered as such.

*Evidence files:* the drive `tools/playtest_runs/cmdfeel/digest.md` (run output, not committed); the probe transcripts in the session scratchpad (`probe_group.txt`, `probe_group2.txt` — the lines are reproduced in §3 and §4 so nothing load-bearing lives only there).
