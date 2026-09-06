"""How small an engagement is too small to be called a battle.

FA-S16-D3 (FA-44). Berthier told the player *"Even the favorable ground
could not save Massena, Sire"* about an exchange of **one casualty against
fifty-eight** — because `battle_report._pick_observation` had no scale gate
anywhere in its ladder. It reached the same gravity verdicts for a
skirmish that it reached for Austerlitz.

**The ruling was not "add a floor." It was "stop having a fourth opinion."**
The engine already answered this question in four different places, with
three different numbers and three different shapes, and a `MIN_CASUALTIES`
grep finds only one of them:

  1. `diplomacy.record_battle` — **the SUM of both sides**, a bare `1000`
     below which a battle earns no war score at all. *This module now owns
     that number*, and the narrator reads the same one, so the engine can
     never again say "not a battle" at 900 while Berthier says "a grievous
     defeat" at 600.
  2. `dispatch.OWN_MAULED_MIN_CASUALTIES = 500` — **ONE side's** dead, ANDed
     with `>= 25%` of that corps. A different quantity in a different shape,
     and it carries a written dissent (WO-16: "if 500 is tuned TWICE, take
     the fraction-of-national-strength form"). ⚠ It is deliberately NOT
     reused here and deliberately NOT tuned; reading a one-sided constant
     against a two-sided total gives it two referents a factor of two apart.
  3. `coalition.add_war_exhaustion_from_battle` — `casualties // 1000`,
     per side, across fourteen call sites. The same idea as (1) expressed
     as a rate rather than a gate; re-plumbing it would move war exhaustion
     and is out of scope.
  4. `battle_report._pick_bombardment_observation` — a **3% FRACTION** of
     the target's strength. Unfiled and unfindable by grep. It does not
     answer FA-44's case (58 casualties on a 58-man corps is 100% of it,
     which is WO-16's remnant lesson again), but a record that claims
     "there are two floors" after this build is wrong.

**Absolute, not proportional, and that was measured rather than assumed.**
A fraction of NATIONAL strength is 1,890 at boot and 1,196 by turn 20 while
the corps producing these lines have fallen to 1,148 and 593 — it drifts
away from the very case it would be built for.

**What the gate covers, honestly.** It is applied per-arm to the five
GRAVITY verdicts — the two terrain arms, the narrow-defeat arm, the costly
-defeat arm, and the costly-VICTORY arm — plus one terminal arm above the
default. It is deliberately NOT applied to any arm that reports a
mechanical STATE: a rout, guns caught in transit, cavalry riding down a
battery, a fort destroyed, an overwatch battery repelling an attack. Those
are facts the player must have at any scale, and PT-D4 landed the rout arm
five slices ago for exactly that reason.

⚠ **Two stated limits.** (a) The coordination family — seventy archived
sub-floor lines, including *"even together, the field could not be held"*
at a total of **one** — is sited ABOVE every candidate gate and is out of
scope; the gate covers the sub-floor loss population minus about a fifth.
(b) `we_lost` is computed against `player_nation`, so in a third-party
AI-vs-AI battle France "loses" whenever the attacker wins; coverage of
those is arbitrary. Pre-existing, not caused by this gate — but do not
write that the gate covers every battle.
"""

# ⚠ FLIP LEVER. False reproduces the pre-FA-S16-D3 narration exactly: every
# gravity verdict fires at any scale, and there is no terminal skirmish arm.
# The war-score gate does NOT read this lever — it read 1000 before this
# module existed and it reads 1000 after, whichever way the lever points.
SKIRMISH_GATE_ACTIVE = True

# The one number, in a home neither reader owns. ⚠ Both readers MUST resolve
# it as a module attribute at call time (`battle_scale.MIN_BATTLE_CASUALTIES`),
# never `from ... import MIN_BATTLE_CASUALTIES` — a from-import binds a copy,
# and the drift pin that monkeypatches one home and asserts both readers move
# is unsatisfiable against a copy.
#
# ⚠ It lives here rather than in either reader because neither imports the
# other today, directly or transitively at import time (measured). A
# module-level edge from a display module to the rules module on `combat.py`'s
# import path would be the first cycle of its kind.
MIN_BATTLE_CASUALTIES = 1000


def is_a_battle(total_casualties) -> bool:
    """True when an engagement is large enough to be spoken of as a battle.

    Reads the constant off the module at call time, on purpose — see above.
    """
    try:
        return int(total_casualties) >= MIN_BATTLE_CASUALTIES
    except (TypeError, ValueError):
        return True  # unreadable input is never silently downgraded
