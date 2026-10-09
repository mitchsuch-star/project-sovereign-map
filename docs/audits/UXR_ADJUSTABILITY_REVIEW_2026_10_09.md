# Adjustability review — is the UI good, what is missing, which buttons would help

> **Status: design memo, October 9, 2026 — FOR THE USER'S RULING before S1 is built.**
> Written at the user's direction at the head of S1 (`docs/PRE_DEPLOY_PLAN.md` §2):
> *"think abstract on adjustability — is UI good, anything missing, any buttons would
> help etc."* Every number here was measured on this machine today; §7 lists the
> decisions with their defaults. Nothing under it is built.

## 1. The frame the user actually sees

| Fact | Measured |
|------|----------|
| **The monitor** | ONE panel, **5120×1440**, Windows scaling **100%** (`Win32 GetDpiForMonitor` = 96; Godot `DisplayServer.screen_get_size(0)` = 5120×1440, `screen_get_dpi(0)` = 96, `screen_get_scale(0)` = 1.0). The plan assumed 3440×1440: its resolution set gains a fifth row, **and its formula "longest side ÷ 1920" is wrong for 32:9** — it would derive 2.67 and a 1920×540 logical screen. |
| **Pixel density** | A 5120×1440 panel at 100% is a 49-inch class: ≈ 108 PPI, **1 px = 0.235 mm**. |
| **The player's own settings** | `user://ui_settings.cfg` holds **no `display/ui_scale` and no terminal size**: every session so far has been played at Interface Scale **1.0** with the **400×270** default command window — 7.8% of the screen's width, 19% of its height. |
| **The body face** | EB Garamond (the theme's `default_font`, 16 px): cap height **0.69 em**, x-height **0.44 em**. The engine's fallback sans is 0.57 em — a Garamond gives up **23% of x-height at equal px**. (Cinzel headings 0.74/0.62; Cormorant menu buttons 0.66/0.42; IM Fell 0.71/0.49 — all via `TextServer.font_get_glyph_size`.) |
| **What that makes the type** | Tutorial card body 13 px → x-height **5.7 px = 1.3 mm**. Theme body 16 px → **7.0 px = 1.65 mm**. Settings hints 11 px → **4.8 px = 1.1 mm**. Comfortable reading x-height is ≈ 0.2° of visual angle; at the 80 cm a 49" panel is sat from, that is **2.8 mm = 12 px on this panel = a 27 px em in EB Garamond = Interface Scale 1.7** on the 16 px body. "I can't read most text" is the arithmetic. |
| **The HUD at 5120 wide** | Terminal bottom-left (`main.tscn` BottomLeftUI 400×270), war-status panel bottom-right (192×192 in the corner), the top bar's counters at the left edge and its nav at the right edge, the tutor card top-right (396 px). At 1.0 the corners are **4,300–5,000 px apart** — a head-turn — and nothing but the map fills the middle. |
| **The instrument** | IQ-10 shoots a 1600×900 window at scales 1.0 and 2.0. Today's probe proves a windowed Godot can be sized to **5120×1440 and even 3840×2160, parked entirely off the desktop (x = 5200), and still render a readable frame** — so the physical census can shoot every resolution without covering the player's screen. The probe also proves `Control.get_screen_transform()` does **not** carry `content_scale_factor` (scale 1.0 at factor 3.0): the census multiplies by the window's factor explicitly. |
| **Map labels** | `map_label_layer.gd` draws with `draw_string` (invisible to a node census). Province labels = clamp(13 × logical_zoom, 14, 34) logical px, nation labels clamp(34 × zoom, 22, 46), where logical_zoom = zoom ÷ scale — so at the zooms the player uses the **minimum clamp makes labels follow Interface Scale** (14 logical × 1.4 = 19.6 physical). Acceptable; UXR-3's eyes judge it. |

## 2. What the player can adjust today

(Census by a read-only agent over every `.gd`/`.tscn`; file:line in `§2a`.)

| Control | Where | Range / persistence |
|---------|-------|--------------------|
| Interface Scale slider + "Reset to 100%" | Settings (menu and pause, ONE shared code-built `SettingsPanel`) | 0.75 – **2.0**, step 0.05, `display/ui_scale`; previews live, saves at drag end (`settings_panel.gd:85-133`, `ui_settings.gd:43-47`) |
| Text Size + / − | the command window's header (`main.tscn:71-101`) | the same value in 0.1 steps; the percentage only in a tooltip; the buttons never disable at the limits (`main.gd:1534-1546`) |
| **One real grip** | the terminal: 20-px corner grip, double-click resets to 400×270 | width 300–1000, height 180–900; the only layout that is **remembered** (`terminal/width,height`; `main.gd:1548-1609`) |
| One hidden edge-drag | the war-status HUD: an invisible 6-px drag on its left/top edges, no resize cursor | width 150–500; **not saved**, and the height is re-fitted to content on every `update_wars`, so a dragged height is lost at the next refresh (`war_status_panel.gd:39-143`) |
| Minimize | the terminal (— button / Tab / Alt+`), the tutor card (– / "Berthier's lesson ▸"); folds inside the log, the diplomatic ledger and the proposal popup | session only; the card re-opens on every world swap |
| Clamp-to-viewport | **30** scripts call `Utils.clamp_centered_panel` (centre-anchored popups and screens) | shrinks into a small window; **nothing grows into a large one**. Not clamped at all: the war-detail popup (right-anchored 330×440), the tutor card, the notice rail |
| Compact top bar | automatic under 1,180 logical px (`top_bar.gd:63`) | — |
| Map | wheel zoom at the cursor; `=`/`−`, `Home`, `M` view mode (Alt+ forms while typing); middle-drag and arrow-key pan | zoom 0.05–2.5 in 10% steps; **no on-screen zoom or fit button; nothing about the view is saved**; no minimap |
| Sound | Battle sounds toggle; Master / Music / SFX / UI sliders | `audio/*` |
| Window | **none** — `project.godot` forces maximized (`window/size/mode=2`); no fullscreen / borderless / windowed toggle, no size picker, no vsync, no `[input]` map (nothing rebindable) | — |
| Theme sizes | ONE named variation, `HeadingLabel` (Cinzel 22) — **used by nothing**; 174 `.tscn` + 94 `.gd` raw overrides, 7–96 px, mode 12 | — |
| Text size apart from scale, font choice, contrast, colour-blind palette, reduced motion, reset-layout, a key reference, panel pinning, opacity | **none** | — |

**⚠ The plan's own count is wrong:** `UX_UI_REVIEW_PLAN.md` §0 says *"four surfaces
have a grip (the terminal, the region panel, the diplomatic ledger, the war-status
panel)"* — that grep matched *the Emperor's grip* in two files. There is one grip and
one hidden edge-drag. Corrected in S1's commit.

### 2b. Three defects the census found on the way (filed as rows in S1)

| Row | Defect | Evidence |
|-----|--------|----------|
| UXR-X1 (P2) | **The saved Interface Scale is not applied at launch.** `main_menu.gd` never reads `UiSettings.get_ui_scale()` in `_ready`; the first apply is `main.gd:760` when a campaign starts. A player who chose 150% sees the menu — and the first-run card, once it exists — at 100% every launch, while the slider reads 150%. | `main_menu.gd:86-119, 415-420`; `menu_boot.gd` |
| UXR-X2 (P3) | **The pause menu's Settings are squeezed.** The panel is authored 360×400 and the clamp treats 400 as its ceiling; the settings scroll's own minimum is 440, and it is the only shrinkable child, so it is cut toward the 48-px floor. | `pause_menu.tscn:32-44`, `pause_menu.gd:54-57`, `utils.gd:640-667, 700-767` |
| UXR-X3 (P2 at scale ≥ 2) | **The tutor card has no height bound.** Its body is `fit_content` with scrolling off and the card sets no bottom edge; card XIX is ≈ 1,400 characters. At Interface Scale 3.0 on a 1440-px panel the logical viewport is 480 px tall — the card runs off the screen, with no scrollbar, and the cap raise would create the case. UXR-1's card work bounds it (max height a viewport fraction + scroll). | `tutorial_overlay.tscn:26-34, 69-74`; `tutorial_overlay.gd:310` |

§2a — the agent's evidence table: see the appendix at the end of this memo.

## 3. Verdict

**Is the UI good?** The surfaces are rich, honest about availability, and the composition
is sound **at 1600×900** — the only window any frame was ever shot at. It is not
*adjustable* in the three ways a monitor like this one needs: nothing asks what screen
it is on, nothing grows to fill the room, and type has no floor. The whole adjustability
kit is one global scale capped at 2.0, one grip, and one hidden edge-drag that forgets.

**What the user reported is structural, not a tuning miss**: the default scale (1.0) is
right for a 24" 1080p panel and wrong for every panel bought since 2018; the 13-px
tutorial type is below any floor at any sensible scale; and the Garamond body costs a
quarter of the x-height a sans would give at the same size.

## 4. What is missing, ranked by reach

| # | Gap | What it would be | Cost | Where |
|---|-----|-------------------|------|-------|
| A | **No question asked of the screen** | Auto-derived Interface Scale at first boot + the one-screen "Can you read this?" card with a live sample; cap 2.0 → 3.0; a theme floor; the tutor card sized as a viewport fraction | in plan | **S1** |
| B | **No window control** | Settings → DISPLAY: *Fullscreen / Borderless / Windowed* and a size picker (*Native · 3440×1440 · 2560×1440 · 1920×1080*). On 32:9 a centred 3440-wide window is a legitimate way to play; today the game forces maximized. `DisplayServer.window_set_mode / window_set_size`, persisted beside the scale | 0.15 | **add to S1** |
| C | **The terminal's default is a 24"-monitor number** | Default footprint as a fraction of the logical viewport (e.g. 28% × 32%, floor 400×270, ceiling the grip's max) so the first thing a player types into is sized for the screen; the grip and the memory stay | 0.1 | **add to S1** |
| D | **Scale has no hotkey** | `Ctrl+=` / `Ctrl+−` / `Ctrl+0` (browser muscle memory) and `Ctrl+wheel` over the HUD, stepping the same value; the terminal's +/− stay | 0.05 | **add to S1** |
| E | **Nothing resets the layout** | "Reset layout" in Settings → INTERFACE: terminal size, panel sizes and the scale back to the auto value (the first-run card's sibling) | 0.05 | **add to S1** |
| F | **The body face is the dearest legibility cost after size** | Settings → INTERFACE: *Body text: Garamond (default) · Plain* — one Theme property swap (`default_font`, the Label/RichTextLabel/LineEdit/Button fonts) at boot; the July design stays the default | 0.1 | **add to S1** (or UXR-2) |
| G | **The hotkeys are taught once, on tutor card XIX** | Settings → CONTROLS: a static key reference (T G D R L N · F1 · Esc · Alt+letter while typing · the map's zoom) | 0.1 | S1 or UXR-3 |
| H | **Text size cannot be raised without enlarging the chrome** | A second slider *Text size* scaling the theme's named sizes only — on an ultra-wide the panels have room, the type is the problem. Needs UXR-2's override diet first (268 raw overrides ignore the theme), so it cannot land honestly in S1 | 0.3 | **UXR-2** |
| I | **Dim type** | *High contrast* toggle raising `UI_TEXT_DIM`-class text one step — the grey-on-navy 11-px hint style is the second killer after size | 0.2 | UXR-2 / UXR-3 |
| J | **The HUD spreads to the corners of a 49" panel** | *HUD width: Full · Centred* — confine the terminal, rail, top bar and war panel to a central band (≈ 2560 logical) with the map still full-bleed; the layout law's natural second rule | 0.4 | **UXR-2** |
| K | **Every ledger is a full-screen modal** | **"The Side Desk"**: pin the Strategic / Diplomatic Ledger or the Generals screen to the right third of an ultra-wide as a NON-modal dock while the war room stays live — the one feature a 32:9 player would name first. The layer-50 screens already render into a panel; the change is a second placement mode + a pin button on each header | 1.0 | a UXR-2 rider, its own gate |
| L | **Only the terminal remembers** | The war HUD's drag gets a visible grip and is persisted like the terminal's (`get/set_panel_size(name)`); the five big screens get grips (UXR-2's own row) | 0.1 | UXR-2 (in plan) |
| M | Colour-blind nation palette, reduced motion (Ken Burns, tweens) | review first | — | UXR-3 decides |

**Buttons that would help, specifically:** a **⌂ Fit Europe** button beside the map's
zoom (the capital-button idiom), a **⟲ Reset layout** in Settings, a **📌 pin** on
each ledger header (K), and — the one the plan already carries — the **first-run
card's slider with a live sample**, which is the only button most players will ever
need.

## 5. The scale formula (decision 3)

Godot ignores Windows scaling (it is DPI-aware), so the game must read it back. The
two signals available are the monitor's effective DPI (the player's own comfort
choice) and its pixel height; its physical size is not exposed. Proposed:

```
d = dpi / 96                      # the Windows scaling the player chose
h = height / 1080                 # 1.0 at 1080p, 1.33 at 1440p, 2.0 at 2160p
s = max(d, (d + h) / 2)           # never below the player's own scaling
if width / height >= 3.0: s += 0.25   # a 32:9 panel (3.56) is sat further from;
                                      # a 21:9 (2.39) is a 27-inch's distance
scale = clamp(round_to(s, 0.05), 1.0, 3.0)
```

*(Corrected at the build, October 9: the first draft wrote the term at 2.3,
which a 21:9 panel crosses — the driven probe showed 3440×1440 deriving 1.40
against this table's 1.15. The term is 3.0 in both twins and the test pins
the table.)*

| Monitor | derived |
|---------|---------|
| 1920×1080 @100% (24") | 1.00 |
| 2560×1440 @100% (27") | 1.15 |
| 3440×1440 @100% (34") | 1.15 |
| **5120×1440 @100% (this machine)** | **1.40** |
| 3840×2160 @150% (27" 4K, Windows default) | 1.75 |
| 3840×2160 @100% (43") | 1.50 |
| 1920×1080 @125% (15" laptop) | 1.25 |

At 1.40 on this panel the 16-px body becomes 22.4 px (x-height 2.3 mm) and the
tutor card 784 physical px wide; the card is where the player settles the last
0.2–0.4. The derived value is written only when no `display/ui_scale` exists and is
tagged `display/ui_scale_auto = true`, so a chosen scale is never overwritten.

## 6. The readability floor (decision 2)

The plan says "cap height under 16 px is RED, under 13 a P1" — but a 16-px cap
height is a 23-px em in this face, which would mark the theme's own 16-px body RED
at every scale under 1.45 and make 1080p unreachable. The industry floor is stated
on the **em** (16 px CSS body; Windows 12 px at 100%), with the face's x-height as
the reason to pick a face. Proposed:

- The census records, per visible text node and per resolution: **em, cap, x in
  physical px**, the face, the node path and the first 40 characters.
- **Body-class text** (theme `Body`/`Small` — every Label, RichTextLabel, Button,
  LineEdit not tagged otherwise): **RED under 16 px em, P1 under 13**.
- **Caption-class text** (nodes tagged `theme_type_variation = "Caption"`: badges,
  version lines, hints): **RED under 14 px em, P1 under 12** — a caption is
  secondary by design, and 0.85× body is the typographic norm.
- The user may move any of the four numbers after seeing the frames.

With UXR-1's floor (no raw override under 14; 10–13 → `Caption` 14, hints that
carry content → `Small` 14 or `Body` 16) and the derived 1.40, every row on the
five named surfaces clears the floor on this panel; at 1.0 on a 1080p panel the
Caption class clears 14 and the body clears 16. That is the done-when.

## 7. Decisions (each with a default; silence takes it)

1. **Resolutions.** The census shoots five: 1920×1080, 2560×1440, 3440×1440,
   **5120×1440**, 3840×2160; the committed BEFORE/AFTER frames are at 5120×1440.
   *Default: yes.*
2. **The floor** as §6 (em-based, two classes). *Default: yes.*
3. **The formula** as §5, with the ultra-wide term; cap 3.0. *Default: yes.*
4. **Add to S1:** B window mode + size picker · C terminal default as a viewport
   fraction · D scale hotkeys · E reset layout · G the CONTROLS reference.
   *Default: yes — S1 grows from 1.0 to ≈ 1.5 sessions, landed as two commits
   (S1a the instrument + the scale fix + the card; S1b the Settings additions).*
5. **F the Plain-font option** in S1 (default Garamond). *Default: yes.*
6. **H / I / J / L** filed as UXR-2 rows; **K "The Side Desk"** filed as a UXR-2
   rider with its own gate. *Default: file them; build nothing of them in S1.*
7. **The first-run card asks ONE question** (the scale, with a live sample); window
   mode and font live in Settings, not on the card. *Default: yes.*

## 8. Landing addendum — S1a built October 9, 2026 ("go")

All seven decisions were taken at their defaults and S1a (UXR-0 + UXR-1) landed the same
day; the record is `docs/UX_UI_REVIEW_PLAN.md` §UXR-1 landing record and the rules
`SYSTEMS_REFERENCE.md` §99. The measured reading over the named set (eleven surfaces ×
five resolutions): **BEFORE RED 255 / P1 750 → AFTER RED 0 / P1 0**, the BEFORE shot from
a pristine HEAD worktree at the shipped 1.0, the AFTER at the derived scales (1.40 on this
panel). Two of this memo's own numbers were corrected by the build: the aspect term (§5,
2.3 → 3.0, a 21:9 panel crossed it) and the "a 34-inch derives 1.15" row, which the
driven table now pins. **Built beyond the memo:** UXR-X1 / X2 / X3 fixed; the theme's own
Button 15 raised to 16 (the last RED row at 1080p); the main menu's column re-fitted on a
short logical viewport (the regression at scale 2.0). **Not built, as decided:** rows H–L
filed as UXR-D1 … D5; K ("The Side Desk") with its own gate. **S1b (the Settings
additions, decisions 4 + 5) is NEXT.** ⚠ The user's half of the done-when — the tutor card
read on their monitor without changing anything — is UXR-4's.

## Appendix §2a — the census (file:line)

Read-only census over every `.gd` / `.tscn` / `project.godot` / `main_theme.tres`,
October 9, 2026 (paths relative to `godot-client/project-sovereign/`; `.gd` under
`scripts/` unless named, `map_*.gd` under `scenes/`).

**Settings surfaces.** `settings_panel.tscn:5-6` is a bare VBoxContainer; every
control is built in `settings_panel.gd`: the scale slider + label 85-105 (writes via
`ui_scale_changed`, the HOST saves), "Reset to 100%" 107-111 / 128-133, Battle
sounds 145-149, the four bus sliders 150-168 (through `AudioManager.set_bus_volume`,
`audio_manager.gd:295-298, 352-360`), the API key + Connect/Disconnect 181-201 /
219-233, Spoken Orders 294-300, Credits 305-324. Main menu frame: `main_menu.gd:
360-420` (≥ 520 px view, ≥ 520 px scroll, Back; Esc closes 127-130; applies
`content_scale_factor` directly 418). Pause frame: `pause_menu.tscn:32-44, 117-128`
(360×400), `pause_menu.gd:54-61, 141-144` (≥ 440 scroll; forwards to `main.gd:764-765`).

**Scale.** `content_scale_factor` written at `main.gd:1682` and `main_menu.gd:418`
only; read in code at `map_renderer_base.gd:1876-1883` (`_target_content_scale`).
`get_ui_scale` readers `main.gd:760, 1538, 1545`, `settings_panel.gd:66-67, 92, 105`;
`set_ui_scale` writers `main.gd:1686`, `main_menu.gd:420`. `_apply_ui_scale`
`main.gd:1676-1690`: clamp → factor → `map_area.refresh_viewport_scale()` → save →
tooltip → `_relayout_terminal`. The retired terminal-only scale: `ui_settings.gd:16-20`.

**Grips.** Terminal: `main.gd:177-184, 1548-1580, 1582-1609, 1645-1668, 1525`;
`ui_settings.gd:33-38, 69-82`. War HUD edge-drag: `war_status_panel.gd:39-49, 79-143`
(re-fit on `update_wars` 196-212). `set_terminal_size` called only at `main.gd:1655,
1668`. Runtime `custom_minimum_size` writes are automatic fitting, never player
controls: `region_panel.gd:656`, `marshal_petition_dialog.gd:86, 141`,
`proposal_confirm_popup.gd:350`, `utils.gd:705, 742`. Keys in `ui_settings.cfg`:
`display/ui_scale`, `terminal/width,height`, `audio/battle_sfx`,
`audio/volume_{master,music,sfx,ui}`, `tutorial/done`, `parser/hint_seen`, `llm/api_key`.

**Clamp.** `utils.gd:604-767`: anchor guard 634-636, `design_size` cache 640-652,
`clamp_ceiling_override` 662-664 (set only by `proposal_confirm_popup.gd:259-261`),
the budget 665-671 (width −24, height −88), `_relax_child_minimums` 676-767 (4 rounds
to a 48-px floor, buttons never shrunk, `relax_last` at
`marshal_petition_dialog.gd:51`, `proposal_confirm_popup.gd:66`). Callers (30):
battle_diorama (fallback behind a flag 197-199), campaign_end, campaign_log,
capture_choice_dialog, clarification_popup, commitment_paradox_popup,
diplomacy_wizard, diplomatic_ledger, dispatch_view, enemy_phase_dialog, gazette_view,
glorious_charge_dialog, incoming_proposal_popup, interrupt_popup, load_dialog,
mailbox_panel, main_menu, marshal_management, marshal_petition_dialog,
objection_dialog, pause_menu, proclamation_popup, proposal_confirm_popup,
redemption_dialog, reward_dialog, sabotage_discovery_popup, strategic_ledger,
strategic_report_popup, talleyrand_objection_popup, vassal_rebellion_popup. Other
fitters: `battle_diorama._fit_tray_to_viewport` 176-210 (uniform scale 0.35–1.0, on
open only), `top_bar._fit_bar` 613-634, `region_panel._fit_height` 638-660,
`war_status_panel._fit_panel_to_content` 199-212, `interrupt_popup._fit_to_content`
115-133, `marshal_petition_dialog._fit_body` 132-142, `main._relayout_terminal`
1592-1609.

**Minimize / hide.** Terminal: `main.tscn:103-109, 275-289`; `main.gd:751-755,
1485-1506, 1210-1218, 1698-1703`. Tutor card: `tutorial_overlay.tscn:57-67, 76-106`;
`.gd:368-372, 440-443, 705-710, 723-725, 734-760`. Region panel: `region_panel.tscn:
32-36`; `.gd:79, 84, 127-132, 155, 504-510`; `main.gd:1403-1406, 714-715`;
`map_renderer_base.gd:2144-2154`. War HUD auto-hide `war_status_panel.gd:158-160`,
`main.gd:7584-7592`. Rail: `notification_bar.gd:18, 345-383, 640-651, 703-711`,
`main.gd:7599-7600` (`dismiss_all` 745-750 never called). Folds: `campaign_log.gd:45,
122, 174-179`; `diplomatic_ledger.gd:690-708, 741-762, 2014-2021`;
`proposal_confirm_popup.gd:33-35, 1016-1146`. Pin / opacity: none (every `modulate.a`
write is animation).

**Window.** No `DisplayServer` call anywhere; `project.godot:21-23` `[display]
window/size/mode=2` only; no `[autoload]`, no `[input]`; `export_presets.cfg` carries
no display keys.

**Map.** Zoom min = whole-map fit (≥ 0.05, `map_renderer_base.gd:1930-1954`), max 2.5
(234-238), step 0.1 (257) tweened 0.2 s (258, 2382-2405); wheel 2110-2115; keys
2358-2381; Alt forms `main.gd:1219-1237, 1241-1253`; middle-drag 2096-2119, 2156-2157;
arrows 2068-2088, 2160-2178 (Up/Down taken by command history while typing,
`main.gd:1175-1180`); Home 2375-2376; view mode M 96-100, 1144-1160, 2377-2381
(`main.gd:7472-7477`), not saved (346). Labels `map_label_layer.gd:24-33, 57-58,
145-170`; avoid the terminal `main.gd:1630-1643`. `_viewport_pixel_scale`
1886-1893 (= `content_scale_factor` via `_refresh_map_viewport_resolution`
1896-1909 and the TextureRect 873-898); `refresh_viewport_scale` 1912-1921.

**Hotkeys.** `main.gd:1388-1413` (Esc ladder), 1416-1418 (pause swallows all),
1129-1131 / 1421-1425 (F1), 1429-1473 + 6831-6846 (L T G D R N), 1117-1124 /
1132-1138 (Alt forms), 1480-1483 / 1204-1209 (E), 1485-1488 / 1210-1218 (Tab);
`strategic_ledger.gd:102-133` (1–8), `diplomatic_ledger.gd:133-159` (1–7),
`marshal_management.gd:107-140` (1–9); Enter/Esc dismissals `enemy_phase_dialog.gd:
949`, `strategic_report_popup.gd:158`, `battle_diorama.gd:1426-1442`, `popup_base.gd:
42`, `mailbox_panel.gd:332`, `proposal_confirm_popup.gd:86`, `war_detail_popup.gd:57`.
Key labels only: `top_bar.tscn:39-79, 131-136`, `top_bar.gd:66-69, 141-150`,
`main.tscn:106, 255, 265, 289`; the boot help `main.gd:901-923`; tutor cards I and
XIX. No reference overlay, no rebinding.

**Theme.** `main_theme.tres`: default font EB Garamond (4, 116) at 16 (117); Button 15
(123), Label 16 (135), LineEdit 16 (136), RichTextLabel normal 16 (138), bold = EB
Garamond 700 (94-98, 139), italics (6, 100-104, 140-141), PanelContainer leather
(106-113, 137); `HeadingLabel` 88-92, 129-134 (unused). Faces outside the theme:
`main_menu.gd:135-145` (Cormorant, IM Fell), `map_label_layer.gd:57-58` (Marcellus SC,
Spectral), `battle_diorama.gd:70-71` (Cinzel, IM Fell italic). Overrides: 174 in 34 of
39 scenes (10–30, mode 12 ×61, 14 ×36, 16 ×22); 94 `.gd` calls in 20 files (85
literals 9–96; computed down to 7 at `war_detail_popup.gd:320, 329`); 2 BBCode
`[font_size]` (24, 26).

**Tutor card.** Layer 90 non-modal (`.gd:7-11`, `.tscn:21-24`); 396 wide, top-right,
no bottom edge (`.tscn:26-34`); body `fit_content`, no scroll (69-74); no width /
height / clamp logic in the script; fonts 13 / 12 / 13 / 12 (`.tscn:47, 54, 74, 85`),
buttons at the theme's 15.

**Accessibility.** Nothing: no colour-blind, contrast, motion, speech or font option
(the one hit is a design comment, `map_connection_layer.gd:51`); motion with no off
switch at `main_menu.gd:22-25, 628-637`, `top_bar.gd:502-522`, `battle_diorama.gd:
1426-1442` (skippable per viewing). Resets: scale only (`settings_panel.gd:107-111`)
and the grip double-click (`main.gd:1648-1649, 1666-1668`).
