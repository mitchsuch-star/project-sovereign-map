"""IQ-10 "The Client Pass" — the runner: shoot every Family-A surface twice.

The two-command road (a future session re-shoots a surface with these two):

    .venv/Scripts/python.exe tools/iq10_capture_payloads.py
    .venv/Scripts/python.exe tools/iq10_run_captures.py

This script turns the payloads `iq10_capture_payloads.py` captured off STAGED
boards into spec JSONs for `tools/iq10_surface_screenshot.gd`, launches the
Godot editor binary once per batch (windowed and parked off-screen, audio on
the Dummy driver — the harness header states the rails), greps the engine log
for `SCRIPT ERROR` between the harness's own BEGIN/END markers, and writes ONE
index JSON naming every PNG, the surface it shows, what it MUST show, and the
frame's recorded text.

The frame record is what makes the pass cheap to read: the harness dumps every
visible string, every probed rect, every button that lies outside the logical
viewport, and every RichTextLabel taller than its box. A defect is read off
that record and CONFIRMED on the PNG, rather than hunted frame by frame.

Options:
    --only <substr>[,<substr>...]   shoot the matching shot ids only
    --scales 1.0,2.0               Interface Scale values (default both)
    --date 2026_09_19              the PNG date stamp
    --godot <path>                 the engine binary

UXR-0 "The readability instrument" (October 9, 2026) — PHYSICAL mode:
    --physical                     shoot each selected surface once per entry of
                                   PHYSICAL_RESOLUTIONS, the window sized to the
                                   monitor (parked off the desktop; proven to
                                   render at 5120x1440 and 3840x2160)
    --physical-scale auto|<x>      Interface Scale per frame: `auto` derives it
                                   as a player at that size would have it
                                   (uxr0_readability_report.derive_ui_scale);
                                   `1.0` is the shipped default — the BEFORE
                                   picture of the user's own screen
Every frame's record carries the text census (em / cap / x in physical px per
visible node); `tools/uxr0_readability_report.py <run>/index.json` applies the
floor and writes the committed machine record.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
PROJECT = REPO / "godot-client" / "project-sovereign"
AUDITS = REPO / "docs" / "audits"
GODOT_DEFAULT = r"C:\Users\User\Downloads\Godot_v4.4.1-stable_win64.exe\Godot_v4.4.1-stable_win64.exe"
# Parked PAST the desktop: the window is real (the renderer needs one) but never
# covers what the player is doing. UXR-0 (October 9, 2026): the desktop is ONE
# 5120-wide panel, so the old [2565, 20] sat on its right half for every run;
# x = 5200 is off it, and a window there still renders (probed at 5120x1440).
WINDOW_POSITION = [5200, 20]
SCRIPT = "../../tools/iq10_surface_screenshot.gd"
# The engine run never talks to a backend (every surface is stubbed), but
# main.gd's `main.tscn` road is REFUSED by the harness while SOVEREIGN_PORT
# points at the player's live 8005, and the menu / settings scenes poll their
# origin over HTTPRequest — an unused port fails fast and touches nothing.
HARNESS_PORT = "8999"

sys.path.insert(0, str(REPO / "tools"))
from uxr0_readability_report import PHYSICAL_RESOLUTIONS, derive_ui_scale  # noqa: E402

# ── the surface table ───────────────────────────────────────────────────────
# One row per SHOT: the scene, how it is entered, and what the frame must show.
# `payload` names a capture in the payload manifest. `tab` presses a ledger
# sub-tab after the screen has rendered (the ledger's own `_switch_tab`).
LEDGER_TABS = ["Forces", "Territories", "Economy", "Intel", "Manpower", "Orders", "Admiralty", "Laws"]
# The Diplomatic Ledger's books IN ORDER (the scene's SubTabRow). GE-3 (Sept
# 25, 2026): index 4 is WAR BARGAINS — the old list named it "Vassals", so
# every "…_vassals" shot below it pressed tab 4 and photographed the War
# Bargains book; VASSALS is 5 and the new CONGRESS book is 6.
DIPLO_TABS = ["Nations", "Treaties", "Balance", "Talleyrand", "Bargains", "Vassals", "Congress"]

SHOTS: list[dict] = [
    # ── S1–S6 the Strategic Ledger, boot (every tab) ────────────────────────
    *[
        {
            "id": f"ledger_boot_{t.lower()}",
            "surface": f"Strategic Ledger — {t} tab",
            "payload": "ledger_boot",
            "scene": "res://scenes/strategic_ledger.tscn",
            "mode": "api_stub",
            "method": "open",
            "api_method": "get_ledger",
            "tab": i,
            "must_show": f"the {t} tab of the 1805 boot: no raw nation tag, no '<null>', "
                         f"every figure the payload carries, nothing clipped at scale 2.0",
        }
        for i, t in enumerate(LEDGER_TABS)
    ],
    # ── the economy tab on the boards that matter (IQ-1, IQ-2) ──────────────
    *[
        {
            "id": f"ledger_{name}_economy",
            "surface": f"Strategic Ledger — Economy ({label})",
            "payload": f"ledger_{name}",
            "scene": "res://scenes/strategic_ledger.tscn",
            "mode": "api_stub",
            "method": "open",
            "api_method": "get_ledger",
            "tab": 2,
            "must_show": must,
        }
        for name, label, must in [
            ("spent", "the chest spent", "the Charges of Empire and the spent figure; IQ-1's convertible chest"),
            ("ceiling_calm", "60% of the ceiling", "the ceiling line below its bound"),
            ("ceiling_above", "150% of the ceiling", "the ceiling line ABOVE its bound, and says so"),
            
            ("ceiling_unbounded", "the legacy world", "an unbounded ceiling rendered without a raw key"),
            ("collapse_one", "one province left", "IQ-2's collapse state, named, not a cheerful net"),
            ("collapse_none", "no province left", "IQ-2's collapse state at zero provinces"),
        ]
    ],
    # ── SR-5r RF-4c: the laws' boards (REFORMS_SPEC §8a "Visual proof"; the
    #    LAWS tab at boot is ledger_boot_laws above) ─────────────────────────
    *[
        {
            "id": f"ledger_laws_{name}",
            "surface": f"Strategic Ledger — Laws ({label})",
            "payload": f"ledger_laws_{name}",
            "scene": "res://scenes/strategic_ledger.tscn",
            "mode": "api_stub",
            "method": "open",
            "api_method": "get_ledger",
            "tab": 7,
            "must_show": must,
        }
        for name, label, must in [
            ("staff", "the Staff in force",
             "the Staff's row IN FORCE with its Repeal chip and what it loses; the footer's upkeep"),
            ("forecast", "a doomed law",
             "the FORECAST naming the Staff and the gold that saves it, and the "
             "'repeal X instead' chip; nothing clipped at scale 2.0"),
        ]
    ],
    {
        "id": "diplo_laws_rival_nations",
        "surface": "Diplomatic Ledger — Nations (a rival's laws)",
        "payload": "diplo_laws_rival",
        "scene": "res://scenes/diplomatic_ledger.tscn",
        "mode": "api_stub", "method": "open", "api_method": "get_diplomatic_ledger", "tab": 0,
        "must_show": "Britain's card carries its Laws line (the Orders in Council and the Militia "
                     "Transfer, with their cost a turn) within the two-line budget",
    },
    # ── S10–S12 the Diplomatic Ledger ───────────────────────────────────────
    *[
        {
            "id": f"diplo_boot_{t.lower()}",
            "surface": f"Diplomatic Ledger — {t} tab",
            "payload": "diplo_ledger_boot",
            "scene": "res://scenes/diplomatic_ledger.tscn",
            "mode": "api_stub",
            "method": "open",
            "api_method": "get_diplomatic_ledger",
            "tab": i,
            "must_show": f"the {t} tab at boot: the Cabinet block reads Talleyrand idle, "
                         f"no raw tag, nothing clipped",
        }
        for i, t in enumerate(DIPLO_TABS)
    ],
    {
        "id": "diplo_collapse_one_nations",
        "surface": "Diplomatic Ledger — Nations (one province left)",
        "payload": "diplo_ledger_collapse_one",
        "scene": "res://scenes/diplomatic_ledger.tscn",
        "mode": "api_stub", "method": "open", "api_method": "get_diplomatic_ledger", "tab": 0,
        "must_show": "IQ-2's collapse line on the diplomatic side; no raw tag",
    },
    {
        "id": "diplo_collapse_cooldown_talleyrand",
        "surface": "Diplomatic Ledger — Talleyrand (coalition cooldown)",
        "payload": "diplo_ledger_collapse_cooldown",
        "scene": "res://scenes/diplomatic_ledger.tscn",
        "mode": "api_stub", "method": "open", "api_method": "get_diplomatic_ledger", "tab": 3,
        "must_show": "IQ-3's spent-league cooldown counsel, and the Cabinet block",
    },
    {
        "id": "diplo_collapse_none_vassals",
        "surface": "Diplomatic Ledger — Vassals (no province left)",
        "payload": "diplo_ledger_collapse_none",
        "scene": "res://scenes/diplomatic_ledger.tscn",
        "mode": "api_stub", "method": "open", "api_method": "get_diplomatic_ledger", "tab": 5,
        "must_show": "the IQ-7 Vassals tab: the petition standing column, the honest chips",
    },
    # ── S19 Generals ────────────────────────────────────────────────────────
    {
        "id": "generals_boot",
        "surface": "Generals (Marshal Management)",
        "payload": "marshal_overview_boot",
        "scene": "res://scenes/marshal_management.tscn",
        "mode": "api_stub", "method": "open", "api_method": "get_marshal_overview",
        "must_show": "the character sheets: skill bars, the glory ladder, GLORY & GRIEVANCES, "
                     "no raw tag, nothing clipped at scale 2.0",
    },
    # ── the morning dispatch ────────────────────────────────────────────────
    {
        "id": "dispatch_collapse",
        "surface": "Dispatch re-read (collapse board)",
        "payload": "dispatch_collapse",
        "scene": "res://scenes/dispatch_view.tscn",
        "mode": "api_stub", "method": "open", "api_method": "get_dispatch",
        "must_show": "IQ-2's collapse headline leads; no raw tag; the rows are legible",
    },
    # ── the letter-book ─────────────────────────────────────────────────────
    {
        "id": "mailbox_boot",
        "surface": "Mailbox / letter-book",
        "payload": "mailbox_boot",
        "scene": "res://scenes/mailbox_panel.tscn",
        "mode": "call", "method": "show_mailbox",
        "must_show": "the envoy rows with their courts named (article, no raw tag); "
                     "the panel is not clipped (the IGR-F 600x400 defect)",
    },
    # ── S15 the war HUD and its detail ──────────────────────────────────────
    *[
        {
            "id": f"war_status_{name}",
            "surface": f"War Status HUD ({label})",
            "payload": f"active_wars_{name}",
            "scene": "res://scenes/war_status_panel.tscn",
            "mode": "call", "method": "update_wars",
            "must_show": must,
        }
        for name, label, must in [
            ("boot", "boot", "the Third Coalition row, the tug-of-war bar filling its track"),
            ("collapse_one", "one province left", "the war rows on a collapsing France"),
            ("collapse_none", "no province left", "the war rows at zero provinces"),
        ]
    ],
    *[
        {
            "id": f"war_detail_{name}",
            "surface": f"War Detail popup ({label})",
            "payload": f"war_detail_{name}",
            "scene": "res://scenes/war_detail_popup.tscn",
            "mode": "call", "method": "show_war",
            "args": ["$payload.war", "$payload.coalition"],
            "must_show": must,
        }
        for name, label, must in [
            ("boot", "boot", "the score breakdown incl. PT-J2's Campaign and Blood rows; the bar tracks"),
            ("collapse_one", "one province left", "a losing score, named honestly"),
            ("collapse_none", "no province left", "the worst case: no cheerful wording"),
        ]
    ],
    # ── S13–S14 the peace popups on a LOSING France ─────────────────────────
    {
        "id": "incoming_peace_losing",
        "surface": "Incoming settlement offer (losing France)",
        "payload": "incoming_peace_losing",
        "scene": "res://scenes/incoming_proposal_popup.tscn",
        "mode": "call", "method": "show_proposal",
        "must_show": "the offer's terms and its ASK/OFFER direction (the FA-S17 'paid the loser' "
                     "fix); three buttons, each with its own action; no raw tag",
    },
    {
        "id": "confirm_peace_losing",
        "surface": "Proposal confirm — drafted peace (losing France)",
        "payload": "confirm_peace_losing",
        "scene": "res://scenes/proposal_confirm_popup.tscn",
        "mode": "call", "method": "show_dialogue",
        "must_show": "the confirm snapshot: the terms, the acceptance components, the agenda "
                     "modifier; the IGR-G relax pass keeps the per-court table readable",
    },
    # ── S20–S21 the enemy phase ─────────────────────────────────────────────
    {
        "id": "enemy_phase_collapse",
        "surface": "Enemy-phase dialog (collapse board)",
        "payload": "end_turn_collapse",
        "scene": "res://scenes/enemy_phase_dialog.tscn",
        "mode": "call", "method": "show_enemy_phase",
        "args": ["$payload.enemy_phase", 2],
        "must_show": "every AI action as prose (no snake_case verb); IQ-5's casualty scope on "
                     "both sides; the battle lines carry their '⚔ View the field' link",
    },
    # ── S8 the top bar ──────────────────────────────────────────────────────
    {
        "id": "top_bar_boot",
        "surface": "Top bar — diplomatic fields",
        "payload": "top_bar_fields_boot",
        "scene": "res://scenes/top_bar.tscn",
        "mode": "call", "method": "update_diplomatic_fields",
        "place": {"position": [0, 0], "height": 64},
        "must_show": "IQ-4's Cabinet line: 'Talleyrand: Idle' where the backend says 'None' — "
                     "never the raw word None",
    },
    # ── NUI "The Admiralty on the Map" (Sept 23, 2026): the Admiralty chip ──
    {
        "id": "top_bar_admiralty",
        "surface": "Top bar — the Admiralty chip (a naval board, boot blockade)",
        "payload": "top_bar_fields_boot",
        "scene": "res://scenes/top_bar.tscn",
        "mode": "call", "method": "update_diplomatic_fields",
        "steps": [{"call": "update_admiralty",
                   "args": ["$payload.naval_player_summary"], "then_wait": 6}],
        "place": {"position": [0, 0], "height": 64},
        "must_show": "the Admiralty chip beside DP — '⚓ 45 sail · BLOCKADED' at 1.0, '⚓ 45!' in "
                     "the compact bar at 2.0 — crimson-bordered under the boot blockade; at 2.0 "
                     "every nav button icon-only and NO button off the logical viewport (IQ10-X1)",
    },

    # ═══ IQ-4 the Cabinet (the mission boards) ═══════════════════════════════
    *[
        {
            "id": f"ledger_mission_{tag}_forces",
            "surface": f"Strategic Ledger — the Cabinet block ({label})",
            "payload": f"ledger_mission_{tag}",
            "scene": "res://scenes/strategic_ledger.tscn",
            "mode": "api_stub", "method": "open", "api_method": "get_ledger", "tab": 0,
            "must_show": must,
        }
        for tag, label, must in [
            ("court", "COURT_NATION running", "the Cabinet block naming the mission, its court, the DP a turn and the favour"),
            ("improve", "IMPROVE_RELATIONS running", "the Cabinet block's effect / drift / net arm"),
            ("gather", "GATHER_INTEL running", "the Cabinet block's effect-text arm"),
            ("undermine", "UNDERMINE_ALLIANCE running", "the pair the mission moves, not the player pair"),
            ("transit", "in transit with a proposal", "the mission PAUSED while he carries a letter, and no Recall"),
            ("starved", "starved of DP", "the mission suspended for want of DP, with its cost stated"),
            ("recalled", "recalled", "the desk empty and free to send again — MS-1's lockout gone"),
        ]
    ],
    *[
        {
            "id": f"diplo_mission_{tag}_talleyrand",
            "surface": f"Diplomatic Ledger — Talleyrand ({label})",
            "payload": f"diplo_ledger_mission_{tag}",
            "scene": "res://scenes/diplomatic_ledger.tscn",
            "mode": "api_stub", "method": "open", "api_method": "get_diplomatic_ledger", "tab": 3,
            "must_show": "the tab agrees with the Cabinet block: one source, one figure",
        }
        for tag, label in [("court", "courting"), ("undermine", "undermining"), ("recalled", "recalled")]
    ],
    *[
        {
            "id": f"rail_mission_{tag}",
            "surface": f"Notice rail — the mission row ({tag})",
            "payload": f"notifications_mission_{tag}",
            "scene": "res://scenes/notification_bar.tscn",
            "mode": "call", "method": "update_notifications",
            "place": {"position": [0, 0], "height": 120},
            "must_show": "ONE mission row with a Recall, its court named, no raw key",
        }
        for tag in ["court", "improve", "gather"]
    ],
    {
        "id": "top_bar_mission_court",
        "surface": "Top bar — a mission standing",
        "payload": "top_bar_fields_mission_court",
        "scene": "res://scenes/top_bar.tscn",
        "mode": "call", "method": "update_diplomatic_fields",
        "place": {"position": [0, 0], "height": 64},
        "must_show": "IQ-4's Cabinet line naming the running mission, never 'Idle' beside a live one",
    },
    # ═══ IQ-7 the client's petition ══════════════════════════════════════════
    {
        "id": "petition_popup",
        "surface": "Client's Petition popup",
        "payload": "petition_popup",
        "scene": "res://scenes/incoming_proposal_popup.tscn",
        "mode": "call", "method": "show_proposal",
        "must_show": "the court with its article (never a raw tag); the price it quotes is the "
                     "price the grant charges; Grant and Refuse each state their terms",
    },
    {
        "id": "petition_popup_no_dp",
        "surface": "Client's Petition popup — the lord cannot pay",
        "payload": "petition_popup_no_dp",
        "scene": "res://scenes/incoming_proposal_popup.tscn",
        "mode": "call", "method": "show_proposal",
        "must_show": "Grant present but DISABLED with its stated reason (THE_LORD_PAYS_TO_GRANT), "
                     "never absent and never silently live",
    },
    {
        "id": "mailbox_petition",
        "surface": "Envoys — a petition waiting",
        "payload": "mailbox_petition",
        "scene": "res://scenes/mailbox_panel.tscn",
        "mode": "call", "method": "show_mailbox",
        "must_show": "the petition row titled with the court's article, beside the routine letters",
    },
    {
        "id": "diplo_petition_granted_vassals",
        "surface": "Diplomatic Ledger — Vassals after a granted petition",
        "payload": "diplo_ledger_petition_granted",
        "scene": "res://scenes/diplomatic_ledger.tscn",
        "mode": "api_stub", "method": "open", "api_method": "get_diplomatic_ledger", "tab": 5,
        "must_show": "the bond and the standing after the grant — not 'N turns until it may ask' "
                     "while the ask is answered",
    },
    # ═══ IQ-5 the butcher's bill ═════════════════════════════════════════════
    *[
        {
            "id": f"diorama_{tag}",
            "surface": f"Battle Diorama ({label})",
            "payload": f"diorama_iq5_{tag}",
            "scene": "res://scenes/battle_diorama.tscn",
            "mode": "call", "method": "show_diorama",
            "args": ["$payload", False],
            "must_show": "the order of battle with each contingent's own losses; IQ-5's scope "
                         "label on the reinforced side; the verdict in Berthier's voice",
        }
        for tag, label in [("aadj", "attacker adjusted"), ("dadj", "defender adjusted")]
    ],
    {
        "id": "enemy_phase_iq5",
        "surface": "Enemy-phase dialog (IQ-5 scope board)",
        "payload": "enemy_phase_iq5_dadj",
        "scene": "res://scenes/enemy_phase_dialog.tscn",
        "mode": "call", "method": "show_enemy_phase",
        "args": ["$payload.enemy_phase", "$payload.turn"],
        "must_show": "the defender's casualties labelled by SCOPE (army vs corps) — the half "
                     "IQ-5 could not show without a client pass",
    },
    # ═══ the region panel, and H1 ════════════════════════════════════════════
    *[
        {
            "id": f"region_{region.lower()}",
            "surface": f"Region Action Panel — {region} ({label})",
            "payload": "game_state_regions",
            "scene": "res://scenes/region_panel.tscn",
            "mode": "map_stub", "method": "show_region",
            "args": [region, "$map"],
            "must_show": must,
        }
        for region, label, must in [
            ("Paris", "own soil, Soult present", "CN-3: one recruit chip per arm — Infantry ENABLED naming "
                                                 "Soult, his men, his gold and the pool; Cavalry and "
                                                 "Artillery dimmed with the backend's reason and remedy; "
                                                 "the ordinance line saying its multiplier; the "
                                                 "Substitutes row, Build/Repair"),
            ("Rhineland", "own soil, Davout present, Murat in range", "CN-3: Infantry via Davout and "
                                                                      "Cavalry via Murat both ENABLED, each "
                                                                      "stating its own man and price; "
                                                                      "Artillery dimmed naming the "
                                                                      "commission remedy"),
            ("Amsterdam", "a vassal's province, Bernadotte present", "H1 + CN-3 (ruling D5): the Substitutes "
                                                                    "row renders on the soil that feeds "
                                                                    "France (3,193g) and the recruit row is "
                                                                    "three DIMMED chips with the one reason "
                                                                    "— recruiting does not open on ally soil"),
            ("Milan", "a vassal's province, Massena present", "H1 again on the Kingdom of Italy's soil, with "
                                                             "the court named by its article; the recruit "
                                                             "row dimmed with one reason (D5)"),
            ("Vienna", "an enemy capital", "no levy rows, no raw tag, the garrison honestly fogged"),
        ]
    ],
    # ═══ the prisoner ════════════════════════════════════════════════════════
    {
        "id": "generals_prisoner",
        "surface": "Generals — a captured marshal",
        "payload": "marshal_overview_prisoner",
        "scene": "res://scenes/marshal_management.tscn",
        "mode": "api_stub", "method": "open", "api_method": "get_marshal_overview",
        "must_show": "the prisoner named as a prisoner with his captor — never an idle corps",
    },
    # ═══ the t20 fixture: a played board ═════════════════════════════════════
    *[
        {
            "id": f"ledger_t20_{t.lower()}",
            "surface": f"Strategic Ledger — {t} (t20 fixture)",
            "payload": "ledger_t20",
            "scene": "res://scenes/strategic_ledger.tscn",
            "mode": "api_stub", "method": "open", "api_method": "get_ledger", "tab": i,
            "must_show": f"the {t} tab on a played board — the case a boot frame cannot show",
        }
        for i, t in [(0, "Forces"), (2, "Economy"), (5, "Orders"), (6, "Admiralty")]
    ],
    *[
        {
            "id": f"diplo_t20_{t.lower()}",
            "surface": f"Diplomatic Ledger — {t} (t20 fixture)",
            "payload": "diplo_ledger_t20",
            "scene": "res://scenes/diplomatic_ledger.tscn",
            "mode": "api_stub", "method": "open", "api_method": "get_diplomatic_ledger", "tab": i,
            "must_show": f"the {t} tab on a played board",
        }
        for i, t in [(0, "Nations"), (1, "Treaties"), (2, "Balance"), (5, "Vassals")]
    ],
    {
        "id": "generals_t20",
        "surface": "Generals (t20 fixture)",
        "payload": "marshal_overview_t20",
        "scene": "res://scenes/marshal_management.tscn",
        "mode": "api_stub", "method": "open", "api_method": "get_marshal_overview",
        "must_show": "a played roster: glory, grievances, the ladder, the trust bars",
    },
    {
        "id": "dispatch_t20",
        "surface": "Dispatch re-read (t20 fixture)",
        "payload": "dispatch_t20_after",
        "scene": "res://scenes/dispatch_view.tscn",
        "mode": "api_stub", "method": "open", "api_method": "get_dispatch",
        "must_show": "the morning dispatch of a played turn: the headline, the beats, no raw tag",
    },
    {
        "id": "enemy_phase_t20",
        "surface": "Enemy-phase dialog (t20 fixture)",
        "payload": "enemy_phase_t20",
        "scene": "res://scenes/enemy_phase_dialog.tscn",
        "mode": "call", "method": "show_enemy_phase",
        "args": ["$payload.enemy_phase", 21],
        "must_show": "every AI action as prose; the battle lines and their field link",
    },
    {
        "id": "war_status_t20",
        "surface": "War Status HUD (t20 fixture)",
        "payload": "active_wars_t20",
        "scene": "res://scenes/war_status_panel.tscn",
        "mode": "call", "method": "update_wars",
        "must_show": "several wars at once: the rows fit, the bars track their containers",
    },
    {
        "id": "war_detail_t20",
        "surface": "War Detail popup (t20 fixture)",
        "payload": "war_detail_t20",
        "scene": "res://scenes/war_detail_popup.tscn",
        "mode": "call", "method": "show_war",
        "args": ["$payload.war", "$payload.coalition"],
        "must_show": "the breakdown on a played war; the exposure and weariness rows",
    },
    {
        "id": "gazette_t20",
        "surface": "Le Moniteur (t20 fixture)",
        "payload": "gazette_t20",
        "scene": "res://scenes/gazette_view.tscn",
        "mode": "api_stub", "method": "open", "api_method": "get_gazette",
        "must_show": "the issues with their captions; no raw tag; the columns fit at 2.0",
    },
    {
        "id": "rail_t20",
        "surface": "Notice rail (t20 fixture)",
        "payload": "notifications_t20_after",
        "scene": "res://scenes/notification_bar.tscn",
        "mode": "call", "method": "update_notifications",
        "place": {"position": [0, 0], "height": 120},
        "must_show": "the tray under its cap, CRITICAL first, each icon its own glyph",
    },
    # ═══ §1d the Aug-16 Napoleon sign-off, staged then and never captured ════
    *[
        {
            "id": f"generals_{tag}",
            "surface": f"Generals — {label}",
            "payload": f"marshal_overview_{tag}",
            "scene": "res://scenes/marshal_management.tscn",
            "mode": "api_stub", "method": "open", "api_method": "get_marshal_overview",
            "must_show": must,
        }
        for tag, label, must in [
            ("np_seat", "Napoleon in the Seat (NP-5)", "the Emperor's own card: the sovereign kit, the Seat, "
                                                       "the Guard's strength"),
            ("np_field", "Napoleon in the field", "the Presence figure as APPLIED, and the star that dims"),
            ("np_captive", "the Eagle in Chains", "a captured sovereign named as a captive — never commandable"),
            ("flagship_t12", "the flagship t12 board", "the played roster the Aug-15 pass staged and never shot"),
        ]
    ],
    {
        "id": "ledger_np_seat_forces",
        "surface": "Strategic Ledger — Forces (Napoleon in the Seat)",
        "payload": "ledger_np_seat",
        "scene": "res://scenes/strategic_ledger.tscn",
        "mode": "api_stub", "method": "open", "api_method": "get_ledger", "tab": 0,
        "must_show": "the Emperor's corps in the muster, the Seat's +1 DP named",
    },
    # ═══ Row EP F3 "The client layout pass" (September 24, 2026) ════════════
    # The four frames the live review's layout rows owe. The wizard has no
    # offline entry (it fetches over its own HTTPRequest), so its rows show
    # the panel, set the step's state, render the captured payload through
    # the SAME `_render_*` the wire response reaches, and `refit` (the live
    # clamp) — see diplomacy_wizard.gd `refit`.
    {
        "id": "petition_command_closed",
        "surface": "Marshal petition — the command arm closed (LV-5)",
        "payload": "petition_command_closed",
        "scene": "res://scenes/marshal_petition_dialog.tscn",
        "mode": "call", "method": "show_petition",
        "must_show": "the whole body above the fold (no clipped second line); the closed arm's "
                     "reason as ONE line under the header; no reason printed twice under a button",
    },
    {
        "id": "wizard_step1",
        "surface": "Diplomacy wizard — step 1, the nation list (LV-20)",
        "payload": "wizard_nations",
        "scene": "res://scenes/diplomacy_wizard.tscn",
        "mode": "call", "method": "show", "args": [],
        "steps": [
            {"set_path": "_current_step", "value": 1},
            {"set_path": "title_label.text", "value": "DIPLOMACY"},
            {"set_path": "assessment_panel.text", "value": "[color=#a0a0a8]\"Your Excellency, which nation requires our diplomatic attention?\"[/color]"},
            {"call": "_lay_out_prompt", "args": [1]},
            {"call": "_render_nations", "args": ["$payload"]},
            {"call": "refit", "args": []},
            {"wait": 4},
        ],
        "must_show": "the prompt directly above the list — no blank gap; every court in its category",
    },
    *[
        {
            "id": f"wizard_step2_{court.lower()}",
            "surface": f"Diplomacy wizard — step 2, {court} ({note})",
            "payload": f"wizard_preview_{court.lower()}",
            "scene": "res://scenes/diplomacy_wizard.tscn",
            "mode": "call", "method": "show", "args": [],
            "steps": [
                {"set_path": "_current_step", "value": 2},
                {"set_path": "_selected_nation", "value": court},
                {"set_path": "title_label.text", "value": f"DIPLOMACY — {court}"},
                {"set_path": "back_button.visible", "value": True},
                {"call": "_lay_out_prompt", "args": [2]},
                {"call": "_render_preview", "args": ["$payload"]},
                {"call": "refit", "args": []},
                {"wait": 4},
            ],
            "must_show": must,
        }
        for court, note, must in [
            ("Austria", "at war", "every chip WRAPPED inside the panel — no horizontal scrollbar; a "
                                  "gate reason as its own smaller line under its chip; no Sponsor chip "
                                  "for a court at war whose design is aimed at France"),
            ("Prussia", "at peace", "the three instrument chips incl. 'Sponsor Their Design', wrapped, "
                                    "with 'Aim their court at Hanover' readable in full"),
        ]
    ],
    {
        "id": "settlement_three_courts",
        "surface": "Settlement table — three courts, Vienna held (LV-14b)",
        "payload": "settlement_three_courts",
        "scene": "res://scenes/proposal_confirm_popup.tscn",
        "mode": "call", "method": "show_dialogue",
        "must_show": "one row per court in the Press/Ease/Drop block — Austria, Britain AND Russia, "
                     "none clipped; the block sits under the table, not over the 'Allies and "
                     "Standing' heading",
    },
    {
        "id": "campaign_log_glyphs",
        "surface": "Campaign log — glyph prefixes (LV-16)",
        "payload": "campaign_log_glyphs",
        "scene": "res://scenes/campaign_log.tscn",
        "mode": "api_stub", "method": "open_log", "api_method": "get_campaign_log",
        "must_show": "a tinted glyph (sword / flag / coins / scroll / handshake) before each row — "
                     "never a bare letter",
    },
    # ── Row EP GE-2: the end screen, four registers ─────────────────────────
    *[
        {
            "id": f"campaign_end_{tag}",
            "surface": f"The end screen — {label}",
            "payload": f"campaign_end_{tag}",
            "scene": "res://scenes/campaign_end.tscn",
            "mode": "call", "method": "show_ending",
            "must_show": must,
        }
        for tag, label, must in (
            ("fall_funeral", "THE FALL OF THE EMPIRE (the Emperor dead, the command road)",
             "the crimson register: the title, the date, 'The Emperor is dead.', THE FUNERAL "
             "paragraphs, THE RECORD, THE VERDICT OF HISTORY — THE ECLIPSE; buttons 'Load a "
             "campaign' / 'Main Menu'; no raw tag; nothing clipped at scale 2.0"),
            ("fall_chains", "THE FALL OF THE EMPIRE (the Eagle in chains)",
             "the crimson register: 'The Emperor, a prisoner these 10 turns, is deposed.', THE "
             "EXILE naming Olmütz and Metternich's line, the record, the eclipse"),
            ("fall_abdication", "THE FALL OF THE EMPIRE (no soil — Brittany alone)",
             "the crimson register: 'The Empire is reduced to Brittany alone — a province, not "
             "a realm.', THE EXILE naming Fontainebleau and Elba, the record, the eclipse"),
            ("humbled", "THE HUMBLED PEACE",
             "the crimson-grey register: 'The Emperor has signed a peace that humbles the "
             "Empire.', THE PEACE paragraph naming Paris, the record, the eclipse; ONE button "
             "'Continue'"),
            ("verdict", "THE VERDICT OF HISTORY",
             "the parchment register: the tier as the heading with its three lines and the "
             "closing, then THE RECORD; ONE button 'Continue'"),
            ("imperial", "THE IMPERIAL PEACE (GE-3's register, STAGED through record_ending)",
             "the gold register: 'Europe accepts the order of the French Empire.', the record, "
             "the tier; buttons 'Continue the reign' / 'Retire to the Tuileries'"),
        )
    ],
    # ── Row EP GE-2: the clock line on the two client surfaces ──────────────
    {
        "id": "ledger_fall_clock_territories",
        "surface": "Strategic Ledger — Territories (the fall clock, two arms)",
        "payload": "ledger_fall_clock",
        "scene": "res://scenes/strategic_ledger.tscn",
        "mode": "api_stub", "method": "open", "api_method": "get_ledger",
        "tab": 1,
        "must_show": "under the collapse note, TWO clock lines: the ticking soil clock dated in "
                     "amber ('1 of 5 · the Empire falls at the end of turn 5 (4 turns remain)') "
                     "and the paused chains clock dimmed with NO date ('the clock stands still — "
                     "no war with his captor')",
    },
    {
        "id": "dispatch_fall_clock",
        "surface": "Dispatch re-read (the fall clock on the banner)",
        "payload": "dispatch_fall_clock",
        "scene": "res://scenes/dispatch_view.tscn",
        "mode": "api_stub", "method": "open", "api_method": "get_dispatch",
        # The warning sits below the marshal roster — scroll the R screen to it.
        "steps": [{"scroll_to": {"text": "THE FALL OF THE EMPIRE"}, "then_wait": 4}],
        "must_show": "THE FALL OF THE EMPIRE heading, the warning's prose, then the clock line — "
                     "the same words the Territories tab prints",
    },
    # ═══ Row EP GE-3 "The Congress of Paris" (September 25, 2026) ════════════
    # The capture group is `congress` (tools/iq10_capture_payloads.py
    # `cap_congress`, whose staging notes say what was written and what was
    # played). The wizard rows render the captured nation list through the
    # SAME `_render_nations` the wire response reaches (the F3 idiom).
    *[
        {
            "id": f"diplo_congress_{tag}",
            "surface": f"Diplomatic Ledger — CONGRESS ({label})",
            "payload": f"diplo_ledger_congress_{payload}",
            "scene": "res://scenes/diplomatic_ledger.tscn",
            "mode": "api_stub", "method": "open_to_congress", "api_method": "get_diplomatic_ledger",
            **({"steps": [{"scroll_to": {"text": scroll}, "then_wait": 4}]} if scroll else {}),
            "must_show": must,
        }
        for tag, payload, label, scroll, must in (
            ("gate", "gate", "the gate at the 1805 boot", "",
             "the CONGRESS tab lit as the 7th book; the clock line in gold ('35 of 50 titled'); "
             "THE SUMMONS with each term ✓/• and the cost; 'Not yet: …' naming the 15 "
             "provinces; THE TABLE opening under it"),
            ("sitting", "sitting", "the sitting, turn 2 of 8", "",
             "the clock line in amber ('THE CONGRESS SITS — turn 2 of 8 …'); THE SITTING "
             "strip (day 1 ✓, day 2 gilded with its answer to come '…', the rest dots; "
             "'Signed 1/4'); THE HOLD's seven "
             "conditions all ✓"),
            ("sitting_table", "sitting", "the sitting — the table", "THE TABLE",
             "the four courts, flags and seats: Britain REFUSES (crimson), Russia SUES "
             "(amber), Austria RECOGNIZES (green), Prussia REFUSES with its reckoning, price, "
             "'takes up arms against us at this end turn unless it signs' and the typed order; "
             "each card's 'Open the Cabinet at …' link"),
        )
    ],
    *[
        {
            "id": f"wizard_step1_congress_{tag}",
            "surface": f"Diplomacy wizard — step 1, the Congress row ({label})",
            "payload": f"wizard_nations_congress_{tag}",
            "scene": "res://scenes/diplomacy_wizard.tscn",
            "mode": "call", "method": "show", "args": [],
            "steps": [
                {"set_path": "_current_step", "value": 1},
                {"set_path": "title_label.text", "value": "DIPLOMACY"},
                {"set_path": "assessment_panel.text", "value": "[color=#a0a0a8]\"Your Excellency, which nation requires our diplomatic attention?\"[/color]"},
                {"call": "_lay_out_prompt", "args": [1]},
                {"call": "_render_nations", "args": ["$payload"]},
                {"call": "refit", "args": []},
                {"wait": 4},
            ],
            "must_show": must,
        }
        for tag, label, must in (
            ("gate", "the gate",
             "'The Congress of Paris' at the TOP of the list, above Formable Nations: the gold "
             "clock line, the seven terms ✓/• with '50 titled provinces (35 of 50)' dotted, "
             "the Summon button DISABLED with its reason beneath, 'View the table'"),
            ("ready", "every term met",
             "every term ✓ and the Summon button ENABLED in gold with its cost "
             "('2 diplomatic points + 1 administrative action')"),
            ("sitting", "the Congress sitting",
             "the amber sitting line, no terms, the Summon button disabled with 'The Congress "
             "already sits — turn 2 of 8.', and 'View the table — the courts' answers, the "
             "hold, the days'"),
        )
    ],
    {
        "id": "campaign_end_imperial_congress",
        "surface": "The end screen — THE IMPERIAL PEACE through a real Congress",
        "payload": "campaign_end_imperial_congress",
        "scene": "res://scenes/campaign_end.tscn",
        "mode": "call", "method": "show_ending",
        "must_show": "the gold register: 'Europe accepts the order of the French Empire.'; THE "
                     "CONGRESS OF PARIS with the four flags — Britain, Russia, Austria, Prussia "
                     "SIGNED in green; '50 of 50 titled provinces.'; THE SITTING strip (days 1–8, "
                     "✓ each, 4/4); THE RECORD; THE VERDICT OF HISTORY; the Moniteur's final line "
                     "in gold italic; buttons 'Continue the reign' / 'Retire to the Tuileries'; "
                     "no EXILE block; nothing clipped at scale 2.0",
    },
    {
        "id": "ledger_congress_clock_territories",
        "surface": "Strategic Ledger — Territories (the Congress clock)",
        "payload": "ledger_congress_clock",
        "scene": "res://scenes/strategic_ledger.tscn",
        "mode": "api_stub", "method": "open", "api_method": "get_ledger",
        "tab": 1,
        "must_show": "under the dateline, the Congress clock line in amber — 'THE CONGRESS SITS — "
                     "turn 2 of 8 · 50 of 50 titled · …' — the same words the banner prints",
    },
    {
        "id": "dispatch_congress_clock",
        "surface": "Dispatch re-read (the Congress clock on the banner)",
        "payload": "dispatch_congress_clock",
        "scene": "res://scenes/dispatch_view.tscn",
        "mode": "api_stub", "method": "open", "api_method": "get_dispatch",
        "steps": [{"scroll_to": {"text": "THE CONGRESS OF PARIS"}, "then_wait": 4}],
        "must_show": "THE CONGRESS OF PARIS heading, then the sitting's clock line in amber — the "
                     "same words the Territories tab prints",
    },
    {
        "id": "gazette_congress",
        "surface": "Le Moniteur — the Congress column",
        "payload": "gazette_congress",
        "scene": "res://scenes/gazette_view.tscn",
        "mode": "api_stub", "method": "open", "api_method": "get_gazette",
        "must_show": "the paper's '— THE CONGRESS OF PARIS —' section after THE COURTS: the "
                     "sitting's day and each court's answer in the paper's voice",
    },
]


# ── Score Finish Step 0 (SF-M, Sept 29, 2026): the two shots SCORE_FINISH_SPEC.md §4.6 names.
# REGISTERED on a machine without the Godot binary — not yet shot; the first run with --godot takes them.
# ── SR-7d DC-3c: the doctrines' boards (DOCTRINES_SPEC §4a) ──────────────────
SHOTS += [
    {
        "id": "generals_doctrine",
        "surface": "Generals — OUR DOCTRINE above the ladder",
        "payload": "marshal_overview_doctrine",
        "scene": "res://scenes/marshal_management.tscn",
        "mode": "api_stub", "method": "open", "api_method": "get_marshal_overview",
        "must_show": "OUR DOCTRINE — The Corps System: the says line, the strength and the flaw "
                     "with their numbers, the flaw's cure status; THE LAURELS below it; "
                     "nothing clipped at scale 2.0",
    },
    {
        "id": "diplo_doctrine_nations",
        "surface": "Diplomatic Ledger — Nations (every court's doctrine)",
        "payload": "diplo_doctrine",
        "scene": "res://scenes/diplomatic_ledger.tscn",
        "mode": "api_stub", "method": "open", "api_method": "get_diplomatic_ledger", "tab": 0,
        "must_show": "a Doctrine line on each great power's card — Austria's reading 'cured since "
                     "turn 1' beside its Laws line, the others 'uncured — <law> would end it once "
                     "<Staff> stands'; at most two lines per court with the laws line",
    },
    {
        "id": "ledger_laws_train",
        "surface": "Strategic Ledger — Laws (the Train's cure line)",
        "payload": "ledger_laws_train",
        "scene": "res://scenes/strategic_ledger.tscn",
        "mode": "api_stub", "method": "open", "api_method": "get_ledger", "tab": 7,
        "must_show": "the Train des Équipages row carrying 'Cures Living off the land — 1 corps "
                     "drawing 80% now ; needs the Grand Quartier Général in force'",
    },
    *[
        {
            "id": f"region_doctrine_{region.lower()}",
            "surface": f"Region Action Panel — {region} ({label})",
            "payload": "game_state_doctrine_regions",
            "scene": "res://scenes/region_panel.tscn",
            "mode": "map_stub", "method": "show_region",
            "args": [region, "$map"],
            "must_show": must,
        }
        for region, label, must in [
            ("Posen", "Prussian, unscouted — the poor mark is geography",
             "'Poor country — a French army here draws 80% (living off the land)' under the "
             "Supply line, with Income / Stability / Supply reading Unknown"),
            ("Tyrol", "Austrian, stripped by war, FULL",
             "'Stripped by war (35%) — poor country for a French army until it recovers below "
             "25%' under the Supply line, beside the War damage figure"),
        ]
    ],
]

SHOTS += [
    {
        "id": "proclamation_warsaw",
        "surface": "The Proclamation — a client carved at the peace table (NA-6c)",
        "payload": "proclamation_warsaw",
        "scene": "res://scenes/proclamation_popup.tscn",
        "mode": "call", "method": "show_proclamation",
        "must_show": "A NATION IS PROCLAIMED over the Duchy of Warsaw's flag; 'By your hand.'; no struck old "
                     "name (nothing died to make it); the engraved forms line; one Acknowledge; no raw tag",
    },
    {
        # EA-E8 (the economy gate, October 5, 2026): this row was staged as
        # `open`, which sends `_fetch_nations` over a raw HTTPRequest to
        # whatever answers on the port — the player's own game when it runs
        # on 8005 — and shot the "Loading…" frame two EYES votes rested on.
        # It renders the captured step-1 payload like every other wizard
        # shot (`_render_nations` adds the Formable Nations entry itself).
        "id": "wizard_formables_entry",
        "surface": "The Cabinet wizard — step 1 with the Formable Nations entry (NA-6d §11.6-8)",
        "payload": "wizard_nations",
        "scene": "res://scenes/diplomacy_wizard.tscn",
        "mode": "call", "method": "show", "args": [],
        "steps": [
            {"set_path": "_current_step", "value": 1},
            {"set_path": "title_label.text", "value": "DIPLOMACY"},
            {"set_path": "assessment_panel.text", "value": "[color=#a0a0a8]\"Your Excellency, which nation requires our diplomatic attention?\"[/color]"},
            {"call": "_lay_out_prompt", "args": [1]},
            {"call": "_render_nations", "args": ["$payload"]},
            {"call": "refit", "args": []},
            {"wait": 4},
        ],
        "must_show": "the one-line step-1 prompt; the nation list; the 'Formable Nations' entry present and "
                     "enabled (the step-3 rows are wizard_formables_step3's, rendered from GET /formables)",
    },
    # ═══ Score Finish Step 7 slices 7–8 (registered by the Step 7 frames, Oct 4) ═══
    {
        "id": "rail_counter_punch",
        "surface": "Notice rail — the counter-punch row opened, with its button (slice 8)",
        "payload": "notifications_counter_punch",
        "scene": "res://scenes/notification_bar.tscn",
        "mode": "call", "method": "update_notifications",
        "place": {"position": [0, 0], "height": 120},
        "steps": [
            {"press": {"meta_key": "notification_data", "meta_field": "type",
                       "equals": "counter_punch_earned"}},
            {"wait": 12},
        ],
        "must_show": "the row's detail panel open: Davout's counter-punch message naming Mack within "
                     "reach at Swabia, ONE full-width gold button 'Strike Mack — free' above "
                     "Keep / Acknowledge; nothing clipped at scale 2.0",
    },
    {
        "id": "region_paris_build_open",
        "surface": "Region Action Panel — Paris, the Build rows unfolded (WO-V-D1)",
        "payload": "game_state_regions",
        "scene": "res://scenes/region_panel.tscn",
        "mode": "map_stub", "method": "show_region",
        "args": ["Paris", "$map"],
        "steps": [
            {"call": "_on_meta_clicked", "args": ["toggle:build"]},
            {"wait": 8},
        ],
        "must_show": "the header reads '▾ Build' and the build rows show beneath it (the folded "
                     "default, '▸ Build — N works', is region_paris's own frame)",
    },
    {
        "id": "ledger_orders_display",
        "surface": "Strategic Ledger — Orders tab, a pursuit of an Archduke (NPC-12, slice 7)",
        "payload": "ledger_orders_display",
        "scene": "res://scenes/strategic_ledger.tscn",
        "mode": "api_stub", "method": "open", "api_method": "get_ledger",
        "tab": 5,
        "must_show": "Lannes's Pursue order names 'Archduke John' — never the roster key "
                     "'ArchdukeJohn'",
    },
    {
        "id": "campaign_log_tiers",
        "surface": "Campaign log — the importance tiers on a played board (EAS-2 client half)",
        "payload": "campaign_log_t20",
        "scene": "res://scenes/campaign_log.tscn",
        "mode": "api_stub", "method": "open_log", "api_method": "get_campaign_log",
        "must_show": "lead rows larger and bold, notable rows mid-size, routine rows smallest; the "
                     "glyphs kept; no raw key",
    },
    *[
        {
            "id": f"settlement_white_review_{tag}",
            "surface": f"The white peace's review — {label} (SF-V2's eyes-on check)",
            "payload": f"settlement_white_review_{tag}",
            "scene": "res://scenes/proposal_confirm_popup.tscn",
            "mode": "call", "method": "show_dialogue",
            "must_show": must,
        }
        for tag, label, must in (
            ("ratify", "Austria beaten and alone at the table",
             "the header 'Will carry as drafted' beside a LIVE 'Ratify White Peace' — the "
             "verdict and the button agree"),
            ("holdout", "the whole-war table at the same score",
             "the header 'Will NOT carry as drafted' and NO Ratify button — only the roads "
             "that remain (return to terms, the separate peace, the truce)"),
        )
    ],
    # ═══ Score Finish Step 7 slice 9 — the frames' own fixes (Oct 5) ═══
    {
        "id": "interrupt_last_stand",
        "surface": "The last-stand question (SF7-X27)",
        "payload": "interrupt_last_stand",
        "scene": "res://scenes/interrupt_popup.tscn",
        "mode": "call", "method": "show_interrupt",
        "steps": [{"wait": 6}],
        "must_show": "NEY REPORTS; the cornered line; Fight to the Last / Attempt a Breakout — "
                     "on a box that fits them, no empty panel below the buttons",
    },
    {
        "id": "wizard_formables_step3",
        "surface": "The Cabinet wizard — step 3, the Formable Nations (SF7-X28)",
        "payload": "formables_after_carve",
        "scene": "res://scenes/diplomacy_wizard.tscn",
        "mode": "call", "method": "show", "args": [],
        "steps": [
            {"set_path": "_current_step", "value": 3},
            {"set_path": "title_label.text", "value": "DIPLOMACY — FORMABLE NATIONS"},
            {"set_path": "assessment_panel.text",
             "value": "[color=#a0a0a8]\"The map of Europe is not finished, Sire. These states "
                      "could yet exist — each names what its existence would require.\"[/color]"},
            {"set_path": "back_button.visible", "value": True},
            {"call": "_lay_out_prompt", "args": [3]},
            {"call": "_render_formables", "args": ["$payload"]},
            {"call": "refit", "args": []},
            {"wait": 4},
        ],
        "must_show": "the two-line quote directly over the list — no blank band between them; "
                     "every row with its gate terms (the step-3 rows the live session drove; "
                     "rendered here from the captured GET /formables, not over HTTP)",
    },
]

# ═══ Score Finish Step 7b "The front page of the peace" (October 5, 2026) ═══
# The capture group is `front_page` (`cap_front_page`: the Step 7b pins' own
# quiet-peace board with London paying Vienna against us, and the boot
# briefing for SF7-X47's TODAY header).
SHOTS += [
    {
        "id": "dispatch_front_page",
        "surface": "Dispatch re-read (the front page of the peace)",
        "payload": "dispatch_front_page",
        "scene": "res://scenes/dispatch_view.tscn",
        "mode": "api_stub", "method": "open", "api_method": "get_dispatch",
        "must_show": "the league's own news leads ('London now pays Vienna 500 gold a turn "
                     "against us', with the price to keep her out); no raw tag",
    },
    {
        "id": "dispatch_front_page_league",
        "surface": "Dispatch re-read (the next league under COALITION THREAT)",
        "payload": "dispatch_front_page",
        "scene": "res://scenes/dispatch_view.tscn",
        "mode": "api_stub", "method": "open", "api_method": "get_dispatch",
        "steps": [{"scroll_to": {"text": "COALITION THREAT"}, "then_wait": 4}],
        "must_show": "the threat line, then the next league: 'At this pace the courts consult "
                     "on turn …' and one row per court with its status and its price",
    },
    {
        "id": "diplo_balance_next_league",
        "surface": "Diplomatic Ledger — Balance of Europe (THE NEXT LEAGUE)",
        "payload": "diplo_ledger_front_page",
        "scene": "res://scenes/diplomatic_ledger.tscn",
        "mode": "api_stub", "method": "open", "api_method": "get_diplomatic_ledger", "tab": 2,
        "steps": [{"scroll_to": {"text": "THE NEXT LEAGUE"}, "then_wait": 4}],
        "must_show": "THE NEXT LEAGUE in place of the bare list: the summary line in amber, a "
                     "row per court (who would join, what her war reopens, who pays her, the "
                     "price to keep her out), the footer; nothing clipped at scale 2.0",
    },
    {
        "id": "dispatch_boot_today",
        "surface": "Dispatch re-read (the boot briefing's TODAY)",
        "payload": "dispatch_boot_today",
        "scene": "res://scenes/dispatch_view.tscn",
        "mode": "api_stub", "method": "open", "api_method": "get_dispatch",
        "steps": [{"scroll_to": {"text": "TODAY"}, "then_wait": 4}],
        "must_show": "no headline on the first morning; TODAY's header says the list is a "
                     "choice ('choose among them; they share one treasury and one army'), "
                     "four orders beneath it",
    },
]


# ═══ UXR-0 (October 9, 2026): the surfaces the user could not read ═══════════
# The war room is `main.tscn` itself behind the harness's MainStub (mode
# "main"): the connection test and the topology answered with real captures,
# then the /new_game response through `_on_new_game_result` — the menu's own
# Begin. The boot is WAITED FOR on its own flag (main.gd's 0.5 s timer is
# real time; the engine's frames are not, parked off-screen).
_WAR_ROOM_STEPS = [
    {"wait_for": "_initial_map_bootstrapped", "timeout": 1800, "then_wait": 10},
    {"call": "_on_new_game_result", "args": ["$payload.new_game"], "then_wait": 30},
]
SHOTS += [
    {
        "id": "war_room_boot",
        "surface": "The war room — map, command window, top bar (Begin the 1805 campaign)",
        "payload": "war_room_boot",
        "scene": "res://scenes/main.tscn",
        "mode": "main", "method": "",
        "steps": _WAR_ROOM_STEPS,
        "settle": 40,
        "must_show": "the 1805 map with its labels, the command window bottom-left with "
                     "the turn-1 briefing, the top bar's counters and nav, the war HUD "
                     "bottom-right; every text row's physical size in the census",
    },
    {
        "id": "war_room_tutorial",
        "surface": "The war room — the School of War's first morning, tutor card top-right",
        "payload": "war_room_tutorial",
        "scene": "res://scenes/main.tscn",
        "mode": "main", "method": "",
        "steps": _WAR_ROOM_STEPS,
        "settle": 40,
        "must_show": "the Danube Lesson's map, the command window, THE SCHOOL OF WAR card "
                     "top-right reading 'I. The Situation' — the surface the user could "
                     "not read; its body rows' physical size in the census",
    },
    {
        "id": "war_room_pause_settings",
        "surface": "The war room — the pause menu open on Settings (UXR-X2)",
        "payload": "war_room_boot",
        "scene": "res://scenes/main.tscn",
        "mode": "main", "method": "",
        "steps": _WAR_ROOM_STEPS + [
            {"node": "@pause_menu", "call": "open_menu", "then_wait": 8},
            {"node": "@pause_menu", "call": "_on_settings", "then_wait": 12},
        ],
        "settle": 30,
        "must_show": "the pause panel with its Settings unfolded: the Interface Scale slider "
                     "and the sound rows readable, NOT squeezed to a sliver by the clamp",
    },
    {
        "id": "tutorial_card",
        "surface": "The School of War card alone (tutorial_overlay.tscn)",
        "payload": "new_game_tutorial",
        "scene": "res://scenes/tutorial_overlay.tscn",
        "mode": "call", "method": "on_world_swap",
        "settle": 20,
        "must_show": "THE SCHOOL OF WAR · 1 of 20 · 'I. The Situation' and its body, the "
                     "quill chip and the Skip chip; the card's width and the body's size "
                     "in the census",
    },
    {
        "id": "main_menu",
        "surface": "The main menu (first boot)",
        "payload": "test_boot",
        "scene": "res://scenes/main_menu.tscn",
        "mode": "call", "method": "",
        "settle": 100,
        "must_show": "the title block, the campaign column, the status line; the menu "
                     "drawn at the Interface Scale the settings hold (UXR-X1)",
    },
    {
        "id": "main_menu_settings",
        "surface": "The main menu — Settings open",
        "payload": "test_boot",
        "scene": "res://scenes/main_menu.tscn",
        "mode": "call", "method": "",
        "steps": [{"wait": 90}, {"call": "_open_settings", "then_wait": 12}],
        "settle": 20,
        "must_show": "the SETTINGS view: INTERFACE with the scale slider, SOUND, SMARTER "
                     "PARSING, SPOKEN ORDERS, CREDITS — every hint's size in the census",
    },
]


def load_manifest(payload_dir: pathlib.Path) -> dict:
    m = json.loads((payload_dir / "manifest.json").read_text(encoding="utf-8"))
    return {c["name"]: c for c in m["captures"]}


def expand_physical(shots: list[dict], physical_scale: str) -> list[dict]:
    """One spec shot per (surface, resolution): the window sized to the
    monitor, the Interface Scale as a player at that size would have it (or
    the shipped 1.0 for the BEFORE picture). The base id is kept on the row
    so the report groups the five frames of one surface."""
    out = []
    for row in shots:
        for (w, h) in PHYSICAL_RESOLUTIONS:
            scale = derive_ui_scale(w, h) if physical_scale == "auto" else float(physical_scale)
            r = dict(row)
            r["base_id"] = row["id"]
            r["id"] = f"{row['id']}__{w}x{h}"
            r["window"] = [w, h]
            r["scales"] = [scale]
            r["resolution"] = [w, h]
            r["physical_scale"] = scale
            r.pop("window_by_scale", None)
            out.append(r)
    return out


def build_spec(shots: list[dict], captures: dict, scales: list[float], date: str,
               spec_path: pathlib.Path, result_path: pathlib.Path,
               png_dir: pathlib.Path | None = None) -> tuple[dict, list[dict]]:
    # SF-R (Step 8): a scoring run keeps its frames in its own run directory
    # (`--png-dir`); every other caller writes them to docs/audits as before.
    png_dir = AUDITS if png_dir is None else pathlib.Path(png_dir)
    out_shots, index = [], []
    for row in shots:
        cap = captures.get(row["payload"])
        if cap is None:
            print(f"  ! no payload '{row['payload']}' for {row['id']} — skipped")
            continue
        # `out` is keyed by the harness's own scale key ("%.1f"): one PNG per
        # Interface Scale, so a clipped frame at 2.0 is its own file.
        row_scales = row.get("scales", scales)
        out = {}
        for s in row_scales:
            if "resolution" in row:
                # Physical mode: the frame is named by its monitor and scale.
                w, h = row["resolution"]
                out["%.1f" % s] = str(png_dir / f"UXR0_{row['base_id'].upper()}_{w}x{h}_S{s:.2f}_{date}.png")
            else:
                tail = "" if abs(s - 1.0) < 1e-9 else "_X%g" % s
                out["%.1f" % s] = str(png_dir / f"IQ10_{row['id'].upper()}{tail}_{date}.png")
        shot = {
            "id": row["id"],
            "scene": row["scene"],
            "mode": row["mode"],
            "method": row["method"],
            "payload": cap["file"],
            "out": out,
            "scales": list(row_scales),
        }
        # NUI (Sept 23, 2026): a row may carry its own `steps` (the Admiralty
        # chip is fed by a second call after the entry method) — the tuple
        # below is the ONLY road a row key takes into the spec, and `steps`
        # was not on it, so the chip shot rendered the bare bar in silence.
        for key in ("args", "api_method", "place", "settle", "window", "window_by_scale",
                    "formation_overrides", "downscale", "steps"):
            if key in row:
                shot[key] = row[key]
        if "tab" in row:
            # Step 7b's frames: the tab switch used to REPLACE a row's own
            # steps, so a row carrying both (the first was THE NEXT LEAGUE's
            # scroll) shot the tab's top in silence. The switch runs first,
            # then the row's steps.
            shot["steps"] = ([{"call": "_switch_tab", "args": [row["tab"]], "then_wait": 4}]
                             + list(row.get("steps") or []))
        out_shots.append(shot)
        entry = {
            "id": row["id"],
            "surface": row["surface"],
            "payload": row["payload"],
            "staging": cap["staging"],
            "facts": cap.get("facts", {}),
            "must_show": row["must_show"],
            "png_by_scale": dict(out),
        }
        if "resolution" in row:
            entry["base_id"] = row["base_id"]
            entry["resolution"] = row["resolution"]
            entry["physical_scale"] = row["physical_scale"]
        index.append(entry)
    spec = {
        "shots": out_shots,
        "scales": scales,
        "window": [1600, 900],
        "window_position": WINDOW_POSITION,
        "result": str(result_path),
    }
    spec_path.write_text(json.dumps(spec, indent=1), encoding="utf-8")
    return spec, index


def run_godot(godot: str, spec_path: pathlib.Path, log_path: pathlib.Path,
              project: pathlib.Path | None = None) -> int:
    env = dict(os.environ)
    env["IQ10_SPEC"] = str(spec_path)
    env.pop("PYTHONIOENCODING", None)
    # Never the player's 8005 (Golden Rule 7): the harness refuses main.tscn
    # on it, and nothing in a capture should reach a live game.
    if env.get("SOVEREIGN_PORT", "") in ("", "8005"):
        env["SOVEREIGN_PORT"] = HARNESS_PORT
    # UXR-0: `--project` shoots ANOTHER checkout's client (a pristine HEAD
    # worktree is how the BEFORE picture is taken honestly after the tree
    # has moved) with THIS repo's harness, by absolute path.
    project = project or PROJECT
    script = SCRIPT if project == PROJECT else str(REPO / "tools" / "iq10_surface_screenshot.gd")
    args = [godot, "--audio-driver", "Dummy", "--windowed", "--resolution", "1600x900",
            "--position", f"{WINDOW_POSITION[0]},{WINDOW_POSITION[1]}",
            "--log-file", str(log_path),
            "--path", str(project), "--script", script]
    proc = subprocess.run(args, env=env, cwd=str(REPO), capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=3600)
    return proc.returncode


def script_errors(log_path: pathlib.Path) -> list[str]:
    if not log_path.exists():
        return ["(no engine log written)"]
    text = log_path.read_text(encoding="utf-8", errors="replace")
    body = text
    if "[IQ10] BEGIN" in text:
        body = text.split("[IQ10] BEGIN", 1)[1]
    if "[IQ10] END" in body:
        body = body.split("[IQ10] END", 1)[0]
    return [ln.strip() for ln in body.splitlines() if "SCRIPT ERROR" in ln]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--scales", default="1.0,2.0")
    ap.add_argument("--date", default="2026_09_19")
    ap.add_argument("--godot", default=os.environ.get("IQ10_GODOT", GODOT_DEFAULT))
    ap.add_argument("--payload-dir", default=os.environ.get("IQ10_PAYLOADS", ""))
    ap.add_argument("--out-dir", default="")
    ap.add_argument("--png-dir", default="")
    ap.add_argument("--physical", action="store_true",
                    help="UXR-0: one frame per surface per PHYSICAL_RESOLUTIONS entry")
    ap.add_argument("--physical-scale", default="auto",
                    help="auto (derive_ui_scale) or a number such as 1.0 (the BEFORE picture)")
    ap.add_argument("--project", default="",
                    help="another checkout's godot-client/project-sovereign to shoot (a "
                         "pristine worktree for a BEFORE record); the harness stays this repo's")
    args = ap.parse_args()

    payload_dir = pathlib.Path(args.payload_dir) if args.payload_dir else None
    if payload_dir is None:
        raise SystemExit("--payload-dir (or IQ10_PAYLOADS) must name the directory "
                         "tools/iq10_capture_payloads.py wrote")
    work = pathlib.Path(args.out_dir) if args.out_dir else payload_dir.parent / "run"
    work.mkdir(parents=True, exist_ok=True)
    AUDITS.mkdir(parents=True, exist_ok=True)
    if args.png_dir:
        png_dir = pathlib.Path(args.png_dir)
    elif args.physical:
        # Physical frames are a RUN's evidence (five per surface); the ones
        # a slice commits are copied to docs/audits by hand, named by surface.
        png_dir = work / "frames"
    else:
        png_dir = AUDITS
    png_dir.mkdir(parents=True, exist_ok=True)

    captures = load_manifest(payload_dir)
    scales = [float(s) for s in args.scales.split(",") if s.strip()]
    wanted = [s.strip().lower() for s in args.only.split(",") if s.strip()]
    shots = [s for s in SHOTS if not wanted or any(w in s["id"].lower() for w in wanted)]
    if args.physical:
        shots = expand_physical(shots, args.physical_scale)
        print(f"{len(shots)} physical frame(s) over {len(PHYSICAL_RESOLUTIONS)} resolutions "
              f"(scale {args.physical_scale})")
    else:
        print(f"{len(shots)} shot(s) x {len(scales)} scale(s)")

    spec_path, result_path = work / "spec.json", work / "result.json"
    log_path = work / "engine.log"
    spec, index = build_spec(shots, captures, scales, args.date, spec_path, result_path,
                             png_dir)
    project = pathlib.Path(args.project) if args.project else None
    code = run_godot(args.godot, spec_path, log_path, project)
    errors = script_errors(log_path)
    result = json.loads(result_path.read_text(encoding="utf-8")) if result_path.exists() else {}

    # The harness writes one result row per (shot, scale), each with its frames.
    by_id: dict[str, list] = {}
    for res in (result.get("results", []) if isinstance(result, dict) else []):
        by_id.setdefault(str(res.get("id", "")), []).append(res)
    for row in index:
        row["results"] = by_id.get(row["id"], [])
    bad = [r["id"] for r in index
           if not r["results"] or any(not x.get("ok") for x in r["results"])]
    if bad:
        print(f"shots not ok: {len(bad)} -> {', '.join(bad[:8])}")
    # Provenance: which client was shot (its git commit) and at what scale
    # rule — a BEFORE record from a worktree names the commit it was taken
    # from, so nobody has to trust a label.
    try:
        client_commit = subprocess.run(
            ["git", "-C", str((project or PROJECT)), "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=30).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        client_commit = ""
    (work / "index.json").write_text(json.dumps({
        "date": args.date, "exit_code": code, "script_errors": errors,
        "spec": str(spec_path), "result": str(result_path), "log": str(log_path),
        "client_project": str(project or PROJECT), "client_commit": client_commit,
        "physical": bool(args.physical),
        "physical_scale": args.physical_scale if args.physical else None,
        "rows": index,
    }, indent=1), encoding="utf-8")
    print(f"godot exit {code}; SCRIPT ERROR lines: {len(errors)}")
    for e in errors[:10]:
        print("  " + e)
    print(f"INDEX_JSON={work / 'index.json'}")
    return 0 if code == 0 and not errors else 1


if __name__ == "__main__":
    sys.exit(main())
