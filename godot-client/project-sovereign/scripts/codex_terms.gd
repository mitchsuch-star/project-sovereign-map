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
# the boot help in main.gd (_print_boot_help); the day's points, great battles
# and the Guard from backend/game_logic/battle_day.py (row BA, BA-3); the last
# hour and pursuit from backend/commands/combat_executor.py, news of a battle
# from backend/game_logic/battle_news.py and intel_surfaces.py (row BA, BA-4).
# Terms are sorted A to Z.

const TERMS: Array = [
	["Actions", "Your marshals' day is a pool of military actions: an order spends them, a question to Berthier is free. A marching order (march, pursue, hold) costs two, support one, garrison two, and waiting is free. Look at the counter by the End Turn button for what is left."],
	["Administrative actions", "A second, separate pool for the business of the realm: recruiting troops, building, repairing, laws, decrees and commissioning marshals. Spending one never touches the orders you can give your marshals, and the reverse."],
	["Alarm of Europe", "When another court swallows a province, the courts around it grow alarmed at the conqueror, a capital more than an ordinary province, so conquest by Europe's own courts is not free. Your own conquests raise your threat instead (see Threat)."],
	["Alliance", "The top of the treaty ladder: offensive and defensive, joint wars, the largest trade income. A nation cannot keep an alliance or defensive alliance with two courts that are at war with each other, which is how coalitions are split."],
	["Armistice", "A ceasefire between two courts at war: no combat, no trade, no entering the other's soil. It lasts at least five turns, either side may end it (back to war), and it ripens into peace only if relations have not fallen below -60."],
	["Attrition", "Armies that stand in a province beyond what it can feed lose men every turn, up to 6% of their strength. Three or more corps crowded into one province lose a further 1% per extra marshal even when they are fed, so one great ball of an army starves faster than scattered corps."],
	["Authority", "Your standing as Emperor, from 0 to 100, with every marshal and court. You spend it to overrule a marshal by your own word and on titles and laws; victories win it back; defeats, broken promises and always giving way to objections cost it. Nothing can be bought that would leave it under 60. At 80 or more the marshals obey more readily; below 50 they defy more and the trust you earn is halved. The crown on the top bar shows it — hover it for what each level does."],
	["Autonomy", "How much freedom a vassal keeps: Puppet, Satellite or Autonomous. The tighter the grip, the more tribute you take and the faster its loyalty drains each turn; an Autonomous vassal keeps its own marshals and its loyalty slowly mends."],
	["Berthier's reading", "On the table of a day that awaits your word, Berthier reads the enemy commander's next word as things stand: he will strike, he may strike, or he will not strike. It is the rule he follows, read at the two ends of his mood, and it says only what you could see for yourself: \"may\" is said of anything that turns on his mood, or on a corps or a state out of your sight. A clash changes the reading. Left to it, your own marshal says what he would do the same way."],
	["Blockade", "A fleet in blockade posture that is at least 1.25 times as strong as the defender's fleet shuts the blockaded court's trade: its trade income is halved. It covers every enemy at war with it at once, and the Admiralty shows who blockades whom."],
	["The Cabinet", "Talleyrand and your envoys. Every diplomatic act is made through the Cabinet and priced in diplomatic points, and Talleyrand will give counsel and assess whether a proposal is likely to be accepted before you spend a point."],
	["The calendar", "One turn is half a month, two turns a month, twenty-four a year. The date is only a label (the campaign opens on Late September 1805) and no rule reads it."],
	["Cavalry limits", "Horses cannot sit still. A cavalry corps held in a defensive stance for three turns is switched to aggressive, and one fortified for three turns is unfortified, each at a cost of 3 trust. Infantry has no such limit."],
	["Coalition", "The price of winning. As your threat in Europe climbs, courts that dislike France (relations below -10, not your vassals) gather against you: at 60 a coalition begins to brew for three turns, at 80 it is declared at once. Its weakest member, the one most worn by war, may be approached for separate terms."],
	["Crowns and recognition", "A new crown can be erected at the peace table, and a marshal may be crowned king, which costs you your best sword and leaves the marshals passed over with grievances. Legitimist courts may withhold recognition of a new crown."],
	["The day's points", "When a pitched battle — 50,000 men or more engaged, both sides together — does not decide the day, the day stays open and each side holds points for the rest of it: two, or three under a commander of high command (8 or more). You and the enemy speak in turns, and the side that did not open the battle speaks first. A word is an order you already know, and it costs points, never an action: the lead presses, another corps leads, the guns open, a corps is brought up or the lead digs in for one point; the Guard for two. To stand, to break off, to fall back or to leave the rest of the day to your marshal costs nothing. The table offers to bring up a corps only where a written order would bring him to this field; a support order for any other corps is an ordinary order, at an action, and the day keeps its points. The enemy answers by his own temper. Two silences in a row, both purses empty or a side leaving the field, and night falls. Say nothing and your corps has stood: he plays what he has left as your turn ends. On the battle table the day's stakes head the words — each purse in pips and in figures, his temper, his road and Berthier's reading of what he will do (see Berthier's reading) — the digits 1 to 9 give the words, and every word says under its name what it costs and what it does: a press its odds and the men on each side, to dig in what the stance is worth to that marshal, an exit that it is free and what it ends. A line that breaks decides the day at once; a day no clash decides drives nobody off, and the fight may be renewed the next turn. A lead holds one day at a time: a second pitched battle he fights while it is open is a single clash. If he wins it and advances he has left his first field, and that day ends where it stands. However a day ends, its clashes and its toll are told in one line, and a day the night closes is told in the morning."],
	["Declared goals (war purpose)", "The stated reason for a war: Conquest, Subjugation, Forced Alliance, Defense or Liberation. It costs no action, and it decides what the peace table may legitimately demand."],
	["Defiance", "After you insist on an order against a marshal's moderate, strong or extreme objection, he may refuse and do what his nature prefers. The chance is capped at 40%. Aggressive men attack and cautious men fortify; a Literal marshal never defies."],
	["Diplomatic points (DP)", "The Cabinet's currency. Proposals, missions and the other acts of diplomacy are priced in them, and they return each turn."],
	["The Dispatch", "The morning briefing at the start of each turn, drawn only from what your scouts and borders let you see. It can be read again from its own screen (see Keys)."],
	["Drill", "A two-turn exercise: the first turn drilling, the second locked in. The next attack the marshal makes gets +20%, once. While drilling he defends at -25%, so do not be caught at it."],
	["End of the day", "The day ends when you say so, with End Turn. Spending your very last action never ends it for you. Then Europe moves, the day becomes half a month later, and the Morning Dispatch tells what happened."],
	["Ending a war", "Press Make peace on the war's card at the top right of the map, or open the Cabinet, choose the court and look under END THE WAR. The peace table opens. THIS DEAL says in plain words what you get, what you give and what you keep, and each court's row says whether it will sign and, if not, why. Offer them more and Ask for more change the deal; Review and sign shows it once more. Nothing is sent until you sign, and a court you leave out stays at war."],
	["The enemy's moves", "What the other courts did when you ended the turn. First the map shows it: the armies you can see march to where they went, then the provinces that changed hands take their new colour, with a caption on the ones that are your business. Click, or press any key, to skip it; the switch Show the enemy's moves on the map, under Orders in Settings, turns it off. Then the report opens. It begins with what changed for you:the provinces you or your allies lost or gained and how (an army marched in and nobody held it, a battle, a siege), your battles, and the enemy armies now next to you. Those provinces flash on the map when you close it. Everything else the other courts did is folded underneath."],
	["Expedition", "A landing of up to 15,000 men from a friendly dockyard province, to a coastal province you cannot walk to or across a sea link an enemy fleet covers. It is a gamble: the odds of slipping through are quoted before you confirm."],
	["Fleets", "Each court's navy is one record: ships, readiness and posture (guard or blockade). New ships join with poor readiness, so a navy is made by sea-time and years, not gold alone. Fleets decide who may cross a sea link."],
	["Fog of war", "Fog filters what you are told, never what happens: combat and movement use the true board. Your own soil and the ground next to your armies are seen in part; a province you scouted, or one you fought in, is seen in full for two turns. A battle between other crowns shows you nothing of its province (see News of a battle)."],
	["Fortify", "A marshal digs in and gains a defensive bonus that grows 2% a turn to a ceiling of 12% (8% for an aggressive man). Enemy bombardment can strip it away."],
	["Garrison", "Detach 3,000 men from a marshal to hold a province you control, for two actions. A court may keep at most three garrisons, the capital's included. A capital garrison replenishes itself; a detachment does not."],
	["Glory and grievance", "Victories raise a marshal's glory, and the marshal at the head of the ladder is Crowned with Glory (+1 shock, +1 defense, +1 administration). The others grow jealous, bring petitions to you, and in the end may march on their own."],
	["Great battle", "A battle with 80,000 men or more engaged, both sides together: its name says so, and news of it reaches every court. Any pitched battle of 50,000 men or more that does not decide the day is fought on in turns (see The day's points); a smaller battle is one clash, as ever."],
	["The Guard", "In a day of battle the Emperor's own attack is the Guard going in, for two points. As it goes in, the enemy's lead loses 10 morale. If it is thrown back, every corps of yours that fought loses 10."],
	["Intelligence levels", "What you know of a province: Full (names, exact strength, morale), Partial (names and a strength band), Stale or Last known (an old snapshot, marked with its age) and Unknown (the province is there, nothing is known of its troops)."],
	["Keeping a province", "A province with nobody in it can be walked back into by any enemy army: that is how a province you took can be lost again without a battle. Leave a corps in it, or post a garrison there (see Garrison), to hold it."],
	["The last hour", "A corps that marches to a battle rolls to arrive in time. A roll won by five points or fewer brings it up at the last hour, with three-quarters of its weight in the fighting; this holds for both sides. The muster shows each corps's chance of arriving and counts a last-hour arrival in the figures it prints."],
	["Le Moniteur (the Gazette)", "The periodical of the capital: a printed issue every few turns, with a back-issue archive you can page through. It tells the war, the courts and the army as the paper saw them."],
	["Marshal recruitment", "A court with a bench of candidates may commission a new marshal for his price in gold, one administrative action and a first corps of 5,000 men from the infantry pool. He arrives at the capital."],
	["Morale", "A corps's will to fight, changed by battle in both victory and defeat according to its casualties. A corps whose morale falls to 25 is forced to retreat."],
	["News of a battle", "A battle shows you its province in full only when you fought in it or it was fought on your own soil. A great battle between other crowns, or an ally's battle in a war you share, reaches you as news instead: the crowns, the province and how the day ended — a great battle's two commanders by name — and never a figure. Le Moniteur prints it, and a great one forces a special edition."],
	["Objection", "A marshal weighs each order against his nature, his trust in you and the situation, and may object. You may trust his counsel, insist, or take a compromise. Trusting raises his trust; insisting lowers it, and a man at low trust objects more."],
	["Peace terms (the settlement table)", "How a war ends. Terms are drawn up with guided suggestions, not typed, and each court's willingness to accept reads the war score and its relations to you. A high war score with the enemy's capital in hand allows dictated terms."],
	["Personality", "Each marshal is Aggressive, Cautious or Literal, and it colours his combat, his objections and his defiance. Literal men follow the letter and never defy."],
	["Pursuit", "When a beaten enemy is driven from the field, a commander with a gift for pursuit rides him down for more casualties: Murat's cavalry takes 5,000. The lead pursues if the gift is his own; if it is not, the best among the corps that fought beside him does. One pursuit is made, never two, and a master of the rearguard such as Kutuzov halves it."],
	["Questions of Europe", "A Question is a named set of disputed provinces with the courts that claim them seated at it: the German, Italian, Eastern and Polish questions. A Congress, once summoned, may rule on one."],
	["Redemption", "When a marshal's trust falls to 20 or lower he asks you for an audience. One answer sets him to administrative duty, which freezes his corps and gives you one more military action for the day; recalling him costs an administrative action and brings the question back if his trust is still low."],
	["Relations", "A number between two courts, separate from the treaty between them: hostility within a state of peace is expressed by relations, not by another state. Relations decide what a court will accept."],
	["Separate peace", "A peace with one court while its partners fight on: in the Cabinet, Offer peace to that court alone; at the peace table, leave the others out. Your other wars go on."],
	["Square formation", "Infantry form square as a defence against cavalry, for one action. Breaking square afterward is free."],
	["Stability", "How settled a province is, from 0 to 100. Hostile (25 or less) yields no income, Unrest (to 50) a quarter, Settling (to 75) three quarters, and Stable the whole. Conquered soil costs upkeep to hold until it settles."],
	["Supply", "Each province feeds only so many men. Your own soil feeds an army half again as well, and so does the soil of an ally, a defensive ally or a vassal. Past the limit, attrition begins."],
	["Take back", "A slipped order can be taken back: press Take back on the map's controls, press Ctrl+Z, or type undo. The board is put back as it stood and the actions are yours again. It works until the order shows you something new, starts a fight, raises a question or the turn ends — after that it stands. Several orders can be taken back one after another."],
	["Taking a province", "A corps takes an enemy province by walking in only when nothing holds it: no enemy corps, no garrison that fights, no fortification. On the enemy's home soil the corps must also have at least 5,000 men, and a corps still rallying from a rout takes nothing. Before you send him, the tag by the cursor says what will happen: takes the province, or enters only and why. A corps already standing there has a Take button on his card: it storms a garrison, or lays siege to a fortified province, which falls when the turn ends if he still stands there."],
	["Threat", "Europe's fear of France. Winning a battle adds to it, a decisive victory more, a captured capital 15, and declaring war 20; it fades a little every turn. High threat brings the coalition."],
	["Tribute", "The share of a vassal's income that comes to its lord: all of it from a Puppet, three quarters from a Satellite, half from an Autonomous vassal."],
	["Trust", "A marshal's confidence in you. High trust makes him object less and obey when you insist (at 80 or more, always); low trust does the reverse. At 20 or less a redemption audience is demanded."],
	["Vassal (client)", "A court bound to a lord. The lord takes tribute, and the vassal joins the lord's wars. Its loyalty rises and falls each turn; investing (1 DP and 200 gold) adds 10, and at zero the vassal rebels and goes to war with its lord."],
	["Vindication", "A marshal's track record: when events prove him right to have objected, he is bolder next time (up to 1.15 times), and proved wrong he is more timid (0.85 times)."],
	["War exhaustion", "A court's weariness with war, rising each turn at war and falling at peace; the loser of a battle takes more. It slows manpower, and a worn coalition member grows readier to negotiate."],
	["War score", "A running measure of a war from -100 to +100: battles won, provinces held and capitals taken raise it. The higher you stand, the more the peace table will bear; at 70 with the enemy's capital in hand even harsh terms can be dictated."],
	["What told", "Under the headline of a battle your marshal led, the table names the one thing that weighed most for the side that did better, by a fixed rule: numbers, when the men committed stood 5 to 4 or better; else the largest named advantage of 10 points or more in the battle's own report (the ground, works, a dug-in line, the guns); else the dice, when the throw stood 3 or more from seven; else it was an even fight. Each clash of a day of battle says it in its own line, and the clash that decides a day is named. The dice on the table are the attacker's throw: the table names him."],
	["White peace", "A peace with no terms: nobody pays and nothing is demanded. Who keeps which occupied province is listed on the peace table, under THIS DEAL, before you sign."],
]


# The order grammar and the verbs, for the ORDERS tab. [verb, example, what it does].
const ORDER_GRAMMAR: String = "An order names the marshal first, then the verb, then what it concerns: <Marshal>, <verb> <target>. The staff reads plain speech, but this form is always understood."

const ORDERS: Array = [
	["Attack", "Ney, attack Mack", "Marches on the named enemy and gives battle."],
	["Move", "Ney, move to Flanders", "To a province within his reach: one action, and he arrives now. On the map, select him and click the province."],
	["March", "Ney, march to Vienna", "For a province further off: a standing order, the marshal walks the whole road over several turns. It costs two actions (the arrow shows on the map)."],
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
	["Right click", "With a corps selected, his order, as a left click gives it: a province sends him, an enemy is attacked, another of your corps is supported. With none selected, it selects the corps under it, or dismisses a card or panel opened from the map."],
	["Click a corps, then a province", "He is sent at once: the tag by the cursor has already said the price, when he arrives and what will happen there. A card asks first only where it matters: a province he would enter without taking, or a road that meets an enemy. Settings, Orders, Ask before every order brings the card back for every order."],
	["Click a stack's label", "Where several corps stand together the label reads a name and how many more: click it for a list, and pick the corps you mean."],
	["Click a corps, then an enemy", "A card shows the attack before it goes."],
	["Click another of your corps", "Selects him instead (support him with a right click or a drag)."],
	["1 to 7, with a corps selected", "His card's orders on an empty line: Hold, Fortify (or Unfortify), Drill, Scout, Fall back, Garrison, Cancel order. A locked one only sounds; its reason is the button's hover."],
	["Drag a corps", "The same as a click: drop it on a province, an enemy, or another of your corps to support him."],
	["Ctrl-click several corps", "Then a province: they march together on one card."],
	["Click a standing order's arrow", "Cancel or change that order."],
]
