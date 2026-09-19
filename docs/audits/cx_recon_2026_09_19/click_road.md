# THE CLICK ROAD — a census of every no-typing intent in the Godot client

Read-only recon, 2026-09-19, at `f7008582` (clean tree). Every row below was
read out of the `.gd` source; line numbers are from `cat -n` / `awk` on the
working tree today, not from any doc. Backend-authored strings were confirmed
by running the real builders on the 1805 boot world (probes in
`probes/`, results quoted inline).

**Scope walked:** all 45 scripts under `godot-client/project-sovereign/scripts/`
and all 9 `.gd` under `scenes/` (counted: `ls scripts/*.gd | wc -l` = 45,
`scenes/*.gd` = 9).

---

## §0 THE THREE ROADS (the shape of the finding)

Every non-typed affordance in this client is one of exactly three kinds. This
matters for the parser question, so it is stated first:

| Road | Mechanism | Ends at | Count |
|---|---|---|---|
| **A — typed-command echo** | builds a natural-language string and POSTs `/command` | the SAME parser a typed order hits | **~70 distinct strings** (§3) |
| **B — structured POST** | POSTs a non-`/command` endpoint with a machine payload | the executor / dialogue handler, **parser never runs** | **16 POST + 15 GET endpoints** (§2) |
| **C — local UI** | toggles, scroll, screen open/close, fill-the-line | nothing leaves the client | — |

Road A is the load-bearing one: **the click road and the typed road converge at
`backend/ai/llm_client.py`'s fast parser.** Every chip pays the parse cost, and
every chip is exposed to every parse defect. There is **no structured
fast-path** for chips — `send_structured_command` (`api_client.gd:151`) exists
but has only **three** call sites, all settlement/request-terms
(`main.gd:6462, 6573, 6592`; wizard payload at `diplomacy_wizard.gd:697-736`),
and even those still carry a free-text `command` string that the backend parses
as the primary route.

Two facts worth carrying into any parser work:

1. **The wizard emits raw nation TAGS, not display names.**
   `_add_nation_button` binds `nation_data["name"]` (`diplomacy_wizard.gd:303,
   326`) and renders `Utils.display_nation_name(nation_name)` beside it — proof
   the bound value is the tag. So the parser receives `propose peace with
   KingdomOfItaly` and `guarantee PapalStates`, never "Kingdom of Italy".
   `main.gd:6172` echoes it through `humanize_nation_keys_in_text()`, which
   confirms the string on the wire carries tags.
2. **Region-panel chips interpolate the LIVE region name verbatim** with no
   quoting (`region_panel.gd:272, 372, 412, 424, 462`), so any province whose
   name contains a parser-significant token rides straight in.

---

## §1 TABLE ONE — intent → click affordance → exact string / endpoint → file:line

Legend: **[A]** typed-command echo (`POST /command`) · **[B]** structured
endpoint · **[C]** local only.

### 1.1 Map + Region Action Panel (`region_panel.gd`, CanvasLayer 26)

Opened by a left-click on a wired province (`scenes/map_renderer_base.gd:2047-2055`
emits `region_clicked`; `main.gd:6362` `_on_map_region_clicked` opens the panel).
Meta router: `region_panel.gd:128-144` — `do:` = full command verbatim,
`order:<verb>:<Name>` → `"<Name>, <verb>"`, `negotiate:<Nation>` → wizard.

| Intent | Affordance | Label | Emits | File:line |
|---|---|---|---|---|
| Raise a battalion | chip ×3 | `Infantry` / `Cavalry` / `Artillery` | **[A]** `recruit <arm> in <Region>` | `region_panel.gd:271-272` |
| Buy substitutes | chip | `Buy Substitutes` | **[A]** `buy substitutes for <Marshal>` | `region_panel.gd:332` |
| — gated | disabled pill | `Buy Substitutes` | **[C]** reason only | `region_panel.gd:341` |
| Build works | chip ×5 | `Depot` / `Fort` / `Training Ground` / `Market` / `Stables` (+ `NNNg`) | **[A]** `build depot in <Region>` etc. — templates in `_BUILD_CHIP_DEFS` | `region_panel.gd:372, 375`; defs `:516-522` |
| Build watchtower | chip | `Watchtower NNNg` | **[A]** `build watchtower in <Region>` | `region_panel.gd:379, 382` |
| Repair a ruined building | chip | `Repair works NNNg` | **[A]** `repair buildings in <Region>` | `region_panel.gd:412` |
| Repair war damage | chip | `Repair war damage NNNg` | **[A]** `repair <Region>` | `region_panel.gd:424` |
| Lay a keel | chip | `Lay down ships (400g)` | **[A]** `build ships` | `region_panel.gd:441` |
| Open the court | chip | `Negotiate with <Nation>` | **[C]→wizard** `negotiate_requested` → `main.gd:6419` → `diplomacy_wizard.open_for_nation` | `region_panel.gd:444` |
| Land a corps | chip | `Land <Marshal> here` | **[A]** `land <Marshal> in <Region>` | `region_panel.gd:461-463` |
| — gated | disabled pill | `No landing here` | **[C]** backend reason | `region_panel.gd:475` |
| Fortify / unfortify | chip | `Fortify` / `Unfortify` | **[A]** `<Marshal>, fortify` / `<Marshal>, unfortify` | `region_panel.gd:545, 547` |
| Drill | chip | `Drill` | **[A]** `<Marshal>, drill` | `region_panel.gd:549` |
| Scout | chip | `Scout` | **[A]** `<Marshal>, scout` | `region_panel.gd:550` |
| Attack a visible enemy | chip ×≤2 | `Attack <Enemy>` | **[A]** `<Marshal>, attack <Enemy>` | `region_panel.gd:557` |
| Close the panel | X / ESC / right-click / sea-click / re-click | — | **[C]** | `region_panel.gd:77`; `main.gd:1079`, `6371-6372`, `6385-6388`; `map_renderer_base.gd:2059, 2065` |

Chip send pipeline: `main.gd:6399` `_on_region_panel_command` → history + echo +
`api_client.send_command` (`main.gd:6409`). Double-click guarded by the shared
`_chip_command_in_flight` latch (`main.gd:6281`).

### 1.2 Map itself (`scenes/map_renderer_base.gd`)

| Intent | Affordance | Effect | File:line |
|---|---|---|---|
| Select province | left-click | emits `region_clicked` | `:2041-2055` |
| Dismiss | right-click / open-water click | emits `map_dismiss_requested` | `:2059, 2065` |
| Zoom | wheel / `+` `-` / Alt+`+` Alt+`-` | **[C]** | `:2030-2035`, `:2234-2236`; Alt form `main.gd:979-986` |
| Recenter | `Home` / Alt+Home | **[C]** | `:2238`; `main.gd:975` |
| Cycle map fill mode | `M` / Alt+M | **[C]** emits `map_mode_changed` → `main.gd:6391` prints the mode | `:2240-2244`; `main.gd:968` |
| Pan | middle-drag / arrow keys | **[C]** | `:2037-2040`, `:2082-2090` |
| Hover a province | mouse move | **[C]** tooltip | `:2163`, `scenes/map_tooltip_layer.gd` |

War-table pieces (`scenes/war_table_piece.gd`) carry **no** input handler — they
are display-only.

### 1.3 Generals / Marshal Management (`marshal_management.gd`, G / Alt+G)

Meta router `:151-172`.

| Intent | Affordance | Label | Emits | File:line |
|---|---|---|---|---|
| Reward a marshal | chip | `Reward — estate or rente…` | **[C]→dialog** `reward_requested(card)` → `main.gd:6183` opens `reward_dialog` | `:564` |
| — gated (4 arms) | disabled pill | `Reward…` | **[C]** stated reason | `:529, 561, 571, 578` |
| Open the bench | chip | `Commission a Marshal…` | **[C]** local view flip | `:304`, handler `:157` |
| Back to roster | chip | `← Back to the Marshalate` | **[C]** | `:315`, handler `:160` |
| Commission a candidate | chip | `Commission <Name> — N,NNNg` | **[A]** `commission <Name>` (built `main.gd:6221`) | `:362`; handler `:163-166` |
| Fortify / unfortify | chip | `Fortify` / `Unfortify` | **[A]** `<Marshal>, fortify` / `unfortify` | `:650, 652` |
| Drill | chip | `Drill` | **[A]** `<Marshal>, drill` | `:654` |

⚠ Asymmetry worth noting: the Generals card offers **no Scout and no Attack**
chip; the region panel offers both. Same marshal, two surfaces, different verb
sets (`marshal_management.gd:648-656` vs `region_panel.gd:545-557`).

### 1.4 Reward dialog (`reward_dialog.gd`, CanvasLayer 109)

Dynamic buttons, `_add_option(label, command, colour)` at `:171-179`; press →
`reward_command` → `main.gd:6252` `_on_reward_command` → `send_command`.

| Intent | Label | Emits | File:line |
|---|---|---|---|
| Endow an estate | `Endow <Region> — NNNg/turn — covers…  [+NNNg investiture]` | **[A]** `endow <Marshal> with <Region>` | `:113-117` |
| Grant / re-size a rente | `Grant rente — NNg/turn to him, NNg/turn from the treasury` | **[A]** `grant <Marshal> a rente` | `:132-138` |
| Revoke a rente | `Revoke his rente — keep NNg/turn…` | **[A]** `revoke <Marshal>'s rente` | `:146-150` |
| Cancel | `Cancel` | **[C]** | `:28, 189` |

### 1.5 Notice rail (`notification_bar.gd`)

| Intent | Affordance | Label | Emits | File:line |
|---|---|---|---|---|
| Expand a notice | icon button | glyph | **[C]** detail panel | `:438` |
| Primary action | full-width button | `details.action_label` (backend) | **[A]** `details.action_command` (backend) → `main.gd:6224` → `_on_reward_command` | `:598-614` |
| Review | button | `details.review_label` (default `Open Ledger`) | **[C]→screen/dialog** `main.gd:5849` router | `:621-633` |
| Keep | button | `Keep` | **[C]** close panel | `:635-639` |
| Acknowledge | button | `Acknowledge` | **[B]** `POST /notifications/dismiss {id}` | `:641-645`; `api_client.gd:226` |
| Dismiss all | — | — | **[B]** `POST /notifications/dismiss {id:"all"}` | `:744`; `api_client.gd:252` |

`action_command` has exactly **two** producers in the backend (AST-free grep,
`backend/`): `dotation.py:1104` → `grant {marshal.name} a rente`, and
`diplomatic_dialogue.py:611` → `mission_recall_command(world)` =
`Talleyrand, cancel mission with {target}` (`:383-388`).

Review-target router (`main.gd:5849-5883`) resolves: `diplomacy_wizard`,
`ally_settlement_petition_popup`, `marshal_reward` (opens the reward dialog on
`route_id` = the marshal's name), `settlement_review` / `ledger_settlements`,
`diplomatic_ledger`, any `ledger_*`.

### 1.6 Strategic Ledger (`strategic_ledger.gd`, T / Alt+T)

Meta router `:1151-1162`.

| Intent | Affordance | Label | Emits | File:line |
|---|---|---|---|---|
| Cancel a standing order | link | `[Cancel]` | **[B]** `POST /cancel_order {marshal}` | `:1090`, `:1153-1156`; `api_client.gd:218` |
| Recall Talleyrand | link | `[Recall]` | **[A]** backend `cabinet.recall_command` = `Talleyrand, cancel mission with <Nation>` | `:1043-1045`; producer `diplomatic_dialogue.py:461` |
| Admiralty orders | chip | backend `label` | **[A]** backend `command` | `:820`; producer `naval.py:2756-2868` |
| — gated | disabled pill | backend `label` | **[C]** backend `reason` | `:829` |
| Switch tab | number keys / tabs | — | **[C]** | `:52-60` |

Measured (`probes/p2_chips.py`, 1805 boot, `historical` seed) — the Admiralty
chip set actually shipped:

```
command='blockade the enemy'   label='Blockade the enemy'                 enabled=True
command='order the diversion'  label='The Grand Diversion'                enabled=True
command='build ships'          label='Lay down ships (400g at Bordelais)' enabled=True
```

A fourth exists only while posture is already `blockade`:
`command='guard home waters'`, `label='Recall to home waters'`
(`naval.py:2759-2764`). At boot the Cabinet block is `{"live": false}` — the
Recall link only renders with a running mission.

### 1.7 Diplomatic Ledger (`diplomatic_ledger.gd`, D / Alt+D)

Meta router `:1640-1667`. Command builder `_vassal_chip_command` `:1670-1682`
(its docstring claims byte-identity with `diplomacy_wizard._build_command` —
verified true for all four verbs).

| Intent | Affordance | Label | Emits | File:line |
|---|---|---|---|---|
| Invest in a vassal | chip | `Invest` | **[A]** `invest in <Nation>` | `:1591`, `:1675` |
| Loosen the rein | chip | `Loosen Rein` | **[A]** `increase autonomy <Nation>` | `:1591`, `:1677` |
| Tighten the rein | chip | `Tighten Rein` | **[A]** `decrease autonomy <Nation>` | `:1591`, `:1679` |
| Release a vassal | chip | `Release` | **[A]** `release <Nation>` | `:1591`, `:1681` |
| Cede a province | chip | `Cede Province…` | **[C]→wizard** `open_diplomacy_for` → `main.gd:6340` | `:1584`, `:1653-1657` |
| Ask Talleyrand | chip | `Assess the Situation` | **[A]** `Talleyrand, assess our situation` (built `main.gd:6357`) | `:1067`, `:1665-1667` |
| Expand a ratification / settlement row | link | headline text | **[C]** local toggle | `:656, 707, 727`; `:1642-1652` |

Chip send: `main.gd:6295` `_on_vassal_command`.

### 1.8 Diplomacy Wizard (`diplomacy_wizard.gd`, F1, or Diplomacy button)

Three steps. Step 1 = nation list (`/diplomatic_preview` GET) + a Formables
button. Step 2 = per-nation action buttons from the backend's `actions[]`.
Step 3 = formables (`/formables` GET).

| Intent | Affordance | Label source | Emits | File:line |
|---|---|---|---|---|
| Pick a court | button | `<display> — <state> — <relation>` | **[C]** step 2 | `:301-327` |
| Any diplomatic action | button | backend `display_name` + cost + effect | **[A]** `_build_command(action_id, nation, payload)` | `:566-609`; builder `:739-809` |
| Multi-war rescue | sub-button | `↳ <war_id>` | **[A]+war_id** structured | `:621-637`, `:706-723` |
| Pick a province to cede | sub-button | `↳ <Region> — income Ng, loyalty +N, they remit N%` | **[A]** `cede territory to <Nation>` **+ structured `region`** | `:639-670`, `:724-735` |
| Open Formables | button | `Formable Nations — states that could yet exist` | **[C]** step 3 | `:345-352` |
| Formable deep link | button | `↳ Open negotiations — <Court>` | **[C]** → step 2 at that court | `:429-448` |
| Open Envoys (gate notice) | button | `Open Envoys (N)` | **[C]→mailbox** | `:843-854` |
| Back / close | button / ESC | — | **[C]** | `:115-140`; `main.gd:1066-1069` |

`_build_command` (`:739-809`) is the single largest command factory in the
client: **28 action ids** (full strings in §3).

Two of those are structured-only by design: `open_settlement` and
`propose_white_peace` carry `war_id` and the free-text is display copy
(`:697-723`, and the comment at `:703-705` says the parser does not
auto-classify "white peace").

### 1.9 War HUD + War Detail (`war_status_panel.gd` 25, `war_detail_popup.gd` 30)

| Intent | Affordance | Label | Emits | File:line |
|---|---|---|---|---|
| Open a war card | row button | `<Opponent>` row | **[C]** `card_clicked` → `main.gd:6490` | `war_status_panel.gd:237-240` |
| Open an armistice card | row button | — | **[C]** | `:342, 357` |
| Open the coalition | header button | `<COALITION NAME>` | **[C]** | `:216-222` |
| Read a foreign war | row button (inert) | `<A> vs <B>` | **[C]** tooltip only, no press handler | `:369-394` |
| Negotiate peace | button | `Negotiate Peace` | **[C]→wizard** | `war_detail_popup.gd:565-575`; `main.gd:6542` |
| Diplomatic options | button | `Diplomatic Options` | **[C]→wizard** | `:642-651` |
| Target a member | button | `Target <Nation>` | **[C]→wizard** | `:618-628`; `main.gd:6548` |
| Open settlement | button | backend label (e.g. `Open Settlement`) | **[A]+structured** `propose common peace with <Nation>` + `{action, target_nation, war_id}` | `:578-588`; `main.gd:6554-6579` |
| — gated | disabled button | `Open Settlement` | **[C]** tooltip reason | `:591-598` |
| Request terms | button | `Request Terms` | **[A]+structured** `request terms from <Nation>` + `{action, target_nation, war_id}` | `:601-615`; `main.gd:6582-6598` |

### 1.10 Mailbox / letter-book (`mailbox_panel.gd`, CanvasLayer 119)

| Intent | Affordance | Label | Emits | File:line |
|---|---|---|---|---|
| Open a letter in full | row click | the letter | **[B]** `POST /mailbox/activate {mailbox_id}` | `:11`; `main.gd:6066-6073`; `api_client.gd:136` |
| Accept a routine ask | button | `Accept` | **[B]** `POST /mailbox/respond {mailbox_id, choice:"accept"}` | `:260-263`; `main.gd:5999-6004`; `api_client.gd:139` |
| Decline a routine ask | button | `Decline` | **[B]** `POST /mailbox/respond {..., choice:"reject"}` | `:266-269` |
| Close | X | — | **[C]** | `:42` |

### 1.11 Modal popups — every one is **[B]**, none parses

| Popup (layer) | Buttons | Endpoint + body | File:line |
|---|---|---|---|
| `objection_dialog` | `Trust <Marshal>…` / `Proceed as Ordered (…)` / `Compromise: …` | `POST /respond_to_objection {choice: "trust"\|"insist"\|"compromise"}` | `:56-58, 275-285`; `main.gd:4376-4395` |
| `interrupt_popup` | dynamic from backend `options[]`, labelled by `OPTION_LABELS` (13 entries: `Attack!`, `Commit the Attack`, `Go Around`, `Hold Position`, `Cancel Order`, `March to the Guns`, `Continue as Ordered`, `Attack Again`, `Follow Ally`, `Hold Current Position`, `Cancel Support`, `Fight to the Last`, `Attempt a Breakout`) + `(trust N)` | `POST /strategic_response {marshal_name, response_type, choice}` | `:23-37, 65-105`; `main.gd:5415-5424` |
| `capture_choice_dialog` | `PLUNDER (+Ng…)` / `SECURE (…)`, or estate stage `CONFISCATE (…)` / `RESPECT THE TITLE (…)` | `POST /capture_choice {choice, dialogue_id}` | `:30-35, 122-127`; `main.gd:4852-4880` |
| `glorious_charge_dialog` | `CHARGE! (2x damage dealt AND taken)` / `Restrain - Normal Attack` | `POST /respond_to_glorious_charge {choice}` | `:38-44, 125-131`; `main.gd:5188-5208` |
| `redemption_dialog` | 4 arms → `settle_account` / `grant_autonomy` / `administrative_role` / `dismiss` | `POST /respond_to_redemption {choice}` | `:38-44, 122-137`; `main.gd:4609+` |
| `marshal_petition_dialog` | dynamic from backend option ids (`acknowledge`, `promise`, `rebuke`, `command`, `let_be`, `mediate`, `reprimand`, `accept_breach`, `force_reconciliation`, `separate`, `concede`, `refuse`, `detach`, `stays`, `march_anyway`, `stand_down`) + `Later` | `POST /marshal_petition_response {choice}`; `Later` sends **nothing** | `:44, 125, 143-151`; ids `backend/game_logic/jealousy.py:1869-2695`; `main.gd:6429-6435`, deferral `main.gd:2420` |
| `incoming_proposal_popup` | `Accept`/`Grant`/`Yield`, `Counter`, `Reject`/`Refuse`/`Defy`, `Not Now` | `POST /respond_to_diplomatic_dialogue {choice:"accept"\|"counter"\|"reject", dialogue_id}`; `dismiss` is local | `:25-28, 180-217`; `main.gd:5689-5704` |
| `proposal_confirm_popup` | options[] buttons + per-court table links (`focus:`, `addmenu:`, `group:`, `sugg:`, `suggopts:`, `suggcs:`, `suggpick:`, `rm:`, `mag:`) | `POST /respond_to_diplomatic_dialogue` with either a **1-based index**, an action string resolved to an index, or `action_params` (`send_dialogue_response_with_params`) | `:208-238, 295-302, 854-1056, 1060-1230`; `main.gd:5606-5687`; allowlist `main.gd:53-137` |
| `talleyrand_objection_popup` | `Proceed` / `Modify` / `Cancel` | `POST /respond_to_diplomatic_objection {choice, action?, target_nation?}` | `:29-31, 93-103`; `main.gd:5706-5716` |
| `sabotage_discovery_popup` | `Confront` / `Overlook` | `POST /respond_to_diplomatic_dialogue {choice:"confront_sabotage"\|"overlook_sabotage", dialogue_id}` | `:21-22, 57-62`; `main.gd:5718-5728` |
| `vassal_rebellion_popup` | `Invest` / `Garrison` / `Accept Risk` | `POST /respond_to_diplomatic_dialogue {choice:"invest_vassal_rebellion"\|"garrison_vassal_rebellion"\|"accept_vassal_rebellion", dialogue_id}` | `:24-26, 66-76`; `main.gd:5732-5746` |
| `commitment_paradox_popup` | `Honor <Defender>` / `Side with <Attacker>` / `Continue` | `POST /respond_to_diplomatic_dialogue {choice: 1\|2, dialogue_id}` — a **bare option index** | `:24-25, 73-81`; `main.gd:5748-5774` |
| `clarification_popup` | dynamic options | **[A]** — reissues `command` verbatim (`clarification_command`) or builds `<Marshal> <keyword> <Target>` | `:93-115`; `main.gd:5558-5599`; backend commands `backend/commands/clarification.py:157, 200, 253, 311, 363` |
| `strategic_report_popup` | `Continue` | **[C]** | `:30, 152` |
| `proclamation_popup` | `Acknowledge` | **[C]** | `:27, 113` |
| `enemy_phase_dialog` | `Continue`, Enter/ESC; `[url=diorama:N]` view-field links | **[C]** | `:46, 851-874`, `:538` |
| `battle_diorama` (121) | `Close` / `Replay` | **[C]** | `:445-454` |
| `load_dialog` | one button per save + `Cancel` | **[B]** `POST /load {filename}` | `:21, 46-49, 70`; `api_client.gd:206` |

### 1.12 Top bar, terminal chrome, menus

| Intent | Affordance | Effect | File:line |
|---|---|---|---|
| Open a screen | 6 top-bar buttons | **[C]** `toggle_screen(…)` | `top_bar.gd:101-106` |
| Open a screen (keyboard) | `L` `T` `G` `D` `R` `N` unfocused; `Alt+L/T/G/D/R/N` while typing | **[C]** | `main.gd:1105-1149`; `main.gd:899-920` |
| Open the Cabinet | `F1` (focused or not), Diplomacy button, terminal link `⚜ Take your seat at the table (F1)` | **[C]** wizard | `main.gd:911, 1097, 6145`, link `main.gd:1964` + `2405` |
| End the turn | End Turn button, `E`, `Alt+E`, Enter on the armed confirm | **[A]** `end turn` | `main.gd:1055, 1156, 953`; send `main.gd:1485` |
| Open envoys | Open Envoys button, envoy badge, dispatch-view button | **[C]→mailbox** (`GET /mailbox`) | `main.gd:5837, 546`; `dispatch_view.gd:26, 472` |
| Open the pause menu | `ESC`, top-bar gear | **[C]** | `main.gd:1064-1088`; `top_bar.gd:161` |
| Toggle the terminal | `Tab`, `Alt+Tab`, `` Alt+` `` | **[C]** | `main.gd:1161, 959` |
| Minimize / restore terminal | buttons | **[C]** | `main.gd:647-650` |
| Resize the terminal | grip drag / double-click | **[C]** | `main.gd:1233, 1255` |
| Text size | `+` / `−` buttons | **[C]** global `content_scale_factor` | `main.gd:1192-1195` |
| View the last field | terminal link `⚔ View the field` / `⚓ View the action` | **[C]** diorama | `main.gd:3001, 3146`, `2397-2402` |
| Expand a log turn | header button | **[C]** | `campaign_log.gd:102` |
| Page the Gazette | `prev` / `next` | **[C]** | `gazette_view.gd:32, 37` |
| Save | pause `Save Game` | **[B]** `POST /save {save_name:"quicksave"}` | `pause_menu.gd:42`; `main.gd:6684-6687` |
| Load | pause `Load Game` → load dialog | **[B]** `POST /load` | `pause_menu.gd:43` |
| New game | pause `New Game` → confirm | **[B]** `POST /new_game {}` | `pause_menu.gd:44-46` |
| Leave to menu | pause `Main Menu` | **[C]** scene change | `pause_menu.gd:48`; `main.gd:817` |
| Quit | pause `Quit` | **[C]** | `pause_menu.gd:49` |
| Interface scale | slider + `Reset to 100%` | **[C]** | `settings_panel.gd:91, 106-108` |
| Bus volumes | 4 sliders | **[C]** | `settings_panel.gd:155-163` |
| Battle sounds | toggle `Battle sounds` | **[C]** | `settings_panel.gd:144-146` |
| Parser key | `Apply key` / `Clear (use .env)` | **[B]** `POST /config/llm {api_key}` | `settings_panel.gd:188-197, 248` |
| Spoken orders | text only ("press Win+H") | **[C]** — OS dictation TYPES into the line; it is the typed road | `settings_panel.gd:292-303` |

### 1.13 Main menu (`main_menu.gd`)

| Intent | Label | Effect | File:line |
|---|---|---|---|
| Return | `Return to the War Room` | **[C]** scene change, no action | `:229, 422` |
| Begin | `Begin the 1805 Campaign` (confirm `Confirm — begin anew`) | **[B]** `POST /new_game {}` via `main.gd:6703` `_on_pause_new_game_requested` | `:230, 426-435`; consumed `main.gd:786-802` |
| Tutorial | `The School of War — a guided campaign` | **[B]** `POST /new_game {"scenario":"tutorial"}` | `:258, 438-455`; `main.gd:6719` |
| Continue | `Continue  ·  <date>` | **[B]** `GET /saves` then `POST /load {filename}` | `:259, 459`; `main.gd:798, 811` |
| Load | `Load a Campaign…` | **[B]** load dialog → `POST /load` | `:260, 463` |
| Settings | `Settings` | **[C]** shared `settings_panel` | `:261` |
| Quit | `Quit to Desktop` | **[C]** | `:262, 467` |
| Backend health | — | **[B]** `GET /test`, `GET /saves` | `:506, 521` |

### 1.14 Tutorial overlay (`tutorial_overlay.gd`, layer 90) — **fills, never sends**

| Intent | Affordance | Effect | File:line |
|---|---|---|---|
| Try the suggested order | chip `✎ <suggest>` | **[C]** writes the string into `command_input`, grabs focus; the player presses Enter | `:513`, `:526-528`; handler `main.gd:6721-6730` |
| Conclude | chip `Conclude the lesson` | **[C]** | `:518, 529-530` |
| Minimize / restore / skip | buttons | **[C]** | `:533-552` |

This is the one affordance in the whole client that is explicitly designed to
NOT bypass the parser (`:15-16` comment). All 11 non-empty `suggest` strings are
listed in §3.

---

## §2 TABLE TWO — every non-`/command` endpoint the client POSTs (and the GETs)

All of these bypass the parser entirely. `api_client.gd` is the complete
inventory except for the three scripts that own their own `HTTPRequest`
(`diplomacy_wizard.gd:63`, `main_menu.gd:506`, `settings_panel.gd:53`).

### 2.1 POST — the click-only action roads

| Endpoint | Body | Sent from | Typed equivalent? |
|---|---|---|---|
| `/respond_to_objection` | `{choice}` | `objection_dialog` | **yes** — `dialogue_routing` accepts typed answers (`backend/main.py:25`, `:3248`) |
| `/respond_to_diplomatic_dialogue` | `{choice, dialogue_id?}` or `{choice, action_params, dialogue_id?}` | 7 popups + settlement table | **yes** (typed answer routing), but the **index** and **`action_params`** shapes have **no typed form** — `main.gd:5629-5639` and `5624-5628` say so explicitly |
| `/respond_to_diplomatic_objection` | `{choice, action?, target_nation?}` | `talleyrand_objection_popup` | UNVERIFIED |
| `/respond_to_redemption` | `{choice}` | `redemption_dialog` | UNVERIFIED |
| `/respond_to_glorious_charge` | `{choice}` | `glorious_charge_dialog` | **yes** — `charge` / `restrain` are in `VALID_ACTIONS` (`validation.py:42-43`) |
| `/capture_choice` | `{choice, dialogue_id?}` | `capture_choice_dialog` | **yes** — typed `plunder`/`secure` (W6-0 `dialogue_id` guard) |
| `/marshal_petition_response` | `{choice}` | `marshal_petition_dialog` | UNVERIFIED |
| `/strategic_response` | `{marshal_name, response_type, choice}` | `interrupt_popup` | **partial** — `main.gd:5435-5437` states the typed `press on` answer exists but is unreachable while the modal is up |
| `/cancel_order` | `{marshal}` | Ledger `[Cancel]` | **yes** — `"cancel"` is in `VALID_ACTIONS` (`validation.py:44`) |
| `/mailbox/activate` | `{mailbox_id}` | mailbox row click | **no** |
| `/mailbox/respond` | `{mailbox_id, choice}` | letter-book Accept/Decline | **no** — added because the W6-0 guard refuses a queued row's `dialogue_id` (`api_client.gd:140-142`) |
| `/notifications/dismiss` | `{id}` or `{id:"all"}` | rail Acknowledge / sweep | **no** |
| `/save` | `{save_name}` | pause Save | **no** — no save verb in `VALID_ACTIONS` |
| `/load` | `{filename}` | load dialog, menu Continue | **no** |
| `/new_game` | `{}` or `{"scenario":"tutorial"}` | pause New Game, menu Begin/Tutorial | **no** |
| `/config/llm` | `{api_key}` | Settings `Apply key` / `Clear` | **no** |

### 2.2 GET — read roads (no typed equivalent; the parser is not involved)

`/test`, `/campaign_log`, `/dispatch`, `/gazette`, `/ledger`,
`/diplomatic_ledger`, `/marshal_overview`, `/pending_envoy`, `/mailbox`,
`/map_topology`, `/pending_redemption`, `/saves`, `/config/llm`,
`/diplomatic_preview` (`diplomacy_wizard.gd:157`), `/formables`
(`diplomacy_wizard.gd:182`).

### 2.3 Dead / unreachable

- **`api_client.get_marshal_trust()` (`:85`) has zero callers** anywhere in the
  client — `GET /marshal_trust/{name}` (`backend/main.py:4552`) is unreachable
  from the UI.
- Backend endpoints the client never touches: `/authority_status`,
  `/debug/*` (13 of them), `/debug_marshal/{name}`, `/delete_save`,
  `/diplomatic_preview` **POST** (`backend/main.py:5656`; the client only GETs),
  `/notifications` GET, `/pending_objection`, `/status`.

---

## §3 EMITTED_STRINGS — every chip/button string that reaches the parser

Exhaustive and literal. Templated slots are substituted with names measured off
the real 1805 boot (`probes/p1_boot.py`): marshals `Ney · Davout · Soult ·
Lannes · Murat · Bernadotte · Massena · Napoleon`; player regions include
`Paris (capital) · Rhineland · Lorraine · Berry · Artois · Gascony`; courts are
raw tags `Austria · Britain · Russia · Prussia · Holland · KingdomOfItaly ·
PapalStates …`.

`[T]` marks a template; `[T-tag]` marks a template whose slot is filled with a
**raw nation tag**, not a display name; `[B]` marks a string built in the
BACKEND and rendered verbatim by the client; `[F]` marks a string that only
FILLS the command line (tutorial) and is sent only if the player presses Enter.

```EMITTED_STRINGS
recruit infantry in Rhineland
recruit cavalry in Rhineland
recruit artillery in Rhineland
buy substitutes for Ney
build depot in Rhineland
build fort in Rhineland
build training ground in Rhineland
build market in Rhineland
build stables in Rhineland
build watchtower in Rhineland
repair buildings in Rhineland
repair Rhineland
build ships
land Soult in Munster
Ney, attack Mack
Ney, fortify
Ney, unfortify
Ney, drill
Ney, scout
commission Grouchy
endow Ney with Swabia
grant Ney a rente
revoke Ney's rente
Talleyrand, cancel mission with Austria
blockade the enemy
guard home waters
order the diversion
invest in Holland
increase autonomy Holland
decrease autonomy Holland
release Holland
cede territory to Holland
Talleyrand, assess our situation
sponsor Prussia, 200 gold
sponsor Prussia against Austria, 200 gold
buy off Prussia
guarantee Prussia
propose armistice with Austria
propose peace with Austria
propose common peace with Austria
propose white peace with Austria
propose open borders with Austria
propose non aggression with Austria
propose defensive alliance with Austria
propose alliance with Austria
propose vassalization to Austria
declare war on Austria
break treaty with Austria
downgrade relations with Austria
send ultimatum to Austria
improve relations with Austria
court Austria
gather intel on Austria
reassure Austria
undermine Austria
request terms from Austria
end turn
never mind
Ney pursue Mack
Ney march to Paris
Ney support Davout
Ney hold Paris
Ney, attack Mack
Ney, move to Bohemia
Davout, support Ney
Talleyrand, send the Austria proposal
Talleyrand, harsh the Austria proposal
Talleyrand, generous the Austria proposal
Talleyrand, adjust the Austria proposal
Talleyrand, proceed the Austria proposal
Talleyrand, trust the Austria proposal
Talleyrand, begin the Austria proposal
Talleyrand, dismiss the Austria proposal
Talleyrand, reconsider the Austria proposal
Talleyrand, elaborate the Austria proposal
Talleyrand, review the Austria proposal
Talleyrand, accept the Austria proposal
Talleyrand, cancel the Austria proposal
Talleyrand, reject the Austria proposal
economy
Senarmont, move to Munich
Ney, defend
Senarmont, bombard Jellacic
Ney, attack Kienmayer
Davout, march to Franconia
Davout, move to Bohemia
Soult, recruit troops
Davout, scout Bohemia
```

### 3.1 Provenance of each block above

| Block | Template form | Source |
|---|---|---|
| `recruit <arm> in <Region>` | `[T]` `"recruit " + arm + " in " + _region`, arms `["infantry","cavalry","artillery"]` | `region_panel.gd:271-272` |
| `buy substitutes for <Marshal>` | `[T]` | `region_panel.gd:332` |
| `build <work> in <Region>` ×6 | `[T]` `_BUILD_CHIP_DEFS` + the watchtower literal | `region_panel.gd:372/375/379/382`, defs `:516-522` |
| `repair buildings in <Region>` / `repair <Region>` | `[T]` | `region_panel.gd:412, 424` |
| `build ships` | literal (two producers) | `region_panel.gd:441`; `naval.py:2862` |
| `land <Marshal> in <Region>` | `[T]` | `region_panel.gd:462` |
| `<Marshal>, attack <Enemy>` | `[T]` | `region_panel.gd:557` |
| `<Marshal>, <fortify\|unfortify\|drill\|scout>` | `[T]` built by the `order:` router `"<Name>, <verb>"` | `region_panel.gd:130-134, 545-550`; `marshal_management.gd:167-172, 650-654` |
| `commission <Name>` | `[T]` | `main.gd:6221`, chip `marshal_management.gd:362` |
| `endow <M> with <R>` / `grant <M> a rente` / `revoke <M>'s rente` | `[T]` | `reward_dialog.gd:115, 136, 148` |
| `grant <M> a rente` (rail) | `[T][B]` | `backend/game_logic/dotation.py:1104` |
| `Talleyrand, cancel mission with <Nation>` | `[T-tag][B]` — two surfaces | `diplomatic_dialogue.py:383-388`; rendered `strategic_ledger.gd:1045`, rail `notification_bar.gd:598`; also built client-side by the wizard `diplomacy_wizard.gd:808` |
| `blockade the enemy` / `guard home waters` / `order the diversion` / `build ships` | `[B]` literals | `naval.py:2761, 2801, 2814, 2825, 2845, 2862` |
| vassal quartet | `[T-tag]` — TWO independent builders that must agree | `diplomatic_ledger.gd:1673-1682` and `diplomacy_wizard.gd:786-793` |
| `cede territory to <Nation>` | `[T-tag]` display echo; the real payload is structured `region` | `diplomacy_wizard.gd:796`, `:724-735` |
| `Talleyrand, assess our situation` | literal | `main.gd:6357` |
| `sponsor …` (2 forms) | `[T-tag]` amount from backend chip, default 200 | `diplomacy_wizard.gd:746-751`; producer `diplomacy.py:11878-11885` |
| all `propose …` / `declare war` / `break treaty` / `downgrade` / `send ultimatum` / `buy off` / `guarantee` | `[T-tag]` | `diplomacy_wizard.gd:752-785` |
| all `mission_*` verbs | `[T-tag]` | `diplomacy_wizard.gd:797-806` |
| `request terms from <Nation>` | `[T-tag]` + structured | `main.gd:6588` |
| `propose common peace with <Nation>` | `[T-tag]` + structured — two surfaces | `diplomacy_wizard.gd:761`; `main.gd:6569` |
| `end turn` | literal | `main.gd:1485` |
| `never mind` | literal — clarification cancel | `main.gd:5596` |
| `<M> <pursue\|march to\|support\|hold> <T>` | `[T]` clarification keyword map | `main.gd:5566-5575` |
| `<M>, attack <E>` / `<M>, move to <R>` / `<M>, support <M2>` | `[T][B]` clarification option commands, reissued verbatim | `backend/commands/clarification.py:157, 200, 253, 311, 363`; reissue `main.gd:5585` |
| `Talleyrand, <keyword> the <Nation> proposal` ×14 | `[T-tag]` — the proposal-popup **fallback** path, only when an action has no matching option index | `main.gd:5662-5687` |
| tutorial suggests ×11 | `[F]` | `tutorial_overlay.gd:58-233` (`"suggest"` keys) |

### 3.2 Notes the parsing agent will want

- **`cede territory to <Nation>` is display copy only** — the click road relies
  on the structured `region` field (`diplomacy_wizard.gd:724-735`). If it parses
  to something, that is a bonus, not a contract.
- **`propose white peace with <Nation>`**: `diplomacy_wizard.gd:763-767` states
  in code that the backend parser does **not** auto-classify "white peace" — it
  is display copy plus a structured payload. Same for `open_settlement`.
- **`sponsor Prussia, 200 gold`** (the no-aim/licence form) is emitted only when
  the backend chip ships an empty `aim`; the backend's own producer always sets
  one (`diplomacy.py:11884`), so the bare form is **UNVERIFIED as reachable**.
- **`Talleyrand, <keyword> the <Nation> proposal`** is the documented *fallback*
  and the comment at `main.gd:5660` calls it "old keyword path". Reachable only
  when the popup's action is absent from `options[]` and not in
  `SETTLEMENT_DIALOGUE_ACTIONS`. **UNVERIFIED as reachable in normal play**, but
  it is live code with no guard.
- The tutorial's suggests already have a backend pin
  (`test_tutorial_position7.py::test_every_suggest_mock_parses`,
  named at `tutorial_overlay.gd:47-48`), so they are the one block with
  existing coverage.

---

## §4 What the census says about routing to the LLM

Stated as measurement, not opinion:

1. **Every chip pays the parse.** 70-odd strings, 100% of them, go through
   `/command`. There is no `action_id` fast path for a chip, even though the
   chip already knows the exact action id it means (`region_panel.gd` builds
   `"recruit infantry in Rhineland"` from an arm string it holds in a loop
   variable; `diplomacy_wizard._build_command` switches on `action_id` and then
   throws it away except for the five structured cases).
2. **The strings chips emit are the narrowest possible grammar** — fixed verb,
   fixed preposition, one or two proper nouns. They are exactly the shapes a
   deterministic matcher handles best, so a chip escalating to the LLM would be
   pure waste. Whether any do is the other agent's measurement.
3. **The tags problem is a click-road problem, not a typing problem.** A human
   types "Italy"; the wizard types `KingdomOfItaly`. Any fuzzy/typo layer tuned
   on human spelling is being fed machine spelling from this road.
4. **16 POST endpoints already bypass the parser** and nothing has broken, which is
   the existence proof that a structured chip road is compatible with this
   architecture.

---

## §5 UNVERIFIED / not established

- Whether any emitted string actually escalates to the LLM (out of scope here;
  §3's block is the input to that measurement).
- Typed equivalence for `/respond_to_diplomatic_objection`,
  `/respond_to_redemption`, `/marshal_petition_response` — I did not trace
  `dialogue_routing`'s coverage of those three families.
- Reachability of `sponsor <N>, <amount> gold` (no-aim form) and of the
  `Talleyrand, <keyword> the <N> proposal` fallback.
- `expedition_landings` was `{}` on the turn-0 boot (`probes/p2_chips.py`), so
  the `land <M> in <R>` chip's exact rendering was read from source, not seen
  live.
- Backend `display_name` labels for wizard actions were read from
  `diplomacy.py` (`Declare War`, `Send Ultimatum`, `Break Treaty`, `Downgrade`,
  `Propose Armistice/Peace/Open Borders/Non-Aggression/Vassal/Alliance/Defensive
  Alliance`, `Improve Relations`, `Court Nation`, `Gather Intel`, `Undermine
  Alliances`, `Reassure Ally`, `Sponsor Their Design (Ng/turn)`, `Buy Off Their
  Design (Ng)`, `Guarantee Their Borders`, `Cancel: <Mission Type>`); I did not
  enumerate every state-branch's exact subset.

## §6 Probes

- `probes/p1_boot.py` — boots `europe_1805.json`, dumps player nation, the 8
  French marshals, 12 French provinces, capital, and the 19 enemy tags.
- `probes/p2_chips.py` — builds the real strategic ledger and naval overlay;
  printed the 3 live Admiralty chip commands, `cabinet: {"live": false}`,
  `player_dockyards: ['Bordelais','Brittany','Flanders','Provence']`,
  `ship_cost: 400`, `expedition_landings: {}`.
- `probes/p3_map.py` — failed (no `WorldState.get_map_summary`); the
  `recruit_price_here` / `substitute_price_here` / `levy` keys the region panel
  reads were instead confirmed at their producers,
  `backend/models/world_state.py:9272, 9281, 9330, 9470-9473`.
