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


# The war score's own DECISIVE test (diplomacy.record_battle, unchanged since
# Phase 8): a blood exchange above DECISIVE_MIN_CASUALTIES in which one side
# bled more than DECISIVE_RATIO times the other. F4 "The fuse is longer"
# (ENDGAME_PLAN §1 F4, Sept 24 2026) made it a named predicate because a
# second reader arrived — the reward curve's "decisive victory as lead" — and
# a second inline copy of `> 10000 and ratio > 2.0` is the drift pattern this
# codebase keeps paying for. The two threat arms in combat_executor keep their
# older inline copies (both combat copies, pinned byte-identical elsewhere).
DECISIVE_MIN_CASUALTIES = 10000
DECISIVE_RATIO = 2.0


def is_decisive_exchange(side_a_casualties, side_b_casualties) -> bool:
    """True when the exchange itself was decisive, whoever won it."""
    try:
        a = int(side_a_casualties)
        b = int(side_b_casualties)
    except (TypeError, ValueError):
        return False
    if a + b <= DECISIVE_MIN_CASUALTIES or a <= 0 or b <= 0:
        return False
    return max(a, b) / min(a, b) > DECISIVE_RATIO


# PC-F6 (the Peace Conundrum F6, October 15, 2026): WHOSE decisive it is.
# `is_decisive_exchange` asks only whether the exchange was lopsided; the war
# score credited it to `winner_nation` without asking who bled, so Massena's
# repulse at Vienna — the garrison held, 8,485 Austrian dead to 2,872 French —
# was booked as a decisive AUSTRIAN victory and took the war's last decisive
# slot. The ruling: a decisive is the WINNER's only when the winner inflicted
# the exchange (the reading the two threat arms in combat_executor and the
# auto-charge already made with their own directional ratio). A victory won at
# 2:1 cost books none; neither does a repulse the attacker bled at 3:1 — the
# side that won the exchange did not win the field, and the war score's blood
# component already prices the dead. A garrison that holds still books a
# defender victory: the city stood.
def is_decisive_victory_exchange(winner_casualties, loser_casualties) -> bool:
    """True when the exchange was decisive AND the winner inflicted it — the
    ONE predicate the war score, the settlement contribution and the reward
    curve read (the series attribution patches this seam)."""
    try:
        won = int(winner_casualties)
        lost = int(loser_casualties)
    except (TypeError, ValueError):
        return False
    return is_decisive_exchange(won, lost) and won < lost


def decisive_credit(attacker_nation, defender_nation, winner_nation,
                    attacker_casualties, defender_casualties):
    """The nation a battle's decisive bonus is credited to — the winner, when
    the winner inflicted the decisive exchange — or None."""
    if winner_nation == attacker_nation:
        won, lost = attacker_casualties, defender_casualties
    elif winner_nation == defender_nation:
        won, lost = defender_casualties, attacker_casualties
    else:
        return None
    return winner_nation if is_decisive_victory_exchange(won, lost) else None


def drop_misbooked_decisives(battle_records, decisive_battles) -> int:
    """PC-F6, on load: a save written before the fix may hold a decisive
    credited to a winner who BLED (the live 1805 campaign's Vienna repulse).
    A legacy record (no `location`) whose battle row is still kept — same
    turn, same winner, same dead — and which `decisive_credit` would not
    credit to that winner is dropped; a record whose battle has been pruned
    cannot be checked and is kept. Mutates `decisive_battles`; returns the
    number dropped."""
    dropped = 0
    for key, decisives in (decisive_battles or {}).items():
        rows = (battle_records or {}).get(key) or []
        kept = []
        for d in decisives:
            if d.get("location") is not None:
                kept.append(d)
                continue
            twins = [r for r in rows
                     if r.get("turn") == d.get("turn") and r.get("winner") == d.get("winner")
                     and int(r.get("attacker_casualties", 0) or 0)
                     + int(r.get("defender_casualties", 0) or 0)
                     == int(d.get("total_casualties", -1) or -1)]
            if twins and not any(
                    decisive_credit(r.get("attacker"), r.get("defender"), r.get("winner"),
                                    r.get("attacker_casualties", 0),
                                    r.get("defender_casualties", 0))
                    for r in twins):
                dropped += 1
                continue
            kept.append(d)
        decisives[:] = kept
    return dropped
