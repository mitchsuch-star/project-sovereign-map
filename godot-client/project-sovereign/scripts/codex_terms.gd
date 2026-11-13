extends RefCounted
class_name CodexTerms

# =============================================================================
# Session UI-5 (November 12, 2026) — the words of "Help & Keys" (data only).
# =============================================================================
# Every line below was written from the code and the docs it names, and only
# what could be confirmed there is listed (an unconfirmed term is left out,
# not guessed). Sources: docs/SYSTEMS_REFERENCE.md (§2 trust, authority,
# defiance, vindication; §3 states; §6 cavalry; §9 fog; §17 coalition; war
# exhaustion; autonomy levels), docs/DIPLOMACY_SPEC.md (§ treaty states),
# docs/DYNAMISM_SPEC.md (§3 Alarm, §4 Questions, §6 crowns), docs/NAVAL_SPEC.md
# (§4), docs/JEALOUSY_SPEC.md, docs/MARSHAL_RECRUITMENT_SPEC.md,
# backend/models/region.py (stability tiers), backend/models/world_state.py
# (supply attrition), backend/game_logic/calendar.py, backend/game_logic/
# vassal.py, backend/game_logic/diplomacy.py (OBJECTIVE_TYPE_DISPLAY),
# backend/ai/validation.py (VALID_ACTIONS), backend/ai/question_desk.py and
# the boot help in main.gd (_print_boot_help).
# Terms are sorted A to Z.

const TERMS: Array = [
	["Action points (AP)", "Your marshals' day is a pool of military actions: an order spends them, a question to Berthier is free. A marching order (march, pursue, hold) costs two, support one, garrison two, and waiting is free. Look at the counter by the End Turn button for what is left."],
	["Administrative actions", "A second, separate pool for the business of the realm: recruiting troops, building, repairing, laws, decrees and commissioning marshals. Spending one never touches the orders you can give your marshals, and the reverse."],
	["Alarm of Europe", "When another court swallows a province, the courts around it grow alarmed at the conqueror, a capital more than an ordinary province, so conquest by Europe's own courts is not free. Your own conquests raise your threat instead (see Threat)."],
	["Alliance", "The top of the treaty ladder: offensive and defensive, joint wars, the largest trade income. A nation cannot keep an alliance or defensive alliance with two courts that are at war with each other, which is how coalitions are split."],
	["Armistice", "A ceasefire between two courts at war: no combat, no trade, no entering the other's soil. It lasts at least five turns, either side may end it (back to war), and it ripens into peace only if relations have not fallen below -60."],
	["Attrition", "Armies that stand in a province beyond what it can feed lose men every turn, up to 6% of their strength. Three or more corps crowded into one province lose a further 1% per extra marshal even when they are fed, so one great ball of an army starves faster than scattered corps."],
	["Authority", "How the marshals take your measure. Always yielding to their objections costs authority (sycophancy); balanced leadership and winning against the odds raise it. Low authority emboldens defiance and shrinks what trust you earn: below 50 your trust gains are halved."],
	["Autonomy", "How much freedom a vassal keeps: Puppet, Satellite or Autonomous. The tighter the grip, the more tribute you take and the faster its loyalty drains each turn; an Autonomous vassal keeps its own marshals and its loyalty slowly mends."],
	["Blockade", "A fleet in blockade posture that is at least 1.25 times as strong as the defender's fleet shuts the blockaded court's trade: its trade income is halved. It covers every enemy at war with it at once, and the Admiralty shows who blockades whom."],
	["The Cabinet", "Talleyrand and your envoys. Every diplomatic act is made through the Cabinet and priced in diplomatic points, and Talleyrand will give counsel and assess whether a proposal is likely to be accepted before you spend a point."],
	["The calendar", "One turn is half a month, two turns a month, twenty-four a year. The date is only a label (the campaign opens on Late September 1805) and no rule reads it."],
	["Cavalry limits", "Horses cannot sit still. A cavalry corps held in a defensive stance for three turns is switched to aggressive, and one fortified for three turns is unfortified, each at a cost of 3 trust. Infantry has no such limit."],
	["Coalition", "The price of winning. As your threat in Europe climbs, courts that dislike France (relations below -10, not your vassals) gather against you: at 60 a coalition begins to brew for three turns, at 80 it is declared at once. Its weakest member, the one most worn by war, may be approached for separate terms."],
	["Crowns and recognition", "A new crown can be erected at the peace table, and a marshal may be crowned king, which costs you your best sword and leaves the marshals passed over with grievances. Legitimist courts may withhold recognition of a new crown."],
	["Declared goals (war purpose)", "The stated reason for a war: Conquest, Subjugation, Forced Alliance, Defense or Liberation. It costs no action, and it decides what the peace table may legitimately demand."],
	["Defiance", "After you insist on an order against a marshal's moderate, strong or extreme objection, he may refuse and do what his nature prefers. The chance is capped at 40%. Aggressive men attack and cautious men fortify; a Literal marshal never defies."],
	["Diplomatic points (DP)", "The Cabinet's currency. Proposals, missions and the other acts of diplomacy are priced in them, and they return each turn."],
	["The Dispatch", "The morning briefing at the start of each turn, drawn only from what your scouts and borders let you see. It can be read again from its own screen (see Keys)."],
	["Drill", "A two-turn exercise: the first turn drilling, the second locked in. The next attack the marshal makes gets +20%, once. While drilling he defends at -25%, so do not be caught at it."],
	["End of the day", "The day ends when you say so, with End Turn. Spending your very last action never ends it for you. Then Europe moves, the day becomes half a month later, and the Morning Dispatch tells what happened."],
	["Expedition", "A landing of up to 15,000 men from a friendly dockyard province, to a coastal province you cannot walk to or across a sea link an enemy fleet covers. It is a gamble: the odds of slipping through are quoted before you confirm."],
	["Fleets", "Each court's navy is one record: ships, readiness and posture (guard or blockade). New ships join with poor readiness, so a navy is made by sea-time and years, not gold alone. Fleets decide who may cross a sea link."],
	["Fog of war", "Fog filters what you are told, never what happens: combat and movement use the true board. Your own soil and the ground next to your armies are seen in part; a scouted province or a fought-over one is seen in full for two turns."],
	["Fortify", "A marshal digs in and gains a defensive bonus that grows 2% a turn to a ceiling of 12% (8% for an aggressive man). Enemy bombardment can strip it away."],
	["Garrison", "Detach 3,000 men from a marshal to hold a province you control, for two actions. A court may keep at most three garrisons, the capital's included. A capital garrison replenishes itself; a detachment does not."],
	["Glory and grievance", "Victories raise a marshal's glory, and the marshal at the head of the ladder is Crowned with Glory (+1 shock, +1 defense, +1 administration). The others grow jealous, bring petitions to you, and in the end may march on their own."],
	["Intelligence levels", "What you know of a province: Full (names, exact strength, morale), Partial (names and a strength band), Stale or Last known (an old snapshot, marked with its age) and Unknown (the province is there, nothing is known of its troops)."],
	["Le Moniteur (the Gazette)", "The periodical of the capital: a printed issue every few turns, with a back-issue archive you can page through. It tells the war, the courts and the army as the paper saw them."],
	["Marshal recruitment", "A court with a bench of candidates may commission a new marshal for his price in gold, one administrative action and a first corps of 5,000 men from the infantry pool. He arrives at the capital."],
	["Morale", "A corps's will to fight, changed by battle in both victory and defeat according to its casualties. A corps whose morale falls to 25 is forced to retreat."],
	["Objection", "A marshal weighs each order against his nature, his trust in you and the situation, and may object. You may trust his counsel, insist, or take a compromise. Trusting raises his trust; insisting lowers it, and a man at low trust objects more."],
	["Peace terms (the settlement table)", "How a war ends. Terms are drawn up with guided suggestions, not typed, and each court's willingness to accept reads the war score and its relations to you. A high war score with the enemy's capital in hand allows dictated terms."],
	["Personality", "Each marshal is Aggressive, Cautious or Literal, and it colours his combat, his objections and his defiance. Literal men follow the letter and never defy."],
	["Questions of Europe", "A Question is a named set of disputed provinces with the courts that claim them seated at it: the German, Italian, Eastern and Polish questions. A Congress, once summoned, may rule on one."],
	["Redemption", "When a marshal's trust falls to 20 or lower he asks you for an audience. One answer sets him to administrative duty, which freezes his corps and gives you one more military action for the day; recalling him costs an administrative action and brings the question back if his trust is still low."],
	["Relations", "A number between two courts, separate from the treaty between them: hostility within a state of peace is expressed by relations, not by another state. Relations decide what a court will accept."],
	["Square formation", "Infantry form square as a defence against cavalry, for one action. Breaking square afterward is free."],
	["Stability", "How settled a province is, from 0 to 100. Hostile (25 or less) yields no income, Unrest (to 50) a quarter, Settling (to 75) three quarters, and Stable the whole. Conquered soil costs upkeep to hold until it settles."],
	["Supply", "Each province feeds only so many men. Your own soil feeds an army half again as well, and so does the soil of an ally, a defensive ally or a vassal. Past the limit, attrition begins."],
	["Threat", "Europe's fear of France. Winning a battle adds to it, a decisive victory more, a captured capital 15, and declaring war 20; it fades a little every turn. High threat brings the coalition."],
	["Tribute", "The share of a vassal's income that comes to its lord: all of it from a Puppet, three quarters from a Satellite, half from an Autonomous vassal."],
	["Trust", "A marshal's confidence in you. High trust makes him object less and obey when you insist (at 80 or more, always); low trust does the reverse. At 20 or less a redemption audience is demanded."],
	["Vassal (client)", "A court bound to a lord. The lord takes tribute, and the vassal joins the lord's wars. Its loyalty rises and falls each turn; investing (1 DP and 200 gold) adds 10, and at zero the vassal rebels and goes to war with its lord."],
	["Vindication", "A marshal's track record: when events prove him right to have objected, he is bolder next time (up to 1.15 times), and proved wrong he is more timid (0.85 times)."],
	["War exhaustion", "A court's weariness with war, rising each turn at war and falling at peace; the loser of a battle takes more. It slows manpower, and a worn coalition member grows readier to negotiate."],
	["War score", "A running measure of a war from -100 to +100: battles won, provinces held and capitals taken raise it. The higher you stand, the more the peace table will bear; at 70 with the enemy's capital in hand even harsh terms can be dictated."],
]


# The order grammar and the verbs, for the ORDERS tab. [verb, example, what it does].
const ORDER_GRAMMAR: String = "An order names the marshal first, then the verb, then what it concerns: <Marshal>, <verb> <target>. The staff reads plain speech, but this form is always understood."

const ORDERS: Array = [
	["Attack", "Ney, attack Mack", "Marches on the named enemy and gives battle."],
	["Move", "Ney, move to Flanders", "One province at a time."],
	["March", "Ney, march to Vienna", "A standing order: the marshal walks the whole road over several turns. It costs two actions (the arrow shows on the map)."],
	["Pursue", "Ney, pursue Mack", "A standing order to chase an enemy marshal wherever he goes."],
	["Support", "Davout, support Ney", "A standing order to march to an ally's side. It costs one action."],
	["Hold", "Ney, hold position", "A standing order to stay put."],
	["Cancel", "cancel", "Halts a standing order. It costs one action."],
	["Scout", "Ney, scout Swabia", "Lights up a province for two turns."],
	["Defend", "Soult, defend", "Takes a defensive stance where he stands."],
	["Wait", "Ney, wait", "Does nothing, for free."],
	["Retreat", "Ney, retreat", "Falls back; a free order."],
	["Drill", "Ney, drill the troops", "Trains for a bonus on the next attack."],
	["Fortify", "Ney, dig in", "Digs in for a defensive bonus. “Unfortify” (“abandon fortifications”) takes it down."],
	["Stance", "Ney, go aggressive", "Changes the corps's stance."],
	["Form square", "Ney, form square", "Infantry against cavalry. “Break square” returns to line, free."],
	["Charge", "Murat, glorious charge!", "A cavalry charge. “Restrain Murat” holds a reckless cavalry commander back."],
	["Garrison", "garrison Paris", "Leaves 3,000 men to hold the province."],
	["Recruit", "recruit infantry at Paris", "Raises troops; an administrative action."],
	["Build", "build market in Paris", "Raises a building; an administrative action."],
	["Repair", "repair the fort", "Mends war damage or a damaged building; an administrative action."],
]

# Commands with no marshal. [command, what it does].
const BARE: Array = [
	["status", "Berthier's report of the war (“how is the war going”). Free."],
	["end turn", "Ends the day. The End Turn button (E) does the same."],
	["economy", "The treasury: income, upkeep and the breakdown (“show me the treasury”). Free."],
	["help", "The list of commands (“commands”). Free."],
	["what can I do", "Berthier names the orders the board takes today. Free."],
]

# Questions to Berthier: free, they cost no action. [question, what it answers].
const QUESTIONS: Array = [
	["what if Ney attacks Mack", "A free preview: who would march with him, before you commit."],
	["where is Kutuzov", "Where a marshal stands, as far as you can know."],
	["who am I fighting", "The wars you are in."],
	["is Paris safe", "How secure a province is."],
	["what happened last turn", "The last day's events."],
	["who holds Swabia", "Who controls a province."],
	["what is Davout doing", "A marshal's standing order and state."],
	["how many action points do I have", "Today's orders and administrative actions that remain."],
]

# The fixed keys (the remappable ones are listed from Keys.actions()). [keys, what they do].
const FIXED_KEYS: Array = [
	["Esc", "Closes the topmost screen or window; with nothing open it opens the menu, and closes it again. In the command line it first clears the suggestions, then a selected corps."],
	["Enter", "Sends the order you typed, or confirms."],
	["Alt + key", "The screen and map keys work while you type if you hold Alt: Alt+L, T, G, D, R (or B), N, E, ` (the command window), M, Home, + and -, and the idle-corps key."],
	["Tab, Shift+Tab, Down", "In the command line: Tab takes the highlighted suggestion (it never sends), Tab again walks the list, Shift+Tab walks back, and Down walks forward."],
	["Up, Down", "In the command line: your earlier orders, back and forward."],
	["Arrow keys", "Pan the map (when you are not typing)."],
	["+ and -", "Zoom the map; the keypad keys work too."],
	["1 to 8", "A ledger's tabs, when a ledger is open (Alt+1 to 8 while you type)."],
	["Ctrl+= , Ctrl+- , Ctrl+0", "Interface Scale: larger, smaller, and back to this screen's own size."],
	["?", "Opens this book, as does its key above."],
	["Double-click a province", "Centres the map on it."],
	["Mouse wheel", "Zooms the map at the cursor."],
	["Middle button drag", "Pans the map."],
	["Right click", "Dismisses a card or panel opened from the map."],
	["Click a corps, then a province", "A card shows the march before it goes."],
	["Click a corps, then an enemy", "A card shows the attack before it goes."],
	["Drag a corps", "The same card as a click: drop it on a province or an enemy."],
	["Ctrl-click several corps", "Then a province: they march together on one card."],
	["Click a standing order's arrow", "Cancel or change that order."],
]
