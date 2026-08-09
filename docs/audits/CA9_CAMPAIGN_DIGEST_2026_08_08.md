====================================================================================================
> Soult, support Ney
====================================================================================================
Soult moves to support Ney (at Rhineland). Moves to Rhineland. Soult will march to Ney's guns — he
  holds your written order. "Soult, support Ney." No more and no less. (1 AP — Soult executes
  precise orders with fewer couriers.)
   [cost=1  turn_advanced=False]

====================================================================================================
> Bernadotte, support Ney
====================================================================================================
Bernadotte moves to support Ney (at Rhineland). Bernadotte will march to Ney's guns — he holds your
  written order. Bernadotte: "As you order. I move when the need is real, not before."
   [cost=1  turn_advanced=False]

====================================================================================================
> Ney, attack Mack at Swabia
====================================================================================================
MUSTER — Ney (24,000; 107,722 with the muster committed) vs Mack (large force) at Swabia — the
  balance of force looks favorable.
  WILL JOIN — Davout: is willing to march if the roads allow
  WILL JOIN — Soult: marches under your written support order
  WILL JOIN — Lannes: marches to the sound of the guns — the Roland of the Army
  WILL JOIN — Murat: will march to the sound of the guns
  WILL JOIN — Bernadotte: marches under your written support order
  (Standing orders decide who marches: 'Soult, support Ney' authorizes even a literal marshal to
  move to his guns.)


[Combat] Ney leads the charge! (Aggressive: +15% attack)
Ney delivers an effective strike. Ney gains the advantage over Mack. Casualties: Ney's army 1,940,
  Mack 16,109. Both armies remain in the field. Ney advances into Swabia. (411 lost to march) Swabia
  remains Bavaria's soil — we drove the enemy from our ally's province; it is not ours to take.
[Materiel] Guns, horses and stores lost with the fallen: France -97g, Austria -805g.
[!] Mack's broken army flees to Nassau! (897 lost to march) (recovering for 3 turns)
   [cost=1  turn_advanced=False]
   <event battle> {"battle_name": "The Great Battle of Swabia", "attacker": {"name": "Ney", "casualties": 1940, "remaining": 23684, "morale": 95, "forced_retreat": false}, "defender": {"name": "Mack", "casualties": 16109, "remaining": 35891, "morale": 25, "forced_retreat": true}, "attacker_nation": "France", "defender_nation": "Austria", "outcome": "attacker_tactical_victory", "victor": "Ney", "enemy_destroyed": false, "region_conquered": false, "region_name": null, "flanking_bonus": 0, "flanking_origins": ["Rhineland"], "vindication": null, "attacker_forced_retreat": false, "defender_forced_retreat": true, "ca
-- REINFORCEMENTS --
   [
    "Davout's forces arrived to reinforce Ney!",
    "Soult's forces arrived to reinforce Ney!",
    "Lannes's forces arrived to reinforce Ney!",
    "Murat's forces arrived to reinforce Ney!",
    "Bernadotte's forces arrived to reinforce Ney!",
    "Massed effective strength: 24,000 (lead) + 83,722 committed (Davout, Soult, Lannes, Murat,
     Bernadotte) = 107,722.",
    "His supporting allies lost 1,624 men combined."
   ]
-- BERTHIER'S AFTER-ACTION REPORT --
   {
    "modifier_breakdown": {
     "attacker": [
      {
       "label": "Personality (aggressive)",
       "value": 15,
       "type": "bonus"
      }
     ],
     "defender": []
    },
    "casualty_summary": {
     "attacker_name": "Ney",
     "attacker_original": 24000,
     "attacker_casualties": 316,
     "attacker_remaining": 23684,
     "defender_name": "Mack",
     "defender_original": 52000,
     "defender_casualties": 16109,
     "defender_remaining": 35891
    },
    "observation": "Davout, Soult, Lannes, Murat and Bernadotte arrived to reinforce Ney! The timely
     arrival swung the battle in our favor, Sire.",
    "enemy_voice": "Mack: \"I withdraw in perfect conformity with a plan I have just completed.\"",
    "marshal_voice": "Ney: \"The bravest of the brave was first through their line \u2014 ask the
     line.\"",
    "expectation_note": "Victory raises Marshal Ney's expectation of reward \u2014 he now looks for
     40g/turn (holds 0g)."
   }
-- POPUP/DIALOGUE [battle_diorama] --
   {
    "battle_name": "The Great Battle of Swabia",
    "region": "Swabia",
    "turn": 1,
    "outcome": "attacker_tactical_victory",
    "victor": "Ney",
    "attacker_nation": "France",
    "defender_nation": "Austria",
    "player_side": "attacker",
    "register": "triumph",
    "significant": true,
    "dramatic": true,
    "great_battle": true,
    "region_conquered": false,
    "attacker": {
     "contingents": [
      {
       "name": "Ney",
       "nation": "France",
       "arm": "infantry",
       "committed": 24000,
       "casualties": 316,
       "remaining": 23684,
       "status": "engaged",
       "lead": true,
       "crowned": false
      },
      {
       "name": "Soult",
       "nation": "France",
       "arm": "infantry",
       "committed": 40000,
       "casualties": 530,
       "remaining": 39470,
       "status": "reinforced",
       "lead": false,
       "crowned": false
      },
      {
       "name": "Davout",
       "nation": "France",
       "arm": "infantry",
       "committed": 26000,
       "casualties": 343,
       "remaining": 25657,
       "status": "reinforced",
       "lead": false,
       "crowned": false
      },
      {
       "name": "Murat",
       "nation": "France",
       "arm": "cavalry",
       "committed": 22000,
       "casualties": 290,
       "remaining": 21710,
       "status": "reinforced",
       "lead": false,
       "crowned": false
      }
     ],
     "reserve_count": 2,
     "casualties_total": 1940,
     "committed_total": 147000,
     "nation": "France"
    },
    "defender": {
     "contingents": [
      {
       "name": "Mack",
       "nation": "Austria",
       "arm": "infantry",
       "committed": 52000,
       "casualties": 16109,
       "remaining": 35891,
       "status": "routed",
       "lead": true,
       "crowned": false
      }
     ],
     "reserve_count": 0,
     "casualties_total": 16109,
     "committed_total": 52000,
     "nation": "Austria"
    },
    "observation": "Davout, Soult, Lannes, Murat and Bernadotte arrived to reinforce Ney! The timely
     arrival swung the battle in our favor, Sire.",
    "enemy_voice": "Mack: \"I withdraw in perfect conformity with a plan I have just completed.\""
   }

====================================================================================================
> Massena, scout Tyrol
====================================================================================================
Not enough actions! Need 1, have 0.

====================================================================================================
> end turn
====================================================================================================
Turn 1 ended. Turn 2 begins!

Income: 3400g | Admiralty: -90g | Blockade: -175g | Upkeep: 1976g (incl. 152g over-limit, 504g
  Grande Armée) | Other: +722g | Net: +1881g | Treasury: 2,584g
   [cost=0  turn_advanced=False]
   <event supply_attrition> {"marshal": "Ney", "nation": "France", "region": "Swabia", "losses": 1396, "message": "Supply shortage at Swabia: Ney loses 1,396 troops"}
   <event supply_attrition> {"marshal": "Davout", "nation": "France", "region": "Swabia", "losses": 1539, "message": "Supply shortage at Swabia: Davout loses 1,539 troops"}
   <event supply_attrition> {"marshal": "Soult", "nation": "France", "region": "Swabia", "losses": 2368, "message": "Supply shortage at Swabia: Soult loses 2,368 troops"}
   <event supply_attrition> {"marshal": "Lannes", "nation": "France", "region": "Swabia", "losses": 1065, "message": "Supply shortage at Swabia: Lannes loses 1,065 troops"}
   <event supply_attrition> {"marshal": "Murat", "nation": "France", "region": "Swabia", "losses": 1302, "message": "Supply shortage at Swabia: Murat loses 1,302 troops"}
   <event supply_attrition> {"marshal": "Bernadotte", "nation": "France", "region": "Swabia", "losses": 1006, "message": "Supply shortage at Swabia: Bernadotte loses 1,006 troops"}
   <event supply_attrition> {"marshal": "Mack", "nation": "Austria", "region": "Nassau", "losses": 699, "message": "Supply shortage at Nassau: Mack loses 699 troops"}
   <event supply_attrition> {"marshal": "Massena", "nation": "France", "region": "Milan", "losses": 1230, "message": "Supply shortage at Milan: Massena loses 1,230 troops"}
   <event supply_attrition> {"marshal": "ArchdukeCharles", "nation": "Austria", "region": "Milan", "losses": 1798, "message": "Supply shortage at Milan: ArchdukeCharles loses 1,798 troops"}
   <event supply_attrition> {"marshal": "ArchdukeJohn", "nation": "Austria", "region": "Milan", "losses": 686, "message": "Supply shortage at Milan: ArchdukeJohn loses 686 troops"}
   <event vassal_loyalty> {"vassal": "Switzerland", "lord": "France", "nation": "France", "old_loyalty": 100, "new_loyalty": 97, "delta": -3, "reason": "satellite drift, the lord's defeats", "recovery_hint": "Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.", "message": "Switzerland loyalty 97 (-3): satellite drift, the lord's defeats \u2014 Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them."}
   <event ai_ai_treaty> {"nation_a": "Sweden", "nation_b": "Russia", "treaty_type": "Open Borders Agreement", "message": "Sweden and Russia have signed an Open Borders Agreement."}
   <event ai_ai_treaty> {"nation_a": "Naples", "nation_b": "Russia", "treaty_type": "Open Borders Agreement", "message": "Naples and Russia have signed an Open Borders Agreement."}
   <event blockade_begins> {"turn": 2, "nation": "France", "blockader": "Britain"}
   <event jealousy_fired> {"message": "Berthier reports that Murat appears envious of Ney's laurels \u2014 he has grown restless for glory.", "nation": "France", "marshal": "Murat", "target": "Ney"}
   <event jealousy_escalation> {"message": "Sire, the rivalry between Murat and Ney has become a matter of concern among the general staff. Their cooperation cannot be relied upon.", "nation": "France", "marshal": "Murat", "target": "Ney"}
   <event jealousy_fired> {"message": "Berthier reports that Bernadotte appears envious of Ney's laurels \u2014 he has grown quiet in the way the staff have learned to read.", "nation": "France", "marshal": "Bernadotte", "target": "Ney"}
   <event jealousy_escalation> {"message": "Sire, the rivalry between Bernadotte and Ney has become a matter of concern among the general staff. Their cooperation cannot be relied upon.", "nation": "France", "marshal": "Bernadotte", "target": "Ney"}
   <event jealousy_restlessness> {"message": "Berthier notes that Davout has grown restless \u2014 he has not seen laurels while Ney wins them. I recommend giving him meaningful orders soon.", "nation": "France", "marshal": "Davout"}
   <event jealousy_autonomous_warning> {"message": "Murat is eyeing Mack's position at Nassau. I cannot guarantee he will wait for orders, Sire \u2014 any command would restrain him.", "nation": "France", "marshal": "Murat"}
   <event glory_crowned> {"message": "Berthier notes that Ney's recent victories have made him the most celebrated commander in the army. (+1 shock, +1 defense, +1 administration while he holds the laurels)", "nation": "France", "marshal": "Ney"}

####################################################################################################
# THE ENEMY PHASE
####################################################################################################
-- Austria --
  - ArchdukeCharles moves to Tyrol
      [move] {"type": "move", "marshal": "ArchdukeCharles", "from": "Carniola", "to": "Tyrol"}
  - ArchdukeJohn changes stance to defensive
      [stance_change] {"type": "stance_change", "marshal": "ArchdukeJohn", "from_stance": "neutral", "to_stance": "defensive", "action_cost": 1}
  - ArchdukeCharles attacks Massena
      [battle] The Great Battle of Milan  -> attacker_tactical_victory  victor=ArchdukeCharles
        ATK ArchdukeCharles  lost   3,388  left  51,527  morale  95
        DEF Massena          lost   7,808  left  34,192  morale  76
        attacker order of battle: ArchdukeCharles 54,000(engaged); ArchdukeJohn 20,000(reinforced)
    [action_count] 3
[summary]
   ArchdukeCharles: move → Tyrol
   ArchdukeJohn: stance_change → defensive
   ArchdukeCharles: attack → Massena

####################################################################################################
# THE MORNING DISPATCH
####################################################################################################
{
 "turn": 2,
 "situation": {
  "player_regions": 28,
  "enemy_regions": 98,
  "treasury": 2584,
  "treasury_delta": 2249,
  "trade_income": 350,
  "occupation": 0,
  "contributions": 0,
  "state_charges": 22,
  "requisitions": 0,
  "overseas": 0,
  "dotation_skim": 0,
  "unmet_marshals": [
   {
    "marshal": "Ney",
    "expectation": 40,
    "satisfaction": 0,
    "shortfall": 40,
    "eroding": false,
    "grace_turns_left": 2,
    "pension": 0
   },
   {
    "marshal": "Davout",
    "expectation": 80,
    "satisfaction": 0,
    "shortfall": 80,
    "eroding": false,
    "grace_turns_left": 2,
    "pension": 0
   },
   {
    "marshal": "Soult",
    "expectation": 80,
    "satisfaction": 0,
    "shortfall": 80,
    "eroding": false,
    "grace_turns_left": 2,
    "pension": 0
   },
   {
    "marshal": "Lannes",
    "expectation": 80,
    "satisfaction": 0,
    "shortfall": 80,
    "eroding": false,
    "grace_turns_left": 2,
    "pension": 0
   },
   {
    "marshal": "Murat",
    "expectation": 80,
    "satisfaction": 0,
    "shortfall": 80,
    "eroding": false,
    "grace_turns_left": 2,
    "pension": 0
   },
   {
    "marshal": "Bernadotte",
    "expectation": 80,
    "satisfaction": 0,
    "shortfall": 80,
    "eroding": false,
    "grace_turns_left": 2,
    "pension": 0
   }
  ],
  "rente_cost": 0,
  "expectation_rises": [
   {
    "marshal": "Ney",
    "expectation": 40,
    "previous": 0,
    "satisfaction": 0
   },
   {
    "marshal": "Davout",
    "expectation": 80,
    "previous": 0,
    "satisfaction": 0
   },
   {
    "marshal": "Soult",
    "expectation": 80,
    "previous": 0,
    "satisfaction": 0
   },
   {
    "marshal": "Lannes",
    "expectation": 80,
    "previous": 0,
    "satisfaction": 0
   },
   {
    "marshal": "Murat",
    "expectation": 80,
    "previous": 0,
    "satisfaction": 0
   },
   {
    "marshal": "Bernadotte",
    "expectation": 80,
    "previous": 0,
    "satisfaction": 0
   }
  ],
  "blockade": 175,
  "admiralty": 90,
  "upkeep_surcharge": 656,
  "force_limit": 130000,
  "over_force_limit": true,
  "bankrupt": false,
  "strength_ratio_pct": 56,
  "authority": 95,
  "authority_label": "Strong"
 },
 "marshals": [
  {
   "name": "Soult",
   "location": "Swabia",
   "strength": 37102,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 0,
   "danger": "",
   "trust": 70,
   "trust_notable": false,
   "morale": 95,
   "morale_warning": false
  },
  {
   "name": "Massena",
   "location": "Milan",
   "strength": 32962,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 1,
   "danger": "IN PERIL \u2014 an enemy force of ~66,583 shares the field (Milan).",
   "trust": 60,
   "trust_notable": false,
   "morale": 76,
   "morale_warning": false
  },
  {
   "name": "Davout",
   "location": "Swabia",
   "strength": 24118,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 1,
   "danger": "",
   "trust": 85,
   "trust_notable": false,
   "morale": 95,
   "morale_warning": false
  },
  {
   "name": "Ney",
   "location": "Swabia",
   "strength": 21877,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 0,
   "danger": "",
   "trust": 75,
   "trust_notable": false,
   "morale": 95,
   "morale_warning": false
  },
  {
   "name": "Murat",
   "location": "Swabia",
   "strength": 20408,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 1,
   "danger": "",
   "trust": 75,
   "trust_notable": false,
   "morale": 95,
   "morale_warning": false
  },
  {
   "name": "Lannes",
   "location": "Swabia",
   "strength": 16698,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 1,
   "danger": "",
   "trust": 85,
   "trust_notable": false,
   "morale": 95,
   "morale_warning": false
  },
  {
   "name": "Bernadotte",
   "location": "Swabia",
   "strength": 15770,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 1,
   "danger": "",
   "trust": 40,
   "trust_notable": true,
   "morale": 95,
   "morale_warning": false
  }
 ],
 "intelligence": [
  {
   "name": "Archduke Charles",
   "location": "Milan",
   "strength_display": "48,184",
   "visibility": "full",
   "intel_turn": 2
  },
  {
   "name": "Archduke John",
   "location": "Milan",
   "strength_display": "18,399",
   "visibility": "full",
   "intel_turn": 2
  },
  {
   "name": "Brunswick",
   "location": "Berlin",
   "strength_display": "large force",
   "visibility": "partial",
   "intel_turn": 1
  },
  {
   "name": "Mack",
   "location": "Nassau",
   "strength_display": "substantial force",
   "visibility": "partial",
   "intel_turn": 2
  }
 ],
 "turn_events": [
  {
   "message": "Supply shortage at Swabia: Ney loses 1,396 troops",
   "severity": "warning"
  },
  {
   "message": "Supply shortage at Swabia: Davout loses 1,539 troops",
   "severity": "warning"
  },
  {
   "message": "Supply shortage at Swabia: Soult loses 2,368 troops",
   "severity": "warning"
  },
  {
   "message": "Supply shortage at Swabia: Lannes loses 1,065 troops",
   "severity": "warning"
  },
  {
   "message": "Supply shortage at Swabia: Murat loses 1,302 troops",
   "severity": "warning"
  },
  {
   "message": "Supply shortage at Swabia: Bernadotte loses 1,006 troops",
   "severity": "warning"
  },
  {
   "message": "Supply shortage at Milan: Massena loses 1,230 troops",
   "severity": "warning"
  },
  {
   "message": "Switzerland loyalty 97 (-3): satellite drift, the lord's defeats \u2014 Invest in
  them, grant them autonomy, garrison their capital, or cede them a province to steady them.",
   "severity": "warning"
  },
  {
   "message": "Berthier reports that Murat appears envious of Ney's laurels \u2014 he has grown
  restless for glory.",
   "severity": "warning"
  },
  {
   "message": "Sire, the rivalry between Murat and Ney has become a matter of concern among the
  general staff. Their cooperation cannot be relied upon.",
   "severity": "warning"
  },
  {
   "message": "Berthier reports that Bernadotte appears envious of Ney's laurels \u2014 he has grown
  quiet in the way the staff have learned to read.",
   "severity": "warning"
  },
  {
   "message": "Sire, the rivalry between Bernadotte and Ney has become a matter of concern among the
  general staff. Their cooperation cannot be relied upon.",
   "severity": "warning"
  },
  {
   "message": "Berthier notes that Davout has grown restless \u2014 he has not seen laurels while
  Ney wins them. I recommend giving him meaningful orders soon.",
   "severity": "info"
  },
  {
   "message": "Murat is eyeing Mack's position at Nassau. I cannot guarantee he will wait for
  orders, Sire \u2014 any command would restrain him.",
   "severity": "warning"
  },
  {
   "message": "Berthier notes that Ney's recent victories have made him the most celebrated
  commander in the army. (+1 shock, +1 defense, +1 administration while he holds the laurels)",
   "severity": "good"
  }
 ],
 "headline": {
  "class": "victory_won",
  "weight": 73,
  "text": "Sire \u2014 Marshal Ney holds the field at Swabia \u2014 Mack's corps is broken and
  flees.",
  "sub_beats": []
 },
 "berthier_note": "The army knows it is winning, Sire. Press the advantage before their line
  reforms.",
 "talleyrand_report": [],
 "talleyrand_discovery": null,
 "talleyrand_override_note": null,
 "talleyrand_redemption": null,
 "coalition_status": {
  "threat_level": 76,
  "tier": "Formed",
  "sources": [
   {
    "source": "hegemony_passive",
    "amount": 1,
    "target": "France"
   },
   {
    "source": "decay",
    "amount": -3
   }
  ],
  "active_coalition": {
   "name": "Third Coalition",
   "leader": "Britain",
   "posture": "defensive",
   "formed_turn": 1,
   "members": [
    {
     "nation": "Austria",
     "war_exhaustion": 24,
     "strength_display": "100,878 men",
     "strength": 100878,
     "gold": 31
    },
    {
     "nation": "Britain",
     "war_exhaustion": 0,
     "strength_display": "Unknown",
     "strength": 0,
     "gold": 0
    },
    {
     "nation": "Russia",
     "war_exhaustion": 0,
     "strength_display": "Unknown",
     "strength": 0,
     "gold": 0
    }
   ]
  }
 },
 "diplomatic_events": [
  {
   "type": "diplomatic_dp_regen",
   "text": "Talleyrand reports: 5 diplomatic points available (base 3, +1 skill, +1 authority).",
   "priority": "LOW"
  },
  {
   "type": "blockade_begins",
   "text": "BLOCKADE: Britain closes France's ports. Trade is halved and the fleet is pinned at
  anchor, where crews rot.",
   "priority": "MEDIUM"
  },
  {
   "type": "blockade_begins",
   "text": "BLOCKADE: Britain closes Holland's ports. Trade is halved and the fleet is pinned at
  anchor, where crews rot.",
   "priority": "MEDIUM"
  },
  {
   "type": "blockade_begins",
   "text": "BLOCKADE: Britain closes Spain's ports. Trade is halved and the fleet is pinned at
  anchor, where crews rot.",
   "priority": "MEDIUM"
  },
  {
   "type": "design_promoted",
   "text": "REVANCHE: Austria will not forgive Bavaria the loss of Bohemia and 2 more provinces. A
  new design hardens in their court.",
   "priority": "HIGH"
  }
 ],
 "pending_envoy_count": 3,
 "pending_envoys": [
  {
   "nation": "Prussia",
   "proposal_type": "open borders",
   "state": "ACTIVE"
  },
  {
   "nation": "Ottoman",
   "proposal_type": "open borders",
   "state": "WAITING"
  },
  {
   "nation": "Portugal",
   "proposal_type": "open borders",
   "state": "WAITING"
  }
 ]
}
-- POPUP/DIALOGUE [notifications] --
   [
    {
     "id": "f0abdb65-a2b4-42fd-a5f0-109da8bb3fae",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Prussia",
     "message": "An envoy from Prussia has arrived with a proposal.",
     "turn_created": 1,
     "details": {},
     "base_title": "Envoy from Prussia",
     "repeat_count": 1
    },
    {
     "id": "4701ccf4-78db-45e9-bf5c-df791e0b21bc",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Ottoman Empire",
     "message": "An envoy from Ottoman Empire has arrived with a proposal.",
     "turn_created": 1,
     "details": {},
     "base_title": "Envoy from Ottoman Empire",
     "repeat_count": 1
    },
    {
     "id": "65ab1d1c-d423-470e-8390-307f98dd8651",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Portugal",
     "message": "An envoy from Portugal has arrived with a proposal.",
     "turn_created": 1,
     "details": {},
     "base_title": "Envoy from Portugal",
     "repeat_count": 1
    },
    {
     "id": "02591a3b-9b4d-4e49-8fc3-35f18287f5a4",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Ney expects reward",
     "message": "Marshal Ney looks for 40g/turn and holds 0g. His patience holds 2 turns \u2014 open
     the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an estate (a Duchy)
     or grant a rente.",
     "turn_created": 2,
     "details": {
      "marshal": "Ney",
      "expectation": 40,
      "satisfaction": 0,
      "shortfall": 40,
      "grace_turns": 2,
      "remaining_grace": 2
     },
     "base_title": "Marshal Ney expects reward",
     "repeat_count": 1
    },
    {
     "id": "ea289989-7899-4d1e-abb8-5b688a13f88b",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Davout expects reward",
     "message": "Marshal Davout looks for 80g/turn and holds 0g. His patience holds 2 turns \u2014
     open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an estate (a
     Duchy) or grant a rente.",
     "turn_created": 2,
     "details": {
      "marshal": "Davout",
      "expectation": 80,
      "satisfaction": 0,
      "shortfall": 80,
      "grace_turns": 2,
      "remaining_grace": 2
     },
     "base_title": "Marshal Davout expects reward",
     "repeat_count": 1
    },
    {
     "id": "465723d4-2eb3-4023-ab04-b1a109d33bcb",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Soult expects reward",
     "message": "Marshal Soult looks for 80g/turn and holds 0g. His patience holds 2 turns \u2014
     open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an estate (a
     Duchy) or grant a rente.",
     "turn_created": 2,
     "details": {
      "marshal": "Soult",
      "expectation": 80,
      "satisfaction": 0,
      "shortfall": 80,
      "grace_turns": 2,
      "remaining_grace": 2
     },
     "base_title": "Marshal Soult expects reward",
     "repeat_count": 1
    },
    {
     "id": "31a30a69-a547-4ff6-8094-041004e245a9",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Lannes expects reward",
     "message": "Marshal Lannes looks for 80g/turn and holds 0g. His patience holds 2 turns \u2014
     open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an estate (a
     Duchy) or grant a rente.",
     "turn_created": 2,
     "details": {
      "marshal": "Lannes",
      "expectation": 80,
      "satisfaction": 0,
      "shortfall": 80,
      "grace_turns": 2,
      "remaining_grace": 2
     },
     "base_title": "Marshal Lannes expects reward",
     "repeat_count": 1
    },
    {
     "id": "33c5fc9c-8b7b-4da7-977b-546717a2143c",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Murat expects reward",
     "message": "Marshal Murat looks for 80g/turn and holds 0g. His patience holds 2 turns \u2014
     open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an estate (a
     Duchy) or grant a rente.",
     "turn_created": 2,
     "details": {
      "marshal": "Murat",
      "expectation": 80,
      "satisfaction": 0,
      "shortfall": 80,
      "grace_turns": 2,
      "remaining_grace": 2
     },
     "base_title": "Marshal Murat expects reward",
     "repeat_count": 1
    },
    {
     "id": "84b62c07-197f-424d-9184-68293

====================================================================================================
> Murat, attack Mack at Nassau
====================================================================================================
MUSTER — Murat (20,408; 49,743 with the muster committed) vs Mack (substantial force) at Nassau —
  the balance of force looks favorable.
  WILL JOIN — Ney: will march to the sound of the guns
  WILL JOIN — Davout: is willing to march if the roads allow
  WILL NOT — Soult: awaits explicit orders and will NOT march — order 'Soult, support Murat' and he
  will march
  WILL JOIN — Lannes: marches to the sound of the guns — the Roland of the Army
  WILL NOT — Bernadotte: will not lift a finger for this marshal


[Combat] Murat leads the charge! (Aggressive: +15% attack)
[Shield] Mack's DEFENSIVE stance strengthens the line! (+15% defense)
[Combat] Murat's combined arms coordination! (+10% attack)
Murat delivers an effective strike. Murat gains the advantage over Mack. Casualties: Murat's army
  878, Mack 23,011. Both armies remain in the field.

[Cavalry] Murat's 'First Horseman of Europe' — the cavalry turns the rout into annihilation! (+5,000
  pursuit casualties) Murat halts at the frontier of Nassau — Hesse's soil, and we are not at war
  with Hesse. To seize it is to make war on Hesse — choose our purpose, or let the province stand.
[Materiel] Guns, horses and stores lost with the fallen: France -43g, Austria -1400g.
[!] Mack's broken army flees to Frankfurt! (31 lost to march) (recovering for 3 turns)
   [cost=1  turn_advanced=False]
   <event battle> {"battle_name": "The Great Battle of Nassau", "attacker": {"name": "Murat", "casualties": 878, "remaining": 20193, "morale": 90, "forced_retreat": false}, "defender": {"name": "Mack", "casualties": 28011, "remaining": 6284, "morale": 0, "forced_retreat": true}, "attacker_nation": "France", "defender_nation": "Austria", "outcome": "attacker_tactical_victory", "victor": "Murat", "enemy_destroyed": false, "region_conquered": false, "region_name": null, "flanking_bonus": 0, "flanking_origins": ["Swabia"], "vindication": null, "attacker_forced_retreat": false, "defender_forced_retreat": true, "cava
-- REINFORCEMENTS --
   [
    "Ney's forces arrived to reinforce Murat!",
    "Davout's forces arrived to reinforce Murat!",
    "Soult awaits explicit orders and did not march to the sound of the guns.",
    "Lannes's forces arrived to reinforce Murat!",
    "Massed effective strength: 20,408 (lead) + 29,335 committed (Ney, Davout, Lannes) = 49,743.",
    "His supporting allies lost 663 men combined."
   ]
-- COORD TUTORIAL --
   {
    "title": "BERTHIER'S REPORT",
    "message": "\"Sire, our marshals fight as one corps for the first time! The combined arms of
     infantry and cavalry proved decisive.\"",
    "tip": "Position different unit types together for combined arms bonuses. Coordination improves
     with strong relationships between marshals.",
    "warning": "When marshals coordinate, casualties are shared. All friendly marshals in a battle
     region take proportional damage \u2014 even those not directly targeted."
   }
-- BERTHIER'S AFTER-ACTION REPORT --
   {
    "modifier_breakdown": {
     "attacker": [
      {
       "label": "Personality (aggressive)",
       "value": 15,
       "type": "bonus"
      }
     ],
     "defender": [
      {
       "label": "Defensive stance",
       "value": 15,
       "type": "bonus"
      }
     ]
    },
    "casualty_summary": {
     "attacker_name": "Murat",
     "attacker_original": 20408,
     "attacker_casualties": 215,
     "attacker_remaining": 20193,
     "defender_name": "Mack",
     "defender_original": 34295,
     "defender_casualties": 28011,
     "defender_remaining": 6284
    },
    "observation": "Ney, Davout and Lannes arrived to reinforce Murat, but Soult failed to reach the
     field in time.",
    "enemy_voice": "Mack: \"I withdraw in perfect conformity with a plan I have just completed.\"",
    "marshal_voice": "Murat: \"Their squares were a suggestion. My cavalry declined it.\"",
    "expectation_note": "Victory raises Marshal Murat's expectation of reward \u2014 he now looks
     for 120g/turn (holds 0g).",
    "jealousy_note": "Murat fought like a man with something to prove \u2014 and proved it. His
     grievance is settled."
   }
-- POPUP/DIALOGUE [envoy_digest] --
   {
    "turn": 2,
    "count": 2,
    "title": "THE COURTS WRITE",
    "lapsing_count": 2,
    "headline": "Ottoman Empire and Portugal write.",
    "deadline_note": "Answer them here. Unanswered letters lapse when the turn ends, and a court
     left waiting will not raise the matter again for some seasons.",
    "items": [
     {
      "mailbox_id": 2,
      "dialogue_id": 2,
      "from_nation": "Ottoman",
      "power_tier": "secondary",
      "proposal_type": "friendly_gift",
      "proposal_type_display": "Open Borders Agreement",
      "diplomat_name": "Reis Efendi",
      "diplomat_line": "Reis Efendi, serene and unhurried: \"The Porte has outlasted a hundred
     ascendancies by trading with each at its noon; France's noon has come, and the bazaar is open.
     Open the borders.\"",
      "clauses": [
       "Proposal: Open Borders Agreement",
       "Clause: Open borders"
      ],
      "acceptance_hint": "natural willingness to negotiate",
      "state": "WAITING",
      "arrival_turn": 1
     },
     {
      "mailbox_id": 3,
      "dialogue_id": 3,
      "from_nation": "Portugal",
      "power_tier": "minor",
      "proposal_type": "friendly_gift",
      "proposal_type_display": "Open Borders Agreement",
      "diplomat_name": "Araujo",
      "diplomat_line": "Araujo, measuring the room: \"Portugal has watched France grow so vast that
     a careful minister in Lisbon thinks less of resisting such a tide than of finding a quiet
     harbor within it. Open the borders.\"",
      "clauses": [
       "Proposal: Open Borders Agreement",
       "Clause: Open borders",
       "Offer: Gold payment - 60"
      ],
      "acceptance_hint": "natural willingness to negotiate",
      "state": "WAITING",
      "arrival_turn": 1
     }
    ]
   }
-- POPUP/DIALOGUE [battle_diorama] --
   {
    "battle_name": "The Great Battle of Nassau",
    "region": "Nassau",
    "turn": 2,
    "outcome": "attacker_tactical_victory",
    "victor": "Murat",
    "attacker_nation": "France",
    "defender_nation": "Austria",
    "player_side": "attacker",
    "register": "triumph",
    "significant": true,
    "dramatic": true,
    "great_battle": true,
    "region_conquered": false,
    "attacker": {
     "contingents": [
      {
       "name": "Murat",
       "nation": "France",
       "arm": "cavalry",
       "committed": 20408,
       "casualties": 215,
       "remaining": 20193,
       "status": "engaged",
       "lead": true,
       "crowned": false
      },
      {
       "name": "Davout",
       "nation": "France",
       "arm": "infantry",
       "committed": 24118,
       "casualties": 256,
       "remaining": 23862,
       "status": "reinforced",
       "lead": false,
       "crowned": false
      },
      {
       "name": "Ney",
       "nation": "France",
       "arm": "infantry",
       "committed": 21877,
       "casualties": 231,
       "remaining": 21646,
       "status": "reinforced",
       "lead": false,
       "crowned": true
      },
      {
       "name": "Lannes",
       "nation": "France",
       "arm": "infantry",
       "committed": 16698,
       "casualties": 176,
       "remaining": 16522,
       "status": "reinforced",
       "lead": false,
       "crowned": false
      },
      {
       "name": "Soult",
       "nation": "France",
       "arm": "infantry",
       "committed": 37102,
       "casualties": 0,
       "remaining": 37102,
       "status": "refused",
       "lead": false,
       "crowned": false,
       "absence_reason": "awaits explicit orders"
      }
     ],
     "reserve_count": 0,
     "casualties_total": 878,
     "committed_total": 83101,
     "nation": "France"
    },
    "defender": {
     "contingents": [
      {
       "name": "Mack",
       "nation": "Austria",
       "arm": "infantry",
       "committed": 34295,
       "casualties": 28011,
       "remaining": 6284,
       "status": "routed",
       "lead": true,
       "crowned": false
      }
     ],
     "reserve_count": 0,
     "casualties_total": 28011,
     "committed_total": 34295,
     "nation": "Austria"
    },
    "observation": "Ney, Davout and Lannes arrived to reinforce Murat, but Soult failed to reach the
     field in time.",
    "enemy_voice": "Mack: \"I withdraw in perfect conformity with a plan I have just completed.\""
   }
-- POPUP/DIALOGUE [marshal_petition] --
   {
    "kind": "jealousy_confrontation",
    "title": "Marshal Murat seeks an audience",
    "body": "Sire, Murat has expressed... displeasure about Ney's recent recognition. He requests a
     command worthy of his talents. The staff now speak of the quarrel openly \u2014 this is no
     longer a passing mood.",
    "speaker": "Murat",
    "options": [
     {
      "id": "acknowledge",
      "label": "Acknowledge",
      "detail": "Free, and it fixes nothing: the grievance stands 3 more turns \u2014 souring his
     ties and coordination with Ney \u2014 then cools on its own.",
      "cost_note": "",
      "enabled": true
     },
     {
      "id": "promise",
      "label": "Promise Glory",
      "detail": "His patience is bought \u2014 the grievance shortens by 2 turns.",
      "cost_note": "1 AP",
      "ap_cost": 1,
      "enabled": true
     },
     {
      "id": "rebuke",
      "label": "Rebuke",
      "detail": "Trust -5. The grievance shortens by 1 turn. He will not act on his own this cycle
     \u2014 he respects the Emperor's anger, briefly.",
      "cost_note": "",
      "enabled": true
     }
    ],
    "context": {
     "marshal": "Murat",
     "target": "Ney",
     "escalation_level": 1
    },
    "turn": 1
   }
-- POPUP/DIALOGUE [notifications] --
   [
    {
     "id": "f0abdb65-a2b4-42fd-a5f0-109da8bb3fae",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Prussia",
     "message": "An envoy from Prussia has arrived with a proposal.",
     "turn_created": 1,
     "details": {},
     "base_title": "Envoy from Prussia",
     "repeat_count": 1
    },
    {
     "id": "4701ccf4-78db-45e9-bf5c-df791e0b21bc",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Ottoman Empire",
     "message": "An envoy from Ottoman Empire has arrived with a proposal.",
     "turn_created": 1,
     "details": {},
     "base_title": "Envoy from Ottoman Empire",
     "repeat_count": 1
    },
    {
     "id": "65ab1d1c-d423-470e-8390-307f98dd8651",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Portugal",
     "message": "An envoy from Portugal has arrived with a proposal.",
     "turn_created": 1,
     "details": {},
     "base_title": "Envoy from Portugal",
     "repeat_count": 1
    },
    {
     "id": "02591a3b-9b4d-4e49-8fc3-35f18287f5a4",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Ney expects reward",
     "message": "Marshal Ney looks for 40g/turn and holds 0g. His patience holds 2 turns \u2014 open
     the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an estate (a Duchy)
     or grant a rente.",
     "turn_created": 2,
     "details": {
      "marshal": "Ney",
      "expectation": 40,
      "satisfaction": 0,
      "shortfall": 40,
      "grace_turns": 2,
      "remaining_grace": 2
     },
     "base_title": "Marshal Ney expects reward",
     "repeat_count": 1
    },
    {
     "id": "ea289989-7899-4d1e-abb8-5b688a13f88b",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Davout expects reward",
     "message": "Marshal Davout looks for 80g/turn and holds 0g. His patience holds 2 turns \u2014
     open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an estate (a
     Duchy) or grant a rente.",
     "turn_created": 2,
     "details": {
      "marshal": "Davout",
      "expectation": 80,
      "satisfaction": 0,
      "shortfall": 80,
      "grace_turns": 2,
      "remaining_grace": 2
     },
     "base_title": "Marshal Davout expects reward",
     "repeat_count": 1
    },
    {
     "id": "465723d4-2eb3-4023-ab04-b1a109d33bcb",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Soult expects reward",
     "message": "Marshal Soult looks for 80g/turn and holds 0g. His patience holds 2 turns \u2014
     open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an estate (a
     Duchy) or grant a rente.",
     "turn_created": 2,
     "details": {
      "marshal": "Soult",
      "expectation": 80,
      "satisfaction": 0,
      "shortfall": 80,
      "grace_turns": 2,
      "remaining_grace": 2
     },
     "base_title": "Marshal Soult expects reward",
     "repeat_count": 1
    },
    {
     "id": "31a30a69-a547-4ff6-8094-041004e245a9",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Lannes expects reward",
     "message": "Marshal Lannes looks for 80g/turn and holds 0g. His patience holds 2 turns \u2014
     open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an estate (a
     Duchy) or grant a rente.",
     "turn_created": 2,
     "details": {
      "marshal": "Lannes",
      "expectation": 80,
      "satisfaction": 0,
      "shortfall": 80,
      "grace_turns": 2,
      "remaining_grace": 2
     },
     "base_title": "Marshal Lannes expects reward",
     "repeat_count": 1
    },
    {
     "id": "33c5fc9c-8b7b-4da7-977b-546717a2143c",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Murat expects reward",
     "message": "Marshal Murat looks for 80g/turn and holds 0g. His patience holds 2 turns \u2014
     open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an estate (a
     Duchy) or grant a rente.",
     "turn_created": 2,
     "details": {
      "marshal": "Murat",
      "expectation": 80,
      "satisfaction": 0,
      "shortfall": 80,
      "grace_turns": 2,
      "remaining_grace": 2
     },
     "base_title": "Marshal Murat expects reward",
     "repeat_count": 1
    },
    {
     "id": "84b62c07-197f-424d-9184-68293

====================================================================================================
> Ney, march on Bohemia
====================================================================================================
I don't understand that choice, Sire. Options: 1=Conquest, 2=Forced Alliance, 3=Subjugation, 4=Back
  Out
-- POPUP/DIALOGUE [envoy_digest] --
   {
    "turn": 2,
    "count": 2,
    "title": "THE COURTS WRITE",
    "lapsing_count": 2,
    "headline": "Ottoman Empire and Portugal write.",
    "deadline_note": "Answer them here. Unanswered letters lapse when the turn ends, and a court
     left waiting will not raise the matter again for some seasons.",
    "items": [
     {
      "mailbox_id": 2,
      "dialogue_id": 2,
      "from_nation": "Ottoman",
      "power_tier": "secondary",
      "proposal_type": "friendly_gift",
      "proposal_type_display": "Open Borders Agreement",
      "diplomat_name": "Reis Efendi",
      "diplomat_line": "Reis Efendi, serene and unhurried: \"The Porte has outlasted a hundred
     ascendancies by trading with each at its noon; France's noon has come, and the bazaar is open.
     Open the borders.\"",
      "clauses": [
       "Proposal: Open Borders Agreement",
       "Clause: Open borders"
      ],
      "acceptance_hint": "natural willingness to negotiate",
      "state": "WAITING",
      "arrival_turn": 1
     },
     {
      "mailbox_id": 3,
      "dialogue_id": 3,
      "from_nation": "Portugal",
      "power_tier": "minor",
      "proposal_type": "friendly_gift",
      "proposal_type_display": "Open Borders Agreement",
      "diplomat_name": "Araujo",
      "diplomat_line": "Araujo, measuring the room: \"Portugal has watched France grow so vast that
     a careful minister in Lisbon thinks less of resisting such a tide than of finding a quiet
     harbor within it. Open the borders.\"",
      "clauses": [
       "Proposal: Open Borders Agreement",
       "Clause: Open borders",
       "Offer: Gold payment - 60"
      ],
      "acceptance_hint": "natural willingness to negotiate",
      "state": "WAITING",
      "arrival_turn": 1
     }
    ]
   }
-- POPUP/DIALOGUE [incoming_proposal] --
   {
    "from_nation": "Prussia",
    "diplomat_name": "Hardenberg",
    "diplomat_personality": "hawk",
    "proposal_type": "open_borders",
    "proposal_type_display": "Open Borders Agreement",
    "clauses": [
     "Proposal: Open Borders Agreement",
     "Clause: Open borders"
    ],
    "talleyrand_assessment": "An unexpected overture. There may be hidden motives worth examining.",
    "acceptance_hint": "natural willingness to negotiate",
    "rejection_hint": "their diplomat outmaneuvered us",
    "is_counter_offer": false,
    "decision_reason": "hegemony_pressure",
    "decision_reason_display": "hegemony pressure",
    "diplomat_line": "Hardenberg, stiffly: \"Prussia's interest is the Rhine at peace and the army
     at home; Berlin signs where those two meet. Open the borders.\"",
    "dialogue_id": 1
   }
-- POPUP/DIALOGUE [notifications] --
   [
    {
     "id": "f0abdb65-a2b4-42fd-a5f0-109da8bb3fae",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Prussia",
     "message": "An envoy from Prussia has arrived with a proposal.",
     "turn_created": 1,
     "details": {},
     "base_title": "Envoy from Prussia",
     "repeat_count": 1
    },
    {
     "id": "4701ccf4-78db-45e9-bf5c-df791e0b21bc",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Ottoman Empire",
     "message": "An envoy from Ottoman Empire has arrived with a proposal.",
     "turn_created": 1,
     "details": {},
     "base_title": "Envoy from Ottoman Empire",
     "repeat_count": 1
    },
    {
     "id": "65ab1d1c-d423-470e-8390-307f98dd8651",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Portugal",
     "message": "An envoy from Portugal has arrived with a proposal.",
     "turn_created": 1,
     "details": {},
     "base_title": "Envoy from Portugal",
     "repeat_count": 1
    },
    {
     "id": "02591a3b-9b4d-4e49-8fc3-35f18287f5a4",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Ney expects reward",
     "message": "Marshal Ney looks for 40g/turn and holds 0g. His patience holds 2 turns \u2014 open
     the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an estate (a Duchy)
     or grant a rente.",
     "turn_created": 2,
     "details": {
      "marshal": "Ney",
      "expectation": 40,
      "satisfaction": 0,
      "shortfall": 40,
      "grace_turns": 2,
      "remaining_grace": 2
     },
     "base_title": "Marshal Ney expects reward",
     "repeat_count": 1
    },
    {
     "id": "ea289989-7899-4d1e-abb8-5b688a13f88b",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Davout expects reward",
     "message": "Marshal Davout looks for 80g/turn and holds 0g. His patience holds 2 turns \u2014
     open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an estate (a
     Duchy) or grant a rente.",
     "turn_created": 2,
     "details": {
      "marshal": "Davout",
      "expectation": 80,
      "satisfaction": 0,
      "shortfall": 80,
      "grace_turns": 2,
      "remaining_grace": 2
     },
     "base_title": "Marshal Davout expects reward",
     "repeat_count": 1
    },
    {
     "id": "465723d4-2eb3-4023-ab04-b1a109d33bcb",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Soult expects reward",
     "message": "Marshal Soult looks for 80g/turn and holds 0g. His patience holds 2 turns \u2014
     open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an estate (a
     Duchy) or grant a rente.",
     "turn_created": 2,
     "details": {
      "marshal": "Soult",
      "expectation": 80,
      "satisfaction": 0,
      "shortfall": 80,
      "grace_turns": 2,
      "remaining_grace": 2
     },
     "base_title": "Marshal Soult expects reward",
     "repeat_count": 1
    },
    {
     "id": "31a30a69-a547-4ff6-8094-041004e245a9",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Lannes expects reward",
     "message": "Marshal Lannes looks for 80g/turn and holds 0g. His patience holds 2 turns \u2014
     open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an estate (a
     Duchy) or grant a rente.",
     "turn_created": 2,
     "details": {
      "marshal": "Lannes",
      "expectation": 80,
      "satisfaction": 0,
      "shortfall": 80,
      "grace_turns": 2,
      "remaining_grace": 2
     },
     "base_title": "Marshal Lannes expects reward",
     "repeat_count": 1
    },
    {
     "id": "33c5fc9c-8b7b-4da7-977b-546717a2143c",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Murat expects reward",
     "message": "Marshal Murat looks for 80g/turn and holds 0g. His patience holds 2 turns \u2014
     open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an estate (a
     Duchy) or grant a rente.",
     "turn_created": 2,
     "details": {
      "marshal": "Murat",
      "expectation": 80,
      "satisfaction": 0,
      "shortfall": 80,
      "grace_turns": 2,
      "remaining_grace": 2
     },
     "base_title": "Marshal Murat expects reward",
     "repeat_count": 1
    },
    {
     "id": "84b62c07-197f-424d-9184-68293

====================================================================================================
> Davout, move to Franconia
====================================================================================================
I don't understand that choice, Sire. Options: 1=Conquest, 2=Forced Alliance, 3=Subjugation, 4=Back
  Out
-- POPUP/DIALOGUE [envoy_digest] --
   {
    "turn": 2,
    "count": 2,
    "title": "THE COURTS WRITE",
    "lapsing_count": 2,
    "headline": "Ottoman Empire and Portugal write.",
    "deadline_note": "Answer them here. Unanswered letters lapse when the turn ends, and a court
     left waiting will not raise the matter again for some seasons.",
    "items": [
     {
      "mailbox_id": 2,
      "dialogue_id": 2,
      "from_nation": "Ottoman",
      "power_tier": "secondary",
      "proposal_type": "friendly_gift",
      "proposal_type_display": "Open Borders Agreement",
      "diplomat_name": "Reis Efendi",
      "diplomat_line": "Reis Efendi, serene and unhurried: \"The Porte has outlasted a hundred
     ascendancies by trading with each at its noon; France's noon has come, and the bazaar is open.
     Open the borders.\"",
      "clauses": [
       "Proposal: Open Borders Agreement",
       "Clause: Open borders"
      ],
      "acceptance_hint": "natural willingness to negotiate",
      "state": "WAITING",
      "arrival_turn": 1
     },
     {
      "mailbox_id": 3,
      "dialogue_id": 3,
      "from_nation": "Portugal",
      "power_tier": "minor",
      "proposal_type": "friendly_gift",
      "proposal_type_display": "Open Borders Agreement",
      "diplomat_name": "Araujo",
      "diplomat_line": "Araujo, measuring the room: \"Portugal has watched France grow so vast that
     a careful minister in Lisbon thinks less of resisting such a tide than of finding a quiet
     harbor within it. Open the borders.\"",
      "clauses": [
       "Proposal: Open Borders Agreement",
       "Clause: Open borders",
       "Offer: Gold payment - 60"
      ],
      "acceptance_hint": "natural willingness to negotiate",
      "state": "WAITING",
      "arrival_turn": 1
     }
    ]
   }
-- POPUP/DIALOGUE [notifications] --
   [
    {
     "id": "f0abdb65-a2b4-42fd-a5f0-109da8bb3fae",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Prussia",
     "message": "An envoy from Prussia has arrived with a proposal.",
     "turn_created": 1,
     "details": {},
     "base_title": "Envoy from Prussia",
     "repeat_count": 1
    },
    {
     "id": "4701ccf4-78db-45e9-bf5c-df791e0b21bc",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Ottoman Empire",
     "message": "An envoy from Ottoman Empire has arrived with a proposal.",
     "turn_created": 1,
     "details": {},
     "base_title": "Envoy from Ottoman Empire",
     "repeat_count": 1
    },
    {
     "id": "65ab1d1c-d423-470e-8390-307f98dd8651",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Portugal",
     "message": "An envoy from Portugal has arrived with a proposal.",
     "turn_created": 1,
     "details": {},
     "base_title": "Envoy from Portugal",
     "repeat_count": 1
    },
    {
     "id": "02591a3b-9b4d-4e49-8fc3-35f18287f5a4",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Ney expects reward",
     "message": "Marshal Ney looks for 40g/turn and holds 0g. His patience holds 2 turns \u2014 open
     the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an estate (a Duchy)
     or grant a rente.",
     "turn_created": 2,
     "details": {
      "marshal": "Ney",
      "expectation": 40,
      "satisfaction": 0,
      "shortfall": 40,
      "grace_turns": 2,
      "remaining_grace": 2
     },
     "base_title": "Marshal Ney expects reward",
     "repeat_count": 1
    },
    {
     "id": "ea289989-7899-4d1e-abb8-5b688a13f88b",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Davout expects reward",
     "message": "Marshal Davout looks for 80g/turn and holds 0g. His patience holds 2 turns \u2014
     open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an estate (a
     Duchy) or grant a rente.",
     "turn_created": 2,
     "details": {
      "marshal": "Davout",
      "expectation": 80,
      "satisfaction": 0,
      "shortfall": 80,
      "grace_turns": 2,
      "remaining_grace": 2
     },
     "base_title": "Marshal Davout expects reward",
     "repeat_count": 1
    },
    {
     "id": "465723d4-2eb3-4023-ab04-b1a109d33bcb",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Soult expects reward",
     "message": "Marshal Soult looks for 80g/turn and holds 0g. His patience holds 2 turns \u2014
     open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an estate (a
     Duchy) or grant a rente.",
     "turn_created": 2,
     "details": {
      "marshal": "Soult",
      "expectation": 80,
      "satisfaction": 0,
      "shortfall": 80,
      "grace_turns": 2,
      "remaining_grace": 2
     },
     "base_title": "Marshal Soult expects reward",
     "repeat_count": 1
    },
    {
     "id": "31a30a69-a547-4ff6-8094-041004e245a9",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Lannes expects reward",
     "message": "Marshal Lannes looks for 80g/turn and holds 0g. His patience holds 2 turns \u2014
     open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an estate (a
     Duchy) or grant a rente.",
     "turn_created": 2,
     "details": {
      "marshal": "Lannes",
      "expectation": 80,
      "satisfaction": 0,
      "shortfall": 80,
      "grace_turns": 2,
      "remaining_grace": 2
     },
     "base_title": "Marshal Lannes expects reward",
     "repeat_count": 1
    },
    {
     "id": "33c5fc9c-8b7b-4da7-977b-546717a2143c",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Murat expects reward",
     "message": "Marshal Murat looks for 80g/turn and holds 0g. His patience holds 2 turns \u2014
     open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an estate (a
     Duchy) or grant a rente.",
     "turn_created": 2,
     "details": {
      "marshal": "Murat",
      "expectation": 80,
      "satisfaction": 0,
      "shortfall": 80,
      "grace_turns": 2,
      "remaining_grace": 2
     },
     "base_title": "Marshal Murat expects reward",
     "repeat_count": 1
    },
    {
     "id": "84b62c07-197f-424d-9184-68293

====================================================================================================
> 4
====================================================================================================
Of course, Sire. Take your time.
-- POPUP/DIALOGUE [envoy_digest] --
   {
    "turn": 2,
    "count": 2,
    "title": "THE COURTS WRITE",
    "lapsing_count": 2,
    "headline": "Ottoman Empire and Portugal write.",
    "deadline_note": "Answer them here. Unanswered letters lapse when the turn ends, and a court
     left waiting will not raise the matter again for some seasons.",
    "items": [
     {
      "mailbox_id": 2,
      "dialogue_id": 2,
      "from_nation": "Ottoman",
      "power_tier": "secondary",
      "proposal_type": "friendly_gift",
      "proposal_type_display": "Open Borders Agreement",
      "diplomat_name": "Reis Efendi",
      "diplomat_line": "Reis Efendi, serene and unhurried: \"The Porte has outlasted a hundred
     ascendancies by trading with each at its noon; France's noon has come, and the bazaar is open.
     Open the borders.\"",
      "clauses": [
       "Proposal: Open Borders Agreement",
       "Clause: Open borders"
      ],
      "acceptance_hint": "natural willingness to negotiate",
      "state": "ACTIVE",
      "arrival_turn": 1
     },
     {
      "mailbox_id": 3,
      "dialogue_id": 3,
      "from_nation": "Portugal",
      "power_tier": "minor",
      "proposal_type": "friendly_gift",
      "proposal_type_display": "Open Borders Agreement",
      "diplomat_name": "Araujo",
      "diplomat_line": "Araujo, measuring the room: \"Portugal has watched France grow so vast that
     a careful minister in Lisbon thinks less of resisting such a tide than of finding a quiet
     harbor within it. Open the borders.\"",
      "clauses": [
       "Proposal: Open Borders Agreement",
       "Clause: Open borders",
       "Offer: Gold payment - 60"
      ],
      "acceptance_hint": "natural willingness to negotiate",
      "state": "WAITING",
      "arrival_turn": 1
     }
    ]
   }
-- POPUP/DIALOGUE [notifications] --
   [
    {
     "id": "f0abdb65-a2b4-42fd-a5f0-109da8bb3fae",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Prussia",
     "message": "An envoy from Prussia has arrived with a proposal.",
     "turn_created": 1,
     "details": {},
     "base_title": "Envoy from Prussia",
     "repeat_count": 1
    },
    {
     "id": "4701ccf4-78db-45e9-bf5c-df791e0b21bc",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Ottoman Empire",
     "message": "An envoy from Ottoman Empire has arrived with a proposal.",
     "turn_created": 1,
     "details": {},
     "base_title": "Envoy from Ottoman Empire",
     "repeat_count": 1
    },
    {
     "id": "65ab1d1c-d423-470e-8390-307f98dd8651",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Portugal",
     "message": "An envoy from Portugal has arrived with a proposal.",
     "turn_created": 1,
     "details": {},
     "base_title": "Envoy from Portugal",
     "repeat_count": 1
    },
    {
     "id": "02591a3b-9b4d-4e49-8fc3-35f18287f5a4",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Ney expects reward",
     "message": "Marshal Ney looks for 40g/turn and holds 0g. His patience holds 2 turns \u2014 open
     the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an estate (a Duchy)
     or grant a rente.",
     "turn_created": 2,
     "details": {
      "marshal": "Ney",
      "expectation": 40,
      "satisfaction": 0,
      "shortfall": 40,
      "grace_turns": 2,
      "remaining_grace": 2
     },
     "base_title": "Marshal Ney expects reward",
     "repeat_count": 1
    },
    {
     "id": "ea289989-7899-4d1e-abb8-5b688a13f88b",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Davout expects reward",
     "message": "Marshal Davout looks for 80g/turn and holds 0g. His patience holds 2 turns \u2014
     open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an estate (a
     Duchy) or grant a rente.",
     "turn_created": 2,
     "details": {
      "marshal": "Davout",
      "expectation": 80,
      "satisfaction": 0,
      "shortfall": 80,
      "grace_turns": 2,
      "remaining_grace": 2
     },
     "base_title": "Marshal Davout expects reward",
     "repeat_count": 1
    },
    {
     "id": "465723d4-2eb3-4023-ab04-b1a109d33bcb",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Soult expects reward",
     "message": "Marshal Soult looks for 80g/turn and holds 0g. His patience holds 2 turns \u2014
     open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an estate (a
     Duchy) or grant a rente.",
     "turn_created": 2,
     "details": {
      "marshal": "Soult",
      "expectation": 80,
      "satisfaction": 0,
      "shortfall": 80,
      "grace_turns": 2,
      "remaining_grace": 2
     },
     "base_title": "Marshal Soult expects reward",
     "repeat_count": 1
    },
    {
     "id": "31a30a69-a547-4ff6-8094-041004e245a9",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Lannes expects reward",
     "message": "Marshal Lannes looks for 80g/turn and holds 0g. His patience holds 2 turns \u2014
     open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an estate (a
     Duchy) or grant a rente.",
     "turn_created": 2,
     "details": {
      "marshal": "Lannes",
      "expectation": 80,
      "satisfaction": 0,
      "shortfall": 80,
      "grace_turns": 2,
      "remaining_grace": 2
     },
     "base_title": "Marshal Lannes expects reward",
     "repeat_count": 1
    },
    {
     "id": "33c5fc9c-8b7b-4da7-977b-546717a2143c",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Murat expects reward",
     "message": "Marshal Murat looks for 80g/turn and holds 0g. His patience holds 2 turns \u2014
     open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an estate (a
     Duchy) or grant a rente.",
     "turn_created": 2,
     "details": {
      "marshal": "Murat",
      "expectation": 80,
      "satisfaction": 0,
      "shortfall": 80,
      "grace_turns": 2,
      "remaining_grace": 2
     },
     "base_title": "Marshal Murat expects reward",
     "repeat_count": 1
    },
    {
     "id": "84b62c07-197f-424d-9184-68293

====================================================================================================
> Davout, move to Franconia
====================================================================================================
Davout moves from Nassau to Franconia (422 lost to march)
[HINT] Tyrol is undefended — attack to capture it!
   [cost=1  turn_advanced=False]
   <event move> {"marshal": "Davout", "from": "Nassau", "to": "Franconia", "march_losses": 422}
-- POPUP/DIALOGUE [notifications] --
   [
    {
     "id": "02591a3b-9b4d-4e49-8fc3-35f18287f5a4",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Ney expects reward",
     "message": "Marshal Ney looks for 40g/turn and holds 0g. His patience holds 2 turns \u2014 open
     the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an estate (a Duchy)
     or grant a rente.",
     "turn_created": 2,
     "details": {
      "marshal": "Ney",
      "expectation": 40,
      "satisfaction": 0,
      "shortfall": 40,
      "grace_turns": 2,
      "remaining_grace": 2
     },
     "base_title": "Marshal Ney expects reward",
     "repeat_count": 1
    },
    {
     "id": "ea289989-7899-4d1e-abb8-5b688a13f88b",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Davout expects reward",
     "message": "Marshal Davout looks for 80g/turn and holds 0g. His patience holds 2 turns \u2014
     open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an estate (a
     Duchy) or grant a rente.",
     "turn_created": 2,
     "details": {
      "marshal": "Davout",
      "expectation": 80,
      "satisfaction": 0,
      "shortfall": 80,
      "grace_turns": 2,
      "remaining_grace": 2
     },
     "base_title": "Marshal Davout expects reward",
     "repeat_count": 1
    },
    {
     "id": "465723d4-2eb3-4023-ab04-b1a109d33bcb",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Soult expects reward",
     "message": "Marshal Soult looks for 80g/turn and holds 0g. His patience holds 2 turns \u2014
     open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an estate (a
     Duchy) or grant a rente.",
     "turn_created": 2,
     "details": {
      "marshal": "Soult",
      "expectation": 80,
      "satisfaction": 0,
      "shortfall": 80,
      "grace_turns": 2,
      "remaining_grace": 2
     },
     "base_title": "Marshal Soult expects reward",
     "repeat_count": 1
    },
    {
     "id": "31a30a69-a547-4ff6-8094-041004e245a9",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Lannes expects reward",
     "message": "Marshal Lannes looks for 80g/turn and holds 0g. His patience holds 2 turns \u2014
     open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an estate (a
     Duchy) or grant a rente.",
     "turn_created": 2,
     "details": {
      "marshal": "Lannes",
      "expectation": 80,
      "satisfaction": 0,
      "shortfall": 80,
      "grace_turns": 2,
      "remaining_grace": 2
     },
     "base_title": "Marshal Lannes expects reward",
     "repeat_count": 1
    },
    {
     "id": "33c5fc9c-8b7b-4da7-977b-546717a2143c",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Murat expects reward",
     "message": "Marshal Murat looks for 80g/turn and holds 0g. His patience holds 2 turns \u2014
     open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an estate (a
     Duchy) or grant a rente.",
     "turn_created": 2,
     "details": {
      "marshal": "Murat",
      "expectation": 80,
      "satisfaction": 0,
      "shortfall": 80,
      "grace_turns": 2,
      "remaining_grace": 2
     },
     "base_title": "Marshal Murat expects reward",
     "repeat_count": 1
    },
    {
     "id": "84b62c07-197f-424d-9184-682932ef6187",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Bernadotte expects reward",
     "message": "Marshal Bernadotte looks for 80g/turn and holds 0g. His patience holds 2 turns
     \u2014 open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an
     estate (a Duchy) or grant a rente.",
     "turn_created": 2,
     "details": {
      "marshal": "Bernadotte",
      "expectation": 80,
      "satisfaction": 0,
      "shortfall": 80,
      "grace_turns": 2,
      "remaining_grace": 2
     },
     "base_title": "Marshal Bernadotte expects reward",
     "repeat_count": 1
    },
    {
     "id": "5c4cb15e-c87a-41ca-aa75-01dd1056ab1b",
     "type": "treaty_signed",
     "priority": 0,
     "title": "Treaty with Ottoman",
     "message": "Ottoman and France have signed an Open Borders Agreement.",
     "turn_created": 2,
     "details": {
      "counterpart": "Ottoman"
     },
     "base_title": "Treaty with Ottoman",
     "repeat_count": 1
    },
    {
     "i

====================================================================================================
> Soult, move to Munich
====================================================================================================
Soult moves from Swabia to Munich (2,226 lost to march)
[HINT] Tyrol is undefended — attack to capture it!
   [cost=1  turn_advanced=False]
   <event move> {"marshal": "Soult", "from": "Swabia", "to": "Munich", "march_losses": 2226}
-- POPUP/DIALOGUE [notifications] --
   [
    {
     "id": "02591a3b-9b4d-4e49-8fc3-35f18287f5a4",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Ney expects reward",
     "message": "Marshal Ney looks for 40g/turn and holds 0g. His patience holds 2 turns \u2014 open
     the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an estate (a Duchy)
     or grant a rente.",
     "turn_created": 2,
     "details": {
      "marshal": "Ney",
      "expectation": 40,
      "satisfaction": 0,
      "shortfall": 40,
      "grace_turns": 2,
      "remaining_grace": 2
     },
     "base_title": "Marshal Ney expects reward",
     "repeat_count": 1
    },
    {
     "id": "ea289989-7899-4d1e-abb8-5b688a13f88b",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Davout expects reward",
     "message": "Marshal Davout looks for 80g/turn and holds 0g. His patience holds 2 turns \u2014
     open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an estate (a
     Duchy) or grant a rente.",
     "turn_created": 2,
     "details": {
      "marshal": "Davout",
      "expectation": 80,
      "satisfaction": 0,
      "shortfall": 80,
      "grace_turns": 2,
      "remaining_grace": 2
     },
     "base_title": "Marshal Davout expects reward",
     "repeat_count": 1
    },
    {
     "id": "465723d4-2eb3-4023-ab04-b1a109d33bcb",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Soult expects reward",
     "message": "Marshal Soult looks for 80g/turn and holds 0g. His patience holds 2 turns \u2014
     open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an estate (a
     Duchy) or grant a rente.",
     "turn_created": 2,
     "details": {
      "marshal": "Soult",
      "expectation": 80,
      "satisfaction": 0,
      "shortfall": 80,
      "grace_turns": 2,
      "remaining_grace": 2
     },
     "base_title": "Marshal Soult expects reward",
     "repeat_count": 1
    },
    {
     "id": "31a30a69-a547-4ff6-8094-041004e245a9",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Lannes expects reward",
     "message": "Marshal Lannes looks for 80g/turn and holds 0g. His patience holds 2 turns \u2014
     open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an estate (a
     Duchy) or grant a rente.",
     "turn_created": 2,
     "details": {
      "marshal": "Lannes",
      "expectation": 80,
      "satisfaction": 0,
      "shortfall": 80,
      "grace_turns": 2,
      "remaining_grace": 2
     },
     "base_title": "Marshal Lannes expects reward",
     "repeat_count": 1
    },
    {
     "id": "33c5fc9c-8b7b-4da7-977b-546717a2143c",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Murat expects reward",
     "message": "Marshal Murat looks for 80g/turn and holds 0g. His patience holds 2 turns \u2014
     open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an estate (a
     Duchy) or grant a rente.",
     "turn_created": 2,
     "details": {
      "marshal": "Murat",
      "expectation": 80,
      "satisfaction": 0,
      "shortfall": 80,
      "grace_turns": 2,
      "remaining_grace": 2
     },
     "base_title": "Marshal Murat expects reward",
     "repeat_count": 1
    },
    {
     "id": "84b62c07-197f-424d-9184-682932ef6187",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Bernadotte expects reward",
     "message": "Marshal Bernadotte looks for 80g/turn and holds 0g. His patience holds 2 turns
     \u2014 open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an
     estate (a Duchy) or grant a rente.",
     "turn_created": 2,
     "details": {
      "marshal": "Bernadotte",
      "expectation": 80,
      "satisfaction": 0,
      "shortfall": 80,
      "grace_turns": 2,
      "remaining_grace": 2
     },
     "base_title": "Marshal Bernadotte expects reward",
     "repeat_count": 1
    },
    {
     "id": "5c4cb15e-c87a-41ca-aa75-01dd1056ab1b",
     "type": "treaty_signed",
     "priority": 0,
     "title": "Treaty with Ottoman",
     "message": "Ottoman and France have signed an Open Borders Agreement.",
     "turn_created": 2,
     "details": {
      "counterpart": "Ottoman"
     },
     "base_title": "Treaty with Ottoman",
     "repeat_count": 1
    },
    {
     "i

====================================================================================================
> Lannes, move to Rhineland
====================================================================================================
Lannes moves from Nassau to Rhineland
   [cost=1  turn_advanced=False]
   <event move> {"marshal": "Lannes", "from": "Nassau", "to": "Rhineland"}
-- POPUP/DIALOGUE [notifications] --
   [
    {
     "id": "02591a3b-9b4d-4e49-8fc3-35f18287f5a4",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Ney expects reward",
     "message": "Marshal Ney looks for 40g/turn and holds 0g. His patience holds 2 turns \u2014 open
     the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an estate (a Duchy)
     or grant a rente.",
     "turn_created": 2,
     "details": {
      "marshal": "Ney",
      "expectation": 40,
      "satisfaction": 0,
      "shortfall": 40,
      "grace_turns": 2,
      "remaining_grace": 2
     },
     "base_title": "Marshal Ney expects reward",
     "repeat_count": 1
    },
    {
     "id": "ea289989-7899-4d1e-abb8-5b688a13f88b",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Davout expects reward",
     "message": "Marshal Davout looks for 80g/turn and holds 0g. His patience holds 2 turns \u2014
     open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an estate (a
     Duchy) or grant a rente.",
     "turn_created": 2,
     "details": {
      "marshal": "Davout",
      "expectation": 80,
      "satisfaction": 0,
      "shortfall": 80,
      "grace_turns": 2,
      "remaining_grace": 2
     },
     "base_title": "Marshal Davout expects reward",
     "repeat_count": 1
    },
    {
     "id": "465723d4-2eb3-4023-ab04-b1a109d33bcb",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Soult expects reward",
     "message": "Marshal Soult looks for 80g/turn and holds 0g. His patience holds 2 turns \u2014
     open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an estate (a
     Duchy) or grant a rente.",
     "turn_created": 2,
     "details": {
      "marshal": "Soult",
      "expectation": 80,
      "satisfaction": 0,
      "shortfall": 80,
      "grace_turns": 2,
      "remaining_grace": 2
     },
     "base_title": "Marshal Soult expects reward",
     "repeat_count": 1
    },
    {
     "id": "31a30a69-a547-4ff6-8094-041004e245a9",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Lannes expects reward",
     "message": "Marshal Lannes looks for 80g/turn and holds 0g. His patience holds 2 turns \u2014
     open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an estate (a
     Duchy) or grant a rente.",
     "turn_created": 2,
     "details": {
      "marshal": "Lannes",
      "expectation": 80,
      "satisfaction": 0,
      "shortfall": 80,
      "grace_turns": 2,
      "remaining_grace": 2
     },
     "base_title": "Marshal Lannes expects reward",
     "repeat_count": 1
    },
    {
     "id": "33c5fc9c-8b7b-4da7-977b-546717a2143c",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Murat expects reward",
     "message": "Marshal Murat looks for 80g/turn and holds 0g. His patience holds 2 turns \u2014
     open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an estate (a
     Duchy) or grant a rente.",
     "turn_created": 2,
     "details": {
      "marshal": "Murat",
      "expectation": 80,
      "satisfaction": 0,
      "shortfall": 80,
      "grace_turns": 2,
      "remaining_grace": 2
     },
     "base_title": "Marshal Murat expects reward",
     "repeat_count": 1
    },
    {
     "id": "84b62c07-197f-424d-9184-682932ef6187",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Bernadotte expects reward",
     "message": "Marshal Bernadotte looks for 80g/turn and holds 0g. His patience holds 2 turns
     \u2014 open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an
     estate (a Duchy) or grant a rente.",
     "turn_created": 2,
     "details": {
      "marshal": "Bernadotte",
      "expectation": 80,
      "satisfaction": 0,
      "shortfall": 80,
      "grace_turns": 2,
      "remaining_grace": 2
     },
     "base_title": "Marshal Bernadotte expects reward",
     "repeat_count": 1
    },
    {
     "id": "5c4cb15e-c87a-41ca-aa75-01dd1056ab1b",
     "type": "treaty_signed",
     "priority": 0,
     "title": "Treaty with Ottoman",
     "message": "Ottoman and France have signed an Open Borders Agreement.",
     "turn_created": 2,
     "details": {
      "counterpart": "Ottoman"
     },
     "base_title": "Treaty with Ottoman",
     "repeat_count": 1
    },
    {
     "i

====================================================================================================
> end turn
====================================================================================================
Turn 2 ended. Turn 3 begins!

Income: 3400g | Charges of Empire: -9g | Admiralty: -90g | Blockade: -213g | Upkeep: 1556g (incl.
  96g over-limit, 252g Grande Armée) | Other: +795g | Net: +2327g | Treasury: 4,928g
   [cost=0  turn_advanced=False]
   <event retreat_recovery> {"marshal": "Massena", "nation": "France", "stage": 1, "penalty": "-40%", "message": "Massena's army is recovering. Effectiveness penalty: -40% The rout's disorder lingers in the ranks."}
   <event construction_complete> {"region": "Franconia", "building": "market", "message": "Construction complete: Market in Franconia!"}
   <event construction_complete> {"region": "Berlin", "building": "market", "message": "Construction complete: Market in Berlin!"}
   <event construction_complete> {"region": "Munich", "building": "market", "message": "Construction complete: Market in Munich!"}
   <event supply_attrition> {"marshal": "Soult", "nation": "France", "region": "Munich", "losses": 1064, "message": "Supply shortage at Munich: Soult loses 1,064 troops"}
   <event supply_attrition> {"marshal": "Massena", "nation": "France", "region": "Munich", "losses": 743, "message": "Supply shortage at Munich: Massena loses 743 troops"}
   <event supply_attrition> {"marshal": "Ney", "nation": "France", "region": "Nassau", "losses": 143, "message": "Supply shortage at Nassau: Ney loses 143 troops"}
   <event garrison_regen> {"region": "Milan", "nation": "Austria", "old_strength": 10000, "new_strength": 12000, "message": "Garrison at Milan reinforced: 10,000 -> 12,000"}
   <event vassal_loyalty> {"vassal": "Switzerland", "lord": "France", "nation": "France", "old_loyalty": 97, "new_loyalty": 94, "delta": -3, "reason": "satellite drift, the lord's defeats", "recovery_hint": "Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.", "message": "Switzerland loyalty 94 (-3): satellite drift, the lord's defeats \u2014 Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them."}
   <event british_subsidy> {"recipient": "Austria", "payer": "Britain", "amount": 200, "war_id": "war_1", "subsidy_source_detail": "unique_eligible", "message": "Britain subsidizes Austria with 200 gold."}
   <event sponsorship_granted> {"kind": "sponsorship", "payer": "Britain", "recipient": "Russia", "aim": "France", "amount": 200, "turns": 10, "licence": false, "turn": 3}
   <event jealousy_resolved> {"message": "Murat's grievance is satisfied \u2014 a victory against a worthy foe. He fights with renewed purpose (+10% attack this turn).", "nation": "France", "marshal": "Murat"}
   <event jealousy_fired> {"message": "Berthier reports that Lannes appears envious of Murat's laurels \u2014 he has grown impatient for something worth the doing.", "nation": "France", "marshal": "Lannes", "target": "Murat"}
   <event jealousy_escalation> {"message": "Sire, the rivalry between Lannes and Murat has become a matter of concern among the general staff. Their cooperation cannot be relied upon.", "nation": "France", "marshal": "Lannes", "target": "Murat"}
   <event jealousy_restlessness> {"message": "Berthier notes that Davout has grown restless \u2014 he has not seen laurels while Murat wins them. I recommend giving him meaningful orders soon.", "nation": "France", "marshal": "Davout"}
   <event jealousy_autonomous_warning> {"message": "Lannes is eyeing Mack's position at Frankfurt. I cannot guarantee he will wait for orders, Sire \u2014 any command would restrain him.", "nation": "France", "marshal": "Lannes"}
   <event glory_crown_lost> {"message": "Ney is no longer the army's most celebrated commander \u2014 the laurels have passed.", "nation": "France", "marshal": "Ney"}

####################################################################################################
# THE ENEMY PHASE
####################################################################################################
-- Austria --
  - ArchdukeCharles attacks Massena
      [battle] The Great Second Battle of Milan  -> attacker_tactical_victory  victor=ArchdukeCharles
        ATK ArchdukeCharles  lost   2,226  left  46,573  morale  95
        DEF Massena          lost   7,849  left  25,113  morale  22  ROUTED
        attacker order of battle: ArchdukeCharles 48,184(engaged); ArchdukeJohn 18,399(engaged)
        defender order of battle: Massena 32,962(routed); Soult 34,876(refused)
        REGION TAKEN: Milan
    [action_count] 3
[summary]
   ArchdukeCharles: attack → Massena

####################################################################################################
# THE MORNING DISPATCH
####################################################################################################
{
 "turn": 3,
 "situation": {
  "player_regions": 28,
  "enemy_regions": 98,
  "treasury": 4928,
  "treasury_delta": 2600,
  "trade_income": 425,
  "occupation": 0,
  "contributions": 0,
  "state_charges": 128,
  "requisitions": 0,
  "overseas": 0,
  "dotation_skim": 0,
  "unmet_marshals": [
   {
    "marshal": "Ney",
    "expectation": 120,
    "satisfaction": 0,
    "shortfall": 120,
    "eroding": false,
    "grace_turns_left": 1,
    "pension": 0
   },
   {
    "marshal": "Davout",
    "expectation": 160,
    "satisfaction": 0,
    "shortfall": 160,
    "eroding": false,
    "grace_turns_left": 1,
    "pension": 0
   },
   {
    "marshal": "Soult",
    "expectation": 80,
    "satisfaction": 0,
    "shortfall": 80,
    "eroding": false,
    "grace_turns_left": 1,
    "pension": 0
   },
   {
    "marshal": "Lannes",
    "expectation": 160,
    "satisfaction": 0,
    "shortfall": 160,
    "eroding": false,
    "grace_turns_left": 1,
    "pension": 0
   },
   {
    "marshal": "Murat",
    "expectation": 120,
    "satisfaction": 0,
    "shortfall": 120,
    "eroding": false,
    "grace_turns_left": 1,
    "pension": 0
   },
   {
    "marshal": "Bernadotte",
    "expectation": 80,
    "satisfaction": 0,
    "shortfall": 80,
    "eroding": false,
    "grace_turns_left": 1,
    "pension": 0
   }
  ],
  "rente_cost": 0,
  "expectation_rises": [
   {
    "marshal": "Ney",
    "expectation": 120,
    "previous": 40,
    "satisfaction": 0
   },
   {
    "marshal": "Davout",
    "expectation": 160,
    "previous": 80,
    "satisfaction": 0
   },
   {
    "marshal": "Lannes",
    "expectation": 160,
    "previous": 80,
    "satisfaction": 0
   },
   {
    "marshal": "Murat",
    "expectation": 120,
    "previous": 80,
    "satisfaction": 0
   }
  ],
  "blockade": 213,
  "admiralty": 90,
  "upkeep_surcharge": 348,
  "force_limit": 130000,
  "over_force_limit": true,
  "bankrupt": false,
  "strength_ratio_pct": 53,
  "authority": 95,
  "authority_label": "Strong"
 },
 "marshals": [
  {
   "name": "Soult",
   "location": "Munich",
   "strength": 33812,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 0,
   "danger": "Starving \u2014 supply has failed at Munich two turns running.",
   "trust": 70,
   "trust_notable": false,
   "morale": 95,
   "morale_warning": false
  },
  {
   "name": "Massena",
   "location": "Munich",
   "strength": 23606,
   "status": "retreating",
   "status_note": "Hunted by Archduke Charles across 1 frontier \u2014 stands at Munich with 23,606
  men.",
   "arc_note": "Hunted by Archduke Charles across 1 frontier \u2014 stands at Munich with 23,606
  men.",
   "idle_turns": 1,
   "danger": "Morale failing (22) \u2014 the men waver.",
   "trust": 60,
   "trust_notable": false,
   "morale": 22,
   "morale_warning": true
  },
  {
   "name": "Davout",
   "location": "Franconia",
   "strength": 23440,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 0,
   "danger": "",
   "trust": 85,
   "trust_notable": false,
   "morale": 90,
   "morale_warning": false
  },
  {
   "name": "Ney",
   "location": "Nassau",
   "strength": 21503,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 1,
   "danger": "Starving \u2014 supply has failed at Nassau two turns running.",
   "trust": 75,
   "trust_notable": false,
   "morale": 90,
   "morale_warning": false
  },
  {
   "name": "Murat",
   "location": "Swabia",
   "strength": 20193,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 0,
   "danger": "",
   "trust": 75,
   "trust_notable": false,
   "morale": 90,
   "morale_warning": false
  },
  {
   "name": "Lannes",
   "location": "Rhineland",
   "strength": 16522,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 0,
   "danger": "",
   "trust": 85,
   "trust_notable": false,
   "morale": 90,
   "morale_warning": false
  },
  {
   "name": "Bernadotte",
   "location": "Swabia",
   "strength": 15770,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 2,
   "danger": "",
   "trust": 40,
   "trust_notable": true,
   "morale": 95,
   "morale_warning": false
  }
 ],
 "intelligence": [
  {
   "name": "Archduke John",
   "location": "Milan",
   "strength_display": "17,784",
   "visibility": "full",
   "intel_turn": 2
  },
  {
   "name": "Archduke Charles",
   "location": "Bohemia",
   "strength_display": "large force",
   "visibility": "partial",
   "intel_turn": 3
  },
  {
   "name": "Brunswick",
   "location": "Berlin",
   "strength_display": "large force",
   "visibility": "partial",
   "intel_turn": 3
  },
  {
   "name": "Mack",
   "location": "Frankfurt",
   "strength_display": "small force",
   "visibility": "partial",
   "intel_turn": 3
  }
 ],
 "turn_events": [
  {
   "message": "Massena's army is recovering. Effectiveness penalty: -40% The rout's disorder lingers
  in the ranks.",
   "severity": "good"
  },
  {
   "message": "Supply shortage at Munich: Soult loses 1,064 troops",
   "severity": "warning"
  },
  {
   "message": "Supply shortage at Munich: Massena loses 743 troops",
   "severity": "warning"
  },
  {
   "message": "Supply shortage at Nassau: Ney loses 143 troops",
   "severity": "warning"
  },
  {
   "message": "Switzerland loyalty 94 (-3): satellite drift, the lord's defeats \u2014 Invest in
  them, grant them autonomy, garrison their capital, or cede them a province to steady them.",
   "severity": "warning"
  },
  {
   "message": "Murat's grievance is satisfied \u2014 a victory against a worthy foe. He fights with
  renewed purpose (+10% attack this turn).",
   "severity": "good"
  },
  {
   "message": "Berthier reports that Lannes appears envious of Murat's laurels \u2014 he has grown
  impatient for something worth the doing.",
   "severity": "warning"
  },
  {
   "message": "Sire, the rivalry between Lannes and Murat has become a matter of concern among the
  general staff. Their cooperation cannot be relied upon.",
   "severity": "warning"
  },
  {
   "message": "Berthier notes that Davout has grown restless \u2014 he has not seen laurels while
  Murat wins them. I recommend giving him meaningful orders soon.",
   "severity": "info"
  },
  {
   "message": "Lannes is eyeing Mack's position at Frankfurt. I cannot guarantee he will wait for
  orders, Sire \u2014 any command would restrain him.",
   "severity": "warning"
  },
  {
   "message": "Ney is no longer the army's most celebrated commander \u2014 the laurels have
  passed.",
   "severity": "warning"
  }
 ],
 "headline": {
  "class": "own_broken",
  "weight": 90,
  "text": "Sire \u2014 Massena's corps has been broken at Milan. He must reform before he fights
  again.",
  "sub_beats": [
   "Sire \u2014 Milan has been taken by Austria.",
   "Sire \u2014 Marshal Murat holds the field at Nassau \u2014 Mack's corps is broken and flees."
  ]
 },
 "berthier_note": "I have ordered the remnants collected, Sire. Do not commit them until they
  reform.",
 "talleyrand_report": [],
 "talleyrand_discovery": null,
 "talleyrand_override_note": null,
 "talleyrand_redemption": null,
 "coalition_status": {
  "threat_level": 82,
  "tier": "Formed",
  "sources": [
   {
    "source": "hegemony_passive",
    "amount": 1,
    "target": "France"
   },
   {
    "source": "decay",
    "amount": -3
   }
  ],
  "active_coalition": {
   "name": "Third Coalition",
   "leader": "Britain",
   "posture": "defensive",
   "formed_turn": 1,
   "members": [
    {
     "nation": "Austria",
     "war_exhaustion": 52,
     "strength_display": "69,213 men",
     "strength": 69213,
     "gold": -831
    },
    {
     "nation": "Britain",
     "war_exhaustion": 0,
     "strength_display": "Unknown",
     "strength": 0,
     "gold": 0
    },
    {
     "nation": "Russia",
     "war_exhaustion": 0,
     "strength_display": "Unknown",
     "strength": 0,
     "gold": 0
    }
   ]
  }
 },
 "diplomatic_events": [
  {
   "type": "diplomatic_dp_regen",
   "text": "Talleyrand reports: 5 diplomatic points available (base 3, +1 skill, +1 authority).",
   "priority": "LOW"
  },
  {
   "type": "paymaster_subsidy",
   "text": "Britain's gold reaches Austria \u2014 the subsidy stands at 200 this season.",
   "priority": "MEDIUM"
  }
 ],
 "pending_envoy_count": 3,
 "pending_envoys": [
  {
   "nation": "Prussia",
   "proposal_type": "open borders",
   "state": "ACTIVE"
  },
  {
   "nation": "Denmark",
   "proposal_type": "non aggression",
   "state": "WAITING"
  },
  {
   "nation": "Saxony",
   "proposal_type": "open borders",
   "state": "WAITING"
  }
 ]
}
-- POPUP/DIALOGUE [notifications] --
   [
    {
     "id": "6848bbb9-3285-45fa-9b83-7d5e119386f8",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Prussia",
     "message": "An envoy from Prussia has arrived with a proposal.",
     "turn_created": 2,
     "details": {},
     "base_title": "Envoy from Prussia",
     "repeat_count": 1
    },
    {
     "id": "859522eb-6d57-4900-a658-290f08b72a45",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Denmark",
     "message": "An envoy from Denmark has arrived with a proposal.",
     "turn_created": 2,
     "details": {},
     "base_title": "Envoy from Denmark",
     "repeat_count": 1
    },
    {
     "id": "000422e6-0264-48e0-af6b-53dfb86322d6",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Saxony",
     "message": "An envoy from Saxony has arrived with a proposal.",
     "turn_created": 2,
     "details": {},
     "base_title": "Envoy from Saxony",
     "repeat_count": 1
    },
    {
     "id": "81263869-7f7d-4ecd-a602-8659fc147e7f",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Ney expects reward",
     "message": "Marshal Ney looks for 120g/turn and holds 0g. His patience holds one more turn
     \u2014 open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an
     estate (a Duchy) or grant a rente.",
     "turn_created": 3,
     "details": {
      "marshal": "Ney",
      "expectation": 120,
      "satisfaction": 0,
      "shortfall": 120,
      "grace_turns": 2,
      "remaining_grace": 1
     },
     "base_title": "Marshal Ney expects reward",
     "repeat_count": 1
    },
    {
     "id": "d26945b6-7b37-4a96-808c-fdf5c87c70c4",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Davout expects reward",
     "message": "Marshal Davout looks for 160g/turn and holds 0g. His patience holds one more turn
     \u2014 open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an
     estate (a Duchy) or grant a rente.",
     "turn_created": 3,
     "details": {
      "marshal": "Davout",
      "expectation": 160,
      "satisfaction": 0,
      "shortfall": 160,
      "grace_turns": 2,
      "remaining_grace": 1
     },
     "base_title": "Marshal Davout expects reward",
     "repeat_count": 1
    },
    {
     "id": "97ca66f6-42b5-491d-b878-b7a22dea1ec6",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Soult expects reward",
     "message": "Marshal Soult looks for 80g/turn and holds 0g. His patience holds one more turn
     \u2014 open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an
     estate (a Duchy) or grant a rente.",
     "turn_created": 3,
     "details": {
      "marshal": "Soult",
      "expectation": 80,
      "satisfaction": 0,
      "shortfall": 80,
      "grace_turns": 2,
      "remaining_grace": 1
     },
     "base_title": "Marshal Soult expects reward",
     "repeat_count": 1
    },
    {
     "id": "22c103e8-b0dc-4a1c-a3a2-21f9e39f440b",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Lannes expects reward",
     "message": "Marshal Lannes looks for 160g/turn and holds 0g. His patience holds one more turn
     \u2014 open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an
     estate (a Duchy) or grant a rente.",
     "turn_created": 3,
     "details": {
      "marshal": "Lannes",
      "expectation": 160,
      "satisfaction": 0,
      "shortfall": 160,
      "grace_turns": 2,
      "remaining_grace": 1
     },
     "base_title": "Marshal Lannes expects reward",
     "repeat_count": 1
    },
    {
     "id": "5c64ce16-90b0-4095-9bda-5cdddd9c3daf",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Murat expects reward",
     "message": "Marshal Murat looks for 120g/turn and holds 0g. His patience holds one more turn
     \u2014 open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an
     estate (a Duchy) or grant a rente.",
     "turn_created": 3,
     "details": {
      "marshal": "Murat",
      "expectation": 120,
      "satisfaction": 0,
      "shortfall": 120,
      "grace_turns": 2,
      "remaining_grace": 1
     },
     "base_title": "Marshal Murat expects reward",
     "repeat_count": 1
    },
    {
     "id": "09c31424-cf83-

====================================================================================================
> Davout, attack Tyrol
====================================================================================================
Davout respectfully raises concerns: 'Sire, the enemy is too strong. We need reinforcements.'
-- POPUP/DIALOGUE [envoy_digest] --
   {
    "turn": 3,
    "count": 2,
    "title": "THE SMALL COURTS WRITE",
    "lapsing_count": 2,
    "headline": "Denmark and Saxony write.",
    "deadline_note": "Answer them here. Unanswered letters lapse when the turn ends, and a court
     left waiting will not raise the matter again for some seasons.",
    "items": [
     {
      "mailbox_id": 5,
      "dialogue_id": 6,
      "from_nation": "Denmark",
      "power_tier": "minor",
      "proposal_type": "non_aggression",
      "proposal_type_display": "Non-Aggression Pact",
      "diplomat_name": "Bernstorff",
      "diplomat_line": "Bernstorff, watchful and correct: \"As his sovereign has long willed,
     Denmark moves toward what the Crown desires. Sign the pact of non-aggression.\"",
      "clauses": [
       "Proposal: Non-Aggression Pact"
      ],
      "acceptance_hint": "natural willingness to negotiate",
      "state": "WAITING",
      "arrival_turn": 2
     },
     {
      "mailbox_id": 6,
      "dialogue_id": 7,
      "from_nation": "Saxony",
      "power_tier": "minor",
      "proposal_type": "friendly_gift",
      "proposal_type_display": "Open Borders Agreement",
      "diplomat_name": "Einsiedel",
      "diplomat_line": "Einsiedel, anxiously: \"Saxony has kept her house through many great reigns
     by keeping her treaties in good repair; His Majesty would merely continue the practice. Open
     the borders.\"",
      "clauses": [
       "Proposal: Open Borders Agreement",
       "Clause: Open borders",
       "Offer: Gold payment - 82"
      ],
      "acceptance_hint": "natural willingness to negotiate",
      "state": "WAITING",
      "arrival_turn": 2
     }
    ]
   }
-- POPUP/DIALOGUE [pending_objection] --
   true
-- POPUP/DIALOGUE [marshal_petition] --
   {
    "kind": "jealousy_confrontation",
    "title": "Marshal Murat seeks an audience",
    "body": "Sire, Murat has expressed... displeasure about Ney's recent recognition. He requests a
     command worthy of his talents. The staff now speak of the quarrel openly \u2014 this is no
     longer a passing mood.",
    "speaker": "Murat",
    "options": [
     {
      "id": "acknowledge",
      "label": "Acknowledge",
      "detail": "Free, and it fixes nothing: the grievance stands 3 more turns \u2014 souring his
     ties and coordination with Ney \u2014 then cools on its own.",
      "cost_note": "",
      "enabled": true
     },
     {
      "id": "promise",
      "label": "Promise Glory",
      "detail": "His patience is bought \u2014 the grievance shortens by 2 turns.",
      "cost_note": "1 AP",
      "ap_cost": 1,
      "enabled": true
     },
     {
      "id": "rebuke",
      "label": "Rebuke",
      "detail": "Trust -5. The grievance shortens by 1 turn. He will not act on his own this cycle
     \u2014 he respects the Emperor's anger, briefly.",
      "cost_note": "",
      "enabled": true
     }
    ],
    "context": {
     "marshal": "Murat",
     "target": "Ney",
     "escalation_level": 1
    },
    "turn": 1
   }
-- POPUP/DIALOGUE [notifications] --
   [
    {
     "id": "6848bbb9-3285-45fa-9b83-7d5e119386f8",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Prussia",
     "message": "An envoy from Prussia has arrived with a proposal.",
     "turn_created": 2,
     "details": {},
     "base_title": "Envoy from Prussia",
     "repeat_count": 1
    },
    {
     "id": "859522eb-6d57-4900-a658-290f08b72a45",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Denmark",
     "message": "An envoy from Denmark has arrived with a proposal.",
     "turn_created": 2,
     "details": {},
     "base_title": "Envoy from Denmark",
     "repeat_count": 1
    },
    {
     "id": "000422e6-0264-48e0-af6b-53dfb86322d6",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Saxony",
     "message": "An envoy from Saxony has arrived with a proposal.",
     "turn_created": 2,
     "details": {},
     "base_title": "Envoy from Saxony",
     "repeat_count": 1
    },
    {
     "id": "81263869-7f7d-4ecd-a602-8659fc147e7f",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Ney expects reward",
     "message": "Marshal Ney looks for 120g/turn and holds 0g. His patience holds one more turn
     \u2014 open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an
     estate (a Duchy) or grant a rente.",
     "turn_created": 3,
     "details": {
      "marshal": "Ney",
      "expectation": 120,
      "satisfaction": 0,
      "shortfall": 120,
      "grace_turns": 2,
      "remaining_grace": 1
     },
     "base_title": "Marshal Ney expects reward",
     "repeat_count": 1
    },
    {
     "id": "d26945b6-7b37-4a96-808c-fdf5c87c70c4",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Davout expects reward",
     "message": "Marshal Davout looks for 160g/turn and holds 0g. His patience holds one more turn
     \u2014 open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an
     estate (a Duchy) or grant a rente.",
     "turn_created": 3,
     "details": {
      "marshal": "Davout",
      "expectation": 160,
      "satisfaction": 0,
      "shortfall": 160,
      "grace_turns": 2,
      "remaining_grace": 1
     },
     "base_title": "Marshal Davout expects reward",
     "repeat_count": 1
    },
    {
     "id": "97ca66f6-42b5-491d-b878-b7a22dea1ec6",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Soult expects reward",
     "message": "Marshal Soult looks for 80g/turn and holds 0g. His patience holds one more turn
     \u2014 open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an
     estate (a Duchy) or grant a rente.",
     "turn_created": 3,
     "details": {
      "marshal": "Soult",
      "expectation": 80,
      "satisfaction": 0,
      "shortfall": 80,
      "grace_turns": 2,
      "remaining_grace": 1
     },
     "base_title": "Marshal Soult expects reward",
     "repeat_count": 1
    },
    {
     "id": "22c103e8-b0dc-4a1c-a3a2-21f9e39f440b",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Lannes expects reward",
     "message": "Marshal Lannes looks for 160g/turn and holds 0g. His patience holds one more turn
     \u2014 open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an
     estate (a Duchy) or grant a rente.",
     "turn_created": 3,
     "details": {
      "marshal": "Lannes",
      "expectation": 160,
      "satisfaction": 0,
      "shortfall": 160,
      "grace_turns": 2,
      "remaining_grace": 1
     },
     "base_title": "Marshal Lannes expects reward",
     "repeat_count": 1
    },
    {
     "id": "5c64ce16-90b0-4095-9bda-5cdddd9c3daf",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Murat expects reward",
     "message": "Marshal Murat looks for 120g/turn and holds 0g. His patience holds one more turn
     \u2014 open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an
     estate (a Duchy) or grant a rente.",
     "turn_created": 3,
     "details": {
      "marshal": "Murat",
      "expectation": 120,
      "satisfaction": 0,
      "shortfall": 120,
      "grace_turns": 2,
      "remaining_grace": 1
     },
     "base_title": "Marshal Murat expects reward",
     "repeat_count": 1
    },
    {
     "id": "09c31424-cf83-

====================================================================================================
> Ney, march on Bohemia
====================================================================================================
Davout awaits your answer, Sire — settle the objection before issuing new orders.
-- POPUP/DIALOGUE [envoy_digest] --
   {
    "turn": 3,
    "count": 2,
    "title": "THE SMALL COURTS WRITE",
    "lapsing_count": 2,
    "headline": "Denmark and Saxony write.",
    "deadline_note": "Answer them here. Unanswered letters lapse when the turn ends, and a court
     left waiting will not raise the matter again for some seasons.",
    "items": [
     {
      "mailbox_id": 5,
      "dialogue_id": 6,
      "from_nation": "Denmark",
      "power_tier": "minor",
      "proposal_type": "non_aggression",
      "proposal_type_display": "Non-Aggression Pact",
      "diplomat_name": "Bernstorff",
      "diplomat_line": "Bernstorff, watchful and correct: \"As his sovereign has long willed,
     Denmark moves toward what the Crown desires. Sign the pact of non-aggression.\"",
      "clauses": [
       "Proposal: Non-Aggression Pact"
      ],
      "acceptance_hint": "natural willingness to negotiate",
      "state": "WAITING",
      "arrival_turn": 2
     },
     {
      "mailbox_id": 6,
      "dialogue_id": 7,
      "from_nation": "Saxony",
      "power_tier": "minor",
      "proposal_type": "friendly_gift",
      "proposal_type_display": "Open Borders Agreement",
      "diplomat_name": "Einsiedel",
      "diplomat_line": "Einsiedel, anxiously: \"Saxony has kept her house through many great reigns
     by keeping her treaties in good repair; His Majesty would merely continue the practice. Open
     the borders.\"",
      "clauses": [
       "Proposal: Open Borders Agreement",
       "Clause: Open borders",
       "Offer: Gold payment - 82"
      ],
      "acceptance_hint": "natural willingness to negotiate",
      "state": "WAITING",
      "arrival_turn": 2
     }
    ]
   }
-- POPUP/DIALOGUE [incoming_proposal] --
   {
    "from_nation": "Prussia",
    "diplomat_name": "Hardenberg",
    "diplomat_personality": "hawk",
    "proposal_type": "open_borders",
    "proposal_type_display": "Open Borders Agreement",
    "clauses": [
     "Proposal: Open Borders Agreement",
     "Clause: Open borders"
    ],
    "talleyrand_assessment": "An unexpected overture. There may be hidden motives worth examining.",
    "acceptance_hint": "natural willingness to negotiate",
    "rejection_hint": "their diplomat outmaneuvered us",
    "is_counter_offer": false,
    "decision_reason": "hegemony_pressure",
    "decision_reason_display": "hegemony pressure",
    "diplomat_line": "Hardenberg, stiffly: \"Berlin will not pretend otherwise: France stands too
     near the Rhine. Prussia would fix that line in ink before she fixes it in blood. Open the
     borders.\"",
    "dialogue_id": 5
   }
-- POPUP/DIALOGUE [notifications] --
   [
    {
     "id": "6848bbb9-3285-45fa-9b83-7d5e119386f8",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Prussia",
     "message": "An envoy from Prussia has arrived with a proposal.",
     "turn_created": 2,
     "details": {},
     "base_title": "Envoy from Prussia",
     "repeat_count": 1
    },
    {
     "id": "859522eb-6d57-4900-a658-290f08b72a45",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Denmark",
     "message": "An envoy from Denmark has arrived with a proposal.",
     "turn_created": 2,
     "details": {},
     "base_title": "Envoy from Denmark",
     "repeat_count": 1
    },
    {
     "id": "000422e6-0264-48e0-af6b-53dfb86322d6",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Saxony",
     "message": "An envoy from Saxony has arrived with a proposal.",
     "turn_created": 2,
     "details": {},
     "base_title": "Envoy from Saxony",
     "repeat_count": 1
    },
    {
     "id": "81263869-7f7d-4ecd-a602-8659fc147e7f",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Ney expects reward",
     "message": "Marshal Ney looks for 120g/turn and holds 0g. His patience holds one more turn
     \u2014 open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an
     estate (a Duchy) or grant a rente.",
     "turn_created": 3,
     "details": {
      "marshal": "Ney",
      "expectation": 120,
      "satisfaction": 0,
      "shortfall": 120,
      "grace_turns": 2,
      "remaining_grace": 1
     },
     "base_title": "Marshal Ney expects reward",
     "repeat_count": 1
    },
    {
     "id": "d26945b6-7b37-4a96-808c-fdf5c87c70c4",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Davout expects reward",
     "message": "Marshal Davout looks for 160g/turn and holds 0g. His patience holds one more turn
     \u2014 open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an
     estate (a Duchy) or grant a rente.",
     "turn_created": 3,
     "details": {
      "marshal": "Davout",
      "expectation": 160,
      "satisfaction": 0,
      "shortfall": 160,
      "grace_turns": 2,
      "remaining_grace": 1
     },
     "base_title": "Marshal Davout expects reward",
     "repeat_count": 1
    },
    {
     "id": "97ca66f6-42b5-491d-b878-b7a22dea1ec6",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Soult expects reward",
     "message": "Marshal Soult looks for 80g/turn and holds 0g. His patience holds one more turn
     \u2014 open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an
     estate (a Duchy) or grant a rente.",
     "turn_created": 3,
     "details": {
      "marshal": "Soult",
      "expectation": 80,
      "satisfaction": 0,
      "shortfall": 80,
      "grace_turns": 2,
      "remaining_grace": 1
     },
     "base_title": "Marshal Soult expects reward",
     "repeat_count": 1
    },
    {
     "id": "22c103e8-b0dc-4a1c-a3a2-21f9e39f440b",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Lannes expects reward",
     "message": "Marshal Lannes looks for 160g/turn and holds 0g. His patience holds one more turn
     \u2014 open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an
     estate (a Duchy) or grant a rente.",
     "turn_created": 3,
     "details": {
      "marshal": "Lannes",
      "expectation": 160,
      "satisfaction": 0,
      "shortfall": 160,
      "grace_turns": 2,
      "remaining_grace": 1
     },
     "base_title": "Marshal Lannes expects reward",
     "repeat_count": 1
    },
    {
     "id": "5c64ce16-90b0-4095-9bda-5cdddd9c3daf",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Murat expects reward",
     "message": "Marshal Murat looks for 120g/turn and holds 0g. His patience holds one more turn
     \u2014 open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an
     estate (a Duchy) or grant a rente.",
     "turn_created": 3,
     "details": {
      "marshal": "Murat",
      "expectation": 120,
      "satisfaction": 0,
      "shortfall": 120,
      "grace_turns": 2,
      "remaining_grace": 1
     },
     "base_title": "Marshal Murat expects reward",
     "repeat_count": 1
    },
    {
     "id": "09c31424-cf83-

====================================================================================================
> status
====================================================================================================
Davout awaits your answer, Sire — settle the objection before issuing new orders.
-- POPUP/DIALOGUE [envoy_digest] --
   {
    "turn": 3,
    "count": 2,
    "title": "THE SMALL COURTS WRITE",
    "lapsing_count": 2,
    "headline": "Denmark and Saxony write.",
    "deadline_note": "Answer them here. Unanswered letters lapse when the turn ends, and a court
     left waiting will not raise the matter again for some seasons.",
    "items": [
     {
      "mailbox_id": 5,
      "dialogue_id": 6,
      "from_nation": "Denmark",
      "power_tier": "minor",
      "proposal_type": "non_aggression",
      "proposal_type_display": "Non-Aggression Pact",
      "diplomat_name": "Bernstorff",
      "diplomat_line": "Bernstorff, watchful and correct: \"As his sovereign has long willed,
     Denmark moves toward what the Crown desires. Sign the pact of non-aggression.\"",
      "clauses": [
       "Proposal: Non-Aggression Pact"
      ],
      "acceptance_hint": "natural willingness to negotiate",
      "state": "WAITING",
      "arrival_turn": 2
     },
     {
      "mailbox_id": 6,
      "dialogue_id": 7,
      "from_nation": "Saxony",
      "power_tier": "minor",
      "proposal_type": "friendly_gift",
      "proposal_type_display": "Open Borders Agreement",
      "diplomat_name": "Einsiedel",
      "diplomat_line": "Einsiedel, anxiously: \"Saxony has kept her house through many great reigns
     by keeping her treaties in good repair; His Majesty would merely continue the practice. Open
     the borders.\"",
      "clauses": [
       "Proposal: Open Borders Agreement",
       "Clause: Open borders",
       "Offer: Gold payment - 82"
      ],
      "acceptance_hint": "natural willingness to negotiate",
      "state": "WAITING",
      "arrival_turn": 2
     }
    ]
   }
-- POPUP/DIALOGUE [incoming_proposal] --
   {
    "from_nation": "Prussia",
    "diplomat_name": "Hardenberg",
    "diplomat_personality": "hawk",
    "proposal_type": "open_borders",
    "proposal_type_display": "Open Borders Agreement",
    "clauses": [
     "Proposal: Open Borders Agreement",
     "Clause: Open borders"
    ],
    "talleyrand_assessment": "An unexpected overture. There may be hidden motives worth examining.",
    "acceptance_hint": "natural willingness to negotiate",
    "rejection_hint": "their diplomat outmaneuvered us",
    "is_counter_offer": false,
    "decision_reason": "hegemony_pressure",
    "decision_reason_display": "hegemony pressure",
    "diplomat_line": "Hardenberg, stiffly: \"Berlin will not pretend otherwise: France stands too
     near the Rhine. Prussia would fix that line in ink before she fixes it in blood. Open the
     borders.\"",
    "dialogue_id": 5
   }
-- POPUP/DIALOGUE [notifications] --
   [
    {
     "id": "6848bbb9-3285-45fa-9b83-7d5e119386f8",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Prussia",
     "message": "An envoy from Prussia has arrived with a proposal.",
     "turn_created": 2,
     "details": {},
     "base_title": "Envoy from Prussia",
     "repeat_count": 1
    },
    {
     "id": "859522eb-6d57-4900-a658-290f08b72a45",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Denmark",
     "message": "An envoy from Denmark has arrived with a proposal.",
     "turn_created": 2,
     "details": {},
     "base_title": "Envoy from Denmark",
     "repeat_count": 1
    },
    {
     "id": "000422e6-0264-48e0-af6b-53dfb86322d6",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Saxony",
     "message": "An envoy from Saxony has arrived with a proposal.",
     "turn_created": 2,
     "details": {},
     "base_title": "Envoy from Saxony",
     "repeat_count": 1
    },
    {
     "id": "81263869-7f7d-4ecd-a602-8659fc147e7f",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Ney expects reward",
     "message": "Marshal Ney looks for 120g/turn and holds 0g. His patience holds one more turn
     \u2014 open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an
     estate (a Duchy) or grant a rente.",
     "turn_created": 3,
     "details": {
      "marshal": "Ney",
      "expectation": 120,
      "satisfaction": 0,
      "shortfall": 120,
      "grace_turns": 2,
      "remaining_grace": 1
     },
     "base_title": "Marshal Ney expects reward",
     "repeat_count": 1
    },
    {
     "id": "d26945b6-7b37-4a96-808c-fdf5c87c70c4",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Davout expects reward",
     "message": "Marshal Davout looks for 160g/turn and holds 0g. His patience holds one more turn
     \u2014 open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an
     estate (a Duchy) or grant a rente.",
     "turn_created": 3,
     "details": {
      "marshal": "Davout",
      "expectation": 160,
      "satisfaction": 0,
      "shortfall": 160,
      "grace_turns": 2,
      "remaining_grace": 1
     },
     "base_title": "Marshal Davout expects reward",
     "repeat_count": 1
    },
    {
     "id": "97ca66f6-42b5-491d-b878-b7a22dea1ec6",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Soult expects reward",
     "message": "Marshal Soult looks for 80g/turn and holds 0g. His patience holds one more turn
     \u2014 open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an
     estate (a Duchy) or grant a rente.",
     "turn_created": 3,
     "details": {
      "marshal": "Soult",
      "expectation": 80,
      "satisfaction": 0,
      "shortfall": 80,
      "grace_turns": 2,
      "remaining_grace": 1
     },
     "base_title": "Marshal Soult expects reward",
     "repeat_count": 1
    },
    {
     "id": "22c103e8-b0dc-4a1c-a3a2-21f9e39f440b",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Lannes expects reward",
     "message": "Marshal Lannes looks for 160g/turn and holds 0g. His patience holds one more turn
     \u2014 open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an
     estate (a Duchy) or grant a rente.",
     "turn_created": 3,
     "details": {
      "marshal": "Lannes",
      "expectation": 160,
      "satisfaction": 0,
      "shortfall": 160,
      "grace_turns": 2,
      "remaining_grace": 1
     },
     "base_title": "Marshal Lannes expects reward",
     "repeat_count": 1
    },
    {
     "id": "5c64ce16-90b0-4095-9bda-5cdddd9c3daf",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Murat expects reward",
     "message": "Marshal Murat looks for 120g/turn and holds 0g. His patience holds one more turn
     \u2014 open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an
     estate (a Duchy) or grant a rente.",
     "turn_created": 3,
     "details": {
      "marshal": "Murat",
      "expectation": 120,
      "satisfaction": 0,
      "shortfall": 120,
      "grace_turns": 2,
      "remaining_grace": 1
     },
     "base_title": "Marshal Murat expects reward",
     "repeat_count": 1
    },
    {
     "id": "09c31424-cf83-

====================================================================================================
> Davout is right, cancel that attack
====================================================================================================
Davout awaits your answer, Sire — settle the objection before issuing new orders.
-- POPUP/DIALOGUE [envoy_digest] --
   {
    "turn": 3,
    "count": 2,
    "title": "THE SMALL COURTS WRITE",
    "lapsing_count": 2,
    "headline": "Denmark and Saxony write.",
    "deadline_note": "Answer them here. Unanswered letters lapse when the turn ends, and a court
     left waiting will not raise the matter again for some seasons.",
    "items": [
     {
      "mailbox_id": 5,
      "dialogue_id": 6,
      "from_nation": "Denmark",
      "power_tier": "minor",
      "proposal_type": "non_aggression",
      "proposal_type_display": "Non-Aggression Pact",
      "diplomat_name": "Bernstorff",
      "diplomat_line": "Bernstorff, watchful and correct: \"As his sovereign has long willed,
     Denmark moves toward what the Crown desires. Sign the pact of non-aggression.\"",
      "clauses": [
       "Proposal: Non-Aggression Pact"
      ],
      "acceptance_hint": "natural willingness to negotiate",
      "state": "WAITING",
      "arrival_turn": 2
     },
     {
      "mailbox_id": 6,
      "dialogue_id": 7,
      "from_nation": "Saxony",
      "power_tier": "minor",
      "proposal_type": "friendly_gift",
      "proposal_type_display": "Open Borders Agreement",
      "diplomat_name": "Einsiedel",
      "diplomat_line": "Einsiedel, anxiously: \"Saxony has kept her house through many great reigns
     by keeping her treaties in good repair; His Majesty would merely continue the practice. Open
     the borders.\"",
      "clauses": [
       "Proposal: Open Borders Agreement",
       "Clause: Open borders",
       "Offer: Gold payment - 82"
      ],
      "acceptance_hint": "natural willingness to negotiate",
      "state": "WAITING",
      "arrival_turn": 2
     }
    ]
   }
-- POPUP/DIALOGUE [incoming_proposal] --
   {
    "from_nation": "Prussia",
    "diplomat_name": "Hardenberg",
    "diplomat_personality": "hawk",
    "proposal_type": "open_borders",
    "proposal_type_display": "Open Borders Agreement",
    "clauses": [
     "Proposal: Open Borders Agreement",
     "Clause: Open borders"
    ],
    "talleyrand_assessment": "An unexpected overture. There may be hidden motives worth examining.",
    "acceptance_hint": "natural willingness to negotiate",
    "rejection_hint": "their diplomat outmaneuvered us",
    "is_counter_offer": false,
    "decision_reason": "hegemony_pressure",
    "decision_reason_display": "hegemony pressure",
    "diplomat_line": "Hardenberg, stiffly: \"Berlin will not pretend otherwise: France stands too
     near the Rhine. Prussia would fix that line in ink before she fixes it in blood. Open the
     borders.\"",
    "dialogue_id": 5
   }
-- POPUP/DIALOGUE [notifications] --
   [
    {
     "id": "6848bbb9-3285-45fa-9b83-7d5e119386f8",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Prussia",
     "message": "An envoy from Prussia has arrived with a proposal.",
     "turn_created": 2,
     "details": {},
     "base_title": "Envoy from Prussia",
     "repeat_count": 1
    },
    {
     "id": "859522eb-6d57-4900-a658-290f08b72a45",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Denmark",
     "message": "An envoy from Denmark has arrived with a proposal.",
     "turn_created": 2,
     "details": {},
     "base_title": "Envoy from Denmark",
     "repeat_count": 1
    },
    {
     "id": "000422e6-0264-48e0-af6b-53dfb86322d6",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Saxony",
     "message": "An envoy from Saxony has arrived with a proposal.",
     "turn_created": 2,
     "details": {},
     "base_title": "Envoy from Saxony",
     "repeat_count": 1
    },
    {
     "id": "81263869-7f7d-4ecd-a602-8659fc147e7f",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Ney expects reward",
     "message": "Marshal Ney looks for 120g/turn and holds 0g. His patience holds one more turn
     \u2014 open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an
     estate (a Duchy) or grant a rente.",
     "turn_created": 3,
     "details": {
      "marshal": "Ney",
      "expectation": 120,
      "satisfaction": 0,
      "shortfall": 120,
      "grace_turns": 2,
      "remaining_grace": 1
     },
     "base_title": "Marshal Ney expects reward",
     "repeat_count": 1
    },
    {
     "id": "d26945b6-7b37-4a96-808c-fdf5c87c70c4",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Davout expects reward",
     "message": "Marshal Davout looks for 160g/turn and holds 0g. His patience holds one more turn
     \u2014 open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an
     estate (a Duchy) or grant a rente.",
     "turn_created": 3,
     "details": {
      "marshal": "Davout",
      "expectation": 160,
      "satisfaction": 0,
      "shortfall": 160,
      "grace_turns": 2,
      "remaining_grace": 1
     },
     "base_title": "Marshal Davout expects reward",
     "repeat_count": 1
    },
    {
     "id": "97ca66f6-42b5-491d-b878-b7a22dea1ec6",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Soult expects reward",
     "message": "Marshal Soult looks for 80g/turn and holds 0g. His patience holds one more turn
     \u2014 open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an
     estate (a Duchy) or grant a rente.",
     "turn_created": 3,
     "details": {
      "marshal": "Soult",
      "expectation": 80,
      "satisfaction": 0,
      "shortfall": 80,
      "grace_turns": 2,
      "remaining_grace": 1
     },
     "base_title": "Marshal Soult expects reward",
     "repeat_count": 1
    },
    {
     "id": "22c103e8-b0dc-4a1c-a3a2-21f9e39f440b",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Lannes expects reward",
     "message": "Marshal Lannes looks for 160g/turn and holds 0g. His patience holds one more turn
     \u2014 open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an
     estate (a Duchy) or grant a rente.",
     "turn_created": 3,
     "details": {
      "marshal": "Lannes",
      "expectation": 160,
      "satisfaction": 0,
      "shortfall": 160,
      "grace_turns": 2,
      "remaining_grace": 1
     },
     "base_title": "Marshal Lannes expects reward",
     "repeat_count": 1
    },
    {
     "id": "5c64ce16-90b0-4095-9bda-5cdddd9c3daf",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Murat expects reward",
     "message": "Marshal Murat looks for 120g/turn and holds 0g. His patience holds one more turn
     \u2014 open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an
     estate (a Duchy) or grant a rente.",
     "turn_created": 3,
     "details": {
      "marshal": "Murat",
      "expectation": 120,
      "satisfaction": 0,
      "shortfall": 120,
      "grace_turns": 2,
      "remaining_grace": 1
     },
     "base_title": "Marshal Murat expects reward",
     "repeat_count": 1
    },
    {
     "id": "09c31424-cf83-

====================================================================================================
> trust
====================================================================================================
You defer to Davout's judgment.

Davout executes their alternative plan.

Davout shifts from NEUTRAL to DEFENSIVE stance. Effect: -10% attack, +15% defense.
   [cost=1  turn_advanced=False]
   <event stance_change> {"marshal": "Davout", "from_stance": "neutral", "to_stance": "defensive", "action_cost": 1}
-- POPUP/DIALOGUE [envoy_digest] --
   {
    "turn": 3,
    "count": 2,
    "title": "THE SMALL COURTS WRITE",
    "lapsing_count": 2,
    "headline": "Denmark and Saxony write.",
    "deadline_note": "Answer them here. Unanswered letters lapse when the turn ends, and a court
     left waiting will not raise the matter again for some seasons.",
    "items": [
     {
      "mailbox_id": 5,
      "dialogue_id": 6,
      "from_nation": "Denmark",
      "power_tier": "minor",
      "proposal_type": "non_aggression",
      "proposal_type_display": "Non-Aggression Pact",
      "diplomat_name": "Bernstorff",
      "diplomat_line": "Bernstorff, watchful and correct: \"As his sovereign has long willed,
     Denmark moves toward what the Crown desires. Sign the pact of non-aggression.\"",
      "clauses": [
       "Proposal: Non-Aggression Pact"
      ],
      "acceptance_hint": "natural willingness to negotiate",
      "state": "WAITING",
      "arrival_turn": 2
     },
     {
      "mailbox_id": 6,
      "dialogue_id": 7,
      "from_nation": "Saxony",
      "power_tier": "minor",
      "proposal_type": "friendly_gift",
      "proposal_type_display": "Open Borders Agreement",
      "diplomat_name": "Einsiedel",
      "diplomat_line": "Einsiedel, anxiously: \"Saxony has kept her house through many great reigns
     by keeping her treaties in good repair; His Majesty would merely continue the practice. Open
     the borders.\"",
      "clauses": [
       "Proposal: Open Borders Agreement",
       "Clause: Open borders",
       "Offer: Gold payment - 82"
      ],
      "acceptance_hint": "natural willingness to negotiate",
      "state": "WAITING",
      "arrival_turn": 2
     }
    ]
   }
-- POPUP/DIALOGUE [incoming_proposal] --
   {
    "from_nation": "Prussia",
    "diplomat_name": "Hardenberg",
    "diplomat_personality": "hawk",
    "proposal_type": "open_borders",
    "proposal_type_display": "Open Borders Agreement",
    "clauses": [
     "Proposal: Open Borders Agreement",
     "Clause: Open borders"
    ],
    "talleyrand_assessment": "An unexpected overture. There may be hidden motives worth examining.",
    "acceptance_hint": "natural willingness to negotiate",
    "rejection_hint": "their diplomat outmaneuvered us",
    "is_counter_offer": false,
    "decision_reason": "hegemony_pressure",
    "decision_reason_display": "hegemony pressure",
    "diplomat_line": "Hardenberg, stiffly: \"Berlin will not pretend otherwise: France stands too
     near the Rhine. Prussia would fix that line in ink before she fixes it in blood. Open the
     borders.\"",
    "dialogue_id": 5
   }
-- POPUP/DIALOGUE [notifications] --
   [
    {
     "id": "6848bbb9-3285-45fa-9b83-7d5e119386f8",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Prussia",
     "message": "An envoy from Prussia has arrived with a proposal.",
     "turn_created": 2,
     "details": {},
     "base_title": "Envoy from Prussia",
     "repeat_count": 1
    },
    {
     "id": "859522eb-6d57-4900-a658-290f08b72a45",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Denmark",
     "message": "An envoy from Denmark has arrived with a proposal.",
     "turn_created": 2,
     "details": {},
     "base_title": "Envoy from Denmark",
     "repeat_count": 1
    },
    {
     "id": "000422e6-0264-48e0-af6b-53dfb86322d6",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Saxony",
     "message": "An envoy from Saxony has arrived with a proposal.",
     "turn_created": 2,
     "details": {},
     "base_title": "Envoy from Saxony",
     "repeat_count": 1
    },
    {
     "id": "81263869-7f7d-4ecd-a602-8659fc147e7f",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Ney expects reward",
     "message": "Marshal Ney looks for 120g/turn and holds 0g. His patience holds one more turn
     \u2014 open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an
     estate (a Duchy) or grant a rente.",
     "turn_created": 3,
     "details": {
      "marshal": "Ney",
      "expectation": 120,
      "satisfaction": 0,
      "shortfall": 120,
      "grace_turns": 2,
      "remaining_grace": 1
     },
     "base_title": "Marshal Ney expects reward",
     "repeat_count": 1
    },
    {
     "id": "d26945b6-7b37-4a96-808c-fdf5c87c70c4",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Davout expects reward",
     "message": "Marshal Davout looks for 160g/turn and holds 0g. His patience holds one more turn
     \u2014 open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an
     estate (a Duchy) or grant a rente.",
     "turn_created": 3,
     "details": {
      "marshal": "Davout",
      "expectation": 160,
      "satisfaction": 0,
      "shortfall": 160,
      "grace_turns": 2,
      "remaining_grace": 1
     },
     "base_title": "Marshal Davout expects reward",
     "repeat_count": 1
    },
    {
     "id": "97ca66f6-42b5-491d-b878-b7a22dea1ec6",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Soult expects reward",
     "message": "Marshal Soult looks for 80g/turn and holds 0g. His patience holds one more turn
     \u2014 open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an
     estate (a Duchy) or grant a rente.",
     "turn_created": 3,
     "details": {
      "marshal": "Soult",
      "expectation": 80,
      "satisfaction": 0,
      "shortfall": 80,
      "grace_turns": 2,
      "remaining_grace": 1
     },
     "base_title": "Marshal Soult expects reward",
     "repeat_count": 1
    },
    {
     "id": "22c103e8-b0dc-4a1c-a3a2-21f9e39f440b",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Lannes expects reward",
     "message": "Marshal Lannes looks for 160g/turn and holds 0g. His patience holds one more turn
     \u2014 open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an
     estate (a Duchy) or grant a rente.",
     "turn_created": 3,
     "details": {
      "marshal": "Lannes",
      "expectation": 160,
      "satisfaction": 0,
      "shortfall": 160,
      "grace_turns": 2,
      "remaining_grace": 1
     },
     "base_title": "Marshal Lannes expects reward",
     "repeat_count": 1
    },
    {
     "id": "5c64ce16-90b0-4095-9bda-5cdddd9c3daf",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Murat expects reward",
     "message": "Marshal Murat looks for 120g/turn and holds 0g. His patience holds one more turn
     \u2014 open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an
     estate (a Duchy) or grant a rente.",
     "turn_created": 3,
     "details": {
      "marshal": "Murat",
      "expectation": 120,
      "satisfaction": 0,
      "shortfall": 120,
      "grace_turns": 2,
      "remaining_grace": 1
     },
     "base_title": "Marshal Murat expects reward",
     "repeat_count": 1
    },
    {
     "id": "09c31424-cf83-

====================================================================================================
> reject Prussia's proposal
====================================================================================================
You have rejected Prussia's proposal. Talleyrand will convey your decision.
-- POPUP/DIALOGUE [notifications] --
   [
    {
     "id": "81263869-7f7d-4ecd-a602-8659fc147e7f",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Ney expects reward",
     "message": "Marshal Ney looks for 120g/turn and holds 0g. His patience holds one more turn
     \u2014 open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an
     estate (a Duchy) or grant a rente.",
     "turn_created": 3,
     "details": {
      "marshal": "Ney",
      "expectation": 120,
      "satisfaction": 0,
      "shortfall": 120,
      "grace_turns": 2,
      "remaining_grace": 1
     },
     "base_title": "Marshal Ney expects reward",
     "repeat_count": 1
    },
    {
     "id": "d26945b6-7b37-4a96-808c-fdf5c87c70c4",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Davout expects reward",
     "message": "Marshal Davout looks for 160g/turn and holds 0g. His patience holds one more turn
     \u2014 open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an
     estate (a Duchy) or grant a rente.",
     "turn_created": 3,
     "details": {
      "marshal": "Davout",
      "expectation": 160,
      "satisfaction": 0,
      "shortfall": 160,
      "grace_turns": 2,
      "remaining_grace": 1
     },
     "base_title": "Marshal Davout expects reward",
     "repeat_count": 1
    },
    {
     "id": "97ca66f6-42b5-491d-b878-b7a22dea1ec6",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Soult expects reward",
     "message": "Marshal Soult looks for 80g/turn and holds 0g. His patience holds one more turn
     \u2014 open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an
     estate (a Duchy) or grant a rente.",
     "turn_created": 3,
     "details": {
      "marshal": "Soult",
      "expectation": 80,
      "satisfaction": 0,
      "shortfall": 80,
      "grace_turns": 2,
      "remaining_grace": 1
     },
     "base_title": "Marshal Soult expects reward",
     "repeat_count": 1
    },
    {
     "id": "22c103e8-b0dc-4a1c-a3a2-21f9e39f440b",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Lannes expects reward",
     "message": "Marshal Lannes looks for 160g/turn and holds 0g. His patience holds one more turn
     \u2014 open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an
     estate (a Duchy) or grant a rente.",
     "turn_created": 3,
     "details": {
      "marshal": "Lannes",
      "expectation": 160,
      "satisfaction": 0,
      "shortfall": 160,
      "grace_turns": 2,
      "remaining_grace": 1
     },
     "base_title": "Marshal Lannes expects reward",
     "repeat_count": 1
    },
    {
     "id": "5c64ce16-90b0-4095-9bda-5cdddd9c3daf",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Murat expects reward",
     "message": "Marshal Murat looks for 120g/turn and holds 0g. His patience holds one more turn
     \u2014 open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an
     estate (a Duchy) or grant a rente.",
     "turn_created": 3,
     "details": {
      "marshal": "Murat",
      "expectation": 120,
      "satisfaction": 0,
      "shortfall": 120,
      "grace_turns": 2,
      "remaining_grace": 1
     },
     "base_title": "Marshal Murat expects reward",
     "repeat_count": 1
    },
    {
     "id": "09c31424-cf83-4d0e-ba9b-51b26231cf8a",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Bernadotte expects reward",
     "message": "Marshal Bernadotte looks for 80g/turn and holds 0g. His patience holds one more
     turn \u2014 open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an
     estate (a Duchy) or grant a rente.",
     "turn_created": 3,
     "details": {
      "marshal": "Bernadotte",
      "expectation": 80,
      "satisfaction": 0,
      "shortfall": 80,
      "grace_turns": 2,
      "remaining_grace": 1
     },
     "base_title": "Marshal Bernadotte expects reward",
     "repeat_count": 1
    },
    {
     "id": "1afb790e-a88d-4bc0-b0ae-fae2fb9b451e",
     "type": "treaty_signed",
     "priority": 0,
     "title": "Treaty with Denmark",
     "message": "Denmark and France have signed a Non-Aggression Pact.",
     "turn_created": 3,
     "details": {
      "counterpart": "Denmark"
     },
     "base_title": "Treaty wi

====================================================================================================
> Ney, march on Bohemia
====================================================================================================
Ney begins march to Bohemia. Route: Franconia -> Bohemia. Moves to Franconia. Ney: "Good. An army
  rots standing still."
   [cost=1  turn_advanced=False]
-- POPUP/DIALOGUE [notifications] --
   [
    {
     "id": "81263869-7f7d-4ecd-a602-8659fc147e7f",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Ney expects reward",
     "message": "Marshal Ney looks for 120g/turn and holds 0g. His patience holds one more turn
     \u2014 open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an
     estate (a Duchy) or grant a rente.",
     "turn_created": 3,
     "details": {
      "marshal": "Ney",
      "expectation": 120,
      "satisfaction": 0,
      "shortfall": 120,
      "grace_turns": 2,
      "remaining_grace": 1
     },
     "base_title": "Marshal Ney expects reward",
     "repeat_count": 1
    },
    {
     "id": "d26945b6-7b37-4a96-808c-fdf5c87c70c4",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Davout expects reward",
     "message": "Marshal Davout looks for 160g/turn and holds 0g. His patience holds one more turn
     \u2014 open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an
     estate (a Duchy) or grant a rente.",
     "turn_created": 3,
     "details": {
      "marshal": "Davout",
      "expectation": 160,
      "satisfaction": 0,
      "shortfall": 160,
      "grace_turns": 2,
      "remaining_grace": 1
     },
     "base_title": "Marshal Davout expects reward",
     "repeat_count": 1
    },
    {
     "id": "97ca66f6-42b5-491d-b878-b7a22dea1ec6",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Soult expects reward",
     "message": "Marshal Soult looks for 80g/turn and holds 0g. His patience holds one more turn
     \u2014 open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an
     estate (a Duchy) or grant a rente.",
     "turn_created": 3,
     "details": {
      "marshal": "Soult",
      "expectation": 80,
      "satisfaction": 0,
      "shortfall": 80,
      "grace_turns": 2,
      "remaining_grace": 1
     },
     "base_title": "Marshal Soult expects reward",
     "repeat_count": 1
    },
    {
     "id": "22c103e8-b0dc-4a1c-a3a2-21f9e39f440b",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Lannes expects reward",
     "message": "Marshal Lannes looks for 160g/turn and holds 0g. His patience holds one more turn
     \u2014 open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an
     estate (a Duchy) or grant a rente.",
     "turn_created": 3,
     "details": {
      "marshal": "Lannes",
      "expectation": 160,
      "satisfaction": 0,
      "shortfall": 160,
      "grace_turns": 2,
      "remaining_grace": 1
     },
     "base_title": "Marshal Lannes expects reward",
     "repeat_count": 1
    },
    {
     "id": "5c64ce16-90b0-4095-9bda-5cdddd9c3daf",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Murat expects reward",
     "message": "Marshal Murat looks for 120g/turn and holds 0g. His patience holds one more turn
     \u2014 open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an
     estate (a Duchy) or grant a rente.",
     "turn_created": 3,
     "details": {
      "marshal": "Murat",
      "expectation": 120,
      "satisfaction": 0,
      "shortfall": 120,
      "grace_turns": 2,
      "remaining_grace": 1
     },
     "base_title": "Marshal Murat expects reward",
     "repeat_count": 1
    },
    {
     "id": "09c31424-cf83-4d0e-ba9b-51b26231cf8a",
     "type": "dotation_expectation",
     "priority": 0,
     "title": "Marshal Bernadotte expects reward",
     "message": "Marshal Bernadotte looks for 80g/turn and holds 0g. His patience holds one more
     turn \u2014 open the Generals screen (press G) and use [ Reward\u2026 ] on his card to endow an
     estate (a Duchy) or grant a rente.",
     "turn_created": 3,
     "details": {
      "marshal": "Bernadotte",
      "expectation": 80,
      "satisfaction": 0,
      "shortfall": 80,
      "grace_turns": 2,
      "remaining_grace": 1
     },
     "base_title": "Marshal Bernadotte expects reward",
     "repeat_count": 1
    },
    {
     "id": "1afb790e-a88d-4bc0-b0ae-fae2fb9b451e",
     "type": "treaty_signed",
     "priority": 0,
     "title": "Treaty with Denmark",
     "message": "Denmark and France have signed a Non-Aggression Pact.",
     "turn_created": 3,
     "details": {
      "counterpart": "Denmark"
     },
     "base_title": "Treaty wi

====================================================================================================
> end turn
====================================================================================================
Turn 3 ended. Turn 4 begins!

Income: 3400g | Charges of Empire: -140g | Admiralty: -90g | Blockade: -250g | Upkeep: 1376g (incl.
  72g over-limit, 144g Grande Armée) | Other: +1224g | Net: +2768g | Treasury: 7,778g
   [cost=0  turn_advanced=False]
   <event retreat_recovery> {"marshal": "Massena", "nation": "France", "stage": 2, "penalty": "-25%", "message": "Massena's army is recovering. Effectiveness penalty: -25% The rout's disorder lingers in the ranks."}
   <event construction_complete> {"region": "Swabia", "building": "market", "message": "Construction complete: Market in Swabia!"}
   <event supply_attrition> {"marshal": "Mack", "nation": "Austria", "region": "Berlin", "losses": 21, "message": "Supply shortage at Berlin: Mack loses 21 troops"}
   <event supply_attrition> {"marshal": "Soult", "nation": "France", "region": "Munich", "losses": 2008, "message": "Supply shortage at Munich: Soult loses 2,008 troops"}
   <event supply_attrition> {"marshal": "Murat", "nation": "France", "region": "Munich", "losses": 1199, "message": "Supply shortage at Munich: Murat loses 1,199 troops"}
   <event supply_attrition> {"marshal": "Bernadotte", "nation": "France", "region": "Munich", "losses": 936, "message": "Supply shortage at Munich: Bernadotte loses 936 troops"}
   <event supply_attrition> {"marshal": "Massena", "nation": "France", "region": "Munich", "losses": 1416, "message": "Supply shortage at Munich: Massena loses 1,416 troops"}
   <event garrison_regen> {"region": "Milan", "nation": "Austria", "old_strength": 12000, "new_strength": 14000, "message": "Garrison at Milan reinforced: 12,000 -> 14,000"}
   <event vassal_loyalty> {"vassal": "Holland", "lord": "France", "nation": "France", "old_loyalty": 98, "new_loyalty": 100, "delta": 2, "reason": "a common enemy, the lord's victories", "recovery_hint": "", "message": "Holland loyalty 100 (+2): a common enemy, the lord's victories"}
   <event vassal_loyalty> {"vassal": "KingdomOfItaly", "lord": "France", "nation": "France", "old_loyalty": 99, "new_loyalty": 100, "delta": 2, "reason": "a common enemy, the lord's victories", "recovery_hint": "", "message": "KingdomOfItaly loyalty 100 (+2): a common enemy, the lord's victories"}
   <event british_subsidy> {"recipient": "Austria", "payer": "Britain", "amount": 200, "war_id": "war_1", "subsidy_source_detail": "unique_eligible", "message": "Britain subsidizes Austria with 200 gold."}
   <event ai_ai_rivalry> {"nations": ["Russia", "Prussia"], "message": "Territorial rivalry between Russia and Prussia grows."}
   <event ai_ai_rivalry> {"nations": ["Russia", "Sweden"], "message": "Territorial rivalry between Russia and Sweden grows."}
   <event sponsorship_granted> {"kind": "sponsorship", "payer": "Britain", "recipient": "Sweden", "aim": "France", "amount": 200, "turns": 10, "licence": false, "turn": 4}
   <event trust_warning> {"marshal": "Bernadotte", "trust": 37, "message": "[!] Bernadotte's trust is faltering (37). Consider giving them more independence."}
   <event jealousy_autonomous_attack> {"message": "Lannes, hungry for glory, has attacked Mack on his own initiative.", "nation": "France", "marshal": "Lannes"}
   <event jealousy_resolved> {"message": "Bernadotte's grievance is satisfied \u2014 a victory won shoulder to shoulder. He holds with renewed purpose (+10% defense this turn).", "nation": "France", "marshal": "Bernadotte"}
   <event jealousy_fired> {"message": "Berthier reports that Bernadotte resents Ney's laurels again, 2 turns after the last \u2014 he has grown quiet in the way the staff have learned to read.", "nation": "France", "marshal": "Bernadotte", "target": "Ney"}
   <event jealousy_escalation> {"message": "The rivalry between Bernadotte and Ney has become entrenched. The wound will not close on its own.", "nation": "France", "marshal": "Bernadotte", "target": "Ney"}
   <event jealousy_fired> {"message": "Berthier reports that Soult appears envious of Lannes's laurels \u2014 he has thrown himself into his post with obsessive diligence.", "nation": "France", "marshal": "Soult", "target": "Lannes"}
   <event intel_updated> {"region": "Brunswick", "new_visibility": "partial", "old_visibility": "unknown", "source": "adjacent"}
   <event intel_updated> {"region": "Franconia", "new_visibility": "full", "old_visibility": "partial", "source": "obsessive_patrols"}
   <event intel_updated> {"region": "Swabia", "new_visibility": "full", "old_visibility": "partial", "source": "obsessive_patrols"}
   <event intel_updated> {"region": "Tyrol", "new_visibility": "full", "old_visibility": "partial", "source": "obsessive_patrols"}
   <event intel_updated> {"region": "Franche-Comte", "new_visibility": "full", "old_visibility": "partial", "source": "obsessive_patrols"}
   <event intel_decayed> {"region": "Bern", "old_visibility": "partial", "new_visibility": "stale"}

####################################################################################################
# THE ENEMY PHASE
####################################################################################################
-- Austria --
  - ArchdukeCharles attacks Carniola
      [conquest] Carniola  capture_choice=secure
  - ArchdukeJohn moves to Tyrol
      [move] {"type": "move", "marshal": "ArchdukeJohn", "from": "Milan", "to": "Tyrol"}
  - ArchdukeCharles moves to Hungary
      [move] {"type": "move", "marshal": "ArchdukeCharles", "from": "Carniola", "to": "Hungary", "march_losses": 1306}
  - ArchdukeJohn attacks Munich
      [battle] The Great Battle of Munich  -> defender_tactical_victory  victor=Soult
        ATK ArchdukeJohn     lost   8,512  left   9,272  morale  20  ROUTED
        DEF Soult            lost     702  left  33,471  morale  90
        defender order of battle: Soult 33,812(engaged); Murat 20,193(reinforced); Bernadotte 15,770(reinforced)
    [action_count] 4
[summary]
   ArchdukeCharles: attack → Carniola
   ArchdukeJohn: move → Tyrol
   ArchdukeCharles: move → Hungary
   ArchdukeJohn: attack → Munich

####################################################################################################
# THE MORNING DISPATCH
####################################################################################################
{
 "turn": 4,
 "situation": {
  "player_regions": 28,
  "enemy_regions": 98,
  "treasury": 7778,
  "treasury_delta": 2674,
  "trade_income": 500,
  "occupation": 0,
  "contributions": 0,
  "state_charges": 272,
  "requisitions": 0,
  "overseas": 0,
  "dotation_skim": 0,
  "unmet_marshals": [
   {
    "marshal": "Ney",
    "expectation": 200,
    "satisfaction": 0,
    "shortfall": 200,
    "eroding": true,
    "grace_turns_left": 0,
    "pension": 0
   },
   {
    "marshal": "Davout",
    "expectation": 240,
    "satisfaction": 0,
    "shortfall": 240,
    "eroding": true,
    "grace_turns_left": 0,
    "pension": 0
   },
   {
    "marshal": "Soult",
    "expectation": 120,
    "satisfaction": 0,
    "shortfall": 120,
    "eroding": true,
    "grace_turns_left": 0,
    "pension": 0
   },
   {
    "marshal": "Lannes",
    "expectation": 200,
    "satisfaction": 0,
    "shortfall": 200,
    "eroding": true,
    "grace_turns_left": 0,
    "pension": 0
   },
   {
    "marshal": "Murat",
    "expectation": 200,
    "satisfaction": 0,
    "shortfall": 200,
    "eroding": true,
    "grace_turns_left": 0,
    "pension": 0
   },
   {
    "marshal": "Bernadotte",
    "expectation": 160,
    "satisfaction": 0,
    "shortfall": 160,
    "eroding": true,
    "grace_turns_left": 0,
    "pension": 0
   }
  ],
  "rente_cost": 0,
  "expectation_rises": [
   {
    "marshal": "Ney",
    "expectation": 200,
    "previous": 120,
    "satisfaction": 0
   },
   {
    "marshal": "Davout",
    "expectation": 240,
    "previous": 160,
    "satisfaction": 0
   },
   {
    "marshal": "Soult",
    "expectation": 120,
    "previous": 80,
    "satisfaction": 0
   },
   {
    "marshal": "Lannes",
    "expectation": 200,
    "previous": 160,
    "satisfaction": 0
   },
   {
    "marshal": "Murat",
    "expectation": 200,
    "previous": 120,
    "satisfaction": 0
   },
   {
    "marshal": "Bernadotte",
    "expectation": 160,
    "previous": 80,
    "satisfaction": 0
   }
  ],
  "blockade": 250,
  "admiralty": 90,
  "upkeep_surcharge": 216,
  "force_limit": 130000,
  "over_force_limit": true,
  "bankrupt": false,
  "strength_ratio_pct": 36,
  "authority": 95,
  "authority_label": "Strong"
 },
 "marshals": [
  {
   "name": "Soult",
   "location": "Munich",
   "strength": 31463,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 1,
   "danger": "Starving \u2014 supply has failed at Munich two turns running.",
   "trust": 67,
   "trust_notable": false,
   "morale": 90,
   "morale_warning": false
  },
  {
   "name": "Davout",
   "location": "Frankfurt",
   "strength": 23415,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 1,
   "danger": "",
   "trust": 85,
   "trust_notable": false,
   "morale": 85,
   "morale_warning": false
  },
  {
   "name": "Massena",
   "location": "Munich",
   "strength": 22190,
   "status": "retreating",
   "status_note": "Hunted by Archduke Charles across 1 frontier \u2014 stands at Munich with 22,190
  men.",
   "arc_note": "Hunted by Archduke Charles across 1 frontier \u2014 stands at Munich with 22,190
  men.",
   "idle_turns": 2,
   "danger": "Morale failing (22) \u2014 the men waver.",
   "trust": 60,
   "trust_notable": false,
   "morale": 22,
   "morale_warning": true
  },
  {
   "name": "Ney",
   "location": "Frankfurt",
   "strength": 21203,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 0,
   "danger": "Starving \u2014 supply has failed at Frankfurt two turns running.",
   "trust": 72,
   "trust_notable": false,
   "morale": 85,
   "morale_warning": false
  },
  {
   "name": "Murat",
   "location": "Munich",
   "strength": 18791,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 1,
   "danger": "",
   "trust": 72,
   "trust_notable": false,
   "morale": 85,
   "morale_warning": false
  },
  {
   "name": "Lannes",
   "location": "Rhineland",
   "strength": 16505,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 0,
   "danger": "",
   "trust": 82,
   "trust_notable": false,
   "morale": 85,
   "morale_warning": false
  },
  {
   "name": "Bernadotte",
   "location": "Munich",
   "strength": 14676,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 1,
   "danger": "",
   "trust": 37,
   "trust_notable": true,
   "morale": 90,
   "morale_warning": false
  }
 ],
 "intelligence": [
  {
   "name": "Archduke Charles",
   "location": "Bohemia",
   "strength_display": "41,842",
   "visibility": "full",
   "intel_turn": 3
  },
  {
   "name": "Archduke John",
   "location": "Bohemia",
   "strength_display": "9,139",
   "visibility": "full",
   "intel_turn": 3
  },
  {
   "name": "Mack",
   "location": "Berlin",
   "strength_display": "screening force",
   "visibility": "partial",
   "intel_turn": 4
  },
  {
   "name": "Brunswick",
   "location": "Berlin",
   "strength_display": "large force",
   "visibility": "partial",
   "intel_turn": 4
  },
  {
   "name": "Castanos",
   "location": "Gascony",
   "strength_display": "small force",
   "visibility": "partial",
   "intel_turn": 4
  }
 ],
 "turn_events": [
  {
   "message": "Massena's army is recovering. Effectiveness penalty: -25% The rout's disorder lingers
  in the ranks.",
   "severity": "good"
  },
  {
   "message": "Supply shortage at Munich: Soult loses 2,008 troops",
   "severity": "warning"
  },
  {
   "message": "Supply shortage at Munich: Murat loses 1,199 troops",
   "severity": "warning"
  },
  {
   "message": "Supply shortage at Munich: Bernadotte loses 936 troops",
   "severity": "warning"
  },
  {
   "message": "Supply shortage at Munich: Massena loses 1,416 troops",
   "severity": "warning"
  },
  {
   "message": "Holland loyalty 100 (+2): a common enemy, the lord's victories",
   "severity": "info"
  },
  {
   "message": "KingdomOfItaly loyalty 100 (+2): a common enemy, the lord's victories",
   "severity": "info"
  },
  {
   "message": "Lannes, hungry for glory, has attacked Mack on his own initiative.",
   "severity": "warning"
  },
  {
   "message": "Bernadotte's grievance is satisfied \u2014 a victory won shoulder to shoulder. He
  holds with renewed purpose (+10% defense this turn).",
   "severity": "good"
  },
  {
   "message": "Berthier reports that Bernadotte resents Ney's laurels again, 2 turns after the last
  \u2014 he has grown quiet in the way the staff have learned to read.",
   "severity": "warning"
  },
  {
   "message": "The rivalry between Bernadotte and Ney has become entrenched. The wound will not
  close on its own.",
   "severity": "warning"
  },
  {
   "message": "Berthier reports that Soult appears envious of Lannes's laurels \u2014 he has thrown
  himself into his post with obsessive diligence.",
   "severity": "warning"
  }
 ],
 "headline": {
  "class": "victory_won",
  "weight": 73,
  "text": "Sire \u2014 Marshal Lannes holds the field at Frankfurt \u2014 Mack's corps is broken and
  flees.",
  "sub_beats": [
   "Sire \u2014 Marshal Soult holds the field at Munich \u2014 Archduke John's corps is broken and
  flees.",
   "Sire \u2014 Soult, Murat, Bernadotte and Massena stand 87,120 men at Munich, which feeds 25,000.
  62,120 too many. 7,366 men lost in 2 turns. A supply depot at Munich would ease it; dispersing a
  corps would end it."
  ]
 },
 "berthier_note": "The army knows it is winning, Sire. Press the advantage before their line
  reforms.",
 "talleyrand_report": [
  {
   "message": "Sire, I believe Bavaria may be ready to discuss improved relations. The diplomatic
  winds favor us.",
   "trigger_type": "acceptance_crossed",
   "target_nation": "Bavaria",
   "priority": 2,
   "elaborate_type": "proposal_options"
  },
  {
   "message": "Sire, I believe Hesse may be ready to discuss improved relations. The diplomatic
  winds favor us.",
   "trigger_type": "acceptance_crossed",
   "target_nation": "Hesse",
   "priority": 2,
   "elaborate_type": "proposal_options"
  }
 ],
 "talleyrand_discovery": null,
 "talleyrand_override_note": null,
 "talleyrand_redemption": null,
 "coalition_status": {
  "threat_level": 83,
  "tier": "Formed",
  "sources": [
   {
    "source": "hegemony_passive",
    "amount": 1,
    "target": "France"
   },
   {
    "source": "decay",
    "amount": -3
   }
  ],
  "active_coalition": {
   "name": "Third Coalition",
   "leader": "Britain",
   "posture": "defensive",
   "formed_turn": 1,
   "members": [
    {
     "nation": "Austria",
     "war_exhaustion": 72,
     "strength_display": "52,446 men",
     "strength": 52446,
     "gold": -441
    },
    {
     "nation": "Britain",
     "war_exhaustion": 0,
     "strength_display": "Unknown",
     "strength": 0,
     "gold": 0
    },
    {
     "nation": "Russia",
     "war_exhaustion": 0,
     "strength_display": "Unknown",
     "strength": 0,
     "gold": 0
    }
   ]
  }
 },
 "diplomatic_events": [
  {
   "type": "diplomatic_dp_regen",
   "text": "Talleyrand reports: 5 diplomatic points available (base 3, +1 skill, +1 authority).",
   "priority": "LOW"
  },
  {
   "type": "paymaster_subsidy",
   "text": "Britain's gold reaches Austria \u2014 the subsidy stands at 200 this season.",
   "priority": "MEDIUM"
  }
 ],
 "pending_envoy_count": 3,
 "pending_envoys": [
  {
   "nation": "Britain",
   "proposal_type": "settlement offer",
   "state": "WAITING"
  },
  {
   "nation": "Hesse",
   "proposal_type": "non aggression",
   "state": "WAITING"
  },
  {
   "nation": "PapalStates",
   "proposal_type": "open borders",
   "state": "WAITING"
  }
 ]
}
-- POPUP/DIALOGUE [notifications] --
   [
    {
     "id": "c9fdca21-9c08-4ec6-886a-3fe7a7f02fa8",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Ney grows bitter",
     "message": "Marshal Ney's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Ney",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Ney grows bitter",
     "repeat_count": 1
    },
    {
     "id": "ff90a7da-d536-4658-af81-bbd0a31ad89d",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Davout grows bitter",
     "message": "Marshal Davout's victories remain unrewarded (expects 240g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Davout",
      "expectation": 240,
      "satisfaction": 0,
      "shortfall": 240
     },
     "base_title": "Marshal Davout grows bitter",
     "repeat_count": 1
    },
    {
     "id": "823b437f-15a0-4fb9-8251-37ed3e1cd475",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Soult grows bitter",
     "message": "Marshal Soult's victories remain unrewarded (expects 120g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Soult",
      "expectation": 120,
      "satisfaction": 0,
      "shortfall": 120
     },
     "base_title": "Marshal Soult grows bitter",
     "repeat_count": 1
    },
    {
     "id": "160c5aa3-8ef9-46f4-9999-9f4232ea3bbf",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Lannes grows bitter",
     "message": "Marshal Lannes's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Lannes",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Lannes grows bitter",
     "repeat_count": 1
    },
    {
     "id": "ea9c2894-880f-4204-90ba-93891be05813",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Murat grows bitter",
     "message": "Marshal Murat's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Murat",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Murat grows bitter",
     "repeat_count": 1
    },
    {
     "id": "11eb075a-98d7-4a9b-94f1-ee058610f860",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Bernadotte grows bitter",
     "message": "Marshal Bernadotte's victories remain unrewarded (expects 160g/turn of estates;
     holds 0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014
     grant a rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Bernadotte",
      "expectation": 160,
      "satisfaction": 0,
      "shortfall": 160
     },
     "base_title": "Marshal Bernadotte grows bitter",
     "repeat_count": 1
    },
    {
     "id": "6b57f491-8922-4c5b-a7ec-76dc5bf17384",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Hesse",
     "message": "An envoy from Hesse has arrived with a proposal.",
     "turn_created": 3,
     "details": {},
     "base_title": "Envoy from Hesse",
     "repeat_count": 1
    },
    {
     "id": "eecb2ded-8b5a-408b-b3af-cc03ed350d29",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Papal States",
     "message": "An envoy from Papal States has arrived with a proposal.",
     "turn_created": 3,
     "details": {},
     "base_title"

====================================================================================================
> end turn
====================================================================================================
I don't understand that choice, Sire. Options: 1=Conquest, 2=Forced Alliance, 3=Subjugation, 4=Back
  Out
-- POPUP/DIALOGUE [envoy_digest] --
   {
    "turn": 4,
    "count": 2,
    "title": "THE SMALL COURTS WRITE",
    "lapsing_count": 2,
    "headline": "Hesse and Papal States write.",
    "deadline_note": "Answer them here. Unanswered letters lapse when the turn ends, and a court
     left waiting will not raise the matter again for some seasons.",
    "items": [
     {
      "mailbox_id": 7,
      "dialogue_id": 9,
      "from_nation": "Hesse",
      "power_tier": "minor",
      "proposal_type": "non_aggression",
      "proposal_type_display": "Non-Aggression Pact",
      "diplomat_name": "Chancery of Hesse",
      "diplomat_line": "Hesse, wishing to go unnoticed: \"Hesse counts what a quarrel with France
     would cost and what an understanding would return, and finds the ledger unanimous. Sign the
     pact of non-aggression.\"",
      "clauses": [
       "Proposal: Non-Aggression Pact"
      ],
      "acceptance_hint": "natural willingness to negotiate",
      "state": "WAITING",
      "arrival_turn": 3
     },
     {
      "mailbox_id": 8,
      "dialogue_id": 10,
      "from_nation": "PapalStates",
      "power_tier": "minor",
      "proposal_type": "friendly_gift",
      "proposal_type_display": "Open Borders Agreement",
      "diplomat_name": "Consalvi",
      "diplomat_line": "Cardinal Consalvi, serenely: \"Rome measures powers in centuries and finds
     it profitable to be patient with all of them; an understanding with France costs the Church
     nothing that time will not repay. Open the borders.\"",
      "clauses": [
       "Proposal: Open Borders Agreement",
       "Clause: Open borders",
       "Offer: Gold payment - 105"
      ],
      "acceptance_hint": "natural willingness to negotiate",
      "state": "WAITING",
      "arrival_turn": 3
     }
    ]
   }
-- POPUP/DIALOGUE [marshal_petition] --
   {
    "kind": "rivalry_confrontation",
    "title": "A rivalry among the marshals",
    "body": "Sire, Ney has refused to attend council where Bernadotte is present. The breach may be
     beyond repair.",
    "speaker": "Ney",
    "options": [
     {
      "id": "accept_breach",
      "label": "Accept the Breach",
      "detail": "They settle into cold war; one may turn openly discontent.",
      "cost_note": "",
      "enabled": true
     },
     {
      "id": "force_reconciliation",
      "label": "Force Reconciliation",
      "detail": "A public gamble on your authority.",
      "cost_note": "2 AP",
      "ap_cost": 2,
      "enabled": true
     },
     {
      "id": "separate",
      "label": "Separate Them",
      "detail": "Not a fix \u2014 Berthier will warn you whenever their commands stand together.",
      "cost_note": "",
      "enabled": true
     }
    ],
    "context": {
     "marshal": "Ney",
     "other": "Bernadotte",
     "new_value": -2
    },
    "turn": 3
   }
-- POPUP/DIALOGUE [notifications] --
   [
    {
     "id": "c9fdca21-9c08-4ec6-886a-3fe7a7f02fa8",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Ney grows bitter",
     "message": "Marshal Ney's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Ney",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Ney grows bitter",
     "repeat_count": 1
    },
    {
     "id": "ff90a7da-d536-4658-af81-bbd0a31ad89d",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Davout grows bitter",
     "message": "Marshal Davout's victories remain unrewarded (expects 240g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Davout",
      "expectation": 240,
      "satisfaction": 0,
      "shortfall": 240
     },
     "base_title": "Marshal Davout grows bitter",
     "repeat_count": 1
    },
    {
     "id": "823b437f-15a0-4fb9-8251-37ed3e1cd475",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Soult grows bitter",
     "message": "Marshal Soult's victories remain unrewarded (expects 120g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Soult",
      "expectation": 120,
      "satisfaction": 0,
      "shortfall": 120
     },
     "base_title": "Marshal Soult grows bitter",
     "repeat_count": 1
    },
    {
     "id": "160c5aa3-8ef9-46f4-9999-9f4232ea3bbf",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Lannes grows bitter",
     "message": "Marshal Lannes's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Lannes",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Lannes grows bitter",
     "repeat_count": 1
    },
    {
     "id": "ea9c2894-880f-4204-90ba-93891be05813",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Murat grows bitter",
     "message": "Marshal Murat's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Murat",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Murat grows bitter",
     "repeat_count": 1
    },
    {
     "id": "11eb075a-98d7-4a9b-94f1-ee058610f860",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Bernadotte grows bitter",
     "message": "Marshal Bernadotte's victories remain unrewarded (expects 160g/turn of estates;
     holds 0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014
     grant a rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Bernadotte",
      "expectation": 160,
      "satisfaction": 0,
      "shortfall": 160
     },
     "base_title": "Marshal Bernadotte grows bitter",
     "repeat_count": 1
    },
    {
     "id": "6b57f491-8922-4c5b-a7ec-76dc5bf17384",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Hesse",
     "message": "An envoy from Hesse has arrived with a proposal.",
     "turn_created": 3,
     "details": {},
     "base_title": "Envoy from Hesse",
     "repeat_count": 1
    },
    {
     "id": "eecb2ded-8b5a-408b-b3af-cc03ed350d29",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Papal States",
     "message": "An envoy from Papal States has arrived with a proposal.",
     "turn_created": 3,
     "details": {},
     "base_title"

====================================================================================================
> 4
====================================================================================================
Of course, Sire. Take your time.
-- POPUP/DIALOGUE [envoy_digest] --
   {
    "turn": 4,
    "count": 2,
    "title": "THE SMALL COURTS WRITE",
    "lapsing_count": 2,
    "headline": "Hesse and Papal States write.",
    "deadline_note": "Answer them here. Unanswered letters lapse when the turn ends, and a court
     left waiting will not raise the matter again for some seasons.",
    "items": [
     {
      "mailbox_id": 7,
      "dialogue_id": 9,
      "from_nation": "Hesse",
      "power_tier": "minor",
      "proposal_type": "non_aggression",
      "proposal_type_display": "Non-Aggression Pact",
      "diplomat_name": "Chancery of Hesse",
      "diplomat_line": "Hesse, wishing to go unnoticed: \"Hesse counts what a quarrel with France
     would cost and what an understanding would return, and finds the ledger unanimous. Sign the
     pact of non-aggression.\"",
      "clauses": [
       "Proposal: Non-Aggression Pact"
      ],
      "acceptance_hint": "natural willingness to negotiate",
      "state": "WAITING",
      "arrival_turn": 3
     },
     {
      "mailbox_id": 8,
      "dialogue_id": 10,
      "from_nation": "PapalStates",
      "power_tier": "minor",
      "proposal_type": "friendly_gift",
      "proposal_type_display": "Open Borders Agreement",
      "diplomat_name": "Consalvi",
      "diplomat_line": "Cardinal Consalvi, serenely: \"Rome measures powers in centuries and finds
     it profitable to be patient with all of them; an understanding with France costs the Church
     nothing that time will not repay. Open the borders.\"",
      "clauses": [
       "Proposal: Open Borders Agreement",
       "Clause: Open borders",
       "Offer: Gold payment - 105"
      ],
      "acceptance_hint": "natural willingness to negotiate",
      "state": "WAITING",
      "arrival_turn": 3
     }
    ]
   }
-- POPUP/DIALOGUE [incoming_settlement_offer] --
   {
    "type": "incoming_settlement_offer",
    "dialogue_type": "incoming_settlement_offer",
    "offer_id": "settlement_offer:war_1:3:1",
    "war_id": "war_1",
    "war_label": "France vs Britain",
    "proposer_nation": "Britain",
    "accepting_side": "attackers",
    "covered_enemy_participants": [
     "Britain",
     "Austria",
     "Russia"
    ],
    "settlement_terms": [
     {
      "type": "peace"
     }
    ],
    "terms_summary": [
     "Peace",
     "Status quo: Austria retains Milan; Bavaria retains Hungary, Moravia."
    ],
    "amount": 0,
    "talleyrand_text": "Sire, Britain has dispatched a settlement of France vs Britain. They ask 0
     gold to close the war; the table is theirs to set, the signature is ours to give or withhold.",
    "proposer_voice": "His Majesty's Government offers terms for France vs Britain. London asks 0
     gold and a return to peace; the price is set, and London is not in the habit of revising
     figures lightly.",
    "options": [
     {
      "label": "Review Settlement Offer",
      "description": "Open the offered terms for ratification review. Ratification still requires a
     final confirm.",
      "action": "accept_settlement_offer",
      "available": true
     },
     {
      "label": "Request Revision",
      "description": "Lay the offered terms on our own table, court by court, and answer with a
     counter draft.",
      "action": "request_settlement_revision",
      "available": true
     },
     {
      "label": "Reject Offer",
      "description": "Decline the offer without further negotiation.",
      "action": "reject_settlement_offer",
      "available": true
     }
    ],
    "available_action_ids": [
     "accept_settlement_offer",
     "request_settlement_revision",
     "reject_settlement_offer"
    ],
    "dialogue_id": 11
   }
-- POPUP/DIALOGUE [notifications] --
   [
    {
     "id": "c9fdca21-9c08-4ec6-886a-3fe7a7f02fa8",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Ney grows bitter",
     "message": "Marshal Ney's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Ney",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Ney grows bitter",
     "repeat_count": 1
    },
    {
     "id": "ff90a7da-d536-4658-af81-bbd0a31ad89d",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Davout grows bitter",
     "message": "Marshal Davout's victories remain unrewarded (expects 240g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Davout",
      "expectation": 240,
      "satisfaction": 0,
      "shortfall": 240
     },
     "base_title": "Marshal Davout grows bitter",
     "repeat_count": 1
    },
    {
     "id": "823b437f-15a0-4fb9-8251-37ed3e1cd475",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Soult grows bitter",
     "message": "Marshal Soult's victories remain unrewarded (expects 120g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Soult",
      "expectation": 120,
      "satisfaction": 0,
      "shortfall": 120
     },
     "base_title": "Marshal Soult grows bitter",
     "repeat_count": 1
    },
    {
     "id": "160c5aa3-8ef9-46f4-9999-9f4232ea3bbf",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Lannes grows bitter",
     "message": "Marshal Lannes's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Lannes",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Lannes grows bitter",
     "repeat_count": 1
    },
    {
     "id": "ea9c2894-880f-4204-90ba-93891be05813",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Murat grows bitter",
     "message": "Marshal Murat's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Murat",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Murat grows bitter",
     "repeat_count": 1
    },
    {
     "id": "11eb075a-98d7-4a9b-94f1-ee058610f860",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Bernadotte grows bitter",
     "message": "Marshal Bernadotte's victories remain unrewarded (expects 160g/turn of estates;
     holds 0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014
     grant a rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Bernadotte",
      "expectation": 160,
      "satisfaction": 0,
      "shortfall": 160
     },
     "base_title": "Marshal Bernadotte grows bitter",
     "repeat_count": 1
    },
    {
     "id": "6b57f491-8922-4c5b-a7ec-76dc5bf17384",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Hesse",
     "message": "An envoy from Hesse has arrived with a proposal.",
     "turn_created": 3,
     "details": {},
     "base_title": "Envoy from Hesse",
     "repeat_count": 1
    },
    {
     "id": "eecb2ded-8b5a-408b-b3af-cc03ed350d29",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Papal States",
     "message": "An envoy from Papal States has arrived with a proposal.",
     "turn_created": 3,
     "details": {},
     "base_title"

====================================================================================================
> Soult, attack Tyrol
====================================================================================================
Soult marches from Munich into Tyrol unopposed! (1,887 lost to march) Captured: Austria → France
Your forces have taken Tyrol. Plunder it for 600 gold — buildings burned, the province left hostile
  — or secure it and keep the country quiet? ('plunder' or 'secure')
   [cost=1  turn_advanced=False]
   <event conquest> {"marshal": "Soult", "region": "Tyrol", "unopposed": true}
-- POPUP/DIALOGUE [envoy_digest] --
   {
    "turn": 4,
    "count": 2,
    "title": "THE SMALL COURTS WRITE",
    "lapsing_count": 2,
    "headline": "Papal States and Hesse write.",
    "deadline_note": "Answer them here. Unanswered letters lapse when the turn ends, and a court
     left waiting will not raise the matter again for some seasons.",
    "items": [
     {
      "mailbox_id": 8,
      "dialogue_id": 10,
      "from_nation": "PapalStates",
      "power_tier": "minor",
      "proposal_type": "friendly_gift",
      "proposal_type_display": "Open Borders Agreement",
      "diplomat_name": "Consalvi",
      "diplomat_line": "Cardinal Consalvi, serenely: \"Rome measures powers in centuries and finds
     it profitable to be patient with all of them; an understanding with France costs the Church
     nothing that time will not repay. Open the borders.\"",
      "clauses": [
       "Proposal: Open Borders Agreement",
       "Clause: Open borders",
       "Offer: Gold payment - 105"
      ],
      "acceptance_hint": "natural willingness to negotiate",
      "state": "WAITING",
      "arrival_turn": 3
     },
     {
      "mailbox_id": 7,
      "dialogue_id": 9,
      "from_nation": "Hesse",
      "power_tier": "minor",
      "proposal_type": "non_aggression",
      "proposal_type_display": "Non-Aggression Pact",
      "diplomat_name": "Chancery of Hesse",
      "diplomat_line": "Hesse, wishing to go unnoticed: \"Hesse counts what a quarrel with France
     would cost and what an understanding would return, and finds the ledger unanimous. Sign the
     pact of non-aggression.\"",
      "clauses": [
       "Proposal: Non-Aggression Pact"
      ],
      "acceptance_hint": "natural willingness to negotiate",
      "state": "WAITING",
      "arrival_turn": 3
     }
    ]
   }
-- POPUP/DIALOGUE [pending_capture_choice] --
   true
-- POPUP/DIALOGUE [notifications] --
   [
    {
     "id": "c9fdca21-9c08-4ec6-886a-3fe7a7f02fa8",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Ney grows bitter",
     "message": "Marshal Ney's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Ney",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Ney grows bitter",
     "repeat_count": 1
    },
    {
     "id": "ff90a7da-d536-4658-af81-bbd0a31ad89d",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Davout grows bitter",
     "message": "Marshal Davout's victories remain unrewarded (expects 240g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Davout",
      "expectation": 240,
      "satisfaction": 0,
      "shortfall": 240
     },
     "base_title": "Marshal Davout grows bitter",
     "repeat_count": 1
    },
    {
     "id": "823b437f-15a0-4fb9-8251-37ed3e1cd475",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Soult grows bitter",
     "message": "Marshal Soult's victories remain unrewarded (expects 120g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Soult",
      "expectation": 120,
      "satisfaction": 0,
      "shortfall": 120
     },
     "base_title": "Marshal Soult grows bitter",
     "repeat_count": 1
    },
    {
     "id": "160c5aa3-8ef9-46f4-9999-9f4232ea3bbf",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Lannes grows bitter",
     "message": "Marshal Lannes's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Lannes",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Lannes grows bitter",
     "repeat_count": 1
    },
    {
     "id": "ea9c2894-880f-4204-90ba-93891be05813",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Murat grows bitter",
     "message": "Marshal Murat's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Murat",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Murat grows bitter",
     "repeat_count": 1
    },
    {
     "id": "11eb075a-98d7-4a9b-94f1-ee058610f860",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Bernadotte grows bitter",
     "message": "Marshal Bernadotte's victories remain unrewarded (expects 160g/turn of estates;
     holds 0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014
     grant a rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Bernadotte",
      "expectation": 160,
      "satisfaction": 0,
      "shortfall": 160
     },
     "base_title": "Marshal Bernadotte grows bitter",
     "repeat_count": 1
    },
    {
     "id": "835f3e9f-0e7d-4381-959a-eeea75f12553",
     "type": "ally_settlement_petition",
     "priority": 1,
     "title": "KingdomOfItaly petitions over settlement scope",
     "message": "KingdomOfItaly petitions for the return of Milan.",
     "turn_created": 4,
     "details": {
      "review_target": "ally_settlement_petition_popup",
      "review_label": "Open Envoys",
      "war_id": "war_1",
      "petition_id":
     "ally_petition:request_reward_or_restoration:war_1:KingdomOfItaly::Austria:Milan",
      "petition_type": "request_reward_or_restoration",
      "ally_nation": "Kingdo

====================================================================================================
> secure
====================================================================================================
Soult secures Tyrol. Stability set to 25. Order is maintained.
   <event secure> {"region": "Tyrol", "capturer": "Soult"}
-- POPUP/DIALOGUE [envoy_digest] --
   {
    "turn": 4,
    "count": 2,
    "title": "THE SMALL COURTS WRITE",
    "lapsing_count": 2,
    "headline": "Papal States and Hesse write.",
    "deadline_note": "Answer them here. Unanswered letters lapse when the turn ends, and a court
     left waiting will not raise the matter again for some seasons.",
    "items": [
     {
      "mailbox_id": 8,
      "dialogue_id": 10,
      "from_nation": "PapalStates",
      "power_tier": "minor",
      "proposal_type": "friendly_gift",
      "proposal_type_display": "Open Borders Agreement",
      "diplomat_name": "Consalvi",
      "diplomat_line": "Cardinal Consalvi, serenely: \"Rome measures powers in centuries and finds
     it profitable to be patient with all of them; an understanding with France costs the Church
     nothing that time will not repay. Open the borders.\"",
      "clauses": [
       "Proposal: Open Borders Agreement",
       "Clause: Open borders",
       "Offer: Gold payment - 105"
      ],
      "acceptance_hint": "natural willingness to negotiate",
      "state": "WAITING",
      "arrival_turn": 3
     },
     {
      "mailbox_id": 7,
      "dialogue_id": 9,
      "from_nation": "Hesse",
      "power_tier": "minor",
      "proposal_type": "non_aggression",
      "proposal_type_display": "Non-Aggression Pact",
      "diplomat_name": "Chancery of Hesse",
      "diplomat_line": "Hesse, wishing to go unnoticed: \"Hesse counts what a quarrel with France
     would cost and what an understanding would return, and finds the ledger unanimous. Sign the
     pact of non-aggression.\"",
      "clauses": [
       "Proposal: Non-Aggression Pact"
      ],
      "acceptance_hint": "natural willingness to negotiate",
      "state": "WAITING",
      "arrival_turn": 3
     }
    ]
   }
-- POPUP/DIALOGUE [capture_choice] --
   "secure"
-- POPUP/DIALOGUE [notifications] --
   [
    {
     "id": "c9fdca21-9c08-4ec6-886a-3fe7a7f02fa8",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Ney grows bitter",
     "message": "Marshal Ney's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Ney",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Ney grows bitter",
     "repeat_count": 1
    },
    {
     "id": "ff90a7da-d536-4658-af81-bbd0a31ad89d",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Davout grows bitter",
     "message": "Marshal Davout's victories remain unrewarded (expects 240g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Davout",
      "expectation": 240,
      "satisfaction": 0,
      "shortfall": 240
     },
     "base_title": "Marshal Davout grows bitter",
     "repeat_count": 1
    },
    {
     "id": "823b437f-15a0-4fb9-8251-37ed3e1cd475",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Soult grows bitter",
     "message": "Marshal Soult's victories remain unrewarded (expects 120g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Soult",
      "expectation": 120,
      "satisfaction": 0,
      "shortfall": 120
     },
     "base_title": "Marshal Soult grows bitter",
     "repeat_count": 1
    },
    {
     "id": "160c5aa3-8ef9-46f4-9999-9f4232ea3bbf",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Lannes grows bitter",
     "message": "Marshal Lannes's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Lannes",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Lannes grows bitter",
     "repeat_count": 1
    },
    {
     "id": "ea9c2894-880f-4204-90ba-93891be05813",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Murat grows bitter",
     "message": "Marshal Murat's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Murat",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Murat grows bitter",
     "repeat_count": 1
    },
    {
     "id": "11eb075a-98d7-4a9b-94f1-ee058610f860",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Bernadotte grows bitter",
     "message": "Marshal Bernadotte's victories remain unrewarded (expects 160g/turn of estates;
     holds 0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014
     grant a rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Bernadotte",
      "expectation": 160,
      "satisfaction": 0,
      "shortfall": 160
     },
     "base_title": "Marshal Bernadotte grows bitter",
     "repeat_count": 1
    },
    {
     "id": "835f3e9f-0e7d-4381-959a-eeea75f12553",
     "type": "ally_settlement_petition",
     "priority": 1,
     "title": "KingdomOfItaly petitions over settlement scope",
     "message": "KingdomOfItaly petitions for the return of Milan.",
     "turn_created": 4,
     "details": {
      "review_target": "ally_settlement_petition_popup",
      "review_label": "Open Envoys",
      "war_id": "war_1",
      "petition_id":
     "ally_petition:request_reward_or_restoration:war_1:KingdomOfItaly::Austria:Milan",
      "petition_type": "request_reward_or_restoration",
      "ally_nation": "Kingdo

====================================================================================================
> Murat, move to Tyrol
====================================================================================================
Murat moves from Munich to Tyrol (375 lost to march)
[HINT] Carniola is undefended — attack to capture it!
   [cost=1  turn_advanced=False]
   <event move> {"marshal": "Murat", "from": "Munich", "to": "Tyrol", "march_losses": 375}
-- POPUP/DIALOGUE [envoy_digest] --
   {
    "turn": 4,
    "count": 2,
    "title": "THE SMALL COURTS WRITE",
    "lapsing_count": 2,
    "headline": "Papal States and Hesse write.",
    "deadline_note": "Answer them here. Unanswered letters lapse when the turn ends, and a court
     left waiting will not raise the matter again for some seasons.",
    "items": [
     {
      "mailbox_id": 8,
      "dialogue_id": 10,
      "from_nation": "PapalStates",
      "power_tier": "minor",
      "proposal_type": "friendly_gift",
      "proposal_type_display": "Open Borders Agreement",
      "diplomat_name": "Consalvi",
      "diplomat_line": "Cardinal Consalvi, serenely: \"Rome measures powers in centuries and finds
     it profitable to be patient with all of them; an understanding with France costs the Church
     nothing that time will not repay. Open the borders.\"",
      "clauses": [
       "Proposal: Open Borders Agreement",
       "Clause: Open borders",
       "Offer: Gold payment - 105"
      ],
      "acceptance_hint": "natural willingness to negotiate",
      "state": "WAITING",
      "arrival_turn": 3
     },
     {
      "mailbox_id": 7,
      "dialogue_id": 9,
      "from_nation": "Hesse",
      "power_tier": "minor",
      "proposal_type": "non_aggression",
      "proposal_type_display": "Non-Aggression Pact",
      "diplomat_name": "Chancery of Hesse",
      "diplomat_line": "Hesse, wishing to go unnoticed: \"Hesse counts what a quarrel with France
     would cost and what an understanding would return, and finds the ledger unanimous. Sign the
     pact of non-aggression.\"",
      "clauses": [
       "Proposal: Non-Aggression Pact"
      ],
      "acceptance_hint": "natural willingness to negotiate",
      "state": "WAITING",
      "arrival_turn": 3
     }
    ]
   }
-- POPUP/DIALOGUE [notifications] --
   [
    {
     "id": "c9fdca21-9c08-4ec6-886a-3fe7a7f02fa8",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Ney grows bitter",
     "message": "Marshal Ney's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Ney",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Ney grows bitter",
     "repeat_count": 1
    },
    {
     "id": "ff90a7da-d536-4658-af81-bbd0a31ad89d",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Davout grows bitter",
     "message": "Marshal Davout's victories remain unrewarded (expects 240g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Davout",
      "expectation": 240,
      "satisfaction": 0,
      "shortfall": 240
     },
     "base_title": "Marshal Davout grows bitter",
     "repeat_count": 1
    },
    {
     "id": "823b437f-15a0-4fb9-8251-37ed3e1cd475",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Soult grows bitter",
     "message": "Marshal Soult's victories remain unrewarded (expects 120g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Soult",
      "expectation": 120,
      "satisfaction": 0,
      "shortfall": 120
     },
     "base_title": "Marshal Soult grows bitter",
     "repeat_count": 1
    },
    {
     "id": "160c5aa3-8ef9-46f4-9999-9f4232ea3bbf",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Lannes grows bitter",
     "message": "Marshal Lannes's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Lannes",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Lannes grows bitter",
     "repeat_count": 1
    },
    {
     "id": "ea9c2894-880f-4204-90ba-93891be05813",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Murat grows bitter",
     "message": "Marshal Murat's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Murat",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Murat grows bitter",
     "repeat_count": 1
    },
    {
     "id": "11eb075a-98d7-4a9b-94f1-ee058610f860",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Bernadotte grows bitter",
     "message": "Marshal Bernadotte's victories remain unrewarded (expects 160g/turn of estates;
     holds 0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014
     grant a rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Bernadotte",
      "expectation": 160,
      "satisfaction": 0,
      "shortfall": 160
     },
     "base_title": "Marshal Bernadotte grows bitter",
     "repeat_count": 1
    },
    {
     "id": "835f3e9f-0e7d-4381-959a-eeea75f12553",
     "type": "ally_settlement_petition",
     "priority": 1,
     "title": "KingdomOfItaly petitions over settlement scope",
     "message": "KingdomOfItaly petitions for the return of Milan.",
     "turn_created": 4,
     "details": {
      "review_target": "ally_settlement_petition_popup",
      "review_label": "Open Envoys",
      "war_id": "war_1",
      "petition_id":
     "ally_petition:request_reward_or_restoration:war_1:KingdomOfItaly::Austria:Milan",
      "petition_type": "request_reward_or_restoration",
      "ally_nation": "Kingdo

====================================================================================================
> Ney, march on Bohemia
====================================================================================================
Ney begins march to Bohemia. Route: Franconia -> Bohemia. Moves to Franconia. Ney: "We march. Pity
  whatever slows us."
   [cost=1  turn_advanced=False]
-- POPUP/DIALOGUE [envoy_digest] --
   {
    "turn": 4,
    "count": 2,
    "title": "THE SMALL COURTS WRITE",
    "lapsing_count": 2,
    "headline": "Papal States and Hesse write.",
    "deadline_note": "Answer them here. Unanswered letters lapse when the turn ends, and a court
     left waiting will not raise the matter again for some seasons.",
    "items": [
     {
      "mailbox_id": 8,
      "dialogue_id": 10,
      "from_nation": "PapalStates",
      "power_tier": "minor",
      "proposal_type": "friendly_gift",
      "proposal_type_display": "Open Borders Agreement",
      "diplomat_name": "Consalvi",
      "diplomat_line": "Cardinal Consalvi, serenely: \"Rome measures powers in centuries and finds
     it profitable to be patient with all of them; an understanding with France costs the Church
     nothing that time will not repay. Open the borders.\"",
      "clauses": [
       "Proposal: Open Borders Agreement",
       "Clause: Open borders",
       "Offer: Gold payment - 105"
      ],
      "acceptance_hint": "natural willingness to negotiate",
      "state": "WAITING",
      "arrival_turn": 3
     },
     {
      "mailbox_id": 7,
      "dialogue_id": 9,
      "from_nation": "Hesse",
      "power_tier": "minor",
      "proposal_type": "non_aggression",
      "proposal_type_display": "Non-Aggression Pact",
      "diplomat_name": "Chancery of Hesse",
      "diplomat_line": "Hesse, wishing to go unnoticed: \"Hesse counts what a quarrel with France
     would cost and what an understanding would return, and finds the ledger unanimous. Sign the
     pact of non-aggression.\"",
      "clauses": [
       "Proposal: Non-Aggression Pact"
      ],
      "acceptance_hint": "natural willingness to negotiate",
      "state": "WAITING",
      "arrival_turn": 3
     }
    ]
   }
-- POPUP/DIALOGUE [notifications] --
   [
    {
     "id": "c9fdca21-9c08-4ec6-886a-3fe7a7f02fa8",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Ney grows bitter",
     "message": "Marshal Ney's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Ney",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Ney grows bitter",
     "repeat_count": 1
    },
    {
     "id": "ff90a7da-d536-4658-af81-bbd0a31ad89d",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Davout grows bitter",
     "message": "Marshal Davout's victories remain unrewarded (expects 240g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Davout",
      "expectation": 240,
      "satisfaction": 0,
      "shortfall": 240
     },
     "base_title": "Marshal Davout grows bitter",
     "repeat_count": 1
    },
    {
     "id": "823b437f-15a0-4fb9-8251-37ed3e1cd475",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Soult grows bitter",
     "message": "Marshal Soult's victories remain unrewarded (expects 120g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Soult",
      "expectation": 120,
      "satisfaction": 0,
      "shortfall": 120
     },
     "base_title": "Marshal Soult grows bitter",
     "repeat_count": 1
    },
    {
     "id": "160c5aa3-8ef9-46f4-9999-9f4232ea3bbf",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Lannes grows bitter",
     "message": "Marshal Lannes's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Lannes",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Lannes grows bitter",
     "repeat_count": 1
    },
    {
     "id": "ea9c2894-880f-4204-90ba-93891be05813",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Murat grows bitter",
     "message": "Marshal Murat's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Murat",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Murat grows bitter",
     "repeat_count": 1
    },
    {
     "id": "11eb075a-98d7-4a9b-94f1-ee058610f860",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Bernadotte grows bitter",
     "message": "Marshal Bernadotte's victories remain unrewarded (expects 160g/turn of estates;
     holds 0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014
     grant a rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Bernadotte",
      "expectation": 160,
      "satisfaction": 0,
      "shortfall": 160
     },
     "base_title": "Marshal Bernadotte grows bitter",
     "repeat_count": 1
    },
    {
     "id": "835f3e9f-0e7d-4381-959a-eeea75f12553",
     "type": "ally_settlement_petition",
     "priority": 1,
     "title": "KingdomOfItaly petitions over settlement scope",
     "message": "KingdomOfItaly petitions for the return of Milan.",
     "turn_created": 4,
     "details": {
      "review_target": "ally_settlement_petition_popup",
      "review_label": "Open Envoys",
      "war_id": "war_1",
      "petition_id":
     "ally_petition:request_reward_or_restoration:war_1:KingdomOfItaly::Austria:Milan",
      "petition_type": "request_reward_or_restoration",
      "ally_nation": "Kingdo

====================================================================================================
> end turn
====================================================================================================
Turn 4 ended. Turn 5 begins!

Income: 3437g | Occupation: -52g | Charges of Empire: -464g | Admiralty: -90g | Blockade: -250g |
  Upkeep: 1244g (incl. 44g over-limit, 72g Grande Armée) | Other: +1262g | Net: +2599g | Treasury:
  10,377g
   [cost=0  turn_advanced=False]
   <event retreat_recovery> {"marshal": "Massena", "nation": "France", "stage": 3, "penalty": "0% (recovered)", "message": "Massena's army is recovering. Effectiveness penalty: 0% (recovered)"}
   <event retreat_recovered> {"marshal": "Massena", "nation": "France", "message": "Massena's army has fully recovered and is combat ready."}
   <event construction_complete> {"region": "Berlin", "building": "supply_depot", "message": "Construction complete: Supply Depot in Berlin!"}
   <event construction_complete> {"region": "Munich", "building": "supply_depot", "message": "Construction complete: Supply Depot in Munich!"}
   <event supply_attrition> {"marshal": "Mack", "nation": "Austria", "region": "Berlin", "losses": 16, "message": "Supply shortage at Berlin: Mack loses 16 troops"}
   <event supply_attrition> {"marshal": "Soult", "nation": "France", "region": "Tyrol", "losses": 561, "message": "Supply shortage at Tyrol: Soult loses 561 troops"}
   <event supply_attrition> {"marshal": "Murat", "nation": "France", "region": "Tyrol", "losses": 349, "message": "Supply shortage at Tyrol: Murat loses 349 troops"}
   <event supply_attrition> {"marshal": "Bernadotte", "nation": "France", "region": "Munich", "losses": 197, "message": "Supply shortage at Munich: Bernadotte loses 197 troops"}
   <event supply_attrition> {"marshal": "Massena", "nation": "France", "region": "Munich", "losses": 298, "message": "Supply shortage at Munich: Massena loses 298 troops"}
   <event garrison_regen> {"region": "Milan", "nation": "Austria", "old_strength": 14000, "new_strength": 16000, "message": "Garrison at Milan reinforced: 14,000 -> 16,000"}
   <event vassal_loyalty> {"vassal": "Switzerland", "lord": "France", "nation": "France", "old_loyalty": 94, "new_loyalty": 92, "delta": -2, "reason": "satellite drift", "recovery_hint": "Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.", "message": "Switzerland loyalty 92 (-2): satellite drift \u2014 Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them."}
   <event sponsorship_granted> {"kind": "sponsorship", "payer": "Russia", "recipient": "Britain", "aim": "France", "amount": 200, "turns": 10, "licence": false, "turn": 5}
   <event intel_decayed> {"region": "Piedmont", "old_visibility": "partial", "new_visibility": "stale"}
   <event strategic_progress> {"marshal": "Ney", "command": "MOVE_TO", "order_status": "active", "message": "Ney is marching to Bohemia (1 turn(s) remaining)."}

####################################################################################################
# THE ENEMY PHASE
####################################################################################################
-- Austria --
  - ArchdukeCharles forms square
      [form_square] {"type": "form_square", "marshal": "ArchdukeCharles", "location": "Bohemia"}
  - ArchdukeCharles attacks Hungary
      [battle] Battle of Hungary  -> attacker_tactical_victory  victor=ArchdukeCharles
        ATK ArchdukeCharles  lost     834  left  41,008  morale  95
        DEF Deroy            lost   9,370  left   3,985  morale   0  ROUTED
        REGION TAKEN: Hungary
  - ArchdukeCharles attacks Moravia
      [battle] Battle of Moravia  -> attacker_tactical_victory  victor=ArchdukeCharles
        ATK ArchdukeCharles  lost      81  left  39,697  morale  95
        DEF Deroy            lost   2,167  left   1,799  morale   0  ROUTED
        REGION TAKEN: Moravia
    [action_count] 3
[summary]
   ArchdukeCharles: form_square
   ArchdukeCharles: attack → Hungary
   ArchdukeCharles: attack → Moravia

####################################################################################################
# THE MORNING DISPATCH
####################################################################################################
{
 "turn": 5,
 "situation": {
  "player_regions": 29,
  "enemy_regions": 97,
  "treasury": 10377,
  "treasury_delta": 2390,
  "trade_income": 500,
  "occupation": 52,
  "contributions": 0,
  "state_charges": 673,
  "requisitions": 0,
  "overseas": 0,
  "dotation_skim": 0,
  "unmet_marshals": [
   {
    "marshal": "Ney",
    "expectation": 200,
    "satisfaction": 0,
    "shortfall": 200,
    "eroding": true,
    "grace_turns_left": 0,
    "pension": 0
   },
   {
    "marshal": "Davout",
    "expectation": 240,
    "satisfaction": 0,
    "shortfall": 240,
    "eroding": true,
    "grace_turns_left": 0,
    "pension": 0
   },
   {
    "marshal": "Soult",
    "expectation": 120,
    "satisfaction": 0,
    "shortfall": 120,
    "eroding": true,
    "grace_turns_left": 0,
    "pension": 0
   },
   {
    "marshal": "Lannes",
    "expectation": 200,
    "satisfaction": 0,
    "shortfall": 200,
    "eroding": true,
    "grace_turns_left": 0,
    "pension": 0
   },
   {
    "marshal": "Murat",
    "expectation": 200,
    "satisfaction": 0,
    "shortfall": 200,
    "eroding": true,
    "grace_turns_left": 0,
    "pension": 0
   },
   {
    "marshal": "Bernadotte",
    "expectation": 160,
    "satisfaction": 0,
    "shortfall": 160,
    "eroding": true,
    "grace_turns_left": 0,
    "pension": 0
   }
  ],
  "rente_cost": 0,
  "expectation_rises": [],
  "blockade": 250,
  "admiralty": 90,
  "upkeep_surcharge": 116,
  "force_limit": 132500,
  "over_force_limit": true,
  "bankrupt": false,
  "strength_ratio_pct": 2,
  "authority": 95,
  "authority_label": "Strong"
 },
 "marshals": [
  {
   "name": "Soult",
   "location": "Tyrol",
   "strength": 29015,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 2,
   "danger": "Starving \u2014 supply has failed at Tyrol two turns running.",
   "trust": 64,
   "trust_notable": false,
   "morale": 90,
   "morale_warning": false
  },
  {
   "name": "Davout",
   "location": "Frankfurt",
   "strength": 23415,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 2,
   "danger": "",
   "trust": 82,
   "trust_notable": false,
   "morale": 85,
   "morale_warning": false
  },
  {
   "name": "Massena",
   "location": "Munich",
   "strength": 21892,
   "status": "idle_restless",
   "status_note": "Hunted by Archduke Charles across 1 frontier \u2014 stands at Munich with 21,892
  men.",
   "arc_note": "Hunted by Archduke Charles across 1 frontier \u2014 stands at Munich with 21,892
  men.",
   "idle_turns": 3,
   "danger": "Morale failing (22) \u2014 the men waver.",
   "trust": 60,
   "trust_notable": false,
   "morale": 22,
   "morale_warning": true
  },
  {
   "name": "Ney",
   "location": "Franconia",
   "strength": 20940,
   "status": "en_route",
   "status_note": "Moving to Bohemia.",
   "arc_note": "",
   "idle_turns": 0,
   "danger": "",
   "trust": 69,
   "trust_notable": false,
   "morale": 85,
   "morale_warning": false
  },
  {
   "name": "Murat",
   "location": "Tyrol",
   "strength": 18067,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 0,
   "danger": "Starving \u2014 supply has failed at Tyrol two turns running.",
   "trust": 69,
   "trust_notable": false,
   "morale": 85,
   "morale_warning": false
  },
  {
   "name": "Lannes",
   "location": "Rhineland",
   "strength": 16505,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 1,
   "danger": "",
   "trust": 79,
   "trust_notable": false,
   "morale": 85,
   "morale_warning": false
  },
  {
   "name": "Bernadotte",
   "location": "Munich",
   "strength": 14479,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 2,
   "danger": "Starving \u2014 supply has failed at Munich two turns running.",
   "trust": 34,
   "trust_notable": true,
   "morale": 90,
   "morale_warning": false
  }
 ],
 "intelligence": [
  {
   "name": "Deroy",
   "location": "Dresden",
   "strength_display": "screening force",
   "visibility": "partial",
   "intel_turn": 5
  },
  {
   "name": "Mack",
   "location": "Berlin",
   "strength_display": "screening force",
   "visibility": "partial",
   "intel_turn": 5
  },
  {
   "name": "Brunswick",
   "location": "Berlin",
   "strength_display": "large force",
   "visibility": "partial",
   "intel_turn": 5
  },
  {
   "name": "Castanos",
   "location": "Artois",
   "strength_display": "small force",
   "visibility": "partial",
   "intel_turn": 5
  }
 ],
 "turn_events": [
  {
   "message": "Massena's army is recovering. Effectiveness penalty: 0% (recovered)",
   "severity": "good"
  },
  {
   "message": "Supply shortage at Tyrol: Soult loses 561 troops",
   "severity": "warning"
  },
  {
   "message": "Supply shortage at Tyrol: Murat loses 349 troops",
   "severity": "warning"
  },
  {
   "message": "Supply shortage at Munich: Bernadotte loses 197 troops",
   "severity": "warning"
  },
  {
   "message": "Supply shortage at Munich: Massena loses 298 troops",
   "severity": "warning"
  },
  {
   "message": "Switzerland loyalty 92 (-2): satellite drift \u2014 Invest in them, grant them
  autonomy, garrison their capital, or cede them a province to steady them.",
   "severity": "warning"
  }
 ],
 "headline": {
  "class": "supply_strain",
  "weight": 72,
  "text": "Sire \u2014 Bernadotte and Massena stand 36,371 men at Munich, which feeds 30,000. 6,371
  too many. 7,861 men lost in 3 turns. Munich already has its depot. Move a corps, or continue to
  pay.",
  "sub_beats": [
   "Sire \u2014 Tyrol has fallen to our arms. The tricolor flies over it this morning.",
   "Sire \u2014 our ally's marshal Deroy was broken at Hungary. Bavaria reels."
  ]
 },
 "berthier_note": "Men lost to the roads are lost for nothing, Sire. Either the province feeds them
  or we spread them.",
 "talleyrand_report": [
  {
   "message": "Sire, I believe Spain may be ready to discuss improved relations. The diplomatic
  winds favor us.",
   "trigger_type": "acceptance_crossed",
   "target_nation": "Spain",
   "priority": 2,
   "elaborate_type": "proposal_options"
  },
  {
   "message": "Sire, I believe Switzerland may be ready to discuss improved relations. The
  diplomatic winds favor us.",
   "trigger_type": "acceptance_crossed",
   "target_nation": "Switzerland",
   "priority": 2,
   "elaborate_type": "proposal_options"
  }
 ],
 "talleyrand_discovery": null,
 "talleyrand_override_note": null,
 "talleyrand_redemption": null,
 "coalition_status": {
  "threat_level": 83,
  "tier": "Formed",
  "sources": [
   {
    "source": "hegemony_passive",
    "amount": 1,
    "target": "France"
   },
   {
    "source": "decay",
    "amount": -3
   }
  ],
  "active_coalition": {
   "name": "Third Coalition",
   "leader": "Britain",
   "posture": "defensive",
   "formed_turn": 1,
   "members": [
    {
     "nation": "Austria",
     "war_exhaustion": 80,
     "strength_display": "48,302 men",
     "strength": 48302,
     "gold": 323
    },
    {
     "nation": "Britain",
     "war_exhaustion": 0,
     "strength_display": "Unknown",
     "strength": 0,
     "gold": 0
    },
    {
     "nation": "Russia",
     "war_exhaustion": 0,
     "strength_display": "Unknown",
     "strength": 0,
     "gold": 0
    }
   ]
  }
 },
 "diplomatic_events": [
  {
   "type": "diplomatic_dp_regen",
   "text": "Talleyrand reports: 5 diplomatic points available (base 3, +1 skill, +1 authority).",
   "priority": "LOW"
  },
  {
   "type": "agenda_shift",
   "text": "The court of Austria takes up a new design: Redeem Italy.",
   "priority": "MEDIUM"
  }
 ],
 "lapsed_offers": [
  {
   "nation": "PapalStates",
   "proposal_type": "friendly gift"
  },
  {
   "nation": "Hesse",
   "proposal_type": "non aggression"
  }
 ],
 "pending_envoy_count": 2,
 "pending_envoys": [
  {
   "nation": "KingdomOfItaly",
   "proposal_type": "request reward or restoration",
   "state": "ACTIVE"
  },
  {
   "nation": "Bavaria",
   "proposal_type": "request reward or restoration",
   "state": "WAITING"
  }
 ]
}
-- POPUP/DIALOGUE [notifications] --
   [
    {
     "id": "c9fdca21-9c08-4ec6-886a-3fe7a7f02fa8",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Ney grows bitter",
     "message": "Marshal Ney's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Ney",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Ney grows bitter",
     "repeat_count": 1
    },
    {
     "id": "ff90a7da-d536-4658-af81-bbd0a31ad89d",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Davout grows bitter",
     "message": "Marshal Davout's victories remain unrewarded (expects 240g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Davout",
      "expectation": 240,
      "satisfaction": 0,
      "shortfall": 240
     },
     "base_title": "Marshal Davout grows bitter",
     "repeat_count": 1
    },
    {
     "id": "823b437f-15a0-4fb9-8251-37ed3e1cd475",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Soult grows bitter",
     "message": "Marshal Soult's victories remain unrewarded (expects 120g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Soult",
      "expectation": 120,
      "satisfaction": 0,
      "shortfall": 120
     },
     "base_title": "Marshal Soult grows bitter",
     "repeat_count": 1
    },
    {
     "id": "160c5aa3-8ef9-46f4-9999-9f4232ea3bbf",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Lannes grows bitter",
     "message": "Marshal Lannes's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Lannes",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Lannes grows bitter",
     "repeat_count": 1
    },
    {
     "id": "ea9c2894-880f-4204-90ba-93891be05813",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Murat grows bitter",
     "message": "Marshal Murat's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Murat",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Murat grows bitter",
     "repeat_count": 1
    },
    {
     "id": "11eb075a-98d7-4a9b-94f1-ee058610f860",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Bernadotte grows bitter",
     "message": "Marshal Bernadotte's victories remain unrewarded (expects 160g/turn of estates;
     holds 0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014
     grant a rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Bernadotte",
      "expectation": 160,
      "satisfaction": 0,
      "shortfall": 160
     },
     "base_title": "Marshal Bernadotte grows bitter",
     "repeat_count": 1
    },
    {
     "id": "835f3e9f-0e7d-4381-959a-eeea75f12553",
     "type": "ally_settlement_petition",
     "priority": 1,
     "title": "KingdomOfItaly petitions over settlement scope",
     "message": "KingdomOfItaly petitions for the return of Milan.",
     "turn_created": 4,
     "details": {
      "review_target": "ally_settlement_petition_popup",
      "review_label": "Open Envoys",
      "war_id": "war_1",
      "petition_id":
     "ally_petition:request_reward_or_restoration:war_1:KingdomOfItaly::Austria:Milan",
      "petition_type": "request_reward_or_restoration",
      "ally_nation": "Kingdo

====================================================================================================
> Soult, support Ney
====================================================================================================
Soult moves to support Ney (at Franconia). Moves to Franconia. Soult will march to Ney's guns — he
  holds your written order. "Soult, support Ney." Understood to the letter. (1 AP — Soult executes
  precise orders with fewer couriers.)
   [cost=1  turn_advanced=False]
-- POPUP/DIALOGUE [marshal_petition] --
   {
    "kind": "rivalry_confrontation",
    "title": "A rivalry among the marshals",
    "body": "Sire, Ney has refused to attend council where Bernadotte is present. The breach may be
     beyond repair.",
    "speaker": "Ney",
    "options": [
     {
      "id": "accept_breach",
      "label": "Accept the Breach",
      "detail": "They settle into cold war; one may turn openly discontent.",
      "cost_note": "",
      "enabled": true
     },
     {
      "id": "force_reconciliation",
      "label": "Force Reconciliation",
      "detail": "A public gamble on your authority.",
      "cost_note": "2 AP",
      "ap_cost": 2,
      "enabled": true
     },
     {
      "id": "separate",
      "label": "Separate Them",
      "detail": "Not a fix \u2014 Berthier will warn you whenever their commands stand together.",
      "cost_note": "",
      "enabled": true
     }
    ],
    "context": {
     "marshal": "Ney",
     "other": "Bernadotte",
     "new_value": -2
    },
    "turn": 3
   }
-- POPUP/DIALOGUE [notifications] --
   [
    {
     "id": "c9fdca21-9c08-4ec6-886a-3fe7a7f02fa8",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Ney grows bitter",
     "message": "Marshal Ney's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Ney",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Ney grows bitter",
     "repeat_count": 1
    },
    {
     "id": "ff90a7da-d536-4658-af81-bbd0a31ad89d",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Davout grows bitter",
     "message": "Marshal Davout's victories remain unrewarded (expects 240g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Davout",
      "expectation": 240,
      "satisfaction": 0,
      "shortfall": 240
     },
     "base_title": "Marshal Davout grows bitter",
     "repeat_count": 1
    },
    {
     "id": "823b437f-15a0-4fb9-8251-37ed3e1cd475",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Soult grows bitter",
     "message": "Marshal Soult's victories remain unrewarded (expects 120g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Soult",
      "expectation": 120,
      "satisfaction": 0,
      "shortfall": 120
     },
     "base_title": "Marshal Soult grows bitter",
     "repeat_count": 1
    },
    {
     "id": "160c5aa3-8ef9-46f4-9999-9f4232ea3bbf",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Lannes grows bitter",
     "message": "Marshal Lannes's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Lannes",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Lannes grows bitter",
     "repeat_count": 1
    },
    {
     "id": "ea9c2894-880f-4204-90ba-93891be05813",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Murat grows bitter",
     "message": "Marshal Murat's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Murat",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Murat grows bitter",
     "repeat_count": 1
    },
    {
     "id": "11eb075a-98d7-4a9b-94f1-ee058610f860",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Bernadotte grows bitter",
     "message": "Marshal Bernadotte's victories remain unrewarded (expects 160g/turn of estates;
     holds 0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014
     grant a rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Bernadotte",
      "expectation": 160,
      "satisfaction": 0,
      "shortfall": 160
     },
     "base_title": "Marshal Bernadotte grows bitter",
     "repeat_count": 1
    },
    {
     "id": "835f3e9f-0e7d-4381-959a-eeea75f12553",
     "type": "ally_settlement_petition",
     "priority": 1,
     "title": "KingdomOfItaly petitions over settlement scope",
     "message": "KingdomOfItaly petitions for the return of Milan.",
     "turn_created": 4,
     "details": {
      "review_target": "ally_settlement_petition_popup",
      "review_label": "Open Envoys",
      "war_id": "war_1",
      "petition_id":
     "ally_petition:request_reward_or_restoration:war_1:KingdomOfItaly::Austria:Milan",
      "petition_type": "request_reward_or_restoration",
      "ally_nation": "Kingdo

====================================================================================================
> Massena, move to Milan
====================================================================================================
Massena moves from Munich to Milan (301 lost to march)
   [cost=1  turn_advanced=False]
   <event move> {"marshal": "Massena", "from": "Munich", "to": "Milan", "march_losses": 301}
-- POPUP/DIALOGUE [notifications] --
   [
    {
     "id": "c9fdca21-9c08-4ec6-886a-3fe7a7f02fa8",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Ney grows bitter",
     "message": "Marshal Ney's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Ney",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Ney grows bitter",
     "repeat_count": 1
    },
    {
     "id": "ff90a7da-d536-4658-af81-bbd0a31ad89d",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Davout grows bitter",
     "message": "Marshal Davout's victories remain unrewarded (expects 240g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Davout",
      "expectation": 240,
      "satisfaction": 0,
      "shortfall": 240
     },
     "base_title": "Marshal Davout grows bitter",
     "repeat_count": 1
    },
    {
     "id": "823b437f-15a0-4fb9-8251-37ed3e1cd475",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Soult grows bitter",
     "message": "Marshal Soult's victories remain unrewarded (expects 120g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Soult",
      "expectation": 120,
      "satisfaction": 0,
      "shortfall": 120
     },
     "base_title": "Marshal Soult grows bitter",
     "repeat_count": 1
    },
    {
     "id": "160c5aa3-8ef9-46f4-9999-9f4232ea3bbf",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Lannes grows bitter",
     "message": "Marshal Lannes's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Lannes",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Lannes grows bitter",
     "repeat_count": 1
    },
    {
     "id": "ea9c2894-880f-4204-90ba-93891be05813",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Murat grows bitter",
     "message": "Marshal Murat's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Murat",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Murat grows bitter",
     "repeat_count": 1
    },
    {
     "id": "11eb075a-98d7-4a9b-94f1-ee058610f860",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Bernadotte grows bitter",
     "message": "Marshal Bernadotte's victories remain unrewarded (expects 160g/turn of estates;
     holds 0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014
     grant a rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Bernadotte",
      "expectation": 160,
      "satisfaction": 0,
      "shortfall": 160
     },
     "base_title": "Marshal Bernadotte grows bitter",
     "repeat_count": 1
    },
    {
     "id": "835f3e9f-0e7d-4381-959a-eeea75f12553",
     "type": "ally_settlement_petition",
     "priority": 1,
     "title": "KingdomOfItaly petitions over settlement scope",
     "message": "KingdomOfItaly petitions for the return of Milan.",
     "turn_created": 4,
     "details": {
      "review_target": "ally_settlement_petition_popup",
      "review_label": "Open Envoys",
      "war_id": "war_1",
      "petition_id":
     "ally_petition:request_reward_or_restoration:war_1:KingdomOfItaly::Austria:Milan",
      "petition_type": "request_reward_or_restoration",
      "ally_nation": "Kingdo

====================================================================================================
> end turn
====================================================================================================
Turn 5 ended. (Warning: 2 action(s) unused) Turn 6 begins!

Income: 3430g | Occupation: -52g | Charges of Empire: -692g | Admiralty: -90g | Blockade: -250g |
  Upkeep: 1112g (incl. 24g over-limit) | Other: +1166g | Net: +2400g | Treasury: 12,777g
   [cost=0  turn_advanced=False]
   <event construction_complete> {"region": "Franconia", "building": "watchtower", "message": "Construction complete: Watchtower in Franconia!"}
   <event construction_complete> {"region": "Berlin", "building": "watchtower", "message": "Construction complete: Watchtower in Berlin!"}
   <event supply_attrition> {"marshal": "Mack", "nation": "Austria", "region": "Berlin", "losses": 16, "message": "Supply shortage at Berlin: Mack loses 16 troops"}
   <event supply_attrition> {"marshal": "Ney", "nation": "France", "region": "Tyrol", "losses": 695, "message": "Supply shortage at Tyrol: Ney loses 695 troops"}
   <event supply_attrition> {"marshal": "Murat", "nation": "France", "region": "Tyrol", "losses": 600, "message": "Supply shortage at Tyrol: Murat loses 600 troops"}
   <event supply_attrition> {"marshal": "Massena", "nation": "France", "region": "Tyrol", "losses": 717, "message": "Supply shortage at Tyrol: Massena loses 717 troops"}
   <event literal_fidelity> {"marshal": "Soult", "nation": "France", "location": "Franconia", "order_type": "SUPPORT", "message": "Soult holds at Franconia, per your orders \u2014 the guns at Tyrol did not move him."}
   <event garrison_regen> {"region": "Milan", "nation": "Austria", "old_strength": 16000, "new_strength": 18000, "message": "Garrison at Milan reinforced: 16,000 -> 18,000"}
   <event british_subsidy> {"recipient": "Austria", "payer": "Britain", "amount": 300, "war_id": "war_1", "subsidy_source_detail": "unique_eligible", "message": "Britain subsidizes Austria with 300 gold."}
   <event sponsorship_granted> {"kind": "sponsorship", "payer": "Britain", "recipient": "Austria", "aim": "France", "amount": 300, "turns": 10, "licence": false, "turn": 6}
   <event jealousy_resolved> {"message": "Soult's resentment of Lannes has cooled with time.", "nation": "France", "marshal": "Soult"}
   <event jealousy_resolved> {"message": "Lannes's resentment of Murat has cooled with time.", "nation": "France", "marshal": "Lannes"}
   <event jealousy_fired> {"message": "Berthier reports that Lannes resents Murat's laurels again, 3 turns after the last \u2014 he has grown impatient for something worth the doing.", "nation": "France", "marshal": "Lannes", "target": "Murat"}
   <event jealousy_escalation> {"message": "The rivalry between Lannes and Murat has become entrenched. The wound will not close on its own.", "nation": "France", "marshal": "Lannes", "target": "Murat"}
   <event jealousy_restlessness> {"message": "Berthier notes that Ney has grown restless \u2014 he has not seen laurels while Murat wins them. I recommend giving him meaningful orders soon.", "nation": "France", "marshal": "Ney"}
   <event glory_crowned> {"message": "Berthier notes that Murat's recent victories have made him the most celebrated commander in the army. (+1 shock, +1 defense, +1 administration while he holds the laurels)", "nation": "France", "marshal": "Murat"}
   <event intel_decayed> {"region": "Bern", "old_visibility": "stale", "new_visibility": "last_known"}
   <event strategic_progress> {"marshal": "Soult", "command": "SUPPORT", "order_status": "active", "message": "Soult is moving to support Ney (0 turn(s) remaining)."}

####################################################################################################
# THE ENEMY PHASE
####################################################################################################
-- Austria --
  - ArchdukeCharles moves to Vienna
      [move] {"type": "move", "marshal": "ArchdukeCharles", "from": "Moravia", "to": "Vienna"}
  - ArchdukeCharles moves to Bohemia
      [move] {"type": "move", "marshal": "ArchdukeCharles", "from": "Vienna", "to": "Bohemia", "march_losses": 1131}
  - ArchdukeCharles forms square
      [form_square] {"type": "form_square", "marshal": "ArchdukeCharles", "location": "Bohemia"}
  - ArchdukeCharles attacks Tyrol
      [battle] The Great Battle of Tyrol  -> defender_tactical_victory  victor=Murat
        ATK ArchdukeCharles  lost   4,452  left  32,131  morale  78
        DEF Murat            lost   1,939  left  17,489  morale  80
        defender order of battle: Murat 18,067(engaged); Massena 21,591(reinforced); Ney 20,940(reinforced); Soult 28,202(refused)
    [action_count] 4
-- Bavaria --
  - Deroy moves to Franconia
      [move] {"type": "move", "marshal": "Deroy", "from": "Dresden", "to": "Franconia"}
  - Deroy holds position
      [wait] {"type": "wait", "marshal": "Deroy", "location": "Franconia", "action_cost": 0}
  - Deroy recruits troops
      [recruit] {"type": "recruit", "marshal": "Deroy", "location": "Franconia", "recruit_type": "infantry", "troops_added": 3000, "gold_cost": 600, "morale_before": 20, "morale_after": 32, "new_strength": 4788, "stability_premium": false, "capital_discount": false, "intendance_pct": 0, "pool_before": 28762, "pool_
    [action_count] 4
[summary]
   ArchdukeCharles: move → Vienna
   ArchdukeCharles: move → Bohemia
   ArchdukeCharles: form_square
   ArchdukeCharles: attack → Tyrol
   Deroy: move → Franconia
   Deroy: wait
   Deroy: recruit → Franconia

####################################################################################################
# THE MORNING DISPATCH
####################################################################################################
{
 "turn": 6,
 "situation": {
  "player_regions": 29,
  "enemy_regions": 97,
  "treasury": 12777,
  "treasury_delta": 2288,
  "trade_income": 500,
  "occupation": 52,
  "contributions": 0,
  "state_charges": 900,
  "requisitions": 0,
  "overseas": 0,
  "dotation_skim": 0,
  "unmet_marshals": [
   {
    "marshal": "Ney",
    "expectation": 280,
    "satisfaction": 0,
    "shortfall": 280,
    "eroding": true,
    "grace_turns_left": 0,
    "pension": 0
   },
   {
    "marshal": "Davout",
    "expectation": 240,
    "satisfaction": 0,
    "shortfall": 240,
    "eroding": true,
    "grace_turns_left": 0,
    "pension": 0
   },
   {
    "marshal": "Soult",
    "expectation": 120,
    "satisfaction": 0,
    "shortfall": 120,
    "eroding": true,
    "grace_turns_left": 0,
    "pension": 0
   },
   {
    "marshal": "Lannes",
    "expectation": 200,
    "satisfaction": 0,
    "shortfall": 200,
    "eroding": true,
    "grace_turns_left": 0,
    "pension": 0
   },
   {
    "marshal": "Murat",
    "expectation": 240,
    "satisfaction": 0,
    "shortfall": 240,
    "eroding": true,
    "grace_turns_left": 0,
    "pension": 0
   },
   {
    "marshal": "Bernadotte",
    "expectation": 160,
    "satisfaction": 0,
    "shortfall": 160,
    "eroding": true,
    "grace_turns_left": 0,
    "pension": 0
   },
   {
    "marshal": "Massena",
    "expectation": 80,
    "satisfaction": 0,
    "shortfall": 80,
    "eroding": false,
    "grace_turns_left": 2,
    "pension": 0
   }
  ],
  "rente_cost": 0,
  "expectation_rises": [
   {
    "marshal": "Ney",
    "expectation": 280,
    "previous": 200,
    "satisfaction": 0
   },
   {
    "marshal": "Murat",
    "expectation": 240,
    "previous": 200,
    "satisfaction": 0
   },
   {
    "marshal": "Massena",
    "expectation": 80,
    "previous": 0,
    "satisfaction": 0
   }
  ],
  "blockade": 250,
  "admiralty": 90,
  "upkeep_surcharge": 24,
  "force_limit": 132500,
  "over_force_limit": true,
  "bankrupt": false,
  "strength_ratio_pct": 1,
  "authority": 100,
  "authority_label": "Strong"
 },
 "marshals": [
  {
   "name": "Soult",
   "location": "Franconia",
   "strength": 28202,
   "status": "en_route",
   "status_note": "Supporting Ney. (to the letter)",
   "arc_note": "",
   "idle_turns": 0,
   "danger": "Starving \u2014 supply has failed at Franconia two turns running.",
   "trust": 61,
   "trust_notable": false,
   "morale": 90,
   "morale_warning": false
  },
  {
   "name": "Davout",
   "location": "Frankfurt",
   "strength": 23415,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 3,
   "danger": "",
   "trust": 79,
   "trust_notable": false,
   "morale": 85,
   "morale_warning": false
  },
  {
   "name": "Massena",
   "location": "Tyrol",
   "strength": 20183,
   "status": "awaiting",
   "status_note": "Hunted by Archduke Charles across 1 frontier \u2014 stands at Tyrol with 20,183
  men.",
   "arc_note": "Hunted by Archduke Charles across 1 frontier \u2014 stands at Tyrol with 20,183
  men.",
   "idle_turns": 0,
   "danger": "Morale failing (17) \u2014 the men waver.",
   "trust": 60,
   "trust_notable": false,
   "morale": 17,
   "morale_warning": true
  },
  {
   "name": "Ney",
   "location": "Tyrol",
   "strength": 19575,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 1,
   "danger": "",
   "trust": 66,
   "trust_notable": false,
   "morale": 80,
   "morale_warning": false
  },
  {
   "name": "Murat",
   "location": "Tyrol",
   "strength": 16889,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 1,
   "danger": "Starving \u2014 supply has failed at Tyrol two turns running.",
   "trust": 66,
   "trust_notable": false,
   "morale": 80,
   "morale_warning": false
  },
  {
   "name": "Lannes",
   "location": "Rhineland",
   "strength": 16505,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 2,
   "danger": "",
   "trust": 76,
   "trust_notable": false,
   "morale": 85,
   "morale_warning": false
  },
  {
   "name": "Bernadotte",
   "location": "Munich",
   "strength": 14479,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 3,
   "danger": "Starving \u2014 supply has failed at Munich two turns running.",
   "trust": 31,
   "trust_notable": true,
   "morale": 90,
   "morale_warning": false
  }
 ],
 "intelligence": [
  {
   "name": "Deroy",
   "location": "Franconia",
   "strength_display": "4,788",
   "visibility": "full",
   "intel_turn": 6
  },
  {
   "name": "Mack",
   "location": "Berlin",
   "strength_display": "1,449",
   "visibility": "full",
   "intel_turn": 5
  },
  {
   "name": "Brunswick",
   "location": "Berlin",
   "strength_display": "50,000",
   "visibility": "full",
   "intel_turn": 5
  },
  {
   "name": "Castanos",
   "location": "Gascony",
   "strength_display": "small force",
   "visibility": "partial",
   "intel_turn": 6
  }
 ],
 "turn_events": [
  {
   "message": "Supply shortage at Tyrol: Ney loses 695 troops",
   "severity": "warning"
  },
  {
   "message": "Supply shortage at Tyrol: Murat loses 600 troops",
   "severity": "warning"
  },
  {
   "message": "Supply shortage at Tyrol: Massena loses 717 troops",
   "severity": "warning"
  },
  {
   "message": "Soult holds at Franconia, per your orders \u2014 the guns at Tyrol did not move
  him.",
   "severity": "info"
  },
  {
   "message": "Soult's resentment of Lannes has cooled with time.",
   "severity": "good"
  },
  {
   "message": "Lannes's resentment of Murat has cooled with time.",
   "severity": "good"
  },
  {
   "message": "Berthier reports that Lannes resents Murat's laurels again, 3 turns after the last
  \u2014 he has grown impatient for something worth the doing.",
   "severity": "warning"
  },
  {
   "message": "The rivalry between Lannes and Murat has become entrenched. The wound will not close
  on its own.",
   "severity": "warning"
  },
  {
   "message": "Berthier notes that Ney has grown restless \u2014 he has not seen laurels while Murat
  wins them. I recommend giving him meaningful orders soon.",
   "severity": "info"
  },
  {
   "message": "Berthier notes that Murat's recent victories have made him the most celebrated
  commander in the army. (+1 shock, +1 defense, +1 administration while he holds the laurels)",
   "severity": "good"
  }
 ],
 "headline": {
  "class": "supply_strain",
  "weight": 72,
  "text": "Sire \u2014 Ney, Murat and Massena stand 56,647 men at Tyrol, which feeds 30,000. 26,647
  too many. 2,922 men lost in 2 turns. A supply depot at Tyrol would ease it; dispersing a corps
  would end it.",
  "sub_beats": [
   "Sire \u2014 Marshal Ney's household goes unpaid. His patience erodes with his purse."
  ]
 },
 "berthier_note": "Men lost to the roads are lost for nothing, Sire. Either the province feeds them
  or we spread them.",
 "talleyrand_report": [
  {
   "message": "Sire, the diplomatic front has been quiet. Perhaps too quiet. Shall I assess our
  options?",
   "trigger_type": "idle_nudge",
   "target_nation": "",
   "priority": 5,
   "elaborate_type": "proposal_options"
  }
 ],
 "talleyrand_discovery": null,
 "talleyrand_override_note": null,
 "talleyrand_redemption": null,
 "coalition_status": {
  "threat_level": 81,
  "tier": "Formed",
  "sources": [
   {
    "source": "hegemony_passive",
    "amount": 1,
    "target": "France"
   },
   {
    "source": "decay",
    "amount": -3
   }
  ],
  "active_coalition": {
   "name": "Third Coalition",
   "leader": "Britain",
   "posture": "defensive",
   "formed_turn": 1,
   "members": [
    {
     "nation": "Austria",
     "war_exhaustion": 92,
     "strength_display": "42,703 men",
     "strength": 42703,
     "gold": 1313
    },
    {
     "nation": "Britain",
     "war_exhaustion": 0,
     "strength_display": "Unknown",
     "strength": 0,
     "gold": 0
    },
    {
     "nation": "Russia",
     "war_exhaustion": 0,
     "strength_display": "Unknown",
     "strength": 0,
     "gold": 0
    }
   ]
  }
 },
 "diplomatic_events": [
  {
   "type": "diplomatic_dp_regen",
   "text": "Talleyrand reports: 5 diplomatic points available (base 3, +1 skill, +1 authority).",
   "priority": "LOW"
  },
  {
   "type": "paymaster_subsidy",
   "text": "Britain's gold reaches Austria \u2014 the subsidy stands at 300 this season.",
   "priority": "MEDIUM"
  },
  {
   "type": "design_promoted",
   "text": "REVANCHE: Spain will not forgive Britain the loss of Aragon and 2 more provinces. A new
  design hardens in their court.",
   "priority": "HIGH"
  },
  {
   "type": "agenda_shift",
   "text": "The court of Spain takes up a new design: Revanche.",
   "priority": "MEDIUM"
  }
 ],
 "pending_envoy_count": 2,
 "pending_envoys": [
  {
   "nation": "KingdomOfItaly",
   "proposal_type": "request reward or restoration",
   "state": "ACTIVE"
  },
  {
   "nation": "Bavaria",
   "proposal_type": "request reward or restoration",
   "state": "WAITING"
  }
 ]
}
-- POPUP/DIALOGUE [notifications] --
   [
    {
     "id": "c9fdca21-9c08-4ec6-886a-3fe7a7f02fa8",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Ney grows bitter",
     "message": "Marshal Ney's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Ney",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Ney grows bitter",
     "repeat_count": 1
    },
    {
     "id": "ff90a7da-d536-4658-af81-bbd0a31ad89d",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Davout grows bitter",
     "message": "Marshal Davout's victories remain unrewarded (expects 240g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Davout",
      "expectation": 240,
      "satisfaction": 0,
      "shortfall": 240
     },
     "base_title": "Marshal Davout grows bitter",
     "repeat_count": 1
    },
    {
     "id": "823b437f-15a0-4fb9-8251-37ed3e1cd475",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Soult grows bitter",
     "message": "Marshal Soult's victories remain unrewarded (expects 120g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Soult",
      "expectation": 120,
      "satisfaction": 0,
      "shortfall": 120
     },
     "base_title": "Marshal Soult grows bitter",
     "repeat_count": 1
    },
    {
     "id": "160c5aa3-8ef9-46f4-9999-9f4232ea3bbf",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Lannes grows bitter",
     "message": "Marshal Lannes's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Lannes",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Lannes grows bitter",
     "repeat_count": 1
    },
    {
     "id": "ea9c2894-880f-4204-90ba-93891be05813",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Murat grows bitter",
     "message": "Marshal Murat's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Murat",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Murat grows bitter",
     "repeat_count": 1
    },
    {
     "id": "11eb075a-98d7-4a9b-94f1-ee058610f860",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Bernadotte grows bitter",
     "message": "Marshal Bernadotte's victories remain unrewarded (expects 160g/turn of estates;
     holds 0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014
     grant a rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Bernadotte",
      "expectation": 160,
      "satisfaction": 0,
      "shortfall": 160
     },
     "base_title": "Marshal Bernadotte grows bitter",
     "repeat_count": 1
    },
    {
     "id": "835f3e9f-0e7d-4381-959a-eeea75f12553",
     "type": "ally_settlement_petition",
     "priority": 1,
     "title": "KingdomOfItaly petitions over settlement scope",
     "message": "KingdomOfItaly petitions for the return of Milan.",
     "turn_created": 4,
     "details": {
      "review_target": "ally_settlement_petition_popup",
      "review_label": "Open Envoys",
      "war_id": "war_1",
      "petition_id":
     "ally_petition:request_reward_or_restoration:war_1:KingdomOfItaly::Austria:Milan",
      "petition_type": "request_reward_or_restoration",
      "ally_nation": "Kingdo

====================================================================================================
> build a supply depot at Tyrol
====================================================================================================
Cannot build in Tyrol — region stability too low (35/100). Need 51+.
   [cost=0  turn_advanced=False]
-- POPUP/DIALOGUE [marshal_petition] --
   {
    "kind": "rivalry_confrontation",
    "title": "A rivalry among the marshals",
    "body": "Sire, Ney has refused to attend council where Bernadotte is present. The breach may be
     beyond repair.",
    "speaker": "Ney",
    "options": [
     {
      "id": "accept_breach",
      "label": "Accept the Breach",
      "detail": "They settle into cold war; one may turn openly discontent.",
      "cost_note": "",
      "enabled": true
     },
     {
      "id": "force_reconciliation",
      "label": "Force Reconciliation",
      "detail": "A public gamble on your authority.",
      "cost_note": "2 AP",
      "ap_cost": 2,
      "enabled": true
     },
     {
      "id": "separate",
      "label": "Separate Them",
      "detail": "Not a fix \u2014 Berthier will warn you whenever their commands stand together.",
      "cost_note": "",
      "enabled": true
     }
    ],
    "context": {
     "marshal": "Ney",
     "other": "Bernadotte",
     "new_value": -2
    },
    "turn": 3
   }
-- POPUP/DIALOGUE [notifications] --
   [
    {
     "id": "c9fdca21-9c08-4ec6-886a-3fe7a7f02fa8",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Ney grows bitter",
     "message": "Marshal Ney's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Ney",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Ney grows bitter",
     "repeat_count": 1
    },
    {
     "id": "ff90a7da-d536-4658-af81-bbd0a31ad89d",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Davout grows bitter",
     "message": "Marshal Davout's victories remain unrewarded (expects 240g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Davout",
      "expectation": 240,
      "satisfaction": 0,
      "shortfall": 240
     },
     "base_title": "Marshal Davout grows bitter",
     "repeat_count": 1
    },
    {
     "id": "823b437f-15a0-4fb9-8251-37ed3e1cd475",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Soult grows bitter",
     "message": "Marshal Soult's victories remain unrewarded (expects 120g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Soult",
      "expectation": 120,
      "satisfaction": 0,
      "shortfall": 120
     },
     "base_title": "Marshal Soult grows bitter",
     "repeat_count": 1
    },
    {
     "id": "160c5aa3-8ef9-46f4-9999-9f4232ea3bbf",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Lannes grows bitter",
     "message": "Marshal Lannes's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Lannes",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Lannes grows bitter",
     "repeat_count": 1
    },
    {
     "id": "ea9c2894-880f-4204-90ba-93891be05813",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Murat grows bitter",
     "message": "Marshal Murat's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Murat",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Murat grows bitter",
     "repeat_count": 1
    },
    {
     "id": "11eb075a-98d7-4a9b-94f1-ee058610f860",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Bernadotte grows bitter",
     "message": "Marshal Bernadotte's victories remain unrewarded (expects 160g/turn of estates;
     holds 0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014
     grant a rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Bernadotte",
      "expectation": 160,
      "satisfaction": 0,
      "shortfall": 160
     },
     "base_title": "Marshal Bernadotte grows bitter",
     "repeat_count": 1
    },
    {
     "id": "835f3e9f-0e7d-4381-959a-eeea75f12553",
     "type": "ally_settlement_petition",
     "priority": 1,
     "title": "KingdomOfItaly petitions over settlement scope",
     "message": "KingdomOfItaly petitions for the return of Milan.",
     "turn_created": 4,
     "details": {
      "review_target": "ally_settlement_petition_popup",
      "review_label": "Open Envoys",
      "war_id": "war_1",
      "petition_id":
     "ally_petition:request_reward_or_restoration:war_1:KingdomOfItaly::Austria:Milan",
      "petition_type": "request_reward_or_restoration",
      "ally_nation": "Kingdo

====================================================================================================
> Murat, attack Bohemia
====================================================================================================
MUSTER — Murat (16,889; 43,778 with the muster committed) vs ArchdukeCharles (32,131 men) at Bohemia
  — the balance of force looks favorable.
  WILL JOIN — Ney: will march to the sound of the guns
  WILL NOT — Soult: awaits explicit orders and will NOT march — order 'Soult, support Murat' and he
  will march
  WILL JOIN — Massena: will march to the sound of the guns


[Combat] Murat leads the charge! (Aggressive: +15% attack)
[Cavalry] Murat's cavalry thrives on Plains terrain! (120% effectiveness)
[Combat] Murat's combined arms coordination! (+10% attack)
[Combat] Adjacent allies bolster Murat's attack! (+4%)
Murat launches a decisive assault. Brutal stalemate between Murat and ArchdukeCharles. Heavy
  casualties on both sides: Murat's army 3,819, ArchdukeCharles's army 3,140.
[Materiel] Guns, horses and stores lost with the fallen: France -190g, Austria -157g.
[!] Massena's broken army flees to Tyrol! (181 lost to march) (recovering for 3 turns)
[!] ArchdukeJohn's broken army flees to Vienna! (recovering for 3 turns)
   [cost=1  turn_advanced=False]
   <event battle> {"battle_name": "Second Battle of Bohemia", "attacker": {"name": "Murat", "casualties": 3819, "remaining": 15150, "morale": 73, "forced_retreat": false}, "defender": {"name": "ArchdukeCharles", "casualties": 3140, "remaining": 29686, "morale": 78, "forced_retreat": false}, "attacker_nation": "France", "defender_nation": "Austria", "outcome": "stalemate", "victor": null, "enemy_destroyed": false, "region_conquered": false, "region_name": null, "flanking_bonus": 0, "flanking_origins": ["Tyrol"], "vindication": null, "attacker_forced_retreat": false, "defender_forced_retreat": false, "cavalry_ter
-- REINFORCEMENTS --
   [
    "Ney could not reach the battlefield in time.",
    "Soult awaits explicit orders and did not march to the sound of the guns.",
    "Massena's forces arrived to reinforce Murat!",
    "Massed effective strength: 16,889 (lead) + 9,330 committed (Massena) = 26,219.",
    "His supporting ally lost 2,080 men.",
    "ArchdukeCharles was reinforced \u2014 massed effective strength: 32,131 (lead) + 4,800
     committed (ArchdukeJohn) = 36,931.",
    "ArchdukeCharles's supporting ally lost 695 men."
   ]
-- BERTHIER'S AFTER-ACTION REPORT --
   {
    "modifier_breakdown": {
     "attacker": [
      {
       "label": "Personality (aggressive)",
       "value": 15,
       "type": "bonus"
      },
      {
       "label": "Recklessness",
       "value": 5,
       "type": "bonus"
      },
      {
       "label": "Cavalry terrain (plains)",
       "value": 20,
       "type": "bonus"
      }
     ],
     "defender": [
      {
       "label": "Habsburg Resolve",
       "value": 3,
       "type": "bonus"
      }
     ]
    },
    "casualty_summary": {
     "attacker_name": "Murat",
     "attacker_original": 16889,
     "attacker_casualties": 1739,
     "attacker_remaining": 15150,
     "defender_name": "ArchdukeCharles",
     "defender_original": 32131,
     "defender_casualties": 2445,
     "defender_remaining": 29686
    },
    "observation": "Massena's timely arrival aided Murat. Ney and Soult, however, were conspicuously
     absent.",
    "enemy_voice": "Archduke Charles: \"France pays full price for every Austrian mile now.\"",
    "marshal_voice": "Murat: \"We traded blood for nothing. I want tomorrow.\""
   }
-- POPUP/DIALOGUE [battle_diorama] --
   {
    "battle_name": "Second Battle of Bohemia",
    "region": "Bohemia",
    "turn": 6,
    "outcome": "stalemate",
    "victor": null,
    "attacker_nation": "France",
    "defender_nation": "Austria",
    "player_side": "attacker",
    "register": "grim",
    "significant": true,
    "dramatic": true,
    "great_battle": false,
    "region_conquered": false,
    "attacker": {
     "contingents": [
      {
       "name": "Murat",
       "nation": "France",
       "arm": "cavalry",
       "committed": 16889,
       "casualties": 1739,
       "remaining": 15150,
       "status": "engaged",
       "lead": true,
       "crowned": true
      },
      {
       "name": "Massena",
       "nation": "France",
       "arm": "infantry",
       "committed": 20183,
       "casualties": 2080,
       "remaining": 18103,
       "status": "reinforced",
       "lead": false,
       "crowned": false
      },
      {
       "name": "Ney",
       "nation": "France",
       "arm": "infantry",
       "committed": 19575,
       "casualties": 0,
       "remaining": 19575,
       "status": "failed_arrive",
       "lead": false,
       "crowned": false,
       "absence_reason": "could not reach the field"
      },
      {
       "name": "Soult",
       "nation": "France",
       "arm": "infantry",
       "committed": 28202,
       "casualties": 0,
       "remaining": 28202,
       "status": "refused",
       "lead": false,
       "crowned": false,
       "absence_reason": "awaits explicit orders"
      }
     ],
     "reserve_count": 0,
     "casualties_total": 3819,
     "committed_total": 37072,
     "nation": "France"
    },
    "defender": {
     "contingents": [
      {
       "name": "ArchdukeCharles",
       "nation": "Austria",
       "arm": "infantry",
       "committed": 32131,
       "casualties": 2445,
       "remaining": 29686,
       "status": "engaged",
       "lead": true,
       "crowned": true
      },
      {
       "name": "ArchdukeJohn",
       "nation": "Austria",
       "arm": "infantry",
       "committed": 9139,
       "casualties": 695,
       "remaining": 8444,
       "status": "reinforced",
       "lead": false,
       "crowned": false
      }
     ],
     "reserve_count": 0,
     "casualties_total": 3140,
     "committed_total": 41270,
     "nation": "Austria"
    },
    "observation": "Massena's timely arrival aided Murat. Ney and Soult, however, were conspicuously
     absent.",
    "enemy_voice": "Archduke Charles: \"France pays full price for every Austrian mile now.\""
   }
-- POPUP/DIALOGUE [notifications] --
   [
    {
     "id": "c9fdca21-9c08-4ec6-886a-3fe7a7f02fa8",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Ney grows bitter",
     "message": "Marshal Ney's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Ney",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Ney grows bitter",
     "repeat_count": 1
    },
    {
     "id": "ff90a7da-d536-4658-af81-bbd0a31ad89d",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Davout grows bitter",
     "message": "Marshal Davout's victories remain unrewarded (expects 240g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Davout",
      "expectation": 240,
      "satisfaction": 0,
      "shortfall": 240
     },
     "base_title": "Marshal Davout grows bitter",
     "repeat_count": 1
    },
    {
     "id": "823b437f-15a0-4fb9-8251-37ed3e1cd475",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Soult grows bitter",
     "message": "Marshal Soult's victories remain unrewarded (expects 120g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Soult",
      "expectation": 120,
      "satisfaction": 0,
      "shortfall": 120
     },
     "base_title": "Marshal Soult grows bitter",
     "repeat_count": 1
    },
    {
     "id": "160c5aa3-8ef9-46f4-9999-9f4232ea3bbf",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Lannes grows bitter",
     "message": "Marshal Lannes's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Lannes",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Lannes grows bitter",
     "repeat_count": 1
    },
    {
     "id": "ea9c2894-880f-4204-90ba-93891be05813",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Murat grows bitter",
     "message": "Marshal Murat's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Murat",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Murat grows bitter",
     "repeat_count": 1
    },
    {
     "id": "11eb075a-98d7-4a9b-94f1-ee058610f860",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Bernadotte grows bitter",
     "message": "Marshal Bernadotte's victories remain unrewarded (expects 160g/turn of estates;
     holds 0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014
     grant a rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Bernadotte",
      "expectation": 160,
      "satisfaction": 0,
      "shortfall": 160
     },
     "base_title": "Marshal Bernadotte grows bitter",
     "repeat_count": 1
    },
    {
     "id": "835f3e9f-0e7d-4381-959a-eeea75f12553",
     "type": "ally_settlement_petition",
     "priority": 1,
     "title": "KingdomOfItaly petitions over settlement scope",
     "message": "KingdomOfItaly petitions for the return of Milan.",
     "turn_created": 4,
     "details": {
      "review_target": "ally_settlement_petition_popup",
      "review_label": "Open Envoys",
      "war_id": "war_1",
      "petition_id":
     "ally_petition:request_reward_or_restoration:war_1:KingdomOfItaly::Austria:Milan",
      "petition_type": "request_reward_or_restoration",
      "ally_nation": "Kingdo

====================================================================================================
> Soult, support Murat
====================================================================================================
Soult moves to support Murat (at Tyrol). Moves to Tyrol. Soult will march to Murat's guns — he holds
  your written order. "Soult, support Murat." Understood to the letter. (1 AP — Soult executes
  precise orders with fewer couriers.)
   [cost=1  turn_advanced=False]
-- POPUP/DIALOGUE [notifications] --
   [
    {
     "id": "c9fdca21-9c08-4ec6-886a-3fe7a7f02fa8",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Ney grows bitter",
     "message": "Marshal Ney's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Ney",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Ney grows bitter",
     "repeat_count": 1
    },
    {
     "id": "ff90a7da-d536-4658-af81-bbd0a31ad89d",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Davout grows bitter",
     "message": "Marshal Davout's victories remain unrewarded (expects 240g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Davout",
      "expectation": 240,
      "satisfaction": 0,
      "shortfall": 240
     },
     "base_title": "Marshal Davout grows bitter",
     "repeat_count": 1
    },
    {
     "id": "823b437f-15a0-4fb9-8251-37ed3e1cd475",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Soult grows bitter",
     "message": "Marshal Soult's victories remain unrewarded (expects 120g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Soult",
      "expectation": 120,
      "satisfaction": 0,
      "shortfall": 120
     },
     "base_title": "Marshal Soult grows bitter",
     "repeat_count": 1
    },
    {
     "id": "160c5aa3-8ef9-46f4-9999-9f4232ea3bbf",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Lannes grows bitter",
     "message": "Marshal Lannes's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Lannes",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Lannes grows bitter",
     "repeat_count": 1
    },
    {
     "id": "ea9c2894-880f-4204-90ba-93891be05813",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Murat grows bitter",
     "message": "Marshal Murat's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Murat",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Murat grows bitter",
     "repeat_count": 1
    },
    {
     "id": "11eb075a-98d7-4a9b-94f1-ee058610f860",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Bernadotte grows bitter",
     "message": "Marshal Bernadotte's victories remain unrewarded (expects 160g/turn of estates;
     holds 0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014
     grant a rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Bernadotte",
      "expectation": 160,
      "satisfaction": 0,
      "shortfall": 160
     },
     "base_title": "Marshal Bernadotte grows bitter",
     "repeat_count": 1
    },
    {
     "id": "835f3e9f-0e7d-4381-959a-eeea75f12553",
     "type": "ally_settlement_petition",
     "priority": 1,
     "title": "KingdomOfItaly petitions over settlement scope",
     "message": "KingdomOfItaly petitions for the return of Milan.",
     "turn_created": 4,
     "details": {
      "review_target": "ally_settlement_petition_popup",
      "review_label": "Open Envoys",
      "war_id": "war_1",
      "petition_id":
     "ally_petition:request_reward_or_restoration:war_1:KingdomOfItaly::Austria:Milan",
      "petition_type": "request_reward_or_restoration",
      "ally_nation": "Kingdo

====================================================================================================
> end turn
====================================================================================================
Turn 6 ended. (Warning: 2 action(s) unused) Turn 7 begins!

Income: 3427g | Occupation: -52g | Charges of Empire: -912g | Admiralty: -90g | Blockade: -250g |
  Upkeep: 1000g | Other: +1193g | Net: +2316g | Treasury: 14,903g
   [cost=0  turn_advanced=False]
   <event retreat_recovery> {"marshal": "Massena", "nation": "France", "stage": 1, "penalty": "-40%", "message": "Massena's army is recovering. Effectiveness penalty: -40% The rout's disorder lingers in the ranks."}
   <event construction_complete> {"region": "Munich", "building": "watchtower", "message": "Construction complete: Watchtower in Munich!"}
   <event supply_attrition> {"marshal": "Mack", "nation": "Austria", "region": "Berlin", "losses": 15, "message": "Supply shortage at Berlin: Mack loses 15 troops"}
   <event supply_attrition> {"marshal": "Ney", "nation": "France", "region": "Tyrol", "losses": 1032, "message": "Supply shortage at Tyrol: Ney loses 1,032 troops"}
   <event supply_attrition> {"marshal": "Soult", "nation": "France", "region": "Tyrol", "losses": 1409, "message": "Supply shortage at Tyrol: Soult loses 1,409 troops"}
   <event supply_attrition> {"marshal": "Murat", "nation": "France", "region": "Tyrol", "losses": 799, "message": "Supply shortage at Tyrol: Murat loses 799 troops"}
   <event supply_attrition> {"marshal": "Massena", "nation": "France", "region": "Tyrol", "losses": 967, "message": "Supply shortage at Tyrol: Massena loses 967 troops"}
   <event literal_fidelity> {"marshal": "Soult", "nation": "France", "location": "Tyrol", "order_type": "SUPPORT", "message": "Soult holds at Tyrol, per your orders \u2014 the guns at Bohemia did not move him."}
   <event garrison_regen> {"region": "Milan", "nation": "Austria", "old_strength": 18000, "new_strength": 20000, "message": "Garrison at Milan reinforced: 18,000 -> 20,000"}
   <event british_subsidy> {"recipient": "Austria", "payer": "Britain", "amount": 300, "war_id": "war_1", "subsidy_source_detail": "unique_eligible", "message": "Britain subsidizes Austria with 300 gold."}
   <event ai_ai_rivalry> {"nations": ["Britain", "Portugal"], "message": "Territorial rivalry between Britain and Portugal grows."}
   <event ai_ai_rivalry> {"nations": ["Russia", "Prussia"], "message": "Territorial rivalry between Russia and Prussia grows."}
   <event ai_ai_downgrade> {"nations": ["Russia", "Sweden"], "from_state": "OPEN_BORDERS", "to_state": "PEACE", "message": "Russia has downgraded relations with Sweden: OPEN_BORDERS \u2192 PEACE."}
   <event sponsorship_granted> {"kind": "sponsorship", "payer": "Britain", "recipient": "Sardinia", "aim": "France", "amount": 300, "turns": 10, "licence": false, "turn": 7}
   <event jealousy_restlessness> {"message": "Berthier notes that Davout has grown restless \u2014 he has not seen laurels while Soult wins them. I recommend giving him meaningful orders soon.", "nation": "France", "marshal": "Davout"}
   <event glory_crown_lost> {"message": "Murat is no longer the army's most celebrated commander \u2014 the laurels have passed.", "nation": "France", "marshal": "Murat"}
   <event jealousy_separation_warning> {"message": "Berthier reminds you: Bernadotte and Ney now stand within reach of each other. You asked to be warned.", "nation": "France", "marshal": "Bernadotte"}
   <event fontainebleau_petition> {"message": "The marshals have come together, Sire \u2014 a collective petition awaits your answer.", "nation": "France"}
   <event intel_decayed> {"region": "Moravia", "old_visibility": "full", "new_visibility": "stale"}
   <event intel_decayed> {"region": "Hungary", "old_visibility": "full", "new_visibility": "stale"}
   <event strategic_progress> {"marshal": "Soult", "command": "SUPPORT", "order_status": "active", "message": "Soult is moving to support Murat (0 turn(s) remaining)."}

####################################################################################################
# THE ENEMY PHASE
####################################################################################################
-- Austria --
  - Mack defends
      [fortified] {"type": "fortified", "marshal": "Mack", "location": "Berlin", "defense_bonus": 2, "personality_bonus": ""}
  - ArchdukeCharles forms square
      [form_square] {"type": "form_square", "marshal": "ArchdukeCharles", "location": "Bohemia"}
  - ArchdukeCharles attacks Deroy
      [battle] Battle of Franconia  -> attacker_tactical_victory  victor=ArchdukeCharles
        ATK ArchdukeCharles  lost     207  left  29,479  morale  78
        DEF Deroy            lost   2,971  left   1,817  morale   0  ROUTED
        REGION TAKEN: Franconia
  - ArchdukeCharles attacks Ney
      [battle] Second Battle of Tyrol  -> defender_tactical_victory  victor=Ney
        ATK ArchdukeCharles  lost   5,157  left  23,469  morale  33
        DEF Ney              lost   1,390  left  19,133  morale  75
        defender order of battle: Ney 19,575(engaged); Soult 26,713(engaged); Murat 15,150(engaged)
  - ArchdukeCharles changes stance to defensive
      [stance_change] {"type": "stance_change", "marshal": "ArchdukeCharles", "from_stance": "neutral", "to_stance": "defensive", "action_cost": 1}
    [action_count] 5
-- Prussia --
  - Brunswick holds position
      [wait] {"type": "wait", "marshal": "Brunswick", "location": "Berlin", "action_cost": 0}
    [action_count] 1
-- Bavaria --
  - Deroy holds position
      [wait] {"type": "wait", "marshal": "Deroy", "location": "Munich", "action_cost": 0}
  - Deroy recruits troops
      [recruit] {"type": "recruit", "marshal": "Deroy", "location": "Munich", "recruit_type": "infantry", "troops_added": 10000, "gold_cost": 450, "morale_before": 10, "morale_after": 35, "new_strength": 11817, "stability_premium": false, "capital_discount": true, "intendance_pct": 0, "pool_before": 27574, "pool_af
    [action_count] 3
[summary]
   Mack: defend
   ArchdukeCharles: form_square
   ArchdukeCharles: attack → Deroy
   ArchdukeCharles: attack → Ney
   ArchdukeCharles: stance_change → defensive
   Brunswick: wait
   Deroy: wait
   Deroy: recruit → Munich

####################################################################################################
# THE MORNING DISPATCH
####################################################################################################
{
 "turn": 7,
 "situation": {
  "player_regions": 29,
  "enemy_regions": 97,
  "treasury": 14903,
  "treasury_delta": 2178,
  "trade_income": 500,
  "occupation": 52,
  "contributions": 0,
  "state_charges": 1119,
  "requisitions": 0,
  "overseas": 0,
  "dotation_skim": 0,
  "unmet_marshals": [
   {
    "marshal": "Ney",
    "expectation": 300,
    "satisfaction": 0,
    "shortfall": 300,
    "eroding": true,
    "grace_turns_left": 0,
    "pension": 0
   },
   {
    "marshal": "Davout",
    "expectation": 240,
    "satisfaction": 0,
    "shortfall": 240,
    "eroding": true,
    "grace_turns_left": 0,
    "pension": 0
   },
   {
    "marshal": "Soult",
    "expectation": 160,
    "satisfaction": 0,
    "shortfall": 160,
    "eroding": true,
    "grace_turns_left": 0,
    "pension": 0
   },
   {
    "marshal": "Lannes",
    "expectation": 200,
    "satisfaction": 0,
    "shortfall": 200,
    "eroding": true,
    "grace_turns_left": 0,
    "pension": 0
   },
   {
    "marshal": "Murat",
    "expectation": 280,
    "satisfaction": 0,
    "shortfall": 280,
    "eroding": true,
    "grace_turns_left": 0,
    "pension": 0
   },
   {
    "marshal": "Bernadotte",
    "expectation": 160,
    "satisfaction": 0,
    "shortfall": 160,
    "eroding": true,
    "grace_turns_left": 0,
    "pension": 0
   },
   {
    "marshal": "Massena",
    "expectation": 80,
    "satisfaction": 0,
    "shortfall": 80,
    "eroding": false,
    "grace_turns_left": 1,
    "pension": 0
   }
  ],
  "rente_cost": 0,
  "expectation_rises": [
   {
    "marshal": "Ney",
    "expectation": 300,
    "previous": 280,
    "satisfaction": 0
   },
   {
    "marshal": "Soult",
    "expectation": 160,
    "previous": 120,
    "satisfaction": 0
   },
   {
    "marshal": "Murat",
    "expectation": 280,
    "previous": 240,
    "satisfaction": 0
   }
  ],
  "blockade": 250,
  "admiralty": 90,
  "upkeep_surcharge": 0,
  "force_limit": 132500,
  "over_force_limit": false,
  "bankrupt": false,
  "strength_ratio_pct": 31,
  "authority": 100,
  "authority_label": "Strong"
 },
 "marshals": [
  {
   "name": "Soult",
   "location": "Tyrol",
   "strength": 24698,
   "status": "en_route",
   "status_note": "Supporting Murat. (to the letter)",
   "arc_note": "",
   "idle_turns": 0,
   "danger": "",
   "trust": 58,
   "trust_notable": false,
   "morale": 85,
   "morale_warning": false
  },
  {
   "name": "Davout",
   "location": "Frankfurt",
   "strength": 23415,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 4,
   "danger": "",
   "trust": 76,
   "trust_notable": false,
   "morale": 85,
   "morale_warning": false
  },
  {
   "name": "Ney",
   "location": "Tyrol",
   "strength": 18101,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 1,
   "danger": "Starving \u2014 supply has failed at Tyrol two turns running.",
   "trust": 60,
   "trust_notable": false,
   "morale": 75,
   "morale_warning": false
  },
  {
   "name": "Massena",
   "location": "Tyrol",
   "strength": 16955,
   "status": "retreating",
   "status_note": "Has fallen back 2 times in five turns \u2014 now at Tyrol with 16,955 men.",
   "arc_note": "Has fallen back 2 times in five turns \u2014 now at Tyrol with 16,955 men.",
   "idle_turns": 1,
   "danger": "Morale failing (10) \u2014 the men waver.",
   "trust": 60,
   "trust_notable": false,
   "morale": 10,
   "morale_warning": true
  },
  {
   "name": "Lannes",
   "location": "Rhineland",
   "strength": 16505,
   "status": "idle_restless",
   "status_note": "3 turns idle.",
   "arc_note": "",
   "idle_turns": 3,
   "danger": "",
   "trust": 73,
   "trust_notable": false,
   "morale": 85,
   "morale_warning": false
  },
  {
   "name": "Bernadotte",
   "location": "Munich",
   "strength": 14479,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 4,
   "danger": "",
   "trust": 28,
   "trust_notable": true,
   "morale": 90,
   "morale_warning": false
  },
  {
   "name": "Murat",
   "location": "Tyrol",
   "strength": 14009,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 0,
   "danger": "Starving \u2014 supply has failed at Tyrol two turns running.",
   "trust": 63,
   "trust_notable": false,
   "morale": 68,
   "morale_warning": false
  }
 ],
 "intelligence": [
  {
   "name": "Deroy",
   "location": "Munich",
   "strength_display": "11,817",
   "visibility": "full",
   "intel_turn": 7
  },
  {
   "name": "Archduke Charles",
   "location": "Bohemia",
   "strength_display": "29,686",
   "visibility": "full",
   "intel_turn": 6
  },
  {
   "name": "Archduke John",
   "location": "Bohemia",
   "strength_display": "8,444",
   "visibility": "full",
   "intel_turn": 6
  },
  {
   "name": "Mack",
   "location": "Berlin",
   "strength_display": "1,449",
   "visibility": "full",
   "intel_turn": 5
  },
  {
   "name": "Brunswick",
   "location": "Berlin",
   "strength_display": "50,000",
   "visibility": "full",
   "intel_turn": 5
  }
 ],
 "turn_events": [
  {
   "message": "Massena's army is recovering. Effectiveness penalty: -40% The rout's disorder lingers
  in the ranks.",
   "severity": "good"
  },
  {
   "message": "Supply shortage at Tyrol: Ney loses 1,032 troops",
   "severity": "warning"
  },
  {
   "message": "Supply shortage at Tyrol: Soult loses 1,409 troops",
   "severity": "warning"
  },
  {
   "message": "Supply shortage at Tyrol: Murat loses 799 troops",
   "severity": "warning"
  },
  {
   "message": "Supply shortage at Tyrol: Massena loses 967 troops",
   "severity": "warning"
  },
  {
   "message": "Soult holds at Tyrol, per your orders \u2014 the guns at Bohemia did not move him.",
   "severity": "info"
  },
  {
   "message": "Berthier notes that Davout has grown restless \u2014 he has not seen laurels while
  Soult wins them. I recommend giving him meaningful orders soon.",
   "severity": "info"
  },
  {
   "message": "Murat is no longer the army's most celebrated commander \u2014 the laurels have
  passed.",
   "severity": "warning"
  },
  {
   "message": "Berthier reminds you: Bernadotte and Ney now stand within reach of each other. You
  asked to be warned.",
   "severity": "warning"
  },
  {
   "message": "The marshals have come together, Sire \u2014 a collective petition awaits your
  answer.",
   "severity": "warning"
  }
 ],
 "headline": {
  "class": "own_broken",
  "weight": 90,
  "text": "Sire \u2014 Massena's corps has been broken at Bohemia. He must reform before he fights
  again.",
  "sub_beats": [
   "Sire \u2014 Ney, Soult, Murat and Massena stand 73,763 men at Tyrol, which feeds 30,000. 43,763
  too many. 7,129 men lost in 3 turns. A supply depot at Tyrol would ease it; dispersing a corps
  would end it.",
   "Sire \u2014 our ally's marshal Deroy was broken at Franconia. Bavaria reels."
  ]
 },
 "berthier_note": "I have ordered the remnants collected, Sire. Do not commit them until they
  reform.",
 "talleyrand_report": [],
 "talleyrand_discovery": null,
 "talleyrand_override_note": null,
 "talleyrand_redemption": null,
 "coalition_status": {
  "threat_level": 79,
  "tier": "Formed",
  "sources": [
   {
    "source": "hegemony_passive",
    "amount": 1,
    "target": "France"
   },
   {
    "source": "decay",
    "amount": -3
   }
  ],
  "active_coalition": {
   "name": "Third Coalition",
   "leader": "Britain",
   "posture": "defensive",
   "formed_turn": 1,
   "members": [
    {
     "nation": "Austria",
     "war_exhaustion": 105,
     "strength_display": "43,331 men",
     "strength": 43331,
     "gold": 1380
    },
    {
     "nation": "Britain",
     "war_exhaustion": 0,
     "strength_display": "Unknown",
     "strength": 0,
     "gold": 0
    },
    {
     "nation": "Russia",
     "war_exhaustion": 0,
     "strength_display": "Unknown",
     "strength": 0,
     "gold": 0
    }
   ]
  }
 },
 "diplomatic_events": [
  {
   "type": "diplomatic_dp_regen",
   "text": "Talleyrand reports: 5 diplomatic points available (base 3, +1 skill, +1 authority).",
   "priority": "LOW"
  },
  {
   "type": "paymaster_subsidy",
   "text": "Britain's gold reaches Austria \u2014 the subsidy stands at 300 this season.",
   "priority": "MEDIUM"
  }
 ],
 "pending_envoy_count": 4,
 "pending_envoys": [
  {
   "nation": "KingdomOfItaly",
   "proposal_type": "request reward or restoration",
   "state": "ACTIVE"
  },
  {
   "nation": "Prussia",
   "proposal_type": "open borders",
   "state": "WAITING"
  },
  {
   "nation": "Hesse",
   "proposal_type": "non aggression",
   "state": "WAITING"
  },
  {
   "nation": "Bavaria",
   "proposal_type": "request reward or restoration",
   "state": "WAITING"
  }
 ]
}
-- POPUP/DIALOGUE [notifications] --
   [
    {
     "id": "f7f1ba82-5ab9-409f-9c9e-88b1c5d855a9",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Prussia",
     "message": "An envoy from Prussia has arrived with a proposal.",
     "turn_created": 6,
     "details": {},
     "base_title": "Envoy from Prussia",
     "repeat_count": 1
    },
    {
     "id": "160cd651-1b8b-43ac-8605-4871a1d38e78",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Hesse",
     "message": "An envoy from Hesse has arrived with a proposal.",
     "turn_created": 6,
     "details": {},
     "base_title": "Envoy from Hesse",
     "repeat_count": 1
    },
    {
     "id": "c9fdca21-9c08-4ec6-886a-3fe7a7f02fa8",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Ney grows bitter",
     "message": "Marshal Ney's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Ney",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Ney grows bitter",
     "repeat_count": 1
    },
    {
     "id": "ff90a7da-d536-4658-af81-bbd0a31ad89d",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Davout grows bitter",
     "message": "Marshal Davout's victories remain unrewarded (expects 240g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Davout",
      "expectation": 240,
      "satisfaction": 0,
      "shortfall": 240
     },
     "base_title": "Marshal Davout grows bitter",
     "repeat_count": 1
    },
    {
     "id": "823b437f-15a0-4fb9-8251-37ed3e1cd475",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Soult grows bitter",
     "message": "Marshal Soult's victories remain unrewarded (expects 120g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Soult",
      "expectation": 120,
      "satisfaction": 0,
      "shortfall": 120
     },
     "base_title": "Marshal Soult grows bitter",
     "repeat_count": 1
    },
    {
     "id": "160c5aa3-8ef9-46f4-9999-9f4232ea3bbf",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Lannes grows bitter",
     "message": "Marshal Lannes's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Lannes",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Lannes grows bitter",
     "repeat_count": 1
    },
    {
     "id": "ea9c2894-880f-4204-90ba-93891be05813",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Murat grows bitter",
     "message": "Marshal Murat's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Murat",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Murat grows bitter",
     "repeat_count": 1
    },
    {
     "id": "11eb075a-98d7-4a9b-94f1-ee058610f860",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Bernadotte grows bitter",
     "message": "Marshal Bernadotte's victories remain unrewarded (expects 160g/turn of estates;
     holds 0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014
     grant a rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Bernadotte",
      "expectation": 160,
      "satisfaction": 0,
      "shortfall": 160
     },
     "base_title": "Marshal Bernadotte g

====================================================================================================
> Ney, attack Charles at Bohemia
====================================================================================================
MUSTER — Ney (18,101; 54,408 with the muster committed) vs ArchdukeCharles (23,469 men) at Franconia
  — the balance of force looks favorable.
  WILL JOIN — Davout: is willing to march if the roads allow
  WILL NOT — Soult: awaits explicit orders and will NOT march — order 'Soult, support Ney' and he
  will march
  WILL JOIN — Murat: will march to the sound of the guns
  WILL NOT — Bernadotte: will not lift a finger for this marshal
  WILL NOT — Massena: is in no condition to fight


[Combat] Ney leads the charge! (Aggressive: +15% attack)
[Shield] ArchdukeCharles's DEFENSIVE stance strengthens the line! (+15% defense)
[Shield] ArchdukeCharles's methodical defense is exemplary! (Cautious: +20% total)
[Combat] Ney's combined arms coordination! (+10% attack)
[Combat] Adjacent allies bolster Ney's attack! (+2%)
Ney struggles in a costly engagement. Brutal stalemate between Ney and ArchdukeCharles. Heavy
  casualties on both sides: Ney 2,105, ArchdukeCharles 2,984.
[Materiel] Guns, horses and stores lost with the fallen: France -105g, Austria -149g.
   [cost=1  turn_advanced=False]
   <event battle> {"battle_name": "Second Battle of Franconia", "attacker": {"name": "Ney", "casualties": 2105, "remaining": 15996, "morale": 70, "forced_retreat": false}, "defender": {"name": "ArchdukeCharles", "casualties": 2984, "remaining": 20485, "morale": 38, "forced_retreat": false}, "attacker_nation": "France", "defender_nation": "Austria", "outcome": "stalemate", "victor": null, "enemy_destroyed": false, "region_conquered": false, "region_name": null, "flanking_bonus": 0, "flanking_origins": ["Tyrol"], "vindication": null, "attacker_forced_retreat": false, "defender_forced_retreat": false, "cavalry_ter
-- REINFORCEMENTS --
   [
    "Davout was nearly in position, but fate intervened at the crucial moment.",
    "Soult awaits explicit orders and did not march to the sound of the guns.",
    "Murat could not reach the battlefield in time."
   ]
-- BERTHIER'S AFTER-ACTION REPORT --
   {
    "modifier_breakdown": {
     "attacker": [
      {
       "label": "Personality (aggressive)",
       "value": 15,
       "type": "bonus"
      }
     ],
     "defender": [
      {
       "label": "Defensive stance",
       "value": 15,
       "type": "bonus"
      },
      {
       "label": "Personality (cautious)",
       "value": 5,
       "type": "bonus"
      },
      {
       "label": "Habsburg Resolve",
       "value": 3,
       "type": "bonus"
      }
     ]
    },
    "casualty_summary": {
     "attacker_name": "Ney",
     "attacker_original": 18101,
     "attacker_casualties": 2105,
     "attacker_remaining": 15996,
     "defender_name": "ArchdukeCharles",
     "defender_original": 23469,
     "defender_casualties": 2984,
     "defender_remaining": 20485
    },
    "observation": "Not one corps reached Ney. Davout, Soult and Murat was expected; Ney fought the
     battle single-handed.",
    "enemy_voice": "Archduke Charles: \"France pays full price for every Austrian mile now.\"",
    "marshal_voice": "Ney: \"We traded blood for nothing. I want tomorrow.\""
   }
-- POPUP/DIALOGUE [envoy_digest] --
   {
    "turn": 7,
    "count": 1,
    "title": "A SMALL COURT WRITES",
    "lapsing_count": 1,
    "headline": "Hesse writes.",
    "deadline_note": "Answer them here. Unanswered letters lapse when the turn ends, and a court
     left waiting will not raise the matter again for some seasons.",
    "items": [
     {
      "mailbox_id": 13,
      "dialogue_id": 17,
      "from_nation": "Hesse",
      "power_tier": "minor",
      "proposal_type": "friendly_gift",
      "proposal_type_display": "Non-Aggression Pact",
      "diplomat_name": "Chancery of Hesse",
      "diplomat_line": "Hesse, wishing to go unnoticed: \"Hesse counts what a quarrel with France
     would cost and what an understanding would return, and finds the ledger unanimous. Sign the
     pact of non-aggression.\"",
      "clauses": [
       "Proposal: Non-Aggression Pact",
       "Offer: Gold payment - 150"
      ],
      "acceptance_hint": "natural willingness to negotiate",
      "state": "WAITING",
      "arrival_turn": 6
     }
    ]
   }
-- POPUP/DIALOGUE [battle_diorama] --
   {
    "battle_name": "Second Battle of Franconia",
    "region": "Franconia",
    "turn": 7,
    "outcome": "stalemate",
    "victor": null,
    "attacker_nation": "France",
    "defender_nation": "Austria",
    "player_side": "attacker",
    "register": "grim",
    "significant": true,
    "dramatic": true,
    "great_battle": false,
    "region_conquered": false,
    "attacker": {
     "contingents": [
      {
       "name": "Ney",
       "nation": "France",
       "arm": "infantry",
       "committed": 18101,
       "casualties": 2105,
       "remaining": 15996,
       "status": "engaged",
       "lead": true,
       "crowned": false
      },
      {
       "name": "Davout",
       "nation": "France",
       "arm": "infantry",
       "committed": 23415,
       "casualties": 0,
       "remaining": 23415,
       "status": "failed_arrive",
       "lead": false,
       "crowned": false,
       "absence_reason": "fate intervened on the march"
      },
      {
       "name": "Soult",
       "nation": "France",
       "arm": "infantry",
       "committed": 24698,
       "casualties": 0,
       "remaining": 24698,
       "status": "refused",
       "lead": false,
       "crowned": false,
       "absence_reason": "awaits explicit orders"
      },
      {
       "name": "Murat",
       "nation": "France",
       "arm": "cavalry",
       "committed": 14009,
       "casualties": 0,
       "remaining": 14009,
       "status": "failed_arrive",
       "lead": false,
       "crowned": false,
       "absence_reason": "could not reach the field"
      }
     ],
     "reserve_count": 0,
     "casualties_total": 2105,
     "committed_total": 18101,
     "nation": "France"
    },
    "defender": {
     "contingents": [
      {
       "name": "ArchdukeCharles",
       "nation": "Austria",
       "arm": "infantry",
       "committed": 23469,
       "casualties": 2984,
       "remaining": 20485,
       "status": "engaged",
       "lead": true,
       "crowned": true
      }
     ],
     "reserve_count": 0,
     "casualties_total": 2984,
     "committed_total": 23469,
     "nation": "Austria"
    },
    "observation": "Not one corps reached Ney. Davout, Soult and Murat was expected; Ney fought the
     battle single-handed.",
    "enemy_voice": "Archduke Charles: \"France pays full price for every Austrian mile now.\""
   }
-- POPUP/DIALOGUE [notifications] --
   [
    {
     "id": "f7f1ba82-5ab9-409f-9c9e-88b1c5d855a9",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Prussia",
     "message": "An envoy from Prussia has arrived with a proposal.",
     "turn_created": 6,
     "details": {},
     "base_title": "Envoy from Prussia",
     "repeat_count": 1
    },
    {
     "id": "160cd651-1b8b-43ac-8605-4871a1d38e78",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Hesse",
     "message": "An envoy from Hesse has arrived with a proposal.",
     "turn_created": 6,
     "details": {},
     "base_title": "Envoy from Hesse",
     "repeat_count": 1
    },
    {
     "id": "c9fdca21-9c08-4ec6-886a-3fe7a7f02fa8",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Ney grows bitter",
     "message": "Marshal Ney's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Ney",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Ney grows bitter",
     "repeat_count": 1
    },
    {
     "id": "ff90a7da-d536-4658-af81-bbd0a31ad89d",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Davout grows bitter",
     "message": "Marshal Davout's victories remain unrewarded (expects 240g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Davout",
      "expectation": 240,
      "satisfaction": 0,
      "shortfall": 240
     },
     "base_title": "Marshal Davout grows bitter",
     "repeat_count": 1
    },
    {
     "id": "823b437f-15a0-4fb9-8251-37ed3e1cd475",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Soult grows bitter",
     "message": "Marshal Soult's victories remain unrewarded (expects 120g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Soult",
      "expectation": 120,
      "satisfaction": 0,
      "shortfall": 120
     },
     "base_title": "Marshal Soult grows bitter",
     "repeat_count": 1
    },
    {
     "id": "160c5aa3-8ef9-46f4-9999-9f4232ea3bbf",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Lannes grows bitter",
     "message": "Marshal Lannes's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Lannes",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Lannes grows bitter",
     "repeat_count": 1
    },
    {
     "id": "ea9c2894-880f-4204-90ba-93891be05813",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Murat grows bitter",
     "message": "Marshal Murat's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Murat",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Murat grows bitter",
     "repeat_count": 1
    },
    {
     "id": "11eb075a-98d7-4a9b-94f1-ee058610f860",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Bernadotte grows bitter",
     "message": "Marshal Bernadotte's victories remain unrewarded (expects 160g/turn of estates;
     holds 0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014
     grant a rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Bernadotte",
      "expectation": 160,
      "satisfaction": 0,
      "shortfall": 160
     },
     "base_title": "Marshal Bernadotte g

====================================================================================================
> Soult, support Ney
====================================================================================================
Soult moves to support Ney (at Tyrol). Soult will march to Ney's guns — he holds your written order.
  "Soult, support Ney." No more and no less. (1 AP — Soult executes precise orders with fewer
  couriers.)
   [cost=1  turn_advanced=False]
-- POPUP/DIALOGUE [envoy_digest] --
   {
    "turn": 7,
    "count": 1,
    "title": "A SMALL COURT WRITES",
    "lapsing_count": 1,
    "headline": "Hesse writes.",
    "deadline_note": "Answer them here. Unanswered letters lapse when the turn ends, and a court
     left waiting will not raise the matter again for some seasons.",
    "items": [
     {
      "mailbox_id": 13,
      "dialogue_id": 17,
      "from_nation": "Hesse",
      "power_tier": "minor",
      "proposal_type": "friendly_gift",
      "proposal_type_display": "Non-Aggression Pact",
      "diplomat_name": "Chancery of Hesse",
      "diplomat_line": "Hesse, wishing to go unnoticed: \"Hesse counts what a quarrel with France
     would cost and what an understanding would return, and finds the ledger unanimous. Sign the
     pact of non-aggression.\"",
      "clauses": [
       "Proposal: Non-Aggression Pact",
       "Offer: Gold payment - 150"
      ],
      "acceptance_hint": "natural willingness to negotiate",
      "state": "WAITING",
      "arrival_turn": 6
     }
    ]
   }
-- POPUP/DIALOGUE [notifications] --
   [
    {
     "id": "f7f1ba82-5ab9-409f-9c9e-88b1c5d855a9",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Prussia",
     "message": "An envoy from Prussia has arrived with a proposal.",
     "turn_created": 6,
     "details": {},
     "base_title": "Envoy from Prussia",
     "repeat_count": 1
    },
    {
     "id": "160cd651-1b8b-43ac-8605-4871a1d38e78",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Hesse",
     "message": "An envoy from Hesse has arrived with a proposal.",
     "turn_created": 6,
     "details": {},
     "base_title": "Envoy from Hesse",
     "repeat_count": 1
    },
    {
     "id": "c9fdca21-9c08-4ec6-886a-3fe7a7f02fa8",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Ney grows bitter",
     "message": "Marshal Ney's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Ney",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Ney grows bitter",
     "repeat_count": 1
    },
    {
     "id": "ff90a7da-d536-4658-af81-bbd0a31ad89d",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Davout grows bitter",
     "message": "Marshal Davout's victories remain unrewarded (expects 240g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Davout",
      "expectation": 240,
      "satisfaction": 0,
      "shortfall": 240
     },
     "base_title": "Marshal Davout grows bitter",
     "repeat_count": 1
    },
    {
     "id": "823b437f-15a0-4fb9-8251-37ed3e1cd475",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Soult grows bitter",
     "message": "Marshal Soult's victories remain unrewarded (expects 120g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Soult",
      "expectation": 120,
      "satisfaction": 0,
      "shortfall": 120
     },
     "base_title": "Marshal Soult grows bitter",
     "repeat_count": 1
    },
    {
     "id": "160c5aa3-8ef9-46f4-9999-9f4232ea3bbf",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Lannes grows bitter",
     "message": "Marshal Lannes's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Lannes",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Lannes grows bitter",
     "repeat_count": 1
    },
    {
     "id": "ea9c2894-880f-4204-90ba-93891be05813",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Murat grows bitter",
     "message": "Marshal Murat's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Murat",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Murat grows bitter",
     "repeat_count": 1
    },
    {
     "id": "11eb075a-98d7-4a9b-94f1-ee058610f860",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Bernadotte grows bitter",
     "message": "Marshal Bernadotte's victories remain unrewarded (expects 160g/turn of estates;
     holds 0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014
     grant a rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Bernadotte",
      "expectation": 160,
      "satisfaction": 0,
      "shortfall": 160
     },
     "base_title": "Marshal Bernadotte g

====================================================================================================
> end turn
====================================================================================================
Turn 7 ended. (Warning: 2 action(s) unused) Turn 8 begins!

Income: 3428g | Occupation: -52g | Charges of Empire: -1142g | Rentes: -2010g | Admiralty: -90g |
  Blockade: -250g | Upkeep: 944g | Other: +1158g | Net: +98g | Treasury: 14,896g
   [cost=0  turn_advanced=False]
   <event retreat_recovery> {"marshal": "Massena", "nation": "France", "stage": 2, "penalty": "-25%", "message": "Massena's army is recovering. Effectiveness penalty: -25% The rout's disorder lingers in the ranks."}
   <event construction_complete> {"region": "Swabia", "building": "watchtower", "message": "Construction complete: Watchtower in Swabia!"}
   <event supply_attrition> {"marshal": "Ney", "nation": "France", "region": "Tyrol", "losses": 813, "message": "Supply shortage at Tyrol: Ney loses 813 troops"}
   <event supply_attrition> {"marshal": "Soult", "nation": "France", "region": "Tyrol", "losses": 1255, "message": "Supply shortage at Tyrol: Soult loses 1,255 troops"}
   <event supply_attrition> {"marshal": "Murat", "nation": "France", "region": "Tyrol", "losses": 712, "message": "Supply shortage at Tyrol: Murat loses 712 troops"}
   <event supply_attrition> {"marshal": "Massena", "nation": "France", "region": "Tyrol", "losses": 861, "message": "Supply shortage at Tyrol: Massena loses 861 troops"}
   <event literal_fidelity> {"marshal": "Soult", "nation": "France", "location": "Tyrol", "order_type": "SUPPORT", "message": "Soult holds at Tyrol, per your orders \u2014 the guns at Franconia did not move him."}
   <event garrison_regen> {"region": "Milan", "nation": "Austria", "old_strength": 20000, "new_strength": 22000, "message": "Garrison at Milan reinforced: 20,000 -> 22,000"}
   <event vassal_loyalty> {"vassal": "Holland", "lord": "France", "nation": "France", "old_loyalty": 100, "new_loyalty": 100, "delta": 2, "reason": "a common enemy, the lord's victories", "recovery_hint": "", "message": "Holland loyalty 100 (+2): a common enemy, the lord's victories"}
   <event vassal_loyalty> {"vassal": "KingdomOfItaly", "lord": "France", "nation": "France", "old_loyalty": 100, "new_loyalty": 100, "delta": 2, "reason": "a common enemy, the lord's victories", "recovery_hint": "", "message": "KingdomOfItaly loyalty 100 (+2): a common enemy, the lord's victories"}
   <event sponsorship_granted> {"kind": "sponsorship", "payer": "Russia", "recipient": "Austria", "aim": "France", "amount": 200, "turns": 10, "licence": false, "turn": 8}
   <event jealousy_resolved> {"message": "Bernadotte's resentment of Ney has cooled for now. What was settled between them at the staff table has not been.", "nation": "France", "marshal": "Bernadotte"}
   <event jealousy_restlessness> {"message": "Berthier notes that Davout has grown restless \u2014 he has not seen laurels while Soult wins them. I recommend giving him meaningful orders soon.", "nation": "France", "marshal": "Davout"}
   <event jealousy_separation_warning> {"message": "Berthier reminds you: Bernadotte and Ney now stand within reach of each other. You asked to be warned.", "nation": "France", "marshal": "Bernadotte"}
   <event intel_decayed> {"region": "Dresden", "old_visibility": "full", "new_visibility": "stale"}
   <event intel_decayed> {"region": "Piedmont", "old_visibility": "partial", "new_visibility": "stale"}
   <event strategic_progress> {"marshal": "Soult", "command": "SUPPORT", "order_status": "active", "message": "Soult is moving to support Ney (0 turn(s) remaining)."}

####################################################################################################
# THE ENEMY PHASE
####################################################################################################
-- Britain --
  - Paget abandons fortified position
      [unfortified] {"type": "unfortified", "marshal": "Paget", "location": "Asturias", "free_ability": false}
  - Paget moves to Galicia
      [move] {"type": "move", "marshal": "Paget", "from": "Asturias", "to": "Galicia", "march_losses": 47}
  - Paget attacks Aragon
      [conquest] Aragon  capture_choice=plunder
    [action_count] 3
-- Austria --
  - Mack retreats to Franconia
      [retreat] {"type": "retreat", "marshal": "Mack", "from": "Berlin", "to": "Franconia", "recovery_stage": 0, "penalty": "-45%", "previous_stance": "defensive", "troop_loss": 0}
  - ArchdukeCharles forms square
      [form_square] {"type": "form_square", "marshal": "ArchdukeCharles", "location": "Franconia"}
  - Mack changes stance to defensive
      [stance_change] {"type": "stance_change", "marshal": "Mack", "from_stance": "neutral", "to_stance": "defensive", "action_cost": 1}
  - ArchdukeCharles attacks Deroy
      [battle] Second Battle of Munich  -> attacker_tactical_victory  victor=ArchdukeCharles
        ATK ArchdukeCharles  lost     880  left  19,605  morale  38
        DEF Deroy            lost   2,897  left   8,920  morale   0  ROUTED
  - ArchdukeCharles attacks Bernadotte
      [battle] Third Battle of Munich  -> defender_tactical_victory  victor=Bernadotte
        ATK ArchdukeCharles  lost   2,488  left  16,725  morale  34
        DEF Bernadotte       lost   1,263  left  13,216  morale  85
        defender order of battle: Bernadotte 14,479(engaged); Soult 24,698(refused)
  - ArchdukeCharles attacks Bernadotte
      [battle] Fourth Battle of Munich  -> defender_tactical_victory  victor=Bernadotte
        ATK ArchdukeCharles  lost   2,492  left  14,233  morale   3  ROUTED
        DEF Bernadotte       lost     838  left  12,378  morale  80
        defender order of battle: Bernadotte 13,216(engaged); Soult 24,698(refused)
    [action_count] 6
-- Spain --
  - Castanos forms square
      [form_square] {"type": "form_square", "marshal": "Castanos", "location": "Leon"}
  - Castanos attacks Aragon
      [battle] Battle of Aragon  -> attacker_tactical_victory  victor=Castanos
        ATK Castanos         lost     724  left  12,045  morale  95
        DEF Paget            lost   1,116  left   3,498  morale  84
  - Castanos attacks Paget
      [battle] Second Battle of Aragon  -> attacker_tactical_victory  victor=Castanos
        ATK Castanos         lost     504  left  11,301  morale  95
        DEF Paget            lost     940  left   2,558  morale  65
  - Castanos is granted a rente upon the treasury
      [rente_granted] {"type": "rente_granted", "marshal": "Castanos", "face": 80, "cost": 120, "previous": 0}
    [action_count] 4
[summary]
   Paget: unfortify
   Paget: move → Galicia
   Paget: attack → Aragon
   Mack: retreat → Franconia
   ArchdukeCharles: form_square
   Mack: stance_change → defensive
   ArchdukeCharles: attack → Deroy
   ArchdukeCharles: attack → Bernadotte
   ArchdukeCharles: attack → Bernadotte
   Castanos: form_square
   Castanos: attack → Aragon
   Castanos: attack → Paget
   Castanos: grant_pension

####################################################################################################
# THE MORNING DISPATCH
####################################################################################################
{
 "turn": 8,
 "situation": {
  "player_regions": 29,
  "enemy_regions": 97,
  "treasury": 14896,
  "treasury_delta": 184,
  "trade_income": 500,
  "occupation": 52,
  "contributions": 0,
  "state_charges": 1160,
  "requisitions": 0,
  "overseas": 0,
  "dotation_skim": 0,
  "unmet_marshals": [
   {
    "marshal": "Bernadotte",
    "expectation": 240,
    "satisfaction": 160,
    "shortfall": 80,
    "eroding": false,
    "grace_turns_left": 2,
    "pension": 160
   },
   {
    "marshal": "Massena",
    "expectation": 80,
    "satisfaction": 0,
    "shortfall": 80,
    "eroding": true,
    "grace_turns_left": 0,
    "pension": 0
   }
  ],
  "rente_cost": 2010,
  "expectation_rises": [
   {
    "marshal": "Bernadotte",
    "expectation": 240,
    "previous": 160,
    "satisfaction": 160
   }
  ],
  "blockade": 250,
  "admiralty": 90,
  "upkeep_surcharge": 0,
  "force_limit": 132500,
  "over_force_limit": false,
  "bankrupt": false,
  "strength_ratio_pct": 35,
  "authority": 100,
  "authority_label": "Strong"
 },
 "marshals": [
  {
   "name": "Soult",
   "location": "Tyrol",
   "strength": 23443,
   "status": "en_route",
   "status_note": "Supporting Ney. (to the letter)",
   "arc_note": "",
   "idle_turns": 1,
   "danger": "Starving \u2014 supply has failed at Tyrol two turns running.",
   "trust": 60,
   "trust_notable": false,
   "morale": 85,
   "morale_warning": false
  },
  {
   "name": "Davout",
   "location": "Frankfurt",
   "strength": 23415,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 5,
   "danger": "",
   "trust": 78,
   "trust_notable": false,
   "morale": 85,
   "morale_warning": false
  },
  {
   "name": "Lannes",
   "location": "Rhineland",
   "strength": 16505,
   "status": "idle_restless",
   "status_note": "4 turns idle.",
   "arc_note": "",
   "idle_turns": 4,
   "danger": "",
   "trust": 75,
   "trust_notable": false,
   "morale": 85,
   "morale_warning": false
  },
  {
   "name": "Massena",
   "location": "Tyrol",
   "strength": 16094,
   "status": "retreating",
   "status_note": "Recovers T9.",
   "arc_note": "",
   "idle_turns": 2,
   "danger": "Morale failing (10) \u2014 the men waver.",
   "trust": 58,
   "trust_notable": false,
   "morale": 10,
   "morale_warning": true
  },
  {
   "name": "Ney",
   "location": "Tyrol",
   "strength": 15183,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 0,
   "danger": "Starving \u2014 supply has failed at Tyrol two turns running.",
   "trust": 62,
   "trust_notable": false,
   "morale": 70,
   "morale_warning": false
  },
  {
   "name": "Murat",
   "location": "Tyrol",
   "strength": 13297,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 1,
   "danger": "Starving \u2014 supply has failed at Tyrol two turns running.",
   "trust": 62,
   "trust_notable": false,
   "morale": 68,
   "morale_warning": false
  },
  {
   "name": "Bernadotte",
   "location": "Munich",
   "strength": 12378,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 1,
   "danger": "",
   "trust": 30,
   "trust_notable": true,
   "morale": 80,
   "morale_warning": false
  }
 ],
 "intelligence": [
  {
   "name": "Archduke Charles",
   "location": "Franconia",
   "strength_display": "20,485",
   "visibility": "full",
   "intel_turn": 7
  },
  {
   "name": "Archduke John",
   "location": "Bohemia",
   "strength_display": "8,444",
   "visibility": "full",
   "intel_turn": 6
  },
  {
   "name": "Mack",
   "location": "Berlin",
   "strength_display": "1,449",
   "visibility": "full",
   "intel_turn": 5
  },
  {
   "name": "Brunswick",
   "location": "Berlin",
   "strength_display": "50,000",
   "visibility": "full",
   "intel_turn": 5
  },
  {
   "name": "Castanos",
   "location": "Aragon",
   "strength_display": "11,301",
   "visibility": "full",
   "intel_turn": 7
  },
  {
   "name": "Paget",
   "location": "Aragon",
   "strength_display": "2,558",
   "visibility": "full",
   "intel_turn": 7
  },
  {
   "name": "Deroy",
   "location": "Swabia",
   "strength_display": "small force",
   "visibility": "partial",
   "intel_turn": 8
  }
 ],
 "turn_events": [
  {
   "message": "Massena's army is recovering. Effectiveness penalty: -25% The rout's disorder lingers
  in the ranks.",
   "severity": "good"
  },
  {
   "message": "Supply shortage at Tyrol: Ney loses 813 troops",
   "severity": "warning"
  },
  {
   "message": "Supply shortage at Tyrol: Soult loses 1,255 troops",
   "severity": "warning"
  },
  {
   "message": "Supply shortage at Tyrol: Murat loses 712 troops",
   "severity": "warning"
  },
  {
   "message": "Supply shortage at Tyrol: Massena loses 861 troops",
   "severity": "warning"
  },
  {
   "message": "Soult holds at Tyrol, per your orders \u2014 the guns at Franconia did not move
  him.",
   "severity": "info"
  },
  {
   "message": "Holland loyalty 100 (+2): a common enemy, the lord's victories",
   "severity": "info"
  },
  {
   "message": "KingdomOfItaly loyalty 100 (+2): a common enemy, the lord's victories",
   "severity": "info"
  },
  {
   "message": "Bernadotte's resentment of Ney has cooled for now. What was settled between them at
  the staff table has not been.",
   "severity": "good"
  },
  {
   "message": "Berthier notes that Davout has grown restless \u2014 he has not seen laurels while
  Soult wins them. I recommend giving him meaningful orders soon.",
   "severity": "info"
  },
  {
   "message": "Berthier reminds you: Bernadotte and Ney now stand within reach of each other. You
  asked to be warned.",
   "severity": "warning"
  }
 ],
 "headline": {
  "class": "victory_won",
  "weight": 73,
  "text": "Sire \u2014 Marshal Bernadotte holds the field at Munich \u2014 Archduke Charles's corps
  is broken and flees.",
  "sub_beats": [
   "Sire \u2014 Ney, Soult, Murat and Massena stand 68,017 men at Tyrol, which feeds 30,000. 38,017
  too many. 9,860 men lost in 3 turns. A supply depot at Tyrol would ease it; dispersing a corps
  would end it.",
   "Sire \u2014 our ally's marshal Deroy was broken at Munich. Bavaria reels."
  ]
 },
 "berthier_note": "The army knows it is winning, Sire. Press the advantage before their line
  reforms.",
 "talleyrand_report": [],
 "talleyrand_discovery": null,
 "talleyrand_override_note": null,
 "talleyrand_redemption": null,
 "coalition_status": {
  "threat_level": 77,
  "tier": "Formed",
  "sources": [
   {
    "source": "hegemony_passive",
    "amount": 1,
    "target": "France"
   },
   {
    "source": "decay",
    "amount": -3
   }
  ],
  "active_coalition": {
   "name": "Third Coalition",
   "leader": "Britain",
   "posture": "defensive",
   "formed_turn": 1,
   "members": [
    {
     "nation": "Austria",
     "war_exhaustion": 117,
     "strength_display": "34,017 men",
     "strength": 34017,
     "gold": 1539
    },
    {
     "nation": "Britain",
     "war_exhaustion": 67,
     "strength_display": "35,558 men",
     "strength": 35558,
     "gold": 1936
    },
    {
     "nation": "Russia",
     "war_exhaustion": 0,
     "strength_display": "Unknown",
     "strength": 0,
     "gold": 0
    }
   ]
  }
 },
 "diplomatic_events": [
  {
   "type": "diplomatic_dp_regen",
   "text": "Talleyrand reports: 5 diplomatic points available (base 3, +1 skill, +1 authority).",
   "priority": "LOW"
  }
 ],
 "lapsed_offers": [
  {
   "nation": "Prussia",
   "proposal_type": "friendly gift"
  },
  {
   "nation": "Hesse",
   "proposal_type": "friendly gift"
  }
 ],
 "pending_envoy_count": 3,
 "pending_envoys": [
  {
   "nation": "KingdomOfItaly",
   "proposal_type": "request reward or restoration",
   "state": "ACTIVE"
  },
  {
   "nation": "PapalStates",
   "proposal_type": "open borders",
   "state": "WAITING"
  },
  {
   "nation": "Bavaria",
   "proposal_type": "request reward or restoration",
   "state": "WAITING"
  }
 ]
}
-- POPUP/DIALOGUE [notifications] --
   [
    {
     "id": "73f91faa-7c19-4dee-befa-77e8ca2425e8",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Massena grows bitter",
     "message": "Marshal Massena's victories remain unrewarded (expects 80g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente to stop
     the erosion.",
     "turn_created": 8,
     "details": {
      "marshal": "Massena",
      "expectation": 80,
      "satisfaction": 0,
      "shortfall": 80
     },
     "base_title": "Marshal Massena grows bitter",
     "repeat_count": 1
    },
    {
     "id": "8d47d698-a84b-422c-a5a4-6970c962bb5e",
     "type": "counter_punch_earned",
     "priority": 1,
     "title": "Bernadotte \u2014 free attack!",
     "message": "Bernadotte earned a free attack from their defensive victory. Use within 2 turns or
     the opportunity expires.",
     "turn_created": 7,
     "details": {
      "marshal": "Bernadotte"
     },
     "base_title": "Bernadotte \u2014 free attack!",
     "repeat_count": 1
    },
    {
     "id": "28140578-1993-462d-a860-3fac0da6291d",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Papal States",
     "message": "An envoy from Papal States has arrived with a proposal.",
     "turn_created": 7,
     "details": {},
     "base_title": "Envoy from Papal States",
     "repeat_count": 1
    },
    {
     "id": "c9fdca21-9c08-4ec6-886a-3fe7a7f02fa8",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Ney grows bitter",
     "message": "Marshal Ney's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Ney",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Ney grows bitter",
     "repeat_count": 1
    },
    {
     "id": "ff90a7da-d536-4658-af81-bbd0a31ad89d",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Davout grows bitter",
     "message": "Marshal Davout's victories remain unrewarded (expects 240g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Davout",
      "expectation": 240,
      "satisfaction": 0,
      "shortfall": 240
     },
     "base_title": "Marshal Davout grows bitter",
     "repeat_count": 1
    },
    {
     "id": "823b437f-15a0-4fb9-8251-37ed3e1cd475",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Soult grows bitter",
     "message": "Marshal Soult's victories remain unrewarded (expects 120g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Soult",
      "expectation": 120,
      "satisfaction": 0,
      "shortfall": 120
     },
     "base_title": "Marshal Soult grows bitter",
     "repeat_count": 1
    },
    {
     "id": "160c5aa3-8ef9-46f4-9999-9f4232ea3bbf",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Lannes grows bitter",
     "message": "Marshal Lannes's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Lannes",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Lannes grows bitter",
     "repeat_count": 1
    },
    {
     "id": "ea9c2894-880f-4204-90ba-93891be05813",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Murat grows bitter",
     "message": "Marshal Murat's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Murat",
      "expecta

====================================================================================================
> Murat, pursue Archduke Charles and destroy him
====================================================================================================
Cannot find 'Archduke Charles' to pursue.
   [cost=0  turn_advanced=False]
-- POPUP/DIALOGUE [envoy_digest] --
   {
    "turn": 8,
    "count": 1,
    "title": "A SMALL COURT WRITES",
    "lapsing_count": 1,
    "headline": "Papal States writes.",
    "deadline_note": "Answer them here. Unanswered letters lapse when the turn ends, and a court
     left waiting will not raise the matter again for some seasons.",
    "items": [
     {
      "mailbox_id": 14,
      "dialogue_id": 18,
      "from_nation": "PapalStates",
      "power_tier": "minor",
      "proposal_type": "open_borders",
      "proposal_type_display": "Open Borders Agreement",
      "diplomat_name": "Consalvi",
      "diplomat_line": "Cardinal Consalvi, serenely: \"France has grown so vast that her shadow now
     falls even upon the altar, and Rome, having no armies to set against it, would far sooner offer
     her friendship than her fear. Open the borders.\"",
      "clauses": [
       "Proposal: Open Borders Agreement",
       "Clause: Open borders"
      ],
      "acceptance_hint": "natural willingness to negotiate",
      "state": "WAITING",
      "arrival_turn": 7
     }
    ]
   }
-- POPUP/DIALOGUE [notifications] --
   [
    {
     "id": "73f91faa-7c19-4dee-befa-77e8ca2425e8",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Massena grows bitter",
     "message": "Marshal Massena's victories remain unrewarded (expects 80g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente to stop
     the erosion.",
     "turn_created": 8,
     "details": {
      "marshal": "Massena",
      "expectation": 80,
      "satisfaction": 0,
      "shortfall": 80
     },
     "base_title": "Marshal Massena grows bitter",
     "repeat_count": 1
    },
    {
     "id": "8d47d698-a84b-422c-a5a4-6970c962bb5e",
     "type": "counter_punch_earned",
     "priority": 1,
     "title": "Bernadotte \u2014 free attack!",
     "message": "Bernadotte earned a free attack from their defensive victory. Use within 2 turns or
     the opportunity expires.",
     "turn_created": 7,
     "details": {
      "marshal": "Bernadotte"
     },
     "base_title": "Bernadotte \u2014 free attack!",
     "repeat_count": 1
    },
    {
     "id": "28140578-1993-462d-a860-3fac0da6291d",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Papal States",
     "message": "An envoy from Papal States has arrived with a proposal.",
     "turn_created": 7,
     "details": {},
     "base_title": "Envoy from Papal States",
     "repeat_count": 1
    },
    {
     "id": "c9fdca21-9c08-4ec6-886a-3fe7a7f02fa8",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Ney grows bitter",
     "message": "Marshal Ney's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Ney",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Ney grows bitter",
     "repeat_count": 1
    },
    {
     "id": "ff90a7da-d536-4658-af81-bbd0a31ad89d",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Davout grows bitter",
     "message": "Marshal Davout's victories remain unrewarded (expects 240g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Davout",
      "expectation": 240,
      "satisfaction": 0,
      "shortfall": 240
     },
     "base_title": "Marshal Davout grows bitter",
     "repeat_count": 1
    },
    {
     "id": "823b437f-15a0-4fb9-8251-37ed3e1cd475",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Soult grows bitter",
     "message": "Marshal Soult's victories remain unrewarded (expects 120g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Soult",
      "expectation": 120,
      "satisfaction": 0,
      "shortfall": 120
     },
     "base_title": "Marshal Soult grows bitter",
     "repeat_count": 1
    },
    {
     "id": "160c5aa3-8ef9-46f4-9999-9f4232ea3bbf",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Lannes grows bitter",
     "message": "Marshal Lannes's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Lannes",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Lannes grows bitter",
     "repeat_count": 1
    },
    {
     "id": "ea9c2894-880f-4204-90ba-93891be05813",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Murat grows bitter",
     "message": "Marshal Murat's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Murat",
      "expecta

====================================================================================================
> Murat, pursue Charles
====================================================================================================
Cannot find 'Charles' to pursue.
   [cost=0  turn_advanced=False]
-- POPUP/DIALOGUE [envoy_digest] --
   {
    "turn": 8,
    "count": 1,
    "title": "A SMALL COURT WRITES",
    "lapsing_count": 1,
    "headline": "Papal States writes.",
    "deadline_note": "Answer them here. Unanswered letters lapse when the turn ends, and a court
     left waiting will not raise the matter again for some seasons.",
    "items": [
     {
      "mailbox_id": 14,
      "dialogue_id": 18,
      "from_nation": "PapalStates",
      "power_tier": "minor",
      "proposal_type": "open_borders",
      "proposal_type_display": "Open Borders Agreement",
      "diplomat_name": "Consalvi",
      "diplomat_line": "Cardinal Consalvi, serenely: \"France has grown so vast that her shadow now
     falls even upon the altar, and Rome, having no armies to set against it, would far sooner offer
     her friendship than her fear. Open the borders.\"",
      "clauses": [
       "Proposal: Open Borders Agreement",
       "Clause: Open borders"
      ],
      "acceptance_hint": "natural willingness to negotiate",
      "state": "WAITING",
      "arrival_turn": 7
     }
    ]
   }
-- POPUP/DIALOGUE [notifications] --
   [
    {
     "id": "73f91faa-7c19-4dee-befa-77e8ca2425e8",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Massena grows bitter",
     "message": "Marshal Massena's victories remain unrewarded (expects 80g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente to stop
     the erosion.",
     "turn_created": 8,
     "details": {
      "marshal": "Massena",
      "expectation": 80,
      "satisfaction": 0,
      "shortfall": 80
     },
     "base_title": "Marshal Massena grows bitter",
     "repeat_count": 1
    },
    {
     "id": "8d47d698-a84b-422c-a5a4-6970c962bb5e",
     "type": "counter_punch_earned",
     "priority": 1,
     "title": "Bernadotte \u2014 free attack!",
     "message": "Bernadotte earned a free attack from their defensive victory. Use within 2 turns or
     the opportunity expires.",
     "turn_created": 7,
     "details": {
      "marshal": "Bernadotte"
     },
     "base_title": "Bernadotte \u2014 free attack!",
     "repeat_count": 1
    },
    {
     "id": "28140578-1993-462d-a860-3fac0da6291d",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Papal States",
     "message": "An envoy from Papal States has arrived with a proposal.",
     "turn_created": 7,
     "details": {},
     "base_title": "Envoy from Papal States",
     "repeat_count": 1
    },
    {
     "id": "c9fdca21-9c08-4ec6-886a-3fe7a7f02fa8",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Ney grows bitter",
     "message": "Marshal Ney's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Ney",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Ney grows bitter",
     "repeat_count": 1
    },
    {
     "id": "ff90a7da-d536-4658-af81-bbd0a31ad89d",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Davout grows bitter",
     "message": "Marshal Davout's victories remain unrewarded (expects 240g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Davout",
      "expectation": 240,
      "satisfaction": 0,
      "shortfall": 240
     },
     "base_title": "Marshal Davout grows bitter",
     "repeat_count": 1
    },
    {
     "id": "823b437f-15a0-4fb9-8251-37ed3e1cd475",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Soult grows bitter",
     "message": "Marshal Soult's victories remain unrewarded (expects 120g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Soult",
      "expectation": 120,
      "satisfaction": 0,
      "shortfall": 120
     },
     "base_title": "Marshal Soult grows bitter",
     "repeat_count": 1
    },
    {
     "id": "160c5aa3-8ef9-46f4-9999-9f4232ea3bbf",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Lannes grows bitter",
     "message": "Marshal Lannes's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Lannes",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Lannes grows bitter",
     "repeat_count": 1
    },
    {
     "id": "ea9c2894-880f-4204-90ba-93891be05813",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Murat grows bitter",
     "message": "Marshal Murat's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Murat",
      "expecta

====================================================================================================
> Murat, pursue ArchdukeCharles
====================================================================================================
Murat: 'Mack bars the way!' Engaging!


[Combat] Murat leads the charge! (Aggressive: +15% attack)
[Shield] Mack's DEFENSIVE stance strengthens the line! (+15% defense)
[Fort] Mack's fortified position provides +9% defense!
[Cavalry] Murat's cavalry thrives on Plains terrain! (120% effectiveness)
[Combat] Murat's combined arms coordination! (+10% attack)
[Combat] Adjacent allies bolster Murat's attack! (+2%)
Murat struggles in a costly engagement. Murat gains the advantage over Mack. Casualties: Murat's
  army 34, Mack 1,216. Both armies remain in the field. Murat advances into Franconia. (132 lost to
  march)
[Materiel] Guns, horses and stores lost with the fallen: France -1g, Austria -60g.
[!] MARSHAL CAPTURED — Mack is taken by France at Franconia! 97 of his men escape home to the
  depots.
   [cost=1  turn_advanced=False]
-- POPUP/DIALOGUE [envoy_digest] --
   {
    "turn": 8,
    "count": 1,
    "title": "A SMALL COURT WRITES",
    "lapsing_count": 1,
    "headline": "Papal States writes.",
    "deadline_note": "Answer them here. Unanswered letters lapse when the turn ends, and a court
     left waiting will not raise the matter again for some seasons.",
    "items": [
     {
      "mailbox_id": 14,
      "dialogue_id": 18,
      "from_nation": "PapalStates",
      "power_tier": "minor",
      "proposal_type": "open_borders",
      "proposal_type_display": "Open Borders Agreement",
      "diplomat_name": "Consalvi",
      "diplomat_line": "Cardinal Consalvi, serenely: \"France has grown so vast that her shadow now
     falls even upon the altar, and Rome, having no armies to set against it, would far sooner offer
     her friendship than her fear. Open the borders.\"",
      "clauses": [
       "Proposal: Open Borders Agreement",
       "Clause: Open borders"
      ],
      "acceptance_hint": "natural willingness to negotiate",
      "state": "WAITING",
      "arrival_turn": 7
     }
    ]
   }
-- POPUP/DIALOGUE [notifications] --
   [
    {
     "id": "73f91faa-7c19-4dee-befa-77e8ca2425e8",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Massena grows bitter",
     "message": "Marshal Massena's victories remain unrewarded (expects 80g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente to stop
     the erosion.",
     "turn_created": 8,
     "details": {
      "marshal": "Massena",
      "expectation": 80,
      "satisfaction": 0,
      "shortfall": 80
     },
     "base_title": "Marshal Massena grows bitter",
     "repeat_count": 1
    },
    {
     "id": "8d47d698-a84b-422c-a5a4-6970c962bb5e",
     "type": "counter_punch_earned",
     "priority": 1,
     "title": "Bernadotte \u2014 free attack!",
     "message": "Bernadotte earned a free attack from their defensive victory. Use within 2 turns or
     the opportunity expires.",
     "turn_created": 7,
     "details": {
      "marshal": "Bernadotte"
     },
     "base_title": "Bernadotte \u2014 free attack!",
     "repeat_count": 1
    },
    {
     "id": "28140578-1993-462d-a860-3fac0da6291d",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Papal States",
     "message": "An envoy from Papal States has arrived with a proposal.",
     "turn_created": 7,
     "details": {},
     "base_title": "Envoy from Papal States",
     "repeat_count": 1
    },
    {
     "id": "c9fdca21-9c08-4ec6-886a-3fe7a7f02fa8",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Ney grows bitter",
     "message": "Marshal Ney's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Ney",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Ney grows bitter",
     "repeat_count": 1
    },
    {
     "id": "ff90a7da-d536-4658-af81-bbd0a31ad89d",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Davout grows bitter",
     "message": "Marshal Davout's victories remain unrewarded (expects 240g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Davout",
      "expectation": 240,
      "satisfaction": 0,
      "shortfall": 240
     },
     "base_title": "Marshal Davout grows bitter",
     "repeat_count": 1
    },
    {
     "id": "823b437f-15a0-4fb9-8251-37ed3e1cd475",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Soult grows bitter",
     "message": "Marshal Soult's victories remain unrewarded (expects 120g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Soult",
      "expectation": 120,
      "satisfaction": 0,
      "shortfall": 120
     },
     "base_title": "Marshal Soult grows bitter",
     "repeat_count": 1
    },
    {
     "id": "160c5aa3-8ef9-46f4-9999-9f4232ea3bbf",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Lannes grows bitter",
     "message": "Marshal Lannes's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Lannes",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Lannes grows bitter",
     "repeat_count": 1
    },
    {
     "id": "ea9c2894-880f-4204-90ba-93891be05813",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Murat grows bitter",
     "message": "Marshal Murat's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Murat",
      "expecta

====================================================================================================
> end turn
====================================================================================================
Turn 8 ended. (Warning: 3 action(s) unused) Turn 9 begins!

Income: 3487g | Occupation: -30g | Charges of Empire: -814g | Rentes: -2010g | Admiralty: -90g |
  Blockade: -250g | Upkeep: 904g | Other: +1262g | Net: +651g | Treasury: 15,546g
   [cost=0  turn_advanced=False]
   <event retreat_recovery> {"marshal": "Massena", "nation": "France", "stage": 3, "penalty": "0% (recovered)", "message": "Massena's army is recovering. Effectiveness penalty: 0% (recovered)"}
   <event retreat_recovered> {"marshal": "Massena", "nation": "France", "message": "Massena's army has fully recovered and is combat ready."}
   <event counter_punch_expired> {"marshal": "Bernadotte", "nation": "France", "message": "[!] Bernadotte's Counter-Punch opportunity has expired! (Must use immediately after defending)"}
   <event construction_complete> {"region": "Milan", "building": "market", "message": "Construction complete: Market in Milan!"}
   <event supply_attrition> {"marshal": "Davout", "nation": "France", "region": "Franconia", "losses": 515, "message": "Supply shortage at Franconia: Davout loses 515 troops"}
   <event supply_attrition> {"marshal": "Murat", "nation": "France", "region": "Franconia", "losses": 289, "message": "Supply shortage at Franconia: Murat loses 289 troops"}
   <event supply_attrition> {"marshal": "Deroy", "nation": "Bavaria", "region": "Franconia", "losses": 177, "message": "Supply shortage at Franconia: Deroy loses 177 troops"}
   <event supply_attrition> {"marshal": "Ney", "nation": "France", "region": "Tyrol", "losses": 491, "message": "Supply shortage at Tyrol: Ney loses 491 troops"}
   <event supply_attrition> {"marshal": "Soult", "nation": "France", "region": "Tyrol", "losses": 758, "message": "Supply shortage at Tyrol: Soult loses 758 troops"}
   <event supply_attrition> {"marshal": "Massena", "nation": "France", "region": "Tyrol", "losses": 520, "message": "Supply shortage at Tyrol: Massena loses 520 troops"}
   <event literal_fidelity> {"marshal": "Soult", "nation": "France", "location": "Tyrol", "order_type": "SUPPORT", "message": "Soult holds at Tyrol, per your orders \u2014 the guns at Franconia did not move him."}
   <event garrison_regen> {"region": "Milan", "nation": "Austria", "old_strength": 22000, "new_strength": 24000, "message": "Garrison at Milan reinforced: 22,000 -> 24,000"}
   <event ai_ai_rivalry> {"nations": ["Russia", "Sweden"], "message": "Territorial rivalry between Russia and Sweden grows."}
   <event sponsorship_granted> {"kind": "sponsorship", "payer": "Russia", "recipient": "Sweden", "aim": "France", "amount": 300, "turns": 10, "licence": false, "turn": 9}
   <event glory_crowned> {"message": "Berthier notes that Murat's recent victories have made him the most celebrated commander in the army. (+1 shock, +1 defense, +1 administration while he holds the laurels)", "nation": "France", "marshal": "Murat"}
   <event jealousy_separation_warning> {"message": "Berthier reminds you: Bernadotte and Ney now stand within reach of each other. You asked to be warned.", "nation": "France", "marshal": "Bernadotte"}
   <event intel_updated> {"region": "Dresden", "new_visibility": "partial", "old_visibility": "stale", "source": "scout"}
   <event intel_decayed> {"region": "Moravia", "old_visibility": "stale", "new_visibility": "last_known"}
   <event intel_decayed> {"region": "Hungary", "old_visibility": "stale", "new_visibility": "last_known"}
   <event strategic_progress> {"marshal": "Murat", "command": "PURSUE", "order_status": "active", "message": "Murat is pursuing ArchdukeCharles (1 turn(s) remaining)."}
   <event strategic_progress> {"marshal": "Soult", "command": "SUPPORT", "order_status": "continues", "message": "Soult supports Ney at Tyrol."}

####################################################################################################
# THE ENEMY PHASE
####################################################################################################
-- Austria --
  - ArchdukeCharles retreats to Bohemia
      [retreat] {"type": "retreat", "marshal": "ArchdukeCharles", "from": "Franconia", "to": "Bohemia", "recovery_stage": 0, "penalty": "-35%", "previous_stance": "defensive", "troop_loss": 0}
  - ArchdukeCharles changes stance to defensive
      [stance_change] {"type": "stance_change", "marshal": "ArchdukeCharles", "from_stance": "neutral", "to_stance": "defensive", "action_cost": 1}
    [action_count] 2
-- Prussia --
  - Brunswick holds position
      [wait] {"type": "wait", "marshal": "Brunswick", "location": "Berlin", "action_cost": 0}
    [action_count] 1
-- Spain --
  - Castanos attacks Aragon
      [conquest] Aragon  capture_choice=secure
  - Castanos forms square
      [form_square] {"type": "form_square", "marshal": "Castanos", "location": "Aragon"}
  - Castanos attacks Galicia
      [battle] Battle of Galicia  -> attacker_tactical_victory  victor=Castanos
        ATK Castanos         lost     165  left  10,409  morale  95
        DEF Paget            lost   1,248  left   1,298  morale   5  ROUTED
        REGION TAKEN: Galicia
    [action_count] 3
-- Bavaria --
  - Deroy moves to Franconia
      [move] {"type": "move", "marshal": "Deroy", "from": "Swabia", "to": "Franconia", "march_losses": 44}
  - Deroy holds position
      [wait] {"type": "wait", "marshal": "Deroy", "location": "Franconia", "action_cost": 0}
    [action_count] 3
[summary]
   ArchdukeCharles: retreat → Bohemia
   ArchdukeCharles: stance_change → defensive
   Brunswick: wait
   Castanos: attack → Aragon
   Castanos: form_square
   Castanos: attack → Galicia
   Deroy: move → Franconia
   Deroy: wait

####################################################################################################
# THE MORNING DISPATCH
####################################################################################################
{
 "turn": 9,
 "situation": {
  "player_regions": 29,
  "enemy_regions": 97,
  "treasury": 15546,
  "treasury_delta": 609,
  "trade_income": 500,
  "occupation": 30,
  "contributions": 0,
  "state_charges": 856,
  "requisitions": 0,
  "overseas": 0,
  "dotation_skim": 0,
  "unmet_marshals": [
   {
    "marshal": "Davout",
    "expectation": 300,
    "satisfaction": 240,
    "shortfall": 60,
    "eroding": false,
    "grace_turns_left": 2,
    "pension": 240
   },
   {
    "marshal": "Murat",
    "expectation": 300,
    "satisfaction": 280,
    "shortfall": 20,
    "eroding": false,
    "grace_turns_left": 2,
    "pension": 280
   },
   {
    "marshal": "Bernadotte",
    "expectation": 240,
    "satisfaction": 160,
    "shortfall": 80,
    "eroding": false,
    "grace_turns_left": 1,
    "pension": 160
   },
   {
    "marshal": "Massena",
    "expectation": 80,
    "satisfaction": 0,
    "shortfall": 80,
    "eroding": true,
    "grace_turns_left": 0,
    "pension": 0
   }
  ],
  "rente_cost": 2010,
  "expectation_rises": [
   {
    "marshal": "Davout",
    "expectation": 300,
    "previous": 240,
    "satisfaction": 240
   },
   {
    "marshal": "Murat",
    "expectation": 300,
    "previous": 280,
    "satisfaction": 280
   }
  ],
  "blockade": 250,
  "admiralty": 90,
  "upkeep_surcharge": 0,
  "force_limit": 132500,
  "over_force_limit": false,
  "bankrupt": false,
  "strength_ratio_pct": 36,
  "authority": 100,
  "authority_label": "Strong"
 },
 "marshals": [
  {
   "name": "Davout",
   "location": "Franconia",
   "strength": 22878,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 1,
   "danger": "",
   "trust": 78,
   "trust_notable": false,
   "morale": 80,
   "morale_warning": false
  },
  {
   "name": "Soult",
   "location": "Tyrol",
   "strength": 22685,
   "status": "en_route",
   "status_note": "Supporting Ney. (to the letter)",
   "arc_note": "",
   "idle_turns": 2,
   "danger": "Starving \u2014 supply has failed at Tyrol two turns running.",
   "trust": 60,
   "trust_notable": false,
   "morale": 85,
   "morale_warning": false
  },
  {
   "name": "Lannes",
   "location": "Rhineland",
   "strength": 16505,
   "status": "idle_restless",
   "status_note": "5 turns idle.",
   "arc_note": "",
   "idle_turns": 5,
   "danger": "",
   "trust": 75,
   "trust_notable": false,
   "morale": 85,
   "morale_warning": false
  },
  {
   "name": "Massena",
   "location": "Tyrol",
   "strength": 15574,
   "status": "idle_restless",
   "status_note": "3 turns idle.",
   "arc_note": "",
   "idle_turns": 3,
   "danger": "Morale failing (10) \u2014 the men waver.",
   "trust": 56,
   "trust_notable": false,
   "morale": 10,
   "morale_warning": true
  },
  {
   "name": "Ney",
   "location": "Tyrol",
   "strength": 14692,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 1,
   "danger": "Starving \u2014 supply has failed at Tyrol two turns running.",
   "trust": 59,
   "trust_notable": false,
   "morale": 70,
   "morale_warning": false
  },
  {
   "name": "Murat",
   "location": "Franconia",
   "strength": 12864,
   "status": "en_route",
   "status_note": "Pursuing ArchdukeCharles.",
   "arc_note": "",
   "idle_turns": 0,
   "danger": "Starving \u2014 supply has failed at Franconia two turns running.",
   "trust": 62,
   "trust_notable": false,
   "morale": 63,
   "morale_warning": false
  },
  {
   "name": "Bernadotte",
   "location": "Munich",
   "strength": 12378,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 2,
   "danger": "",
   "trust": 30,
   "trust_notable": true,
   "morale": 80,
   "morale_warning": false
  }
 ],
 "intelligence": [
  {
   "name": "Archduke Charles",
   "location": "Bohemia",
   "strength_display": "29,686",
   "visibility": "full",
   "intel_turn": 6
  },
  {
   "name": "Archduke John",
   "location": "Bohemia",
   "strength_display": "8,444",
   "visibility": "full",
   "intel_turn": 6
  },
  {
   "name": "Deroy",
   "location": "Franconia",
   "strength_display": "8,699",
   "visibility": "full",
   "intel_turn": 9
  },
  {
   "name": "Mack",
   "location": "Berlin",
   "strength_display": "1,449",
   "visibility": "full",
   "intel_turn": 5
  },
  {
   "name": "Brunswick",
   "location": "Berlin",
   "strength_display": "50,000",
   "visibility": "full",
   "intel_turn": 5
  },
  {
   "name": "Castanos",
   "location": "Aragon",
   "strength_display": "11,301",
   "visibility": "full",
   "intel_turn": 7
  },
  {
   "name": "Paget",
   "location": "Galicia",
   "strength_display": "1,298",
   "visibility": "full",
   "intel_turn": 8
  }
 ],
 "turn_events": [
  {
   "message": "Massena's army is recovering. Effectiveness penalty: 0% (recovered)",
   "severity": "good"
  },
  {
   "message": "[!] Bernadotte's Counter-Punch opportunity has expired! (Must use immediately after
  defending)",
   "severity": "warning"
  },
  {
   "message": "Supply shortage at Franconia: Davout loses 515 troops",
   "severity": "warning"
  },
  {
   "message": "Supply shortage at Franconia: Murat loses 289 troops",
   "severity": "warning"
  },
  {
   "message": "Supply shortage at Tyrol: Ney loses 491 troops",
   "severity": "warning"
  },
  {
   "message": "Supply shortage at Tyrol: Soult loses 758 troops",
   "severity": "warning"
  },
  {
   "message": "Supply shortage at Tyrol: Massena loses 520 troops",
   "severity": "warning"
  },
  {
   "message": "Soult holds at Tyrol, per your orders \u2014 the guns at Franconia did not move
  him.",
   "severity": "info"
  },
  {
   "message": "Berthier notes that Murat's recent victories have made him the most celebrated
  commander in the army. (+1 shock, +1 defense, +1 administration while he holds the laurels)",
   "severity": "good"
  },
  {
   "message": "Berthier reminds you: Bernadotte and Ney now stand within reach of each other. You
  asked to be warned.",
   "severity": "warning"
  }
 ],
 "headline": {
  "class": "marshal_captured",
  "weight": 95,
  "text": "Sire \u2014 Marshal Mack has been taken. France holds him prisoner.",
  "sub_beats": [
   "Sire \u2014 Ney, Soult and Massena stand 52,951 men at Tyrol, which feeds 30,000. 22,951 too
  many. 9,617 men lost in 3 turns. A supply depot at Tyrol would ease it; dispersing a corps would
  end it.",
   "Sire \u2014 Marshal Massena's household goes unpaid. His patience erodes with his purse."
  ]
 },
 "berthier_note": "We must consider his ransom, Sire \u2014 or make his captors regret the
  keeping.",
 "talleyrand_report": [],
 "talleyrand_discovery": null,
 "talleyrand_override_note": null,
 "talleyrand_redemption": null,
 "coalition_status": {
  "threat_level": 78,
  "tier": "Formed",
  "sources": [
   {
    "source": "hegemony_passive",
    "amount": 1,
    "target": "France"
   },
   {
    "source": "decay",
    "amount": -3
   }
  ],
  "active_coalition": {
   "name": "Third Coalition",
   "leader": "Britain",
   "posture": "defensive",
   "formed_turn": 1,
   "members": [
    {
     "nation": "Austria",
     "war_exhaustion": 126,
     "strength_display": "32,536 men",
     "strength": 32536,
     "gold": 2633
    },
    {
     "nation": "Britain",
     "war_exhaustion": 0,
     "strength_display": "Unknown",
     "strength": 0,
     "gold": 0
    },
    {
     "nation": "Russia",
     "war_exhaustion": 0,
     "strength_display": "Unknown",
     "strength": 0,
     "gold": 0
    }
   ]
  }
 },
 "diplomatic_events": [
  {
   "type": "diplomatic_dp_regen",
   "text": "Talleyrand reports: 5 diplomatic points available (base 3, +1 skill, +1 authority).",
   "priority": "LOW"
  }
 ],
 "lapsed_offers": [
  {
   "nation": "PapalStates",
   "proposal_type": "open borders"
  }
 ],
 "pending_envoy_count": 3,
 "pending_envoys": [
  {
   "nation": "KingdomOfItaly",
   "proposal_type": "request reward or restoration",
   "state": "ACTIVE"
  },
  {
   "nation": "Britain",
   "proposal_type": "settlement offer",
   "state": "WAITING"
  },
  {
   "nation": "Bavaria",
   "proposal_type": "request reward or restoration",
   "state": "WAITING"
  }
 ]
}
-- POPUP/DIALOGUE [notifications] --
   [
    {
     "id": "6e5cb538-9460-469d-8e1a-fd9ba4fe4d95",
     "type": "incoming_settlement_offer",
     "priority": 1,
     "title": "Settlement offer from Britain (x2)",
     "message": "Britain has offered terms to settle France vs Britain. Asking 629 gold.",
     "turn_created": 8,
     "details": {
      "war_id": "war_1",
      "offer_id": "settlement_offer:war_1:8:1",
      "proposer_nation": "Britain",
      "amount": 629,
      "review_target": "incoming_settlement_offer_popup"
     },
     "base_title": "Settlement offer from Britain",
     "repeat_count": 2
    },
    {
     "id": "73f91faa-7c19-4dee-befa-77e8ca2425e8",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Massena grows bitter",
     "message": "Marshal Massena's victories remain unrewarded (expects 80g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente to stop
     the erosion.",
     "turn_created": 8,
     "details": {
      "marshal": "Massena",
      "expectation": 80,
      "satisfaction": 0,
      "shortfall": 80
     },
     "base_title": "Marshal Massena grows bitter",
     "repeat_count": 1
    },
    {
     "id": "8d47d698-a84b-422c-a5a4-6970c962bb5e",
     "type": "counter_punch_earned",
     "priority": 1,
     "title": "Bernadotte \u2014 free attack!",
     "message": "Bernadotte earned a free attack from their defensive victory. Use within 2 turns or
     the opportunity expires.",
     "turn_created": 7,
     "details": {
      "marshal": "Bernadotte"
     },
     "base_title": "Bernadotte \u2014 free attack!",
     "repeat_count": 1
    },
    {
     "id": "c9fdca21-9c08-4ec6-886a-3fe7a7f02fa8",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Ney grows bitter",
     "message": "Marshal Ney's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Ney",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Ney grows bitter",
     "repeat_count": 1
    },
    {
     "id": "ff90a7da-d536-4658-af81-bbd0a31ad89d",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Davout grows bitter",
     "message": "Marshal Davout's victories remain unrewarded (expects 240g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Davout",
      "expectation": 240,
      "satisfaction": 0,
      "shortfall": 240
     },
     "base_title": "Marshal Davout grows bitter",
     "repeat_count": 1
    },
    {
     "id": "823b437f-15a0-4fb9-8251-37ed3e1cd475",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Soult grows bitter",
     "message": "Marshal Soult's victories remain unrewarded (expects 120g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Soult",
      "expectation": 120,
      "satisfaction": 0,
      "shortfall": 120
     },
     "base_title": "Marshal Soult grows bitter",
     "repeat_count": 1
    },
    {
     "id": "160c5aa3-8ef9-46f4-9999-9f4232ea3bbf",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Lannes grows bitter",
     "message": "Marshal Lannes's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Lannes",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Lannes grows bitter",
     "repeat_count": 1
    },
    {
     "id": "ea9c2894-880f-4204-90ba-93891be05813",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Murat grows bitter",
     "message": "Marshal Murat's victories remain unrewarded (expects 200g/turn of estates;

====================================================================================================
> end turn
====================================================================================================
Turn 9 ended. (Warning: 4 action(s) unused) Turn 10 begins!

Income: 3478g | Occupation: -30g | Charges of Empire: -898g | Rentes: -2010g | Admiralty: -90g |
  Blockade: -250g | Upkeep: 872g | Other: +1254g | Net: +582g | Treasury: 16,128g
   [cost=0  turn_advanced=False]
   <event construction_complete> {"region": "Franconia", "building": "watchtower", "message": "Construction complete: Watchtower in Franconia!"}
   <event supply_attrition> {"marshal": "Ney", "nation": "France", "region": "Tyrol", "losses": 879, "message": "Supply shortage at Tyrol: Ney loses 879 troops"}
   <event supply_attrition> {"marshal": "Davout", "nation": "France", "region": "Tyrol", "losses": 1369, "message": "Supply shortage at Tyrol: Davout loses 1,369 troops"}
   <event supply_attrition> {"marshal": "Soult", "nation": "France", "region": "Tyrol", "losses": 1358, "message": "Supply shortage at Tyrol: Soult loses 1,358 troops"}
   <event supply_attrition> {"marshal": "Murat", "nation": "France", "region": "Tyrol", "losses": 770, "message": "Supply shortage at Tyrol: Murat loses 770 troops"}
   <event supply_attrition> {"marshal": "Massena", "nation": "France", "region": "Tyrol", "losses": 932, "message": "Supply shortage at Tyrol: Massena loses 932 troops"}
   <event garrison_regen> {"region": "Milan", "nation": "Austria", "old_strength": 24000, "new_strength": 25000, "message": "Garrison at Milan reinforced: 24,000 -> 25,000"}
   <event british_subsidy> {"recipient": "Russia", "payer": "Britain", "amount": 200, "war_id": "war_1", "subsidy_source_detail": "unique_eligible", "message": "Britain subsidizes Russia with 200 gold."}
   <event ai_ai_rivalry> {"nations": ["Russia", "Prussia"], "message": "Territorial rivalry between Russia and Prussia grows."}
   <event ai_ai_rivalry> {"nations": ["Russia", "Sweden"], "message": "Territorial rivalry between Russia and Sweden grows."}
   <event sponsorship_granted> {"kind": "sponsorship", "payer": "Russia", "recipient": "Sardinia", "aim": "France", "amount": 300, "turns": 10, "licence": false, "turn": 10}
   <event jealousy_fired> {"message": "Berthier reports that Bernadotte resents Ney's laurels for the third time \u2014 he has grown careful about what he commits to paper.", "nation": "France", "marshal": "Bernadotte", "target": "Ney"}
   <event jealousy_fired> {"message": "Berthier reports that Ney appears envious of Bernadotte's laurels \u2014 he has grown loud at the staff table about who is given the honours.", "nation": "France", "marshal": "Ney", "target": "Bernadotte"}
   <event jealousy_escalation> {"message": "The feud between Bernadotte and Ney is now mutual \u2014 each schemes against the other. Separate them, Sire, or accept the friction.", "nation": "France", "marshal": "Bernadotte", "target": "Ney"}
   <event jealousy_restlessness> {"message": "Berthier notes that Massena has grown restless \u2014 he has not seen laurels while Bernadotte wins them. I recommend giving him meaningful orders soon.", "nation": "France", "marshal": "Massena"}
   <event jealousy_separation_warning> {"message": "Berthier reminds you: Bernadotte and Ney now stand within reach of each other. You asked to be warned.", "nation": "France", "marshal": "Bernadotte"}
   <event intel_decayed> {"region": "Piedmont", "old_visibility": "stale", "new_visibility": "last_known"}
   <event intel_decayed> {"region": "Berlin", "old_visibility": "full", "new_visibility": "last_known"}
   <event intel_decayed> {"region": "Aragon", "old_visibility": "full", "new_visibility": "stale"}
   <event strategic_progress> {"marshal": "Soult", "command": "SUPPORT", "order_status": "completed", "message": "The order was \"Soult, support Ney\". Ney is secure. I await further instruction."}

####################################################################################################
# THE ENEMY PHASE
####################################################################################################
-- Austria --
  - ArchdukeJohn attacks Massena
      [battle] Third Battle of Tyrol  -> defender_tactical_victory  victor=Massena
        ATK ArchdukeJohn     lost   8,764  left   9,496  morale   0  ROUTED
        DEF Massena          lost     173  left  15,544  morale   5
        defender order of battle: Massena 15,574(engaged); Davout 22,878(reinforced); Soult 22,685(engaged); Ney 14,692(engaged); Bernadotte 12,378(refused)
    [action_count] 1
-- Bavaria --
  - Deroy holds position
      [wait] {"type": "wait", "marshal": "Deroy", "location": "Franconia", "action_cost": 0}
    [action_count] 2
[summary]
   ArchdukeJohn: attack → Massena
   Deroy: wait

####################################################################################################
# THE MORNING DISPATCH
####################################################################################################
{
 "turn": 10,
 "situation": {
  "player_regions": 29,
  "enemy_regions": 97,
  "treasury": 16128,
  "treasury_delta": 550,
  "trade_income": 500,
  "occupation": 30,
  "contributions": 0,
  "state_charges": 938,
  "requisitions": 0,
  "overseas": 0,
  "dotation_skim": 0,
  "unmet_marshals": [
   {
    "marshal": "Davout",
    "expectation": 300,
    "satisfaction": 240,
    "shortfall": 60,
    "eroding": false,
    "grace_turns_left": 1,
    "pension": 240
   },
   {
    "marshal": "Soult",
    "expectation": 200,
    "satisfaction": 160,
    "shortfall": 40,
    "eroding": false,
    "grace_turns_left": 2,
    "pension": 160
   },
   {
    "marshal": "Murat",
    "expectation": 300,
    "satisfaction": 280,
    "shortfall": 20,
    "eroding": false,
    "grace_turns_left": 1,
    "pension": 280
   },
   {
    "marshal": "Bernadotte",
    "expectation": 240,
    "satisfaction": 160,
    "shortfall": 80,
    "eroding": true,
    "grace_turns_left": 0,
    "pension": 160
   },
   {
    "marshal": "Massena",
    "expectation": 120,
    "satisfaction": 0,
    "shortfall": 120,
    "eroding": true,
    "grace_turns_left": 0,
    "pension": 0
   }
  ],
  "rente_cost": 2010,
  "expectation_rises": [
   {
    "marshal": "Soult",
    "expectation": 200,
    "previous": 160,
    "satisfaction": 160
   },
   {
    "marshal": "Massena",
    "expectation": 120,
    "previous": 80,
    "satisfaction": 0
   }
  ],
  "blockade": 250,
  "admiralty": 90,
  "upkeep_surcharge": 0,
  "force_limit": 132500,
  "over_force_limit": false,
  "bankrupt": false,
  "strength_ratio_pct": 38,
  "authority": 100,
  "authority_label": "Strong"
 },
 "marshals": [
  {
   "name": "Davout",
   "location": "Tyrol",
   "strength": 21463,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 1,
   "danger": "Starving \u2014 supply has failed at Tyrol two turns running.",
   "trust": 78,
   "trust_notable": false,
   "morale": 75,
   "morale_warning": false
  },
  {
   "name": "Soult",
   "location": "Tyrol",
   "strength": 21283,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 3,
   "danger": "Starving \u2014 supply has failed at Tyrol two turns running.",
   "trust": 65,
   "trust_notable": false,
   "morale": 80,
   "morale_warning": false
  },
  {
   "name": "Lannes",
   "location": "Rhineland",
   "strength": 16505,
   "status": "idle_restless",
   "status_note": "6 turns idle.",
   "arc_note": "",
   "idle_turns": 6,
   "danger": "",
   "trust": 75,
   "trust_notable": false,
   "morale": 85,
   "morale_warning": false
  },
  {
   "name": "Massena",
   "location": "Tyrol",
   "strength": 14612,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 1,
   "danger": "Morale failing (5) \u2014 the men waver.",
   "trust": 53,
   "trust_notable": true,
   "morale": 5,
   "morale_warning": true
  },
  {
   "name": "Ney",
   "location": "Tyrol",
   "strength": 13785,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 2,
   "danger": "Starving \u2014 supply has failed at Tyrol two turns running.",
   "trust": 59,
   "trust_notable": false,
   "morale": 65,
   "morale_warning": false
  },
  {
   "name": "Bernadotte",
   "location": "Munich",
   "strength": 12378,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 3,
   "danger": "",
   "trust": 28,
   "trust_notable": true,
   "morale": 80,
   "morale_warning": false
  },
  {
   "name": "Murat",
   "location": "Tyrol",
   "strength": 12069,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 1,
   "danger": "Starving \u2014 supply has failed at Tyrol two turns running.",
   "trust": 62,
   "trust_notable": false,
   "morale": 58,
   "morale_warning": true
  }
 ],
 "intelligence": [
  {
   "name": "Archduke Charles",
   "location": "Bohemia",
   "strength_display": "29,686",
   "visibility": "full",
   "intel_turn": 6
  },
  {
   "name": "Archduke John",
   "location": "Bohemia",
   "strength_display": "8,444",
   "visibility": "full",
   "intel_turn": 6
  },
  {
   "name": "Deroy",
   "location": "Franconia",
   "strength_display": "8,699",
   "visibility": "full",
   "intel_turn": 9
  },
  {
   "name": "Paget",
   "location": "Leon",
   "strength_display": "626",
   "visibility": "full",
   "intel_turn": 9
  },
  {
   "name": "Castanos",
   "location": "Aragon",
   "strength_display": "small force",
   "visibility": "stale",
   "intel_turn": 7
  },
  {
   "name": "Mack",
   "location": "Berlin",
   "strength_display": "screening force",
   "visibility": "last_known",
   "intel_turn": 5
  },
  {
   "name": "Brunswick",
   "location": "Berlin",
   "strength_display": "large force",
   "visibility": "last_known",
   "intel_turn": 5
  }
 ],
 "turn_events": [
  {
   "message": "Supply shortage at Tyrol: Ney loses 879 troops",
   "severity": "warning"
  },
  {
   "message": "Supply shortage at Tyrol: Davout loses 1,369 troops",
   "severity": "warning"
  },
  {
   "message": "Supply shortage at Tyrol: Soult loses 1,358 troops",
   "severity": "warning"
  },
  {
   "message": "Supply shortage at Tyrol: Murat loses 770 troops",
   "severity": "warning"
  },
  {
   "message": "Supply shortage at Tyrol: Massena loses 932 troops",
   "severity": "warning"
  },
  {
   "message": "Berthier reports that Bernadotte resents Ney's laurels for the third time \u2014 he
  has grown careful about what he commits to paper.",
   "severity": "warning"
  },
  {
   "message": "Berthier reports that Ney appears envious of Bernadotte's laurels \u2014 he has grown
  loud at the staff table about who is given the honours.",
   "severity": "warning"
  },
  {
   "message": "The feud between Bernadotte and Ney is now mutual \u2014 each schemes against the
  other. Separate them, Sire, or accept the friction.",
   "severity": "warning"
  },
  {
   "message": "Berthier notes that Massena has grown restless \u2014 he has not seen laurels while
  Bernadotte wins them. I recommend giving him meaningful orders soon.",
   "severity": "info"
  },
  {
   "message": "Berthier reminds you: Bernadotte and Ney now stand within reach of each other. You
  asked to be warned.",
   "severity": "warning"
  }
 ],
 "headline": {
  "class": "marshal_captured",
  "weight": 95,
  "text": "Sire \u2014 Marshal Paget has been taken. Spain holds him prisoner.",
  "sub_beats": [
   "Sire \u2014 Marshal Massena holds the field at Tyrol \u2014 Archduke John's corps is broken and
  flees.",
   "Sire \u2014 Ney, Davout, Soult, Murat and Massena stand 83,212 men at Tyrol, which feeds 30,000.
  53,212 too many. 10,718 men lost in 3 turns. A supply depot at Tyrol would ease it; dispersing a
  corps would end it."
  ]
 },
 "berthier_note": "We must consider his ransom, Sire \u2014 or make his captors regret the
  keeping.",
 "talleyrand_report": [],
 "talleyrand_discovery": null,
 "talleyrand_override_note": null,
 "talleyrand_redemption": null,
 "coalition_status": {
  "threat_level": 76,
  "tier": "Formed",
  "sources": [
   {
    "source": "hegemony_passive",
    "amount": 1,
    "target": "France"
   },
   {
    "source": "decay",
    "amount": -3
   }
  ],
  "active_coalition": {
   "name": "Third Coalition",
   "leader": "Britain",
   "posture": "defensive",
   "formed_turn": 1,
   "members": [
    {
     "nation": "Austria",
     "war_exhaustion": 0,
     "strength_display": "Unknown",
     "strength": 0,
     "gold": 0
    },
    {
     "nation": "Britain",
     "war_exhaustion": 0,
     "strength_display": "Unknown",
     "strength": 0,
     "gold": 0
    },
    {
     "nation": "Russia",
     "war_exhaustion": 0,
     "strength_display": "Unknown",
     "strength": 0,
     "gold": 0
    }
   ]
  }
 },
 "diplomatic_events": [
  {
   "type": "diplomatic_dp_regen",
   "text": "Talleyrand reports: 5 diplomatic points available (base 3, +1 skill, +1 authority).",
   "priority": "LOW"
  },
  {
   "type": "paymaster_subsidy",
   "text": "Britain's gold reaches Russia \u2014 the subsidy stands at 200 this season.",
   "priority": "MEDIUM"
  }
 ],
 "pending_envoy_count": 5,
 "pending_envoys": [
  {
   "nation": "KingdomOfItaly",
   "proposal_type": "request reward or restoration",
   "state": "ACTIVE"
  },
  {
   "nation": "Britain",
   "proposal_type": "settlement offer",
   "state": "WAITING"
  },
  {
   "nation": "Prussia",
   "proposal_type": "open borders",
   "state": "WAITING"
  },
  {
   "nation": "Hesse",
   "proposal_type": "open borders",
   "state": "WAITING"
  },
  {
   "nation": "Bavaria",
   "proposal_type": "request reward or restoration",
   "state": "WAITING"
  }
 ]
}
-- POPUP/DIALOGUE [notifications] --
   [
    {
     "id": "11eb075a-98d7-4a9b-94f1-ee058610f860",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Bernadotte grows bitter (x2)",
     "message": "Marshal Bernadotte's victories remain unrewarded (expects 240g/turn of estates;
     holds 160g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente
     to stop the erosion.",
     "turn_created": 10,
     "details": {
      "marshal": "Bernadotte",
      "expectation": 240,
      "satisfaction": 160,
      "shortfall": 80
     },
     "base_title": "Marshal Bernadotte grows bitter",
     "repeat_count": 2
    },
    {
     "id": "d32e9d62-0c5b-4d49-a5ba-5465f3102611",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Prussia",
     "message": "An envoy from Prussia has arrived with a proposal.",
     "turn_created": 9,
     "details": {},
     "base_title": "Envoy from Prussia",
     "repeat_count": 1
    },
    {
     "id": "fc301eca-f803-46d7-ba8d-ff9367e0ef71",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Hesse",
     "message": "An envoy from Hesse has arrived with a proposal.",
     "turn_created": 9,
     "details": {},
     "base_title": "Envoy from Hesse",
     "repeat_count": 1
    },
    {
     "id": "552b1a44-5cbe-4a9a-a123-61707f7c98de",
     "type": "strategic_order_complete",
     "priority": 1,
     "title": "Soult arrived",
     "message": "Soult has completed their SUPPORT order \u2014 arrived at Tyrol.",
     "turn_created": 9,
     "details": {
      "marshal": "Soult",
      "order_type": "SUPPORT",
      "target": "Ney"
     },
     "base_title": "Soult arrived",
     "repeat_count": 1
    },
    {
     "id": "6e5cb538-9460-469d-8e1a-fd9ba4fe4d95",
     "type": "incoming_settlement_offer",
     "priority": 1,
     "title": "Settlement offer from Britain (x2)",
     "message": "Britain has offered terms to settle France vs Britain. Asking 629 gold.",
     "turn_created": 8,
     "details": {
      "war_id": "war_1",
      "offer_id": "settlement_offer:war_1:8:1",
      "proposer_nation": "Britain",
      "amount": 629,
      "review_target": "incoming_settlement_offer_popup"
     },
     "base_title": "Settlement offer from Britain",
     "repeat_count": 2
    },
    {
     "id": "73f91faa-7c19-4dee-befa-77e8ca2425e8",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Massena grows bitter",
     "message": "Marshal Massena's victories remain unrewarded (expects 80g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente to stop
     the erosion.",
     "turn_created": 8,
     "details": {
      "marshal": "Massena",
      "expectation": 80,
      "satisfaction": 0,
      "shortfall": 80
     },
     "base_title": "Marshal Massena grows bitter",
     "repeat_count": 1
    },
    {
     "id": "8d47d698-a84b-422c-a5a4-6970c962bb5e",
     "type": "counter_punch_earned",
     "priority": 1,
     "title": "Bernadotte \u2014 free attack!",
     "message": "Bernadotte earned a free attack from their defensive victory. Use within 2 turns or
     the opportunity expires.",
     "turn_created": 7,
     "details": {
      "marshal": "Bernadotte"
     },
     "base_title": "Bernadotte \u2014 free attack!",
     "repeat_count": 1
    },
    {
     "id": "c9fdca21-9c08-4ec6-886a-3fe7a7f02fa8",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Ney grows bitter",
     "message": "Marshal Ney's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Ney",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Ney grows bitter",
     "repeat_count": 1
    },
    {
     "id": "ff90a7da-d536-4658-af81-bbd0a31ad89d",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Davout grows bitter",
     "message": "Marshal Davout's victories remain unrewarded (expects 240g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,


====================================================================================================
> Davout, move to Bohemia
====================================================================================================
Davout moves from Tyrol to Bohemia. Bohemia falls to France! (was Austria) (277 lost to march)
[HINT] Undefended regions nearby: Carniola, Hungary — attack to capture!
Your forces have taken Bohemia. Plunder it for 800 gold — buildings burned, the province left
  hostile — or secure it and keep the country quiet? ('plunder' or 'secure')
   [cost=1  turn_advanced=False]
   <event move> {"marshal": "Davout", "from": "Tyrol", "to": "Bohemia", "march_losses": 277}
-- POPUP/DIALOGUE [envoy_digest] --
   {
    "turn": 10,
    "count": 1,
    "title": "A SMALL COURT WRITES",
    "lapsing_count": 1,
    "headline": "Hesse writes.",
    "deadline_note": "Answer them here. Unanswered letters lapse when the turn ends, and a court
     left waiting will not raise the matter again for some seasons.",
    "items": [
     {
      "mailbox_id": 17,
      "dialogue_id": 21,
      "from_nation": "Hesse",
      "power_tier": "minor",
      "proposal_type": "open_borders",
      "proposal_type_display": "Open Borders Agreement",
      "diplomat_name": "Chancery of Hesse",
      "diplomat_line": "Hesse, wishing to go unnoticed: \"Hesse counts what a quarrel with France
     would cost and what an understanding would return, and finds the ledger unanimous. Open the
     borders.\"",
      "clauses": [
       "Proposal: Open Borders Agreement",
       "Clause: Open borders"
      ],
      "acceptance_hint": "natural willingness to negotiate",
      "state": "WAITING",
      "arrival_turn": 9
     }
    ]
   }
-- POPUP/DIALOGUE [pending_capture_choice] --
   true
-- POPUP/DIALOGUE [notifications] --
   [
    {
     "id": "11eb075a-98d7-4a9b-94f1-ee058610f860",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Bernadotte grows bitter (x2)",
     "message": "Marshal Bernadotte's victories remain unrewarded (expects 240g/turn of estates;
     holds 160g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente
     to stop the erosion.",
     "turn_created": 10,
     "details": {
      "marshal": "Bernadotte",
      "expectation": 240,
      "satisfaction": 160,
      "shortfall": 80
     },
     "base_title": "Marshal Bernadotte grows bitter",
     "repeat_count": 2
    },
    {
     "id": "d32e9d62-0c5b-4d49-a5ba-5465f3102611",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Prussia",
     "message": "An envoy from Prussia has arrived with a proposal.",
     "turn_created": 9,
     "details": {},
     "base_title": "Envoy from Prussia",
     "repeat_count": 1
    },
    {
     "id": "fc301eca-f803-46d7-ba8d-ff9367e0ef71",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Hesse",
     "message": "An envoy from Hesse has arrived with a proposal.",
     "turn_created": 9,
     "details": {},
     "base_title": "Envoy from Hesse",
     "repeat_count": 1
    },
    {
     "id": "552b1a44-5cbe-4a9a-a123-61707f7c98de",
     "type": "strategic_order_complete",
     "priority": 1,
     "title": "Soult arrived",
     "message": "Soult has completed their SUPPORT order \u2014 arrived at Tyrol.",
     "turn_created": 9,
     "details": {
      "marshal": "Soult",
      "order_type": "SUPPORT",
      "target": "Ney"
     },
     "base_title": "Soult arrived",
     "repeat_count": 1
    },
    {
     "id": "6e5cb538-9460-469d-8e1a-fd9ba4fe4d95",
     "type": "incoming_settlement_offer",
     "priority": 1,
     "title": "Settlement offer from Britain (x2)",
     "message": "Britain has offered terms to settle France vs Britain. Asking 629 gold.",
     "turn_created": 8,
     "details": {
      "war_id": "war_1",
      "offer_id": "settlement_offer:war_1:8:1",
      "proposer_nation": "Britain",
      "amount": 629,
      "review_target": "incoming_settlement_offer_popup"
     },
     "base_title": "Settlement offer from Britain",
     "repeat_count": 2
    },
    {
     "id": "73f91faa-7c19-4dee-befa-77e8ca2425e8",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Massena grows bitter",
     "message": "Marshal Massena's victories remain unrewarded (expects 80g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente to stop
     the erosion.",
     "turn_created": 8,
     "details": {
      "marshal": "Massena",
      "expectation": 80,
      "satisfaction": 0,
      "shortfall": 80
     },
     "base_title": "Marshal Massena grows bitter",
     "repeat_count": 1
    },
    {
     "id": "8d47d698-a84b-422c-a5a4-6970c962bb5e",
     "type": "counter_punch_earned",
     "priority": 1,
     "title": "Bernadotte \u2014 free attack!",
     "message": "Bernadotte earned a free attack from their defensive victory. Use within 2 turns or
     the opportunity expires.",
     "turn_created": 7,
     "details": {
      "marshal": "Bernadotte"
     },
     "base_title": "Bernadotte \u2014 free attack!",
     "repeat_count": 1
    },
    {
     "id": "c9fdca21-9c08-4ec6-886a-3fe7a7f02fa8",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Ney grows bitter",
     "message": "Marshal Ney's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Ney",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Ney grows bitter",
     "repeat_count": 1
    },
    {
     "id": "ff90a7da-d536-4658-af81-bbd0a31ad89d",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Davout grows bitter",
     "message": "Marshal Davout's victories remain unrewarded (expects 240g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,


====================================================================================================
> Ney, move to Munich
====================================================================================================
You must decide how to handle the captured region first!
Your forces have taken Bohemia. Plunder it for 800 gold — buildings burned, the province left
  hostile — or secure it and keep the country quiet? ('plunder' or 'secure')
-- POPUP/DIALOGUE [envoy_digest] --
   {
    "turn": 10,
    "count": 1,
    "title": "A SMALL COURT WRITES",
    "lapsing_count": 1,
    "headline": "Hesse writes.",
    "deadline_note": "Answer them here. Unanswered letters lapse when the turn ends, and a court
     left waiting will not raise the matter again for some seasons.",
    "items": [
     {
      "mailbox_id": 17,
      "dialogue_id": 21,
      "from_nation": "Hesse",
      "power_tier": "minor",
      "proposal_type": "open_borders",
      "proposal_type_display": "Open Borders Agreement",
      "diplomat_name": "Chancery of Hesse",
      "diplomat_line": "Hesse, wishing to go unnoticed: \"Hesse counts what a quarrel with France
     would cost and what an understanding would return, and finds the ledger unanimous. Open the
     borders.\"",
      "clauses": [
       "Proposal: Open Borders Agreement",
       "Clause: Open borders"
      ],
      "acceptance_hint": "natural willingness to negotiate",
      "state": "WAITING",
      "arrival_turn": 9
     }
    ]
   }
-- POPUP/DIALOGUE [pending_capture_choice] --
   true
-- POPUP/DIALOGUE [notifications] --
   [
    {
     "id": "11eb075a-98d7-4a9b-94f1-ee058610f860",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Bernadotte grows bitter (x2)",
     "message": "Marshal Bernadotte's victories remain unrewarded (expects 240g/turn of estates;
     holds 160g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente
     to stop the erosion.",
     "turn_created": 10,
     "details": {
      "marshal": "Bernadotte",
      "expectation": 240,
      "satisfaction": 160,
      "shortfall": 80
     },
     "base_title": "Marshal Bernadotte grows bitter",
     "repeat_count": 2
    },
    {
     "id": "d32e9d62-0c5b-4d49-a5ba-5465f3102611",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Prussia",
     "message": "An envoy from Prussia has arrived with a proposal.",
     "turn_created": 9,
     "details": {},
     "base_title": "Envoy from Prussia",
     "repeat_count": 1
    },
    {
     "id": "fc301eca-f803-46d7-ba8d-ff9367e0ef71",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Hesse",
     "message": "An envoy from Hesse has arrived with a proposal.",
     "turn_created": 9,
     "details": {},
     "base_title": "Envoy from Hesse",
     "repeat_count": 1
    },
    {
     "id": "552b1a44-5cbe-4a9a-a123-61707f7c98de",
     "type": "strategic_order_complete",
     "priority": 1,
     "title": "Soult arrived",
     "message": "Soult has completed their SUPPORT order \u2014 arrived at Tyrol.",
     "turn_created": 9,
     "details": {
      "marshal": "Soult",
      "order_type": "SUPPORT",
      "target": "Ney"
     },
     "base_title": "Soult arrived",
     "repeat_count": 1
    },
    {
     "id": "6e5cb538-9460-469d-8e1a-fd9ba4fe4d95",
     "type": "incoming_settlement_offer",
     "priority": 1,
     "title": "Settlement offer from Britain (x2)",
     "message": "Britain has offered terms to settle France vs Britain. Asking 629 gold.",
     "turn_created": 8,
     "details": {
      "war_id": "war_1",
      "offer_id": "settlement_offer:war_1:8:1",
      "proposer_nation": "Britain",
      "amount": 629,
      "review_target": "incoming_settlement_offer_popup"
     },
     "base_title": "Settlement offer from Britain",
     "repeat_count": 2
    },
    {
     "id": "73f91faa-7c19-4dee-befa-77e8ca2425e8",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Massena grows bitter",
     "message": "Marshal Massena's victories remain unrewarded (expects 80g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente to stop
     the erosion.",
     "turn_created": 8,
     "details": {
      "marshal": "Massena",
      "expectation": 80,
      "satisfaction": 0,
      "shortfall": 80
     },
     "base_title": "Marshal Massena grows bitter",
     "repeat_count": 1
    },
    {
     "id": "8d47d698-a84b-422c-a5a4-6970c962bb5e",
     "type": "counter_punch_earned",
     "priority": 1,
     "title": "Bernadotte \u2014 free attack!",
     "message": "Bernadotte earned a free attack from their defensive victory. Use within 2 turns or
     the opportunity expires.",
     "turn_created": 7,
     "details": {
      "marshal": "Bernadotte"
     },
     "base_title": "Bernadotte \u2014 free attack!",
     "repeat_count": 1
    },
    {
     "id": "c9fdca21-9c08-4ec6-886a-3fe7a7f02fa8",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Ney grows bitter",
     "message": "Marshal Ney's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Ney",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Ney grows bitter",
     "repeat_count": 1
    },
    {
     "id": "ff90a7da-d536-4658-af81-bbd0a31ad89d",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Davout grows bitter",
     "message": "Marshal Davout's victories remain unrewarded (expects 240g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,


====================================================================================================
> Murat, march on Vienna
====================================================================================================
You must decide how to handle the captured region first!
Your forces have taken Bohemia. Plunder it for 800 gold — buildings burned, the province left
  hostile — or secure it and keep the country quiet? ('plunder' or 'secure')
-- POPUP/DIALOGUE [envoy_digest] --
   {
    "turn": 10,
    "count": 1,
    "title": "A SMALL COURT WRITES",
    "lapsing_count": 1,
    "headline": "Hesse writes.",
    "deadline_note": "Answer them here. Unanswered letters lapse when the turn ends, and a court
     left waiting will not raise the matter again for some seasons.",
    "items": [
     {
      "mailbox_id": 17,
      "dialogue_id": 21,
      "from_nation": "Hesse",
      "power_tier": "minor",
      "proposal_type": "open_borders",
      "proposal_type_display": "Open Borders Agreement",
      "diplomat_name": "Chancery of Hesse",
      "diplomat_line": "Hesse, wishing to go unnoticed: \"Hesse counts what a quarrel with France
     would cost and what an understanding would return, and finds the ledger unanimous. Open the
     borders.\"",
      "clauses": [
       "Proposal: Open Borders Agreement",
       "Clause: Open borders"
      ],
      "acceptance_hint": "natural willingness to negotiate",
      "state": "WAITING",
      "arrival_turn": 9
     }
    ]
   }
-- POPUP/DIALOGUE [pending_capture_choice] --
   true
-- POPUP/DIALOGUE [notifications] --
   [
    {
     "id": "11eb075a-98d7-4a9b-94f1-ee058610f860",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Bernadotte grows bitter (x2)",
     "message": "Marshal Bernadotte's victories remain unrewarded (expects 240g/turn of estates;
     holds 160g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente
     to stop the erosion.",
     "turn_created": 10,
     "details": {
      "marshal": "Bernadotte",
      "expectation": 240,
      "satisfaction": 160,
      "shortfall": 80
     },
     "base_title": "Marshal Bernadotte grows bitter",
     "repeat_count": 2
    },
    {
     "id": "d32e9d62-0c5b-4d49-a5ba-5465f3102611",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Prussia",
     "message": "An envoy from Prussia has arrived with a proposal.",
     "turn_created": 9,
     "details": {},
     "base_title": "Envoy from Prussia",
     "repeat_count": 1
    },
    {
     "id": "fc301eca-f803-46d7-ba8d-ff9367e0ef71",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Hesse",
     "message": "An envoy from Hesse has arrived with a proposal.",
     "turn_created": 9,
     "details": {},
     "base_title": "Envoy from Hesse",
     "repeat_count": 1
    },
    {
     "id": "552b1a44-5cbe-4a9a-a123-61707f7c98de",
     "type": "strategic_order_complete",
     "priority": 1,
     "title": "Soult arrived",
     "message": "Soult has completed their SUPPORT order \u2014 arrived at Tyrol.",
     "turn_created": 9,
     "details": {
      "marshal": "Soult",
      "order_type": "SUPPORT",
      "target": "Ney"
     },
     "base_title": "Soult arrived",
     "repeat_count": 1
    },
    {
     "id": "6e5cb538-9460-469d-8e1a-fd9ba4fe4d95",
     "type": "incoming_settlement_offer",
     "priority": 1,
     "title": "Settlement offer from Britain (x2)",
     "message": "Britain has offered terms to settle France vs Britain. Asking 629 gold.",
     "turn_created": 8,
     "details": {
      "war_id": "war_1",
      "offer_id": "settlement_offer:war_1:8:1",
      "proposer_nation": "Britain",
      "amount": 629,
      "review_target": "incoming_settlement_offer_popup"
     },
     "base_title": "Settlement offer from Britain",
     "repeat_count": 2
    },
    {
     "id": "73f91faa-7c19-4dee-befa-77e8ca2425e8",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Massena grows bitter",
     "message": "Marshal Massena's victories remain unrewarded (expects 80g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente to stop
     the erosion.",
     "turn_created": 8,
     "details": {
      "marshal": "Massena",
      "expectation": 80,
      "satisfaction": 0,
      "shortfall": 80
     },
     "base_title": "Marshal Massena grows bitter",
     "repeat_count": 1
    },
    {
     "id": "8d47d698-a84b-422c-a5a4-6970c962bb5e",
     "type": "counter_punch_earned",
     "priority": 1,
     "title": "Bernadotte \u2014 free attack!",
     "message": "Bernadotte earned a free attack from their defensive victory. Use within 2 turns or
     the opportunity expires.",
     "turn_created": 7,
     "details": {
      "marshal": "Bernadotte"
     },
     "base_title": "Bernadotte \u2014 free attack!",
     "repeat_count": 1
    },
    {
     "id": "c9fdca21-9c08-4ec6-886a-3fe7a7f02fa8",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Ney grows bitter",
     "message": "Marshal Ney's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Ney",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Ney grows bitter",
     "repeat_count": 1
    },
    {
     "id": "ff90a7da-d536-4658-af81-bbd0a31ad89d",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Davout grows bitter",
     "message": "Marshal Davout's victories remain unrewarded (expects 240g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,


====================================================================================================
> plunder
====================================================================================================
Davout's troops plunder Bohemia! Gained 800 gold. Buildings destroyed. Stability set to 10.
   <event plunder> {"region": "Bohemia", "capturer": "Davout", "gold_gained": 800}
-- POPUP/DIALOGUE [envoy_digest] --
   {
    "turn": 10,
    "count": 1,
    "title": "A SMALL COURT WRITES",
    "lapsing_count": 1,
    "headline": "Hesse writes.",
    "deadline_note": "Answer them here. Unanswered letters lapse when the turn ends, and a court
     left waiting will not raise the matter again for some seasons.",
    "items": [
     {
      "mailbox_id": 17,
      "dialogue_id": 21,
      "from_nation": "Hesse",
      "power_tier": "minor",
      "proposal_type": "open_borders",
      "proposal_type_display": "Open Borders Agreement",
      "diplomat_name": "Chancery of Hesse",
      "diplomat_line": "Hesse, wishing to go unnoticed: \"Hesse counts what a quarrel with France
     would cost and what an understanding would return, and finds the ledger unanimous. Open the
     borders.\"",
      "clauses": [
       "Proposal: Open Borders Agreement",
       "Clause: Open borders"
      ],
      "acceptance_hint": "natural willingness to negotiate",
      "state": "WAITING",
      "arrival_turn": 9
     }
    ]
   }
-- POPUP/DIALOGUE [capture_choice] --
   "plunder"
-- POPUP/DIALOGUE [notifications] --
   [
    {
     "id": "11eb075a-98d7-4a9b-94f1-ee058610f860",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Bernadotte grows bitter (x2)",
     "message": "Marshal Bernadotte's victories remain unrewarded (expects 240g/turn of estates;
     holds 160g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente
     to stop the erosion.",
     "turn_created": 10,
     "details": {
      "marshal": "Bernadotte",
      "expectation": 240,
      "satisfaction": 160,
      "shortfall": 80
     },
     "base_title": "Marshal Bernadotte grows bitter",
     "repeat_count": 2
    },
    {
     "id": "d32e9d62-0c5b-4d49-a5ba-5465f3102611",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Prussia",
     "message": "An envoy from Prussia has arrived with a proposal.",
     "turn_created": 9,
     "details": {},
     "base_title": "Envoy from Prussia",
     "repeat_count": 1
    },
    {
     "id": "fc301eca-f803-46d7-ba8d-ff9367e0ef71",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Hesse",
     "message": "An envoy from Hesse has arrived with a proposal.",
     "turn_created": 9,
     "details": {},
     "base_title": "Envoy from Hesse",
     "repeat_count": 1
    },
    {
     "id": "552b1a44-5cbe-4a9a-a123-61707f7c98de",
     "type": "strategic_order_complete",
     "priority": 1,
     "title": "Soult arrived",
     "message": "Soult has completed their SUPPORT order \u2014 arrived at Tyrol.",
     "turn_created": 9,
     "details": {
      "marshal": "Soult",
      "order_type": "SUPPORT",
      "target": "Ney"
     },
     "base_title": "Soult arrived",
     "repeat_count": 1
    },
    {
     "id": "6e5cb538-9460-469d-8e1a-fd9ba4fe4d95",
     "type": "incoming_settlement_offer",
     "priority": 1,
     "title": "Settlement offer from Britain (x2)",
     "message": "Britain has offered terms to settle France vs Britain. Asking 629 gold.",
     "turn_created": 8,
     "details": {
      "war_id": "war_1",
      "offer_id": "settlement_offer:war_1:8:1",
      "proposer_nation": "Britain",
      "amount": 629,
      "review_target": "incoming_settlement_offer_popup"
     },
     "base_title": "Settlement offer from Britain",
     "repeat_count": 2
    },
    {
     "id": "73f91faa-7c19-4dee-befa-77e8ca2425e8",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Massena grows bitter",
     "message": "Marshal Massena's victories remain unrewarded (expects 80g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente to stop
     the erosion.",
     "turn_created": 8,
     "details": {
      "marshal": "Massena",
      "expectation": 80,
      "satisfaction": 0,
      "shortfall": 80
     },
     "base_title": "Marshal Massena grows bitter",
     "repeat_count": 1
    },
    {
     "id": "8d47d698-a84b-422c-a5a4-6970c962bb5e",
     "type": "counter_punch_earned",
     "priority": 1,
     "title": "Bernadotte \u2014 free attack!",
     "message": "Bernadotte earned a free attack from their defensive victory. Use within 2 turns or
     the opportunity expires.",
     "turn_created": 7,
     "details": {
      "marshal": "Bernadotte"
     },
     "base_title": "Bernadotte \u2014 free attack!",
     "repeat_count": 1
    },
    {
     "id": "c9fdca21-9c08-4ec6-886a-3fe7a7f02fa8",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Ney grows bitter",
     "message": "Marshal Ney's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Ney",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Ney grows bitter",
     "repeat_count": 1
    },
    {
     "id": "ff90a7da-d536-4658-af81-bbd0a31ad89d",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Davout grows bitter",
     "message": "Marshal Davout's victories remain unrewarded (expects 240g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,


====================================================================================================
> Murat, march on Vienna
====================================================================================================
Murat begins march to Vienna. Route: Bohemia -> Vienna. Moves to Bohemia. Murat: "Good. An army rots
  standing still."
   [cost=1  turn_advanced=False]
-- POPUP/DIALOGUE [envoy_digest] --
   {
    "turn": 10,
    "count": 1,
    "title": "A SMALL COURT WRITES",
    "lapsing_count": 1,
    "headline": "Hesse writes.",
    "deadline_note": "Answer them here. Unanswered letters lapse when the turn ends, and a court
     left waiting will not raise the matter again for some seasons.",
    "items": [
     {
      "mailbox_id": 17,
      "dialogue_id": 21,
      "from_nation": "Hesse",
      "power_tier": "minor",
      "proposal_type": "open_borders",
      "proposal_type_display": "Open Borders Agreement",
      "diplomat_name": "Chancery of Hesse",
      "diplomat_line": "Hesse, wishing to go unnoticed: \"Hesse counts what a quarrel with France
     would cost and what an understanding would return, and finds the ledger unanimous. Open the
     borders.\"",
      "clauses": [
       "Proposal: Open Borders Agreement",
       "Clause: Open borders"
      ],
      "acceptance_hint": "natural willingness to negotiate",
      "state": "WAITING",
      "arrival_turn": 9
     }
    ]
   }
-- POPUP/DIALOGUE [marshal_petition] --
   {
    "kind": "jealousy_confrontation",
    "title": "Marshal Bernadotte seeks an audience",
    "body": "Sire, Bernadotte has expressed reservations about the recognition afforded to Ney. He
     requests that his contributions be... noted. The feud with Ney is now mutual and the army knows
     it. He asks, plainly, where the Emperor stands.",
    "speaker": "Bernadotte",
    "options": [
     {
      "id": "acknowledge",
      "label": "Acknowledge",
      "detail": "Free, and it fixes nothing: the grievance stands 2 more turns \u2014 souring his
     ties and coordination with Ney \u2014 then cools on its own.",
      "cost_note": "",
      "enabled": true
     },
     {
      "id": "promise",
      "label": "Promise Glory",
      "detail": "His patience is bought \u2014 the grievance shortens by 2 turns.",
      "cost_note": "1 AP",
      "ap_cost": 1,
      "enabled": true
     },
     {
      "id": "rebuke",
      "label": "Rebuke",
      "detail": "Trust -5. The grievance shortens by 1 turn.",
      "cost_note": "",
      "enabled": true
     }
    ],
    "context": {
     "marshal": "Bernadotte",
     "target": "Ney",
     "escalation_level": 3
    },
    "turn": 9
   }
-- POPUP/DIALOGUE [notifications] --
   [
    {
     "id": "11eb075a-98d7-4a9b-94f1-ee058610f860",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Bernadotte grows bitter (x2)",
     "message": "Marshal Bernadotte's victories remain unrewarded (expects 240g/turn of estates;
     holds 160g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente
     to stop the erosion.",
     "turn_created": 10,
     "details": {
      "marshal": "Bernadotte",
      "expectation": 240,
      "satisfaction": 160,
      "shortfall": 80
     },
     "base_title": "Marshal Bernadotte grows bitter",
     "repeat_count": 2
    },
    {
     "id": "d32e9d62-0c5b-4d49-a5ba-5465f3102611",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Prussia",
     "message": "An envoy from Prussia has arrived with a proposal.",
     "turn_created": 9,
     "details": {},
     "base_title": "Envoy from Prussia",
     "repeat_count": 1
    },
    {
     "id": "fc301eca-f803-46d7-ba8d-ff9367e0ef71",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Hesse",
     "message": "An envoy from Hesse has arrived with a proposal.",
     "turn_created": 9,
     "details": {},
     "base_title": "Envoy from Hesse",
     "repeat_count": 1
    },
    {
     "id": "552b1a44-5cbe-4a9a-a123-61707f7c98de",
     "type": "strategic_order_complete",
     "priority": 1,
     "title": "Soult arrived",
     "message": "Soult has completed their SUPPORT order \u2014 arrived at Tyrol.",
     "turn_created": 9,
     "details": {
      "marshal": "Soult",
      "order_type": "SUPPORT",
      "target": "Ney"
     },
     "base_title": "Soult arrived",
     "repeat_count": 1
    },
    {
     "id": "6e5cb538-9460-469d-8e1a-fd9ba4fe4d95",
     "type": "incoming_settlement_offer",
     "priority": 1,
     "title": "Settlement offer from Britain (x2)",
     "message": "Britain has offered terms to settle France vs Britain. Asking 629 gold.",
     "turn_created": 8,
     "details": {
      "war_id": "war_1",
      "offer_id": "settlement_offer:war_1:8:1",
      "proposer_nation": "Britain",
      "amount": 629,
      "review_target": "incoming_settlement_offer_popup"
     },
     "base_title": "Settlement offer from Britain",
     "repeat_count": 2
    },
    {
     "id": "73f91faa-7c19-4dee-befa-77e8ca2425e8",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Massena grows bitter",
     "message": "Marshal Massena's victories remain unrewarded (expects 80g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente to stop
     the erosion.",
     "turn_created": 8,
     "details": {
      "marshal": "Massena",
      "expectation": 80,
      "satisfaction": 0,
      "shortfall": 80
     },
     "base_title": "Marshal Massena grows bitter",
     "repeat_count": 1
    },
    {
     "id": "8d47d698-a84b-422c-a5a4-6970c962bb5e",
     "type": "counter_punch_earned",
     "priority": 1,
     "title": "Bernadotte \u2014 free attack!",
     "message": "Bernadotte earned a free attack from their defensive victory. Use within 2 turns or
     the opportunity expires.",
     "turn_created": 7,
     "details": {
      "marshal": "Bernadotte"
     },
     "base_title": "Bernadotte \u2014 free attack!",
     "repeat_count": 1
    },
    {
     "id": "c9fdca21-9c08-4ec6-886a-3fe7a7f02fa8",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Ney grows bitter",
     "message": "Marshal Ney's victories remain unrewarded (expects 200g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,
     "details": {
      "marshal": "Ney",
      "expectation": 200,
      "satisfaction": 0,
      "shortfall": 200
     },
     "base_title": "Marshal Ney grows bitter",
     "repeat_count": 1
    },
    {
     "id": "ff90a7da-d536-4658-af81-bbd0a31ad89d",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Davout grows bitter",
     "message": "Marshal Davout's victories remain unrewarded (expects 240g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 no conquered province remains to endow \u2014 grant a
     rente, or let victory furnish an estate.",
     "turn_created": 4,


====================================================================================================
> end turn
====================================================================================================
Turn 10 ended. (Warning: 1 action(s) unused) Turn 11 begins!

Income: 3481g | Occupation: -130g | Charges of Empire: -1482g | Rentes: -2010g | Admiralty: -90g |
  Blockade: -250g | Upkeep: 856g | Other: +1222g | Net: -115g | Treasury: 16,813g
   [cost=0  turn_advanced=False]
   <event supply_attrition> {"marshal": "Davout", "nation": "France", "region": "Bohemia", "losses": 416, "message": "Supply shortage at Bohemia: Davout loses 416 troops"}
   <event supply_attrition> {"marshal": "Murat", "nation": "France", "region": "Bohemia", "losses": 234, "message": "Supply shortage at Bohemia: Murat loses 234 troops"}
   <event supply_attrition> {"marshal": "Massena", "nation": "France", "region": "Bohemia", "losses": 287, "message": "Supply shortage at Bohemia: Massena loses 287 troops"}
   <event supply_attrition> {"marshal": "Ney", "nation": "France", "region": "Tyrol", "losses": 172, "message": "Supply shortage at Tyrol: Ney loses 172 troops"}
   <event supply_attrition> {"marshal": "Soult", "nation": "France", "region": "Tyrol", "losses": 266, "message": "Supply shortage at Tyrol: Soult loses 266 troops"}
   <event british_subsidy> {"recipient": "Austria", "payer": "Britain", "amount": 200, "war_id": "war_1", "subsidy_source_detail": "unique_eligible", "message": "Britain subsidizes Austria with 200 gold."}
   <event jealousy_resolved> {"message": "Lannes's resentment of Murat has cooled for now. What was settled between them at the staff table has not been.", "nation": "France", "marshal": "Lannes"}
   <event jealousy_fired> {"message": "Berthier reports that Lannes resents Murat's laurels for the third time \u2014 he has grown restless for glory.", "nation": "France", "marshal": "Lannes", "target": "Murat"}
   <event jealousy_fired> {"message": "Berthier reports that Murat appears envious of Lannes's laurels \u2014 he has grown restless for glory.", "nation": "France", "marshal": "Murat", "target": "Lannes"}
   <event jealousy_escalation> {"message": "The feud between Lannes and Murat is now mutual \u2014 each schemes against the other. Separate them, Sire, or accept the friction.", "nation": "France", "marshal": "Lannes", "target": "Murat"}
   <event jealousy_fired> {"message": "Berthier reports that Davout appears envious of Murat's laurels \u2014 he has grown cold and withholding.", "nation": "France", "marshal": "Davout", "target": "Murat"}
   <event jealousy_autonomous_warning> {"message": "Ney is eyeing Shrapnel's position at Carniola. I cannot guarantee he will wait for orders, Sire \u2014 any command would restrain him.", "nation": "France", "marshal": "Ney"}
   <event jealousy_separation_warning> {"message": "Berthier reminds you: Bernadotte and Ney now stand within reach of each other. You asked to be warned.", "nation": "France", "marshal": "Bernadotte"}
   <event intel_decayed> {"region": "Brunswick", "old_visibility": "partial", "new_visibility": "stale"}
   <event intel_decayed> {"region": "Galicia", "old_visibility": "full", "new_visibility": "stale"}
   <event strategic_progress> {"marshal": "Murat", "command": "MOVE_TO", "order_status": "active", "message": "Murat is marching to Vienna (1 turn(s) remaining)."}

####################################################################################################
# THE ENEMY PHASE
####################################################################################################
-- Britain --
  - Shrapnel embarks an expedition for Carniola
      [expedition_landed] {"type": "expedition_landed", "marshal": "Shrapnel", "target": "Carniola"}
    [action_count] 3
-- Austria --
  - ArchdukeCharles attacks Davout
      [battle] Third Battle of Bohemia  -> defender_tactical_victory  victor=Davout
        ATK ArchdukeCharles  lost   5,381  left  28,711  morale   0  ROUTED
        DEF Davout           lost     816  left  20,823  morale  70
        defender order of battle: Davout 21,186(engaged); Massena 14,612(reinforced); Murat 11,949(engaged); Ney 13,785(failed_arrive)
    [action_count] 1
-- Bavaria --
  - Deroy holds position
      [wait] {"type": "wait", "marshal": "Deroy", "location": "Franconia", "action_cost": 0}
    [action_count] 2
[summary]
   Shrapnel: naval_expedition → Carniola
   ArchdukeCharles: attack → Davout
   Deroy: wait

####################################################################################################
# THE MORNING DISPATCH
####################################################################################################
{
 "turn": 11,
 "situation": {
  "player_regions": 30,
  "enemy_regions": 96,
  "treasury": 16813,
  "treasury_delta": -68,
  "trade_income": 500,
  "occupation": 130,
  "contributions": 0,
  "state_charges": 1475,
  "requisitions": 0,
  "overseas": 0,
  "dotation_skim": 0,
  "unmet_marshals": [
   {
    "marshal": "Davout",
    "expectation": 300,
    "satisfaction": 240,
    "shortfall": 60,
    "eroding": true,
    "grace_turns_left": 0,
    "pension": 240
   },
   {
    "marshal": "Soult",
    "expectation": 200,
    "satisfaction": 160,
    "shortfall": 40,
    "eroding": false,
    "grace_turns_left": 1,
    "pension": 160
   },
   {
    "marshal": "Murat",
    "expectation": 300,
    "satisfaction": 280,
    "shortfall": 20,
    "eroding": true,
    "grace_turns_left": 0,
    "pension": 280
   },
   {
    "marshal": "Bernadotte",
    "expectation": 240,
    "satisfaction": 160,
    "shortfall": 80,
    "eroding": true,
    "grace_turns_left": 0,
    "pension": 160
   },
   {
    "marshal": "Massena",
    "expectation": 200,
    "satisfaction": 0,
    "shortfall": 200,
    "eroding": true,
    "grace_turns_left": 0,
    "pension": 0
   }
  ],
  "rente_cost": 2010,
  "expectation_rises": [
   {
    "marshal": "Massena",
    "expectation": 200,
    "previous": 120,
    "satisfaction": 0
   }
  ],
  "blockade": 250,
  "admiralty": 90,
  "upkeep_surcharge": 0,
  "force_limit": 135000,
  "over_force_limit": false,
  "bankrupt": false,
  "strength_ratio_pct": 30,
  "authority": 100,
  "authority_label": "Strong"
 },
 "marshals": [
  {
   "name": "Soult",
   "location": "Tyrol",
   "strength": 21017,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 4,
   "danger": "Starving \u2014 supply has failed at Tyrol two turns running.",
   "trust": 65,
   "trust_notable": false,
   "morale": 80,
   "morale_warning": false
  },
  {
   "name": "Davout",
   "location": "Bohemia",
   "strength": 20407,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 0,
   "danger": "Starving \u2014 supply has failed at Bohemia two turns running.",
   "trust": 76,
   "trust_notable": false,
   "morale": 70,
   "morale_warning": false
  },
  {
   "name": "Lannes",
   "location": "Rhineland",
   "strength": 16505,
   "status": "idle_restless",
   "status_note": "7 turns idle.",
   "arc_note": "",
   "idle_turns": 7,
   "danger": "",
   "trust": 75,
   "trust_notable": false,
   "morale": 85,
   "morale_warning": false
  },
  {
   "name": "Massena",
   "location": "Bohemia",
   "strength": 14076,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 1,
   "danger": "Morale failing (0) \u2014 the men waver.",
   "trust": 50,
   "trust_notable": true,
   "morale": 0,
   "morale_warning": true
  },
  {
   "name": "Ney",
   "location": "Tyrol",
   "strength": 13613,
   "status": "idle_restless",
   "status_note": "3 turns idle.",
   "arc_note": "",
   "idle_turns": 3,
   "danger": "Starving \u2014 supply has failed at Tyrol two turns running.",
   "trust": 56,
   "trust_notable": false,
   "morale": 65,
   "morale_warning": false
  },
  {
   "name": "Bernadotte",
   "location": "Munich",
   "strength": 12378,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 4,
   "danger": "",
   "trust": 26,
   "trust_notable": true,
   "morale": 80,
   "morale_warning": false
  },
  {
   "name": "Murat",
   "location": "Bohemia",
   "strength": 11511,
   "status": "en_route",
   "status_note": "Moving to Vienna.",
   "arc_note": "",
   "idle_turns": 0,
   "danger": "Starving \u2014 supply has failed at Bohemia two turns running.",
   "trust": 61,
   "trust_notable": false,
   "morale": 53,
   "morale_warning": true
  }
 ],
 "intelligence": [
  {
   "name": "Deroy",
   "location": "Franconia",
   "strength_display": "8,699",
   "visibility": "full",
   "intel_turn": 9
  },
  {
   "name": "Paget",
   "location": "Leon",
   "strength_display": "626",
   "visibility": "full",
   "intel_turn": 9
  },
  {
   "name": "Kutuzov",
   "location": "Hungary",
   "strength_display": "substantial force",
   "visibility": "partial",
   "intel_turn": 11
  },
  {
   "name": "Castanos",
   "location": "Aragon",
   "strength_display": "small force",
   "visibility": "stale",
   "intel_turn": 7
  },
  {
   "name": "Mack",
   "location": "Berlin",
   "strength_display": "screening force",
   "visibility": "last_known",
   "intel_turn": 5
  },
  {
   "name": "Brunswick",
   "location": "Berlin",
   "strength_display": "large force",
   "visibility": "last_known",
   "intel_turn": 5
  }
 ],
 "turn_events": [
  {
   "message": "Supply shortage at Bohemia: Davout loses 416 troops",
   "severity": "warning"
  },
  {
   "message": "Supply shortage at Bohemia: Murat loses 234 troops",
   "severity": "warning"
  },
  {
   "message": "Supply shortage at Bohemia: Massena loses 287 troops",
   "severity": "warning"
  },
  {
   "message": "Supply shortage at Tyrol: Ney loses 172 troops",
   "severity": "warning"
  },
  {
   "message": "Supply shortage at Tyrol: Soult loses 266 troops",
   "severity": "warning"
  },
  {
   "message": "Lannes's resentment of Murat has cooled for now. What was settled between them at the
  staff table has not been.",
   "severity": "good"
  },
  {
   "message": "Berthier reports that Lannes resents Murat's laurels for the third time \u2014 he has
  grown restless for glory.",
   "severity": "warning"
  },
  {
   "message": "Berthier reports that Murat appears envious of Lannes's laurels \u2014 he has grown
  restless for glory.",
   "severity": "warning"
  },
  {
   "message": "The feud between Lannes and Murat is now mutual \u2014 each schemes against the
  other. Separate them, Sire, or accept the friction.",
   "severity": "warning"
  },
  {
   "message": "Berthier reports that Davout appears envious of Murat's laurels \u2014 he has grown
  cold and withholding.",
   "severity": "warning"
  },
  {
   "message": "Ney is eyeing Shrapnel's position at Carniola. I cannot guarantee he will wait for
  orders, Sire \u2014 any command would restrain him.",
   "severity": "warning"
  },
  {
   "message": "Berthier reminds you: Bernadotte and Ney now stand within reach of each other. You
  asked to be warned.",
   "severity": "warning"
  }
 ],
 "headline": {
  "class": "victory_won",
  "weight": 73,
  "text": "Sire \u2014 Marshal Davout holds the field at Bohemia \u2014 Archduke Charles's corps is
  broken and flees.",
  "sub_beats": [
   "Sire \u2014 Ney and Soult stand 34,630 men at Tyrol, which feeds 30,000. 4,630 too many. 7,515
  men lost in 3 turns. A supply depot at Tyrol would ease it; dispersing a corps would end it.",
   "Sire \u2014 Marshal Davout's household goes unpaid. His patience erodes with his purse."
  ]
 },
 "berthier_note": "The army knows it is winning, Sire. Press the advantage before their line
  reforms.",
 "talleyrand_report": [
  {
   "message": "Sire, the diplomatic front has been quiet. Perhaps too quiet. Shall I assess our
  options?",
   "trigger_type": "idle_nudge",
   "target_nation": "",
   "priority": 5,
   "elaborate_type": "proposal_options"
  }
 ],
 "talleyrand_discovery": null,
 "talleyrand_override_note": null,
 "talleyrand_redemption": null,
 "coalition_status": {
  "threat_level": 76,
  "tier": "Formed",
  "sources": [
   {
    "source": "hegemony_passive",
    "amount": 1,
    "target": "France"
   },
   {
    "source": "decay",
    "amount": -3
   }
  ],
  "active_coalition": {
   "name": "Third Coalition",
   "leader": "Britain",
   "posture": "defensive",
   "formed_turn": 1,
   "members": [
    {
     "nation": "Austria",
     "war_exhaustion": 0,
     "strength_display": "40,517 men",
     "strength": 0,
     "gold": 0
    },
    {
     "nation": "Britain",
     "war_exhaustion": 92,
     "strength_display": "33,000 men",
     "strength": 33000,
     "gold": 4616
    },
    {
     "nation": "Russia",
     "war_exhaustion": 90,
     "strength_display": "~65,000 men",
     "strength": 0,
     "gold": 0
    }
   ]
  }
 },
 "diplomatic_events": [
  {
   "type": "diplomatic_dp_regen",
   "text": "Talleyrand reports: 5 diplomatic points available (base 3, +1 skill, +1 authority).",
   "priority": "LOW"
  },
  {
   "type": "paymaster_subsidy",
   "text": "Britain's gold reaches Austria \u2014 the subsidy stands at 200 this season.",
   "priority": "MEDIUM"
  },
  {
   "type": "agenda_shift",
   "text": "The court of Austria takes up a new design: Revanche.",
   "priority": "MEDIUM"
  }
 ],
 "lapsed_offers": [
  {
   "nation": "Prussia",
   "proposal_type": "open borders"
  },
  {
   "nation": "Hesse",
   "proposal_type": "open borders"
  }
 ],
 "pending_envoy_count": 4,
 "pending_envoys": [
  {
   "nation": "KingdomOfItaly",
   "proposal_type": "request reward or restoration",
   "state": "ACTIVE"
  },
  {
   "nation": "Britain",
   "proposal_type": "settlement offer",
   "state": "WAITING"
  },
  {
   "nation": "PapalStates",
   "proposal_type": "open borders",
   "state": "WAITING"
  },
  {
   "nation": "Bavaria",
   "proposal_type": "request reward or restoration",
   "state": "WAITING"
  }
 ]
}
-- POPUP/DIALOGUE [notifications] --
   [
    {
     "id": "ff90a7da-d536-4658-af81-bbd0a31ad89d",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Davout grows bitter (x2)",
     "message": "Marshal Davout's victories remain unrewarded (expects 300g/turn of estates; holds
     240g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente to stop
     the erosion.",
     "turn_created": 11,
     "details": {
      "marshal": "Davout",
      "expectation": 300,
      "satisfaction": 240,
      "shortfall": 60
     },
     "base_title": "Marshal Davout grows bitter",
     "repeat_count": 2
    },
    {
     "id": "ea9c2894-880f-4204-90ba-93891be05813",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Murat grows bitter (x2)",
     "message": "Marshal Murat's victories remain unrewarded (expects 300g/turn of estates; holds
     280g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente to stop
     the erosion.",
     "turn_created": 11,
     "details": {
      "marshal": "Murat",
      "expectation": 300,
      "satisfaction": 280,
      "shortfall": 20
     },
     "base_title": "Marshal Murat grows bitter",
     "repeat_count": 2
    },
    {
     "id": "11eb075a-98d7-4a9b-94f1-ee058610f860",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Bernadotte grows bitter (x2)",
     "message": "Marshal Bernadotte's victories remain unrewarded (expects 240g/turn of estates;
     holds 160g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente
     to stop the erosion.",
     "turn_created": 10,
     "details": {
      "marshal": "Bernadotte",
      "expectation": 240,
      "satisfaction": 160,
      "shortfall": 80
     },
     "base_title": "Marshal Bernadotte grows bitter",
     "repeat_count": 2
    },
    {
     "id": "36d9d8db-6539-449d-a72e-e376e20d03dc",
     "type": "counter_punch_earned",
     "priority": 1,
     "title": "Davout \u2014 free attack!",
     "message": "Davout earned a free attack from their defensive victory. Use within 2 turns or the
     opportunity expires.",
     "turn_created": 10,
     "details": {
      "marshal": "Davout"
     },
     "base_title": "Davout \u2014 free attack!",
     "repeat_count": 1
    },
    {
     "id": "a43863cd-f0c3-4ca3-858c-2f5951848d5f",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Papal States",
     "message": "An envoy from Papal States has arrived with a proposal.",
     "turn_created": 10,
     "details": {},
     "base_title": "Envoy from Papal States",
     "repeat_count": 1
    },
    {
     "id": "552b1a44-5cbe-4a9a-a123-61707f7c98de",
     "type": "strategic_order_complete",
     "priority": 1,
     "title": "Soult arrived",
     "message": "Soult has completed their SUPPORT order \u2014 arrived at Tyrol.",
     "turn_created": 9,
     "details": {
      "marshal": "Soult",
      "order_type": "SUPPORT",
      "target": "Ney"
     },
     "base_title": "Soult arrived",
     "repeat_count": 1
    },
    {
     "id": "6e5cb538-9460-469d-8e1a-fd9ba4fe4d95",
     "type": "incoming_settlement_offer",
     "priority": 1,
     "title": "Settlement offer from Britain (x2)",
     "message": "Britain has offered terms to settle France vs Britain. Asking 629 gold.",
     "turn_created": 8,
     "details": {
      "war_id": "war_1",
      "offer_id": "settlement_offer:war_1:8:1",
      "proposer_nation": "Britain",
      "amount": 629,
      "review_target": "incoming_settlement_offer_popup"
     },
     "base_title": "Settlement offer from Britain",
     "repeat_count": 2
    },
    {
     "id": "73f91faa-7c19-4dee-befa-77e8ca2425e8",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Massena grows bitter",
     "message": "Marshal Massena's victories remain unrewarded (expects 80g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente to stop
     the erosion.",
     "turn_created": 8,
     "details": {
      "marshal": "Massena",
      "expectation": 80,
      "satisfaction": 0,
      "shortfall": 80
     },
     "base_title": "Marshal Massena grows bitter",
     "repeat_count": 1
    },
    {
     "id": "8d47d698-a84b-422c-a5a4-6970c962bb5e",
     "type": "counter_punch_earned",
     "priority": 1,
     "title": "Bernadotte \u2014 free attack!"

====================================================================================================
> Davout, support Murat
====================================================================================================
Davout moves to support Murat (at Bohemia). Davout will march to Murat's guns — he holds your
  written order. Davout: "As you order. I move when the need is real, not before."
   [cost=1  turn_advanced=False]
-- POPUP/DIALOGUE [envoy_digest] --
   {
    "turn": 11,
    "count": 1,
    "title": "A SMALL COURT WRITES",
    "lapsing_count": 1,
    "headline": "Papal States writes.",
    "deadline_note": "Answer them here. Unanswered letters lapse when the turn ends, and a court
     left waiting will not raise the matter again for some seasons.",
    "items": [
     {
      "mailbox_id": 18,
      "dialogue_id": 23,
      "from_nation": "PapalStates",
      "power_tier": "minor",
      "proposal_type": "friendly_gift",
      "proposal_type_display": "Open Borders Agreement",
      "diplomat_name": "Consalvi",
      "diplomat_line": "Cardinal Consalvi, serenely: \"France has grown so vast that her shadow now
     falls even upon the altar, and Rome, having no armies to set against it, would far sooner offer
     her friendship than her fear. Open the borders.\"",
      "clauses": [
       "Proposal: Open Borders Agreement",
       "Clause: Open borders",
       "Offer: Gold payment - 150"
      ],
      "acceptance_hint": "natural willingness to negotiate",
      "state": "WAITING",
      "arrival_turn": 10
     }
    ]
   }
-- POPUP/DIALOGUE [notifications] --
   [
    {
     "id": "ff90a7da-d536-4658-af81-bbd0a31ad89d",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Davout grows bitter (x2)",
     "message": "Marshal Davout's victories remain unrewarded (expects 300g/turn of estates; holds
     240g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente to stop
     the erosion.",
     "turn_created": 11,
     "details": {
      "marshal": "Davout",
      "expectation": 300,
      "satisfaction": 240,
      "shortfall": 60
     },
     "base_title": "Marshal Davout grows bitter",
     "repeat_count": 2
    },
    {
     "id": "ea9c2894-880f-4204-90ba-93891be05813",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Murat grows bitter (x2)",
     "message": "Marshal Murat's victories remain unrewarded (expects 300g/turn of estates; holds
     280g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente to stop
     the erosion.",
     "turn_created": 11,
     "details": {
      "marshal": "Murat",
      "expectation": 300,
      "satisfaction": 280,
      "shortfall": 20
     },
     "base_title": "Marshal Murat grows bitter",
     "repeat_count": 2
    },
    {
     "id": "11eb075a-98d7-4a9b-94f1-ee058610f860",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Bernadotte grows bitter (x2)",
     "message": "Marshal Bernadotte's victories remain unrewarded (expects 240g/turn of estates;
     holds 160g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente
     to stop the erosion.",
     "turn_created": 10,
     "details": {
      "marshal": "Bernadotte",
      "expectation": 240,
      "satisfaction": 160,
      "shortfall": 80
     },
     "base_title": "Marshal Bernadotte grows bitter",
     "repeat_count": 2
    },
    {
     "id": "36d9d8db-6539-449d-a72e-e376e20d03dc",
     "type": "counter_punch_earned",
     "priority": 1,
     "title": "Davout \u2014 free attack!",
     "message": "Davout earned a free attack from their defensive victory. Use within 2 turns or the
     opportunity expires.",
     "turn_created": 10,
     "details": {
      "marshal": "Davout"
     },
     "base_title": "Davout \u2014 free attack!",
     "repeat_count": 1
    },
    {
     "id": "a43863cd-f0c3-4ca3-858c-2f5951848d5f",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Papal States",
     "message": "An envoy from Papal States has arrived with a proposal.",
     "turn_created": 10,
     "details": {},
     "base_title": "Envoy from Papal States",
     "repeat_count": 1
    },
    {
     "id": "552b1a44-5cbe-4a9a-a123-61707f7c98de",
     "type": "strategic_order_complete",
     "priority": 1,
     "title": "Soult arrived",
     "message": "Soult has completed their SUPPORT order \u2014 arrived at Tyrol.",
     "turn_created": 9,
     "details": {
      "marshal": "Soult",
      "order_type": "SUPPORT",
      "target": "Ney"
     },
     "base_title": "Soult arrived",
     "repeat_count": 1
    },
    {
     "id": "6e5cb538-9460-469d-8e1a-fd9ba4fe4d95",
     "type": "incoming_settlement_offer",
     "priority": 1,
     "title": "Settlement offer from Britain (x2)",
     "message": "Britain has offered terms to settle France vs Britain. Asking 629 gold.",
     "turn_created": 8,
     "details": {
      "war_id": "war_1",
      "offer_id": "settlement_offer:war_1:8:1",
      "proposer_nation": "Britain",
      "amount": 629,
      "review_target": "incoming_settlement_offer_popup"
     },
     "base_title": "Settlement offer from Britain",
     "repeat_count": 2
    },
    {
     "id": "73f91faa-7c19-4dee-befa-77e8ca2425e8",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Massena grows bitter",
     "message": "Marshal Massena's victories remain unrewarded (expects 80g/turn of estates; holds
     0g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente to stop
     the erosion.",
     "turn_created": 8,
     "details": {
      "marshal": "Massena",
      "expectation": 80,
      "satisfaction": 0,
      "shortfall": 80
     },
     "base_title": "Marshal Massena grows bitter",
     "repeat_count": 1
    },
    {
     "id": "8d47d698-a84b-422c-a5a4-6970c962bb5e",
     "type": "counter_punch_earned",
     "priority": 1,
     "title": "Bernadotte \u2014 free attack!"

====================================================================================================
> end turn
====================================================================================================
Turn 11 ended. (Warning: 1 action(s) unused) Turn 12 begins!

Income: 3483g | Occupation: -205g | Charges of Empire: -1516g | Rentes: -2010g | Infrastructure:
  -20g | Admiralty: -90g | Blockade: -250g | Upkeep: 824g | Other: +1202g | Net: -230g | Treasury:
  16,583g
   [cost=0  turn_advanced=False]
   <event counter_punch_expired> {"marshal": "Davout", "nation": "France", "message": "[!] Davout's Counter-Punch opportunity has expired! (Must use immediately after defending)"}
   <event construction_complete> {"region": "Carniola", "building": "market", "message": "Construction complete: Market in Carniola!"}
   <event supply_attrition> {"marshal": "Ney", "nation": "France", "region": "Carniola", "losses": 410, "message": "Supply shortage at Carniola: Ney loses 410 troops"}
   <event supply_attrition> {"marshal": "Davout", "nation": "France", "region": "Carniola", "losses": 623, "message": "Supply shortage at Carniola: Davout loses 623 troops"}
   <event supply_attrition> {"marshal": "Murat", "nation": "France", "region": "Carniola", "losses": 351, "message": "Supply shortage at Carniola: Murat loses 351 troops"}
   <event supply_attrition> {"marshal": "Massena", "nation": "France", "region": "Carniola", "losses": 429, "message": "Supply shortage at Carniola: Massena loses 429 troops"}
   <event supply_attrition> {"marshal": "ArchdukeCharles", "nation": "Austria", "region": "Moravia", "losses": 542, "message": "Supply shortage at Moravia: ArchdukeCharles loses 542 troops"}
   <event supply_attrition> {"marshal": "ArchdukeJohn", "nation": "Austria", "region": "Moravia", "losses": 248, "message": "Supply shortage at Moravia: ArchdukeJohn loses 248 troops"}
   <event supply_attrition> {"marshal": "Bennigsen", "nation": "Russia", "region": "Moravia", "losses": 105, "message": "Supply shortage at Moravia: Bennigsen loses 105 troops"}
   <event vassal_loyalty> {"vassal": "Holland", "lord": "France", "nation": "France", "old_loyalty": 100, "new_loyalty": 100, "delta": 2, "reason": "a common enemy, the lord's victories", "recovery_hint": "", "message": "Holland loyalty 100 (+2): a common enemy, the lord's victories"}
   <event vassal_loyalty> {"vassal": "KingdomOfItaly", "lord": "France", "nation": "France", "old_loyalty": 100, "new_loyalty": 100, "delta": 2, "reason": "a common enemy, the lord's victories", "recovery_hint": "", "message": "KingdomOfItaly loyalty 100 (+2): a common enemy, the lord's victories"}
   <event british_subsidy> {"recipient": "Russia", "payer": "Britain", "amount": 300, "war_id": "war_1", "subsidy_source_detail": "unique_eligible", "message": "Britain subsidizes Russia with 300 gold."}
   <event jealousy_resolved> {"message": "Bernadotte's resentment of Ney has cooled for now. What was settled between them at the staff table has not been.", "nation": "France", "marshal": "Bernadotte"}
   <event jealousy_resolved> {"message": "Davout's grievance is satisfied \u2014 a victory won shoulder to shoulder. He holds with renewed purpose (+10% defense this turn).", "nation": "France", "marshal": "Davout"}
   <event jealousy_autonomous_attack> {"message": "Ney, hungry for glory, has attacked Shrapnel on his own initiative.", "nation": "France", "marshal": "Ney"}
   <event jealousy_resolved> {"message": "Ney's grievance is satisfied \u2014 a victory against a worthy foe. He fights with renewed purpose (+10% attack this turn).", "nation": "France", "marshal": "Ney"}
   <event jealousy_resolved> {"message": "Murat's grievance is satisfied \u2014 a victory against a worthy foe. He fights with renewed purpose (+10% attack this turn).", "nation": "France", "marshal": "Murat"}
   <event jealousy_fired> {"message": "Berthier reports that Bernadotte resents Ney's laurels for the fourth time \u2014 he has grown cold and withholding.", "nation": "France", "marshal": "Bernadotte", "target": "Ney"}
   <event jealousy_fired> {"message": "Berthier reports that Ney resents Bernadotte's laurels again, 2 turns after the last \u2014 he has grown loud at the staff table about who is given the honours.", "nation": "France", "marshal": "Ney", "target": "Bernadotte"}
   <event jealousy_escalation> {"message": "The feud between Bernadotte and Ney is now mutual \u2014 each schemes against the other. Separate them, Sire, or accept the friction.", "nation": "France", "marshal": "Bernadotte", "target": "Ney"}
   <event jealousy_fired> {"message": "Berthier reports that Davout resents Murat's laurels again, 1 turns after the last \u2014 he has grown cold and withholding.", "nation": "France", "marshal": "Davout", "target": "Murat"}
   <event jealousy_restlessness> {"message": "Berthier notes that Soult has been holding position for some time while others receive commands. He may begin to feel... overlooked.", "nation": "France", "marshal": "Soult"}
   <event jealousy_autonomous_warning> {"message": "Ney is eyeing Shrapnel's position at Albania. I cannot guarantee he will wait for orders, Sire \u2014 any command would restrain him.", "nation": "France", "marshal": "Ney"}
   <event glory_crowned> {"message": "Berthier notes that Ney's recent victories have made him the most celebrated commander in the army. (+1 shock, +1 defense, +1 administration while he holds the laurels)", "nation": "France", "marshal": "Ney"}
   <event glory_crown_lost> {"message": "Murat is no longer the army's most celebrated commander \u2014 the laurels have passed.", "nation": "France", "marshal": "Murat"}
   <event intel_updated> {"region": "Albania", "new_visibility": "partial", "old_visibility": "unknown", "source": "adjacent"}
   <event intel_updated> {"region": "Croatia", "new_visibility": "partial", "old_visibility": "unknown", "source": "adjacent"}
   <event intel_decayed> {"region": "Aragon", "old_visibility": "stale", "new_visibility": "last_known"}
   <event intel_decayed> {"region": "Leon", "old_visibility": "full", "new_visibility": "stale"}

####################################################################################################
# THE ENEMY PHASE
####################################################################################################
-- Russia --
  - Bennigsen moves to Moravia
      [move] {"type": "move", "marshal": "Bennigsen", "from": "Podolia", "to": "Moravia", "march_losses": 150}
  - Kutuzov attacks Ney
      [battle] Second Battle of Carniola  -> defender_tactical_victory  victor=Ney
        ATK Kutuzov          lost   4,622  left  27,631  morale  35
        DEF Ney              lost   1,010  left  13,176  morale  55
        defender order of battle: Ney 13,404(engaged); Davout 20,335(engaged); Massena 14,028(engaged); Murat 11,472(engaged); Soult 21,017(refused)
    [action_count] 2
-- Austria --
  - ArchdukeCharles holds position
      [wait] {"type": "wait", "marshal": "ArchdukeCharles", "location": "Moravia", "action_cost": 0}
  - ArchdukeJohn holds position
      [wait] {"type": "wait", "marshal": "ArchdukeJohn", "location": "Moravia", "action_cost": 0}
    [action_count] 2
-- Bavaria --
  - Deroy moves to Bohemia
      [move] {"type": "move", "marshal": "Deroy", "from": "Franconia", "to": "Bohemia", "march_losses": 86}
  - Deroy attacks Hungary
      [conquest] Hungary  capture_choice=secure
  - Deroy attacks Moravia
      [battle] Second Battle of Moravia  -> defender_tactical_victory  victor=ArchdukeCharles
        ATK Deroy            lost   2,339  left   6,188  morale  12  ROUTED
        DEF ArchdukeCharles  lost     947  left  27,121  morale  10
    [action_count] 3
[summary]
   Bennigsen: move → Moravia
   Kutuzov: attack → Ney
   ArchdukeCharles: wait
   ArchdukeJohn: wait
   Deroy: move → Bohemia
   Deroy: attack → Hungary
   Deroy: attack → Moravia

####################################################################################################
# THE MORNING DISPATCH
####################################################################################################
{
 "turn": 12,
 "situation": {
  "player_regions": 31,
  "enemy_regions": 95,
  "treasury": 16583,
  "treasury_delta": -153,
  "trade_income": 500,
  "occupation": 205,
  "contributions": 0,
  "state_charges": 1499,
  "requisitions": 0,
  "overseas": 0,
  "dotation_skim": 0,
  "unmet_marshals": [
   {
    "marshal": "Davout",
    "expectation": 300,
    "satisfaction": 240,
    "shortfall": 60,
    "eroding": true,
    "grace_turns_left": 0,
    "pension": 240
   },
   {
    "marshal": "Soult",
    "expectation": 200,
    "satisfaction": 160,
    "shortfall": 40,
    "eroding": true,
    "grace_turns_left": 0,
    "pension": 160
   },
   {
    "marshal": "Murat",
    "expectation": 300,
    "satisfaction": 280,
    "shortfall": 20,
    "eroding": true,
    "grace_turns_left": 0,
    "pension": 280
   },
   {
    "marshal": "Bernadotte",
    "expectation": 240,
    "satisfaction": 160,
    "shortfall": 80,
    "eroding": true,
    "grace_turns_left": 0,
    "pension": 160
   },
   {
    "marshal": "Massena",
    "expectation": 300,
    "satisfaction": 0,
    "shortfall": 300,
    "eroding": true,
    "grace_turns_left": 0,
    "pension": 0
   }
  ],
  "rente_cost": 2010,
  "expectation_rises": [
   {
    "marshal": "Massena",
    "expectation": 300,
    "previous": 200,
    "satisfaction": 0
   }
  ],
  "blockade": 250,
  "admiralty": 90,
  "upkeep_surcharge": 0,
  "force_limit": 137500,
  "over_force_limit": false,
  "bankrupt": false,
  "strength_ratio_pct": 75,
  "authority": 100,
  "authority_label": "Strong"
 },
 "marshals": [
  {
   "name": "Soult",
   "location": "Tyrol",
   "strength": 21017,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 5,
   "danger": "Starving \u2014 supply has failed at Tyrol two turns running.",
   "trust": 64,
   "trust_notable": false,
   "morale": 80,
   "morale_warning": false
  },
  {
   "name": "Davout",
   "location": "Carniola",
   "strength": 19364,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 1,
   "danger": "Starving \u2014 supply has failed at Carniola two turns running.",
   "trust": 74,
   "trust_notable": false,
   "morale": 60,
   "morale_warning": false
  },
  {
   "name": "Lannes",
   "location": "Rhineland",
   "strength": 16505,
   "status": "idle_restless",
   "status_note": "8 turns idle.",
   "arc_note": "",
   "idle_turns": 8,
   "danger": "",
   "trust": 75,
   "trust_notable": false,
   "morale": 85,
   "morale_warning": false
  },
  {
   "name": "Massena",
   "location": "Carniola",
   "strength": 13360,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 1,
   "danger": "Morale failing (0) \u2014 the men waver.",
   "trust": 47,
   "trust_notable": true,
   "morale": 0,
   "morale_warning": true
  },
  {
   "name": "Ney",
   "location": "Carniola",
   "strength": 12766,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 0,
   "danger": "Starving \u2014 supply has failed at Carniola two turns running.",
   "trust": 56,
   "trust_notable": false,
   "morale": 55,
   "morale_warning": true
  },
  {
   "name": "Bernadotte",
   "location": "Munich",
   "strength": 12378,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 5,
   "danger": "",
   "trust": 24,
   "trust_notable": true,
   "morale": 80,
   "morale_warning": false
  },
  {
   "name": "Murat",
   "location": "Carniola",
   "strength": 10926,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 1,
   "danger": "Starving \u2014 supply has failed at Carniola two turns running.",
   "trust": 60,
   "trust_notable": false,
   "morale": 43,
   "morale_warning": true
  }
 ],
 "intelligence": [
  {
   "name": "Deroy",
   "location": "Franconia",
   "strength_display": "8,699",
   "visibility": "full",
   "intel_turn": 9
  },
  {
   "name": "Archduke Charles",
   "location": "Moravia",
   "strength_display": "27,121",
   "visibility": "full",
   "intel_turn": 11
  },
  {
   "name": "Archduke John",
   "location": "Moravia",
   "strength_display": "12,449",
   "visibility": "full",
   "intel_turn": 11
  },
  {
   "name": "Bennigsen",
   "location": "Moravia",
   "strength_display": "4,850",
   "visibility": "full",
   "intel_turn": 11
  },
  {
   "name": "Shrapnel",
   "location": "Albania",
   "strength_display": "screening force",
   "visibility": "partial",
   "intel_turn": 12
  },
  {
   "name": "Kutuzov",
   "location": "Hungary",
   "strength_display": "substantial force",
   "visibility": "partial",
   "intel_turn": 12
  },
  {
   "name": "Paget",
   "location": "Leon",
   "strength_display": "screening force",
   "visibility": "stale",
   "intel_turn": 9
  },
  {
   "name": "Mack",
   "location": "Berlin",
   "strength_display": "screening force",
   "visibility": "last_known",
   "intel_turn": 5
  },
  {
   "name": "Brunswick",
   "location": "Berlin",
   "strength_display": "large force",
   "visibility": "last_known",
   "intel_turn": 5
  },
  {
   "name": "Castanos",
   "location": "Aragon",
   "strength_display": "small force",
   "visibility": "last_known",
   "intel_turn": 7
  }
 ],
 "turn_events": [
  {
   "message": "[!] Davout's Counter-Punch opportunity has expired! (Must use immediately after
  defending)",
   "severity": "warning"
  },
  {
   "message": "Supply shortage at Carniola: Ney loses 410 troops",
   "severity": "warning"
  },
  {
   "message": "Supply shortage at Carniola: Davout loses 623 troops",
   "severity": "warning"
  },
  {
   "message": "Supply shortage at Carniola: Murat loses 351 troops",
   "severity": "warning"
  },
  {
   "message": "Supply shortage at Carniola: Massena loses 429 troops",
   "severity": "warning"
  },
  {
   "message": "Holland loyalty 100 (+2): a common enemy, the lord's victories",
   "severity": "info"
  },
  {
   "message": "KingdomOfItaly loyalty 100 (+2): a common enemy, the lord's victories",
   "severity": "info"
  },
  {
   "message": "Bernadotte's resentment of Ney has cooled for now. What was settled between them at
  the staff table has not been.",
   "severity": "good"
  },
  {
   "message": "Davout's grievance is satisfied \u2014 a victory won shoulder to shoulder. He holds
  with renewed purpose (+10% defense this turn).",
   "severity": "good"
  },
  {
   "message": "Ney, hungry for glory, has attacked Shrapnel on his own initiative.",
   "severity": "warning"
  },
  {
   "message": "Ney's grievance is satisfied \u2014 a victory against a worthy foe. He fights with
  renewed purpose (+10% attack this turn).",
   "severity": "good"
  },
  {
   "message": "Murat's grievance is satisfied \u2014 a victory against a worthy foe. He fights with
  renewed purpose (+10% attack this turn).",
   "severity": "good"
  },
  {
   "message": "Berthier reports that Bernadotte resents Ney's laurels for the fourth time \u2014 he
  has grown cold and withholding.",
   "severity": "warning"
  },
  {
   "message": "Berthier reports that Ney resents Bernadotte's laurels again, 2 turns after the last
  \u2014 he has grown loud at the staff table about who is given the honours.",
   "severity": "warning"
  },
  {
   "message": "The feud between Bernadotte and Ney is now mutual \u2014 each schemes against the
  other. Separate them, Sire, or accept the friction.",
   "severity": "warning"
  },
  {
   "message": "Berthier reports that Davout resents Murat's laurels again, 1 turns after the last
  \u2014 he has grown cold and withholding.",
   "severity": "warning"
  },
  {
   "message": "Berthier notes that Soult has been holding position for some time while others
  receive commands. He may begin to feel... overlooked.",
   "severity": "info"
  },
  {
   "message": "Ney is eyeing Shrapnel's position at Albania. I cannot guarantee he will wait for
  orders, Sire \u2014 any command would restrain him.",
   "severity": "warning"
  },
  {
   "message": "Berthier notes that Ney's recent victories have made him the most celebrated
  commander in the army. (+1 shock, +1 defense, +1 administration while he holds the laurels)",
   "severity": "good"
  },
  {
   "message": "Murat is no longer the army's most celebrated commander \u2014 the laurels have
  passed.",
   "severity": "warning"
  }
 ],
 "headline": {
  "class": "ally_broken",
  "weight": 60,
  "text": "Sire \u2014 our ally's marshal Deroy was broken at Hungary. Bavaria reels.",
  "sub_beats": [
   "Sire \u2014 Marshal Davout's household goes unpaid. His patience erodes with his purse.",
   "Sire \u2014 the establishment stands 31,184 men under the ordinance, and the depots hold 99,061.
  10,000 foot cost 450 gold at Paris, where a marshal must stand to receive them."
  ]
 },
 "berthier_note": "Our ally bleeds, Sire. If we do not steady them, they may seek terms without
  us.",
 "talleyrand_report": [],
 "talleyrand_discovery": null,
 "talleyrand_override_note": null,
 "talleyrand_redemption": null,
 "coalition_status": {
  "threat_level": 79,
  "tier": "Formed",
  "sources": [
   {
    "source": "hegemony_passive",
    "amount": 1,
    "target": "France"
   },
   {
    "source": "decay",
    "amount": -3
   }
  ],
  "active_coalition": {
   "name": "Third Coalition",
   "leader": "Britain",
   "posture": "cautious",
   "formed_turn": 1,
   "members": [
    {
     "nation": "Austria",
     "war_exhaustion": 163,
     "strength_display": "38,780 men",
     "strength": 38780,
     "gold": 3843
    },
    {
     "nation": "Britain",
     "war_exhaustion": 102,
     "strength_display": "~30,000 men",
     "strength": 0,
     "gold": 0
    },
    {
     "nation": "Russia",
     "war_exhaustion": 102,
     "strength_display": "64,376 men",
     "strength": 64376,
     "gold": 5554
    }
   ]
  }
 },
 "diplomatic_events": [
  {
   "type": "diplomatic_dp_regen",
   "text": "Talleyrand reports: 5 diplomatic points available (base 3, +1 skill, +1 authority).",
   "priority": "LOW"
  },
  {
   "type": "paymaster_subsidy",
   "text": "Britain's gold reaches Russia \u2014 the subsidy stands at 300 this season.",
   "priority": "MEDIUM"
  },
  {
   "type": "agenda_shift",
   "text": "The court of Austria takes up a new design: its own survival.",
   "priority": "MEDIUM"
  }
 ],
 "lapsed_offers": [
  {
   "nation": "PapalStates",
   "proposal_type": "friendly gift"
  }
 ],
 "pending_envoy_count": 7,
 "pending_envoys": [
  {
   "nation": "KingdomOfItaly",
   "proposal_type": "request reward or restoration",
   "state": "ACTIVE"
  },
  {
   "nation": "Britain",
   "proposal_type": "settlement offer",
   "state": "WAITING"
  },
  {
   "nation": "Britain",
   "proposal_type": "armistice losing",
   "state": "WAITING"
  },
  {
   "nation": "Russia",
   "proposal_type": "armistice losing",
   "state": "WAITING"
  },
  {
   "nation": "Austria",
   "proposal_type": "armistice losing",
   "state": "WAITING"
  },
  {
   "nation": "Naples",
   "proposal_type": "open borders",
   "state": "WAITING"
  },
  {
   "nation": "Bavaria",
   "proposal_type": "request reward or restoration",
   "state": "WAITING"
  }
 ]
}
-- POPUP/DIALOGUE [envoy_digest] --
   {
    "turn": 12,
    "count": 1,
    "title": "A COURT WRITES",
    "lapsing_count": 1,
    "headline": "Naples writes.",
    "deadline_note": "Answer them here. Unanswered letters lapse when the turn ends, and a court
     left waiting will not raise the matter again for some seasons.",
    "items": [
     {
      "mailbox_id": 22,
      "dialogue_id": 28,
      "from_nation": "Naples",
      "power_tier": "secondary",
      "proposal_type": "friendly_gift",
      "proposal_type_display": "Open Borders Agreement",
      "diplomat_name": "Medici",
      "diplomat_line": "Medici, smoothly evasive: \"Naples has always counted better than she has
     fought, and the count favors friendship with France. Open the borders.\"",
      "clauses": [
       "Proposal: Open Borders Agreement",
       "Clause: Open borders",
       "Offer: Gold payment - 150"
      ],
      "acceptance_hint": "natural willingness to negotiate",
      "state": "WAITING",
      "arrival_turn": 11
     }
    ]
   }
-- POPUP/DIALOGUE [pending_capture_choice] --
   true
-- POPUP/DIALOGUE [notifications] --
   [
    {
     "id": "823b437f-15a0-4fb9-8251-37ed3e1cd475",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Soult grows bitter (x2)",
     "message": "Marshal Soult's victories remain unrewarded (expects 200g/turn of estates; holds
     160g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente to stop
     the erosion.",
     "turn_created": 12,
     "details": {
      "marshal": "Soult",
      "expectation": 200,
      "satisfaction": 160,
      "shortfall": 40
     },
     "base_title": "Marshal Soult grows bitter",
     "repeat_count": 2
    },
    {
     "id": "ff90a7da-d536-4658-af81-bbd0a31ad89d",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Davout grows bitter (x2)",
     "message": "Marshal Davout's victories remain unrewarded (expects 300g/turn of estates; holds
     240g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente to stop
     the erosion.",
     "turn_created": 11,
     "details": {
      "marshal": "Davout",
      "expectation": 300,
      "satisfaction": 240,
      "shortfall": 60
     },
     "base_title": "Marshal Davout grows bitter",
     "repeat_count": 2
    },
    {
     "id": "ea9c2894-880f-4204-90ba-93891be05813",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Murat grows bitter (x2)",
     "message": "Marshal Murat's victories remain unrewarded (expects 300g/turn of estates; holds
     280g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente to stop
     the erosion.",
     "turn_created": 11,
     "details": {
      "marshal": "Murat",
      "expectation": 300,
      "satisfaction": 280,
      "shortfall": 20
     },
     "base_title": "Marshal Murat grows bitter",
     "repeat_count": 2
    },
    {
     "id": "13e2e89e-a83a-41f0-8e76-f00675c19a5f",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Britain",
     "message": "An envoy from Britain has arrived with a proposal.",
     "turn_created": 11,
     "details": {},
     "base_title": "Envoy from Britain",
     "repeat_count": 1
    },
    {
     "id": "8206bb8e-0171-44d7-86f6-7e5d6ae0e0d9",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Russia",
     "message": "An envoy from Russia has arrived with a proposal.",
     "turn_created": 11,
     "details": {},
     "base_title": "Envoy from Russia",
     "repeat_count": 1
    },
    {
     "id": "48486a32-2d91-4bb3-8650-fdeb03e9305d",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Austria",
     "message": "An envoy from Austria has arrived with a proposal.",
     "turn_created": 11,
     "details": {},
     "base_title": "Envoy from Austria",
     "repeat_count": 1
    },
    {
     "id": "cbe3bc0f-798b-4dc1-9a27-317273269402",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Naples",
     "message": "An envoy from Naples has arrived with a proposal.",
     "turn_created": 11,
     "details": {},
     "base_title": "Envoy from Naples",
     "repeat_count": 1
    },
    {
     "id": "11eb075a-98d7-4a9b-94f1-ee058610f860",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Bernadotte grows bitter (x2)",
     "message": "Marshal Bernadotte's victories remain unrewarded (expects 240g/turn of estates;
     holds 160g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente
     to stop the erosion.",
     "turn_created": 10,
     "details": {
      "marshal": "Bernadotte",
      "expectation": 240,
      "satisfaction": 160,
      "shortfall": 80
     },
     "base_title": "Marshal Bernadotte grows bitter",
     "repeat_count": 2
    },
    {
     "id": "36d9d8db-6539-449d-a72e-e376e20d03dc",
     "type": "counter_punch_earned",
     "priority": 1,
     "title": "Davout \u2014 free attack!",
     "message": "Davout earned a free attack from their defensive victory. Use within 2 turns or the
     opportunity expires.",
     "turn_created": 10,
     "details": {
      "marshal": "Davout"
     },
     "base_title": "Davout \u2014 free attack!",
     "repeat_count": 1
    },
    {
     "id": "552b1a44-5cbe-4a9a-a123-61707f7c98de",
     "type": "strategic_order_complete",
     "priority": 1,
     "title": "Soult arrived",
     "message": "Soult has completed t

====================================================================================================
> end turn
====================================================================================================
You must decide how to handle the captured region first!
Your forces have taken Carniola. Plunder it for 600 gold — buildings burned, the province left
  hostile — or secure it and keep the country quiet? ('plunder' or 'secure')
-- POPUP/DIALOGUE [envoy_digest] --
   {
    "turn": 12,
    "count": 1,
    "title": "A COURT WRITES",
    "lapsing_count": 1,
    "headline": "Naples writes.",
    "deadline_note": "Answer them here. Unanswered letters lapse when the turn ends, and a court
     left waiting will not raise the matter again for some seasons.",
    "items": [
     {
      "mailbox_id": 22,
      "dialogue_id": 28,
      "from_nation": "Naples",
      "power_tier": "secondary",
      "proposal_type": "friendly_gift",
      "proposal_type_display": "Open Borders Agreement",
      "diplomat_name": "Medici",
      "diplomat_line": "Medici, smoothly evasive: \"Naples has always counted better than she has
     fought, and the count favors friendship with France. Open the borders.\"",
      "clauses": [
       "Proposal: Open Borders Agreement",
       "Clause: Open borders",
       "Offer: Gold payment - 150"
      ],
      "acceptance_hint": "natural willingness to negotiate",
      "state": "WAITING",
      "arrival_turn": 11
     }
    ]
   }
-- POPUP/DIALOGUE [pending_capture_choice] --
   true
-- POPUP/DIALOGUE [notifications] --
   [
    {
     "id": "823b437f-15a0-4fb9-8251-37ed3e1cd475",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Soult grows bitter (x2)",
     "message": "Marshal Soult's victories remain unrewarded (expects 200g/turn of estates; holds
     160g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente to stop
     the erosion.",
     "turn_created": 12,
     "details": {
      "marshal": "Soult",
      "expectation": 200,
      "satisfaction": 160,
      "shortfall": 40
     },
     "base_title": "Marshal Soult grows bitter",
     "repeat_count": 2
    },
    {
     "id": "ff90a7da-d536-4658-af81-bbd0a31ad89d",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Davout grows bitter (x2)",
     "message": "Marshal Davout's victories remain unrewarded (expects 300g/turn of estates; holds
     240g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente to stop
     the erosion.",
     "turn_created": 11,
     "details": {
      "marshal": "Davout",
      "expectation": 300,
      "satisfaction": 240,
      "shortfall": 60
     },
     "base_title": "Marshal Davout grows bitter",
     "repeat_count": 2
    },
    {
     "id": "ea9c2894-880f-4204-90ba-93891be05813",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Murat grows bitter (x2)",
     "message": "Marshal Murat's victories remain unrewarded (expects 300g/turn of estates; holds
     280g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente to stop
     the erosion.",
     "turn_created": 11,
     "details": {
      "marshal": "Murat",
      "expectation": 300,
      "satisfaction": 280,
      "shortfall": 20
     },
     "base_title": "Marshal Murat grows bitter",
     "repeat_count": 2
    },
    {
     "id": "13e2e89e-a83a-41f0-8e76-f00675c19a5f",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Britain",
     "message": "An envoy from Britain has arrived with a proposal.",
     "turn_created": 11,
     "details": {},
     "base_title": "Envoy from Britain",
     "repeat_count": 1
    },
    {
     "id": "8206bb8e-0171-44d7-86f6-7e5d6ae0e0d9",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Russia",
     "message": "An envoy from Russia has arrived with a proposal.",
     "turn_created": 11,
     "details": {},
     "base_title": "Envoy from Russia",
     "repeat_count": 1
    },
    {
     "id": "48486a32-2d91-4bb3-8650-fdeb03e9305d",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Austria",
     "message": "An envoy from Austria has arrived with a proposal.",
     "turn_created": 11,
     "details": {},
     "base_title": "Envoy from Austria",
     "repeat_count": 1
    },
    {
     "id": "cbe3bc0f-798b-4dc1-9a27-317273269402",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Naples",
     "message": "An envoy from Naples has arrived with a proposal.",
     "turn_created": 11,
     "details": {},
     "base_title": "Envoy from Naples",
     "repeat_count": 1
    },
    {
     "id": "11eb075a-98d7-4a9b-94f1-ee058610f860",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Bernadotte grows bitter (x2)",
     "message": "Marshal Bernadotte's victories remain unrewarded (expects 240g/turn of estates;
     holds 160g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente
     to stop the erosion.",
     "turn_created": 10,
     "details": {
      "marshal": "Bernadotte",
      "expectation": 240,
      "satisfaction": 160,
      "shortfall": 80
     },
     "base_title": "Marshal Bernadotte grows bitter",
     "repeat_count": 2
    },
    {
     "id": "36d9d8db-6539-449d-a72e-e376e20d03dc",
     "type": "counter_punch_earned",
     "priority": 1,
     "title": "Davout \u2014 free attack!",
     "message": "Davout earned a free attack from their defensive victory. Use within 2 turns or the
     opportunity expires.",
     "turn_created": 10,
     "details": {
      "marshal": "Davout"
     },
     "base_title": "Davout \u2014 free attack!",
     "repeat_count": 1
    },
    {
     "id": "552b1a44-5cbe-4a9a-a123-61707f7c98de",
     "type": "strategic_order_complete",
     "priority": 1,
     "title": "Soult arrived",
     "message": "Soult has completed t

====================================================================================================
> secure
====================================================================================================
Ney secures Carniola. Stability set to 25. Order is maintained. 1 building(s) damaged.
   <event secure> {"region": "Carniola", "capturer": "Ney"}
-- POPUP/DIALOGUE [envoy_digest] --
   {
    "turn": 12,
    "count": 1,
    "title": "A COURT WRITES",
    "lapsing_count": 1,
    "headline": "Naples writes.",
    "deadline_note": "Answer them here. Unanswered letters lapse when the turn ends, and a court
     left waiting will not raise the matter again for some seasons.",
    "items": [
     {
      "mailbox_id": 22,
      "dialogue_id": 28,
      "from_nation": "Naples",
      "power_tier": "secondary",
      "proposal_type": "friendly_gift",
      "proposal_type_display": "Open Borders Agreement",
      "diplomat_name": "Medici",
      "diplomat_line": "Medici, smoothly evasive: \"Naples has always counted better than she has
     fought, and the count favors friendship with France. Open the borders.\"",
      "clauses": [
       "Proposal: Open Borders Agreement",
       "Clause: Open borders",
       "Offer: Gold payment - 150"
      ],
      "acceptance_hint": "natural willingness to negotiate",
      "state": "WAITING",
      "arrival_turn": 11
     }
    ]
   }
-- POPUP/DIALOGUE [capture_choice] --
   "secure"
-- POPUP/DIALOGUE [notifications] --
   [
    {
     "id": "823b437f-15a0-4fb9-8251-37ed3e1cd475",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Soult grows bitter (x2)",
     "message": "Marshal Soult's victories remain unrewarded (expects 200g/turn of estates; holds
     160g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente to stop
     the erosion.",
     "turn_created": 12,
     "details": {
      "marshal": "Soult",
      "expectation": 200,
      "satisfaction": 160,
      "shortfall": 40
     },
     "base_title": "Marshal Soult grows bitter",
     "repeat_count": 2
    },
    {
     "id": "ff90a7da-d536-4658-af81-bbd0a31ad89d",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Davout grows bitter (x2)",
     "message": "Marshal Davout's victories remain unrewarded (expects 300g/turn of estates; holds
     240g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente to stop
     the erosion.",
     "turn_created": 11,
     "details": {
      "marshal": "Davout",
      "expectation": 300,
      "satisfaction": 240,
      "shortfall": 60
     },
     "base_title": "Marshal Davout grows bitter",
     "repeat_count": 2
    },
    {
     "id": "ea9c2894-880f-4204-90ba-93891be05813",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Murat grows bitter (x2)",
     "message": "Marshal Murat's victories remain unrewarded (expects 300g/turn of estates; holds
     280g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente to stop
     the erosion.",
     "turn_created": 11,
     "details": {
      "marshal": "Murat",
      "expectation": 300,
      "satisfaction": 280,
      "shortfall": 20
     },
     "base_title": "Marshal Murat grows bitter",
     "repeat_count": 2
    },
    {
     "id": "13e2e89e-a83a-41f0-8e76-f00675c19a5f",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Britain",
     "message": "An envoy from Britain has arrived with a proposal.",
     "turn_created": 11,
     "details": {},
     "base_title": "Envoy from Britain",
     "repeat_count": 1
    },
    {
     "id": "8206bb8e-0171-44d7-86f6-7e5d6ae0e0d9",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Russia",
     "message": "An envoy from Russia has arrived with a proposal.",
     "turn_created": 11,
     "details": {},
     "base_title": "Envoy from Russia",
     "repeat_count": 1
    },
    {
     "id": "48486a32-2d91-4bb3-8650-fdeb03e9305d",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Austria",
     "message": "An envoy from Austria has arrived with a proposal.",
     "turn_created": 11,
     "details": {},
     "base_title": "Envoy from Austria",
     "repeat_count": 1
    },
    {
     "id": "cbe3bc0f-798b-4dc1-9a27-317273269402",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Naples",
     "message": "An envoy from Naples has arrived with a proposal.",
     "turn_created": 11,
     "details": {},
     "base_title": "Envoy from Naples",
     "repeat_count": 1
    },
    {
     "id": "11eb075a-98d7-4a9b-94f1-ee058610f860",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Bernadotte grows bitter (x2)",
     "message": "Marshal Bernadotte's victories remain unrewarded (expects 240g/turn of estates;
     holds 160g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente
     to stop the erosion.",
     "turn_created": 10,
     "details": {
      "marshal": "Bernadotte",
      "expectation": 240,
      "satisfaction": 160,
      "shortfall": 80
     },
     "base_title": "Marshal Bernadotte grows bitter",
     "repeat_count": 2
    },
    {
     "id": "36d9d8db-6539-449d-a72e-e376e20d03dc",
     "type": "counter_punch_earned",
     "priority": 1,
     "title": "Davout \u2014 free attack!",
     "message": "Davout earned a free attack from their defensive victory. Use within 2 turns or the
     opportunity expires.",
     "turn_created": 10,
     "details": {
      "marshal": "Davout"
     },
     "base_title": "Davout \u2014 free attack!",
     "repeat_count": 1
    },
    {
     "id": "552b1a44-5cbe-4a9a-a123-61707f7c98de",
     "type": "strategic_order_complete",
     "priority": 1,
     "title": "Soult arrived",
     "message": "Soult has completed t

====================================================================================================
> end turn
====================================================================================================
Turn 12 ended. (Warning: 4 action(s) unused) Turn 13 begins!

Income: 3514g | Occupation: -90g | Charges of Empire: -1527g | Rentes: -2010g | Admiralty: -90g |
  Blockade: -250g | Upkeep: 792g | Other: +1094g | Net: -151g | Treasury: 16,432g
   [cost=0  turn_advanced=False]
   <event construction_complete> {"region": "Moravia", "building": "market", "message": "Construction complete: Market in Moravia!"}
   <event supply_attrition> {"marshal": "Davout", "nation": "France", "region": "Albania", "losses": 448, "message": "Supply shortage at Albania: Davout loses 448 troops"}
   <event supply_attrition> {"marshal": "Murat", "nation": "France", "region": "Albania", "losses": 253, "message": "Supply shortage at Albania: Murat loses 253 troops"}
   <event supply_attrition> {"marshal": "Massena", "nation": "France", "region": "Albania", "losses": 309, "message": "Supply shortage at Albania: Massena loses 309 troops"}
   <event british_subsidy> {"recipient": "Austria", "payer": "Britain", "amount": 300, "war_id": "war_1", "subsidy_source_detail": "unique_eligible", "message": "Britain subsidizes Austria with 300 gold."}
   <event sponsorship_expired> {"payer": "Britain", "recipient": "Russia", "aim": "France", "kind": "sponsorship", "turn": 13}
   <event jealousy_resolved> {"message": "Davout's grievance is satisfied \u2014 a victory won shoulder to shoulder. He holds with renewed purpose (+10% defense this turn).", "nation": "France", "marshal": "Davout"}
   <event jealousy_autonomous_attack> {"message": "Ney, hungry for glory, has attacked Shrapnel on his own initiative.", "nation": "France", "marshal": "Ney"}
   <event jealousy_resolved> {"message": "Ney's grievance is satisfied \u2014 he has surpassed Bernadotte in glory. He fights with renewed purpose (+10% attack this turn).", "nation": "France", "marshal": "Ney"}
   <event jealousy_ladder_shift> {"message": "Ney has proven himself beyond Bernadotte. The grievance fades.", "nation": "France", "marshal": "Ney"}
   <event jealousy_fired> {"message": "Berthier reports that Davout resents Murat's laurels for the third time \u2014 he has grown cold and withholding.", "nation": "France", "marshal": "Davout", "target": "Murat"}
   <event jealousy_escalation> {"message": "Sire, the rivalry between Davout and Murat has become a matter of concern among the general staff. Their cooperation cannot be relied upon.", "nation": "France", "marshal": "Davout", "target": "Murat"}
   <event jealousy_fired> {"message": "Berthier reports that Soult appears envious of Bernadotte's laurels \u2014 he has thrown himself into his post with obsessive diligence.", "nation": "France", "marshal": "Soult", "target": "Bernadotte"}
   <event jealousy_restlessness> {"message": "Berthier notes that Murat has grown restless \u2014 he has not seen laurels while Ney wins them. I recommend giving him meaningful orders soon.", "nation": "France", "marshal": "Murat"}
   <event intel_updated> {"region": "Epirus", "new_visibility": "partial", "old_visibility": "unknown", "source": "adjacent"}
   <event intel_updated> {"region": "Milan", "new_visibility": "full", "old_visibility": "partial", "source": "obsessive_patrols"}
   <event intel_decayed> {"region": "Brunswick", "old_visibility": "stale", "new_visibility": "last_known"}
   <event intel_decayed> {"region": "Galicia", "old_visibility": "stale", "new_visibility": "last_known"}

####################################################################################################
# THE ENEMY PHASE
####################################################################################################
-- Russia --
  - Kutuzov attacks Ney
      [battle] Third Battle of Carniola  -> stalemate  victor=None
        ATK Kutuzov          lost   2,228  left  25,403  morale  35
        DEF Ney              lost   1,587  left  11,176  morale  45
        defender order of battle: Ney 12,763(engaged); Soult 21,017(refused)
  - Kutuzov attacks Bohemia
      [conquest] Bohemia  capture_choice=secure
    [action_count] 2
-- Austria --
  - ArchdukeJohn moves to Vienna
      [move] {"type": "move", "marshal": "ArchdukeJohn", "from": "Moravia", "to": "Vienna"}
  - ArchdukeCharles attacks Carniola
      [battle] Fourth Battle of Carniola  -> stalemate  victor=None
        ATK ArchdukeCharles  lost   1,828  left  24,444  morale  10  ROUTED
        DEF Ney              lost   1,799  left   9,377  morale  40
        defender order of battle: Ney 11,176(engaged); Soult 21,017(refused)
  - ArchdukeJohn attacks Bohemia
      [battle] Fourth Battle of Bohemia  -> attacker_tactical_victory  victor=ArchdukeJohn
        ATK ArchdukeJohn     lost     500  left  11,701  morale  26
        DEF Deroy            lost   1,914  left   4,244  morale   0  ROUTED
    [action_count] 3
[summary]
   Kutuzov: attack → Ney
   Kutuzov: attack → Bohemia
   ArchdukeJohn: move → Vienna
   ArchdukeCharles: attack → Carniola
   ArchdukeJohn: attack → Bohemia

####################################################################################################
# THE MORNING DISPATCH
####################################################################################################
{
 "turn": 13,
 "situation": {
  "player_regions": 30,
  "enemy_regions": 96,
  "treasury": 16432,
  "treasury_delta": 15,
  "trade_income": 500,
  "occupation": 90,
  "contributions": 0,
  "state_charges": 1529,
  "requisitions": 0,
  "overseas": 0,
  "dotation_skim": 0,
  "unmet_marshals": [
   {
    "marshal": "Davout",
    "expectation": 300,
    "satisfaction": 240,
    "shortfall": 60,
    "eroding": true,
    "grace_turns_left": 0,
    "pension": 240
   },
   {
    "marshal": "Soult",
    "expectation": 200,
    "satisfaction": 160,
    "shortfall": 40,
    "eroding": true,
    "grace_turns_left": 0,
    "pension": 160
   },
   {
    "marshal": "Murat",
    "expectation": 300,
    "satisfaction": 280,
    "shortfall": 20,
    "eroding": true,
    "grace_turns_left": 0,
    "pension": 280
   },
   {
    "marshal": "Bernadotte",
    "expectation": 240,
    "satisfaction": 160,
    "shortfall": 80,
    "eroding": true,
    "grace_turns_left": 0,
    "pension": 160
   },
   {
    "marshal": "Massena",
    "expectation": 300,
    "satisfaction": 0,
    "shortfall": 300,
    "eroding": true,
    "grace_turns_left": 0,
    "pension": 0
   }
  ],
  "rente_cost": 2010,
  "expectation_rises": [],
  "blockade": 250,
  "admiralty": 90,
  "upkeep_surcharge": 0,
  "force_limit": 135000,
  "over_force_limit": false,
  "bankrupt": false,
  "strength_ratio_pct": 72,
  "authority": 100,
  "authority_label": "Strong"
 },
 "marshals": [
  {
   "name": "Soult",
   "location": "Tyrol",
   "strength": 21017,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 6,
   "danger": "",
   "trust": 63,
   "trust_notable": false,
   "morale": 80,
   "morale_warning": false
  },
  {
   "name": "Davout",
   "location": "Albania",
   "strength": 18910,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 1,
   "danger": "Starving \u2014 supply has failed at Albania two turns running.",
   "trust": 72,
   "trust_notable": false,
   "morale": 55,
   "morale_warning": true
  },
  {
   "name": "Lannes",
   "location": "Rhineland",
   "strength": 16505,
   "status": "idle_restless",
   "status_note": "9 turns idle.",
   "arc_note": "",
   "idle_turns": 9,
   "danger": "",
   "trust": 75,
   "trust_notable": false,
   "morale": 85,
   "morale_warning": false
  },
  {
   "name": "Massena",
   "location": "Albania",
   "strength": 13048,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 1,
   "danger": "Morale failing (0) \u2014 the men waver.",
   "trust": 44,
   "trust_notable": true,
   "morale": 0,
   "morale_warning": true
  },
  {
   "name": "Bernadotte",
   "location": "Munich",
   "strength": 12378,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 6,
   "danger": "",
   "trust": 22,
   "trust_notable": true,
   "morale": 80,
   "morale_warning": false
  },
  {
   "name": "Murat",
   "location": "Albania",
   "strength": 10671,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 1,
   "danger": "Morale failing (38) \u2014 the men waver.",
   "trust": 59,
   "trust_notable": false,
   "morale": 38,
   "morale_warning": true
  },
  {
   "name": "Ney",
   "location": "Carniola",
   "strength": 9377,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 0,
   "danger": "Starving \u2014 supply has failed at Carniola two turns running.",
   "trust": 56,
   "trust_notable": false,
   "morale": 40,
   "morale_warning": true
  }
 ],
 "intelligence": [
  {
   "name": "Archduke John",
   "location": "Bohemia",
   "strength_display": "11,643",
   "visibility": "full",
   "intel_turn": 13
  },
  {
   "name": "Kutuzov",
   "location": "Bohemia",
   "strength_display": "24,875",
   "visibility": "full",
   "intel_turn": 13
  },
  {
   "name": "Archduke Charles",
   "location": "Moravia",
   "strength_display": "27,121",
   "visibility": "full",
   "intel_turn": 11
  },
  {
   "name": "Bennigsen",
   "location": "Moravia",
   "strength_display": "4,850",
   "visibility": "full",
   "intel_turn": 11
  },
  {
   "name": "Castanos",
   "location": "Gascony",
   "strength_display": "small force",
   "visibility": "partial",
   "intel_turn": 13
  },
  {
   "name": "Paget",
   "location": "Leon",
   "strength_display": "screening force",
   "visibility": "stale",
   "intel_turn": 9
  },
  {
   "name": "Mack",
   "location": "Berlin",
   "strength_display": "screening force",
   "visibility": "last_known",
   "intel_turn": 5
  },
  {
   "name": "Brunswick",
   "location": "Berlin",
   "strength_display": "large force",
   "visibility": "last_known",
   "intel_turn": 5
  }
 ],
 "turn_events": [
  {
   "message": "Supply shortage at Albania: Davout loses 448 troops",
   "severity": "warning"
  },
  {
   "message": "Supply shortage at Albania: Murat loses 253 troops",
   "severity": "warning"
  },
  {
   "message": "Supply shortage at Albania: Massena loses 309 troops",
   "severity": "warning"
  },
  {
   "message": "Davout's grievance is satisfied \u2014 a victory won shoulder to shoulder. He holds
  with renewed purpose (+10% defense this turn).",
   "severity": "good"
  },
  {
   "message": "Ney, hungry for glory, has attacked Shrapnel on his own initiative.",
   "severity": "warning"
  },
  {
   "message": "Ney's grievance is satisfied \u2014 he has surpassed Bernadotte in glory. He fights
  with renewed purpose (+10% attack this turn).",
   "severity": "good"
  },
  {
   "message": "Ney has proven himself beyond Bernadotte. The grievance fades.",
   "severity": "good"
  },
  {
   "message": "Berthier reports that Davout resents Murat's laurels for the third time \u2014 he has
  grown cold and withholding.",
   "severity": "warning"
  },
  {
   "message": "Sire, the rivalry between Davout and Murat has become a matter of concern among the
  general staff. Their cooperation cannot be relied upon.",
   "severity": "warning"
  },
  {
   "message": "Berthier reports that Soult appears envious of Bernadotte's laurels \u2014 he has
  thrown himself into his post with obsessive diligence.",
   "severity": "warning"
  },
  {
   "message": "Berthier notes that Murat has grown restless \u2014 he has not seen laurels while Ney
  wins them. I recommend giving him meaningful orders soon.",
   "severity": "info"
  }
 ],
 "headline": {
  "class": "marshal_captured",
  "weight": 95,
  "text": "Sire \u2014 Marshal Shrapnel has been taken. France holds him prisoner.",
  "sub_beats": [
   "Sire \u2014 Marshal Deroy has been taken. Austria holds him prisoner.",
   "Sire \u2014 Bohemia has been taken by Russia."
  ]
 },
 "berthier_note": "We must consider his ransom, Sire \u2014 or make his captors regret the
  keeping.",
 "talleyrand_report": [],
 "talleyrand_discovery": null,
 "talleyrand_override_note": null,
 "talleyrand_redemption": null,
 "coalition_status": {
  "threat_level": 80,
  "tier": "Formed",
  "sources": [
   {
    "source": "hegemony_passive",
    "amount": 1,
    "target": "France"
   },
   {
    "source": "decay",
    "amount": -3
   }
  ],
  "active_coalition": {
   "name": "Third Coalition",
   "leader": "Britain",
   "posture": "defensive",
   "formed_turn": 1,
   "members": [
    {
     "nation": "Austria",
     "war_exhaustion": 171,
     "strength_display": "46,087 men",
     "strength": 46087,
     "gold": 4577
    },
    {
     "nation": "Britain",
     "war_exhaustion": 0,
     "strength_display": "Unknown",
     "strength": 0,
     "gold": 0
    },
    {
     "nation": "Russia",
     "war_exhaustion": 110,
     "strength_display": "61,620 men",
     "strength": 61620,
     "gold": 5237
    }
   ]
  }
 },
 "diplomatic_events": [
  {
   "type": "diplomatic_dp_regen",
   "text": "Talleyrand reports: 5 diplomatic points available (base 3, +1 skill, +1 authority).",
   "priority": "LOW"
  },
  {
   "type": "paymaster_subsidy",
   "text": "Britain's gold reaches Austria \u2014 the subsidy stands at 300 this season.",
   "priority": "MEDIUM"
  },
  {
   "type": "agenda_shift",
   "text": "The court of Austria takes up a new design: Revanche.",
   "priority": "MEDIUM"
  }
 ],
 "lapsed_offers": [
  {
   "nation": "Britain",
   "proposal_type": "armistice"
  },
  {
   "nation": "Russia",
   "proposal_type": "armistice"
  },
  {
   "nation": "Austria",
   "proposal_type": "armistice losing"
  },
  {
   "nation": "Naples",
   "proposal_type": "friendly gift"
  }
 ],
 "pending_envoy_count": 3,
 "pending_envoys": [
  {
   "nation": "Britain",
   "proposal_type": "settlement offer",
   "state": "WAITING"
  },
  {
   "nation": "Hesse",
   "proposal_type": "non aggression",
   "state": "WAITING"
  },
  {
   "nation": "Bavaria",
   "proposal_type": "request reward or restoration",
   "state": "WAITING"
  }
 ]
}
-- POPUP/DIALOGUE [notifications] --
   [
    {
     "id": "823b437f-15a0-4fb9-8251-37ed3e1cd475",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Soult grows bitter (x2)",
     "message": "Marshal Soult's victories remain unrewarded (expects 200g/turn of estates; holds
     160g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente to stop
     the erosion.",
     "turn_created": 12,
     "details": {
      "marshal": "Soult",
      "expectation": 200,
      "satisfaction": 160,
      "shortfall": 40
     },
     "base_title": "Marshal Soult grows bitter",
     "repeat_count": 2
    },
    {
     "id": "9a25aed2-7866-4a27-810a-4638070fed7c",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Hesse",
     "message": "An envoy from Hesse has arrived with a proposal.",
     "turn_created": 12,
     "details": {},
     "base_title": "Envoy from Hesse",
     "repeat_count": 1
    },
    {
     "id": "ff90a7da-d536-4658-af81-bbd0a31ad89d",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Davout grows bitter (x2)",
     "message": "Marshal Davout's victories remain unrewarded (expects 300g/turn of estates; holds
     240g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente to stop
     the erosion.",
     "turn_created": 11,
     "details": {
      "marshal": "Davout",
      "expectation": 300,
      "satisfaction": 240,
      "shortfall": 60
     },
     "base_title": "Marshal Davout grows bitter",
     "repeat_count": 2
    },
    {
     "id": "ea9c2894-880f-4204-90ba-93891be05813",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Murat grows bitter (x2)",
     "message": "Marshal Murat's victories remain unrewarded (expects 300g/turn of estates; holds
     280g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente to stop
     the erosion.",
     "turn_created": 11,
     "details": {
      "marshal": "Murat",
      "expectation": 300,
      "satisfaction": 280,
      "shortfall": 20
     },
     "base_title": "Marshal Murat grows bitter",
     "repeat_count": 2
    },
    {
     "id": "11eb075a-98d7-4a9b-94f1-ee058610f860",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Bernadotte grows bitter (x2)",
     "message": "Marshal Bernadotte's victories remain unrewarded (expects 240g/turn of estates;
     holds 160g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente
     to stop the erosion.",
     "turn_created": 10,
     "details": {
      "marshal": "Bernadotte",
      "expectation": 240,
      "satisfaction": 160,
      "shortfall": 80
     },
     "base_title": "Marshal Bernadotte grows bitter",
     "repeat_count": 2
    },
    {
     "id": "36d9d8db-6539-449d-a72e-e376e20d03dc",
     "type": "counter_punch_earned",
     "priority": 1,
     "title": "Davout \u2014 free attack!",
     "message": "Davout earned a free attack from their defensive victory. Use within 2 turns or the
     opportunity expires.",
     "turn_created": 10,
     "details": {
      "marshal": "Davout"
     },
     "base_title": "Davout \u2014 free attack!",
     "repeat_count": 1
    },
    {
     "id": "552b1a44-5cbe-4a9a-a123-61707f7c98de",
     "type": "strategic_order_complete",
     "priority": 1,
     "title": "Soult arrived",
     "message": "Soult has completed their SUPPORT order \u2014 arrived at Tyrol.",
     "turn_created": 9,
     "details": {
      "marshal": "Soult",
      "order_type": "SUPPORT",
      "target": "Ney"
     },
     "base_title": "Soult arrived",
     "repeat_count": 1
    },
    {
     "id": "6e5cb538-9460-469d-8e1a-fd9ba4fe4d95",
     "type": "incoming_settlement_offer",
     "priority": 1,
     "title": "Settlement offer from Britain (x2)",
     "message": "Britain has offered terms to settle France vs Britain. Asking 629 gold.",
     "turn_created": 8,
     "details": {
      "war_id": "war_1",
      "offer_id": "settlement_offer:war_1:8:1",
      "proposer_nation": "Britain",
      "amount": 629,
      "review_target": "incoming_settlement_offer_popup"
     },
     "base_title": "Settlement offer from Britain",
     "repeat_count": 2
    },
    {
     "id": "73f91faa-7c19-4dee-befa-77e8ca2425e8",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Massena grows bitter",
     "message": "Marshal

====================================================================================================
> Murat, attack Vienna
====================================================================================================
I don't understand that choice, Sire. Options: 1=Conquest, 2=Forced Alliance, 3=Subjugation, 4=Back
  Out
-- POPUP/DIALOGUE [envoy_digest] --
   {
    "turn": 13,
    "count": 1,
    "title": "A SMALL COURT WRITES",
    "lapsing_count": 1,
    "headline": "Hesse writes.",
    "deadline_note": "Answer them here. Unanswered letters lapse when the turn ends, and a court
     left waiting will not raise the matter again for some seasons.",
    "items": [
     {
      "mailbox_id": 23,
      "dialogue_id": 30,
      "from_nation": "Hesse",
      "power_tier": "minor",
      "proposal_type": "non_aggression",
      "proposal_type_display": "Non-Aggression Pact",
      "diplomat_name": "Chancery of Hesse",
      "diplomat_line": "Hesse, wishing to go unnoticed: \"Hesse counts what a quarrel with France
     would cost and what an understanding would return, and finds the ledger unanimous. Sign the
     pact of non-aggression.\"",
      "clauses": [
       "Proposal: Non-Aggression Pact"
      ],
      "acceptance_hint": "natural willingness to negotiate",
      "state": "WAITING",
      "arrival_turn": 12
     }
    ]
   }
-- POPUP/DIALOGUE [marshal_petition] --
   {
    "kind": "jealousy_confrontation",
    "title": "Marshal Davout seeks an audience",
    "body": "Sire, Davout has expressed reservations about the recognition afforded to Murat. He
     requests that his contributions be... noted.",
    "speaker": "Davout",
    "options": [
     {
      "id": "acknowledge",
      "label": "Acknowledge",
      "detail": "Free, and it fixes nothing: the grievance stands 2 more turns \u2014 souring his
     ties and coordination with Murat \u2014 then cools on its own.",
      "cost_note": "",
      "enabled": true
     },
     {
      "id": "promise",
      "label": "Promise Glory",
      "detail": "His patience is bought \u2014 the grievance shortens by 2 turns.",
      "cost_note": "1 AP",
      "ap_cost": 1,
      "enabled": true
     },
     {
      "id": "rebuke",
      "label": "Rebuke",
      "detail": "Trust -5. The grievance shortens by 1 turn.",
      "cost_note": "",
      "enabled": true
     }
    ],
    "context": {
     "marshal": "Davout",
     "target": "Murat",
     "escalation_level": 0
    },
    "turn": 11
   }
-- POPUP/DIALOGUE [notifications] --
   [
    {
     "id": "823b437f-15a0-4fb9-8251-37ed3e1cd475",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Soult grows bitter (x2)",
     "message": "Marshal Soult's victories remain unrewarded (expects 200g/turn of estates; holds
     160g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente to stop
     the erosion.",
     "turn_created": 12,
     "details": {
      "marshal": "Soult",
      "expectation": 200,
      "satisfaction": 160,
      "shortfall": 40
     },
     "base_title": "Marshal Soult grows bitter",
     "repeat_count": 2
    },
    {
     "id": "9a25aed2-7866-4a27-810a-4638070fed7c",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Hesse",
     "message": "An envoy from Hesse has arrived with a proposal.",
     "turn_created": 12,
     "details": {},
     "base_title": "Envoy from Hesse",
     "repeat_count": 1
    },
    {
     "id": "ff90a7da-d536-4658-af81-bbd0a31ad89d",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Davout grows bitter (x2)",
     "message": "Marshal Davout's victories remain unrewarded (expects 300g/turn of estates; holds
     240g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente to stop
     the erosion.",
     "turn_created": 11,
     "details": {
      "marshal": "Davout",
      "expectation": 300,
      "satisfaction": 240,
      "shortfall": 60
     },
     "base_title": "Marshal Davout grows bitter",
     "repeat_count": 2
    },
    {
     "id": "ea9c2894-880f-4204-90ba-93891be05813",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Murat grows bitter (x2)",
     "message": "Marshal Murat's victories remain unrewarded (expects 300g/turn of estates; holds
     280g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente to stop
     the erosion.",
     "turn_created": 11,
     "details": {
      "marshal": "Murat",
      "expectation": 300,
      "satisfaction": 280,
      "shortfall": 20
     },
     "base_title": "Marshal Murat grows bitter",
     "repeat_count": 2
    },
    {
     "id": "11eb075a-98d7-4a9b-94f1-ee058610f860",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Bernadotte grows bitter (x2)",
     "message": "Marshal Bernadotte's victories remain unrewarded (expects 240g/turn of estates;
     holds 160g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente
     to stop the erosion.",
     "turn_created": 10,
     "details": {
      "marshal": "Bernadotte",
      "expectation": 240,
      "satisfaction": 160,
      "shortfall": 80
     },
     "base_title": "Marshal Bernadotte grows bitter",
     "repeat_count": 2
    },
    {
     "id": "36d9d8db-6539-449d-a72e-e376e20d03dc",
     "type": "counter_punch_earned",
     "priority": 1,
     "title": "Davout \u2014 free attack!",
     "message": "Davout earned a free attack from their defensive victory. Use within 2 turns or the
     opportunity expires.",
     "turn_created": 10,
     "details": {
      "marshal": "Davout"
     },
     "base_title": "Davout \u2014 free attack!",
     "repeat_count": 1
    },
    {
     "id": "552b1a44-5cbe-4a9a-a123-61707f7c98de",
     "type": "strategic_order_complete",
     "priority": 1,
     "title": "Soult arrived",
     "message": "Soult has completed their SUPPORT order \u2014 arrived at Tyrol.",
     "turn_created": 9,
     "details": {
      "marshal": "Soult",
      "order_type": "SUPPORT",
      "target": "Ney"
     },
     "base_title": "Soult arrived",
     "repeat_count": 1
    },
    {
     "id": "6e5cb538-9460-469d-8e1a-fd9ba4fe4d95",
     "type": "incoming_settlement_offer",
     "priority": 1,
     "title": "Settlement offer from Britain (x2)",
     "message": "Britain has offered terms to settle France vs Britain. Asking 629 gold.",
     "turn_created": 8,
     "details": {
      "war_id": "war_1",
      "offer_id": "settlement_offer:war_1:8:1",
      "proposer_nation": "Britain",
      "amount": 629,
      "review_target": "incoming_settlement_offer_popup"
     },
     "base_title": "Settlement offer from Britain",
     "repeat_count": 2
    },
    {
     "id": "73f91faa-7c19-4dee-befa-77e8ca2425e8",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Massena grows bitter",
     "message": "Marshal

====================================================================================================
> 4
====================================================================================================
Of course, Sire. Take your time.
-- POPUP/DIALOGUE [envoy_digest] --
   {
    "turn": 13,
    "count": 1,
    "title": "A SMALL COURT WRITES",
    "lapsing_count": 1,
    "headline": "Hesse writes.",
    "deadline_note": "Answer them here. Unanswered letters lapse when the turn ends, and a court
     left waiting will not raise the matter again for some seasons.",
    "items": [
     {
      "mailbox_id": 23,
      "dialogue_id": 30,
      "from_nation": "Hesse",
      "power_tier": "minor",
      "proposal_type": "non_aggression",
      "proposal_type_display": "Non-Aggression Pact",
      "diplomat_name": "Chancery of Hesse",
      "diplomat_line": "Hesse, wishing to go unnoticed: \"Hesse counts what a quarrel with France
     would cost and what an understanding would return, and finds the ledger unanimous. Sign the
     pact of non-aggression.\"",
      "clauses": [
       "Proposal: Non-Aggression Pact"
      ],
      "acceptance_hint": "natural willingness to negotiate",
      "state": "WAITING",
      "arrival_turn": 12
     }
    ]
   }
-- POPUP/DIALOGUE [notifications] --
   [
    {
     "id": "823b437f-15a0-4fb9-8251-37ed3e1cd475",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Soult grows bitter (x2)",
     "message": "Marshal Soult's victories remain unrewarded (expects 200g/turn of estates; holds
     160g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente to stop
     the erosion.",
     "turn_created": 12,
     "details": {
      "marshal": "Soult",
      "expectation": 200,
      "satisfaction": 160,
      "shortfall": 40
     },
     "base_title": "Marshal Soult grows bitter",
     "repeat_count": 2
    },
    {
     "id": "9a25aed2-7866-4a27-810a-4638070fed7c",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Hesse",
     "message": "An envoy from Hesse has arrived with a proposal.",
     "turn_created": 12,
     "details": {},
     "base_title": "Envoy from Hesse",
     "repeat_count": 1
    },
    {
     "id": "ff90a7da-d536-4658-af81-bbd0a31ad89d",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Davout grows bitter (x2)",
     "message": "Marshal Davout's victories remain unrewarded (expects 300g/turn of estates; holds
     240g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente to stop
     the erosion.",
     "turn_created": 11,
     "details": {
      "marshal": "Davout",
      "expectation": 300,
      "satisfaction": 240,
      "shortfall": 60
     },
     "base_title": "Marshal Davout grows bitter",
     "repeat_count": 2
    },
    {
     "id": "ea9c2894-880f-4204-90ba-93891be05813",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Murat grows bitter (x2)",
     "message": "Marshal Murat's victories remain unrewarded (expects 300g/turn of estates; holds
     280g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente to stop
     the erosion.",
     "turn_created": 11,
     "details": {
      "marshal": "Murat",
      "expectation": 300,
      "satisfaction": 280,
      "shortfall": 20
     },
     "base_title": "Marshal Murat grows bitter",
     "repeat_count": 2
    },
    {
     "id": "11eb075a-98d7-4a9b-94f1-ee058610f860",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Bernadotte grows bitter (x2)",
     "message": "Marshal Bernadotte's victories remain unrewarded (expects 240g/turn of estates;
     holds 160g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente
     to stop the erosion.",
     "turn_created": 10,
     "details": {
      "marshal": "Bernadotte",
      "expectation": 240,
      "satisfaction": 160,
      "shortfall": 80
     },
     "base_title": "Marshal Bernadotte grows bitter",
     "repeat_count": 2
    },
    {
     "id": "36d9d8db-6539-449d-a72e-e376e20d03dc",
     "type": "counter_punch_earned",
     "priority": 1,
     "title": "Davout \u2014 free attack!",
     "message": "Davout earned a free attack from their defensive victory. Use within 2 turns or the
     opportunity expires.",
     "turn_created": 10,
     "details": {
      "marshal": "Davout"
     },
     "base_title": "Davout \u2014 free attack!",
     "repeat_count": 1
    },
    {
     "id": "552b1a44-5cbe-4a9a-a123-61707f7c98de",
     "type": "strategic_order_complete",
     "priority": 1,
     "title": "Soult arrived",
     "message": "Soult has completed their SUPPORT order \u2014 arrived at Tyrol.",
     "turn_created": 9,
     "details": {
      "marshal": "Soult",
      "order_type": "SUPPORT",
      "target": "Ney"
     },
     "base_title": "Soult arrived",
     "repeat_count": 1
    },
    {
     "id": "6e5cb538-9460-469d-8e1a-fd9ba4fe4d95",
     "type": "incoming_settlement_offer",
     "priority": 1,
     "title": "Settlement offer from Britain (x2)",
     "message": "Britain has offered terms to settle France vs Britain. Asking 629 gold.",
     "turn_created": 8,
     "details": {
      "war_id": "war_1",
      "offer_id": "settlement_offer:war_1:8:1",
      "proposer_nation": "Britain",
      "amount": 629,
      "review_target": "incoming_settlement_offer_popup"
     },
     "base_title": "Settlement offer from Britain",
     "repeat_count": 2
    },
    {
     "id": "73f91faa-7c19-4dee-befa-77e8ca2425e8",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Massena grows bitter",
     "message": "Marshal

====================================================================================================
> Murat, attack Vienna
====================================================================================================
Murat cannot reach Vienna from Albania! Range: 2, Distance: 3
   [cost=0  turn_advanced=False]
-- POPUP/DIALOGUE [envoy_digest] --
   {
    "turn": 13,
    "count": 1,
    "title": "A SMALL COURT WRITES",
    "lapsing_count": 1,
    "headline": "Hesse writes.",
    "deadline_note": "Answer them here. Unanswered letters lapse when the turn ends, and a court
     left waiting will not raise the matter again for some seasons.",
    "items": [
     {
      "mailbox_id": 23,
      "dialogue_id": 30,
      "from_nation": "Hesse",
      "power_tier": "minor",
      "proposal_type": "non_aggression",
      "proposal_type_display": "Non-Aggression Pact",
      "diplomat_name": "Chancery of Hesse",
      "diplomat_line": "Hesse, wishing to go unnoticed: \"Hesse counts what a quarrel with France
     would cost and what an understanding would return, and finds the ledger unanimous. Sign the
     pact of non-aggression.\"",
      "clauses": [
       "Proposal: Non-Aggression Pact"
      ],
      "acceptance_hint": "natural willingness to negotiate",
      "state": "WAITING",
      "arrival_turn": 12
     }
    ]
   }
-- POPUP/DIALOGUE [notifications] --
   [
    {
     "id": "823b437f-15a0-4fb9-8251-37ed3e1cd475",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Soult grows bitter (x2)",
     "message": "Marshal Soult's victories remain unrewarded (expects 200g/turn of estates; holds
     160g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente to stop
     the erosion.",
     "turn_created": 12,
     "details": {
      "marshal": "Soult",
      "expectation": 200,
      "satisfaction": 160,
      "shortfall": 40
     },
     "base_title": "Marshal Soult grows bitter",
     "repeat_count": 2
    },
    {
     "id": "9a25aed2-7866-4a27-810a-4638070fed7c",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Hesse",
     "message": "An envoy from Hesse has arrived with a proposal.",
     "turn_created": 12,
     "details": {},
     "base_title": "Envoy from Hesse",
     "repeat_count": 1
    },
    {
     "id": "ff90a7da-d536-4658-af81-bbd0a31ad89d",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Davout grows bitter (x2)",
     "message": "Marshal Davout's victories remain unrewarded (expects 300g/turn of estates; holds
     240g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente to stop
     the erosion.",
     "turn_created": 11,
     "details": {
      "marshal": "Davout",
      "expectation": 300,
      "satisfaction": 240,
      "shortfall": 60
     },
     "base_title": "Marshal Davout grows bitter",
     "repeat_count": 2
    },
    {
     "id": "ea9c2894-880f-4204-90ba-93891be05813",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Murat grows bitter (x2)",
     "message": "Marshal Murat's victories remain unrewarded (expects 300g/turn of estates; holds
     280g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente to stop
     the erosion.",
     "turn_created": 11,
     "details": {
      "marshal": "Murat",
      "expectation": 300,
      "satisfaction": 280,
      "shortfall": 20
     },
     "base_title": "Marshal Murat grows bitter",
     "repeat_count": 2
    },
    {
     "id": "11eb075a-98d7-4a9b-94f1-ee058610f860",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Bernadotte grows bitter (x2)",
     "message": "Marshal Bernadotte's victories remain unrewarded (expects 240g/turn of estates;
     holds 160g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente
     to stop the erosion.",
     "turn_created": 10,
     "details": {
      "marshal": "Bernadotte",
      "expectation": 240,
      "satisfaction": 160,
      "shortfall": 80
     },
     "base_title": "Marshal Bernadotte grows bitter",
     "repeat_count": 2
    },
    {
     "id": "36d9d8db-6539-449d-a72e-e376e20d03dc",
     "type": "counter_punch_earned",
     "priority": 1,
     "title": "Davout \u2014 free attack!",
     "message": "Davout earned a free attack from their defensive victory. Use within 2 turns or the
     opportunity expires.",
     "turn_created": 10,
     "details": {
      "marshal": "Davout"
     },
     "base_title": "Davout \u2014 free attack!",
     "repeat_count": 1
    },
    {
     "id": "552b1a44-5cbe-4a9a-a123-61707f7c98de",
     "type": "strategic_order_complete",
     "priority": 1,
     "title": "Soult arrived",
     "message": "Soult has completed their SUPPORT order \u2014 arrived at Tyrol.",
     "turn_created": 9,
     "details": {
      "marshal": "Soult",
      "order_type": "SUPPORT",
      "target": "Ney"
     },
     "base_title": "Soult arrived",
     "repeat_count": 1
    },
    {
     "id": "6e5cb538-9460-469d-8e1a-fd9ba4fe4d95",
     "type": "incoming_settlement_offer",
     "priority": 1,
     "title": "Settlement offer from Britain (x2)",
     "message": "Britain has offered terms to settle France vs Britain. Asking 629 gold.",
     "turn_created": 8,
     "details": {
      "war_id": "war_1",
      "offer_id": "settlement_offer:war_1:8:1",
      "proposer_nation": "Britain",
      "amount": 629,
      "review_target": "incoming_settlement_offer_popup"
     },
     "base_title": "Settlement offer from Britain",
     "repeat_count": 2
    },
    {
     "id": "73f91faa-7c19-4dee-befa-77e8ca2425e8",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Massena grows bitter",
     "message": "Marshal

====================================================================================================
> status
====================================================================================================
=== BERTHIER'S INTELLIGENCE REPORT ===

YOUR FORCES:
  Ney (Carniola): 9,377 troops, morale 40, neutral stance
  Davout (Albania): 18,910 troops, morale 55, defensive stance
  Soult (Tyrol): 21,017 troops, morale 80, neutral stance
  Lannes (Rhineland): 16,505 troops, morale 85, neutral stance
  Murat (Albania): 10,671 troops, morale 38, neutral stance
  Bernadotte (Munich): 12,378 troops, morale 80, neutral stance
  Massena (Albania): 13,048 troops, morale 0, neutral stance

CONFIRMED INTELLIGENCE:
  Archduke John (Austria): 11,643 troops at Bohemia, defensive stance, morale 31
  Kutuzov (Russia): 24,875 troops at Bohemia, defensive stance, morale 45 — famed for 'The Old Fox'

RECENT REPORTS:
  Paget: screening force near Leon [4 turns ago]
  Castanos: small force near Gascony

LAST KNOWN:
  Mack, Brunswick: last seen near Berlin, 8 turns ago
  Castanos, Paget: last seen near Aragon, 6 turns ago
  Paget: last seen near Galicia, 5 turns ago

NO INTELLIGENCE: No word from 73 provinces beyond the frontiers of Silesia, Podolia, Posen, Rome,
  Beira, Ukraine, Lisbon, Asturias.

   [cost=0  turn_advanced=False]
-- POPUP/DIALOGUE [envoy_digest] --
   {
    "turn": 13,
    "count": 1,
    "title": "A SMALL COURT WRITES",
    "lapsing_count": 1,
    "headline": "Hesse writes.",
    "deadline_note": "Answer them here. Unanswered letters lapse when the turn ends, and a court
     left waiting will not raise the matter again for some seasons.",
    "items": [
     {
      "mailbox_id": 23,
      "dialogue_id": 30,
      "from_nation": "Hesse",
      "power_tier": "minor",
      "proposal_type": "non_aggression",
      "proposal_type_display": "Non-Aggression Pact",
      "diplomat_name": "Chancery of Hesse",
      "diplomat_line": "Hesse, wishing to go unnoticed: \"Hesse counts what a quarrel with France
     would cost and what an understanding would return, and finds the ledger unanimous. Sign the
     pact of non-aggression.\"",
      "clauses": [
       "Proposal: Non-Aggression Pact"
      ],
      "acceptance_hint": "natural willingness to negotiate",
      "state": "WAITING",
      "arrival_turn": 12
     }
    ]
   }
-- POPUP/DIALOGUE [notifications] --
   [
    {
     "id": "823b437f-15a0-4fb9-8251-37ed3e1cd475",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Soult grows bitter (x2)",
     "message": "Marshal Soult's victories remain unrewarded (expects 200g/turn of estates; holds
     160g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente to stop
     the erosion.",
     "turn_created": 12,
     "details": {
      "marshal": "Soult",
      "expectation": 200,
      "satisfaction": 160,
      "shortfall": 40
     },
     "base_title": "Marshal Soult grows bitter",
     "repeat_count": 2
    },
    {
     "id": "9a25aed2-7866-4a27-810a-4638070fed7c",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Hesse",
     "message": "An envoy from Hesse has arrived with a proposal.",
     "turn_created": 12,
     "details": {},
     "base_title": "Envoy from Hesse",
     "repeat_count": 1
    },
    {
     "id": "ff90a7da-d536-4658-af81-bbd0a31ad89d",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Davout grows bitter (x2)",
     "message": "Marshal Davout's victories remain unrewarded (expects 300g/turn of estates; holds
     240g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente to stop
     the erosion.",
     "turn_created": 11,
     "details": {
      "marshal": "Davout",
      "expectation": 300,
      "satisfaction": 240,
      "shortfall": 60
     },
     "base_title": "Marshal Davout grows bitter",
     "repeat_count": 2
    },
    {
     "id": "ea9c2894-880f-4204-90ba-93891be05813",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Murat grows bitter (x2)",
     "message": "Marshal Murat's victories remain unrewarded (expects 300g/turn of estates; holds
     280g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente to stop
     the erosion.",
     "turn_created": 11,
     "details": {
      "marshal": "Murat",
      "expectation": 300,
      "satisfaction": 280,
      "shortfall": 20
     },
     "base_title": "Marshal Murat grows bitter",
     "repeat_count": 2
    },
    {
     "id": "11eb075a-98d7-4a9b-94f1-ee058610f860",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Bernadotte grows bitter (x2)",
     "message": "Marshal Bernadotte's victories remain unrewarded (expects 240g/turn of estates;
     holds 160g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente
     to stop the erosion.",
     "turn_created": 10,
     "details": {
      "marshal": "Bernadotte",
      "expectation": 240,
      "satisfaction": 160,
      "shortfall": 80
     },
     "base_title": "Marshal Bernadotte grows bitter",
     "repeat_count": 2
    },
    {
     "id": "36d9d8db-6539-449d-a72e-e376e20d03dc",
     "type": "counter_punch_earned",
     "priority": 1,
     "title": "Davout \u2014 free attack!",
     "message": "Davout earned a free attack from their defensive victory. Use within 2 turns or the
     opportunity expires.",
     "turn_created": 10,
     "details": {
      "marshal": "Davout"
     },
     "base_title": "Davout \u2014 free attack!",
     "repeat_count": 1
    },
    {
     "id": "552b1a44-5cbe-4a9a-a123-61707f7c98de",
     "type": "strategic_order_complete",
     "priority": 1,
     "title": "Soult arrived",
     "message": "Soult has completed their SUPPORT order \u2014 arrived at Tyrol.",
     "turn_created": 9,
     "details": {
      "marshal": "Soult",
      "order_type": "SUPPORT",
      "target": "Ney"
     },
     "base_title": "Soult arrived",
     "repeat_count": 1
    },
    {
     "id": "6e5cb538-9460-469d-8e1a-fd9ba4fe4d95",
     "type": "incoming_settlement_offer",
     "priority": 1,
     "title": "Settlement offer from Britain (x2)",
     "message": "Britain has offered terms to settle France vs Britain. Asking 629 gold.",
     "turn_created": 8,
     "details": {
      "war_id": "war_1",
      "offer_id": "settlement_offer:war_1:8:1",
      "proposer_nation": "Britain",
      "amount": 629,
      "review_target": "incoming_settlement_offer_popup"
     },
     "base_title": "Settlement offer from Britain",
     "repeat_count": 2
    },
    {
     "id": "73f91faa-7c19-4dee-befa-77e8ca2425e8",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Massena grows bitter",
     "message": "Marshal

====================================================================================================
> end turn
====================================================================================================
Turn 13 ended. (Warning: 4 action(s) unused) Turn 14 begins!

Income: 3517g | Occupation: -90g | Charges of Empire: -1573g | Rentes: -2010g | Admiralty: -90g |
  Blockade: -250g | Upkeep: 784g | Other: +1236g | Net: -44g | Treasury: 16,388g
   [cost=0  turn_advanced=False]
   <event construction_complete> {"region": "Milan", "building": "supply_depot", "message": "Construction complete: Supply Depot in Milan!"}
   <event supply_attrition> {"marshal": "Ney", "nation": "France", "region": "Carniola", "losses": 278, "message": "Supply shortage at Carniola: Ney loses 278 troops"}
   <event supply_attrition> {"marshal": "Davout", "nation": "France", "region": "Carniola", "losses": 561, "message": "Supply shortage at Carniola: Davout loses 561 troops"}
   <event supply_attrition> {"marshal": "Murat", "nation": "France", "region": "Carniola", "losses": 316, "message": "Supply shortage at Carniola: Murat loses 316 troops"}
   <event supply_attrition> {"marshal": "Massena", "nation": "France", "region": "Carniola", "losses": 387, "message": "Supply shortage at Carniola: Massena loses 387 troops"}
   <event vassal_loyalty> {"vassal": "Holland", "lord": "France", "nation": "France", "old_loyalty": 100, "new_loyalty": 100, "delta": 2, "reason": "a common enemy, the lord's victories", "recovery_hint": "", "message": "Holland loyalty 100 (+2): a common enemy, the lord's victories"}
   <event vassal_loyalty> {"vassal": "KingdomOfItaly", "lord": "France", "nation": "France", "old_loyalty": 100, "new_loyalty": 100, "delta": 2, "reason": "a common enemy, the lord's victories", "recovery_hint": "", "message": "KingdomOfItaly loyalty 100 (+2): a common enemy, the lord's victories"}
   <event british_subsidy> {"recipient": "Russia", "payer": "Britain", "amount": 300, "war_id": "war_1", "subsidy_source_detail": "unique_eligible", "message": "Britain subsidizes Russia with 300 gold."}
   <event sponsorship_granted> {"kind": "sponsorship", "payer": "Britain", "recipient": "Russia", "aim": "France", "amount": 300, "turns": 10, "licence": false, "turn": 14}
   <event sponsorship_expired> {"payer": "Britain", "recipient": "Sweden", "aim": "France", "kind": "sponsorship", "turn": 14}
   <event jealousy_resolved> {"message": "Davout's grievance is satisfied \u2014 a victory won shoulder to shoulder. He holds with renewed purpose (+10% defense this turn).", "nation": "France", "marshal": "Davout"}
   <event jealousy_fired> {"message": "Berthier reports that Murat resents Ney's laurels again, 12 turns after the last \u2014 he has grown restless for glory.", "nation": "France", "marshal": "Murat", "target": "Ney"}
   <event jealousy_fired> {"message": "Berthier reports that Davout appears envious of Ney's laurels \u2014 he has grown careful about what he commits to paper.", "nation": "France", "marshal": "Davout", "target": "Ney"}
   <event intel_updated> {"region": "Milan", "new_visibility": "full", "old_visibility": "partial", "source": "obsessive_patrols"}
   <event intel_decayed> {"region": "Dresden", "old_visibility": "partial", "new_visibility": "stale"}
   <event intel_decayed> {"region": "Vienna", "old_visibility": "partial", "new_visibility": "stale"}
   <event intel_decayed> {"region": "Moravia", "old_visibility": "full", "new_visibility": "stale"}
   <event intel_decayed> {"region": "Leon", "old_visibility": "stale", "new_visibility": "last_known"}

####################################################################################################
# THE ENEMY PHASE
####################################################################################################
-- Russia --
  - Kutuzov attacks Ney
      [battle] Fifth Battle of Carniola  -> defender_tactical_victory  victor=Ney
        ATK Kutuzov          lost   5,601  left  19,274  morale   0  ROUTED
        DEF Ney              lost     349  left   9,315  morale  35
        defender order of battle: Ney 9,377(engaged); Davout 18,910(reinforced); Massena 13,048(reinforced); Murat 10,671(reinforced); Soult 21,017(refused)
    [action_count] 1
-- Austria --
  - ArchdukeJohn attacks Ney
      [battle] Sixth Battle of Carniola  -> defender_tactical_victory  victor=Ney
        ATK ArchdukeJohn     lost   5,588  left   6,055  morale   0  ROUTED
        DEF Ney              lost     185  left   9,282  morale  30
        defender order of battle: Ney 9,315(engaged); Davout 18,781(engaged); Massena 12,961(engaged); Murat 10,600(engaged); Soult 21,017(refused)
    [action_count] 1
[summary]
   Kutuzov: attack → Ney
   ArchdukeJohn: attack → Ney

####################################################################################################
# THE MORNING DISPATCH
####################################################################################################
{
 "turn": 14,
 "situation": {
  "player_regions": 30,
  "enemy_regions": 96,
  "treasury": 16388,
  "treasury_delta": -16,
  "trade_income": 500,
  "occupation": 90,
  "contributions": 0,
  "state_charges": 1571,
  "requisitions": 0,
  "overseas": 0,
  "dotation_skim": 0,
  "unmet_marshals": [
   {
    "marshal": "Davout",
    "expectation": 300,
    "satisfaction": 240,
    "shortfall": 60,
    "eroding": true,
    "grace_turns_left": 0,
    "pension": 240
   },
   {
    "marshal": "Soult",
    "expectation": 200,
    "satisfaction": 160,
    "shortfall": 40,
    "eroding": true,
    "grace_turns_left": 0,
    "pension": 160
   },
   {
    "marshal": "Murat",
    "expectation": 300,
    "satisfaction": 280,
    "shortfall": 20,
    "eroding": true,
    "grace_turns_left": 0,
    "pension": 280
   },
   {
    "marshal": "Bernadotte",
    "expectation": 240,
    "satisfaction": 160,
    "shortfall": 80,
    "eroding": true,
    "grace_turns_left": 0,
    "pension": 160
   },
   {
    "marshal": "Massena",
    "expectation": 300,
    "satisfaction": 0,
    "shortfall": 300,
    "eroding": true,
    "grace_turns_left": 0,
    "pension": 0
   }
  ],
  "rente_cost": 2010,
  "expectation_rises": [],
  "blockade": 250,
  "admiralty": 90,
  "upkeep_surcharge": 0,
  "force_limit": 135000,
  "over_force_limit": false,
  "bankrupt": false,
  "strength_ratio_pct": 45,
  "authority": 100,
  "authority_label": "Strong"
 },
 "marshals": [
  {
   "name": "Soult",
   "location": "Tyrol",
   "strength": 21017,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 7,
   "danger": "",
   "trust": 62,
   "trust_notable": false,
   "morale": 80,
   "morale_warning": false
  },
  {
   "name": "Davout",
   "location": "Carniola",
   "strength": 18151,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 1,
   "danger": "Starving \u2014 supply has failed at Carniola two turns running.",
   "trust": 70,
   "trust_notable": false,
   "morale": 45,
   "morale_warning": true
  },
  {
   "name": "Lannes",
   "location": "Rhineland",
   "strength": 16505,
   "status": "idle_restless",
   "status_note": "10 turns idle.",
   "arc_note": "",
   "idle_turns": 10,
   "danger": "",
   "trust": 75,
   "trust_notable": false,
   "morale": 85,
   "morale_warning": false
  },
  {
   "name": "Massena",
   "location": "Carniola",
   "strength": 12528,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 1,
   "danger": "Morale failing (0) \u2014 the men waver.",
   "trust": 41,
   "trust_notable": true,
   "morale": 0,
   "morale_warning": true
  },
  {
   "name": "Bernadotte",
   "location": "Munich",
   "strength": 12378,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 7,
   "danger": "",
   "trust": 20,
   "trust_notable": true,
   "morale": 80,
   "morale_warning": false
  },
  {
   "name": "Murat",
   "location": "Carniola",
   "strength": 10247,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 1,
   "danger": "Morale failing (28) \u2014 the men waver.",
   "trust": 58,
   "trust_notable": false,
   "morale": 28,
   "morale_warning": true
  },
  {
   "name": "Ney",
   "location": "Carniola",
   "strength": 9004,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 1,
   "danger": "Morale failing (30) \u2014 the men waver.",
   "trust": 56,
   "trust_notable": false,
   "morale": 30,
   "morale_warning": true
  }
 ],
 "intelligence": [
  {
   "name": "Castanos",
   "location": "Artois",
   "strength_display": "small force",
   "visibility": "partial",
   "intel_turn": 14
  },
  {
   "name": "Archduke Charles",
   "location": "Moravia",
   "strength_display": "substantial force",
   "visibility": "stale",
   "intel_turn": 11
  },
  {
   "name": "Archduke John",
   "location": "Moravia",
   "strength_display": "small force",
   "visibility": "stale",
   "intel_turn": 11
  },
  {
   "name": "Bennigsen",
   "location": "Moravia",
   "strength_display": "screening force",
   "visibility": "stale",
   "intel_turn": 11
  },
  {
   "name": "Mack",
   "location": "Berlin",
   "strength_display": "screening force",
   "visibility": "last_known",
   "intel_turn": 5
  },
  {
   "name": "Brunswick",
   "location": "Berlin",
   "strength_display": "large force",
   "visibility": "last_known",
   "intel_turn": 5
  },
  {
   "name": "Paget",
   "location": "Leon",
   "strength_display": "screening force",
   "visibility": "last_known",
   "intel_turn": 9
  }
 ],
 "turn_events": [
  {
   "message": "Supply shortage at Carniola: Ney loses 278 troops",
   "severity": "warning"
  },
  {
   "message": "Supply shortage at Carniola: Davout loses 561 troops",
   "severity": "warning"
  },
  {
   "message": "Supply shortage at Carniola: Murat loses 316 troops",
   "severity": "warning"
  },
  {
   "message": "Supply shortage at Carniola: Massena loses 387 troops",
   "severity": "warning"
  },
  {
   "message": "Holland loyalty 100 (+2): a common enemy, the lord's victories",
   "severity": "info"
  },
  {
   "message": "KingdomOfItaly loyalty 100 (+2): a common enemy, the lord's victories",
   "severity": "info"
  },
  {
   "message": "Davout's grievance is satisfied \u2014 a victory won shoulder to shoulder. He holds
  with renewed purpose (+10% defense this turn).",
   "severity": "good"
  },
  {
   "message": "Berthier reports that Murat resents Ney's laurels again, 12 turns after the last
  \u2014 he has grown restless for glory.",
   "severity": "warning"
  },
  {
   "message": "Berthier reports that Davout appears envious of Ney's laurels \u2014 he has grown
  careful about what he commits to paper.",
   "severity": "warning"
  }
 ],
 "headline": {
  "class": "victory_won",
  "weight": 73,
  "text": "Sire \u2014 Marshal Ney holds the field at Carniola \u2014 Archduke John's corps is
  broken and flees.",
  "sub_beats": [
   "Sire \u2014 Marshal Davout's household goes unpaid. His patience erodes with his purse.",
   "Sire \u2014 the establishment stands 35,170 men under the ordinance, and the depots hold
  100,000. 10,000 foot cost 450 gold at Paris, where a marshal must stand to receive them."
  ]
 },
 "berthier_note": "The army knows it is winning, Sire. Press the advantage before their line
  reforms.",
 "talleyrand_report": [
  {
   "message": "Sire, I believe Bavaria may be ready to discuss improved relations. The diplomatic
  winds favor us.",
   "trigger_type": "acceptance_crossed",
   "target_nation": "Bavaria",
   "priority": 2,
   "elaborate_type": "proposal_options"
  },
  {
   "message": "Sire, I believe Hesse may be ready to discuss improved relations. The diplomatic
  winds favor us.",
   "trigger_type": "acceptance_crossed",
   "target_nation": "Hesse",
   "priority": 2,
   "elaborate_type": "proposal_options"
  }
 ],
 "talleyrand_discovery": null,
 "talleyrand_override_note": null,
 "talleyrand_redemption": null,
 "coalition_status": {
  "threat_level": 78,
  "tier": "Formed",
  "sources": [
   {
    "source": "hegemony_passive",
    "amount": 1,
    "target": "France"
   },
   {
    "source": "decay",
    "amount": -3
   }
  ],
  "active_coalition": {
   "name": "Third Coalition",
   "leader": "Britain",
   "posture": "defensive",
   "formed_turn": 1,
   "members": [
    {
     "nation": "Austria",
     "war_exhaustion": 0,
     "strength_display": "Considerable",
     "strength": 0,
     "gold": 0
    },
    {
     "nation": "Britain",
     "war_exhaustion": 0,
     "strength_display": "Unknown",
     "strength": 0,
     "gold": 0
    },
    {
     "nation": "Russia",
     "war_exhaustion": 0,
     "strength_display": "Considerable",
     "strength": 0,
     "gold": 0
    }
   ]
  }
 },
 "diplomatic_events": [
  {
   "type": "diplomatic_dp_regen",
   "text": "Talleyrand reports: 5 diplomatic points available (base 3, +1 skill, +1 authority).",
   "priority": "LOW"
  },
  {
   "type": "paymaster_subsidy",
   "text": "Britain's gold reaches Russia \u2014 the subsidy stands at 300 this season.",
   "priority": "MEDIUM"
  }
 ],
 "lapsed_offers": [
  {
   "nation": "Hesse",
   "proposal_type": "non aggression"
  }
 ],
 "pending_envoy_count": 3,
 "pending_envoys": [
  {
   "nation": "Britain",
   "proposal_type": "settlement offer",
   "state": "ACTIVE"
  },
  {
   "nation": "Prussia",
   "proposal_type": "open borders",
   "state": "WAITING"
  },
  {
   "nation": "Bavaria",
   "proposal_type": "request reward or restoration",
   "state": "WAITING"
  }
 ]
}
-- POPUP/DIALOGUE [notifications] --
   [
    {
     "id": "81f980f4-f39e-4bcb-b8e8-5529381d1ab8",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Prussia",
     "message": "An envoy from Prussia has arrived with a proposal.",
     "turn_created": 13,
     "details": {},
     "base_title": "Envoy from Prussia",
     "repeat_count": 1
    },
    {
     "id": "823b437f-15a0-4fb9-8251-37ed3e1cd475",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Soult grows bitter (x2)",
     "message": "Marshal Soult's victories remain unrewarded (expects 200g/turn of estates; holds
     160g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente to stop
     the erosion.",
     "turn_created": 12,
     "details": {
      "marshal": "Soult",
      "expectation": 200,
      "satisfaction": 160,
      "shortfall": 40
     },
     "base_title": "Marshal Soult grows bitter",
     "repeat_count": 2
    },
    {
     "id": "ff90a7da-d536-4658-af81-bbd0a31ad89d",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Davout grows bitter (x2)",
     "message": "Marshal Davout's victories remain unrewarded (expects 300g/turn of estates; holds
     240g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente to stop
     the erosion.",
     "turn_created": 11,
     "details": {
      "marshal": "Davout",
      "expectation": 300,
      "satisfaction": 240,
      "shortfall": 60
     },
     "base_title": "Marshal Davout grows bitter",
     "repeat_count": 2
    },
    {
     "id": "ea9c2894-880f-4204-90ba-93891be05813",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Murat grows bitter (x2)",
     "message": "Marshal Murat's victories remain unrewarded (expects 300g/turn of estates; holds
     280g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente to stop
     the erosion.",
     "turn_created": 11,
     "details": {
      "marshal": "Murat",
      "expectation": 300,
      "satisfaction": 280,
      "shortfall": 20
     },
     "base_title": "Marshal Murat grows bitter",
     "repeat_count": 2
    },
    {
     "id": "11eb075a-98d7-4a9b-94f1-ee058610f860",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Bernadotte grows bitter (x2)",
     "message": "Marshal Bernadotte's victories remain unrewarded (expects 240g/turn of estates;
     holds 160g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente
     to stop the erosion.",
     "turn_created": 10,
     "details": {
      "marshal": "Bernadotte",
      "expectation": 240,
      "satisfaction": 160,
      "shortfall": 80
     },
     "base_title": "Marshal Bernadotte grows bitter",
     "repeat_count": 2
    },
    {
     "id": "36d9d8db-6539-449d-a72e-e376e20d03dc",
     "type": "counter_punch_earned",
     "priority": 1,
     "title": "Davout \u2014 free attack!",
     "message": "Davout earned a free attack from their defensive victory. Use within 2 turns or the
     opportunity expires.",
     "turn_created": 10,
     "details": {
      "marshal": "Davout"
     },
     "base_title": "Davout \u2014 free attack!",
     "repeat_count": 1
    },
    {
     "id": "552b1a44-5cbe-4a9a-a123-61707f7c98de",
     "type": "strategic_order_complete",
     "priority": 1,
     "title": "Soult arrived",
     "message": "Soult has completed their SUPPORT order \u2014 arrived at Tyrol.",
     "turn_created": 9,
     "details": {
      "marshal": "Soult",
      "order_type": "SUPPORT",
      "target": "Ney"
     },
     "base_title": "Soult arrived",
     "repeat_count": 1
    },
    {
     "id": "6e5cb538-9460-469d-8e1a-fd9ba4fe4d95",
     "type": "incoming_settlement_offer",
     "priority": 1,
     "title": "Settlement offer from Britain (x2)",
     "message": "Britain has offered terms to settle France vs Britain. Asking 629 gold.",
     "turn_created": 8,
     "details": {
      "war_id": "war_1",
      "offer_id": "settlement_offer:war_1:8:1",
      "proposer_nation": "Britain",
      "amount": 629,
      "review_target": "incoming_settlement_offer_popup"
     },
     "base_title": "Settlement offer from Britain",
     "repeat_count": 2
    },
    {
     "id": "73f91faa-7c19-4dee-befa-77e8ca2425e8",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Massena grows bitter",
     "message": "M

====================================================================================================
> end turn
====================================================================================================
Turn 14 ended. (Warning: 4 action(s) unused) Turn 15 begins!

Income: 3519g | Occupation: -90g | Charges of Empire: -1617g | Rentes: -2010g | Admiralty: -90g |
  Blockade: -250g | Upkeep: 760g | Other: +1262g | Net: -36g | Treasury: 16,352g
   [cost=0  turn_advanced=False]
   <event supply_attrition> {"marshal": "Ney", "nation": "France", "region": "Carniola", "losses": 270, "message": "Supply shortage at Carniola: Ney loses 270 troops"}
   <event supply_attrition> {"marshal": "Davout", "nation": "France", "region": "Carniola", "losses": 544, "message": "Supply shortage at Carniola: Davout loses 544 troops"}
   <event supply_attrition> {"marshal": "Murat", "nation": "France", "region": "Carniola", "losses": 307, "message": "Supply shortage at Carniola: Murat loses 307 troops"}
   <event supply_attrition> {"marshal": "Massena", "nation": "France", "region": "Carniola", "losses": 375, "message": "Supply shortage at Carniola: Massena loses 375 troops"}
   <event vassal_loyalty> {"vassal": "Switzerland", "lord": "France", "nation": "France", "old_loyalty": 86, "new_loyalty": 84, "delta": -2, "reason": "satellite drift", "recovery_hint": "Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.", "message": "Switzerland loyalty 84 (-2): satellite drift \u2014 Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them."}
   <event british_subsidy> {"recipient": "Austria", "payer": "Britain", "amount": 300, "war_id": "war_1", "subsidy_source_detail": "unique_eligible", "message": "Britain subsidizes Austria with 300 gold."}
   <event sponsorship_granted> {"kind": "sponsorship", "payer": "Britain", "recipient": "Sweden", "aim": "France", "amount": 300, "turns": 10, "licence": false, "turn": 15}
   <event third_party_peace> {"war_id": "war_1", "proposer": "Austria", "accepter": "Bavaria", "broker": null, "consequence": "Both courts are spent; their side of the war ends while the greater war goes on.", "message": "Peace concluded between Austria and Bavaria without France. Both courts are spent; their side of the war ends while the greater war goes on."}
   <event sponsorship_expired> {"payer": "Russia", "recipient": "Britain", "aim": "France", "kind": "sponsorship", "turn": 15}
   <event trust_warning> {"marshal": "Massena", "trust": 38, "message": "[!] Massena's trust is faltering (38). Consider giving them more independence."}
   <event jealousy_resolved> {"message": "Soult's resentment of Bernadotte has cooled with time.", "nation": "France", "marshal": "Soult"}

####################################################################################################
# THE ENEMY PHASE
####################################################################################################
[fog_hidden_summary] ["Our scouts report activity within Britain's borders, but their formations remain beyond our
  sight.", "Our scouts report activity within Russia's borders, but their formations remain beyond
  our sight.", "Our scouts report activity within Austria's borders, but their formations remain
  beyond our sight.", "Our scouts report activity within Prussia's borders, but their formations
  remain beyond our sight.", "Our scouts report activity within Spain's borders, but their
  formations remain beyond our sight.", "Our scouts report activity within Ottoman's borders, but
  their formations remain beyond our sight.", "Our scouts report activity within Sweden's borders,
  but their formations remain beyond our sight.", "Our scouts report activity within Naples's
  borders, but their formations remain beyond our sight.", "Our scouts report activity within
  Denmark's borders, but their formations remain beyond our sight."]

####################################################################################################
# THE MORNING DISPATCH
####################################################################################################
{
 "turn": 15,
 "situation": {
  "player_regions": 30,
  "enemy_regions": 96,
  "treasury": 16352,
  "treasury_delta": -32,
  "trade_income": 500,
  "occupation": 90,
  "contributions": 0,
  "state_charges": 1613,
  "requisitions": 0,
  "overseas": 0,
  "dotation_skim": 0,
  "unmet_marshals": [
   {
    "marshal": "Davout",
    "expectation": 300,
    "satisfaction": 240,
    "shortfall": 60,
    "eroding": true,
    "grace_turns_left": 0,
    "pension": 240
   },
   {
    "marshal": "Soult",
    "expectation": 200,
    "satisfaction": 160,
    "shortfall": 40,
    "eroding": true,
    "grace_turns_left": 0,
    "pension": 160
   },
   {
    "marshal": "Murat",
    "expectation": 300,
    "satisfaction": 280,
    "shortfall": 20,
    "eroding": true,
    "grace_turns_left": 0,
    "pension": 280
   },
   {
    "marshal": "Bernadotte",
    "expectation": 240,
    "satisfaction": 160,
    "shortfall": 80,
    "eroding": true,
    "grace_turns_left": 0,
    "pension": 160
   },
   {
    "marshal": "Massena",
    "expectation": 300,
    "satisfaction": 0,
    "shortfall": 300,
    "eroding": true,
    "grace_turns_left": 0,
    "pension": 0
   }
  ],
  "rente_cost": 2010,
  "expectation_rises": [],
  "blockade": 250,
  "admiralty": 90,
  "upkeep_surcharge": 0,
  "force_limit": 135000,
  "over_force_limit": false,
  "bankrupt": false,
  "strength_ratio_pct": 46,
  "authority": 100,
  "authority_label": "Strong"
 },
 "marshals": [
  {
   "name": "Soult",
   "location": "Tyrol",
   "strength": 21017,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 8,
   "danger": "",
   "trust": 61,
   "trust_notable": false,
   "morale": 80,
   "morale_warning": false
  },
  {
   "name": "Davout",
   "location": "Carniola",
   "strength": 17607,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 2,
   "danger": "Starving \u2014 supply has failed at Carniola two turns running.",
   "trust": 68,
   "trust_notable": false,
   "morale": 45,
   "morale_warning": true
  },
  {
   "name": "Lannes",
   "location": "Rhineland",
   "strength": 16505,
   "status": "idle_restless",
   "status_note": "11 turns idle.",
   "arc_note": "",
   "idle_turns": 11,
   "danger": "",
   "trust": 75,
   "trust_notable": false,
   "morale": 85,
   "morale_warning": false
  },
  {
   "name": "Bernadotte",
   "location": "Munich",
   "strength": 12378,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 8,
   "danger": "",
   "trust": 18,
   "trust_notable": true,
   "morale": 80,
   "morale_warning": false
  },
  {
   "name": "Massena",
   "location": "Carniola",
   "strength": 12153,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 2,
   "danger": "Morale failing (0) \u2014 the men waver.",
   "trust": 38,
   "trust_notable": true,
   "morale": 0,
   "morale_warning": true
  },
  {
   "name": "Murat",
   "location": "Carniola",
   "strength": 9940,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 2,
   "danger": "Morale failing (28) \u2014 the men waver.",
   "trust": 57,
   "trust_notable": false,
   "morale": 28,
   "morale_warning": true
  },
  {
   "name": "Ney",
   "location": "Carniola",
   "strength": 8734,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 2,
   "danger": "Morale failing (30) \u2014 the men waver.",
   "trust": 56,
   "trust_notable": false,
   "morale": 30,
   "morale_warning": true
  }
 ],
 "intelligence": [
  {
   "name": "Deroy",
   "location": "Munich",
   "strength_display": "5,000",
   "visibility": "full",
   "intel_turn": 15
  },
  {
   "name": "Castanos",
   "location": "Artois",
   "strength_display": "small force",
   "visibility": "partial",
   "intel_turn": 15
  },
  {
   "name": "Archduke Charles",
   "location": "Moravia",
   "strength_display": "substantial force",
   "visibility": "stale",
   "intel_turn": 11
  },
  {
   "name": "Archduke John",
   "location": "Moravia",
   "strength_display": "small force",
   "visibility": "stale",
   "intel_turn": 11
  },
  {
   "name": "Bennigsen",
   "location": "Moravia",
   "strength_display": "screening force",
   "visibility": "stale",
   "intel_turn": 11
  },
  {
   "name": "Mack",
   "location": "Berlin",
   "strength_display": "screening force",
   "visibility": "last_known",
   "intel_turn": 5
  },
  {
   "name": "Brunswick",
   "location": "Berlin",
   "strength_display": "large force",
   "visibility": "last_known",
   "intel_turn": 5
  },
  {
   "name": "Paget",
   "location": "Leon",
   "strength_display": "screening force",
   "visibility": "last_known",
   "intel_turn": 9
  }
 ],
 "turn_events": [
  {
   "message": "Supply shortage at Carniola: Ney loses 270 troops",
   "severity": "warning"
  },
  {
   "message": "Supply shortage at Carniola: Davout loses 544 troops",
   "severity": "warning"
  },
  {
   "message": "Supply shortage at Carniola: Murat loses 307 troops",
   "severity": "warning"
  },
  {
   "message": "Supply shortage at Carniola: Massena loses 375 troops",
   "severity": "warning"
  },
  {
   "message": "Switzerland loyalty 84 (-2): satellite drift \u2014 Invest in them, grant them
  autonomy, garrison their capital, or cede them a province to steady them.",
   "severity": "warning"
  },
  {
   "message": "Soult's resentment of Bernadotte has cooled with time.",
   "severity": "good"
  }
 ],
 "headline": {
  "class": "estate_eroding",
  "weight": 55,
  "text": "Sire \u2014 Marshal Davout's household goes unpaid. His patience erodes with his purse.",
  "sub_beats": [
   "Sire \u2014 the establishment stands 36,666 men under the ordinance, and the depots hold
  100,000. 10,000 foot cost 450 gold at Paris, where a marshal must stand to receive them.",
   "Sire \u2014 Austria and Bavaria have made peace without us."
  ]
 },
 "berthier_note": "A marshal who feels forgotten fights like one, Sire. The estate rolls want
  attention.",
 "talleyrand_report": [
  {
   "message": "Sire, I believe Spain may be ready to discuss improved relations. The diplomatic
  winds favor us.",
   "trigger_type": "acceptance_crossed",
   "target_nation": "Spain",
   "priority": 2,
   "elaborate_type": "proposal_options"
  },
  {
   "message": "Sire, I believe Switzerland may be ready to discuss improved relations. The
  diplomatic winds favor us.",
   "trigger_type": "acceptance_crossed",
   "target_nation": "Switzerland",
   "priority": 2,
   "elaborate_type": "proposal_options"
  }
 ],
 "talleyrand_discovery": null,
 "talleyrand_override_note": null,
 "talleyrand_redemption": null,
 "coalition_status": {
  "threat_level": 76,
  "tier": "Formed",
  "sources": [
   {
    "source": "hegemony_passive",
    "amount": 1,
    "target": "France"
   },
   {
    "source": "decay",
    "amount": -3
   }
  ],
  "active_coalition": {
   "name": "Third Coalition",
   "leader": "Britain",
   "posture": "defensive",
   "formed_turn": 1,
   "members": [
    {
     "nation": "Austria",
     "war_exhaustion": 0,
     "strength_display": "Considerable",
     "strength": 0,
     "gold": 0
    },
    {
     "nation": "Britain",
     "war_exhaustion": 0,
     "strength_display": "Unknown",
     "strength": 0,
     "gold": 0
    },
    {
     "nation": "Russia",
     "war_exhaustion": 0,
     "strength_display": "Considerable",
     "strength": 0,
     "gold": 0
    }
   ]
  }
 },
 "diplomatic_events": [
  {
   "type": "diplomatic_dp_regen",
   "text": "Talleyrand reports: 5 diplomatic points available (base 3, +1 skill, +1 authority).",
   "priority": "LOW"
  },
  {
   "type": "paymaster_subsidy",
   "text": "Britain's gold reaches Austria \u2014 the subsidy stands at 300 this season.",
   "priority": "MEDIUM"
  },
  {
   "type": "third_party_peace",
   "text": "THE CONGRESS: Austria and Bavaria have made their peace without France. Both courts are
  spent; their side of the war ends while the greater war goes on.",
   "priority": "HIGH"
  }
 ],
 "lapsed_offers": [
  {
   "nation": "Prussia",
   "proposal_type": "friendly gift"
  }
 ],
 "pending_envoy_count": 4,
 "pending_envoys": [
  {
   "nation": "Britain",
   "proposal_type": "settlement offer",
   "state": "ACTIVE"
  },
  {
   "nation": "Naples",
   "proposal_type": "open borders",
   "state": "WAITING"
  },
  {
   "nation": "PapalStates",
   "proposal_type": "open borders",
   "state": "WAITING"
  },
  {
   "nation": "Bavaria",
   "proposal_type": "request reward or restoration",
   "state": "WAITING"
  }
 ]
}
-- POPUP/DIALOGUE [notifications] --
   [
    {
     "id": "972f56f2-80ce-4d1f-bb4f-067c1a31849f",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Naples",
     "message": "An envoy from Naples has arrived with a proposal.",
     "turn_created": 14,
     "details": {},
     "base_title": "Envoy from Naples",
     "repeat_count": 1
    },
    {
     "id": "a6db96ea-2bd2-45ea-8eb4-3853975f59a1",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Papal States",
     "message": "An envoy from Papal States has arrived with a proposal.",
     "turn_created": 14,
     "details": {},
     "base_title": "Envoy from Papal States",
     "repeat_count": 1
    },
    {
     "id": "823b437f-15a0-4fb9-8251-37ed3e1cd475",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Soult grows bitter (x2)",
     "message": "Marshal Soult's victories remain unrewarded (expects 200g/turn of estates; holds
     160g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente to stop
     the erosion.",
     "turn_created": 12,
     "details": {
      "marshal": "Soult",
      "expectation": 200,
      "satisfaction": 160,
      "shortfall": 40
     },
     "base_title": "Marshal Soult grows bitter",
     "repeat_count": 2
    },
    {
     "id": "ff90a7da-d536-4658-af81-bbd0a31ad89d",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Davout grows bitter (x2)",
     "message": "Marshal Davout's victories remain unrewarded (expects 300g/turn of estates; holds
     240g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente to stop
     the erosion.",
     "turn_created": 11,
     "details": {
      "marshal": "Davout",
      "expectation": 300,
      "satisfaction": 240,
      "shortfall": 60
     },
     "base_title": "Marshal Davout grows bitter",
     "repeat_count": 2
    },
    {
     "id": "ea9c2894-880f-4204-90ba-93891be05813",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Murat grows bitter (x2)",
     "message": "Marshal Murat's victories remain unrewarded (expects 300g/turn of estates; holds
     280g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente to stop
     the erosion.",
     "turn_created": 11,
     "details": {
      "marshal": "Murat",
      "expectation": 300,
      "satisfaction": 280,
      "shortfall": 20
     },
     "base_title": "Marshal Murat grows bitter",
     "repeat_count": 2
    },
    {
     "id": "11eb075a-98d7-4a9b-94f1-ee058610f860",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Bernadotte grows bitter (x2)",
     "message": "Marshal Bernadotte's victories remain unrewarded (expects 240g/turn of estates;
     holds 160g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente
     to stop the erosion.",
     "turn_created": 10,
     "details": {
      "marshal": "Bernadotte",
      "expectation": 240,
      "satisfaction": 160,
      "shortfall": 80
     },
     "base_title": "Marshal Bernadotte grows bitter",
     "repeat_count": 2
    },
    {
     "id": "36d9d8db-6539-449d-a72e-e376e20d03dc",
     "type": "counter_punch_earned",
     "priority": 1,
     "title": "Davout \u2014 free attack!",
     "message": "Davout earned a free attack from their defensive victory. Use within 2 turns or the
     opportunity expires.",
     "turn_created": 10,
     "details": {
      "marshal": "Davout"
     },
     "base_title": "Davout \u2014 free attack!",
     "repeat_count": 1
    },
    {
     "id": "552b1a44-5cbe-4a9a-a123-61707f7c98de",
     "type": "strategic_order_complete",
     "priority": 1,
     "title": "Soult arrived",
     "message": "Soult has completed their SUPPORT order \u2014 arrived at Tyrol.",
     "turn_created": 9,
     "details": {
      "marshal": "Soult",
      "order_type": "SUPPORT",
      "target": "Ney"
     },
     "base_title": "Soult arrived",
     "repeat_count": 1
    },
    {
     "id": "6e5cb538-9460-469d-8e1a-fd9ba4fe4d95",
     "type": "incoming_settlement_offer",
     "priority": 1,
     "title": "Settlement offer from Britain (x2)",
     "message": "Britain has offered terms to settle France vs Britain. Asking 629 gold.",
     "turn_created": 8,
     "details": {
      "war_id": "war_1",
      "offer_id": "settlement_offer:war_1:8:1",
      "proposer_nation": "Br

====================================================================================================
> end turn
====================================================================================================
Turn 15 ended. (Warning: 4 action(s) unused) Turn 16 begins!

Income: 3543g | Occupation: -67g | Charges of Empire: -1659g | Rentes: -2010g | Admiralty: -90g |
  Blockade: -250g | Upkeep: 752g | Other: +1262g | Net: -23g | Treasury: 16,329g
   [cost=0  turn_advanced=False]
   <event supply_attrition> {"marshal": "Ney", "nation": "France", "region": "Carniola", "losses": 262, "message": "Supply shortage at Carniola: Ney loses 262 troops"}
   <event supply_attrition> {"marshal": "Davout", "nation": "France", "region": "Carniola", "losses": 528, "message": "Supply shortage at Carniola: Davout loses 528 troops"}
   <event supply_attrition> {"marshal": "Murat", "nation": "France", "region": "Carniola", "losses": 298, "message": "Supply shortage at Carniola: Murat loses 298 troops"}
   <event supply_attrition> {"marshal": "Massena", "nation": "France", "region": "Carniola", "losses": 364, "message": "Supply shortage at Carniola: Massena loses 364 troops"}
   <event supply_attrition> {"marshal": "Bernadotte", "nation": "France", "region": "Munich", "losses": 169, "message": "Supply shortage at Munich: Bernadotte loses 169 troops"}
   <event vassal_loyalty> {"vassal": "Switzerland", "lord": "France", "nation": "France", "old_loyalty": 84, "new_loyalty": 82, "delta": -2, "reason": "satellite drift", "recovery_hint": "Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.", "message": "Switzerland loyalty 82 (-2): satellite drift \u2014 Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them."}
   <event british_subsidy> {"recipient": "Austria", "payer": "Britain", "amount": 300, "war_id": "war_1", "subsidy_source_detail": "unique_eligible", "message": "Britain subsidizes Austria with 300 gold."}
   <event sponsorship_granted> {"kind": "sponsorship", "payer": "Russia", "recipient": "Britain", "aim": "France", "amount": 300, "turns": 10, "licence": false, "turn": 16}
   <event third_party_peace> {"war_id": "war_1", "proposer": "Britain", "accepter": "Spain", "broker": null, "consequence": "Both courts are spent; their side of the war ends while the greater war goes on.", "message": "Peace concluded between Britain and Spain without France. Both courts are spent; their side of the war ends while the greater war goes on."}
   <event sponsorship_expired> {"payer": "Britain", "recipient": "Austria", "aim": "France", "kind": "sponsorship", "turn": 16}
   <event jealousy_resolved> {"message": "Lannes's resentment of Murat has cooled for now. What was settled between them at the staff table has not been.", "nation": "France", "marshal": "Lannes"}
   <event jealousy_fired> {"message": "Berthier reports that Lannes resents Murat's laurels for the fourth time \u2014 he has grown restless for glory.", "nation": "France", "marshal": "Lannes", "target": "Murat"}
   <event jealousy_fired> {"message": "Berthier reports that Murat resents Lannes's laurels again, 5 turns after the last \u2014 he has grown impatient for something worth the doing.", "nation": "France", "marshal": "Murat", "target": "Lannes"}
   <event jealousy_escalation> {"message": "The feud between Lannes and Murat is now mutual \u2014 each schemes against the other. Separate them, Sire, or accept the friction.", "nation": "France", "marshal": "Lannes", "target": "Murat"}
   <event intel_decayed> {"region": "Dresden", "old_visibility": "stale", "new_visibility": "last_known"}
   <event intel_decayed> {"region": "Vienna", "old_visibility": "stale", "new_visibility": "last_known"}
   <event intel_decayed> {"region": "Moravia", "old_visibility": "stale", "new_visibility": "last_known"}
   <event intel_decayed> {"region": "Epirus", "old_visibility": "partial", "new_visibility": "stale"}

####################################################################################################
# THE ENEMY PHASE
####################################################################################################
-- Bavaria --
  - Deroy holds position
      [wait] {"type": "wait", "marshal": "Deroy", "location": "Munich", "action_cost": 0}
  - Deroy recruits troops
      [recruit] {"type": "recruit", "marshal": "Deroy", "location": "Munich", "recruit_type": "infantry", "troops_added": 10000, "gold_cost": 150, "morale_before": 60, "morale_after": 46, "new_strength": 15000, "stability_premium": false, "capital_discount": true, "intendance_pct": 0, "pool_before": 32693, "pool_af
  - Deroy recruits troops
      [recruit] {"type": "recruit", "marshal": "Deroy", "location": "Munich", "recruit_type": "infantry", "troops_added": 10000, "gold_cost": 150, "morale_before": 46, "morale_after": 43, "new_strength": 25000, "stability_premium": false, "capital_discount": true, "intendance_pct": 0, "pool_before": 22693, "pool_af
    [action_count] 4
[summary]
   Deroy: wait
   Deroy: recruit → Munich
   Deroy: recruit → Munich

####################################################################################################
# THE MORNING DISPATCH
####################################################################################################
{
 "turn": 16,
 "situation": {
  "player_regions": 30,
  "enemy_regions": 96,
  "treasury": 16329,
  "treasury_delta": -20,
  "trade_income": 500,
  "occupation": 67,
  "contributions": 0,
  "state_charges": 1656,
  "requisitions": 0,
  "overseas": 0,
  "dotation_skim": 0,
  "unmet_marshals": [
   {
    "marshal": "Davout",
    "expectation": 300,
    "satisfaction": 240,
    "shortfall": 60,
    "eroding": true,
    "grace_turns_left": 0,
    "pension": 240
   },
   {
    "marshal": "Soult",
    "expectation": 200,
    "satisfaction": 160,
    "shortfall": 40,
    "eroding": true,
    "grace_turns_left": 0,
    "pension": 160
   },
   {
    "marshal": "Murat",
    "expectation": 300,
    "satisfaction": 280,
    "shortfall": 20,
    "eroding": true,
    "grace_turns_left": 0,
    "pension": 280
   },
   {
    "marshal": "Bernadotte",
    "expectation": 240,
    "satisfaction": 160,
    "shortfall": 80,
    "eroding": true,
    "grace_turns_left": 0,
    "pension": 160
   },
   {
    "marshal": "Massena",
    "expectation": 300,
    "satisfaction": 0,
    "shortfall": 300,
    "eroding": true,
    "grace_turns_left": 0,
    "pension": 0
   }
  ],
  "rente_cost": 2010,
  "expectation_rises": [],
  "blockade": 250,
  "admiralty": 90,
  "upkeep_surcharge": 0,
  "force_limit": 135000,
  "over_force_limit": false,
  "bankrupt": false,
  "strength_ratio_pct": 47,
  "authority": 100,
  "authority_label": "Strong"
 },
 "marshals": [
  {
   "name": "Soult",
   "location": "Tyrol",
   "strength": 21017,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 9,
   "danger": "",
   "trust": 60,
   "trust_notable": false,
   "morale": 80,
   "morale_warning": false
  },
  {
   "name": "Davout",
   "location": "Carniola",
   "strength": 17079,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 3,
   "danger": "Starving \u2014 supply has failed at Carniola two turns running.",
   "trust": 66,
   "trust_notable": false,
   "morale": 45,
   "morale_warning": true
  },
  {
   "name": "Lannes",
   "location": "Rhineland",
   "strength": 16505,
   "status": "idle_restless",
   "status_note": "12 turns idle.",
   "arc_note": "",
   "idle_turns": 12,
   "danger": "",
   "trust": 75,
   "trust_notable": false,
   "morale": 85,
   "morale_warning": false
  },
  {
   "name": "Bernadotte",
   "location": "Munich",
   "strength": 12209,
   "status": "awaiting",
   "status_note": "Awaiting orders.",
   "arc_note": "",
   "idle_turns": 9,
   "danger": "",
   "trust": 16,
   "trust_notable": true,
   "morale": 80,
   "morale_warning": false
  },
  {
   "name": "Massena",
   "location": "Carniola",
   "strength": 11789,
   "status": "idle_restless",
   "status_note": "3 turns idle.",
   "arc_note": "",
   "idle_turns": 3,
   "danger": "Morale failing (0) \u2014 the men waver.",
   "trust": 35,
   "trust_notable": true,
   "morale": 0,
   "morale_warning": true
  },
  {
   "name": "Murat",
   "location": "Carniola",
   "strength": 9642,
   "status": "idle_restless",
   "status_note": "3 turns idle.",
   "arc_note": "",
   "idle_turns": 3,
   "danger": "Morale failing (28) \u2014 the men waver.",
   "trust": 56,
   "trust_notable": false,
   "morale": 28,
   "morale_warning": true
  },
  {
   "name": "Ney",
   "location": "Carniola",
   "strength": 8472,
   "status": "idle_restless",
   "status_note": "3 turns idle.",
   "arc_note": "",
   "idle_turns": 3,
   "danger": "Morale failing (30) \u2014 the men waver.",
   "trust": 56,
   "trust_notable": false,
   "morale": 30,
   "morale_warning": true
  }
 ],
 "intelligence": [
  {
   "name": "Deroy",
   "location": "Munich",
   "strength_display": "25,000",
   "visibility": "full",
   "intel_turn": 16
  },
  {
   "name": "Castanos",
   "location": "Artois",
   "strength_display": "small force",
   "visibility": "partial",
   "intel_turn": 16
  },
  {
   "name": "Mack",
   "location": "Berlin",
   "strength_display": "screening force",
   "visibility": "last_known",
   "intel_turn": 5
  },
  {
   "name": "Brunswick",
   "location": "Berlin",
   "strength_display": "large force",
   "visibility": "last_known",
   "intel_turn": 5
  },
  {
   "name": "Archduke Charles",
   "location": "Moravia",
   "strength_display": "substantial force",
   "visibility": "last_known",
   "intel_turn": 11
  },
  {
   "name": "Archduke John",
   "location": "Moravia",
   "strength_display": "small force",
   "visibility": "last_known",
   "intel_turn": 11
  },
  {
   "name": "Bennigsen",
   "location": "Moravia",
   "strength_display": "screening force",
   "visibility": "last_known",
   "intel_turn": 11
  },
  {
   "name": "Paget",
   "location": "Leon",
   "strength_display": "screening force",
   "visibility": "last_known",
   "intel_turn": 9
  }
 ],
 "turn_events": [
  {
   "message": "Supply shortage at Carniola: Ney loses 262 troops",
   "severity": "warning"
  },
  {
   "message": "Supply shortage at Carniola: Davout loses 528 troops",
   "severity": "warning"
  },
  {
   "message": "Supply shortage at Carniola: Murat loses 298 troops",
   "severity": "warning"
  },
  {
   "message": "Supply shortage at Carniola: Massena loses 364 troops",
   "severity": "warning"
  },
  {
   "message": "Supply shortage at Munich: Bernadotte loses 169 troops",
   "severity": "warning"
  },
  {
   "message": "Switzerland loyalty 82 (-2): satellite drift \u2014 Invest in them, grant them
  autonomy, garrison their capital, or cede them a province to steady them.",
   "severity": "warning"
  },
  {
   "message": "Lannes's resentment of Murat has cooled for now. What was settled between them at the
  staff table has not been.",
   "severity": "good"
  },
  {
   "message": "Berthier reports that Lannes resents Murat's laurels for the fourth time \u2014 he
  has grown restless for glory.",
   "severity": "warning"
  },
  {
   "message": "Berthier reports that Murat resents Lannes's laurels again, 5 turns after the last
  \u2014 he has grown impatient for something worth the doing.",
   "severity": "warning"
  },
  {
   "message": "The feud between Lannes and Murat is now mutual \u2014 each schemes against the
  other. Separate them, Sire, or accept the friction.",
   "severity": "warning"
  }
 ],
 "headline": {
  "class": "levy_open",
  "weight": 54,
  "text": "Sire \u2014 the establishment stands 38,287 men under the ordinance, and the depots hold
  100,000. 10,000 foot cost 450 gold at Paris, where a marshal must stand to receive them.",
  "sub_beats": [
   "Sire \u2014 Marshal Davout's household goes unpaid. His patience erodes with his purse.",
   "Sire \u2014 Austria and Bavaria have made peace without us."
  ]
 },
 "berthier_note": "The depots are full and the ordinance allows it, Sire. Conscripts do not improve
  with keeping.",
 "talleyrand_report": [
  {
   "message": "Sire, the diplomatic front has been quiet. Perhaps too quiet. Shall I assess our
  options?",
   "trigger_type": "idle_nudge",
   "target_nation": "",
   "priority": 5,
   "elaborate_type": "proposal_options"
  }
 ],
 "talleyrand_discovery": null,
 "talleyrand_override_note": null,
 "talleyrand_redemption": null,
 "coalition_status": {
  "threat_level": 74,
  "tier": "Formed",
  "sources": [
   {
    "source": "hegemony_passive",
    "amount": 1,
    "target": "France"
   },
   {
    "source": "decay",
    "amount": -3
   }
  ],
  "active_coalition": {
   "name": "Third Coalition",
   "leader": "Britain",
   "posture": "defensive",
   "formed_turn": 1,
   "members": [
    {
     "nation": "Austria",
     "war_exhaustion": 0,
     "strength_display": "54,390 men",
     "strength": 0,
     "gold": 0
    },
    {
     "nation": "Britain",
     "war_exhaustion": 0,
     "strength_display": "Unknown",
     "strength": 0,
     "gold": 0
    },
    {
     "nation": "Russia",
     "war_exhaustion": 0,
     "strength_display": "58,726 men",
     "strength": 0,
     "gold": 0
    }
   ]
  }
 },
 "diplomatic_events": [
  {
   "type": "diplomatic_dp_regen",
   "text": "Talleyrand reports: 5 diplomatic points available (base 3, +1 skill, +1 authority).",
   "priority": "LOW"
  },
  {
   "type": "paymaster_subsidy",
   "text": "Britain's gold reaches Austria \u2014 the subsidy stands at 300 this season.",
   "priority": "MEDIUM"
  },
  {
   "type": "third_party_peace",
   "text": "THE CONGRESS: Britain and Spain have made their peace without France. Both courts are
  spent; their side of the war ends while the greater war goes on.",
   "priority": "HIGH"
  },
  {
   "type": "blockade_broken",
   "text": "The blockade of Spain is broken \u2014 her ports breathe, her crews may drill again.",
   "priority": "MEDIUM"
  }
 ],
 "lapsed_offers": [
  {
   "nation": "Naples",
   "proposal_type": "open borders"
  },
  {
   "nation": "PapalStates",
   "proposal_type": "open borders"
  }
 ],
 "pending_envoy_count": 3,
 "pending_envoys": [
  {
   "nation": "Britain",
   "proposal_type": "settlement offer",
   "state": "ACTIVE"
  },
  {
   "nation": "Hesse",
   "proposal_type": "non aggression",
   "state": "WAITING"
  },
  {
   "nation": "Bavaria",
   "proposal_type": "request reward or restoration",
   "state": "WAITING"
  }
 ]
}
-- POPUP/DIALOGUE [notifications] --
   [
    {
     "id": "ad3d7e5a-d784-4f79-84ac-bd60591fa8d3",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Hesse",
     "message": "An envoy from Hesse has arrived with a proposal.",
     "turn_created": 15,
     "details": {},
     "base_title": "Envoy from Hesse",
     "repeat_count": 1
    },
    {
     "id": "823b437f-15a0-4fb9-8251-37ed3e1cd475",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Soult grows bitter (x2)",
     "message": "Marshal Soult's victories remain unrewarded (expects 200g/turn of estates; holds
     160g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente to stop
     the erosion.",
     "turn_created": 12,
     "details": {
      "marshal": "Soult",
      "expectation": 200,
      "satisfaction": 160,
      "shortfall": 40
     },
     "base_title": "Marshal Soult grows bitter",
     "repeat_count": 2
    },
    {
     "id": "ff90a7da-d536-4658-af81-bbd0a31ad89d",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Davout grows bitter (x2)",
     "message": "Marshal Davout's victories remain unrewarded (expects 300g/turn of estates; holds
     240g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente to stop
     the erosion.",
     "turn_created": 11,
     "details": {
      "marshal": "Davout",
      "expectation": 300,
      "satisfaction": 240,
      "shortfall": 60
     },
     "base_title": "Marshal Davout grows bitter",
     "repeat_count": 2
    },
    {
     "id": "ea9c2894-880f-4204-90ba-93891be05813",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Murat grows bitter (x2)",
     "message": "Marshal Murat's victories remain unrewarded (expects 300g/turn of estates; holds
     280g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente to stop
     the erosion.",
     "turn_created": 11,
     "details": {
      "marshal": "Murat",
      "expectation": 300,
      "satisfaction": 280,
      "shortfall": 20
     },
     "base_title": "Marshal Murat grows bitter",
     "repeat_count": 2
    },
    {
     "id": "11eb075a-98d7-4a9b-94f1-ee058610f860",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Bernadotte grows bitter (x2)",
     "message": "Marshal Bernadotte's victories remain unrewarded (expects 240g/turn of estates;
     holds 160g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente
     to stop the erosion.",
     "turn_created": 10,
     "details": {
      "marshal": "Bernadotte",
      "expectation": 240,
      "satisfaction": 160,
      "shortfall": 80
     },
     "base_title": "Marshal Bernadotte grows bitter",
     "repeat_count": 2
    },
    {
     "id": "36d9d8db-6539-449d-a72e-e376e20d03dc",
     "type": "counter_punch_earned",
     "priority": 1,
     "title": "Davout \u2014 free attack!",
     "message": "Davout earned a free attack from their defensive victory. Use within 2 turns or the
     opportunity expires.",
     "turn_created": 10,
     "details": {
      "marshal": "Davout"
     },
     "base_title": "Davout \u2014 free attack!",
     "repeat_count": 1
    },
    {
     "id": "552b1a44-5cbe-4a9a-a123-61707f7c98de",
     "type": "strategic_order_complete",
     "priority": 1,
     "title": "Soult arrived",
     "message": "Soult has completed their SUPPORT order \u2014 arrived at Tyrol.",
     "turn_created": 9,
     "details": {
      "marshal": "Soult",
      "order_type": "SUPPORT",
      "target": "Ney"
     },
     "base_title": "Soult arrived",
     "repeat_count": 1
    },
    {
     "id": "6e5cb538-9460-469d-8e1a-fd9ba4fe4d95",
     "type": "incoming_settlement_offer",
     "priority": 1,
     "title": "Settlement offer from Britain (x2)",
     "message": "Britain has offered terms to settle France vs Britain. Asking 629 gold.",
     "turn_created": 8,
     "details": {
      "war_id": "war_1",
      "offer_id": "settlement_offer:war_1:8:1",
      "proposer_nation": "Britain",
      "amount": 629,
      "review_target": "incoming_settlement_offer_popup"
     },
     "base_title": "Settlement offer from Britain",
     "repeat_count": 2
    },
    {
     "id": "73f91faa-7c19-4dee-befa-77e8ca2425e8",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Massena grows bitter",
     "message": "Marshal

====================================================================================================
> Talleyrand, assess our situation
====================================================================================================
Sire — the state of Europe, plainly told.

  Against Britain + Austria + Russia: the war favors us (+13) — 10 battles across 15 turns.
    Britain's design: The Low Countries — They will not suffer France's bloc in Flanders.
    Their price: prepared to go as far as war — France stands in the way (weight 83).
    Austria's design: Revanche — Their court will not rest while Russia holds Bohemia.
    Their price: prepared to go as far as an ultimatum — Russia stands in the way (weight 72).
    Russia's design: Arbiter of Europe — They stand against France's dominion over Europe (41% of
  its weight).
    Their price: prepared to go as far as war — France stands in the way (weight 88).

  Third Coalition stands against us, led by Britain — its posture is DEFENSIVE. (Threat 74, Formed.)
  What stirred Europe this turn: Natural threat decay (-3); Hegemony Passive (+1).

  Switzerland: loyalty 82, falling.
  Holland: loyalty 100, falling.
  KingdomOfItaly: loyalty 100, falling.

My counsel, Sire: Britain's war has a purpose we can price — 'The Low Countries'. We hold what their
  court wants; offer it at the table and their reason to fight goes with it. Their court is prepared
  to go as far as war.
   [cost=0  turn_advanced=False]
-- POPUP/DIALOGUE [envoy_digest] --
   {
    "turn": 16,
    "count": 1,
    "title": "A SMALL COURT WRITES",
    "lapsing_count": 1,
    "headline": "Hesse writes.",
    "deadline_note": "Answer them here. Unanswered letters lapse when the turn ends, and a court
     left waiting will not raise the matter again for some seasons.",
    "items": [
     {
      "mailbox_id": 27,
      "dialogue_id": 34,
      "from_nation": "Hesse",
      "power_tier": "minor",
      "proposal_type": "friendly_gift",
      "proposal_type_display": "Non-Aggression Pact",
      "diplomat_name": "Chancery of Hesse",
      "diplomat_line": "Hesse, wishing to go unnoticed: \"Hesse counts what a quarrel with France
     would cost and what an understanding would return, and finds the ledger unanimous. Sign the
     pact of non-aggression.\"",
      "clauses": [
       "Proposal: Non-Aggression Pact",
       "Offer: Gold payment - 150"
      ],
      "acceptance_hint": "natural willingness to negotiate",
      "state": "WAITING",
      "arrival_turn": 15
     }
    ]
   }
-- POPUP/DIALOGUE [diplomatic_dialogue] --
   {
    "type": "advisory",
    "target_nation": "",
    "talleyrand_text": "Sire \u2014 the state of Europe, plainly told.\n\n  Against Britain +
     Austria + Russia: the war favors us (+13) \u2014 10 battles across 15 turns.\n    Britain's
     design: The Low Countries \u2014 They will not suffer France's bloc in Flanders.\n    Their
     price: prepared to go as far as war \u2014 France stands in the way (weight 83).\n    Austria's
     design: Revanche \u2014 Their court will not rest while Russia holds Bohemia.\n    Their price:
     prepared to go as far as an ultimatum \u2014 Russia stands in the way (weight 72).\n
     Russia's design: Arbiter of Europe \u2014 They stand against France's dominion over Europe (41%
     of its weight).\n    Their price: prepared to go as far as war \u2014 France stands in the way
     (weight 88).\n\n  Third Coalition stands against us, led by Britain \u2014 its posture is
     DEFENSIVE. (Threat 74, Formed.)\n  What stirred Europe this turn: Natural threat decay (-3);
     Hegemony Passive (+1).\n\n  Switzerland: loyalty 82, falling.\n  Holland: loyalty 100,
     falling.\n  KingdomOfItaly: loyalty 100, falling.\n\nMy counsel, Sire: Britain's war has a
     purpose we can price \u2014 'The Low Countries'. We hold what their court wants; offer it at
     the table and their reason to fight goes with it. Their court is prepared to go as far as
     war.",
    "options": [
     {
      "label": "Satisfy their design (Britain)",
      "description": "Their court fights for 'The Low Countries' \u2014 open talks and put it on the
     table.",
      "action": "expand_options",
      "terms": {
       "target_nation": "Britain"
      }
     },
     {
      "label": "Thank you",
      "description": "Dismiss.",
      "action": "dismiss"
     }
    ],
    "context": {
     "advisory_type": "assess_situation",
     "situation_summary": "The war room assessment.",
     "wars": [
      {
       "opponent": "Britain",
       "war_score": 13,
       "trend": "stable",
       "agendas": {
        "Britain": {
         "id": "low_countries",
         "title": "The Low Countries",
         "stance_line": "They will not suffer France's bloc in Flanders."
        },
        "Austria": {
         "id": "revanche_austria",
         "title": "Revanche",
         "stance_line": "Their court will not rest while Russia holds Bohemia."
        },
        "Russia": {
         "id": "arbiter_of_europe",
         "title": "Arbiter of Europe",
         "stance_line": "They stand against France's dominion over Europe (41% of its weight)."
        }
       },
       "intents": {
        "Britain": {
         "want_id": "low_countries",
         "want_title": "The Low Countries",
         "against": "France",
         "against_display": "France",
         "weight": 83,
         "price": "fight",
         "price_display": "War",
         "summary": "prepared to go as far as war \u2014 France stands in the way (weight 83)"
        },
        "Austria": {
         "want_id": "revanche_austria",
         "want_title": "Revanche",
         "against": "Russia",
         "against_display": "Russia",
         "weight": 72,
         "price": "coerce",
         "price_display": "An ultimatum",
         "summary": "prepared to go as far as an ultimatum \u2014 Russia stands in the way (weight
     72)"
        },
        "Russia": {
         "want_id": "arbiter_of_europe",
         "want_title": "Arbiter of Europe",
         "against": "France",
         "against_display": "France",
         "weight": 88,
         "price": "fight",
         "price_display": "War",
         "summary": "prepared to go as far as war \u2014 France stands in the way (weight 88)"
        }
       }
      }
     ],
     "posture": "defensive",
     "threat_level": 74,
     "threat_tier": "Formed",
     "threat_sources": [
      {
       "source": "decay",
       "label": "Natural threat decay",
       "amount": -3
      },
      {
       "source": "hegemony_passive",
       "label": "Hegemony Passive",
       "amount": 1
      }
     ],
     "designs_in_check": [],
     "vassals": [
      {
       "vassal": "Switzerland",
       "loyalty": 82,
       "trend": "falling",
       "reason": ""
      },
      {
       "vassal": "Holland",
       "loyalty": 100,
       "trend": "falling",
       "reason": ""
      },
      {
       "vassal": "KingdomOf
-- POPUP/DIALOGUE [marshal_petition] --
   {
    "kind": "jealousy_confrontation",
    "title": "Marshal Davout seeks an audience",
    "body": "Sire, Davout has expressed reservations about the recognition afforded to Murat. He
     requests that his contributions be... noted.",
    "speaker": "Davout",
    "options": [
     {
      "id": "acknowledge",
      "label": "Acknowledge",
      "detail": "Free, and it fixes nothing: the grievance stands 2 more turns \u2014 souring his
     ties and coordination with Murat \u2014 then cools on its own.",
      "cost_note": "",
      "enabled": true
     },
     {
      "id": "promise",
      "label": "Promise Glory",
      "detail": "His patience is bought \u2014 the grievance shortens by 2 turns.",
      "cost_note": "1 AP",
      "ap_cost": 1,
      "enabled": true
     },
     {
      "id": "rebuke",
      "label": "Rebuke",
      "detail": "Trust -5. The grievance shortens by 1 turn.",
      "cost_note": "",
      "enabled": true
     }
    ],
    "context": {
     "marshal": "Davout",
     "target": "Murat",
     "escalation_level": 0
    },
    "turn": 11
   }
-- POPUP/DIALOGUE [notifications] --
   [
    {
     "id": "ad3d7e5a-d784-4f79-84ac-bd60591fa8d3",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Hesse",
     "message": "An envoy from Hesse has arrived with a proposal.",
     "turn_created": 15,
     "details": {},
     "base_title": "Envoy from Hesse",
     "repeat_count": 1
    },
    {
     "id": "823b437f-15a0-4fb9-8251-37ed3e1cd475",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Soult grows bitter (x2)",
     "message": "Marshal Soult's victories remain unrewarded (expects 200g/turn of estates; holds
     160g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente to stop
     the erosion.",
     "turn_created": 12,
     "details": {
      "marshal": "Soult",
      "expectation": 200,
      "satisfaction": 160,
      "shortfall": 40
     },
     "base_title": "Marshal Soult grows bitter",
     "repeat_count": 2
    },
    {
     "id": "ff90a7da-d536-4658-af81-bbd0a31ad89d",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Davout grows bitter (x2)",
     "message": "Marshal Davout's victories remain unrewarded (expects 300g/turn of estates; holds
     240g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente to stop
     the erosion.",
     "turn_created": 11,
     "details": {
      "marshal": "Davout",
      "expectation": 300,
      "satisfaction": 240,
      "shortfall": 60
     },
     "base_title": "Marshal Davout grows bitter",
     "repeat_count": 2
    },
    {
     "id": "ea9c2894-880f-4204-90ba-93891be05813",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Murat grows bitter (x2)",
     "message": "Marshal Murat's victories remain unrewarded (expects 300g/turn of estates; holds
     280g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente to stop
     the erosion.",
     "turn_created": 11,
     "details": {
      "marshal": "Murat",
      "expectation": 300,
      "satisfaction": 280,
      "shortfall": 20
     },
     "base_title": "Marshal Murat grows bitter",
     "repeat_count": 2
    },
    {
     "id": "11eb075a-98d7-4a9b-94f1-ee058610f860",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Bernadotte grows bitter (x2)",
     "message": "Marshal Bernadotte's victories remain unrewarded (expects 240g/turn of estates;
     holds 160g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente
     to stop the erosion.",
     "turn_created": 10,
     "details": {
      "marshal": "Bernadotte",
      "expectation": 240,
      "satisfaction": 160,
      "shortfall": 80
     },
     "base_title": "Marshal Bernadotte grows bitter",
     "repeat_count": 2
    },
    {
     "id": "36d9d8db-6539-449d-a72e-e376e20d03dc",
     "type": "counter_punch_earned",
     "priority": 1,
     "title": "Davout \u2014 free attack!",
     "message": "Davout earned a free attack from their defensive victory. Use within 2 turns or the
     opportunity expires.",
     "turn_created": 10,
     "details": {
      "marshal": "Davout"
     },
     "base_title": "Davout \u2014 free attack!",
     "repeat_count": 1
    },
    {
     "id": "552b1a44-5cbe-4a9a-a123-61707f7c98de",
     "type": "strategic_order_complete",
     "priority": 1,
     "title": "Soult arrived",
     "message": "Soult has completed their SUPPORT order \u2014 arrived at Tyrol.",
     "turn_created": 9,
     "details": {
      "marshal": "Soult",
      "order_type": "SUPPORT",
      "target": "Ney"
     },
     "base_title": "Soult arrived",
     "repeat_count": 1
    },
    {
     "id": "6e5cb538-9460-469d-8e1a-fd9ba4fe4d95",
     "type": "incoming_settlement_offer",
     "priority": 1,
     "title": "Settlement offer from Britain (x2)",
     "message": "Britain has offered terms to settle France vs Britain. Asking 629 gold.",
     "turn_created": 8,
     "details": {
      "war_id": "war_1",
      "offer_id": "settlement_offer:war_1:8:1",
      "proposer_nation": "Britain",
      "amount": 629,
      "review_target": "incoming_settlement_offer_popup"
     },
     "base_title": "Settlement offer from Britain",
     "repeat_count": 2
    },
    {
     "id": "73f91faa-7c19-4dee-befa-77e8ca2425e8",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Massena grows bitter",
     "message": "Marshal

====================================================================================================
> propose peace to Austria
====================================================================================================
Sire, regarding the Peace Treaty proposal to Austria, I have prepared terms appropriate to the
  current military situation.
   [cost=0  turn_advanced=False]
-- POPUP/DIALOGUE [envoy_digest] --
   {
    "turn": 16,
    "count": 1,
    "title": "A SMALL COURT WRITES",
    "lapsing_count": 1,
    "headline": "Hesse writes.",
    "deadline_note": "Answer them here. Unanswered letters lapse when the turn ends, and a court
     left waiting will not raise the matter again for some seasons.",
    "items": [
     {
      "mailbox_id": 27,
      "dialogue_id": 34,
      "from_nation": "Hesse",
      "power_tier": "minor",
      "proposal_type": "friendly_gift",
      "proposal_type_display": "Non-Aggression Pact",
      "diplomat_name": "Chancery of Hesse",
      "diplomat_line": "Hesse, wishing to go unnoticed: \"Hesse counts what a quarrel with France
     would cost and what an understanding would return, and finds the ledger unanimous. Sign the
     pact of non-aggression.\"",
      "clauses": [
       "Proposal: Non-Aggression Pact",
       "Offer: Gold payment - 150"
      ],
      "acceptance_hint": "natural willingness to negotiate",
      "state": "WAITING",
      "arrival_turn": 15
     }
    ]
   }
-- POPUP/DIALOGUE [diplomatic_dialogue] --
   {
    "type": "proposal_confirm",
    "target_nation": "Austria",
    "talleyrand_text": "Sire, regarding the Peace Treaty proposal to Austria, I have prepared terms
     appropriate to the current military situation.",
    "options": [
     {
      "label": "Send as suggested",
      "description": "Send the proposal with my recommended terms.",
      "action": "execute_proposal",
      "terms": {
       "type": "peace",
       "proposal_type": "peace",
       "proposer_nation": "France",
       "target_nation": "Austria",
       "sweeteners": [
        {
         "type": "gold_per_turn",
         "value": 77
        }
       ],
       "demands": [],
       "clauses": [],
       "talleyrand_commentary": "Metternich will study every clause for hidden advantage. I've kept
     the terms clean."
      }
     },
     {
      "label": "Harsher terms",
      "description": "Demand more \u2014 we can afford to push.",
      "action": "modify_harsh"
     },
     {
      "label": "More generous",
      "description": "Sweeten the offer to improve chances of acceptance.",
      "action": "modify_generous"
     },
     {
      "label": "Adjust terms",
      "description": "Build the offer step by step.",
      "action": "adjust_terms"
     },
     {
      "label": "Reconsider",
      "description": "Let me think about this.",
      "action": "reconsider"
     }
    ],
    "context": {
     "war_score": 19,
     "relation": -80,
     "threat": 74,
     "current_state": "WAR",
     "diplomat_name": "Metternich",
     "diplomat_personality": "schemer",
     "proposal_type": "peace"
    },
    "turn_created": 16,
    "blocking": false,
    "talleyrand_commentary": "Metternich will study every clause for hidden advantage. I've kept the
     terms clean.",
    "proposal_terms_summary": [
     "Peace Treaty (end state of war)",
     "France offers 77 gold/turn"
    ],
    "annotated_terms": [
     {
      "clause_type": "gold_per_turn",
      "from_nation": "France",
      "to_nation": "Austria",
      "regions": [],
      "term_direction": "concession",
      "sweetener_value": 77,
      "display_label": "France pays 77 gold per turn to Austria"
     }
    ],
    "war_context_snapshot": {
     "target_nation": "Austria",
     "current_state": "WAR",
     "proposed_state": "PEACE",
     "war_score": 19,
     "war_score_components": {
      "territory": 10,
      "battle": 19,
      "decisive_battle": 0,
      "capital": -10,
      "ticking": 0
     },
     "war_score_trend": "falling",
     "war_duration_turns": 15,
     "battles_fought": 7,
     "battles_won": 7,
     "battles_lost": 0,
     "decisive_victories": 1,
     "decisive_defeats": 1,
     "french_casualties_total": 4699,
     "enemy_casualties_total": 31086,
     "regions_held_by_france": [
      "Carniola",
      "Tyrol"
     ],
     "regions_held_by_enemy": [],
     "france_relation": -80,
     "acceptance_preview": {
      "score": 45,
      "outcome": "COUNTER",
      "outcome_display": "COUNTER expected",
      "largest_positive": "Base Disposition",
      "largest_negative": "Relation Modifier"
     },
     "harshness": 0.0,
     "harshness_label": "generous",
     "proposal_terms": {
      "type": "peace",
      "proposal_type": "peace",
      "proposer_nation": "France",
      "target_nation": "Austria",
      "sweeteners": [
       {
        "type": "gold_per_turn",
        "value": 77
       }
      ],
      "demands": [],
      "clauses": [],
      "talleyrand_commentary": "Metternich will study every clause for hidden advantage. I've kept
     the terms clean."
     },
     "annotated_terms": [
      {
       "clause_type": "gold_per_turn",
       "from_nation": "France",
       "to_nation": "Austria",
       "regions": [],
       "term_direction": "concession",
       "sweetener_value": 77,
       "display_label": "France pays 77 gold per turn to Austria"
      }
     ],
     "fallout_warnings": [],
     "commitment_conflicts": [
      {
       "conflict_type": "bloc_opposition",
       "severity": "INFO",
       "affected_entity": "Austria",
       "display": "Austria sits outside your bloc. Peace normalizes relations with a nation
     resisting your European influence.",
       "detail": {
        "hegemon": "France",
        "bloc_share": 0.41
       }
      }
     ],
     "war_objective": null,
     "settlement_tier": "white_peace",
     "settlement_tier_display": "White Peace",
     "tier_mismatch_warnings": []
    },
    "harshness": 0.0
-- POPUP/DIALOGUE [notifications] --
   [
    {
     "id": "ad3d7e5a-d784-4f79-84ac-bd60591fa8d3",
     "type": "diplomatic_proposal",
     "priority": 1,
     "title": "Envoy from Hesse",
     "message": "An envoy from Hesse has arrived with a proposal.",
     "turn_created": 15,
     "details": {},
     "base_title": "Envoy from Hesse",
     "repeat_count": 1
    },
    {
     "id": "823b437f-15a0-4fb9-8251-37ed3e1cd475",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Soult grows bitter (x2)",
     "message": "Marshal Soult's victories remain unrewarded (expects 200g/turn of estates; holds
     160g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente to stop
     the erosion.",
     "turn_created": 12,
     "details": {
      "marshal": "Soult",
      "expectation": 200,
      "satisfaction": 160,
      "shortfall": 40
     },
     "base_title": "Marshal Soult grows bitter",
     "repeat_count": 2
    },
    {
     "id": "ff90a7da-d536-4658-af81-bbd0a31ad89d",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Davout grows bitter (x2)",
     "message": "Marshal Davout's victories remain unrewarded (expects 300g/turn of estates; holds
     240g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente to stop
     the erosion.",
     "turn_created": 11,
     "details": {
      "marshal": "Davout",
      "expectation": 300,
      "satisfaction": 240,
      "shortfall": 60
     },
     "base_title": "Marshal Davout grows bitter",
     "repeat_count": 2
    },
    {
     "id": "ea9c2894-880f-4204-90ba-93891be05813",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Murat grows bitter (x2)",
     "message": "Marshal Murat's victories remain unrewarded (expects 300g/turn of estates; holds
     280g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente to stop
     the erosion.",
     "turn_created": 11,
     "details": {
      "marshal": "Murat",
      "expectation": 300,
      "satisfaction": 280,
      "shortfall": 20
     },
     "base_title": "Marshal Murat grows bitter",
     "repeat_count": 2
    },
    {
     "id": "11eb075a-98d7-4a9b-94f1-ee058610f860",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Bernadotte grows bitter (x2)",
     "message": "Marshal Bernadotte's victories remain unrewarded (expects 240g/turn of estates;
     holds 160g/turn). His loyalty is fraying \u2014 endow him with an estate or grant him a rente
     to stop the erosion.",
     "turn_created": 10,
     "details": {
      "marshal": "Bernadotte",
      "expectation": 240,
      "satisfaction": 160,
      "shortfall": 80
     },
     "base_title": "Marshal Bernadotte grows bitter",
     "repeat_count": 2
    },
    {
     "id": "36d9d8db-6539-449d-a72e-e376e20d03dc",
     "type": "counter_punch_earned",
     "priority": 1,
     "title": "Davout \u2014 free attack!",
     "message": "Davout earned a free attack from their defensive victory. Use within 2 turns or the
     opportunity expires.",
     "turn_created": 10,
     "details": {
      "marshal": "Davout"
     },
     "base_title": "Davout \u2014 free attack!",
     "repeat_count": 1
    },
    {
     "id": "552b1a44-5cbe-4a9a-a123-61707f7c98de",
     "type": "strategic_order_complete",
     "priority": 1,
     "title": "Soult arrived",
     "message": "Soult has completed their SUPPORT order \u2014 arrived at Tyrol.",
     "turn_created": 9,
     "details": {
      "marshal": "Soult",
      "order_type": "SUPPORT",
      "target": "Ney"
     },
     "base_title": "Soult arrived",
     "repeat_count": 1
    },
    {
     "id": "6e5cb538-9460-469d-8e1a-fd9ba4fe4d95",
     "type": "incoming_settlement_offer",
     "priority": 1,
     "title": "Settlement offer from Britain (x2)",
     "message": "Britain has offered terms to settle France vs Britain. Asking 629 gold.",
     "turn_created": 8,
     "details": {
      "war_id": "war_1",
      "offer_id": "settlement_offer:war_1:8:1",
      "proposer_nation": "Britain",
      "amount": 629,
      "review_target": "incoming_settlement_offer_popup"
     },
     "base_title": "Settlement offer from Britain",
     "repeat_count": 2
    },
    {
     "id": "73f91faa-7c19-4dee-befa-77e8ca2425e8",
     "type": "dotation_erosion",
     "priority": 1,
     "title": "Marshal Massena grows bitter",
     "message": "Marshal

