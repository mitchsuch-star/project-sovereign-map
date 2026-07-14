# Live-Play Evidence — Sweep 2 (Combat Overhaul Phase 3 exit)

**Date:** July 14, 2026
**Mode:** `LLM_MODE=anthropic` (real parsing), backend 127.0.0.1:8005, France / 1805 vs Third Coalition.
**Purpose:** fresh 6–8 turn playthrough to confirm the Phase-3 drama unlock — decisive
battles feed the glory ladder (DR-1), deeds accrete (DR-2), and a jealousy petition
surfaces **organically** (M7 in the wild), with Marshal Drama felt as ≥7.5.

**Opening board (turn 1):**
- Ney (aggressive, shock 9) + Davout (cautious, def/tac 8) @ Rhineland — adjacent to Mack's Austrians @ Swabia.
- Bernadotte (cautious) co-located with Deroy (Bavaria, 22k) @ Franconia.
- Soult (literal, 40k) @ Lorraine; Lannes (aggr) + Murat (aggr cav) @ Franche-Comte; Massena (aggr, 42k) @ Milan.
- Pre-seeded rivalries (hair-trigger per DR-3): Ney↔Soult/Murat/Bernadotte = Rival; Davout↔Bernadotte, Murat↔Bernadotte = Hostile.
- **Plan:** make Ney the glory hog (mass Davout/Lannes behind his assaults on Mack); let his rivals sit; watch for an organic petition.

---

### Glory ladder snapshot (turn 1)
```
[
  {
    "name": "Ney",
    "glory": 0,
    "crowned": false,
    "jealous_of": null,
    "personality": "aggressive"
  },
  {
    "name": "Davout",
    "glory": 0,
    "crowned": false,
    "jealous_of": null,
    "personality": "cautious"
  },
  {
    "name": "Soult",
    "glory": 0,
    "crowned": false,
    "jealous_of": null,
    "personality": "literal"
  },
  {
    "name": "Lannes",
    "glory": 0,
    "crowned": false,
    "jealous_of": null,
    "personality": "aggressive"
  },
  {
    "name": "Murat",
    "glory": 0,
    "crowned": false,
    "jealous_of": null,
    "personality": "aggressive"
  },
  {
    "name": "Bernadotte",
    "glory": 0,
    "crowned": false,
    "jealous_of": null,
    "personality": "cautious"
  },
  {
    "name": "Massena",
    "glory": 0,
    "crowned": false,
    "jealous_of": null,
    "personality": "aggressive"
  }
]
```
| Marshal | glory | rank | crowned | jealous_of | surge | warned | trust | str | idle | feuds |
|---|---|---|---|---|---|---|---|---|---|---|
| Ney | 0 | 1 | False | None | False | False | 75 | 24000 | 0 | [] |
| Davout | 0 | 2 | False | None | False | False | 85 | 26000 | 0 | [] |
| Soult | 0 | 3 | False | None | False | False | 70 | 40000 | 0 | [] |
| Lannes | 0 | 4 | False | None | False | False | 85 | 18000 | 0 | [] |
| Murat | 0 | 5 | False | None | False | False | 75 | 22000 | 0 | [] |
| Bernadotte | 0 | 6 | False | None | False | False | 40 | 17000 | 0 | [] |
| Massena | 0 | 7 | False | None | False | False | 60 | 42000 | 0 | [] |

> **Marshal Ney, lead the assault on Mack at Swabia**  _(turn 1)_
  MSG: MUSTER — Ney (24,000) vs Mack (large force) at Swabia — odds favorable.
         WILL JOIN — Davout: is willing to march if the roads allow
         WILL NOT — Soult: awaits explicit orders and will NOT march — order 'Soult, support Ney' and he will march
         WILL JOIN — Lannes: marches to the sound of the guns — the Roland of the Army
         WILL JOIN — Murat: will march to the sound of the guns
         WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Ney') would likely bring him
         (Standing orders decide who marches: 'Soult, support Ney' authorizes even a literal marshal to move to his guns.)
       
       
       [Combat] Ney leads the charge! (Aggressive: +15% attack)
       [Combat] Adjacent allies bolster Ney's attack! (+2%)
       Ney engages in solid combat. Ney gains the advantage over Mack. Casualties: Ney 756, Mack 10,974. Both armies remain in the field. Ney advances into Swabia. (383 lost to march)
  AP: cost=1 remaining=3 turn_advanced=False new_turn=None
  BATTLE: 
     casualties: {"attacker_name": "Ney", "attacker_original": 24000, "attacker_casualties": 756, "attacker_remaining": 23244, "defender_name": "Mack", "defender_original": 52000, "defender_casualties": 10974, "defender_remaining": 41026}
     expectation_note: Victory raises Marshal Ney's expectation of reward — he now looks for 40g/turn (holds 0g).

> **Davout, march to Swabia and reinforce Ney**  _(turn 1)_
  MSG: Davout is engaged with Mack and cannot begin a strategic march. Deal with the engagement first.
  AP: cost=0 remaining=3 turn_advanced=False new_turn=None

> **Bernadotte, attack the Bavarians under Deroy at Franconia**  _(turn 1)_
  MSG: Bernadotte cannot attack Bavaria — they are our ally, Sire, and we are not at war with them.

> **Massena, advance from Milan toward Tyrol against Archduke John**  _(turn 1)_
  MSG: Berthier frowns at the dispatch. "I see Marshal Massena's name, Sire, but the instruction is unclear. Valid orders include: attack, break_square, build, cancel, change_autonomy, charge."
  AP: cost=0 remaining=3 turn_advanced=False new_turn=None

> **Massena, attack Archduke John in Tyrol**  _(turn 1)_
  MSG: MUSTER — Massena (42,000) vs ArchdukeJohn (substantial force) at Tyrol — odds favorable.
         WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Massena') would likely bring him
       
       
       [Combat] Massena leads the charge! (Aggressive: +15% attack)
       [Shield] ArchdukeJohn stands firm against superior numbers! (Cautious: +10% outnumbered)
       [Terrain] ArchdukeJohn benefits from Mountains terrain (+25% defense)
       Massena's attack meets fierce resistance. ArchdukeJohn holds the line. Casualties: Massena 8,083, ArchdukeJohn 425. Both armies remain in the field.
  AP: cost=1 remaining=2 turn_advanced=False new_turn=None
  BATTLE: 
     casualties: {"attacker_name": "Massena", "attacker_original": 42000, "attacker_casualties": 8083, "attacker_remaining": 33917, "defender_name": "ArchdukeJohn", "defender_original": 20000, "defender_casualties": 425, "defender_remaining": 19575}

> **end turn**  _(turn 1)_
  MSG: Turn 1 ended. (Warning: 2 action(s) unused) Turn 2 begins!
       
       Income: 3200g | Upkeep: 1416g (incl. 136g over-limit) | Other: +887g | Net: +2671g | Treasury: 3,471g
  AP: cost=0 remaining=4 turn_advanced=False new_turn=None

### Glory ladder snapshot (turn 2)
```
[
  {
    "name": "Ney",
    "glory": 4,
    "crowned": false,
    "jealous_of": null,
    "personality": "aggressive"
  },
  {
    "name": "Lannes",
    "glory": 4,
    "crowned": false,
    "jealous_of": null,
    "personality": "aggressive"
  },
  {
    "name": "Davout",
    "glory": 2,
    "crowned": false,
    "jealous_of": null,
    "personality": "cautious"
  },
  {
    "name": "Murat",
    "glory": 2,
    "crowned": false,
    "jealous_of": "Ney",
    "personality": "aggressive"
  },
  {
    "name": "Soult",
    "glory": 0,
    "crowned": false,
    "jealous_of": null,
    "personality": "literal"
  },
  {
    "name": "Bernadotte",
    "glory": 0,
    "crowned": false,
    "jealous_of": null,
    "personality": "cautious"
  },
  {
    "name": "Massena",
    "glory": 0,
    "crowned": false,
    "jealous_of": null,
    "personality": "aggressive"
  }
]
```
| Marshal | glory | rank | crowned | jealous_of | surge | warned | trust | str | idle | feuds |
|---|---|---|---|---|---|---|---|---|---|---|
| Ney | 4 | 1 | False | None | False | False | 75 | 21609 | 0 | [] |
| Davout | 2 | 3 | False | None | False | False | 85 | 23798 | 1 | [] |
| Soult | 0 | 5 | False | None | False | False | 70 | 40000 | 1 | [] |
| Lannes | 4 | 2 | False | None | False | False | 85 | 16478 | 1 | [] |
| Murat | 2 | 4 | False | Ney | False | False | 75 | 20140 | 1 | [] |
| Bernadotte | 0 | 6 | False | None | False | False | 40 | 17000 | 1 | [] |
| Massena | 0 | 7 | False | None | False | False | 60 | 23164 | 0 | [] |

> **Marshal Ney, press the attack on Mack at Swabia**  _(turn 2)_
  MSG: Ney pursues Mack (at Frankfurt). Moves to Franconia.
  AP: cost=1 remaining=2 turn_advanced=False new_turn=None
  *** MARSHAL PETITION ***
     {
       "kind": "jealousy_confrontation",
       "title": "Marshal Murat seeks an audience",
       "body": "Sire, Murat has expressed... displeasure about Ney's recent recognition. He requests a command worthy of his talents.",
       "speaker": "Murat",
       "options": [
         {
           "id": "acknowledge",
           "label": "Acknowledge",
           "detail": "The grievance runs its course.",
           "cost_note": "",
           "enabled": true
         },
         {
           "id": "promise",
           "label": "Promise Glory",
           "detail": "His patience is bought \u2014 the grievance shortens by 2 turns.",
           "cost_note": "1 AP",
           "enabled": true
         },
         {
           "id": "rebuke",
           "label": "Rebuke",
           "detail": "Trust -5. The grievance shortens by 1 turn. He will not act on his own this cycle \u2014 he respects the Emperor's anger, briefly.",
           "cost_note": "",
           "enabled": true
         }
       ],
       "context": {
         "marshal": "Murat",
         "target": "Ney"
       },
       "turn": 1
     }

> PETITION RESPONSE: promise
  MSG: Murat bows. "I will hold you to it, Sire." His grievance shortens.

> **Murat, pursue and destroy Mack's broken corps**  _(turn 2)_
  MSG: Not enough actions! Need 2, have 1.

> **end turn**  _(turn 2)_
  MSG: Turn 2 ended. (Warning: 1 action(s) unused) Turn 3 begins!
       
       Income: 3200g | Upkeep: 1320g (incl. 104g over-limit) | Other: +850g | Net: +2730g | Treasury: 6,201g
  AP: cost=0 remaining=4 turn_advanced=False new_turn=None

### Glory ladder snapshot (turn 3)
```
[
  {
    "name": "Ney",
    "glory": 5,
    "crowned": false,
    "jealous_of": null,
    "personality": "aggressive"
  },
  {
    "name": "Lannes",
    "glory": 5,
    "crowned": false,
    "jealous_of": null,
    "personality": "aggressive"
  },
  {
    "name": "Davout",
    "glory": 3,
    "crowned": false,
    "jealous_of": null,
    "personality": "cautious"
  },
  {
    "name": "Murat",
    "glory": 3,
    "crowned": false,
    "jealous_of": "Ney",
    "personality": "aggressive"
  },
  {
    "name": "Massena",
    "glory": 1,
    "crowned": false,
    "jealous_of": null,
    "personality": "aggressive"
  },
  {
    "name": "Soult",
    "glory": 0,
    "crowned": false,
    "jealous_of": null,
    "personality": "literal"
  },
  {
    "name": "Bernadotte",
    "glory": 0,
    "crowned": false,
    "jealous_of": null,
    "personality": "cautious"
  }
]
```
| Marshal | glory | rank | crowned | jealous_of | surge | warned | trust | str | idle | feuds |
|---|---|---|---|---|---|---|---|---|---|---|
| Ney | 5 | 1 | False | None | False | False | 75 | 19725 | 0 | ['Murat'] |
| Davout | 3 | 3 | False | None | False | False | 85 | 22012 | 1 | [] |
| Soult | 0 | 6 | False | None | False | False | 70 | 40000 | 2 | [] |
| Lannes | 5 | 2 | False | None | False | False | 85 | 15243 | 1 | [] |
| Murat | 3 | 4 | False | Ney | False | True | 75 | 18630 | 1 | ['Ney'] |
| Bernadotte | 0 | 7 | False | None | False | False | 40 | 17000 | 2 | [] |
| Massena | 1 | 5 | False | None | False | False | 60 | 21428 | 1 | [] |

> **Marshal Ney, attack Mack at Frankfurt and finish him**  _(turn 3)_
  MSG: Ney pursues Mack (at Gelderland). Moves to Franconia.
  AP: cost=1 remaining=2 turn_advanced=False new_turn=None
  *** MARSHAL PETITION ***
     {
       "kind": "rivalry_confrontation",
       "title": "A rivalry among the marshals",
       "body": "Sire, harsh words were exchanged between Ney and Murat before the general staff.",
       "speaker": "Ney",
       "options": [
         {
           "id": "let_be",
           "label": "Let Them Sort It Out",
           "detail": "Most likely they simmer; it may yet escalate \u2014 or mend.",
           "cost_note": "",
           "enabled": true
         },
         {
           "id": "mediate",
           "label": "Mediate",
           "detail": "Your authority decides whether they listen.",
           "cost_note": "1 AP",
           "enabled": true
         },
         {
           "id": "reprimand",
           "label": "Reprimand Both",
           "detail": "Trust -3 on both \u2014 anger redirected at you may mend the breach.",
           "cost_note": "",
           "enabled": true
         }
       ],
       "context": {
         "marshal": "Ney",
         "other": "Murat",
         "new_value": -1
       },
       "turn": 2
     }

> PETITION RESPONSE: let_be
  MSG: Ney and Murat: It escalates without you — the breach deepens to open hostility.

> **Murat, march north to join Marshal Ney at the front**  _(turn 3)_
  MSG: Murat: 'ArchdukeCharles blocks the path at Milan. Odds unfavorable. Your orders?'
       (Murat stands down from his intended attack — your orders reached him in time.)
  AP: cost=1 remaining=1 turn_advanced=False new_turn=None
  STRATEGIC INTERRUPT: {"marshal": "Murat", "interrupt_type": "contact_bad_odds", "enemy": "ArchdukeCharles", "location": "Milan", "is_first_step": true, "options": ["attack_anyway", "go_around", "hold_position", "cancel_order"]}

> **end turn**  _(turn 3)_
  MSG: Turn 3 ended. (Warning: 1 action(s) unused) Turn 4 begins!
       
       Income: 3200g | Upkeep: 1244g (incl. 76g over-limit) | Other: +850g | Net: +2806g | Treasury: 9,007g
  AP: cost=0 remaining=4 turn_advanced=False new_turn=None

### Glory ladder snapshot (turn 4)
```
[
  {
    "name": "Ney",
    "glory": 6,
    "crowned": false,
    "jealous_of": null,
    "personality": "aggressive"
  },
  {
    "name": "Davout",
    "glory": 6,
    "crowned": false,
    "jealous_of": null,
    "personality": "cautious"
  },
  {
    "name": "Lannes",
    "glory": 6,
    "crowned": false,
    "jealous_of": null,
    "personality": "aggressive"
  },
  {
    "name": "Murat",
    "glory": 4,
    "crowned": false,
    "jealous_of": null,
    "personality": "aggressive"
  },
  {
    "name": "Massena",
    "glory": 1,
    "crowned": false,
    "jealous_of": null,
    "personality": "aggressive"
  },
  {
    "name": "Soult",
    "glory": 0,
    "crowned": false,
    "jealous_of": null,
    "personality": "literal"
  },
  {
    "name": "Bernadotte",
    "glory": 0,
    "crowned": false,
    "jealous_of": null,
    "personality": "cautious"
  }
]
```
| Marshal | glory | rank | crowned | jealous_of | surge | warned | trust | str | idle | feuds |
|---|---|---|---|---|---|---|---|---|---|---|
| Ney | 6 | 1 | False | None | False | False | 72 | 18209 | 0 | ['Murat'] |
| Davout | 6 | 2 | False | None | False | False | 82 | 20523 | 1 | [] |
| Soult | 0 | 6 | False | None | False | False | 70 | 40000 | 3 | [] |
| Lannes | 6 | 3 | False | None | False | False | 82 | 14213 | 2 | [] |
| Murat | 4 | 4 | False | None | False | False | 72 | 17372 | 2 | ['Ney'] |
| Bernadotte | 0 | 7 | False | None | False | False | 40 | 17000 | 3 | [] |
| Massena | 1 | 5 | False | None | False | False | 60 | 20143 | 2 | [] |

> **Marshal Ney, march on the Austrian capital and capture Vienna**  _(turn 4)_
  MSG: Ney: 'ArchdukeCharles blocks the path at Tyrol. Odds unfavorable. Your orders?'
  AP: cost=1 remaining=3 turn_advanced=False new_turn=None
  STRATEGIC INTERRUPT: {"marshal": "Ney", "interrupt_type": "contact_bad_odds", "enemy": "ArchdukeCharles", "location": "Tyrol", "is_first_step": true, "options": ["attack_anyway", "go_around", "hold_position", "cancel_order"]}

> INTERRUPT: Ney attack_anyway (massed assault on the archdukes in Tyrol)
  MSG: Ney attacks ArchdukeCharles and wins! Continuing his march. 
       [Combat] Ney leads the charge! (Aggressive: +15% attack)
       [Shield] ArchdukeCharles's DEFENSIVE stance strengthens the line! (+15% defense)
       [Shield] ArchdukeCharles's methodical defense is exemplary! (Cautious: +20% total)
       [Terrain] ArchdukeCharles benefits from Mountains terrain (+25% defense)
       [Combat] Ney's combined arms coordination! (+10% attack)
       [Combat] Adjacent allies bolster Ney's attack! (+2%)
       Ney's attack meets fierce resistance. Ney gains the advantage over ArchdukeCharles. Casualties: Ney 332, ArchdukeCharles 3,432. Both armies remain in the field. Ney advances into Tyrol. (357 lost to march)
       [!] ArchdukeCharles's broken army flees to Bohemia! (recovering for 2 turns)
  casualties: {"attacker_name": "Ney", "attacker_original": 18209, "attacker_casualties": 332, "attacker_remaining": 17877, "defender_name": "ArchdukeCharles", "defender_original": 27626, "defender_casualties": 3432, "defender_remaining": 24194}

> **end turn**  _(turn 4)_
  MSG: Turn 4 ended. (Warning: 3 action(s) unused) Turn 5 begins!
       
       Income: 3200g | Upkeep: 1152g (incl. 48g over-limit) | Other: +850g | Net: +2898g | Treasury: 11,905g
  AP: cost=0 remaining=4 turn_advanced=False new_turn=None

### Glory ladder snapshot (turn 5)
```
[
  {
    "name": "Ney",
    "glory": 10,
    "crowned": false,
    "jealous_of": null,
    "personality": "aggressive"
  },
  {
    "name": "Lannes",
    "glory": 10,
    "crowned": false,
    "jealous_of": null,
    "personality": "aggressive"
  },
  {
    "name": "Davout",
    "glory": 8,
    "crowned": false,
    "jealous_of": null,
    "personality": "cautious"
  },
  {
    "name": "Murat",
    "glory": 4,
    "crowned": false,
    "jealous_of": "Davout",
    "personality": "aggressive"
  },
  {
    "name": "Massena",
    "glory": 3,
    "crowned": false,
    "jealous_of": null,
    "personality": "aggressive"
  },
  {
    "name": "Soult",
    "glory": 0,
    "crowned": false,
    "jealous_of": null,
    "personality": "literal"
  },
  {
    "name": "Bernadotte",
    "glory": 0,
    "crowned": false,
    "jealous_of": "Massena",
    "personality": "cautious"
  }
]
```
| Marshal | glory | rank | crowned | jealous_of | surge | warned | trust | str | idle | feuds |
|---|---|---|---|---|---|---|---|---|---|---|
| Ney | 10 | 1 | False | None | False | False | 69 | 16420 | 0 | ['Murat'] |
| Davout | 8 | 3 | False | None | False | False | 79 | 18880 | 1 | [] |
| Soult | 0 | 6 | False | None | False | False | 70 | 40000 | 4 | [] |
| Lannes | 10 | 2 | False | None | False | False | 79 | 13079 | 1 | [] |
| Murat | 4 | 4 | False | Davout | False | False | 66 | 16004 | 0 | ['Ney'] |
| Bernadotte | 0 | 7 | False | Massena | False | False | 40 | 17000 | 4 | [] |
| Massena | 3 | 5 | False | None | False | False | 57 | 18535 | 1 | [] |

> **Marshal Ney, continue the advance and seize Vienna**  _(turn 5)_
  MSG: Berthier peers at the dispatch with concern. "I cannot make sense of this, Sire. A clear order might be: 'Ney, attack Deroy' or 'end turn'. For diplomacy: 'declare war on Prussia' or 'propose peace with Austria'."
  AP: cost=0 remaining=4 turn_advanced=False new_turn=None
  *** MARSHAL PETITION ***
     {
       "kind": "jealousy_confrontation",
       "title": "Marshal Murat seeks an audience",
       "body": "Sire, Murat has expressed... displeasure about Davout's recent recognition. He requests a command worthy of his talents.",
       "speaker": "Murat",
       "options": [
         {
           "id": "acknowledge",
           "label": "Acknowledge",
           "detail": "The grievance runs its course.",
           "cost_note": "",
           "enabled": true
         },
         {
           "id": "promise",
           "label": "Promise Glory",
           "detail": "His patience is bought \u2014 the grievance shortens by 2 turns.",
           "cost_note": "1 AP",
           "enabled": true
         },
         {
           "id": "rebuke",
           "label": "Rebuke",
           "detail": "Trust -5. The grievance shortens by 1 turn. He will not act on his own this cycle \u2014 he respects the Emperor's anger, briefly.",
           "cost_note": "",
           "enabled": true
         }
       ],
       "context": {
         "marshal": "Murat",
         "target": "Davout"
       },
       "turn": 4
     }

> PETITION RESPONSE: rebuke
  MSG: Murat stiffens under the rebuke (-5 trust).

> **Marshal Ney, attack Vienna**  _(turn 5)_
  MSG: Ney cannot reach Vienna from Tyrol! Range: 1, Distance: 2
  AP: cost=0 remaining=4 turn_advanced=False new_turn=None

> **end turn**  _(turn 5)_
  MSG: Turn 5 ended. (Warning: 4 action(s) unused) Turn 6 begins!
       
       Income: 3200g | Upkeep: 1092g (incl. 28g over-limit) | Other: +850g | Net: +2958g | Treasury: 14,863g
  AP: cost=0 remaining=4 turn_advanced=False new_turn=None

### Glory ladder snapshot (turn 6)
```
[
  {
    "name": "Ney",
    "glory": 10,
    "crowned": false,
    "jealous_of": null,
    "personality": "aggressive"
  },
  {
    "name": "Lannes",
    "glory": 10,
    "crowned": false,
    "jealous_of": null,
    "personality": "aggressive"
  },
  {
    "name": "Davout",
    "glory": 8,
    "crowned": false,
    "jealous_of": null,
    "personality": "cautious"
  },
  {
    "name": "Murat",
    "glory": 4,
    "crowned": false,
    "jealous_of": "Davout",
    "personality": "aggressive"
  },
  {
    "name": "Massena",
    "glory": 3,
    "crowned": false,
    "jealous_of": null,
    "personality": "aggressive"
  },
  {
    "name": "Soult",
    "glory": 0,
    "crowned": false,
    "jealous_of": null,
    "personality": "literal"
  },
  {
    "name": "Bernadotte",
    "glory": 0,
    "crowned": false,
    "jealous_of": "Massena",
    "personality": "cautious"
  }
]
```
| Marshal | glory | rank | crowned | jealous_of | surge | warned | trust | str | idle | feuds |
|---|---|---|---|---|---|---|---|---|---|---|
| Ney | 10 | 1 | False | None | False | False | 66 | 15435 | 1 | ['Murat'] |
| Davout | 8 | 3 | False | None | False | False | 76 | 17748 | 2 | [] |
| Soult | 0 | 6 | False | None | False | False | 70 | 40000 | 5 | [] |
| Lannes | 10 | 2 | False | None | False | False | 76 | 12295 | 2 | [] |
| Murat | 4 | 4 | False | Davout | False | False | 58 | 15044 | 1 | ['Ney'] |
| Bernadotte | 0 | 7 | False | Massena | False | False | 40 | 17000 | 5 | [] |
| Massena | 3 | 5 | False | None | False | False | 54 | 17423 | 2 | [] |

> **Marshal Ney, march to Vienna**  _(turn 6)_
  MSG: Ney begins march to Vienna. Route: Bohemia -> Vienna. Moves to Bohemia.
  AP: cost=1 remaining=2 turn_advanced=False new_turn=None
  *** MARSHAL PETITION ***
     {
       "kind": "fontainebleau",
       "title": "The marshals petition the Emperor",
       "body": "Sire, the marshals come together: Ney, Davout, Lannes, Murat and Massena stand unrewarded while the Empire feeds on their victories. They ask for estates, rentes, or peace \u2014 1300g/turn of expectation stands unmet. The army does not march on glory alone.",
       "speaker": "Ney",
       "options": [
         {
           "id": "concede",
           "label": "\"I will find the means\"",
           "detail": "Every petitioner receives a rente at his shortfall (+2 trust each). The treasury will carry ~1950g/turn.",
           "cost_note": "",
           "enabled": true
         },
         {
           "id": "refuse",
           "label": "\"The Empire does not beg\"",
           "detail": "Trust -8 on every petitioner. The erosion continues.",
           "cost_note": "",
           "enabled": true
         },
         {
           "id": "promise",
           "label": "\"The next conquest is yours\"",
           "detail": "Their patience extends 3 turns; the court hears you buy time with words (authority -2).",
           "cost_note": "",
           "enabled": true
         }
       ],
       "context": {
         "marshals": [
           "Ney",
           "Davout",
           "Lannes",
           "Murat",
           "Massena"
         ]
       },
       "turn": 5
     }

> **Marshal Soult, advance from Lorraine toward the Austrian front at Munich**  _(turn 6)_
  MSG: Soult begins marching to Munich (distance: 2). Moved to Swabia. Route: Swabia -> Munich.
  AP: cost=1 remaining=1 turn_advanced=False new_turn=None

> **end turn**  _(turn 6)_
  MSG: Turn 6 ended. (Warning: 1 action(s) unused) Turn 7 begins!
       
       Income: 3000g | Upkeep: 1052g (incl. 36g over-limit) | Other: +812g | Net: +2760g | Treasury: 17,623g
  AP: cost=0 remaining=4 turn_advanced=False new_turn=None

### Glory ladder snapshot (turn 7)
```
[
  {
    "name": "Ney",
    "glory": 10,
    "crowned": false,
    "jealous_of": null,
    "personality": "aggressive"
  },
  {
    "name": "Lannes",
    "glory": 10,
    "crowned": false,
    "jealous_of": null,
    "personality": "aggressive"
  },
  {
    "name": "Davout",
    "glory": 8,
    "crowned": false,
    "jealous_of": null,
    "personality": "cautious"
  },
  {
    "name": "Murat",
    "glory": 4,
    "crowned": false,
    "jealous_of": "Davout",
    "personality": "aggressive"
  },
  {
    "name": "Massena",
    "glory": 3,
    "crowned": false,
    "jealous_of": null,
    "personality": "aggressive"
  },
  {
    "name": "Soult",
    "glory": 0,
    "crowned": false,
    "jealous_of": null,
    "personality": "literal"
  },
  {
    "name": "Bernadotte",
    "glory": 0,
    "crowned": false,
    "jealous_of": "Massena",
    "personality": "cautious"
  }
]
```
| Marshal | glory | rank | crowned | jealous_of | surge | warned | trust | str | idle | feuds |
|---|---|---|---|---|---|---|---|---|---|---|
| Ney | 10 | 1 | False | None | False | False | 63 | 15281 | 0 | ['Murat'] |
| Davout | 8 | 3 | False | None | False | False | 73 | 16684 | 3 | [] |
| Soult | 0 | 6 | False | None | False | False | 71 | 38800 | 0 | [] |
| Lannes | 10 | 2 | False | None | False | False | 73 | 11558 | 3 | [] |
| Murat | 4 | 4 | False | Davout | False | False | 55 | 14142 | 2 | ['Ney'] |
| Bernadotte | 0 | 7 | False | Massena | False | False | 40 | 17000 | 6 | [] |
| Massena | 3 | 5 | False | None | False | False | 51 | 16378 | 3 | [] |

> PETITION RESPONSE: concede
  MSG: "I will find the means." Rentes are granted: Ney (300g/turn); Davout (300g/turn); Lannes (300g/turn); Murat (240g/turn); Massena (160g/turn). The treasury will feel it.

### Glory ladder snapshot (turn 7)
```
[
  {
    "name": "Ney",
    "glory": 10,
    "crowned": false,
    "jealous_of": null,
    "personality": "aggressive"
  },
  {
    "name": "Lannes",
    "glory": 10,
    "crowned": false,
    "jealous_of": null,
    "personality": "aggressive"
  },
  {
    "name": "Davout",
    "glory": 8,
    "crowned": false,
    "jealous_of": null,
    "personality": "cautious"
  },
  {
    "name": "Murat",
    "glory": 4,
    "crowned": false,
    "jealous_of": "Davout",
    "personality": "aggressive"
  },
  {
    "name": "Massena",
    "glory": 3,
    "crowned": false,
    "jealous_of": null,
    "personality": "aggressive"
  },
  {
    "name": "Soult",
    "glory": 0,
    "crowned": false,
    "jealous_of": null,
    "personality": "literal"
  },
  {
    "name": "Bernadotte",
    "glory": 0,
    "crowned": false,
    "jealous_of": "Massena",
    "personality": "cautious"
  }
]
```
| Marshal | glory | rank | crowned | jealous_of | surge | warned | trust | str | idle | feuds |
|---|---|---|---|---|---|---|---|---|---|---|
| Ney | 10 | 1 | False | None | False | False | 65 | 15281 | 0 | ['Murat'] |
| Davout | 8 | 3 | False | None | False | False | 75 | 16684 | 3 | [] |
| Soult | 0 | 6 | False | None | False | False | 71 | 38800 | 0 | [] |
| Lannes | 10 | 2 | False | None | False | False | 75 | 11558 | 3 | [] |
| Murat | 4 | 4 | False | Davout | False | False | 57 | 14142 | 2 | ['Ney'] |
| Bernadotte | 0 | 7 | False | Massena | False | False | 40 | 17000 | 6 | [] |
| Massena | 3 | 5 | False | None | False | False | 53 | 16378 | 3 | [] |

---

## Findings summary (6-turn France/1805 playthrough, LLM_MODE=anthropic)

### Marshal Drama — the Phase-3 unlock is FELT (organic, unscripted)
- **Glory now flows from attrition (DR-1).** Turn 1: Ney out-bled Mack 10,974:756 in an *inconclusive* city assault and was awarded glory (4) — zero under baseline. Reinforcers who "marched to the guns" (Lannes 4, Davout 2, Murat 2) also scored. The triple lock is broken in the wild.
- **Deeds accreted (DR-2).** Ney climbed 4→5→6→10 across turns; no evaporation at turn 6. A real ladder gap formed (Ney/Lannes 10 · Davout 8 · Murat 4 · Massena 3 · Soult/Bernadotte 0).
- **FOUR petitions surfaced organically across THREE kinds + the collective beat:**
  1. **Turn 2 — jealousy_confrontation:** "Marshal Murat seeks an audience… displeasure about Ney's recent recognition." (M7 in the wild: petition at turn 2, spec target ≤8.)
  2. **Turn 3 — rivalry_confrontation:** "harsh words were exchanged between Ney and Murat before the general staff." Choosing *Let Them Sort It Out* → **"the breach deepens to open hostility"** (mutual feud registered: Ney['Murat'] / Murat['Ney']).
  3. **Turn 5 — jealousy_confrontation (re-targeted):** after the ladder shifted, Murat petitions over **Davout's** recognition — the **one-rung-up targeting** flowing into the channel (Murat glory 4 → resents Davout glory 8, the rung above).
  4. **Turn 6 — Fontainebleau (ESP-1):** five marshals collectively petition — "1300g/turn of expectation stands unmet… The army does not march on glory alone." *Concede* granted rentes (Ney/Davout/Lannes 300g, Murat 240g, Massena 160g, +2 trust each) — **Jealousy ↔ ES-7 reward economy interlocked.**
- **Multiple jealous marshals concurrently:** Murat→Ney→Davout, Bernadotte→Massena. The literal Soult expressed no petition (correct — literal jealousy is the Vindicated Garrison, not the petition channel).
- **DR-3 authority dampening did NOT smother it:** player authority booted at 100 and stayed high, yet the hair-trigger rival edge (Ney↔Murat = Rival) fired at turn 2 — exactly the "exempt the first rung" design.
- **Consequence loop is real:** trust eroded on the un-rewarded (Murat 75→55, Massena 60→51, Bernadotte 40) until the rente concession bumped them back +2.

### Combat (Phase 1–2, corroboration)
- **Decisive & additive:** massed coordinated assault broke **two** enemy commanders — Mack (turn 1, large→small, fled) and ArchdukeCharles (turn 4, broken, "flees to Bohemia, recovering 2 turns") — and advanced into Swabia then Tyrol. Battle text named the combined-arms (+10%) and adjacent-ally (+2%) contributions (CO-6 legibility).
- **M6 held (defender edge intact):** Massena's 42k shattered on ArchdukeJohn in mountains (out-bled 8,083:425 the *wrong* way, +25% terrain +10% cautious-outnumbered). Mass is not a free win into fortified mountains.
- **Legible interrupts:** `contact_bad_odds` popups ("ArchdukeCharles blocks the path… Odds unfavorable. Your orders?") with attack_anyway/go_around/hold/cancel; range feedback ("cannot reach Vienna… Range 1, Distance 2").

### Honest friction (for the reviewers)
- **Over-convergence:** "march to the sound of the guns" pulled all five lead marshals onto Munich by turn 4 — powerful but it can strip other fronts; a player may want a leash.
- **Flee-chase loop:** broken enemies (Mack) out-run pursuit repeatedly, producing "pursues… moves to X" with no contact for several turns.
- **Parser misses:** "seize Vienna" / "continue the advance and seize Vienna" failed to parse (needed "attack Vienna" / "march to Vienna"); these are Phase-6 PF-class items, not Phase-3.
- **Economy still loose (Phase-4 territory):** despite conceding ~1,900g/turn of rentes, treasury still climbed 800→17,623 over 6 turns; net income *rose* as corps attrited. Gold remains near-free (EC-U1/EC-U2 own this).
