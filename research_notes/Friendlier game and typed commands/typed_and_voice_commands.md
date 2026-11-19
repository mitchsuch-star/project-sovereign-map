# Typed and spoken commands as a way to play games (notes as of November 2026)

Method note: about 18 searches/fetches. Search snippets were often AI-summarised; where I only had a snippet, I say so. Steam counts are third-party tracker snapshots and drift; treat as approximate. Several named games (Hacknet, Stories Untold, Quadrilateral Cowboy, The Roottrees Are Dead, Type Help, TIS-100, Star Trek Bridge Crew, Lifeline, Bot Colony, Starship Commander, Paradox consoles, Dwarf Fortress, MUDs) were NOT researched; see Gaps. No LLM-game material included (other researcher).

## 1. Why parser games lost the mainstream; how modern IF softened the parser

### Takeaway
The parser's core defect, as designers named it, is that the prompt promises "anything" but accepts only what the author implemented, so players guess the words ("guess the verb") and cannot see what is possible. Sierra and LucasArts replaced typing with visible verbs/mouse around 1987-1990 for exactly that reason. Modern IF keeps the expressive upside and removes the guessing with visible hooks (links, suggested verbs, teaching errors).

### Cited Findings
- Guess-the-verb is the named trope: the player must hit the exact verb or phrasing the author intended (e.g. "use crank" answered by "how do you want to use the crank?"). — [TV Tropes, Guess the Verb](https://www.tvtropes.org/pmwiki/pmwiki.php/Main/GuessTheVerb) (opinion/wiki, undated)
- Maniac Mansion's verb-object interface (1987) was designed to eradicate the command-line guessing game; all commands were put on screen. — [PC Gamer on Maniac Mansion's interface](https://www.pcgamer.com/how-maniac-mansions-verb-object-interface-revolutionised-adventure-games) (snippet only; retrospective journalism)
- Ron Gilbert's 1989 essay "Why Adventure Games Suck" appeared in Chris Crawford's Journal of Computer Game Design (per Filfre). I could not retrieve its full text, so I cannot quote its specific parser arguments. In a later interview Gilbert said the difficulty was "a product of poor design more than anything" and that 1990s puzzles became arbitrary. — [Digital Antiquarian (Filfre) post, July 2015](https://www.filfre.net/2015/07/31/); [engineered.at essay index](https://engineered.at/topics/game-persistence) (snippets only)
- King's Quest V (1990) was Sierra's first main-series game to drop the typed parser for point-and-click; Conquests of Camelot (1990) is called one of Sierra's last parser games; Filfre frames it as "a slow move away from text" and does not condemn the parser itself. — [Filfre, "Sierra at the Cusp of the Multimedia Age," Jan 2018](https://www.filfre.net/2018/01/sierra-at-the-cusp-of-the-multimedia-age)
- Sierra's design differed from LucasArts': verbs became cursor modes that persist until changed. Designer Scott Murphy recalled his team wanted to keep the parser but management (Ken Williams) had decided on point-and-click for KQ5 and Space Quest IV. A 1991 review praised the "non-typing parser" alongside VGA graphics (via Wikipedia sourcing). — [Wiki summary via search; King's Quest V, SierraHelp](https://wiki.sierrahelp.com/index.php/King%27s_Quest_V); [Hacker-news mirror of Ars Technica history of graphic adventures, 2011](https://hn.jakechampion.name/reader/https://arstechnica.com/gaming/2011/01/history-of-graphic-adventures) (snippets only; the Murphy quote was not verified at source)
- Graham Nelson's "A Bill of Player's Rights" (Usenet, May 1993, later in The Craft of Adventure) opens: "fine line between a challenge and a nuisance"; the designer must think first as a player. It is about fair play more than the parser, and one forum summary notes the parser is the area where authors have least control. — [AGI Wiki copy](https://www.agiwiki.sierrahelp.com/index.php/The_Craft_of_Adventure_-_A_Bill_of_Player%27s_Rights); [IF Archive PDF](https://origin.ifarchive.org/if-archive/info/Craft.Of.Adventure.T1.A4.pdf) (I did not read the full list)
- Emily Short (blog, June 2010), read directly: the parser prompt implies anything can be typed, which is misleading ("a lie"); costs = novice frustration, guess-the-verb, paralysis of choice, authoring overhead for absurd input, failed NLP alternatives. Benefits = breadth of verbs/nouns, discovery of surprising actions, and typing in the same idiom as the output feels more engaging than menus. Middle grounds she lists: highlighted nouns, suggested commands, tutorial modes, autocomplete (risk: reveals puzzle solutions). Her proposal: select a noun, see only the verbs the author implemented ("no defaults": a verb exists only when a response exists), with typing still allowed. She says she is not ready to abandon the parser. — [Emily Short, "So, Do We Need This Parser Thing Anyway?"](https://emshort.blog/2010/06/07/so-do-we-need-this-parser-thing-anyway/) (first ~100k characters read; opinion by an expert practitioner)
- IFWiki documents "parser-choice hybrids" (a full world model behind choice-style links/buttons) with examples including Texture and Contrition; Short notes Quest can drive a parser narrative through hyperlinks. A forum thread is sceptical that hybrid input is elegant unless the choice and parsed situations are sharply differentiated. — [IFWiki, Parser-choice hybrid](https://www.ifwiki.org/Parser-choice_hybrid); [intfiction.org thread](https://intfiction.org/t/alternates-to-natural-language-parsing/5271) (snippets)
- Short also wrote later posts on this ("IF Only: Text Adventures For People Who Hate Guessing The Verb", 2016; "Mailbag: The Unique Selling Points of Parser IF", May 2017); I did not open them. — [Mailbag, 2017](https://emshort.blog/2017/05/04/mailbag-the-endangered-art-of-parser-if/)

### Inferences
- The strongest design verdict from the history is not "typing is bad" but "invisible affordances are bad": every softening technique (visible verbs, noun highlighting, suggestions, no-defaults) works by making possibilities recognisable.
- Short's "typing in the output's idiom feels more involved" is the one pro-parser argument that survives; it is an engagement/immersion claim, not a speed claim, and is opinion.
- The user's complaint ("need to look up names") is the same defect in a new costume: a recall burden on proper nouns rather than verbs.

### Gaps
- Gilbert's essay text and Sierra designers' contemporaneous judgments (primary interviews) not retrieved; no sales data comparing parser vs point-and-click titles found.
- Nelson's full list of rights not read.

## 2. HCI evidence: recognition vs recall, command line vs menus, command palettes

### Takeaway
No controlled study I found shows typed commands beating menus/GUI for novices; the classic 1985 comparison found implementation quality mattered more than style. Command palettes and typeahead are practitioner-reported hybrids that work by turning recall into recognition while staying optional for experts; no published measurement of palettes specifically found.

### Cited Findings
- Whiteside, Jones, Levy and Wixon (CHI '85), 76 users, 7 interfaces across command, menu and iconic styles: large usability differences between systems, suggesting careful crafting mattered more than style; no evidence of a learnability/usability trade-off; feedback, input forms, help and navigation aids were problem areas in all three styles. (From abstracts/indexing only; full text not read.) — [Bohrium abstract](https://www.bohrium.com/paper-details/user-performance-with-command-menu-and-iconic-interfaces/812025262521712640-18187); [Good et al. publication list](https://michaelgood.info/publications/usability/building-a-user-derived-interface/)
- Recognition-over-recall is Nielsen's heuristic: make objects, actions and options visible so users need not remember. Alan Dix's glossary says recognition-based techniques tend to be easier to learn and use, and that command lines can reduce memory load with autocomplete or templates. — [Alan Dix glossary](https://alandix.com/glossary/ai4hci/recognition%20rather%20than%20recall) (search summary)
- A CHI '95 paper states theories of display-based interaction assume recognition, not recall, drives interaction (a theoretical assumption, not an experiment). — [CHI '95 proceedings](https://chi1995.chistatic.hosting.acm.org/proceedings/papers/mf_bdy.htm); a UBC paper (Hendy et al., GI 2010) says visible commands make GUIs easier to learn and less error-prone and studies showing accelerators to ease the move to expert use — [GEKA paper](https://www.cs.ubc.ca/~joanna/papers/GI2010_Hendy.pdf)
- Palette practitioner writing: a palette is "a modal autocomplete" (Rob Dodson); typing a half-remembered fragment surfaces the command; recall starts the interaction and recognition finishes it (a design case study); helps discover rarely used commands; avoids memorising shortcuts. — [Rob Dodson](https://robdodson.me/command-palettes/); [Command.ai history](https://command.ai/blog/command-palette-past-present-and-future); [Steve Kinney on VS Code](https://stevekinney.com/courses/visual-studio-code/vscode-command-palette) (all opinion/practitioner; some search hits were AI-generated summaries I discarded)

### Inferences
- The consistent mechanism across palettes and IF softening is: type a fragment, pick from a visible list. Applied to the game, a typed line that autocompletes marshal/place names and verbs keeps the keyboard's speed and removes the lookup.
- Whiteside's lesson (execution quality over style) supports "fix the lookup problem" over "cut the input style".

### Gaps
- No NN/g study directly comparing CLI vs GUI for novices vs experts located; no published speed/error numbers for command palettes; no study specific to games.

## 3. Games where typing is the celebrated core

### Takeaway
Typing-core games sell when the keyboard is justified by the fiction, the player is acting under tension or expressing something a button cannot, and vocabulary is discoverable inside play. Complaints cluster on repetition, learning curve and having to think of words with no cues.

### Cited Findings
- Duskers (2016): Metacritic 83 from 10 critics (9 positive, 0 negative), user score 6.5 from 22; Steam about 90% positive from roughly 2,300-2,750 reviews (tracker snapshots). Reviewers: instructions to drones are typed; commands chain with semicolons including multiple drones; typing under time pressure creates tension. Complaints: slow pace, command learning curve, typing similar commands repeatedly. — [Metacritic (legacy)](https://legacy.prod.metacritic.com/game/pc/duskers/critic-reviews); [GamingOnLinux review, May 2016](https://www.gamingonlinux.com/2016/05/duskers-leaves-early-access-heres-a-review/page=1/); [Christ Centered Gamer review](https://www.christcenteredgamer.com/reviews/pc-mac/duskers-pc)
- Cryptmaster (2024): Metacritic 77 (12 critics), OpenCritic 76 with 85% recommending; Steam 94% positive from about 1,660 reviews (gg.deals, undated). Reviewers: every action (open a chest, swing a sword) needs a word you work out from letter clues; the card side-games were weaker; one reviewer spent 3-5 minutes thinking of words from a couple of letters. — [OpenCritic](https://opencritic.com/game/16681/cryptmaster/reviews); [Metacritic (legacy)](https://legacy.prod.metacritic.com/game/pc/cryptmaster/critic-reviews); [gg.deals](https://gg.deals/game/cryptmaster/); [Press Start review, May 2024](https://press-start.com.au/reviews/pc-reviews/2024/05/10/cryptmaster-review-words-are-weapons/)
- Event[0] (2016): Metacritic 75 (34 critics), user 7.0; OpenCritic 74; Steam "Very Positive", about 80% positive from about 2,280 (Steambase, 2026). Critics split: enjoyment depends on whether you like chatting; procedurally generated reply volume does not fully hide limits of the free-text parser. — [Steambase](https://steambase.io/games/event-0/reviews); [PC Gamer review](https://pcgamer.com/event0-review); [Metacritic (legacy)](https://legacy.prod.metacritic.com/game/pc/event0/critic-reviews)
- Her Story: Metacritic 86 (Deku Deals listing); Steam Very Positive, 5,000-10,000 reviews depending on tracker. The store text says players explore a database by typing search terms. Typing here is the discovery act itself, with no commands to learn. — [Deku Deals](https://www.dekudeals.com/items/her-story?platform=all); [Steam store](https://store.steampowered.com/app/368370)
- The Typing of the Dead: Overkill: Steam 87% positive, about 2,400 reviews. — [Steam store](https://store.steampowered.com/app/246580/The_Typing_of_The_Dead_Overkill/) (no review commentary gathered)

### Inferences
- The three successes (Duskers, Cryptmaster, Her Story) each make typing the verb that the fiction is about (a terminal, spell-words, a search). Event[0]'s weaker critic scores track the unbounded free-text part.
- Cryptmaster's 3-5-minute complaint shows what happens when recall is demanded with weak cues; Duskers' chained-command praise shows the expert-accelerator upside.
- These are mostly 2016-era or niche titles; none is a strategy game with a click alternative.

### Gaps
- Not researched or no data found: Hacknet, Stories Untold, Quadrilateral Cowboy, TIS-100 (no Steam data returned), Epistory, The Roottrees Are Dead, Type Help. Review commentary for Typing of the Dead not gathered. Metacritic user scores are tiny samples.

## 4. Voice/natural-language orders in strategy and tactics

### Takeaway
Voice orders are praised as an immersion hook and for recognition quality in constrained vocabularies, but reviewers repeatedly say they are slower than buttons and shallow beyond the novelty, and a developer put numbers on why they are fragile.

### Cited Findings
- EndWar (2008): Metacritic 77 (Xbox 360, 63 critics, user 8.4), 76 (PS3, 33 critics, user 7.0). Critics singled out voice control as the best/defining feature; also said the rest was repetitive and shallow, voice works well only in a limited setting (Softpedia: with more units it would become overwhelming); GameSpot: a standard headset recognised most but not all commands. — [Metacritic X360](https://legacy.prod.metacritic.com/game/xbox-360/tom-clancys-endwar/critic-reviews); [Kotaku review](https://kotaku.com/tom-clancys-endwar-review-vocal-annihilation-5086994); [Softpedia](https://www.softpedia.com/reviews/games/playstation3/Tom-Clancy-039-s-EndWar-Review-102157.shtml); [GameSpot](https://www.gamespot.com/reviews/tom-clancys-endwar-review/1900-6205359/)
- There Came an Echo (2015): recognition praised (Destructoid "superb", troubles only when many commands rapid-fire; accented English supported; custom commands possible); but High Def Digest says most commands are facsimiles of a button press with little expediency, Push Square says once novelty fades it does little to engage, others call other systems shallow; text versions via radial menu exist. No postmortem found. — [Destructoid](https://vip-develop.destructoid.com/?p=160318); [High Def Digest](https://games.highdefdigest.com/18806/there_came_an_echo_pc.html); [Push Square](https://www.pushsquare.com/reviews/ps4/there_came_an_echo); [GameSpot](https://www.gamespot.com/games/there-came-an-echo/reviews/)
- Radio General (developer post, pre-release): wanted EndWar-like voice command; says voice is "slower than mouse and keyboard", out-of-box accuracy about 70% was too low (a third of failures would frustrate an RTS); fixes: unique phonetic unit names, grammar "<RECIPIENTS> <ORDER> <EXTRA>", a restricted dictionary, NATO letters for grid squares, mid-speech feedback showing remaining words; accents and microphones vary. — [Game Developer](https://gamedeveloper.com/audio/the-journey-to-speech-recognition-and-how-to-do-it-yourself) (developer opinion, undated)
- Radio General store page: Very Positive, about 500 reviews (snapshots vary), speech English-only. Radio Commander: Vietnam '64: Mostly Positive, about 1,750 reviews; voice optional; some users report recognition fails (from a third-party AI summary, indicative only). — [Steam: Radio General](https://store.steampowered.com/app/1011610/); [Steam: Radio Commander](https://store.steampowered.com/app/871530)

### Inferences
- Even the best-received voice games ship an alternate input, and critics frame voice as the mode that creates mood, not the fastest mode. This matches the game's own measurement that clicking is faster per order.
- Radio General's design (named recipients, fixed grammar, live feedback) is effectively a typed-command-with-autocomplete design; it transfers directly to a text bar.

### Gaps
- No postmortem for EndWar or There Came an Echo found; no independent Radio General reviews found; Lifeline, Bot Colony, Starship Commander, Bridge Crew voice mode not researched; no data on how many players abandoned voice for mouse.

## 5. Optional consoles/command bars in strategy and management games

### Takeaway
Not researched; no evidence collected.

### Cited Findings
- (none)

### Inferences
- Palette literature in section 2 is the nearest evidence.

### Gaps
- Paradox consoles, Dwarf Fortress, roguelike keys, MUDs not searched; no usage data located. A report writer should flag this as unevidenced.

## 6. Synthesis: when typed input is worth it, when it is a chore

### Takeaway
The evidence supports keeping typing only as an optional, suggestion-backed layer that earns its place by doing what buttons cannot (free questions, multi-army one-liners, expressive character replies); as a primary or only path for single orders it is a chore.

### Cited Findings (condensed from above)
- Worth it: fiction justifies the keyboard and tension rewards speed (Duskers); chaining several commands in one line (Duskers semicolons); expressiveness and discovery (Short); recall removed by autocomplete/templates (Dix, palette writers); constrained vocabulary and live feedback (Radio General); optional alongside menus (There Came an Echo radial menu; Radio Commander optional voice).
- Chore: unseen vocabulary and guess-the-verb (Short, Gilbert, Maniac Mansion); thinking of words with weak cues (Cryptmaster); repeating similar commands (Duskers review); voice or text that merely duplicates a button without speed gain (High Def Digest on Echo); failure rate (Radio General 70% figure); shallow rest of game (EndWar, Echo reviews).

### Inferences
- Reshape, not cut or keep-as-is: (1) autocomplete/type-ahead for marshal and place names so nothing needs looking up; (2) show what the line can do (suggested chips, Short's "no defaults": only offer verbs that have a response); (3) lean on what clicking cannot do, namely questions and multi-army lines; (4) make replies characterful, since Short's engagement argument and the typing-core hits depend on voice and response; (5) keep it clearly optional.
- Caution: all review data are for games where typing/voice is the core, or for voice novelty; I found no evidence on a typed bar in a mouse-first strategy game, so the "keep as optional accelerator" conclusion rests on HCI reasoning and analogy (palettes), not direct measurement.

### Gaps
- No controlled experiment on typed vs clicked orders in games; no published numbers on how often players use optional console/command bars.
