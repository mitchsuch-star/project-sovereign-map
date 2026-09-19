# IQ-10 "The Client Pass" — September 19, 2026

**Platform:** Windows 11, Godot 4.4.1.stable, 1600x900 capture window, Interface
Scale 1.0 and 2.0 (`ui_settings.gd` MIN 0.75 / MAX 2.0).
**Tree:** master `954efadc` (the IQ-7 review round, IQ-8, IQ-9) **plus this
row's diff** — the four client/backend fixes below are in the frames.
**Parser:** mock throughout; no key, no network (the IQ-9 floor).
**Saves:** every capture ran under a sandboxed `INK_IRON_SAVE_DIR`; the
developer's `saves/autosave.json` mtime did not move (the IQ-7 review round's
save floor, re-checked here).

## What this row is

UI/UX had not been looked at since September 11, and the reason was always the
same: no instrument. The pass builds one, uses it, and leaves it committed.

```bash
.venv/Scripts/python.exe tools/iq10_capture_payloads.py --out <dir>
.venv/Scripts/python.exe tools/iq10_run_captures.py --payload-dir <dir>
```

Two commands re-shoot every surface in this memo. The first captures REAL
endpoint payloads off STAGED boards in-process (the collapse board, the mission
boards, the IQ-5 battles, the IQ-7 petition, a prisoner, the region map, the
t10/t20 fixtures, and the four Napoleon saves staged on August 16 and never
captured); the second drives `tools/iq10_surface_screenshot.gd`, one generic
offscreen capture that instantiates the REAL scene, calls its REAL entry method,
sets `content_scale_factor`, and saves a PNG **plus a machine record of every
visible string, every button that lies outside the logical viewport, and every
RichTextLabel taller than its box**.

That record is why the pass found things. A human reading 160 frames would not
have measured that the diorama's Close button sits at y=658 on a 450-high
screen; the harness reports it, and the frame then shows it.

**80 surfaces x 2 Interface Scales = 160 frames, all committed under
`docs/audits/IQ10_*.png`.** Godot exit 0, **0 `SCRIPT ERROR`**.

## What it found, and what was done

| id | severity | defect | disposition |
|---|---|---|---|
| **H1** | P2 | **The levy and the substitute market never rendered on the soil that feeds France.** `region_panel.gd` gated EVERY action row on `controller == _PLAYER_NATION`, while the comment on the substitutes row beside it said the market "renders on ALLY soil too because the granary is open there (IQ1-3A)". The backend prices that ground and always did: measured on the 1805 boot, Amsterdam (Holland's province, Bernadotte standing on it) at **598g a battalion and 3,193g a substitute batch**, Milan at 3,672g — and the one surface where the choice is made showed a French corps on friendly ground no way to feed itself. | ✅ **FIXED** — `var feeds_us` reads the ground the backend PRICED (it prices only where a French corps stands, so no second rule is needed); the levy and substitutes rows follow it, Build/Repair/garrison stay own-soil. Before/after: `IQ10_REGION_AMSTERDAM_2026_09_19.png` now carries the Recruit chips, the ordinance line and "Substitutes … 3,193g per 10,000 — no men off the rolls (22,000 under the establishment)". Pinned three ways incl. a backend measurement. |
| **IQ10-1** | P3 | **A captive projected an aura.** On the Aug-16 `np_visual_captive` save (Napoleon taken at T11, held at Vienna, strength 0) the Generals card advertised "The Presence — Every French corps fighting in the Emperor's province gains +10% attack and defense. Enemy commanders will not attack his army at odds they would accept against any marshal." Every combat seam reads a STANDING marshal (NP-4); the card was the one surface saying otherwise, and NP-V's §15.4 pass had made every OTHER aura surface decay-aware. | ✅ **FIXED** (`marshal_overview._build_ability`, lever `CAPTIVITY_SUSPENDS_THE_ABILITY`): a captive's ability is named but not ACTIVE and ships no effect text. `IQ10_GENERALS_NP_CAPTIVE_2026_09_19.png` (the line is gone) beside `IQ10_GENERALS_NP_SEAT_2026_09_19.png` (it stands). |
| **IQ10-2** | P4 | **"PRISONER of Kingdom of Italy since T1."** — R7, the rule the IQ-7 review round applied to every vassal sentence, one surface over. | ✅ **FIXED** (`THE_PRISONER_NOTE_TAKES_THE_ARTICLE`): "PRISONER of **the** Kingdom of Italy since T1."; Austria and Switzerland are unchanged. `IQ10_GENERALS_PRISONER_2026_09_19.png`. |
| **IQ10-3** | P4 | **"…or refuse it.."** — the petition popup's Grant-unavailable line added a full stop to a reason that is already a whole sentence. The only double punctuation in 160 frames. | ✅ **FIXED** (`incoming_proposal_popup.gd`): the stop is added only when the reason lacks one. `IQ10_PETITION_POPUP_NO_DP_2026_09_19.png`. |
| **IQ10-4** | P3 | **The EMPTY letter-book did not fit at Interface Scale 2.0.** `show_mailbox` returns early when there are no envoys — one line before `Utils.clamp_centered_panel`. Measured: the authored 960x720 rect stood inside an 800x450 logical viewport, the Close button at **y=746**, and the visible middle of the panel was a single flat colour (the capture recorded a blank frame). With one row present the same panel already fitted at 776x362. | ✅ **FIXED** (the early arm clamps too). Re-measured after: **776x362, Close at y=342**. `IQ10_MAILBOX_BOOT_X2_2026_09_19.png`. |
| **IQ10-5** | P3 | **The Battle Diorama did not fit at Interface Scale 2.0.** `_tray_inner.custom_minimum_size = Vector2(TRAY_W, TRAY_H)` is a hard floor, so the clamp shrank the height (362) and could not shrink the width: the tray sat at **x=-100 with width 1000**, hanging off both edges, and Replay/Close landed at **y=658**. ESC still closed it (`ui_cancel`), so it was legibility, not a soft-lock. | ✅ **FIXED** (`_fit_tray_to_viewport`, lever `THE_TABLEAU_FITS_THE_SCREEN`): a tableau in design pixels with absolutely placed children fits by SCALING, not by reflowing. Re-measured: **548x362 at x=126**, everything on screen; scale 1.0 on any window that already fits, so ordinary frames are unchanged. `IQ10_DIORAMA_DADJ_X2_2026_09_19.png`. |
| **IQ10-6** | P3 | **The game's own sentence was not typable.** The confirmation says "I shall begin efforts to **gather intelligence on** Austria" (`MISSION_DESCRIPTIONS["GATHER_INTEL"]`) and only the abbreviation `gather intel on` parsed — a player who echoed the game got Berthier's shrug. Found by the payload capture, whose own staging used the long form. | ✅ **FIXED** (`llm_client` mission keywords). Pinned by a drift test: the string the game PRINTS must be a string the parser knows. |
| **IQ10-7** | P4 | **The IQ-10 payload harness invented a proposal type.** Its transit staging typed `propose trade agreement with Sweden`; `trade_agreement` exists as exactly one line of suggested-terms copy (`diplomatic_templates.py`) and is offered by no wizard and no executor, so the staging could never have worked. | ✅ **FIXED in the tool** (it proposes open borders now). ⚠ The dead `trade_agreement` copy row is left standing and recorded here, not deleted — it belongs to whoever owns the suggested-terms table. |

### Routed, not fixed

| id | severity | defect | owner |
|---|---|---|---|
| **IQ10-X1** | P3 | **The top bar overflows at Interface Scale 2.0.** Measured on two boards: `EventLogBtn` at **x=-26** (boot) and **x=-65.5** (with a mission standing) — off the left edge — while `MenuBtn` sits at x=798 of an 800-wide logical viewport. The L hotkey still opens the log, so nothing is unreachable, but the bar silently loses buttons as its content grows. The honest fix is a bar that sheds its "(L)" hints, or scrolls, at narrow widths — a layout decision, not a copy one. | the next UI slice (the `top_bar.gd` layout); frames `IQ10_TOP_BAR_BOOT_X2_2026_09_19.png`, `IQ10_TOP_BAR_MISSION_COURT_X2_2026_09_19.png` |
| **IQ10-X2** | P4 | **The petition popup's decisive line sits at the fold.** With Grant unavailable, the crimson reason renders as the LAST line of a scrollable body and is cut mid-sentence at 1600x900 ("…the petition stands until the turn"). Nothing is lost (the body scrolls, and the same sentence is the Grant button's tooltip), but the one line that explains a dead button is the one the player must scroll for. | the next UI slice; frame `IQ10_PETITION_POPUP_NO_DP_2026_09_19.png` |

## The index

Every surface, both scales, with the sentence its frame is read against.
`PASS ⚠` marks a frame that passes on content with a layout flag recorded above.

| surface | frames (1.0 / 2.0) | what it must show | verdict |
|---|---|---|---|
| **Strategic Ledger — Forces tab** | `IQ10_LEDGER_BOOT_FORCES_2026_09_19.png` · `IQ10_LEDGER_BOOT_FORCES_X2_2026_09_19.png` | the Forces tab of the 1805 boot: no raw nation tag, no '<null>', every figure the payload carries, nothing clipped at scale 2.0 | PASS |
| **Strategic Ledger — Territories tab** | `IQ10_LEDGER_BOOT_TERRITORIES_2026_09_19.png` · `IQ10_LEDGER_BOOT_TERRITORIES_X2_2026_09_19.png` | the Territories tab of the 1805 boot: no raw nation tag, no '<null>', every figure the payload carries, nothing clipped at scale 2.0 | PASS |
| **Strategic Ledger — Economy tab** | `IQ10_LEDGER_BOOT_ECONOMY_2026_09_19.png` · `IQ10_LEDGER_BOOT_ECONOMY_X2_2026_09_19.png` | the Economy tab of the 1805 boot: no raw nation tag, no '<null>', every figure the payload carries, nothing clipped at scale 2.0 | PASS |
| **Strategic Ledger — Intel tab** | `IQ10_LEDGER_BOOT_INTEL_2026_09_19.png` · `IQ10_LEDGER_BOOT_INTEL_X2_2026_09_19.png` | the Intel tab of the 1805 boot: no raw nation tag, no '<null>', every figure the payload carries, nothing clipped at scale 2.0 | PASS |
| **Strategic Ledger — Manpower tab** | `IQ10_LEDGER_BOOT_MANPOWER_2026_09_19.png` · `IQ10_LEDGER_BOOT_MANPOWER_X2_2026_09_19.png` | the Manpower tab of the 1805 boot: no raw nation tag, no '<null>', every figure the payload carries, nothing clipped at scale 2.0 | PASS |
| **Strategic Ledger — Orders tab** | `IQ10_LEDGER_BOOT_ORDERS_2026_09_19.png` · `IQ10_LEDGER_BOOT_ORDERS_X2_2026_09_19.png` | the Orders tab of the 1805 boot: no raw nation tag, no '<null>', every figure the payload carries, nothing clipped at scale 2.0 | PASS |
| **Strategic Ledger — Admiralty tab** | `IQ10_LEDGER_BOOT_ADMIRALTY_2026_09_19.png` · `IQ10_LEDGER_BOOT_ADMIRALTY_X2_2026_09_19.png` | the Admiralty tab of the 1805 boot: no raw nation tag, no '<null>', every figure the payload carries, nothing clipped at scale 2.0 | PASS |
| **Strategic Ledger — Economy (the chest spent)** | `IQ10_LEDGER_SPENT_ECONOMY_2026_09_19.png` · `IQ10_LEDGER_SPENT_ECONOMY_X2_2026_09_19.png` | the Charges of Empire and the spent figure; IQ-1's convertible chest | PASS |
| **Strategic Ledger — Economy (60% of the ceiling)** | `IQ10_LEDGER_CEILING_CALM_ECONOMY_2026_09_19.png` · `IQ10_LEDGER_CEILING_CALM_ECONOMY_X2_2026_09_19.png` | the ceiling line below its bound | PASS |
| **Strategic Ledger — Economy (150% of the ceiling)** | `IQ10_LEDGER_CEILING_ABOVE_ECONOMY_2026_09_19.png` · `IQ10_LEDGER_CEILING_ABOVE_ECONOMY_X2_2026_09_19.png` | the ceiling line ABOVE its bound, and says so | PASS |
| **Strategic Ledger — Economy (the legacy world)** | `IQ10_LEDGER_CEILING_UNBOUNDED_ECONOMY_2026_09_19.png` · `IQ10_LEDGER_CEILING_UNBOUNDED_ECONOMY_X2_2026_09_19.png` | an unbounded ceiling rendered without a raw key | PASS |
| **Strategic Ledger — Economy (one province left)** | `IQ10_LEDGER_COLLAPSE_ONE_ECONOMY_2026_09_19.png` · `IQ10_LEDGER_COLLAPSE_ONE_ECONOMY_X2_2026_09_19.png` | IQ-2's collapse state, named, not a cheerful net | PASS |
| **Strategic Ledger — Economy (no province left)** | `IQ10_LEDGER_COLLAPSE_NONE_ECONOMY_2026_09_19.png` · `IQ10_LEDGER_COLLAPSE_NONE_ECONOMY_X2_2026_09_19.png` | IQ-2's collapse state at zero provinces | PASS |
| **Diplomatic Ledger — Nations tab** | `IQ10_DIPLO_BOOT_NATIONS_2026_09_19.png` · `IQ10_DIPLO_BOOT_NATIONS_X2_2026_09_19.png` | the Nations tab at boot: the Cabinet block reads Talleyrand idle, no raw tag, nothing clipped | PASS |
| **Diplomatic Ledger — Treaties tab** | `IQ10_DIPLO_BOOT_TREATIES_2026_09_19.png` · `IQ10_DIPLO_BOOT_TREATIES_X2_2026_09_19.png` | the Treaties tab at boot: the Cabinet block reads Talleyrand idle, no raw tag, nothing clipped | PASS |
| **Diplomatic Ledger — Balance tab** | `IQ10_DIPLO_BOOT_BALANCE_2026_09_19.png` · `IQ10_DIPLO_BOOT_BALANCE_X2_2026_09_19.png` | the Balance tab at boot: the Cabinet block reads Talleyrand idle, no raw tag, nothing clipped | PASS |
| **Diplomatic Ledger — Talleyrand tab** | `IQ10_DIPLO_BOOT_TALLEYRAND_2026_09_19.png` · `IQ10_DIPLO_BOOT_TALLEYRAND_X2_2026_09_19.png` | the Talleyrand tab at boot: the Cabinet block reads Talleyrand idle, no raw tag, nothing clipped | PASS |
| **Diplomatic Ledger — Vassals tab** | `IQ10_DIPLO_BOOT_VASSALS_2026_09_19.png` · `IQ10_DIPLO_BOOT_VASSALS_X2_2026_09_19.png` | the Vassals tab at boot: the Cabinet block reads Talleyrand idle, no raw tag, nothing clipped | PASS |
| **Diplomatic Ledger — Nations (one province left)** | `IQ10_DIPLO_COLLAPSE_ONE_NATIONS_2026_09_19.png` · `IQ10_DIPLO_COLLAPSE_ONE_NATIONS_X2_2026_09_19.png` | IQ-2's collapse line on the diplomatic side; no raw tag | PASS |
| **Diplomatic Ledger — Talleyrand (coalition cooldown)** | `IQ10_DIPLO_COLLAPSE_COOLDOWN_TALLEYRAND_2026_09_19.png` · `IQ10_DIPLO_COLLAPSE_COOLDOWN_TALLEYRAND_X2_2026_09_19.png` | IQ-3's spent-league cooldown counsel, and the Cabinet block | PASS |
| **Diplomatic Ledger — Vassals (no province left)** | `IQ10_DIPLO_COLLAPSE_NONE_VASSALS_2026_09_19.png` · `IQ10_DIPLO_COLLAPSE_NONE_VASSALS_X2_2026_09_19.png` | the IQ-7 Vassals tab: the petition standing column, the honest chips | PASS |
| **Generals (Marshal Management)** | `IQ10_GENERALS_BOOT_2026_09_19.png` · `IQ10_GENERALS_BOOT_X2_2026_09_19.png` | the character sheets: skill bars, the glory ladder, GLORY & GRIEVANCES, no raw tag, nothing clipped at scale 2.0 | PASS |
| **Dispatch re-read (collapse board)** | `IQ10_DISPATCH_COLLAPSE_2026_09_19.png` · `IQ10_DISPATCH_COLLAPSE_X2_2026_09_19.png` | IQ-2's collapse headline leads; no raw tag; the rows are legible | PASS |
| **Mailbox / letter-book** | `IQ10_MAILBOX_BOOT_2026_09_19.png` · `IQ10_MAILBOX_BOOT_X2_2026_09_19.png` | the envoy rows with their courts named (article, no raw tag); the panel is not clipped (the IGR-F 600x400 defect) | PASS |
| **War Status HUD (boot)** | `IQ10_WAR_STATUS_BOOT_2026_09_19.png` · `IQ10_WAR_STATUS_BOOT_X2_2026_09_19.png` | the Third Coalition row, the tug-of-war bar filling its track | PASS |
| **War Status HUD (one province left)** | `IQ10_WAR_STATUS_COLLAPSE_ONE_2026_09_19.png` · `IQ10_WAR_STATUS_COLLAPSE_ONE_X2_2026_09_19.png` | the war rows on a collapsing France | PASS |
| **War Status HUD (no province left)** | `IQ10_WAR_STATUS_COLLAPSE_NONE_2026_09_19.png` · `IQ10_WAR_STATUS_COLLAPSE_NONE_X2_2026_09_19.png` | the war rows at zero provinces | PASS |
| **War Detail popup (boot)** | `IQ10_WAR_DETAIL_BOOT_2026_09_19.png` · `IQ10_WAR_DETAIL_BOOT_X2_2026_09_19.png` | the score breakdown incl. PT-J2's Campaign and Blood rows; the bar tracks | PASS |
| **War Detail popup (one province left)** | `IQ10_WAR_DETAIL_COLLAPSE_ONE_2026_09_19.png` · `IQ10_WAR_DETAIL_COLLAPSE_ONE_X2_2026_09_19.png` | a losing score, named honestly | PASS |
| **War Detail popup (no province left)** | `IQ10_WAR_DETAIL_COLLAPSE_NONE_2026_09_19.png` · `IQ10_WAR_DETAIL_COLLAPSE_NONE_X2_2026_09_19.png` | the worst case: no cheerful wording | PASS |
| **Incoming settlement offer (losing France)** | `IQ10_INCOMING_PEACE_LOSING_2026_09_19.png` · `IQ10_INCOMING_PEACE_LOSING_X2_2026_09_19.png` | the offer's terms and its ASK/OFFER direction (the FA-S17 'paid the loser' fix); three buttons, each with its own action; no raw tag | PASS |
| **Proposal confirm — drafted peace (losing France)** | `IQ10_CONFIRM_PEACE_LOSING_2026_09_19.png` · `IQ10_CONFIRM_PEACE_LOSING_X2_2026_09_19.png` | the confirm snapshot: the terms, the acceptance components, the agenda modifier; the IGR-G relax pass keeps the per-court table readable | PASS |
| **Enemy-phase dialog (collapse board)** | `IQ10_ENEMY_PHASE_COLLAPSE_2026_09_19.png` · `IQ10_ENEMY_PHASE_COLLAPSE_X2_2026_09_19.png` | every AI action as prose (no snake_case verb); IQ-5's casualty scope on both sides; the battle lines carry their '⚔ View the field' link | PASS |
| **Top bar — diplomatic fields** | `IQ10_TOP_BAR_BOOT_2026_09_19.png` · `IQ10_TOP_BAR_BOOT_X2_2026_09_19.png` | IQ-4's Cabinet line: 'Talleyrand: Idle' where the backend says 'None' — never the raw word None | PASS ⚠ offscreen@2.0 |
| **Strategic Ledger — the Cabinet block (COURT_NATION running)** | `IQ10_LEDGER_MISSION_COURT_FORCES_2026_09_19.png` · `IQ10_LEDGER_MISSION_COURT_FORCES_X2_2026_09_19.png` | the Cabinet block naming the mission, its court, the DP a turn and the favour | PASS |
| **Strategic Ledger — the Cabinet block (IMPROVE_RELATIONS running)** | `IQ10_LEDGER_MISSION_IMPROVE_FORCES_2026_09_19.png` · `IQ10_LEDGER_MISSION_IMPROVE_FORCES_X2_2026_09_19.png` | the Cabinet block's effect / drift / net arm | PASS |
| **Strategic Ledger — the Cabinet block (GATHER_INTEL running)** | `IQ10_LEDGER_MISSION_GATHER_FORCES_2026_09_19.png` · `IQ10_LEDGER_MISSION_GATHER_FORCES_X2_2026_09_19.png` | the Cabinet block's effect-text arm | PASS |
| **Strategic Ledger — the Cabinet block (UNDERMINE_ALLIANCE running)** | `IQ10_LEDGER_MISSION_UNDERMINE_FORCES_2026_09_19.png` · `IQ10_LEDGER_MISSION_UNDERMINE_FORCES_X2_2026_09_19.png` | the pair the mission moves, not the player pair | PASS |
| **Strategic Ledger — the Cabinet block (in transit with a proposal)** | `IQ10_LEDGER_MISSION_TRANSIT_FORCES_2026_09_19.png` · `IQ10_LEDGER_MISSION_TRANSIT_FORCES_X2_2026_09_19.png` | the mission PAUSED while he carries a letter, and no Recall | PASS |
| **Strategic Ledger — the Cabinet block (starved of DP)** | `IQ10_LEDGER_MISSION_STARVED_FORCES_2026_09_19.png` · `IQ10_LEDGER_MISSION_STARVED_FORCES_X2_2026_09_19.png` | the mission suspended for want of DP, with its cost stated | PASS |
| **Strategic Ledger — the Cabinet block (recalled)** | `IQ10_LEDGER_MISSION_RECALLED_FORCES_2026_09_19.png` · `IQ10_LEDGER_MISSION_RECALLED_FORCES_X2_2026_09_19.png` | the desk empty and free to send again — MS-1's lockout gone | PASS |
| **Diplomatic Ledger — Talleyrand (courting)** | `IQ10_DIPLO_MISSION_COURT_TALLEYRAND_2026_09_19.png` · `IQ10_DIPLO_MISSION_COURT_TALLEYRAND_X2_2026_09_19.png` | the tab agrees with the Cabinet block: one source, one figure | PASS |
| **Diplomatic Ledger — Talleyrand (undermining)** | `IQ10_DIPLO_MISSION_UNDERMINE_TALLEYRAND_2026_09_19.png` · `IQ10_DIPLO_MISSION_UNDERMINE_TALLEYRAND_X2_2026_09_19.png` | the tab agrees with the Cabinet block: one source, one figure | PASS |
| **Diplomatic Ledger — Talleyrand (recalled)** | `IQ10_DIPLO_MISSION_RECALLED_TALLEYRAND_2026_09_19.png` · `IQ10_DIPLO_MISSION_RECALLED_TALLEYRAND_X2_2026_09_19.png` | the tab agrees with the Cabinet block: one source, one figure | PASS |
| **Notice rail — the mission row (court)** | `IQ10_RAIL_MISSION_COURT_2026_09_19.png` · `IQ10_RAIL_MISSION_COURT_X2_2026_09_19.png` | ONE mission row with a Recall, its court named, no raw key | PASS |
| **Notice rail — the mission row (improve)** | `IQ10_RAIL_MISSION_IMPROVE_2026_09_19.png` · `IQ10_RAIL_MISSION_IMPROVE_X2_2026_09_19.png` | ONE mission row with a Recall, its court named, no raw key | PASS |
| **Notice rail — the mission row (gather)** | `IQ10_RAIL_MISSION_GATHER_2026_09_19.png` · `IQ10_RAIL_MISSION_GATHER_X2_2026_09_19.png` | ONE mission row with a Recall, its court named, no raw key | PASS |
| **Top bar — a mission standing** | `IQ10_TOP_BAR_MISSION_COURT_2026_09_19.png` · `IQ10_TOP_BAR_MISSION_COURT_X2_2026_09_19.png` | IQ-4's Cabinet line naming the running mission, never 'Idle' beside a live one | PASS ⚠ offscreen@2.0 |
| **Client's Petition popup** | `IQ10_PETITION_POPUP_2026_09_19.png` · `IQ10_PETITION_POPUP_X2_2026_09_19.png` | the court with its article (never a raw tag); the price it quotes is the price the grant charges; Grant and Refuse each state their terms | PASS |
| **Client's Petition popup — the lord cannot pay** | `IQ10_PETITION_POPUP_NO_DP_2026_09_19.png` · `IQ10_PETITION_POPUP_NO_DP_X2_2026_09_19.png` | Grant present but DISABLED with its stated reason (THE_LORD_PAYS_TO_GRANT), never absent and never silently live | PASS |
| **Envoys — a petition waiting** | `IQ10_MAILBOX_PETITION_2026_09_19.png` · `IQ10_MAILBOX_PETITION_X2_2026_09_19.png` | the petition row titled with the court's article, beside the routine letters | PASS |
| **Diplomatic Ledger — Vassals after a granted petition** | `IQ10_DIPLO_PETITION_GRANTED_VASSALS_2026_09_19.png` · `IQ10_DIPLO_PETITION_GRANTED_VASSALS_X2_2026_09_19.png` | the bond and the standing after the grant — not 'N turns until it may ask' while the ask is answered | PASS |
| **Battle Diorama (attacker adjusted)** | `IQ10_DIORAMA_AADJ_2026_09_19.png` · `IQ10_DIORAMA_AADJ_X2_2026_09_19.png` | the order of battle with each contingent's own losses; IQ-5's scope label on the reinforced side; the verdict in Berthier's voice | PASS |
| **Battle Diorama (defender adjusted)** | `IQ10_DIORAMA_DADJ_2026_09_19.png` · `IQ10_DIORAMA_DADJ_X2_2026_09_19.png` | the order of battle with each contingent's own losses; IQ-5's scope label on the reinforced side; the verdict in Berthier's voice | PASS |
| **Enemy-phase dialog (IQ-5 scope board)** | `IQ10_ENEMY_PHASE_IQ5_2026_09_19.png` · `IQ10_ENEMY_PHASE_IQ5_X2_2026_09_19.png` | the defender's casualties labelled by SCOPE (army vs corps) — the half IQ-5 could not show without a client pass | PASS |
| **Region Action Panel — Paris (own soil, Soult present)** | `IQ10_REGION_PARIS_2026_09_19.png` · `IQ10_REGION_PARIS_X2_2026_09_19.png` | the recruit chips, the levy line with the price HERE, the Substitutes row, Build/Repair | PASS |
| **Region Action Panel — Amsterdam (a vassal's province, Bernadotte present)** | `IQ10_REGION_AMSTERDAM_2026_09_19.png` · `IQ10_REGION_AMSTERDAM_X2_2026_09_19.png` | H1: the levy and the Substitutes row render on the soil that feeds France (the backend prices it: 598g / 3,193g) | PASS |
| **Region Action Panel — Milan (a vassal's province, Massena present)** | `IQ10_REGION_MILAN_2026_09_19.png` · `IQ10_REGION_MILAN_X2_2026_09_19.png` | H1 again on the Kingdom of Italy's soil, with the court named by its article | PASS |
| **Region Action Panel — Vienna (an enemy capital)** | `IQ10_REGION_VIENNA_2026_09_19.png` · `IQ10_REGION_VIENNA_X2_2026_09_19.png` | no levy rows, no raw tag, the garrison honestly fogged | PASS |
| **Generals — a captured marshal** | `IQ10_GENERALS_PRISONER_2026_09_19.png` · `IQ10_GENERALS_PRISONER_X2_2026_09_19.png` | the prisoner named as a prisoner with his captor — never an idle corps | PASS |
| **Strategic Ledger — Forces (t20 fixture)** | `IQ10_LEDGER_T20_FORCES_2026_09_19.png` · `IQ10_LEDGER_T20_FORCES_X2_2026_09_19.png` | the Forces tab on a played board — the case a boot frame cannot show | PASS |
| **Strategic Ledger — Economy (t20 fixture)** | `IQ10_LEDGER_T20_ECONOMY_2026_09_19.png` · `IQ10_LEDGER_T20_ECONOMY_X2_2026_09_19.png` | the Economy tab on a played board — the case a boot frame cannot show | PASS |
| **Strategic Ledger — Orders (t20 fixture)** | `IQ10_LEDGER_T20_ORDERS_2026_09_19.png` · `IQ10_LEDGER_T20_ORDERS_X2_2026_09_19.png` | the Orders tab on a played board — the case a boot frame cannot show | PASS |
| **Strategic Ledger — Admiralty (t20 fixture)** | `IQ10_LEDGER_T20_ADMIRALTY_2026_09_19.png` · `IQ10_LEDGER_T20_ADMIRALTY_X2_2026_09_19.png` | the Admiralty tab on a played board — the case a boot frame cannot show | PASS |
| **Diplomatic Ledger — Nations (t20 fixture)** | `IQ10_DIPLO_T20_NATIONS_2026_09_19.png` · `IQ10_DIPLO_T20_NATIONS_X2_2026_09_19.png` | the Nations tab on a played board | PASS |
| **Diplomatic Ledger — Treaties (t20 fixture)** | `IQ10_DIPLO_T20_TREATIES_2026_09_19.png` · `IQ10_DIPLO_T20_TREATIES_X2_2026_09_19.png` | the Treaties tab on a played board | PASS |
| **Diplomatic Ledger — Balance (t20 fixture)** | `IQ10_DIPLO_T20_BALANCE_2026_09_19.png` · `IQ10_DIPLO_T20_BALANCE_X2_2026_09_19.png` | the Balance tab on a played board | PASS |
| **Diplomatic Ledger — Vassals (t20 fixture)** | `IQ10_DIPLO_T20_VASSALS_2026_09_19.png` · `IQ10_DIPLO_T20_VASSALS_X2_2026_09_19.png` | the Vassals tab on a played board | PASS |
| **Generals (t20 fixture)** | `IQ10_GENERALS_T20_2026_09_19.png` · `IQ10_GENERALS_T20_X2_2026_09_19.png` | a played roster: glory, grievances, the ladder, the trust bars | PASS |
| **Dispatch re-read (t20 fixture)** | `IQ10_DISPATCH_T20_2026_09_19.png` · `IQ10_DISPATCH_T20_X2_2026_09_19.png` | the morning dispatch of a played turn: the headline, the beats, no raw tag | PASS |
| **Enemy-phase dialog (t20 fixture)** | `IQ10_ENEMY_PHASE_T20_2026_09_19.png` · `IQ10_ENEMY_PHASE_T20_X2_2026_09_19.png` | every AI action as prose; the battle lines and their field link | PASS |
| **War Status HUD (t20 fixture)** | `IQ10_WAR_STATUS_T20_2026_09_19.png` · `IQ10_WAR_STATUS_T20_X2_2026_09_19.png` | several wars at once: the rows fit, the bars track their containers | PASS |
| **War Detail popup (t20 fixture)** | `IQ10_WAR_DETAIL_T20_2026_09_19.png` · `IQ10_WAR_DETAIL_T20_X2_2026_09_19.png` | the breakdown on a played war; the exposure and weariness rows | PASS |
| **Le Moniteur (t20 fixture)** | `IQ10_GAZETTE_T20_2026_09_19.png` · `IQ10_GAZETTE_T20_X2_2026_09_19.png` | the issues with their captions; no raw tag; the columns fit at 2.0 | PASS |
| **Notice rail (t20 fixture)** | `IQ10_RAIL_T20_2026_09_19.png` · `IQ10_RAIL_T20_X2_2026_09_19.png` | the tray under its cap, CRITICAL first, each icon its own glyph | PASS |
| **Generals — Napoleon in the Seat (NP-5)** | `IQ10_GENERALS_NP_SEAT_2026_09_19.png` · `IQ10_GENERALS_NP_SEAT_X2_2026_09_19.png` | the Emperor's own card: the sovereign kit, the Seat, the Guard's strength | PASS |
| **Generals — Napoleon in the field** | `IQ10_GENERALS_NP_FIELD_2026_09_19.png` · `IQ10_GENERALS_NP_FIELD_X2_2026_09_19.png` | the Presence figure as APPLIED, and the star that dims | PASS |
| **Generals — the Eagle in Chains** | `IQ10_GENERALS_NP_CAPTIVE_2026_09_19.png` · `IQ10_GENERALS_NP_CAPTIVE_X2_2026_09_19.png` | a captured sovereign named as a captive — never commandable | PASS |
| **Generals — the flagship t12 board** | `IQ10_GENERALS_FLAGSHIP_T12_2026_09_19.png` · `IQ10_GENERALS_FLAGSHIP_T12_X2_2026_09_19.png` | the played roster the Aug-15 pass staged and never shot | PASS |
| **Strategic Ledger — Forces (Napoleon in the Seat)** | `IQ10_LEDGER_NP_SEAT_FORCES_2026_09_19.png` · `IQ10_LEDGER_NP_SEAT_FORCES_X2_2026_09_19.png` | the Emperor's corps in the muster, the Seat's +1 DP named | PASS |

## The older sign-offs (recon §1d)

| owed since | surface | status |
|---|---|---|
| Aug 16, 2026 (row NP) | the three staged Napoleon saves — Seat, field, the Eagle in Chains | **CAPTURED HERE** (`IQ10_GENERALS_NP_SEAT/FIELD/NP_CAPTIVE_*`), and the captive's card is the row's IQ10-1 |
| Aug 15, 2026 (flagship t12) | the played board the comprehensive playtest staged | **CAPTURED HERE** (`IQ10_GENERALS_FLAGSHIP_T12_*`) |
| Jul 31, 2026 (IGR-G) | the settlement popup's relax pass | **RE-CAPTURED** (`IQ10_CONFIRM_PEACE_LOSING_*`) |
| Sept 11–12 (FA slice 17) | the client half of the re-score | **PARTLY** — the Family-A surfaces are here; the terminal flows (S17/S18/S22/S24) are Family B and still owe a played session |

**Still owed to the user, and not dischargeable by a harness:** a human deciding
whether these screens FEEL right — the pacing of the diorama, whether the
ledger's density reads as rich or as noise, whether the tableau at 0.55 scale is
still dramatic. This pass proves what is on screen and what fits; it does not
prove what is good.

## Re-score

**UI/UX 7.5 → 7.5 (HELD), ⚠ FOR USER CONFIRMATION.**

The frames are better than the prior pass could show — honest availability is
real on the surfaces that carry it (the petition's Grant is dimmed WITH its
reason in the tooltip, `IQ10_PETITION_POPUP_NO_DP_*`), the diorama is a genuinely
composed tableau (`IQ10_DIORAMA_DADJ_*`), the region panel now states its terms
on ally soil, and 160 frames carry **no raw nation tag, no `<null>`, no
snake_case verb and one piece of double punctuation** (fixed).

It is held rather than raised because two of the seven defects are the same
failure — **a surface authored at a fixed size that does not fit the client's
own maximum Interface Scale** — and the third instance (the top bar) is routed,
not fixed. A score above 7.5 should wait until Interface Scale 2.0 is a
first-class case rather than a thing each surface remembers separately, and
until a human has looked.

## Method notes for the next pass

- **Read the machine record first, the pixels second.** `clipped_text`,
  `buttons_offscreen` and the text dump answered most questions in one grep;
  the PNGs then confirmed. Reading 160 frames by eye would have cost more and
  found less.
- **A payload is a fixture with a date.** Re-capture after a backend change or
  the frame shows the old copy — this pass shot the prisoner card twice for
  exactly that reason.
- **The capture harness can only shoot what a payload stages.** The two defects
  it could NOT have found are the ones needing a live flow (the terminal, the
  tutorial); those stay Family B and still owe a played session.
