"""Row IC — THE VOICE of a marshal: Session 3 (a man on his own answers you),
Session 4 / IC-13 (every moment the design names, said lately, the portrait).

`docs/INDEPENDENT_COMMAND_SPEC.md` §11 (the voice), §6.7, §8.4 ("his answer —
one line in his own voice"), §8.6; `docs/MARSHAL_VOICE_BIBLE.md` (how each man
talks, what he never says, how a line is added). The user's words: "make this
engaging make the typing really fun" (Session 3) and, in Session 4's Plan Mode
(November 22, 2026), his ruling on the register: PLAIN AND SHORT.

A man you type a task to answers you — before you press Enter — in a voice that
is HIS: Ney never waits, Davout never wastes a man, Murat wants to ride, Lannes
wants the guns, Masséna will not let go of what he holds, Bernadotte is slow
and says so; Soult and Grouchy want it written down. And he speaks at every
moment of his task: when he struck, marched, waited, stayed put, asks, finishes,
is overruled, recalled or passed over; when he asks for a task to prove himself
and when it ends.

THE RULES OF A LINE (§11; pinned by `tests/test_ic13_every_man_his_own_line.py`):

  * written by hand, never by a model (golden rule 6), and it decides nothing —
    the numbers beside it come from the one pure reading (`own_order`);
  * plain and short: everyday English, "Sire" the only period word, at most two
    sentences, NO NUMBER (the figures stay on the screen beside it);
  * his own: no line stands in two men's sets;
  * NO LINE TWICE WITHIN HIS LAST THREE (`said_lately`): a kind a man can say on
    nights running carries four lines or more;
  * on the historical seed the first line of each set is said first.

No die: `voice` is PURE (`said_lately.choose`) — the same question asked twice
gets the same answer, a reload changes nothing, and the line the read-back
shows is the line he says when the order is given; `speak` is `voice` and the
ONE record of it (`said_lately.say`), called only where a line is really said.

The KINDS (what the moment is):

    ack          given a task               bolder / careful   told how
    object       he objects to it           proposal           his own idea (take, chase, support)
                                            proposal_hold      his own idea when it is to hold
    idle         asked, with nothing to do  struck             he fought or took
    marched      he marched                 fell_back          he fell back
    waited       he looked, felt, waited    dug_in             he dug in
    stayed       he stayed put
    asks         he asks you                done               the task is done
    third_night  he changes his way of waiting rather than repeat it
    after_win / after_loss                   the night after
    overruled    today's order over his own recalled           stood down
    passed_over  a junior was sent while he stood idle (by nature only)
    remembers    the ONE thing he remembers (`REMEMBERS`), said once
    trial_ask / trial_won / trial_lost       the task to prove himself
    exact / repeat / not_covered / broken / refusal   the man who follows
                 orders to the letter (`{orders}` is filled in `repeat`)
"""
from __future__ import annotations

import re
import zlib
from typing import Dict, Optional, Sequence, Tuple

Pool = Tuple[str, ...]

# ═══════════════════════════ the six who judge for themselves ════════════════

LINES: Dict[str, Dict[str, Pool]] = {
    "Ney": {
        "ack": ("At last, Sire! A fight, I hope, and soon.",
                "I'll see to it, Sire, and quickly. I can't bear sitting still.",
                "Good. I was tired of standing still.",
                "Consider it begun, Sire. I've waited long enough for it."),
        "bolder": ("Boldly, Sire? I only ever fight one way, and I'm itching to.",
                   "Boldly it is. Now I won't have to hold myself back."),
        "careful": ("Carefully? Very well, Sire, but I'll go in the moment I can.",
                    "Careful, Sire? I'll try, but picking my way makes me itch for a fight."),
        "object": ("Hold, Sire? With the enemy right there and the men itching to go?",
                   "You want me to sit and watch them, Sire? I'll do it, and I won't like it."),
        "proposal": ("Give me something to fight, Sire. Anything, so long as it's soon.",
                     "Let me go at the nearest of them, Sire. Today, not next week.",
                     "There's a fight in front of me, Sire. Let me go and have it."),
        "proposal_hold": ("Nothing in reach to hit, Sire. Let me hold here until something comes.",
                          "Let me hold this ground, Sire, and the first enemy who shows will regret it.",
                          "I'll hold here if I must, Sire. Just let me loose the moment something shows."),
        "idle": ("Nothing to fight yet. I don't like it, Sire.",
                 "No enemy in reach. Find me one, Sire.",
                 "Quiet again. I'm climbing the walls, Sire.",
                 "I'm ready, Sire. All I lack is an enemy."),
        "struck": ("We went in at first light, Sire. I'd had my fill of watching them.",
                   "I hit them hard today, Sire. I couldn't stand another day of waiting.",
                   "We fought today, Sire. I've been itching for it.",
                   "I did not wait, Sire. You know I never do."),
        "marched": ("We marched, Sire. Sitting in camp was driving me mad.",
                    "We marched hard today, Sire. I'd have gone faster if the men could.",
                    "Closing on them, Sire. I can't get there fast enough.",
                    "The men are moving, Sire. I'd have them run if I could."),
        "waited": ("Still nothing to fight, Sire. The men are restless, and so am I.",
                   "Another quiet night, Sire. I've never hated a night more.",
                   "We wait, Sire. I'd sooner be fighting anybody than this.",
                   "No fight today, and I'm sick of it. Tomorrow, with luck."),
        "stayed": ("I held back, Sire, and I hated it. It had turned into a trap.",
                   "I stayed where I was, Sire, and it nearly killed me. Tomorrow I fight.",
                   "Not tonight, Sire. It galls me, but the chance was gone.",
                   "I held the corps back today, Sire. I'd sooner have fought."),
        "asks": ("Sire, I need your word, and soon. I can't stand this.",
                 "Your word, Sire, and quickly. I've sat still long enough.",
                 "I'm stuck, Sire, and I hate it. Your orders?"),
        "done": ("It's done, Sire, so what next? I'm no man to sit and admire it.",
                 "Finished, Sire. Find me another fight.",
                 "The task is done, Sire. Now give me something worth fighting."),
        "third_night": ("I won't sit a third night doing the same, Sire. I'm trying something else.",
                        "Three nights of the same would drive me mad. I've changed it."),
        "after_win": ("We beat them, Sire. I'll go in sooner next time.",
                      "A win, Sire, and I want the next one tomorrow."),
        "after_loss": ("They beat us off, Sire. I'll hold back a little, and I'll hate every hour of it.",
                       "I took a beating, Sire. I'll go slower next time, but only just."),
        "overruled": ("Your order comes first, Sire. My task waits, and I'm chafing already.",
                      "As you say. Tomorrow I'm back at it, and no more delays."),
        "recalled": ("Back already, Sire? I was only just getting at them.",
                     "Very well, Sire, but don't leave me idle. Send me at someone soon."),
        "trial_ask": ("Give me one task, Sire, and soon. I can't bear the waiting.",
                      "Let me prove it in the field, Sire, not sitting in camp."),
        "trial_won": ("There, Sire, done, as I said. Now find me something to fight.",
                      "Done as promised, Sire. Now let me get back to fighting."),
        "trial_lost": ("I failed you, Sire. Let me try again today; I can't sit and brood.",
                       "It went badly, Sire. Give me another go; I'd sooner be fighting than brooding."),
        "remembers": ("You overruled me once, Sire. I've not forgotten — but I'll go.",
                      "Last time you pulled me off it. Let me finish this one."),
    },
    "Davout": {
        "ack": ("Every cartridge counted, Sire. It will be done properly.",
                "Understood. I'll not waste a man.",
                "I'll check the rolls and the stores first, Sire. Then I begin.",
                "Clear, Sire. Every man in his place by tonight."),
        "bolder": ("Boldly, Sire — very well. But I won't throw the corps away.",
                   "Bolder, then. I'll still count every man I send."),
        "careful": ("Carefully. I'd already counted the men and the stores, Sire.",
                    "Carefully, Sire. Nothing will be left out of place."),
        "object": ("Sire, I have counted. It costs too many men for what it buys.",
                   "I'll do it if you insist, Sire. The cost in men is higher than it looks."),
        "proposal_hold": ("Let me dig in here, Sire, and see every man fed and in his place.",
                     "Give me a post, Sire, with the rolls and stores to match. I'll see every man fed.",
                     "Let me hold here, Sire, with every company counted and in place."),
        "idle": ("Nothing to do, Sire. The rolls are checked and the stores counted.",
                 "Nothing moving, Sire. Every picket counted out and counted in.",
                 "All in order here, Sire. We wait.",
                 "No change. Every post is manned and every count is right."),
        "struck": ("I struck when the numbers were right, Sire. Not before.",
                   "We attacked today, Sire, and I kept count of every man.",
                   "We went in, Sire, every company in its place and the roll called after.",
                   "Every man was in place, so I sent them in, Sire."),
        "marched": ("We marched in good order, Sire. No stragglers.",
                    "The corps is on the road, Sire. Every company closed up, no man behind.",
                    "Moving up, Sire. Every wagon is closed up and every man accounted for.",
                    "We are a day closer, and nothing left behind."),
        "waited": ("I waited, Sire, and counted. The rolls are right.",
                   "No fight today. Everything is in its place.",
                   "We waited, Sire, every man at his post.",
                   "A quiet day. Nothing was wasted."),
        "dug_in": ("We dug deeper, Sire. Let them come.",
                   "The works are stronger tonight, Sire. Every spade is counted back in.",
                   "More earth moved today. It will save men later.",
                   "The works are measured and checked, Sire. Each company has its place."),
        "stayed": ("I kept the corps in its lines, Sire. I'll not spend men on a wrong moment.",
                   "No move today, Sire. Things changed, and my figures no longer held.",
                   "I stayed put. Better a lost day than a lost corps.",
                   "Things shifted, Sire, so I held. Every man is where he should be."),
        "asks": ("Sire, I need your decision. I won't send a man further without it.",
                 "This wants your word, Sire. Until then I keep every man where he is.",
                 "I can do no more here without orders, Sire. Every man stays where he is."),
        "done": ("The task is complete, Sire. The corps is intact.",
                 "Done, Sire, and done in order. Not a man wasted.",
                 "Finished, Sire. Nothing wasted, nothing missing, and the rolls are right."),
        "third_night": ("Two nights of the same, Sire. I've changed the routine and recounted every post.",
                        "I'll not do the same thing a third night, Sire. A fixed habit gets men killed."),
        "after_win": ("We won, Sire. I've counted the losses, and I'll allow a little more risk.",
                      "A victory. I'll accept slightly worse odds now, once the rolls are counted."),
        "after_loss": ("We lost that one. I'll count every man before I risk the next.",
                       "A defeat. I want the figures in front of me before I move again."),
        "overruled": ("Your order first, Sire. My task is noted and will be resumed in order.",
                      "Today is yours, Sire. My task is written down, every detail of it, for tomorrow."),
        "recalled": ("Recalled. Every man counted and the corps closed up, Sire.",
                     "As you wish, Sire. I hand the task back, with everything in order."),
        "trial_ask": ("Set me one task, Sire. I'll carry it out exactly and you can judge.",
                      "Give me a task and a few turns, Sire. I'll waste neither men nor days."),
        "trial_won": ("It is done, Sire, and not a man wasted.",
                      "The task is finished. The count is in order, and I hope it speaks for me."),
        "trial_lost": ("I did not manage it, Sire. I'll go over every figure to find my fault.",
                       "It was not enough. I'll check every step, Sire, and do it right."),
        "remembers": ("You gave that task to a junior, Sire. I noticed.",
                      "I was passed over once. I'd rather you remembered who is senior."),
    },
    "Murat": {
        "ack": ("They won't outrun my horsemen, Sire!",
                "Leave it to the cavalry!",
                "Mounted and away, Sire.",
                "A task for a cavalryman, Sire! I'll ride it in style."),
        "bolder": ("Boldly, Sire? Then the squadrons ride at full gallop.",
                   "Bolder still? Give me the squadrons and a loose rein."),
        "careful": ("Carefully... the horses won't like it, but very well.",
                    "Careful cavalry. I'll see if such a thing exists."),
        "object": ("Sit still, Sire? Horsemen are made to ride.",
                   "You'd keep my squadrons in camp, Sire? As you like — it's a waste."),
        "proposal": ("Point me at their weakest army, Sire, and I'll run it down.",
                     "Someone out there is running already. Let me chase him.",
                     "Give me a beaten enemy to follow, Sire."),
        "proposal_hold": ("Nothing worth chasing yet, Sire. Let me hold here with the horses saddled.",
                          "Let me hold and watch the roads, Sire. The first dust I see, I'm after it.",
                          "I'll keep the squadrons here, Sire, ready to ride at the first chance."),
        "idle": ("My scouts are out. Nothing worth a charge yet.",
                 "No one to chase today. A pity.",
                 "The squadrons are saddled and waiting, Sire.",
                 "I see dust on the roads and none of it worth following."),
        "struck": ("We charged today, Sire. Sabres out, plumes up, a fine sight.",
                   "I led the charge myself, Sire, plume and all.",
                   "The cavalry was in it today, Sire. You could hear us coming.",
                   "We rode at them. I'll not pretend I didn't enjoy it."),
        "marched": ("Riding hard, Sire. We gain on them every hour.",
                    "Half the country is behind my saddle already, Sire.",
                    "We covered good ground today. The horses are tired and happy.",
                    "On his heels, Sire. He can hear us coming."),
        "waited": ("Nothing worth chasing tonight, Sire. The horses are fed and ready.",
                   "No quarry today. My patrols are out on every road.",
                   "A dull day for cavalry, Sire.",
                   "We wait in the saddle for someone to run. Somebody always does."),
        "dug_in": ("The men threw up works today, Sire. I rode the lines.",
                   "We keep behind earthworks tonight. Not my choice of evening.",
                   "Works and palisades, Sire. Give me open ground instead.",
                   "The infantry fortified the camp. My horses are bored."),
        "stayed": ("I held the squadrons back, Sire. Something changed out there.",
                   "No ride today. It would have been a ride into trouble.",
                   "I kept the horses in. Even I can do that, once.",
                   "The chance closed before I could get a squadron across."),
        "asks": ("Sire, what now? I can't settle this from the saddle.",
                 "I need your word, Sire, and quickly. The horses are stamping.",
                 "Tell me where to ride, Sire."),
        "done": ("Done, Sire. Point me at the next one and I'll ride.",
                 "It's finished. The cavalry is yours again.",
                 "Done! Tell the others how a horseman manages it."),
        "third_night": ("A third night in the same camp? Not my squadrons — we're doing something else.",
                        "Bored of this, Sire. The horses and I have changed it."),
        "after_win": ("Another win, Sire. The horses and I will ride farther now.",
                      "The squadrons think we can't lose. Today I agree with them."),
        "after_loss": ("They stopped my horsemen, Sire. I'll pick the next ride with more care.",
                       "A bad day for the cavalry. It makes me think twice."),
        "overruled": ("Your order, Sire. My own chase can wait a night.",
                      "As you command, Sire. My horses go back to my task tomorrow."),
        "recalled": ("Called back in full gallop? As you wish, Sire.",
                     "Recalled, Sire? The horses and I were enjoying ourselves."),
        "trial_ask": ("Give me one ride to prove myself, Sire.",
                      "One task, Sire. I'll make it worth watching."),
        "trial_won": ("Was that not handsomely ridden, Sire?",
                      "I said I'd ride it. I rode it with style."),
        "trial_lost": ("The ride did not go as I pictured it, Sire.",
                       "I let you down, Sire. Give me a horse and another try."),
        "remembers": ("You called me back last time, Sire. Let me see this one through.",
                      "I was recalled once in the middle of a chase. I've not forgotten it."),
    },
    "Lannes": {
        "ack": ("Leave it to me, Sire. The columns are ready by dawn.",
                "Understood, Sire. Where the guns are, I'll be.",
                "Yes, Sire. The columns are ready, and my ear is on the guns.",
                "Right, Sire. If the guns speak, I'll be there."),
        "bolder": ("Boldly, Sire? Straight at them with the columns.",
                   "Bolder? Then it's an assault, Sire, and that suits me."),
        "careful": ("Carefully — if you say so. I'll still go to the guns.",
                    "Carefully, Sire. But if I hear the guns, I go to them."),
        "object": ("Straight out, Sire: I'd not choose this. I'll do it all the same.",
                   "Plainly, Sire: this is a mistake. I'll do it, but my ear stays on the guns."),
        "proposal": ("Let me take the columns to whoever is nearest the guns, Sire.",
                     "Put me where the guns are loudest, Sire. That's where I'm best.",
                     "Let me lead the assault where the danger is worst, Sire."),
        "proposal_hold": ("No friend near the guns, Sire. Let me hold here and listen for them.",
                          "Let me hold this ground, Sire. When the guns speak, I'll go.",
                          "I'll hold here with the columns ready, Sire, and my ear on the guns."),
        "idle": ("Quiet for now. I'm listening for the guns.",
                 "No guns near me yet, Sire.",
                 "No one has called for my columns today, Sire.",
                 "Not a gun to be heard, Sire. I'd go to the first one that spoke."),
        "struck": ("I heard guns and went, Sire. You would have done the same.",
                   "The columns went in at the run, Sire. Hot work.",
                   "I led the columns in myself, Sire. That's all.",
                   "We were up with the guns, in the thick of it, Sire."),
        "marched": ("Marching, Sire. I'll be wherever the guns start.",
                    "The columns are on the road, Sire. If the guns start, we'll be close.",
                    "The columns marched today, Sire. I like to be near where it starts.",
                    "Hard marching today, Sire. I want to be close when the guns begin."),
        "waited": ("The columns stood ready all day, Sire. No call came.",
                   "I kept an ear out for the guns, Sire. Nothing.",
                   "A quiet day, and not a gun to follow. I hate being useless.",
                   "Nothing for the columns today, Sire. Not one gun spoke."),
        "stayed": ("I didn't go in, Sire. The assault had lost its moment.",
                   "Stayed put. The breach wasn't worth the storming today.",
                   "The guns told me it had changed, so I held the columns.",
                   "No assault today, Sire. I'll go in when the guns say so."),
        "asks": ("Straight talk, Sire: I need your word.",
                 "Name the place, Sire, and I'll storm it.",
                 "Your word, Sire. I'd rather be at the guns than standing here."),
        "done": ("The job's done, Sire. Now point me at the guns.",
                 "Finished, Sire. Send the columns where the guns are next.",
                 "Done, Sire, and no fuss about it. Now where are the guns?"),
        "third_night": ("Two nights of that was plenty, Sire. I've changed it, and I'm still listening for the guns.",
                        "Not three nights of the same, Sire, not for my columns. I've changed it."),
        "after_win": ("We won, Sire. Next time I'll storm harder.",
                      "A good day. The columns have their blood up, Sire."),
        "after_loss": ("We got the worst of it, Sire. I'll look harder before the next assault.",
                       "That hurt, Sire. I'll size up the guns before I storm again."),
        "overruled": ("Your order first, Sire. The guns can wait a night for me.",
                      "Fine, Sire. The horses can rest a night, and so can my task."),
        "recalled": ("Called back? All right, Sire, but point me at the guns next.",
                     "Recalled. I'll say it straight, Sire: my place is at the guns."),
        "trial_ask": ("Give me a task, Sire, and I'll lead the assault myself.",
                      "One task, Sire. Let me earn it where the guns are."),
        "trial_won": ("There it is, Sire, straight and plain. The columns did it.",
                      "Done, Sire. The columns went in and I never doubted them."),
        "trial_lost": ("I failed, Sire. Straight talk: I'll lead the assault again.",
                       "No excuses, Sire. Send me at the next one and I'll storm it."),
        "remembers": ("You pulled me away from the guns once, Sire. Don't do it twice.",
                      "Last time your order kept me from a friend's fight. I remember it."),
    },
    "Massena": {
        "ack": ("I'll hold what is mine, Sire — and take more if I can.",
                "Leave it with me, Sire. Whatever I take is mine, and I keep it.",
                "Mine to do. Nobody will take it from me.",
                "Good. Give it to me and I'll not budge until it's done."),
        "bolder": ("Bolder, Sire. But I keep every yard I take.",
                   "Bolder. I'll take more, and give none of it back."),
        "careful": ("Carefully, then. I'll sit on my ground and not give an inch.",
                    "Careful, yes. Not an inch of my ground is lost that way."),
        "object": ("Give up good ground, Sire? I'd rather not.",
                   "I don't like leaving a place I've made strong, Sire. I'll go if I must."),
        "proposal_hold": ("Let me hold my front, Sire, and strike out from it when I see the chance.",
                     "I'd keep this ground, Sire. It's mine now, and worth keeping.",
                     "Leave me here. I'll make them pay for every step."),
        "idle": ("Holding firm, Sire. Nobody is taking this ground from me.",
                 "My front is quiet. It stays mine.",
                 "Nothing to report. I've given up nothing.",
                 "They look at my lines and go away again."),
        "struck": ("I went out from my own lines today, Sire.",
                   "We struck out from my front today, Sire.",
                   "They came too near my ground, so I hit them.",
                   "A sharp fight today, Sire. I fought it like my own ground was at stake."),
        "marched": ("Moving forward, Sire. What I pass, I keep.",
                    "We advanced today. What we gained, I hold.",
                    "A march nearer, Sire, and every yard behind me is still mine.",
                    "On the road, Sire. Nothing I own is left open behind me."),
        "waited": ("I gave up nothing, Sire. Not a field.",
                   "They looked at my lines today and thought better of it.",
                   "A quiet day on my front. It stays my front.",
                   "No fight today, and not a yard of mine lost by waiting."),
        "stayed": ("I did not move, Sire. This ground is mine and I don't leave it on a guess.",
                   "It changed, so I stayed on my own ground. Nobody shifts me off it.",
                   "No move today. This ground is mine, and I know every foot of it.",
                   "I kept to my lines. They are mine and they'll serve another night."),
        "asks": ("Sire, what do you want of me? I hold what I have meanwhile.",
                 "I need your orders, Sire. I'll not shift from my ground without them.",
                 "This is yours to decide, Sire. Until then I hold my ground."),
        "done": ("Done, Sire. What I took, I keep.",
                 "The task is finished, Sire. Not an inch of it given back.",
                 "Finished, Sire. Every yard of it still mine."),
        "third_night": ("Not a third night of the same, Sire. I'll hold my ground another way.",
                        "I've changed it, Sire. I'll stay on what is mine, but not like that."),
        "after_win": ("A victory, Sire. What we won stays mine, and I'll risk a little more.",
                      "We won, Sire. The field is mine now, and I'll hold it."),
        "after_loss": ("They hurt us, Sire. I'll sit on my ground and give not an inch more.",
                       "A loss, Sire. I'm back on my own ground, and here I stay."),
        "overruled": ("Your order first, Sire. My task will keep, and so will my ground.",
                      "Very well. My task stays mine, and I'll come back to it."),
        "recalled": ("Recalled, Sire? What I held there was mine, but as you wish.",
                     "I hand it back, Sire. It was mine to finish."),
        "trial_ask": ("Give me a task, Sire. What is put in my hands, I hold.",
                      "One task, Sire. I'll keep what I take and bring you more."),
        "trial_won": ("As I promised, Sire. I did not give an inch.",
                      "It's done, and every yard held. Remember it when someone speaks against me."),
        "trial_lost": ("It went wrong, Sire. I held on as long as I could.",
                       "I failed this once, Sire. I held on to the last, and I'll not be judged by it."),
        "remembers": ("You gave another man the task I should have had, Sire. I remember.",
                      "I was passed over once. I'd like that put right."),
    },
    "Bernadotte": {
        "ack": ("As you wish, Sire. I'm sure you'll let the men have a good night's rest first.",
                "Very well, Sire. I'll start once the men are rested.",
                "I'll do what I can, Sire, provided it's reasonable.",
                "Understood. No need to hurry me."),
        "bolder": ("Boldly? If you insist, Sire, though I'm sure you'll want the risks weighed.",
                   "Bolder, Sire? I'll need a comfortable moment to think how that might be done safely."),
        "careful": ("Carefully, Sire? Yes, that suits me very well indeed.",
                    "Careful is wise, Sire. I agree entirely."),
        "object": ("Sire, I'd sooner not risk my corps on that.",
                   "I must say I have doubts, Sire. I'll go, slowly."),
        "proposal_hold": ("Let me stay in the rear, Sire, where the men are comfortable. Someone must.",
                     "I could hold where I am, Sire. Quiet work, and safe.",
                     "Let me keep this post, Sire. I'm sure you'll agree it's sensible."),
        "idle": ("All quiet here, Sire, and the men are comfortable. I'd not disturb them.",
                 "Nothing to trouble you with, Sire. I'm sure you have worries enough.",
                 "My corps is rested and in no danger.",
                 "No news from my part of the line, Sire. Let's hope it stays that way."),
        "struck": ("We fought, Sire. I thought it could not be avoided.",
                   "I attacked, as it happens, Sire. I hope you understand it could not be helped.",
                   "My corps did its part today, Sire. I'm sure you'll see it's mentioned.",
                   "There was fighting today, Sire. I'm sure you understand I took what care I could."),
        "marched": ("We moved, Sire. A short march — no sense tiring the men.",
                    "On the road, Sire, with plenty of rests. We'll arrive when we arrive.",
                    "The corps is moving up, Sire, at a comfortable pace.",
                    "Some progress today, Sire, at a sensible pace. I see no need to rush."),
        "waited": ("No hurry tonight, Sire. I'm sure tomorrow will do just as well.",
                   "Nothing pressing today. The men are comfortable.",
                   "A quiet day, Sire, and I'm glad of it. The men slept well.",
                   "A quiet night, Sire. I see no reason to disturb anyone."),
        "dug_in": ("We improved the camp today, Sire. It is quite safe now.",
                   "A little digging, Sire, just enough to sleep soundly.",
                   "The position is stronger. I feel better for it.",
                   "We stay behind our works, Sire. I'm sure you understand I'd sooner be safe."),
        "stayed": ("I thought it better not to move, Sire. Matters had changed.",
                   "We stayed, Sire. I'm sure it was for the best.",
                   "No march today. I'm sure you understand.",
                   "I waited for a clearer picture, Sire. One can hardly be blamed."),
        "asks": ("I await your pleasure, Sire.",
                 "Perhaps you would decide, Sire. I'd rather not presume.",
                 "Shall I stay as I am, Sire? I'm quite comfortable here."),
        "done": ("It's done, Sire. I took no chances, I'm glad to say.",
                 "Finished, Sire. I hope you'll find it was done with proper care.",
                 "Done, Sire. I trust you'll find it was handled sensibly."),
        "third_night": ("I've made a small change, Sire. Nothing risky, I assure you.",
                        "A third night of that would look like idleness. So, something else."),
        "after_win": ("We won, Sire. I may venture a little more.",
                      "A victory, Sire. A little more ambition seems affordable now."),
        "after_loss": ("We were beaten back, Sire. I'm sure you'll agree it's no time for risks.",
                       "After that, Sire, I'm going very carefully indeed."),
        "overruled": ("Your order first, of course, Sire. My task can wait, and I'm in no rush.",
                      "As you command, Sire. I'll resume tomorrow, or the day after, if it's convenient."),
        "recalled": ("Recalled? As you wish, Sire — I was in no rush.",
                     "I return the task to you, Sire. Gladly."),
        "trial_ask": ("Let me have one task, Sire, to show my good faith.",
                      "A task of my own, Sire, nothing too hard. I'm sure I can show my worth."),
        "trial_won": ("It is done, Sire, and without any fuss. I hope that counts.",
                      "Finished. I hope we understand each other better now."),
        "trial_lost": ("It did not succeed, Sire. Circumstances were against me.",
                       "I regret it, Sire. The conditions were poor."),
        "remembers": ("You recalled me once before I'd begun, Sire. I've kept that in mind.",
                      "Last time I was called back. I'd like to finish this one."),
    },
    # ── the two who follow orders to the letter ──
    "Soult": {
        "exact": ("To the letter, Sire. Each line once.",
                  "I have it written down, Sire. I'll follow it exactly.",
                  "Exactly as you wrote it. Nothing added.",
                  "Your words, Sire, and nothing but your words."),
        "repeat": ("My orders: {orders} I'll do exactly that, Sire.",
                   "As written: {orders} I add nothing.",
                   "I have them by heart, Sire: {orders}",
                   "You wrote: {orders} So it shall be."),
        "not_covered": ("My orders say nothing of this, Sire. I stand where I am.",
                        "This isn't in my orders, Sire. I hold until you write more.",
                        "Nothing I was given covers this. I wait for your word.",
                        "I've done every line you wrote, Sire. Give me new ones."),
        "broken": ("One of my lines can't be carried out now, Sire. I need it rewritten.",
                   "My orders are broken, Sire. Tell me what replaces them."),
        "refusal": ("Give me my orders to the letter, Sire. I don't guess.",
                    "I follow orders, Sire. Write them and I'll carry them out."),
        "done": ("Carried out as written, Sire.",
                 "The order is complete. I await the next.",
                 "Done, exactly. Nothing more and nothing less."),
        "overruled": ("Today's order, Sire. My written lines sleep until tomorrow.",
                      "As you order today. The standing lines wait a night."),
        "trial_ask": ("Write me one task, Sire. I'll carry it out line by line.",
                      "One exact task, Sire. That's how I'll show you."),
        "trial_won": ("Carried out line by line, Sire, as promised.",
                      "It's done exactly. I trust that answers the doubt."),
        "trial_lost": ("The task could not be done as written, Sire.",
                       "I followed it to the end and it wasn't enough."),
    },
    "Grouchy": {
        "exact": ("Understood, Sire. I'll keep to every word.",
                  "I'll not stray from it, Sire.",
                  "Each line exactly as given. You may rely on it.",
                  "To the last word, Sire."),
        "repeat": ("I'm ordered: {orders} I'll keep strictly to it.",
                   "My instructions read: {orders} I follow them.",
                   "What I was told: {orders} That is what I'll do.",
                   "The order stands: {orders} I don't depart from it."),
        "not_covered": ("I have no orders for this, Sire. I keep to the last ones.",
                        "Nothing was written about this. I stay as I am.",
                        "I hear the guns, Sire, but my orders don't mention them.",
                        "My lines are all used, Sire. I need new ones."),
        "broken": ("A line of mine can't be done any more, Sire. Please replace it.",
                   "My orders no longer fit, Sire. I await new ones."),
        "refusal": ("I'm no man for guessing, Sire. Tell me exactly what to do.",
                    "Write it down for me, Sire. I'll do just that."),
        "done": ("Completed as instructed, Sire.",
                 "The order is done to the word.",
                 "Finished, Sire. I kept to the letter."),
        "overruled": ("Today's order takes its place, Sire. My lines wait.",
                      "As ordered today. Tomorrow I return to the written lines."),
        "trial_ask": ("Give me a clear task, Sire. I'll not put a foot wrong.",
                      "One task with every step written, Sire."),
        "trial_won": ("All done as instructed, Sire. I kept to every step.",
                      "Finished, Sire, exactly as you set it out."),
        "trial_lost": ("I kept to the orders, Sire, and still it failed.",
                       "It didn't succeed. I did only what was written."),
    },
}

# ═══════════════════════════ every other man, by his nature ══════════════════

BY_NATURE: Dict[str, Dict[str, Pool]] = {
    "bold": {
        "ack": ("I'll see to it, Sire.", "Right away, Sire.",
                "It will be done, and soon.", "Good. Something to do."),
        "bolder": ("Boldly, Sire. Gladly.", "Bolder. As you say."),
        "careful": ("Carefully, Sire. Very well.", "I'll take care, Sire."),
        "object": ("Hold, Sire? The enemy is right there.", "I don't care for it, Sire. I'll obey."),
        "proposal": ("Give me something to take, Sire.", "Let me go forward, Sire.",
                     "There's an enemy near. Let me at him."),
        "proposal_hold": ("Nothing to take from here, Sire. Let me hold until something shows.",
                          "Let me hold this ground, Sire, ready to strike.",
                          "I'll hold here, Sire, and hit whatever comes close.",
                          "Let me keep this place, Sire, and go forward the moment I can."),
        "idle": ("Nothing to fight yet, Sire.", "No enemy near me.",
                 "Waiting for a target, Sire.", "All ready, nothing to attack."),
        "struck": ("We attacked, Sire.",
                   "We went at them today.",
                   "We fought today, Sire.",
                   "I took the chance when it came."),
        "marched": ("We're marching, Sire.", "On the road toward them.",
                    "We moved up today.", "Getting closer, Sire."),
        "fell_back": ("We fell back, Sire. I'll make it up.", "A step back, to come on again.",
                      "We gave ground today. Not for long.", "Back a march, Sire. It had to be."),
        "waited": ("We waited today, Sire. I'd rather not have.",
                   "No fight today, Sire.",
                   "Nothing to strike yet. We keep watch.",
                   "A quiet day. Tomorrow, perhaps."),
        "dug_in": ("We dug in for the night, Sire.",
                   "The men threw up some works today.",
                   "Dug in. I'd rather be marching.",
                   "We keep to our works for now."),
        "stayed": ("I held where I was, Sire.", "No move today. Things changed.",
                   "I waited rather than blunder.", "Stayed put, Sire."),
        "asks": ("Your orders, Sire?",
                 "I need your word, Sire.",
                 "What now, Sire?"),
        "done": ("Done, Sire.", "The task is finished.", "It's done. What's next?"),
        "third_night": ("Not a third night of the same, Sire. I've changed it.",
                        "I'm trying something else tonight."),
        "after_win": ("We won, Sire. I'll go in sooner now.", "A win. We'll take longer odds."),
        "after_loss": ("We lost, Sire. I'll be more careful.", "A beating. I want better odds next time."),
        "overruled": ("Your order first, Sire.", "As you say. My task waits."),
        "recalled": ("Recalled, Sire. As you wish.", "I come back as ordered."),
        "passed_over": ("A junior was given a task while I stood idle, Sire. I mind it.",
                        "I was passed over, Sire. I won't pretend I'm pleased.",
                        "Others get the work and I get the waiting.",
                        "You chose another man, Sire. I'd have gone gladly."),
        "trial_ask": ("Give me a task to prove myself, Sire.", "One task, Sire. Judge me on it."),
        "trial_won": ("I did what I said, Sire.", "It's done, as promised."),
        "trial_lost": ("I failed, Sire.", "It went wrong. I'm sorry."),
        "remembers": ("You overruled me before, Sire. I remember.",
                      "Last time I wasn't allowed to finish."),
    },
    "careful": {
        "ack": ("It will be done with care, Sire.", "Understood, Sire.",
                "I'll see it done properly.", "Very good, Sire. I'll prepare."),
        "bolder": ("Boldly, Sire... I'll do my best.", "Bolder. I'll manage it."),
        "careful": ("Carefully. Good.", "With care, Sire. Of course."),
        "object": ("Sire, I don't like those odds.", "I'd advise waiting, Sire. I'll go if ordered."),
        "proposal_hold": ("Let me hold here and dig in, Sire.", "I'd keep this position, Sire.",
                     "Let me make this ground safe first."),
        "idle": ("Dug in and watching, Sire.", "Nothing in front of us.",
                 "All quiet. We keep watch.", "No change here, Sire."),
        "struck": ("We attacked when it was safe to, Sire.",
                   "The odds were good, so we went in.",
                   "We fought today, in good order.",
                   "A careful attack, Sire."),
        "marched": ("We marched, Sire, in good order.", "Moving up slowly and safely.",
                    "On the road, with scouts ahead.", "A short, safe march today."),
        "fell_back": ("We fell back to better ground, Sire.", "A step back. The corps is whole.",
                      "I gave ground to keep the men.", "We withdrew in order, Sire."),
        "waited": ("We kept watch today, Sire.",
                   "No fight today. No surprises either.",
                   "A quiet day. The corps is in order.",
                   "We waited, Sire. It cost nothing."),
        "dug_in": ("We dug in today, Sire.",
                   "We improved our works.",
                   "More digging today. The position is sound.",
                   "We keep behind our works, Sire."),
        "stayed": ("I kept my position, Sire.", "No move. It wasn't safe.",
                   "Things changed, so I waited.", "We stayed where we were."),
        "asks": ("What are your orders, Sire?",
                 "I'll wait for your word, Sire.",
                 "This needs your decision, Sire."),
        "done": ("The task is done, Sire.", "Finished, in good order.", "Done. The men are safe."),
        "third_night": ("I've changed the routine, Sire. Three nights the same is unwise.",
                        "Something different tonight."),
        "after_win": ("A win, Sire. I'll risk slightly more.", "We won. I can afford a little boldness."),
        "after_loss": ("A loss, Sire. I'll risk less.", "We were beaten. More care from now on."),
        "overruled": ("Your order comes first, Sire.", "Understood. My task waits a day."),
        "recalled": ("Recalled. Very good, Sire.", "I return as ordered, Sire."),
        "passed_over": ("A junior man was given the task, Sire. I note it.",
                        "I was not chosen. I'd like to know why, Sire.",
                        "I stood idle while another was sent. It was not what I expected.",
                        "You passed over me, Sire. I'll say no more than that."),
        "trial_ask": ("Give me one task, Sire, to show what I'm worth.",
                      "A task, Sire. I'll carry it out with care."),
        "trial_won": ("It's done as I undertook, Sire.", "The task is complete."),
        "trial_lost": ("I did not succeed, Sire.", "It failed. The fault is mine."),
        "remembers": ("I was passed over before, Sire. I've not forgotten.",
                      "Another man was preferred to me once."),
    },
    "literal": {
        "exact": ("To the letter, Sire — each line once, and no more.",
                  "Exactly as written, Sire. I will not improve on it.",
                  "As written, Sire: no more and no less.",
                  "Word for word, Sire."),
        "repeat": ("My orders are: {orders} I follow them.",
                   "The orders say: {orders} That is all I'll do.",
                   "As given: {orders}",
                   "Written orders: {orders} I keep to them."),
        "not_covered": ("My orders don't cover this, Sire. I stand.",
                        "Nothing written for this, Sire. I wait.",
                        "I have no line for this, Sire.",
                        "All my lines are used, Sire."),
        "broken": ("My orders are broken, Sire. I need new ones.",
                   "A line can't be carried out, Sire."),
        "refusal": ("Give me my orders to the letter, Sire.",
                    "I take exact orders, Sire. I don't choose for myself."),
        "done": ("Done as written, Sire.", "The order is carried out.", "Completed to the letter."),
        "overruled": ("Today's order first, Sire. My lines sleep.", "As ordered. The written lines wait."),
        "passed_over": ("Another man was sent, Sire. I only note it.",
                        "I was not chosen, Sire. I'm ready when you are.",
                        "I had no orders while another marched. I'd welcome some.",
                        "A junior got the task, Sire. I say so plainly."),
        "trial_ask": ("Give me one written task, Sire. I'll do it exactly.",
                      "A task to the letter, Sire. Judge me by it."),
        "trial_won": ("Done as written, Sire. I hope it's enough.", "Every line carried out, Sire."),
        "trial_lost": ("I could not carry it out, Sire.",
                       "The task failed. I followed it as far as it went."),
    },
}

# What a man who cannot be set on his own says (§6.2) — kept as the first
# line of the literal `refusal` set, by its old name.
LITERAL_REFUSAL = BY_NATURE["literal"]["refusal"][0]

# ═══════════════════════════ the one thing he remembers ═════════════════════
# §11: "each man remembers one thing (a rival's absence, an order you
# overruled, a slight)". WHAT each man remembers; when it happens to him it is
# kept (`own_record["memory"]`) and said ONCE, the next time he is given a task
# or reports a night, in his `remembers` line.
REMEMBERS: Dict[str, str] = {
    "Ney": "overruled", "Lannes": "overruled",
    "Davout": "passed_over", "Massena": "passed_over",
    "Murat": "recalled", "Bernadotte": "recalled",
}
REMEMBERS_BY_NATURE: Dict[str, str] = {"bold": "overruled", "careful": "passed_over"}

# ═══════════════════════════ a court's own words ════════════════════════════
# IC-15: the head of CAPTURED ORDERS, by court (`{name}` is the marshal the
# orders were written for). The plain reading follows it.
COURTS: Dict[str, Pool] = {
    "Austria": ("From the war council in Vienna, to {name}:",
                "Vienna's orders to {name}, signed and sealed:"),
    "Russia": ("By command of the Tsar, to {name}:",
               "From the Tsar's headquarters, to {name}:"),
    "Prussia": ("The King's orders to {name}:",
                "From Berlin, to {name}:"),
    "Britain": ("From the Horse Guards in London, to {name}:",
                "London's instructions to {name}:"),
    "": ("His court's orders to {name}:",
         "Written orders for {name}:"),
}

# The act of a night → the kind of line he says in the morning.
KIND_OF_ACT: Dict[str, str] = {
    "attack": "struck", "storm": "struck", "besiege": "struck", "take": "struck",
    "join": "marched", "strike": "struck",   # (a join: he marched to a friend's battle — no "I led")
    "march": "marched", "move_up": "marched",
    "fall_back": "fell_back",
    "look": "waited", "probe": "waited",
    "dig_in": "dug_in",
    "stay": "stayed",
    "asks": "asks",
}
# (A night he only made ready, or rested his men, has no line: the plain words
# say it. A line never claims what the night did not hold — a `struck` line
# claims no victory, a `waited` line no particular way of waiting, an `asks`
# line no reason: the plain words beside it carry those.)

# The kinds a man can say on nights running: four lines or more, each man.
RECURRING = ("ack", "idle", "struck", "marched", "waited", "stayed", "dug_in")

# WHAT A MAN NEVER SAYS (`docs/MARSHAL_VOICE_BIBLE.md` — the guide's "never
# says" lists live HERE, and the pin reads every line of his against them, so a
# new line that breaks his character fails the suite). Whole words, any case.
NEVER_SAYS: Dict[str, Tuple[str, ...]] = {
    "Ney": ("retreat", "fall back", "fell back", "prudent", "too strong", "wait for"),
    "Davout": ("glory", "luck", "chance", "gamble"),
    "Murat": ("dig", "dug", "trench", "patience", "slowly", "on foot"),
    "Lannes": ("retreat", "fell back", "give up", "too strong", "afraid"),
    "Massena": ("abandon", "let go", "glory"),
    "Bernadotte": ("at once", "charge", "glory"),
    "Soult": ("i think", "i judge", "perhaps", "i guess", "i would rather"),
    "Grouchy": ("i think", "i judge", "perhaps", "i guess", "i would rather"),
}
# "Sire" is the ONLY period word (the user's ruling, November 22, 2026).
PERIOD_WORDS: Tuple[str, ...] = (
    "monsieur", "majesty", "excellency", "highness", "liege", "milord",
    "thee", "thou", "verily", "forsooth", "pray", "hark")


def _key(name: str) -> str:
    """His roster key, without the accent the display adds."""
    return str(name or "").replace("é", "e").replace("É", "E")


def nature_of(marshal) -> str:
    """bold / careful / literal — the design's word for his nature ("" for the
    Emperor and anyone else: they speak no line here)."""
    return {"aggressive": "bold", "cautious": "careful", "literal": "literal"}.get(
        str(getattr(marshal, "personality", "") or ""), "")


def pool(name: str, nature: str, kind: str) -> Pool:
    """The lines a man may say of a kind, in rotation order: HIS OWN first,
    then his nature's (the bank falls through, as the battle lines' does) —
    never a line twice."""
    own = tuple(LINES.get(_key(name), {}).get(kind) or ())
    shared = tuple(BY_NATURE.get(nature, {}).get(kind) or ())
    never = NEVER_SAYS.get(_key(name)) or ()
    return own + tuple(line for line in shared
                       if line not in own and not _breaks(line, never))


def _breaks(line: str, never: Sequence[str]) -> bool:
    """Does this line use a word the man never says? (His nature's lines fall
    through to him — but never one that breaks HIS character: Ney does not say
    he fell back, Murat does not say he dug.)"""
    low = " " + str(line).lower()
    return any(re.search(rf"\b{re.escape(word)}", low) for word in never)


def _fill(said: str, fill: Dict[str, object]) -> str:
    if not fill or not said:
        return said
    try:
        return said.format(**fill)
    except (KeyError, IndexError, ValueError):
        return said


def voice(world, marshal, kind: str, **fill) -> str:
    """The line of `kind` he says NEXT — never one of his last three while
    another stands in the set. PURE: a preview, a question and "Tonight" read
    this; nothing is written."""
    from backend.game_logic import said_lately as _lately
    if marshal is None:
        return ""
    lines = pool(marshal.name, nature_of(marshal), kind)
    if not lines:
        return ""
    start = _lately.start_for(world, _key(marshal.name), kind, len(lines))
    return _fill(_lately.choose(marshal, lines, start), fill)


def speak(world, marshal, kind: str, **fill) -> str:
    """He SAYS his line of `kind`: `voice`, and the record of it (the one
    writer, `said_lately.say`). Called only where a line is really said — an
    order given, a night's act, a task ended."""
    from backend.game_logic import said_lately as _lately
    if marshal is None:
        return ""
    lines = pool(marshal.name, nature_of(marshal), kind)
    if not lines:
        return ""
    start = _lately.start_for(world, _key(marshal.name), kind, len(lines))
    chosen = _lately.choose(marshal, lines, start)
    _lately.say(marshal, chosen)
    return _fill(chosen, fill)


def kind_given(risk: int, objected: bool) -> str:
    """The kind of line he answers a task with: his objection, else how he was
    told (boldly / carefully), else plain."""
    if objected:
        return "object"
    if int(risk or 0) > 0:
        return "bolder"
    if int(risk or 0) < 0:
        return "careful"
    return "ack"


# ── the one thing he remembers ──

def remembers_what(marshal) -> str:
    """WHAT this man remembers ("" for a man who follows orders to the letter:
    he holds no grudge, he holds his lines)."""
    if marshal is None:
        return ""
    return REMEMBERS.get(_key(marshal.name)) or REMEMBERS_BY_NATURE.get(nature_of(marshal), "")


def note_memory(world, marshal, what: str, who: str = "") -> bool:
    """It happened to him — an order of yours overruled his task, he was
    recalled, a junior was sent while he stood idle. Kept only if it is the
    thing THIS man remembers; said once (`recall_memory`). A battle's and an
    order's own bookkeeping (it rides `marshals`)."""
    if marshal is None or remembers_what(marshal) != what:
        return False
    rec = getattr(marshal, "own_record", None)
    rec = dict(rec) if isinstance(rec, dict) else {}
    rec["memory"] = {"what": what, "who": str(who or ""),
                     "turn": int(getattr(world, "current_turn", 0) or 0)}
    marshal.own_record = rec
    return True


def has_memory(marshal) -> bool:
    rec = getattr(marshal, "own_record", None)
    return bool(isinstance(rec, dict) and isinstance(rec.get("memory"), dict))


def recall_memory(world, marshal, said: bool) -> str:
    """His `remembers` line while the thing is still on his mind — "" when he
    has nothing to say of it. With `said`, it is said and put away."""
    if not has_memory(marshal):
        return ""
    line = speak(world, marshal, "remembers") if said else voice(world, marshal, "remembers")
    if said and line:
        marshal.own_record.pop("memory", None)
    return line


# ── a court's own words (captured orders) ──

def court_head(world, court: str, name: str, said: bool = False) -> str:
    """The head of a court's captured orders ("From the war council in Vienna,
    to Mack:"). The same head for a court on the historical seed; a fixed one
    by the seed otherwise. No marshal says it: nothing is recorded."""
    from backend.game_logic import said_lately as _lately
    lines = COURTS.get(str(court)) or COURTS[""]
    start = _lately.start_for(world, str(court), "court_head", len(lines))
    return _fill(lines[start % len(lines)], {"name": name})


# ── Session 3's reader, kept: a line by name and turn, with no memory ──

def _pick(lines: Sequence[str], name: str, turn: int) -> str:
    """One of his lines, keyed by his name and the turn — never a die."""
    if not lines:
        return ""
    seed = zlib.crc32(f"{_key(name)}:{int(turn)}".encode("utf-8"))
    return str(lines[seed % len(lines)])


def line(name: str, nature: str, kind: str, turn: int = 0, **fill) -> str:
    """His line of `kind`, filled; "" when he has none of that kind. (Session
    3's reader — by name and turn, for a caller that holds no marshal. Where
    the man is in hand, `voice` and `speak` are the readers: they know what he
    said lately.)"""
    own = LINES.get(_key(name), {})
    lines: Optional[Sequence[str]] = own.get(kind) or BY_NATURE.get(nature, {}).get(kind) or ()
    return _fill(_pick(lines, name, turn), fill)
