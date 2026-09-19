# VERDICT:DESK-1 — **CONFIRMED** (P2 stands; the filed boot census *under*-states it)

Refutation pass against lens `desk`, finding DESK-1, at master `727cf88a`
(working tree clean, no repo file edited). Default verdict was REFUTED. It
survived every attack I made, and two of the attacks strengthened it.

Probes are mine, written from scratch, in
`…/scratchpad/cx_review/probes/refute_desk1/` (`harness.py`, `p1`…`p9`,
`fixplugin.py`). Every line quoted below came out of a run I did.

---

## 1. Does it reproduce, exactly as stated? — YES

`p1_repro.py`, fresh `build_world("1805")`, driven through `POST /command`
with the world/game_state/parser triple swapped:

```
turn 1  player France  AP 4
Kutuzov -> ('Russia', 'Podolia')
vis(Podolia) = unknown

> why not attack Kutuzov
No corps of ours stands within reach of Kutuzov at Podolia, Sire —
there is no battle to weigh.                                   [AP 4 -> 4]

> where is Kutuzov
We have no word of Kutuzov's whereabouts, Sire.                [AP 4 -> 4]

> what happens if I attack Kutuzov
No corps of ours stands within reach of Kutuzov at Podolia, Sire —
there is no battle to weigh.                                   [AP 4 -> 4]
```

My own strict census (`p2_attack_vectors.py`, part c) — every live enemy
corps on the boot board, with the branch taken:

| | |
|---|---|
| live enemy corps | 14 |
| cell PARTIAL/FULL (no leak) | 4 — Deroy/Franconia **full**, Mack/Swabia, ArchdukeJohn/Tyrol, Brunswick/Berlin **partial** |
| cell **UNKNOWN and the province named** | **10** |

ArchdukeCharles→Carniola, Kutuzov→Podolia, Buxhowden→Volhynia, Moore→London,
Hohenlohe→Silesia, Armfelt→Scania, Damas→Naples, Frederick→Jutland,
Castanos→La Mancha, Abdurrahman→Karaman. **The filed 10-of-14 is exact**, and
all ten sit in the `no-corps` branch — the four muster-branch cases are the
four the player can legitimately see.

*One filed figure I could not reproduce:* the t20 line reads "9 UNKNOWN +
1 STALE of 17". I measure the same **10 leaks (9 unknown + 1 stale)** but a
denominator of 12 live corps, not 17. The leak count is right; the
denominator is not, and nothing turns on it.

---

## 2. Did row CX ship it, or is it pre-existing? — **ROW CX (CX-2, `5fc3d5c8`)**

```
git show b4a27a15^:backend/ai/question_desk.py | grep -c _answer_what_if  -> 0
git show 5fc3d5c8 :backend/ai/question_desk.py | grep -c _answer_what_if  -> 2
```

The function does not exist before the row.

**And the disclosure is not pre-existing by another route either** — which is
the attack I expected to kill this finding and which instead made it worse.
`p2` part (a), same board, same turn:

```
> Ney, attack Kutuzov
    No intelligence on Kutuzov's position, Sire. Scout for him before
    Ney can give chase.                        [AP 4->4]  names Podolia: False
> attack Kutuzov
    No marshals in range of Kutuzov            [AP 4->4]  names Podolia: False
> Ney, pursue Kutuzov
    No intelligence on Kutuzov's position, Sire…  [AP 4->4] names Podolia: False
```

**The executor refuses fog-honestly and names nothing. The desk, asked the
same thing, names the province.** That is the exact inverse of
`_answer_what_if`'s own docstring — *"the player is told exactly what he
would be told a moment later."*

`p3` part (a) closed the other routes: `/ledger`, `/diplomatic_ledger`,
`/campaign_log`, `/marshal_overview` payloads contain neither `Kutuzov` nor
`Podolia`; the fog-filtered `game_state.enemies` holds exactly
`['ArchdukeJohn','Brunswick','Deroy','Mack']` — the four visible ones; and
`where is` / `what is X doing` / `how many men does X have` all refuse
correctly. **The what-if arm is the only route to this province.**

The contract it breaks is written in this row's own source **twice** —
`llm_client._askable_enemy_names` (≈343) and again ≈542: *"his POSITION is
the fogged half, and the desk answers it honestly ('no word of Kutuzov's
whereabouts')."*

---

## 3. Is the severity right? — **P2 stands, and the boot census is the weak half of the case**

The obvious refutation is that at boot all ten stand on their own home soil,
which a player could guess. I tested past it.

**It is a live tracker, not a boot disclosure** (`p2` part b) — move him and
the answer follows, free, every time:

```
boot     Podolia  (unknown) -> "…Kutuzov at Podolia…"
moved to Volhynia (unknown) -> "…Kutuzov at Volhynia…"
moved to Moravia  (unknown) -> "…Kutuzov at Moravia…"
```

**Mid-campaign it is bigger, and it names marching armies on foreign soil**
(`p7`, committed fixtures; `p9`, 24 ambient turns from boot):

| board | leaked |
|---|---|
| fixture t10 | 12 of 16 live corps |
| fixture t20 | 10 (9 unknown + 1 **stale**) |
| 24 ambient turns | **133 fogged at-war corps readings**; **15 of a fogged corps standing OFF its own soil** |

Those fifteen include, each invisible on the player's map and each named for
free at 0 AP:

```
t11  Kutuzov    of Russia  @ Moravia    (held by Austria)  at-war
t20  Paget      of Britain @ Normandy   (held by Austria)  at-war
t25  Moore      of Britain @ Limousin   (held by Austria)  at-war
t25  Shrapnel   of Britain @ Limousin   (held by Austria)  at-war
```

A British landing force inside France whose province the desk hands over is
not guessable home soil. The stale case is the subtler half: at t20 Brunswick
is at `stale`, where `_answer_enemy` gives a **dated** report and the what-if
arm states the **live** position as present fact.

Severity **not over-stated**. If anything the row should lead with the
Normandy/Limousin case rather than the boot list.

---

## 4. Is it player-reachable through the shipped client? — **YES, 8 of 8**

I re-implemented `_redirect_diplomatic_command` in Python from main.gd's own
constant blocks, parsed out of the `.gd` source rather than transcribed
(`p8`, part b; advisory=7, nohome=18, warroom=2, family=115, nation_any=13,
exempt=20):

```
REACHES | what happens if I attack Kutuzov   | advisory (wh-word 'what')
REACHES | should I attack Kutuzov            | fail-open -> BACKEND
REACHES | why not attack Kutuzov             | advisory (wh-word 'why')
REACHES | what about attacking Kutuzov       | advisory (wh-word 'what')
REACHES | is it time to attack Kutuzov       | fail-open -> BACKEND
REACHES | what if we attack Kutuzov          | advisory (wh-word 'what')
REACHES | could I attack Kutuzov             | fail-open -> BACKEND
REACHES | how about we attack Kutuzov        | advisory (wh-word 'how')
```

`"attack"` is **not** a `DIPLO_FAMILY_KEYWORD`; it appears in main.gd only in
`DIPLO_ADDRESS_EXEMPT_WORDS`, which *exempts* rather than claims. Five
phrasings are exempted as wh-word advisories, three fail open. Nothing is
eaten.

---

## 5. Would the suggested fix ship a regression? — **NO**, measured two ways

**(a) Injected and run.** `fixplugin.py` is a pytest plugin that patches
`question_desk._answer_what_if` with the exact suggested gate
(`visibility_at_least(PARTIAL)` → `_answer_enemy`'s own "no word" line) at
session start. No repo file touched.

```
BASELINE : cx1 + cx2 + cx3 + test_fog_of_war + fa_slice7   -> 390 passed
WITH FIX : same five files, plugin loaded                  -> 390 passed
```

**Zero pins red.** The flagship pin `what happens if I attack Mack` survives
because Mack's cell is **partial** at boot. `p3` part (b) walked all eleven
attack-shaped utterances the row's own tests pin; the one that appeared to
change was chased down in `p4` and is the once-per-campaign muster hint
latching on first use, not the fix (`call 0: len=1253, calls 1-3: len=1137`,
unpatched).

**(b) Why it is safe structurally — the invariant, measured.** The candidate
set `_answer_what_if` builds is "own corps co-located with, or adjacent to,
the foe". `calculate_visibility` gives FULL to a marshal's own cell (step 0)
and PARTIAL to every cell adjacent to a friendly army (step 2). I checked the
one window that would break this — a corps marching adjacent **mid-turn**,
before end-of-turn recompute — and it does not exist (`p5`): the move itself
refreshes, measured `Bernadotte, move to Bohemia` → `vis(Carniola)` goes
**unknown → partial** inside that one command.

So *candidates non-empty ⟹ cell is PARTIAL+*, measured with **0 violations**
across boot, t2–t7, fixture t10 and fixture t20 (`p6`, `p7`). The gate can
fire **only** on the no-corps branch; it cannot suppress a muster for a
battle the player could really fight.

**(c) And the gate is sufficient, not merely necessary.** I checked whether
the muster branch leaks strength at PARTIAL, which would have made the fix
incomplete. It does not — it is already band-honest and matches
`_answer_enemy` exactly (`p8`, part a):

```
Mack  @Swabia    partial  true 52,000 -> "Mack (large force)"     exact printed: False
Deroy @Franconia full     true 22,000 -> "Deroy (22,000 men)"     exact printed: True
```

`STALE` ranks 2 against `PARTIAL` 3, so the gate also covers the stale case.

**The one caution worth writing on the row:** do not narrow it by reaching
for `world.get_visible_enemies()` instead — that would also stop the desk
answering about an **ally's** marshal at Franconia (Deroy, FULL, reachable
today), which `_answer_enemy` deliberately answers per its own R3-4 note.
Gate on the cell, as filed.

---

## Verdict

**CONFIRMED, P2, player-reachable, shipped by row CX (CX-2 `5fc3d5c8`).**
The fix as filed is correct, sufficient, and reds nothing.
