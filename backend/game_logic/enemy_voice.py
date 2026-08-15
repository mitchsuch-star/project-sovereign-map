"""Enemy marshal voices — W6-6 (EXP-M2): the men you fight have mouths.

After a battle the enemy commander gets ONE line in his register, shown in
the battle report (`battle_report.enemy_voice`) and as a campaign-log
flavor suffix. Deterministic template bank (GR6): keyed by (personality ×
situation), rotated by the region's battle count (W6-2's serialized
`battle_counts`) — no RNG, reproducible. Display-only; nothing serializes.

Voice ownership (WAVE6_FUN_FACTOR_SPEC §14): enemy MARSHALS only — named
diplomats stay owned by DIPLOMAT_VOICE_BIBLE/`resolve_named_diplomat`.
"""

from typing import Dict, List, Optional

from backend.display_names import humanize_entity_name

# Situations, always from the ENEMY commander's perspective:
#   repelled_you      — he defended and held/won against your attack
#   beat_you_attacking — he attacked you and won
#   lost_ground       — he lost the field (either side)
#   forced_retreat    — he was driven from the field
#   stalemate         — neither side yielded

# XR-5 (position 9, Aug 8 2026): bank growth is APPEND-ONLY — index 0 of
# every bank is pinned by tests and by the deterministic rotation
# (battle_counts is serialized), so new variants go at the END. The audit
# measured Mack's one-line stalemate bank repeating verbatim 3× across the
# seven-battle Ulm grind: bank SIZE is the variety lever (the CA8-D4
# lesson), and the per-region battle count already advances the rotation.
_PERSONALITY_LINES: Dict[str, Dict[str, List[str]]] = {
    "aggressive": {
        "repelled_you": [
            "Come again, and I will bury you where you stand.",
            "Is that the best France sends against me?",
            "Your dead mark the high-water line. Study it.",
        ],
        "beat_you_attacking": [
            "Forward! They break — give them no time to breathe!",
            "Your line bent like green wood. Next time it snaps.",
            "I asked for one gap in your line. You gave me three.",
        ],
        "lost_ground": [
            "This field is borrowed, not surrendered. I will collect.",
            "You have my ground. Keep it warm for me.",
            "Enjoy the campfires tonight. They are the last quiet ones.",
        ],
        "forced_retreat": [
            "A withdrawal, nothing more. My sword is still drawn.",
            "Mark this place. I will answer for it in kind.",
            "I go to fetch more men. Do wait.",
        ],
        "stalemate": [
            "Neither of us yields? Good. I prefer a foe worth killing.",
            "Tomorrow, then. My men are not done with you.",
            "Blood for blood and nothing settled — so we do it again.",
        ],
    },
    "cautious": {
        "repelled_you": [
            "I do not leave my ground. You were warned.",
            "Every step you took was counted, and paid for.",
            "The approach was obvious. I had it measured a week ago.",
        ],
        "beat_you_attacking": [
            "The moment was measured twice before I struck.",
            "I attack only when the ledger favors it. It did.",
            "You were overextended. I merely presented the invoice.",
        ],
        "lost_ground": [
            "Noted. The next position will cost you double.",
            "You bought this field dearly. I doubt you can afford another.",
            "Ground can be repurchased. Armies cannot.",
        ],
        "forced_retreat": [
            "An army preserved is a battle not yet lost.",
            "I trade ground for time. Time is on my side.",
            "I decline a battle on your terms; the next is on mine.",
        ],
        "stalemate": [
            "You gained nothing. I call that a victory of arithmetic.",
            "Patience wins wars, not charges.",
            "A day of arithmetic. The sums still favor me.",
        ],
    },
    "literal": {
        "repelled_you": [
            "My orders were to hold. The position is held.",
            "The line stands where it was drawn. Precisely.",
            "The instruction said hold. Holding has occurred.",
        ],
        "beat_you_attacking": [
            "The objective was taken as instructed. Nothing further.",
            "Executed as ordered. Your dispositions were insufficient.",
            "The attack proceeded per timetable. The timetable was correct.",
        ],
        "lost_ground": [
            "The position could not be held with the forces assigned. So reported.",
            "I shall await revised instructions.",
            "Losses are recorded. Blame is a separate column.",
        ],
        "forced_retreat": [
            "Withdrawal conducted in order. The army is intact.",
            "The field is yours. My orders now read otherwise.",
            "The retirement was executed by the book. The book is intact.",
        ],
        "stalemate": [
            "The engagement is recorded as indecisive. Accurately.",
            "Both lines remain. The report writes itself.",
            "Result: nil. The paperwork, however, is complete.",
        ],
    },
}

# Marquee enemies get their own rows — these OVERRIDE the personality
# default when present for the situation.
_NAMED_LINES: Dict[str, Dict[str, List[str]]] = {
    "Mack": {
        "repelled_you": [
            "Mack does not leave his ground. He sees no reason to start today.",
            "The Danube line holds because I drew it correctly.",
            "You have read of my system, I see. It does not include losing "
            "this ground.",
        ],
        "lost_ground": [
            "A temporary derangement of the arithmetic. Vienna will understand.",
            "The map has erred, not I. The correction is being drafted.",
            "Note the hour. History will want to know who failed me.",
        ],
        "forced_retreat": [
            "This is not a rout. It is a revision of the plan.",
            "I withdraw in perfect conformity with a plan I have just "
            "completed.",
            "The army retires; the system remains intact. You will see.",
        ],
        "stalemate": [
            "You see? The position was sound. It is always sound.",
            "An honorable pause. My calculations required nothing more today.",
            "You failed to break me, which the system predicted. Consult it.",
        ],
    },
    "Kutuzov": {
        "repelled_you": [
            "Russia is patient, Frenchman. You will learn what that costs.",
            "The old man sleeps with one eye open. It was open today.",
        ],
        "lost_ground": [
            "Take the ground. Winter will take it back.",
            "Ground is Russia's cheapest possession. Spend it freely.",
        ],
        "forced_retreat": [
            "I retreat into Russia. Armies that follow me there do not return.",
            "Every verst you advance is a verst further from home.",
        ],
        "stalemate": [
            "Bleed here as long as you like. We have more blood than you have men.",
            "Sit with me a while longer. Winter is walking this way.",
        ],
    },
    "ArchdukeCharles": {
        "repelled_you": [
            "Austria has lost battles to France. Not this one.",
            "The Habsburg army you remember is not the one before you.",
        ],
        "beat_you_attacking": [
            "Your marshals are bold. Boldness is not a plan.",
            "Even the Grande Armée bleeds when pressed at the right hour.",
        ],
        "lost_ground": [
            "We will meet again on ground of my choosing.",
            "Austria endures. It is the thing we do best.",
        ],
        "stalemate": [
            "France pays full price for every Austrian mile now.",
            "Your Emperor needs quick victories. I need only deny them.",
        ],
    },
    "Wellington": {
        "repelled_you": [
            "They came on in the old style, and we saw them off in the old style.",
            "A near-run thing — which is to say, a thing we won.",
        ],
        "lost_ground": [
            "A setback. The line will be redrawn — it always is.",
            "London is not lost when a field is.",
        ],
        "stalemate": [
            "Hard pounding, gentlemen. We shall see who pounds longest.",
            "Steady is not glamorous, monsieur. It is merely undefeated.",
        ],
    },
    "Blucher": {
        "repelled_you": [
            "Vorwärts was for attacking. For you, I stood still — it was enough.",
            "Papa Blücher holds his schnapps and his ground alike.",
        ],
        "beat_you_attacking": [
            "Vorwärts! Always forwards — you finally understand the word.",
            "Hussars do not wait for permission. Neither do I.",
        ],
        "forced_retreat": [
            "Old Blücher falls back. Old Blücher always comes back.",
            "Retreat is merely the run-up, Franzose.",
        ],
        "stalemate": [
            "Tomorrow we go again. I did not get old by stopping.",
            "My men can bleed longer than your men can march.",
        ],
    },
}

VOICE_SITUATIONS = ("repelled_you", "beat_you_attacking", "lost_ground",
                    "forced_retreat", "stalemate")


def derive_enemy_situation(outcome: str, enemy_was_attacker: bool,
                           enemy_forced_retreat: bool) -> Optional[str]:
    """Map a battle outcome to the enemy commander's situation key."""
    if enemy_forced_retreat:
        return "forced_retreat"
    if outcome == "stalemate":
        return "stalemate"
    attacker_won = "attacker" in outcome and "victory" in outcome
    defender_won = "defender" in outcome and "victory" in outcome
    if enemy_was_attacker:
        if attacker_won:
            return "beat_you_attacking"
        if defender_won:
            return "lost_ground"
    else:
        if defender_won:
            return "repelled_you"
        if attacker_won:
            return "lost_ground"
    return None  # mutual destruction — no one left to speak


def pick_enemy_voice(enemy_name: str, personality: str, situation: str,
                     rotation_key: int = 0) -> str:
    """One line in the enemy commander's register ("" when none applies).

    Named rows (Mack, Kutuzov, Archduke Charles, Wellington, Blücher)
    override the personality default; rotation is deterministic by
    `rotation_key` (the region's battle count).
    """
    if situation not in VOICE_SITUATIONS:
        return ""
    # NP-0: a sovereign never speaks through the commander-voice banks —
    # not even an ENEMY one (a Kaiser/Tsar authored later gets a named row
    # or silence, never the cautious filler below). NAPOLEON_SPEC §2/§10.
    if personality == "sovereign":
        return ""
    bank = _NAMED_LINES.get(enemy_name, {}).get(situation)
    if not bank:
        bank = _PERSONALITY_LINES.get(personality, {}).get(situation)
    if not bank:
        bank = _PERSONALITY_LINES["cautious"].get(situation, [])
    if not bank:
        return ""
    line = bank[int(rotation_key) % len(bank)]
    return f"{humanize_entity_name(enemy_name)}: \"{line}\""
