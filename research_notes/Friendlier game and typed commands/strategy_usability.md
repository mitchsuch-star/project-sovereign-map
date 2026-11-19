# What makes complex turn-based strategy games user-friendly (learnable, legible, low-friction), as of November 2026

Scope note: about 25 tool calls. Coverage is strong on Paradox games (CK3, Victoria 3, EU5), Civ VII, Andersen CHI 2012, Slay the Spire and Into the Breach, and the Steam achievement check. It is thin or absent on Humankind, Stellaris, HOI4, Total War advisors, Field of Glory II, Shadow Empire and the Civ VI advisor. Those are listed under Gaps rather than guessed. Search-result summaries were produced by a search tool, so a claim marked "search summary" was not read on the page itself.

## 1. Onboarding: what worked and failed in the genre, and what developers say they learned

### Takeaway
The best-documented evidence is from Paradox. CK3's own telemetry (2024) found that finishing the tutorial barely predicted retention, even though the tutorial as a whole mattered. The 67-box linear tutorial was cut to roughly a third and made progressively disclosed. Victoria 3 moved teaching into an optional objective driven by the in-game journal. Civ VII's launch UI shows the opposite failure: information that is missing, and noise with no priority. Across the games checked, onboarding that rides on the game's own surfaces (journal, tooltips, events) is favoured over a separate linear lesson, but no source measured that comparison head to head.

### Cited Findings

**Crusader Kings III**
- Paradox UX staff (Valeska Martins, Ellinor Zetterman) published a tutorial-refresh deep dive on 12 Sept 2024. Telemetry showed the tutorial "had a significant effect on player retention" even though it did not cover all mechanics. Finishing it "was not a major determining factor" in whether players kept playing, which the team read as "something about the tutorial was lacking". — [Game Developer, "Deep Dive: Refreshing the Crusader Kings III tutorial mode through optimized UX" (Sept 2024)](https://gamedeveloper.com/design/deep-dive-refreshing-the-crusader-kings-iii-tutorial-mode-through-optimized-ux)
- The original tutorial was 67 sequential text boxes. The team judged it too long and information-dense. Much of it was "not immediately useful" and many players went to video tutorials instead. The text windows did not resize to content. — same source
- Changes made: cut non-essential content (about one-third of the 67 messages kept as a baseline, then rewritten), progressive disclosure (for example revealing character-panel information gradually), dynamically sized windows, and a "softer onboarding layer" of narrative-hook events with explanation in tooltips. Staff from other studio teams were used as playtesters to counter the core team's "curse of knowledge". — same source
- The old tutorial was kept in the game so old and new can be compared in telemetry. The article states no result numbers. Playtesting gave mostly qualitative feedback, and the team said quantitative data would need a public release. — same source. **No published post-change retention number was found.**
- The team studied narrative-framed tutorials in Civilization VI and Against the Storm as references. — same source
- At CK3's 2020 launch, tooltips had their own tooltips (nested hover), and critics praised "tooltips galore" and a dynamic tutorial (NME), while PC World found hyperlinks leading "further and further down a terminology rabbit hole". — [search summary of PC World / NME coverage via GamingOnLinux and others](https://www.gamingonlinux.com/2020/03/paradox-to-give-players-a-lot-more-guidance-in-crusader-kings-3-new-overview-video); [NME](https://www.nme.com/reviews/crusader-kings-iii-review-a-superb-sequel-that-welcomes-new-players-to-the-joys-of-grand-strategy-2744117)
- Player-side complaint that persisted: Digital Trends called the tutorial "dense, long, and often boring". In April 2022 PureXbox reported newcomers on Game Pass getting stuck, with veterans pointing them to YouTube and trial and error. — [Digital Trends](https://www.digitaltrends.com/gaming/crusader-kings-iii-beginners-guide-10-tips-tricks/); [PureXbox 2022](https://www.purexbox.com/news/2022/04/xbox-players-are-getting-stuck-at-the-tutorial-in-crusader-kings-3) (both as characterised in a search summary)
- "Legends of Crusader Kings III" was a new-player acquisition initiative that gave five historical figures as starting characters, one per playstyle (secondary report). — [Mein-MMO](https://mein-mmo.de/en/steam-it-is-a-hard-game-that-hardly-anyone-finishes-now-it-wants-more-beginners,1113788). Reception data for it was not found.

**Victoria 3**
- Dev Diary 51 (Paradox, 2022): the tutorial became an optional player objective, "Learn the Game", delivered through the Journal, instead of a separate mode. Each journal entry can carry up to two popup lessons: "Tell me How" (step-by-step, may guide through the interface) and "Tell me Why" (the purpose and effects, with illustrations). Lessons are short, modular and player-triggered. — [Victoria 3 Dev Diary 51](https://www.paradoxinteractive.com/games/victoria-3/news/dev-diary-51-tutorials)
- The same diary: challenges are reactive to the chosen country (Sweden gets a rye farm task, Sokoto a millet farm task) and appear in a sequence that depends on prior progress. The AI is less aggressive by default under the objective. Sweden and the USA are recommended starts. Concept tooltips can launch walkthroughs at any time. — same source
- The authors chose to ask players in context what they want, rather than sorting them into Novice, Intermediate or Expert tracks, and note many first-time Paradox players "never learn how to unpause". They state the balance "remains to be fully answered". The diary reports no player data. — same source (the paraphrase of "never learn how to unpause" is from a fetch summary)
- Victoria 3's 2024 retrospective (Dev Diary 142), per a search summary, says the team learned to focus more on the "why" of journal entries in future design. I could not fetch the page to confirm wording. — [Dev Diary 142 (forum page, search result only)](https://admin-forum.paradoxplaza.com/forum/developer-diary/victoria-3-dev-diary-142-2024-in-retrospect.1726056/page-3)
- Critic reception on legibility was split. Destructoid praised nested tooltips letting every calculation be expanded; Prima Games found mouse-over tooltips good but said each task led to "multiple tooltips, panels, tabs, and icons" that left the reviewer confused and discouraged; Inverse (7/10) said production chains felt too abstract. — [Prima Games](https://primagames.com/gaming/victoria-3-review-fresh-new-look-and-fresh-eyes); [Inverse](https://www.inverse.com/gaming/victoria-3-review-pc); [Destructoid](https://destructoid.com/reviews/review-victoria-3-pc-paradox-interactive-strategy) (all via one search summary; not individually opened)

**Europa Universalis V (launched Nov 2025)**
- Steam reception moved over time. A search summary reports early snapshots around 72 percent positive ("Mostly Positive"), and a later aggregator snapshot (stmstat) of about 29,000 reviews at about 66.5 percent ("Mixed"). The capture dates are unstated, so treat the numbers as snapshots. Metacritic critics listed 85/100. — [stmstat](https://stmstat.com/app/3450310/reviews); [search summary sources via Tobold/pcgameshardware](https://www.pcgameshardware.de/Europa-Universalis-5-Spiel-75214/News/Globalstrategie-Release-sorgt-fuer-Aufsehen-1485894/)
- Blogger Tobold (31 hours, Nov 2025): notifications "absolutely abysmal" (missed France breaking an alliance, no obvious alert settings); menus unclear about which sections are informational versus open a deeper view; most of his time spent paused learning; he learned partly from YouTube and Twitch; picking a small, well-documented country (Holland) helped; "very inaccessible". He also notes that using the in-game tutorial or mission tree disables achievements. — [Tobold's Blog, Nov 2025](https://tobolds.blogspot.com/2025/11/europa-universalis-v-first-impressions.html)
- Paradox's patch 1.1 ("Rossbach", early 2026), per one secondary outlet: alerts can be permanently muted (with a recovery menu), pinned filters per screen, collapsible unit screens, a more prominent call-to-war notice, reworked market screens showing supply and demand factors, mass-upgrade and move-all commands, and an army/navy template builder. The outlet frames these as answers to nested and cluttered windows, hard-to-find data and excessive clicking. — [FinalBoss.io](https://finalboss.io/europa-universalis-5-rossbach-1-1-tackles-ui) (secondary; verify against Paradox patch notes)
- Reviewers credit EU5's automation as helpful to newcomers but not a full fix: GameWatcher calls it an "incredibly useful tool for newcomers" that "doesn't fully solve" the Paradox tutorial problem. — [GameWatcher review](https://www.gamewatcher.com/europa-universalis-v/review) (search summary)
- A later Tobold post (April 2026) says the economy "mostly just plays itself" once automated, and he learned trade efficiency through community experiments, not in-game explanation. That is a legibility caution for automation: it hides the cause and effect that new players need. — [Tobold, Apr 2026](https://tobolds.blogspot.com/2026/04/eu5-game-playing-itself.html?m=1)

**Civilization VII (launch Feb 2025)**
- Early access began 6 Feb 2025, full release 11 Feb. Steam and Reddit users called the UI confusing and impractical, and some called the game unfinished. Reported Steam positivity was about 50 percent from roughly 8,000 reviews at one snapshot (Notebookcheck), against more favourable critic scores. — [Notebookcheck](https://www.notebookcheck.net/Civilization-VII-s-rough-launch-sparks-backlash-developers-pledge-improvements.958568.0.html); [Game8](https://game8.co/articles/latest/civilization-vii-steam-version-suffers-deluge-of-negative-reviews-as-advanced-access-releases)
- Firaxis said its "top priority is improving the UI", promised a March 1.1.0 patch, and named intuitive UI interactions and map readability. Players also missed queued movement and faster play. — [CGM](https://www.cgmagonline.com/news/civilization-vii-quality-of-life-updates)
- Aftermath's review said the UI "doesn't tell you things you need to know" and "continually tells you things you don't need to know", with no way to separate "what's a bother and what's important". It also said hover tooltips were missing though present in an earlier build, and that cities were no longer scannable at a glance. It argued "bad UI" also masks deeper design issues. — [Aftermath review](https://aftermath.site/civilization-vii-review/)

**Old World (Mohawk, 2021)**
- Reviewers found the tutorial thin and guidance scattered. One review (Russell Troxel) says mechanics are introduced "a step behind" need-to-know, so a unit's tutorial can appear only after the player has used it. A Quarter to Three forum post reports Mohawk found teaching through tooltips harder than expected. Some players found the curve smooth, so opinion is split. — [Quarter to Three](https://www.quartertothree.com/fp/2021/07/01/bringing-new-eyes-to-old-world/); [Troxel review](https://russelltroxel.com/writing/2021/7/11/old-world-review) (search summaries; 2021, may predate tutorial updates)

**Unity of Command 2 (2019)**
- PC Gamer called it an excellent wargame for newcomers and hardcore players, and its interface "good enough" not to fight the design. A developer post says the new tutorial "is not perfect" but is far better than the first game's. Steam summaries note finicky UI for some. — [PC Gamer review](https://www.pcgamer.com/unity-of-command-2-review/) (search summary; 2019)

**Into the Breach and Slay the Spire (the "show the enemy's plan" examples)**
- Subset Games (Justin Ma, Gamasutra interview) wanted each death to feel the player's own fault, which made telegraphed attacks a core mechanic; with every enemy attack telegraphed and no randomness in your own attacks, play becomes puzzle-like. — [Game Developer, "Road to the IGF: Into the Breach"](https://gamedeveloper.com/game-platforms/road-to-the-igf-subset-games-i-into-the-breach-i-) (as characterised by a search summary)
- Slay the Spire's team has said revealing enemy intent is what "finally made the game come together". Their stated reason for an icon over each enemy is that clicking each foe to check its plan would be tedious. — [Mega Crit talk summarised at Game Developer / JikGuard](https://www.jikguard.com/news/watch-casey-yano-break-down-the-design-decisions-behind-slay-the-spire) (search summary; speaker attribution unconfirmed)

### Inferences
- CK3's telemetry finding (completion not predictive) suggests that a lesson being finished is a poor success metric. A game should track whether the player later uses the taught system, not whether they got to the end of the tutorial.
- The shared Paradox direction (CK3 narrative-hook events, Victoria 3 journal objectives, EU5 recommended small countries and automation) is to teach in the flow of play and to recommend a small start. This matches the user's existing hints and help screen; the gap evidence points to is cause-and-effect and priority, not a lack of a help screen.
- Civ VII's failure, as reviewers describe it, is about information priority and missing hover information, not about too little tutorial. That is a warning for any game with many alerts.

### Gaps
- No post-refresh CK3 retention figure, and no Victoria 3 tutorial metrics, are published.
- Not researched or not found: Humankind, Stellaris, HOI4, Total War advisors, Field of Glory II, Shadow Empire onboarding; Civ VI advisor evidence; EU5 developer diaries on onboarding (only secondary coverage found).
- I found no GDC talk on CK3 UX (the Game Developer article is the closest primary source). I did not find the Paradox Victoria 3 UX diary (DD 29) text; the fetch failed.

## 2. Published numbers: tutorial completion, drop-off, and the academic finding

### Takeaway
There are no developer-stated retention figures for the named strategy games. Steam global achievements do not expose a clean tutorial or first-hour metric for CK3, Victoria 3, Civ VI or Civ VII. The one rigorous academic result (Andersen et al., CHI 2012, over 45,000 players) says tutorials matter in the most complex game and not in simple ones. I found no replication.

### Cited Findings
- Andersen et al. built eight tutorial designs into three games of varying complexity and measured engagement and retention over more than 45,000 players. Tutorials raised play time by up to 29 percent in the most complex game. In the two simpler games they had no significant effect. The authors suggest tutorial investment may not be justified where mechanics can be discovered by experimentation. — [UW GRAIL project page](https://grail.cs.washington.edu/projects/game-abtesting/chi2012/)
- A search summary states the most complex game was Foldit, with up to 75 percent more player progress; the project page names Refraction, Hello Worlds and Foldit but does not say which is most complex. — [paper listing at DBLP](https://dblp1.uni-trier.de/rec/conf/chi/AndersenOLSLTCP12.html) (not independently confirmed; treat the 75 percent as unverified)
- When I tried to read the PDF, only compressed text came back. The readable section headings were: "Tutorials were only justified in the most complex game", "Context-sensitivity can improve engagement", "Tutorial freedom did not affect player behavior", and "On-demand help harmed and helped player retention". The game names in that file did not match the project page (it showed Kongregate games), so the PDF may be a different or linked paper; **treat these headings as unverified for CHI 2012.** — [chi2012.pdf](https://grail.cs.washington.edu/projects/game-abtesting/chi2012/chi2012.pdf)
- Complexity caveat: the three games are casual or web games and a citizen-science game (Foldit), not 4X or grand strategy, so the finding is directional only for a Napoleonic grand-strategy game. It was measured in 2012.
- Steam global achievements: CK3 (26 of 56 base achievements shown) and Victoria 3 (26 of 152) have no tutorial or first-hour achievement; the most common listed CK3 achievement is "Marry another character" at 61.5 percent, and "Defeat a faction in a war" is 28.3 percent. Victoria 3's most common listed is 42.1 percent. Civ VI's early achievements run 60 to 74 percent (for example "Have six improvements at once" 74.3 percent), while "Win a regular game at Settler difficulty" is 37.4 percent. Civ VII's visible achievements are 27.9 percent or lower. — [CK3](https://steamcommunity.com/stats/1158310/achievements); [Victoria 3](https://steamcommunity.com/stats/529340/achievements); [Civ VI](https://steamcommunity.com/stats/289070/achievements); [Civ VII](https://steamcommunity.com/stats/1295660/achievements) (snapshot as read Nov 2026; pages showed partial lists)
- These percentages measure all owners (including people who never launched the game), not tutorial completion. Do not read them as a retention rate.
- Smaller strategy games do show a steep tutorial funnel: Lord of Rigel "Start Tutorial" 40.6 percent versus "Complete Tutorial" 4.3 percent; Offworld Trading Company first tutorial finished 59.8 percent and the sixth 23.1 percent; Renaissance Kingdom Wars 84.0 percent to 38.0 percent. — [Lord of Rigel et al. via Steam stats search](https://steamcommunity.com/stats/421260/achievements) (search summary, cited pages not individually opened; snapshots, dates unknown)
- A peer-reviewed MDPI paper (40 participants) reports a figure that 61 percent of customers delete a game within 24 hours of download, and finds tutorials helped complex games and not simple ones. I did not open it, and the publication year is unconfirmed. — [MDPI Multimodal Technologies and Interaction 4(3):41](https://www.mdpi.com/2414-4088/4/3/41/html)
- Wayline blog claims (for example a 30 percent retention rise from an interactive tutorial) have no published method; do not rely on them. — [Wayline](https://www.wayline.io/blog/myth-tutorials-are-ux)

### Inferences
- A tutorial funnel on Steam usually loses most players somewhere in the lesson sequence (in small examples, around 40 to 90 percent are gone by the end), so shorter lessons and optional lessons are a reasonable bet, though no number ties this to a grand-strategy title.
- Taken with Andersen, a game with many interlocking systems is in the "tutorials are justified" category, but the form matters: Andersen's section heading on context-sensitivity (unverified) matches the CK3/Victoria 3 move toward in-context teaching.

### Gaps
- No developer-stated retention or drop-off figure for CK3, Victoria 3, EU5, Civ, Old World, Humankind, Stellaris or HOI4.
- No replication of Andersen 2012 in 4X or grand strategy found. A later study would need a venue-specific search (CHI PLAY, FDG).
- Per-game Andersen numbers (beyond the 29 percent) could not be verified.

## 3. Legibility principles with evidence

### Takeaway
The strongest evidence is for showing the enemy's plan and showing the outcome before the commitment (Slay the Spire, Into the Breach, one-click move preview), for explaining numbers on hover (nested tooltips, praised but with a confusion risk), and for priority-sorted alerts with a mute control (Civ VII and EU5 both drew complaints about alert noise). General usability principles (recognition over recall, progressive disclosure) are well established but have little game-specific measurement.

### Cited Findings
- Nielsen's heuristic: minimise memory load by keeping objects, actions and options visible; recognition is easier than recall because there are more retrieval cues. — [Nielsen via UX Design summary](https://uxdesign.cc/jakob-nielsens-sixth-usability-heuristic-for-user-interface-design-ac88e7d58ec); [NN/g video](https://www.nngroup.com/videos/recognition-vs-recall/) (secondary summary; I did not reach the NN/g article itself)
- Progressive disclosure (NN/g): defer advanced or rarely used options to a secondary screen so only the primary options show by default; it makes applications easier to learn and less error-prone. A secondary source cites a 1997 claim (Carroll and Rosson) that "no empirical evidence exists" for its effectiveness; that quote is secondhand and unverified. — [NN/g video](https://www.nngroup.com/videos/progressive-disclosure/); [Jakob Nielsen PhD substack](https://jakobnielsenphd.substack.com/p/progressive-disclosure)
- CK3 applied progressive disclosure to the character panel as part of the 2024 refresh, but the post reports no measured effect. — [Game Developer](https://gamedeveloper.com/design/deep-dive-refreshing-the-crusader-kings-iii-tutorial-mode-through-optimized-ux)
- Showing the outcome before commitment: Into the Breach and Slay the Spire show the enemy's next action every turn (see Section 1). Slay the Spire's team said that checking each enemy by click would be tedious, hence an icon on every enemy. Both are developer statements, not measurements.
- Explaining outcomes after the fact: Victoria 3's "Tell me Why" lessons and nested tooltips are the main shipped examples; Destructoid praised nested tooltips ("every simulated calculation, keyword and concept") while Prima reported tooltip-and-panel sprawl. — [Dev Diary 51](https://www.paradoxinteractive.com/games/victoria-3/news/dev-diary-51-tutorials); [Prima](https://primagames.com/gaming/victoria-3-review-fresh-new-look-and-fresh-eyes) (search summary)
- Alerts and end-turn queues: Tobold on EU5 launch ("absolutely abysmal" notifications, missed an alliance break) and Paradox's 1.1 response (mute with recovery, a more prominent call-to-war notice) show alert prominence and noise were the pain points. Aftermath on Civ VII says the UI cannot separate what is a bother from what is important. — [Tobold](https://tobolds.blogspot.com/2025/11/europa-universalis-v-first-impressions.html); [FinalBoss.io](https://finalboss.io/europa-universalis-5-rossbach-1-1-tackles-ui); [Aftermath](https://aftermath.site/civilization-vii-review/)
- Friction reduction: Civ VII players missed queued movement and faster play (CGM); EU5 added move-all-by-category and templates in 1.1 against "excessive clicking" complaints (FinalBoss, secondary).
- Automation as an onboarding aid: reviewers say it helps but does not solve onboarding (GameWatcher), and Tobold reports the economy then "plays itself" with little visibility into its decisions.
- Soren Johnson ("7 Deadly Sins for Strategy Games", 2008) criticises the black-box, interface-less trend of the late 1990s; his "A Study in Transparency" talk argues transparency is the key factor when mechanics are primary. — [Game Developer](https://gamedeveloper.com/game-platforms/opinion-7-deadly-sins-for-strategy-games); [Designer Notes](https://designer-notes.com/category/games/page/3) (as summarised in search; not opened; dated 2008 and later)
- Undo: **no published evidence on undo in strategy games was found.**
- Single consistent interaction grammar: **no published evidence found specific to this genre.**

### Inferences
- The user's one-click move with a preview tag and the replayed enemy moves fit the best-evidenced pattern (show the plan before and the result after). The pattern leaves room for a preview of every other costly order, such as attack odds, and for a one-line "why" on outcomes.
- Complaints about alerts concern priority and mute, not volume alone. A queue sorted by "needs your decision" and a mute-with-recovery control are the concrete versions.
- Tooltip depth is a double-edged tool: nested explanation helps experts and confuses beginners if each answer opens more panels. Keep the first layer to the one number and its main causes.

### Gaps
- No quantified A/B evidence for forecasts, previews, undo, end-turn blockers or next-action suggestions in a strategy game.
- Hodent's "The Gamer's Brain" and CHI/CHI PLAY work on strategy legibility were not reached.

## 4. "Disconnected": making many subsystems feel like one game

### Takeaway
The only on-point evidence found is Paradox's journal (Victoria 3) and CK3's narrative-hook events, which tie teaching and objectives to one visible surface, and the Victoria 3 retrospective lesson to explain the "why". Reviewers of EU5 and Victoria 3 describe the pain as many interlocking systems with opaque cause and effect. No designer writing specifically on "shared currency" or "event text names its mechanical cause" was found.

### Cited Findings
- Victoria 3's journal is the single place where objectives, tutorial challenges and explanations live; entries are reactive to country and sequenced. — [Dev Diary 51](https://www.paradoxinteractive.com/games/victoria-3/news/dev-diary-51-tutorials)
- Victoria 3's retrospective (per search summary) says the team must focus more on the "why" of journal entries. — [Dev Diary 142](https://admin-forum.paradoxplaza.com/forum/developer-diary/victoria-3-dev-diary-142-2024-in-retrospect.1726056/page-3) (unverified wording)
- Tobold on EU5: "many more interlocking systems than EU4" is "hard to grasp"; he learned trade efficiency from community experiments, not in-game text. — [Tobold Nov 2025](https://tobolds.blogspot.com/2025/11/europa-universalis-v-first-impressions.html); [Tobold Apr 2026](https://tobolds.blogspot.com/2026/04/eu5-game-playing-itself.html?m=1)
- Paradox's EU5 1.1 reworked market screens to show supply and demand effects and the factors behind the estate economy, in answer to hard-to-find data. — [FinalBoss.io](https://finalboss.io/europa-universalis-5-rossbach-1-1-tackles-ui) (secondary)
- Scanlines (Substack) argues Victoria 3 is less opaque than its predecessor because it surfaces pressing issues such as goods shortages from the start. — [Scanlines](https://scanlines.substack.com/p/the-grand-strategy-game-that-rationalises) (search summary; one critic's opinion)

### Inferences
- A single home surface that lists "what needs you now, and why" (the journal pattern) is the nearest tested answer to "disconnected". Each entry should name the mechanic causing it.
- Event and letter text that names its mechanical cause is a design judgement here, not an evidenced practice; I found no source measuring it.

### Gaps
- No designer talk found on shared currencies or on showing cause-and-effect chains across subsystems.
- The Victoria 3 UX diary (DD 29) could not be fetched.

## 5. What new players most often complain about

### Takeaway
Recurring complaints across the launches checked: tutorial too long or too shallow; important events missed because of alert noise; hard-to-find information; too many clicks; missing hover information; nested windows. These appear in CK3 (2020 to 2022), Victoria 3 (2022), Old World (2021), EU5 (2025 to 2026) and Civ VII (2025).

### Cited Findings
- Tutorial length and quality: CK3 (Digital Trends: dense, long, boring; Paradox: 67 boxes), Old World (thin, a step behind), Unity of Command 2 ("not perfect"), EU5 (the "thousand hours" joke, onboarding "insufficient" per one review). Sources in Section 1.
- Alerts and missed events: EU5 (Tobold), Civ VII (Aftermath).
- Information hard to find or missing: Civ VII (CGM, Aftermath), EU5 hard-to-find data (FinalBoss), Victoria 3 economy poorly explained (Vaporlens aggregator, weaker source). — [Vaporlens Victoria 3](https://vaporlens.app/app/529340/victoria_3)
- Click count and micromanagement: Civ VII (queued movement), EU5 (excessive clicking, mass commands added).
- Nested or cluttered windows: EU5 (FinalBoss), Victoria 3 (Prima).
- Steam score context: Civ VII about 50 percent positive at launch snapshot (Notebookcheck); EU5 about 66 to 72 percent over snapshots. Scores reflect many causes, not just UI.
- Critics and players diverged in Civ VII and EU5 reception (critics warmer than Steam users), per the sources in Section 1.

### Inferences
- The user's playtester's "convoluted, opaque, disconnected" maps most closely to the alerts, missing-information and cause-and-effect complaints, not to tutorial length.

### Gaps
- No systematic review corpus was analysed; the complaints come from selected articles and summaries. Reddit threads and Steam review texts were not directly read (search results only).

## 6. Session-zero design: guided first scenario, small start, recommended picks

### Takeaway
Evidence points toward in-game, optional guidance with a small, recommended start. It is stated by developers and reviewers, with no measured comparison against a sandbox start.

### Cited Findings
- Victoria 3: tutorial as an optional objective, less aggressive AI under it by default, and Sweden and the USA recommended as starts. — [Dev Diary 51](https://www.paradoxinteractive.com/games/victoria-3/news/dev-diary-51-tutorials)
- CK3: five "Legends" historical starting characters, one per playstyle (secondary report). — [Mein-MMO](https://mein-mmo.de/en/steam-it-is-a-hard-game-that-hardly-anyone-finishes-now-it-wants-more-beginners,1113788)
- EU5: Tobold found the smallest recommended country (Holland) easier because guidance existed. — [Tobold](https://tobolds.blogspot.com/2025/11/europa-universalis-v-first-impressions.html)
- CK3 narrative-hook events as a softer onboarding layer (see Section 1). — [Game Developer](https://gamedeveloper.com/design/deep-dive-refreshing-the-crusader-kings-iii-tutorial-mode-through-optimized-ux)
- Tutorial that disables achievements in EU5 is criticised by Tobold because it penalises asking for help. — [Tobold](https://tobolds.blogspot.com/2025/11/europa-universalis-v-first-impressions.html)
- Old World players advise starting on the lowest difficulties (a guide, not a measurement). — [Re-Actor guide](https://re-actor.net/old-world-new-player-guide/)

### Inferences
- A guided first scenario with a narrow scope that widens, plus a recommended start, is consistent with every Paradox approach reviewed, but no source compares it to sandbox-first.

### Gaps
- No measured comparison of guided versus sandbox first sessions in this genre.
- Total War, Humankind, Stellaris and Shadow Empire first-session designs were not researched.

## Ranked practices for the report writer (by strength of evidence, with the caveat that rank reflects the sources found, not measured effect sizes)

1. Show the plan and the result: telegraph enemy intent and show outcome previews (Slay the Spire, Into the Breach, both developer statements). Strongest convergence, no measured effect.
2. Priority-sorted "needs you" alerts with mute and recovery (EU5 1.1, Civ VII complaints). Two major launches drew complaints on this in 2025.
3. In-flow teaching tied to an objective list that explains the "why" (Victoria 3 journal; CK3 narrative hooks). Developer intent only; no published results.
4. Short, optional, context-triggered lessons over a long linear tutorial (CK3 67 boxes cut to about a third; completion not predictive of retention).
5. Hover explanations of numbers, with a limit on nesting depth (Destructoid praise versus Prima confusion).
6. Cut clicks with bulk commands once the basics are learnt (EU5 1.1, Civ VII queued moves).
7. Small recommended start (Victoria 3, EU5 Holland).
8. Be careful with automation as an onboarding fix: helps, but hides cause and effect (GameWatcher, Tobold).
