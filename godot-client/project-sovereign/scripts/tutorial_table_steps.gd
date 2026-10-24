extends RefCounted
# THE SCHOOL OF WAR — THE TABLE (S14d part 2, docs/TABLE_LESSON_SPEC.md §4.2;
# October 24, 2026). The Peace of Pressburg, December 1805: seven cards over
# three turns in Berthier's voice — a mission, a separate peace, a vassal.
#
# The card is `tutorial_overlay.gd`; this script holds ONLY the Table's steps,
# bound through the registry (`LESSONS["tutorial_table"]`). Same shape as the
# Danube's `const STEPS`: id, turn_gate, title, body, suggest/suggest_action
# (always empty here — "diplomacy is never typed": every step is a door or a
# button on the real screen), `open` (a door kind main.gd answers:
# `cabinet:<court>` the Cabinet, `settlement:<war_id>:<court>` the table),
# `advance` (a predicate of tutorial_overlay.gd over response fields ONLY —
# `game_state` carries no diplomatic field), optional `refusal_of` (the line
# the door sends, so a refused door releases the step with the reason) and
# optional `alt` arms keyed by the overlay's `_table_state`.
#
# The board (`tutorial_table_1805.json`) is tuned by tools/_table_board_probe.py
# so the acts the cards name are the engine's own verdicts: Austria's row
# WILL SIGN (57 of 50), her separate peace 69 (Favorable) and signed the
# second morning; Bavaria's suggested vassalage 45 COUNTER, eased once 54
# ACCEPT and signed the third morning. A line's fact the board does not
# deliver changes the line, never the board.
#
# History on the cards is the record's (Austerlitz 2 December; the armistice
# 4–6 December; Pressburg 26 December; Bavaria a kingdom 1 January 1806; the
# Confederation of the Rhine 12 July 1806). The game steps — the Reassure
# mission, the eased terms — are game steps and are not dressed as history.
# The cards name offices only as the record holds them (S14D-X41): the
# Elector of Bavaria, the Tsar, Austria's envoy — never a man's later office.

const STEPS := [
	{
		"id": "austerlitz",
		"turn_gate": 1,
		"title": "I. The Day After Austerlitz",
		"body": "Sire — Ulm and Austerlitz are on the record, Vienna is ours, and the Tsar's army is marching home by the Hungarian road. The war is now made at the table. Before you treat with Austria, hold your ally: open the Cabinet on Bavaria and send Talleyrand to REASSURE her — one diplomatic point a turn, of the five you hold; they return each morning. An ally is reassured, not courted; a neutral is courted. Her warmth must hold while we treat with her enemy and then ask more of her. Confirm on the card that follows.",
		"suggest": "",
		"suggest_action": "",
		"open": "cabinet:Bavaria",
		"open_label": "Open the Cabinet on Bavaria ▸",
		"advance": "_pred_mission_started",
	},
	{
		"id": "table",
		"turn_gate": 1,
		"title": "II. Every Court for Itself",
		"body": "A war with two courts is settled at ONE table, Sire. Open it below: the door stages Talleyrand's draft on the whole war for no diplomatic point and no action, and Bavaria's claim to the Tyrol arrives beside it — the peace itself answers her. Read the rows: Austria's reads WILL SIGN; Russia holds out, for her seat is unbeaten and a whole-war peace needs every court's consent. Britain is not at this table — no war with her stands on this board. The table's own line, at its foot, names what the table is.",
		"suggest": "",
		"suggest_action": "",
		"open": "settlement:war_1:Austria",
		"open_label": "Open the table ▸",
		"refusal_of": "propose common peace with Austria",
		"advance": "_pred_table_mounted",
	},
	{
		"id": "austria_alone",
		"turn_gate": 1,
		"title": "III. Austria Alone",
		"body": "Then leave Russia at war and take Austria alone, Sire. On her row stands the chip SEPARATE PEACE WITH AUSTRIA, with the figure her envoy reads for it. Click it: the chooser says what a separate peace does to our allies — PROCEED, and Talleyrand lays the bilateral draft before you, her slice of the table in his own hand. Send it as suggested — three diplomatic points — then end the turn. Austria answers in the morning.",
		"suggest": "",
		"suggest_action": "",
		"advance": "_pred_austria_peace_sent",
	},
	{
		"id": "pressburg",
		"turn_gate": 2,
		"title": "IV. The Peace of Pressburg",
		"body": "Austria signed alone, Sire — as she did at Pressburg on the 26th of December. The Tsar would not sign and marched his army home; Britain, not on this board, fought on. The war card now reads Russia alone, and Bavaria and Italy, carried in by our peace, are at peace with Vienna too. A separate peace is the Emperor's oldest instrument: break the league one court at a time.",
		"suggest": "",
		"suggest_action": "",
		"advance": "_pred_austria_peace_signed",
		# The board is tuned so she signs; the arm is for a drift.
		"alt": {
			"austria_refused": {
				"body": "Austria has NOT signed, Sire — her envoy's answer stands on the notice rail. A refusal is her price named: read it, and answer it from the Cabinet — ease the terms, or send them again — or fight on. The school moves on when you end the turn.",
			},
		},
	},
	{
		"id": "bavaria",
		"turn_gate": 2,
		"title": "V. The Kingdom of Bavaria",
		"body": "Now the ally who fought beside us, Sire. Open the Cabinet on Bavaria and PROPOSE VASSALAGE: a vassal keeps her crown and her army, pays what the treaty names, and follows our wars; her LOYALTY and her AUTONOMY are the two dials of the bond — the Diplomatic Ledger's Vassals rows keep them — and only a court of half our power or less may be bound. Europe reads every treaty vassal as a threat: five points on the scale. On the terms page Talleyrand's own suggestion reads that a counter is likely — ease it ONCE (MORE GENEROUS) and the estimate turns; send, then end the turn. On the 1st of January 1806 the Elector of Bavaria was a king; by July his kingdom stood inside the Confederation of the Rhine, under our protection.",
		"suggest": "",
		"suggest_action": "",
		"open": "cabinet:Bavaria",
		"open_label": "Propose vassalage ▸",
		"advance": "_pred_bavaria_vassal_sent",
		"alt": {
			"letter_waiting": {
				"body": "A letter stands on the notice rail, Sire — answer the envoy first; the Cabinet waits on your word. Then open the Cabinet on Bavaria and PROPOSE VASSALAGE: ease Talleyrand's suggestion once (MORE GENEROUS), send, and end the turn.",
			},
		},
	},
	{
		"id": "first_stone",
		"turn_gate": 3,
		"title": "VI. The First Stone",
		"body": "Bavaria is yours to protect, Sire. Her loyalty stands in the Diplomatic Ledger's Vassals rows ([color=#e8d4a8]D[/color]) and drifts a little each turn unless it is tended — invest in her, grant her autonomy, garrison her capital, or cede her a province; what the treaty names she pays each morning, and her corps marches when we call. The first stone of the Confederation is laid.",
		"suggest": "",
		"suggest_action": "",
		"advance": "_pred_bavaria_vassal_signed",
		"alt": {
			"bavaria_countered": {
				"body": "Bavaria has COUNTERED, Sire — her envoy's card stands before you with the terms she will sign, and it names what she struck. Accept her counter on the card, and she is yours to protect by the next morning.",
			},
		},
	},
	{
		"id": "handoff",
		"turn_gate": 3,
		"title": "VII. The Lesson Ends",
		"body": "Three acts in three turns, Sire: a mission, a separate peace, a vassal. Every screen you opened here keeps its first note for the great campaign — the Cabinet, the table, the chooser — and the roads of the Empire wait there under the Cabinet. The real war of 1805 is at the main menu under BEGIN.",
		"suggest": "",
		"suggest_action": "",
		"advance": "_pred_never",
	},
]
