"""
Morning Dispatch — Berthier's turn-start briefing (Phase 6.5)

Builds a structured dict for Godot to render as terminal output at turn start.
All values int()-wrapped per CLAUDE.md rule: "All numbers to Godot: int()".

Fog-filtered: enemy intel uses RegionIntel visibility, never raw marshal data.
"""

from typing import Dict, List, Optional, Any

from backend.display_names import (
    humanize_entity_name, marshal_honorific, with_definite_article,
)
from backend.nation_config import get_player_nation
from backend.models.intel import (
    FULL, PARTIAL, STALE, LAST_KNOWN, UNKNOWN,
    get_strength_band,
)
from backend.game_logic.commitments_routing import (
    COMMITMENTS_ROUTES,
    commitments_priority,
    format_commitments_notice,
)
from backend.game_logic.settlement_presentation import (
    SETTLEMENT_PRIMARY_BEAT_CAP,
    cap_settlement_dispatch_lines,
    compose_digest_oneliner,
    compose_summary_oneliner,
    is_settlement_event_type,
    is_settlement_event_visible,
    settlement_priority,
)
from backend.game_logic.formations import formed_display_name


# ============================================================================
# STRENGTH BAND MIDPOINTS — for estimating enemy strength from fog intel
# ============================================================================
# Maps band string -> midpoint estimate (used for threat ratio calculation)
BAND_MIDPOINTS: Dict[str, int] = {
    "no forces": 0,
    "screening force": 2500,
    "small force": 10000,
    "substantial force": 27500,
    "large force": 55000,
    "massive force": 85000,
}


# ============================================================================
# W6-3 THE DISPATCH REWRITE — "Berthier tells the story" (EXP-N1)
# ============================================================================
# Headline weights (blessed defaults — display only, tunable freely).
# The dispatch opens with the top-scored fog-visible event of the turn
# rendered as one prose sentence, plus up to 2 sub-beats.
# ── FA slice 11 flip levers ────────────────────────────────────────────
# False restores the pre-slice briefing at each seam independently.
SOIL_ALARM_IS_ONE_RUN = True          # FA-12
SOIL_ALARM_IS_HOME_SOIL_ONLY = True   # FA-N14
THE_SHELLING_IS_BRIEFED = True        # FA-25
A_LOST_SATELLITE_CAN_LEAD = True      # FA-38

HEADLINE_WEIGHTS: Dict[str, int] = {
    # NP-4 (NAPOLEON_SPEC §7.2): the Eagle in Chains outranks even a
    # fallen homeland province — the Empire is a PERSON, and the person is
    # in an enemy cell (the Malet coup ran on a rumor of less).
    "sovereign_captured": 101,
    # ── WO-D6 (row WO slice 4, Aug 22 2026): "The Capital Speaks" ───────
    # The fall of the player's OWN capital was narrated with the template
    # Limousin gets three turns later. Measured on the 1805 board, four
    # homeland provinces lost in one turn: with Paris logged LAST the page
    # read "Limousin has fallen / Berry / Normandy" and PARIS WAS NOT ON
    # IT AT ALL — four candidates at one weight, sorted stably, and only
    # three slots. It sits one BELOW `sovereign_captured` because NP-4's
    # ruling stands: the Empire is a person before it is a place.
    "capital_lost": 100,
    "home_captured": 99,        # own homeland region captured by enemy
    # PC15-1: annihilation outranks capture — a prisoner can be ransomed,
    # a destroyed corps is gone for good. One above marshal_captured.
    "marshal_destroyed": 96,
    "marshal_captured": 95,     # W6-7 capture events (top-weight per spec)
    # ── CA8-26 / gate CA8-D6 (close-out gate 10.2, Aug 7 2026) ──────────
    # The dispatch finally has headline classes for a FRENCH SUCCESS. The
    # measured campaign produced 14 of 14 misfortune headlines, and on the
    # turn France stormed Vienna AND Austria was eliminated the lead was a
    # supply nag. The weight principle that replaces the old absolute: at
    # equal scale the wound still leads; a triumph outranks only a wound of
    # SMALLER scale than itself. Elimination and a stormed capital beat a
    # broken corps (Vienna is bigger news than one corps reforming); a
    # decisive field victory beats the standing hunger nag on the day it is
    # won but not a lost province; a routine conquest sits below every
    # direct wound to France's own body.
    "enemy_eliminated": 93,     # a court France fought is knocked out
    "capital_stormed": 92,      # France takes an enemy CAPITAL
    # CA8-9 (creative audit, Aug 4 2026): a marshal's fall told together
    # with the rise it reverses. Ranked one ABOVE the bare `own_broken` for
    # exactly the reason `region_lost_estate` sits above `region_lost` — it
    # is the SAME event told better, and one of the two sentences is about a
    # man with a history. It absorbs the plain fall candidate for that
    # marshal rather than sitting on top of it (see `_build_headline`), so
    # the sub-beat never restates the headline.
    "marshal_reversal": 91,
    "own_broken": 90,           # own marshal broken / force-retreated
    # FA-38 (slice 11): losing a SATELLITE could not lead the briefing at
    # all. Measured: Holland bribed away, Switzerland eliminated and Berry
    # lost in one tick led with "Berry has fallen" and EMPTY sub-beats; with
    # only the satellites lost the headline was None and the whole page was
    # a supply nag. A satellite is a province's worth of empire and a
    # standing army, so it ranks above a bare province (`region_lost` 75)
    # and below a broken corps of our own (90) — at equal scale the wound to
    # our own body still leads.
    "vassal_lost": 84,
    # ── CA9-F12: the mirror of the file's top-weight wound ──────────────
    # An enemy commander taken is PERMANENT, and it contains a decisive
    # field win (73) — it is that win plus the man. It sits BELOW
    # `own_broken` (90) because CA8-D6's principle is "at equal scale the
    # wound still leads", and below `capital_stormed` (92) /
    # `enemy_eliminated` (93) so the triumph ladder stays ordered by its
    # own scale. In-band tunable.
    "enemy_marshal_captured": 88,
    # PC15-1: the destroyed mirror — permanent, so one above the capture
    # mirror; still below own_broken 90 (at equal scale the wound leads).
    "enemy_marshal_destroyed": 89,
    "own_mauled": 85,           # own marshal lost >=25% strength
    # ── FA-R5 (slice 14): the escalade against OUR OWN works ────────────
    # Two classes because a headline carries exactly one weight and the two
    # outcomes are not the same news. Both are WOUND classes, gated on the
    # player being the DEFENDER: our own repulse abroad belongs to the
    # `region_taken` / `victory_won` triumph ladder, and building it as a
    # triumph here would re-open CA8-D6.
    #
    # `garrison_stormed` 87 — the defenders are dead and the enemy stands
    # in the province with an occupation clock running. Above `own_mauled`
    # (85): a garrison annihilated is a bigger wound than a corps bloodied.
    # Below `enemy_marshal_captured` (88) by CA8-D6's rule — taking an
    # enemy marshal is the larger event.
    "garrison_stormed": 87,
    # `garrison_held` 82 — the works held and we bled them. ABOVE
    # `enemy_on_our_soil` (80) deliberately: without it the briefing led
    # with the weaker, later and vaguer sentence ("{enemy} has crossed into
    # {region}") about a province where a fight had actually been won.
    "garrison_held": 82,
    "enemy_on_our_soil": 80,    # enemy army stands on own-controlled soil
    # CA8-22 (creative audit, Aug 4 2026): the same province, when it was a
    # marshal's duchy. Ranked one above the bare map fact BECAUSE it is the
    # same event told better — the played campaign generated
    # "Austria has seized Carniola, the estate that funded Marshal Ney's
    # honor. He will not forget it, Sire." on the very turn the dispatch led
    # with the flat "Carniola has been taken by Austria." The better
    # sentence existed and was routed to the notification bar.
    "region_lost_estate": 76,
    "region_lost": 75,          # any own/vassal region captured
    # CA8-26: a DECISIVE field victory beats the standing hunger nag on the
    # day it is won (73 > 72) — but never a lost province (75): at equal
    # scale the wound leads.
    "victory_won": 73,
    # Econ spec review §5: an army starving is a slower catastrophe than a
    # province falling and a faster one than a war declaration, so it sits
    # BETWEEN them. Before this, `supply_attrition` was not in this table at
    # all — the drain that took the played campaign from 189,000 men to
    # 60,183 could never be the lead, while a 180g/turn household nag at
    # weight 55 led half the dispatches.
    # WIN-D3 "The Road Home". The lapse warning sits ABOVE supply_strain: a
    # stack over capacity bleeds men, but a passage running out loses the
    # whole corps, and the remedy (march, or be interned) is on a clock.
    "passage_lapsing": 74,
    "supply_strain": 72,
    "war_touches_us": 70,       # coalition tier change / war decl. vs us
    # The peace's own consequence for the army. Below every direct wound to
    # France, above a routine conquest — it is the answer to "what happens
    # to the men who won it", which the player asks the moment he signs.
    "road_home": 69,
    "road_home_mid_treaty": 69,
    # CA8-26: a routine conquest is a success below every direct wound to
    # France's own body and above Europe's business and the household nags.
    "region_taken": 68,         # France conquers a province (non-capital)
    "ally_broken": 60,          # ally suffered a major defeat
    "estate_eroding": 55,       # ES-7 erosion began
    # Econ spec review §6 (a): the establishment stands under the ordinance
    # and the depots can fill it. Below every crisis and below the erosion
    # nag — an opportunity never outranks a wound — but above Europe's own
    # business, because it is France's own army.
    "levy_open": 54,
    # AI-3/AI-4b (Stage D): Europe's own crises may LEAD the dispatch —
    # the vignette's "the dispatch leads with the one foregrounded
    # crisis" — but always below anything that touches France directly
    # (pin 13: France's war never reads as incidental).
    "europe_at_war": 52,        # an AI war declared, France not party
    "europe_crisis": 50,        # beat 2 — the foregrounded brewing crisis
    "europe_congress": 48,      # beat 6 — a third-party peace concluded
    "europe_crisis_passed": 46,  # beat 7 — the stand-down, cause named
}

# One prose template per headline class, in Berthier's register.
# ════════════════════════════════════════════════════════════════════════
# PC-7 (quiet-France played campaign, Aug 3 2026): STANDING vs EVENT classes.
#
# Measured over 42 played turns: `estate_eroding` led 21 of 41 dispatches
# (51%), with a run of SEVEN consecutive turns and the byte-identical
# sentence about Davout's household twelve times — while the treasury held
# 39,000g and the remedy cost 180g/turn. The first line the player reads
# every turn was the most repetitive text in the game, and it crowded out
# the thing actually killing that campaign (an army starving on supply
# attrition, strength ratio 55% → 11%, never once the lead).
#
# The cause is a category error in the weight table: most classes are
# EVENT-derived off a one-turn event-log window, so on a quiet turn they do
# not exist — but these two are STATE predicates that re-manufacture their
# candidate every turn until the player acts. Weight 55 then wins by
# walkover, forever. The July-19 anti-repeat guard had two holes: it
# compared exact rendered TEXT rather than class, and it was gated behind
# `len(candidates) > 1`, so the sole-candidate turns — exactly the ones that
# produced the seven-turn run — skipped it entirely.
#
# The rule here is deliberately NOT suppression. `CREATIVE_AUDIT_2026_07_19`
# §308 says a standing crisis is "demoted to a sub-beat (never suppressed)",
# and `test_creative_audit_2026_07_19.py::test_headline_keeps_its_lead_when_
# it_is_the_only_news` pins it. Suppressing a lone standing crisis would have
# turned the seven-turn run into seven turns of being told nothing at all,
# which is worse than repetition. So: yield the lead when there is other
# news, and when there is not, ESCALATE the wording instead of repeating it.
# ════════════════════════════════════════════════════════════════════════
# `levy_open` joins them for the same reason: it is a STATE predicate that
# re-manufactures its candidate every turn the gate stands open, so without
# the cooldown it would become the next stuck record. Riding PC-7's existing
# machinery is also why "The Levy is Open" needs no serialized memory of the
# over->under flip — the escalation ladder below says it better than a
# one-shot beat could, and it keeps saying it while the offer stands.
# `supply_strain` is standing for the same reason: a stack over capacity
# re-manufactures its candidate every turn until the player moves it, so
# without the cooldown the famine simply replaces the household nag as the
# stuck record — fixing the symptom by swapping which sentence repeats.
STANDING_HEADLINE_CLASSES = frozenset({"estate_eroding", "enemy_on_our_soil",
                                       "levy_open", "supply_strain"})

# Consecutive turns a standing class may hold the lead before it must yield
# to any other candidate. Blessed default, display-only, tunable in band.
STANDING_LEAD_MAX = 2

# Sub-beat slots under the headline. Named (it was a bare `>= 2`) because
# WO-D6's diverse-tail rule is expressed as "the LAST slot", and a magic
# number cannot say which one that is.
SUB_BEAT_SLOTS = 2

# How far below the candidate it displaces the diverse tail may reach.
# The reserved slot varies the KIND of news; it may never trade a wound for
# something this table considers materially smaller.
#
# DERIVED, not guessed. The promotion the rule exists to allow is a captured
# marshal (95) beside a fallen homeland province (99) — a drop of 4 — and the
# whole marshal-fate band sits within 14 of it (`own_mauled` 85). The review
# round measured what an unbounded preference actually did on the 1805 board:
# a weight-99 homeland province evicted for `enemy_on_our_soil` 80, for the
# standing household nag 55, and for a foreign congress 48. Anything in
# [14, 19) separates those; 15 is the round number in that window.
# Blessed default, display-only, tunable in band.
DIVERSE_TAIL_MAX_WEIGHT_DROP = 15

# Escalating variants for a standing class that keeps the lead because it is
# genuinely the only news. Indexed by how long it has led; the last entry is
# the terminal register. The base template is streak 1.
_STANDING_ESCALATION: Dict[str, List[str]] = {
    "estate_eroding": [
        "Sire — Marshal {marshal} has now gone unrewarded {turns} turns. The "
        "staff have noticed which of us he no longer looks at.",
        "Sire — {turns} turns without settlement on Marshal {marshal}. A "
        "rente would close it today; the arrears will not close themselves.",
        "Sire — Marshal {marshal}'s grievance is {turns} turns old and has "
        "stopped being a household matter. It is now a question of the army.",
    ],
    "enemy_on_our_soil": [
        "Sire — {turns} turns now with enemy colours on French soil. The "
        "country is watching to see how long we permit it.",
        "Sire — the enemy has stood on our ground {turns} turns. Every turn "
        "of it is worth a province to their recruiting sergeants.",
    ],
    "supply_strain": [
        "Sire — {turns} turns of famine at {region} now. {losses} gone, and "
        "not one of them to the enemy. {remedy}",
        # PC15-12: {have} agrees with the subject — "Massena has been",
        # "Ney and Soult have been".
        "Sire — {who} {have} been {turns} turns over what {region} can "
        "feed. {losses}. The country will ask where the army went. {remedy}",
    ],
    "levy_open": [
        "Sire — {turns} turns now with the establishment under the ordinance "
        "and the depots standing full. {headroom} men at {capital}, and "
        "nobody has gone to collect them.",
        "Sire — the levy has stood open {turns} turns. {price} gold puts "
        "{amount} foot in the line at {capital}, where a marshal must "
        "stand to receive them; the conscripts do not improve with "
        "keeping.",
    ],
}

_HEADLINE_TEMPLATES: Dict[str, str] = {
    # NP-4: Berthier writes to the imperial government the cell cannot
    # reach — the style holds (the campaign log's chronicle rule is
    # untouched; this is the staff's own dispatch).
    "sovereign_captured": "Sire — the Emperor himself is TAKEN. {captor} holds him, and the Empire holds its breath.",
    # WO-D6 (slice 4): the one sentence the game owed the player. Nation-
    # neutral by construction — the class is keyed on the world's own
    # capital map, so a modded scenario's Prussia reads it about Berlin.
    "capital_lost": ("Sire — {region} HAS FALLEN. Our capital is in "
                     "{captor}'s hands, and every courier in Europe is "
                     "already carrying the news."),
    "home_captured": "Sire — {region} has fallen. Enemy colours fly over French homeland soil.",
    "marshal_captured": "Sire — Marshal {marshal} has been taken. {captor} holds him prisoner.",
    # CA9-F12: the mirror. Composed backend-side like its CA8-D6 siblings
    # because the captive court and the field are both optional.
    "enemy_marshal_captured": "Sire — {line}",
    # PC15-1: both destruction arms composed backend-side (field and
    # victor are optional keys on the event).
    "marshal_destroyed": "Sire — {line}",
    "enemy_marshal_destroyed": "Sire — {line}",
    # CA8-9: the joined arc. The whole sentence is composed backend-side by
    # `_compose_reversal_line` because its shape varies with how many acts
    # the campaign actually produced (crowned / endowed / beaten /
    # dispossessed / uncrowned), and a fixed template would have to invent
    # the beats it lacks.
    "marshal_reversal": "Sire — {line}",
    "own_broken": "Sire — {marshal}'s corps has been broken at {region}. He must reform before he fights again.",
    # WO-16 (slice 12): the proportion EARNED the word; the absolute figure
    # alone read "29 men lost" as trivial and withheld it.
    "own_mauled": "Sire — {marshal} was mauled at {region}: {proportion} of his corps — {casualties} men — lost in a single action.",
    # FA-R5 (slice 14)
    "garrison_stormed": ("Sire — the garrison of {region} is destroyed. "
                         "{enemy} threw {enemy_lost} men at the works and "
                         "carried them."),
    "garrison_held": ("Sire — {region} holds. {enemy} left {enemy_lost} men "
                      "before the works; {remaining} of ours are still under "
                      "arms."),
    "enemy_on_our_soil": "Sire — {enemy} has crossed into {region}. {defenders_line}",
    "region_lost": "Sire — {region} has been taken by {captor}.",
    # FA-38: one class, four ways to lose a satellite. Each says what
    # actually happened, because the player's next move differs in each.
    "vassal_lost": "Sire — {vassal} is no longer ours. {detail}",
    "region_lost_estate": ("Sire — {captor} has taken {region} — the estate "
                           "that funded Marshal {marshal}'s honour. He will "
                           "not forget it."),
    # CA8-2: states the establishment, the capacity and the overage, so the
    # remedy "move a corps" finally has a target size.
    # PC15-12: {stand} agrees with the subject — one marshal "stands",
    # several "stand" (the played line read "Massena stand 21,858 men").
    "supply_strain": ("Sire — {who} {stand} {strength} men at {region}, "
                      "which feeds {capacity}. {over} too many. {losses} "
                      "lost in {turns} turns. {remedy}"),
    "war_touches_us": "Sire — {line}",
    # WIN-D3 §4.3 — the beat names names and the deadline, and when a corps
    # has no land route it says so plainly rather than pretending (§5).
    "road_home": "Sire — the war with {other} is over. {line}",
    # FA-N61 (slice 12): the same class, a later moment. The peace was
    # signed turns ago and this corps was stranded after it, so the
    # sentence above would have told the player the war had just ended
    # every time the treaty picked somebody up.
    "road_home_mid_treaty": "Sire — under the peace with {other}. {line}",
    "passage_lapsing": ("Sire — {who} {is_are} no nearer home, and the safe "
                        "passage runs out in {turns_left} turn(s). After "
                        "that {his_their} corps will be interned where "
                        "{it_they}."),
    "ally_broken": "Sire — our ally's marshal {marshal} was broken at {region}. {nation} reels.",
    "estate_eroding": "Sire — Marshal {marshal}'s household goes unpaid. His patience erodes with his purse.",
    # CA8-11: the headline names a price and a place, so it must also name
    # the condition — recruits join a marshal who can reach the depot, and
    # in the played campaign every French marshal was in Germany or Italy
    # while the briefing kept advertising Paris.
    "levy_open": ("Sire — the establishment stands {headroom} men under the "
                  "ordinance, and the depots hold {pool}. {amount} foot cost "
                  "{price} gold at {capital}, where a marshal must stand to "
                  "receive them."),
    "europe_at_war": "Sire — {aggressor} has declared war on {target}. The stated cause: {reason}.",
    "europe_crisis": "Sire — {nation} moves toward war with {target}. The design is open; the timing is not.",
    "europe_congress": "Sire — {proposer} and {accepter} have made peace without us.",
    "europe_crisis_passed": "Sire — {nation} stands down over {target}; {cause}.",
    # CA8-26 / CA8-D6: the success classes. Composed backend-side (the
    # `war_touches_us` idiom) because each line's shape varies with what
    # the event actually was — liberation vs conquest, field vs the
    # enemy's own capital, who beat whom.
    "enemy_eliminated": "Sire — {line}",
    "capital_stormed": "Sire — {line}",
    "victory_won": "Sire — {line}",
    "region_taken": "Sire — {line}",
}

# Beat-7 cause copy for the headline arm (R7 — composed backend-side).
# Entries here override the shared short form where the headline wants a
# fuller phrasing; anything absent falls through to
# war_council.crisis_cause_phrase(), which covers the WHOLE taxonomy —
# including AI-3r's exposed / outmatched / penniless. Before the July 25,
# 2026 in-game review this map was the only lookup and silently rendered
# those three as "the moment passed".
_CRISIS_CAUSE_HEADLINE: Dict[str, str] = {
    "satisfied": "the want is won",
    "bought_off": "the design was bought off, and the bargain stands",
    "deterred": "the guarantee held",
    "starved": "the moment passed",
}


def _crisis_cause_headline(cause: str) -> str:
    """Headline phrasing for a beat-7 cause, honest for every cause id."""
    key = str(cause or "")
    if key in _CRISIS_CAUSE_HEADLINE:
        return _CRISIS_CAUSE_HEADLINE[key]
    from backend.game_logic.war_council import crisis_cause_phrase
    return crisis_cause_phrase(key)

# Headline-aware Berthier closing notes (W6-3 §5.4) — one per class.
_HEADLINE_BERTHIER_NOTES: Dict[str, str] = {
    # NP-4: the Brétigny counsel — the fastest road home is the table.
    "sovereign_captured": "The captor will name his price, and every acceptance formula in Europe now reads the cell. The table, not a rescue column, brings him home fastest.",
    # WO-D6 (slice 4): the lookup is guarded, so a class with no note is
    # SILENT rather than broken — which is exactly how CA8-22's two new
    # classes ended six of twelve briefings with Berthier saying nothing.
    # The note closes on the decision the loss creates, never on lament.
    "capital_lost": "The army will hear of this before nightfall, Sire. Every order you give today will be read as your answer to it.",
    "home_captured": "France herself is under the enemy's boot, Sire. Every other matter is secondary.",
    "marshal_captured": "We must consider his ransom, Sire — or make his captors regret the keeping.",
    # CA9-N2: the same note fired when FRANCE was the captor — "consider
    # his ransom … or make his captors regret the keeping" while the man
    # sat in a French prison. The note is keyed on the class string alone
    # (`_pick_berthier_note`), so splitting the class by direction is the
    # whole fix; this is its other half.
    "enemy_marshal_captured": "A commander is not replaced like a battalion, Sire. Press them before they find another.",
    # PC15-1: the fall is permanent — the note answers with the recovery
    # path that actually exists (the bench; PT-J4's commission arm rides it).
    "marshal_destroyed": "France does not replace such men by decree, Sire. The army fights one corps short until another is raised.",
    "enemy_marshal_destroyed": "Their order of battle is one commander shorter — permanently, Sire. Press the advantage while their line is headless.",
    # CA8-9: Berthier closes on the man, not the ledger — the note answers
    # the arc the headline opened.
    #
    # Review fix: the first draft asserted the crown ("he was the best of
    # us") and a fixed interval ("a fortnight ago"). `rose` is satisfied by
    # an ESTATE GRANT alone, and the gap ranges 0-5 turns, so both claims
    # were false for most instances — and "fortnight" was a hapax in the
    # whole backend against a game that defines no turn length. Every other
    # entry in this table is true for every instance of its class; this one
    # now is too.
    "marshal_reversal": "Men remember being raised, Sire, and they remember being left.",
    "own_broken": "I have ordered the remnants collected, Sire. Do not commit them until they reform.",
    "own_mauled": "The butcher's bill is heavy, Sire. The army feels it.",
    # FA-R5 (slice 14)
    "garrison_stormed": "The works are gone, Sire. Whoever relieves that province must do it in the open field.",
    "garrison_held": "The walls held, Sire — but a garrison that is not relieved is a garrison that is counted.",
    "enemy_on_our_soil": "They are on our soil, Sire. The marshals await only your word.",
    "region_lost": "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking.",
    # FA-38: caught by `test_every_headline_class_has_a_template_and_a_note`,
    # which is exactly the pin it exists to be.
    "vassal_lost": "A satellite is an army we no longer command and a frontier we no longer hold, Sire. The courts that are still ours are reading this too.",
    "region_lost_estate": "He will expect it back, Sire — or its equal. An unpaid marshal is a slower loss than a province.",
    # CA8-22 drive-by: the two classes added by the Aug-4 econ slice had no
    # closing note, so the dispatch that led six of twelve briefings ended
    # without Berthier saying anything at all. The lookup is guarded, so
    # this was silent rather than broken.
    "supply_strain": "Men lost to the roads are lost for nothing, Sire. Either the province feeds them or we spread them.",
    "road_home": "The treaty gives them the road, Sire, not the rations. They should be walking it.",
    "road_home_mid_treaty": "The treaty gives them the road, Sire, not the rations. They should be walking it.",
    "passage_lapsing": "A treaty's patience is short, Sire. Order him home, or explain the loss to the Senate.",
    "levy_open": "The depots are full and the ordinance allows it, Sire. Conscripts do not improve with keeping.",
    "war_touches_us": "Europe stirs against us, Sire. We should look to our alliances.",
    "ally_broken": "Our ally bleeds, Sire. If we do not steady them, they may seek terms without us.",
    "estate_eroding": "A marshal who feels forgotten fights like one, Sire. The estate rolls want attention.",
    "europe_at_war": "A war we are not in, Sire — for now. Both courts will come asking; the question is what our neutrality is worth.",
    "europe_crisis": "The instruments are on the table, Sire — compensate, guarantee, or let it come having been asked.",
    "europe_congress": "A peace made without France sets a table we were not at, Sire. Note who gained.",
    "europe_crisis_passed": "A war that does not happen leaves no monument, Sire — note what held it, and keep that instrument sharp.",
    # CA8-26: Berthier closes on a triumph the way he closes on a wound —
    # with the next decision it creates, never with congratulation alone.
    "enemy_eliminated": "One enemy the fewer, Sire. Every court in Europe is doing its arithmetic tonight.",
    "capital_stormed": "Their capital in our hands is worth ten field victories, Sire. Expect their court to sue — or to flee.",
    "victory_won": "The army knows it is winning, Sire. Press the advantage before their line reforms.",
    "region_taken": "Ground taken must be garrisoned or it bleeds, Sire. Decide what this province is for.",
}


def _headline_keys(candidate: Dict[str, Any]) -> tuple:
    """CA8-5's dedupe key for one candidate: its (class, identity) AND its
    rendered text, so a class that renders identically from two different
    identities still collapses. One source — the sub-beat loop reads it
    for both the seen-set and every eligibility test."""
    return ((candidate["class"], candidate["identity"]),
            ("", candidate["text"]))


def _build_headline(world, player_nation: str) -> Optional[Dict[str, Any]]:
    """W6-3 §5.1: score the turn's fog-visible events; return the headline.

    Returns {"class", "weight", "text", "sub_beats": [str, ...]} or None
    when nothing scored above the noise floor. Deterministic templates over
    existing events — no LLM (GR6). Bounded work: one pass over the recent
    event-log window + the player's own intel entries (GR8-safe).
    """
    window = [e for e in world.event_log
              if e.get("turn", 0) >= world.current_turn - 1]
    home_regions = set(world.nation_starting_regions.get(player_nation, []) or [])
    vassals_of_player = {
        v for v, s in getattr(world, "vassals", {}).items()
        if s.get("lord") == player_nation
    }
    candidates: List[Dict[str, Any]] = []
    # CA8-26 / gate CA8-D6: success accumulators. A French field victory is
    # raised from the battle event (annihilation) or from a battle WIN
    # joined to the LOSING marshal's forced rout (the ordinary decisive
    # shape — `attacker_victory` fires only on total destruction, while a
    # routed enemy logs a separate forced retreat). Close-out review
    # [B-F2]: the join is by the MAN, not the map — a repulsed attacker's
    # rout event stamps his ORIGIN region while the battle names the
    # defender's, so a location join was structurally dead for the
    # standard adjacent-assault geometry (France's defensive victories
    # would never have composed).
    _french_wins: Dict[str, Dict[str, Any]] = {}
    _enemy_routs: Dict[str, str] = {}
    # WIN-D3: every corps whose safe passage is running out this turn.
    _lapsing: List[Dict[str, Any]] = []

    def _add(cls: str, identity: str = "", **fields):
        text = _HEADLINE_TEMPLATES[cls].format(**fields)
        candidates.append({
            "class": cls,
            "weight": int(HEADLINE_WEIGHTS[cls]),
            "text": text,
            # PC-7: standing classes carry WHO/WHAT they are about, so the
            # lead-streak survives the text changing underneath it.
            "identity": identity or cls,
            # The template's own arguments, kept so the escalation ladder can
            # re-render with them. Before this it could only substitute
            # {marshal} and {turns}, which silently bounded what a standing
            # class was allowed to say as it escalated.
            "fields": dict(fields),
        })

    for e in window:
        etype = e.get("type", "")
        if etype == "region_captured":
            captor = e.get("captured_by", "")
            region = e.get("region", "")
            prev = e.get("captured_from", "")
            if captor and captor != player_nation:
                # ── WO-11 (slice 4): the wound has a DIRECTION ──────────
                # `home_captured` fired whenever ANY non-player power took
                # homeland soil — including an ALLY liberating it from a
                # third party. Measured: Spain retaking Paris from Austria
                # printed "Paris has fallen. Enemy colours fly over French
                # homeland soil." A province that changes hands between two
                # enemies, on soil we had already lost, is not a fresh wound
                # and produces no candidate.
                #
                # "The player's side" is wider than the player, and the
                # review round caught the first cut being too narrow: it
                # read only {us, our vassals}, so when an ALLY who had
                # liberated Paris lost it again to Austria the briefing
                # said NOTHING — a regression this slice introduced, since
                # the direction-blind arm at least fired then. The rule is
                # the honest one: the province passed FROM our side TO
                # someone not on it. The captor half is not extra scope —
                # it is required by the first half, or an ally taking a
                # province from another ally would read as our wound.
                def _on_our_side(nation: str) -> bool:
                    return bool(nation) and (
                        nation == player_nation
                        or nation in vassals_of_player
                        or world.are_allies(player_nation, nation))

                _ours_to_lose = (_on_our_side(prev)
                                 and not _on_our_side(captor))
                # WO-D6: STRUCTURAL, never the literal "Paris" — the
                # world's own capital map, so the class holds for any
                # nation and any scenario. Read outside the `home_regions`
                # branch because a capital need not be a starting region
                # (a formed or carved state's is not).
                _own_capital = world.get_nation_capital(player_nation)
                if (_ours_to_lose and _own_capital
                        and region == _own_capital):
                    _add("capital_lost", f"capital_lost:{region}",
                         region=region,
                         captor=formed_display_name(world, captor))
                elif _ours_to_lose and region in home_regions:
                    # FA-53 (slice 11) is REFUTED BY A LANDED DESIGN
                    # DECISION and this line is deliberately unchanged.
                    # The row asks for the several provinces of one bad day
                    # to collapse into a tally so the page has slots left
                    # for other news. WO slice 4 (WO-D6, "The Capital
                    # Speaks") measured the SAME failure — four provinces
                    # lost in a turn, the page reading "Limousin / Berry /
                    # Normandy" with PARIS not on it — and answered it by
                    # splitting `capital_lost` out so the capital always
                    # leads, KEEPING the three-province page and pinning it
                    # five ways (`test_three_provinces_and_nothing_else_
                    # still_fill_both_slots` and four siblings). Collapsing
                    # here reds all five. Two designs, one already chosen.
                    _add("home_captured", f"home_captured:{region}", region=region)
                elif _ours_to_lose:
                    # CA8-22: if the province was a marshal's endowment, the
                    # human fact outranks the map fact — it is the same
                    # event, and one of the two sentences is about a man.
                    _holder = next(
                        (m.name for m in world.marshals.values()
                         if m.nation == player_nation
                         and region in (getattr(m, "dotation_regions", None) or [])),
                        "")
                    if _holder:
                        _add("region_lost_estate",
                             f"region_lost:{region}", region=region,
                             marshal=humanize_entity_name(_holder),
                             captor=formed_display_name(world, captor))
                    else:
                        _add("region_lost", f"region_lost:{region}",
                             region=region,
                             captor=formed_display_name(world, captor))
            elif captor == player_nation and region:
                # ── CA8-26 / gate CA8-D6: France's own conquest is NEWS ──
                # The dispatch had no headline class for a French success at
                # all — 14 of 14 measured headlines were misfortunes, and
                # the turn Vienna fell the lead was a supply nag.
                _prev_capital = (world.get_nation_capital(prev)
                                 if prev else None)
                if _prev_capital and _prev_capital == region:
                    _add("capital_stormed", f"capital_stormed:{region}",
                         line=(f"{region} is taken — "
                               f"{formed_display_name(world, prev)}'s own "
                               f"capital, and the tricolor flies over it "
                               f"this morning."))
                elif region in home_regions:
                    _add("region_taken", f"region_taken:{region}",
                         line=(f"{region} is French again. The enemy is "
                               f"driven out and the province restored."))
                else:
                    _add("region_taken", f"region_taken:{region}",
                         line=(f"{region} has fallen to our arms. The "
                               f"tricolor flies over it this morning."))
        elif etype == "nation_eliminated":
            # CA8-26: a court France fought, knocked out of the war — the
            # existing event (no new campaign-log type). Gated on France
            # having actually OPPOSED them in a war instance, so a third
            # party's kill never reads as a French triumph. Elimination
            # sets every pair to PEACE before this builder runs, so the
            # instance record (kept for the AI-4 grudge window) is the
            # honest witness, not the live diplomatic state.
            #
            # Close-out review [B-F1]: `side_by_nation` alone is NOT that
            # witness — `_eliminate_nation` runs
            # `mark_participant_eliminated_in_all_wars` BEFORE logging the
            # event, and that helper POPS the fallen court from
            # `side_by_nation` (the same strip that made NA-3's first
            # grudge cut production-dead). The durable key is
            # `participant_meta[nation]["side"]`, written at attach time
            # and never popped; `side_by_nation` stays the first read so a
            # hand-authored or historical instance still answers.
            fallen = e.get("nation", "")
            _we_fought_them = False
            for _inst in (getattr(world, "war_instances", {}) or {}).values():
                if not isinstance(_inst, dict):
                    continue
                _sides = _inst.get("side_by_nation") or {}
                _meta = _inst.get("participant_meta") or {}
                _ours = (_sides.get(player_nation)
                         or (_meta.get(player_nation) or {}).get("side"))
                _theirs = (_sides.get(fallen)
                           or (_meta.get(fallen) or {}).get("side"))
                if _ours and _theirs and _ours != _theirs:
                    _we_fought_them = True
                    break
            if fallen and _we_fought_them:
                _add("enemy_eliminated", f"enemy_eliminated:{fallen}",
                     line=(f"{formed_display_name(world, fallen)} is knocked "
                           f"out of the war. No army remains beneath their "
                           f"colours."))
            elif (A_LOST_SATELLITE_CAN_LEAD and fallen
                  and str(e.get("lord") or "") == player_nation):
                # FA-38: OUR OWN satellite, annihilated. `_we_fought_them` is
                # correctly False (we never opposed it), so before this arm
                # the tick produced no candidate at all and the page led with
                # a supply nag. `_eliminate_nation` deletes the vassal row, so
                # the lord is read off the EVENT and never off `world.vassals`.
                _add("vassal_lost", f"vassal_lost:{fallen}",
                     vassal=formed_display_name(world, fallen),
                     detail="Conquered — the satellite is gone.")
        elif A_LOST_SATELLITE_CAN_LEAD and etype in (
                "vassal_broke_free", "vassal_defected", "vassal_transferred"):
            # FA-38: the other three ways an empire loses a satellite.
            # `vassal_broke_free` is FA-N74's new row; without it this class
            # could see a defection and a transfer but never a rebellion.
            _lord = str(e.get("lord") or e.get("from_lord") or "")
            _vassal = str(e.get("vassal") or "")
            if _lord != player_nation or not _vassal:
                continue
            if etype == "vassal_transferred":
                _to = formed_display_name(
                    world, str(e.get("to_lord") or "another crown"))
                _detail = f"{_to} is their protector now."
            elif etype == "vassal_defected":
                _briber = formed_display_name(
                    world, str(e.get("briber") or "a rival court"))
                _detail = f"{_briber}'s gold bought them."
            elif str(e.get("exit") or "") == "vassal_rebellion_armistice":
                _detail = "They broke free; the armistice holds."
            elif str(e.get("exit") or "") == "vassal_rebellion_independent":
                _detail = "They broke free and stand alone."
            else:
                _detail = "They have rebelled, and it is war."
            _add("vassal_lost", f"vassal_lost:{_vassal}",
                 vassal=formed_display_name(world, _vassal),
                 detail=_detail)
        elif etype == "marshal_captured":
            # ── CA9 F12 + N2: the capture has a DIRECTION ────────────────
            # `nation` is the CAPTIVE's own court (`combat_executor`'s
            # `_capture_marshal` stamps `owner = marshal.nation`); `captor`
            # is the taker. This branch read NEITHER, so France taking Mack
            # at Ulm led the briefing at weight 95 as a French disaster —
            # twice in one played campaign — and Berthier closed on paying
            # his ransom (N2). Splitting the CLASS by direction fixes N2
            # for free: `_pick_berthier_note` keys on the class string
            # alone, so the note follows without a new parameter.
            #
            # The ladder mirrors `own_broken`/`ally_broken` thirty lines
            # below. The third arm — a capture France is neither party to —
            # is a finding neither row carried: `_build_headline` reads the
            # raw event log, so AUSTRIA taking a RUSSIAN marshal led
            # France's morning briefing at 95, phrased as a French loss. It
            # now produces no candidate at all, which IS gate CA8-D6 ("a
            # third party's kill is never our triumph"), and is not our
            # wound either.
            #
            # `enemy_eliminated`'s D6 `war_instances` witness is
            # deliberately NOT reused. That loop exists because
            # `nation_eliminated` names only the fallen court; this event
            # NAMES its captor, so France's part is a one-key read. Reusing
            # the loop would credit France whenever it merely shared a war
            # with the victim — manufacturing the exact misread D6 forbids.
            cap_nation = e.get("nation", "")
            cap_captor = e.get("captor", "")
            cap_marshal = humanize_entity_name(e.get("marshal", "?"))
            if cap_nation == player_nation:
                # NP-4: the sovereign's capture is its OWN crisis class —
                # weight above home_captured; the event's `sovereign` key
                # is stamped by WorldState.capture_marshal.
                _cls = ("sovereign_captured" if e.get("sovereign")
                        else "marshal_captured")
                _add(_cls,
                     f"{_cls}:{e.get('marshal', '?')}",
                     marshal=cap_marshal,
                     # CA8 sweep 4: `captor` is a NATION TAG (combat_executor
                     # stamps `captor_nation`), so `humanize_entity_name` — a
                     # marshal-name humaniser — rendered "Kingdom Of Italy holds
                     # him prisoner." at weight 95: a dead name AND a mis-case,
                     # from the highest-weight headline in the file.
                     captor=(formed_display_name(world, cap_captor)
                             if cap_captor else "the enemy"))
            elif cap_captor == player_nation:
                # Same dead-name discipline on the new slot — the captive's
                # court is a nation tag too.
                # CA9 review round: "of Ottoman Empire" / "of Kingdom
                # of Italy" — the same article the F7 line already takes.
                _of = (f" of {with_definite_article(formed_display_name(world, cap_nation))}"
                       if cap_nation else "")
                _at = (f" at {e['location']}" if e.get("location") else "")
                _add("enemy_marshal_captured",
                     f"enemy_marshal_captured:{e.get('marshal', '?')}",
                     # NP-V: a captured enemy SOVEREIGN is not "Marshal
                     # Kaiser" — the honorific is single-sourced.
                     line=(f"{marshal_honorific(world, e.get('marshal', ''))}"
                           f"{_of} is taken{_at} — he "
                           f"is our prisoner, and their order of battle is "
                           f"one commander shorter."))
        elif etype == "marshal_destroyed":
            # ── PC15-1: annihilation gets the same direction ladder the
            # capture split earned (CA9 F12 + N2): own loss / our kill /
            # third party = no candidate (gate CA8-D6 — a third party's
            # kill is never our triumph, and is not our wound either).
            des_nation = e.get("nation", "")
            des_victor = e.get("victor", "")
            des_marshal = humanize_entity_name(e.get("marshal", "?"))
            des_at = (f" at {e['location']}" if e.get("location") else "")
            if des_nation == player_nation:
                if e.get("cause") == "attrition":
                    des_line = (f"Marshal {des_marshal}'s corps has wasted "
                                f"away{des_at} — starved out to the last "
                                f"man. He will not return to the order of "
                                f"battle.")
                elif e.get("cause") == "interned":
                    # WIN-D3: internment is not annihilation, and the
                    # briefing must not say it is. The corps was disarmed
                    # for overstaying a safe passage the treaty gave it —
                    # a diplomatic humiliation, not a battlefield loss.
                    _host = e.get("victor") or ""
                    _by = (f" by {formed_display_name(world, _host)}"
                           if _host else "")
                    des_line = (f"Marshal {des_marshal}'s corps was interned"
                                f"{des_at}{_by} — its safe passage had "
                                f"expired and it had not come home. The men "
                                f"are disarmed and the colours are lost.")
                else:
                    des_line = (f"Marshal {des_marshal}'s corps has been "
                                f"DESTROYED{des_at}. He will not return to "
                                f"the order of battle.")
                _add("marshal_destroyed",
                     f"marshal_destroyed:{e.get('marshal', '?')}",
                     line=des_line)
            elif des_victor == player_nation:
                _of = (f" of {with_definite_article(formed_display_name(world, des_nation))}"
                       if des_nation else "")
                _add("enemy_marshal_destroyed",
                     f"enemy_marshal_destroyed:{e.get('marshal', '?')}",
                     line=(f"Marshal {des_marshal}{_of} is destroyed{des_at} "
                           f"— his corps annihilated, his name struck from "
                           f"their order of battle."))
        elif etype in ("marshal_broken", "retreat"):
            # ────────────────────────────────────────────────────────────
            # CA8-5 (creative audit, Aug 4 2026): `own_broken` carries the
            # right sentence and outranks `own_mauled` at weight 90 — and it
            # was STRUCTURALLY UNREACHABLE in ordinary play. `marshal_broken`
            # occurs zero times across a 12-turn played campaign: the
            # ordinary break logs `{"type": "retreat"}` (combat_executor.py
            # :2455, world_state.py :10471/:10508/:10977) and `marshal_broken`
            # is emitted only on the rare no-retreat-route SHATTERED branch.
            # So the narration could not say "Ney's corps has been broken" at
            # all, and the turn a corps routed led with the casualty count
            # instead.
            #
            # A VOLUNTARY withdrawal is not a break — `movement_executor`'s
            # own retreat verb logs the same event type. The four rout sites
            # stamp `forced: True`; nothing else does, so the player's own
            # ordered withdrawal never reads as a rout.
            # ────────────────────────────────────────────────────────────
            if etype == "retreat" and not e.get("forced"):
                continue
            m_nation = e.get("nation", "")
            marshal_disp = humanize_entity_name(e.get("marshal", "?"))
            region = e.get("region", e.get("location", e.get("from", "the field")))
            if m_nation == player_nation:
                _add("own_broken", f"own_broken:{e.get('marshal', '?')}",
                     marshal=marshal_disp, region=region)
            elif (m_nation
                    and world.get_diplomatic_state(player_nation, m_nation) == "ALLIANCE"):
                _add("ally_broken", f"ally_broken:{e.get('marshal', '?')}",
                     marshal=marshal_disp, region=region,
                     # CA8 sweep 4: the last `_add()` still passing a nation
                     # tag through the marshal-name humaniser.
                     nation=formed_display_name(world, m_nation))
            elif (m_nation
                    and world.get_diplomatic_state(player_nation, m_nation) == "WAR"):
                # CA8-26: an ENEMY corps breaking is half of a French
                # victory — joined below to a French battle win over THAT
                # marshal, so an AI-vs-AI rout never reads as our triumph
                # ([B-F2]: keyed by the man, not the region).
                _enemy_routs[str(e.get("marshal", ""))] = marshal_disp
        elif etype == "battle" or (THE_SHELLING_IS_BRIEFED
                                   and etype == "bombardment"):
            # Own marshal mauled: >=25% of pre-battle strength lost.
            #
            # FA-25 (slice 11): this was the ONLY `own_mauled` producer and it
            # matched `battle` alone, so a bombardment — the mechanic that
            # takes thousands of men without a battle — reached neither the
            # headline nor Le Moniteur. The trap in "also accept bombardment":
            # a bombardment event has NO `location` key (its field is
            # `defender_location`), so reusing the line verbatim renders
            # "Ney was mauled at the field". Read both.
            for side, cas_key in (("attacker", "attacker_casualties"),
                                  ("defender", "defender_casualties")):
                if e.get(f"{side}_nation") != player_nation:
                    continue
                name = e.get(side, "")
                casualties = int(e.get(cas_key, 0) or 0)
                m = world.get_marshal(name)
                if m is None or casualties <= 0:
                    continue
                pre = m.strength + casualties
                # WO-16 (slice 12): the absolute floor. A quarter of an
                # 87-man remnant is 22 men and led the briefing on the turn
                # a vassal defected and a homeland province fell.
                if (pre > 0 and casualties >= 0.25 * pre
                        and casualties >= OWN_MAULED_MIN_CASUALTIES):
                    # CA8-5: identity is the MAN, not the casualty figure.
                    # Three distinct battles at one province in one phase are
                    # one story, not three headline slots.
                    _add("own_mauled", f"own_mauled:{name}",
                         marshal=humanize_entity_name(name),
                         region=(e.get("location")
                                 or e.get(f"{side}_location")
                                 or "the field"),
                         casualties=f"{casualties:,}",
                         proportion=_mauled_proportion(casualties, pre))
            # CA8-26: record a French battle WIN for the success composer
            # below. Annihilation outcomes stand alone; tactical wins count
            # only when joined to an enemy rout at the same field.
            _outcome = str(e.get("outcome", ""))
            _loc = str(e.get("location", "") or "")
            if _loc:
                if (e.get("attacker_nation") == player_nation
                        and _outcome in ("attacker_victory",
                                         "attacker_tactical_victory")):
                    _french_wins[_loc] = {
                        "victor": str(e.get("attacker", "") or ""),
                        "loser": str(e.get("defender", "") or ""),
                        "annihilation": _outcome == "attacker_victory",
                    }
                elif (e.get("defender_nation") == player_nation
                        and _outcome in ("defender_victory",
                                         "defender_tactical_victory")):
                    _french_wins[_loc] = {
                        "victor": str(e.get("defender", "") or ""),
                        "loser": str(e.get("attacker", "") or ""),
                        "annihilation": _outcome == "defender_victory",
                    }
        elif etype in ("diplomatic_war_declared", "war_declaration"):
            aggressor = e.get("aggressor") or e.get("nation", "")
            target = e.get("target", "")
            if player_nation in (aggressor, target):
                other = target if aggressor == player_nation else aggressor
                _add("war_touches_us",
                     line=f"{formed_display_name(world, other)} and France are at war.")
            elif etype == "war_declaration" and aggressor and target:
                # AI-3 (Stage D): a war between other powers may lead the
                # dispatch — with its STATED REASON (pin 4: no unexplained
                # war). Weighted below everything France-centric.
                reason = (e.get("stated_reason")
                          or e.get("casus_belli_label") or "conquest")
                _add("europe_at_war",
                     aggressor=formed_display_name(world, aggressor),
                     target=formed_display_name(world, target),
                     reason=str(reason))
        elif etype == "garrison_assault":
            # FA-R5 (slice 14): an escalade against OUR OWN works. Gated on
            # the player being the DEFENDER — a garrison we storm abroad is
            # the triumph ladder's business (`region_taken` / `victory_won`),
            # and CA8-D6 settled that a French success is not composed here
            # as a wound.
            #
            # Measured before this arm existed: Austria batters the Paris
            # garrison 25,000 -> 12,500, loses 6,250 doing it, and the next
            # morning's `headline` is None with the note "Your armies stand
            # ready, Sire. The initiative is ours." The word "Paris" did not
            # appear in the dispatch at all. The fortified variant is worse —
            # the garrison annihilated and an occupation clock started, still
            # silent, and the only thing that ever recovered it was
            # `enemy_on_our_soil` on the FOLLOWING intel refresh, saying
            # "{enemy} has crossed into Paris. No French corps stands in his
            # path" about a province he had stormed.
            #
            # Identity is the PROVINCE: several assaults on one town in one
            # enemy phase are one siege, not three headline slots (CA8-5).
            # Neither class is in STANDING_HEADLINE_CLASSES — this is current
            # news, and a state-derived class in that set repeats and buries
            # everything else (PC-7's `marshal_reversal` trap).
            if e.get("defender_nation") == player_nation:
                _garrison_region = str(e.get("region", "") or "")
                _besieger = humanize_entity_name(str(e.get("marshal", "")
                                                     or "the enemy"))
                _their_loss = int(e.get("attacker_losses", 0) or 0)
                _left = int(e.get("garrison_remaining", 0) or 0)
                if _garrison_region:
                    if e.get("held"):
                        _add("garrison_held",
                             f"garrison:{_garrison_region}",
                             region=_garrison_region,
                             enemy=_besieger,
                             enemy_lost=f"{_their_loss:,}",
                             remaining=f"{_left:,}")
                    else:
                        _add("garrison_stormed",
                             f"garrison:{_garrison_region}",
                             region=_garrison_region,
                             enemy=_besieger,
                             enemy_lost=f"{_their_loss:,}")
        elif etype == "evacuation_granted":
            # WIN-D3 §4.3. Only for a peace France itself signed — the
            # producer's own message names our corps and their destinations
            # (the campaign-log filter draws the same line).
            _pair = (e.get("nation_a", ""), e.get("nation_b", ""))
            if player_nation in _pair:
                _other = _pair[1] if _pair[0] == player_nation else _pair[0]
                # FA-N61 (slice 12): a mid-treaty top-up is keyed on the
                # CORPS, not the pair. The peace's own beat already holds
                # `road_home:<pair>`, and two corps stranded on the same
                # treaty are two pieces of news, not one.
                # `.get(k, default)` returns the default only for a
                # MISSING key, never for a present-but-empty one, so
                # `e.get("marshals", [""])[0]` is the documented
                # footgun: one producer writing `marshals: []` is an
                # IndexError in the morning briefing. Slice-12 review.
                _named = (e.get("marshals") or [""])[0]
                _identity = (f"road_home:{_named}"
                             if e.get("mid_treaty")
                             else f"road_home:{'|'.join(sorted(_pair))}")
                _add("road_home_mid_treaty" if e.get("mid_treaty")
                     else "road_home",
                     identity=_identity,
                     other=formed_display_name(world, _other),
                     line=str(e.get("message", "")))
        elif etype == "evacuation_lapsing":
            # COLLECTED, not added one-by-one. The dispatch shows ONE
            # headline, so with several corps lapsing at once only the
            # luckiest was ever named — and in the acceptance run a marshal
            # was interned having never appeared in a briefing, while the
            # design promises three explicit warnings before that happens.
            # One beat, every name, the soonest deadline.
            if e.get("nation") == player_nation:
                _lapsing.append(e)
        elif etype == "crisis_brewing":
            _add("europe_crisis",
                 nation=formed_display_name(world, e.get("nation", "?")),
                 target=formed_display_name(world, e.get("target", "?")))
        elif etype == "crisis_passed":
            _add("europe_crisis_passed",
                 nation=formed_display_name(world, e.get("nation", "?")),
                 target=formed_display_name(world, e.get("target", "?")),
                 cause=_crisis_cause_headline(e.get("cause", "starved")))
        elif etype == "third_party_peace":
            # PC15-D4 piece 4: the peace is stamped DURING advance (new
            # turn) and the dispatch builds after advance in the same
            # call, so the -1 event window rendered the identical
            # sentence at turn N AND N+1 (diplomacy-latewar T22-23).
            # Current-news gate — advance-stamped beats render once.
            # (The enemy-phase-stamped classes above are stamped
            # PRE-increment and must NOT get this gate.)
            if int(e.get("turn", -1)) == int(world.current_turn):
                _add("europe_congress",
                     proposer=formed_display_name(world, e.get("proposer", "?")),
                     accepter=formed_display_name(world, e.get("accepter", "?")))
        elif etype in ("coalition_formed", "coalition_brewing_started"):
            # Stage D review fix [r1/r6]: an ECLIPSE coalition's events
            # carry target_nation != player — those must never render as
            # "against us" (the europe_* arms and the campaign log carry
            # them instead).
            _etarget = e.get("target_nation") or player_nation
            if _etarget != player_nation:
                pass
            elif etype == "coalition_formed":
                _add("war_touches_us",
                     line="a Coalition has formed against France.")
            else:
                _add("war_touches_us",
                     line="the courts of Europe are drawing together against us.")

    # WIN-D3: ONE beat for every corps whose safe passage is running out,
    # ordered by how little time is left. Aggregated rather than per-marshal
    # because the dispatch shows a single headline: the acceptance run had
    # Ney's warning win the slot three turns running while Davout, lapsing
    # beside him, was interned without ever being mentioned.
    if _lapsing:
        # The window is two turns wide, so a corps still dawdling appears
        # twice and the first cut of this beat read "Davout, Soult, Davout
        # and Soult". One row per marshal, the most urgent reading kept.
        _freshest: Dict[str, Dict[str, Any]] = {}
        for _row in _lapsing:
            _key = str(_row.get("marshal", "?"))
            _prev = _freshest.get(_key)
            if (_prev is None
                    or int(_row.get("turns_left") or 0)
                    < int(_prev.get("turns_left") or 0)):
                _freshest[_key] = _row
        _lapsing = sorted(_freshest.values(),
                          key=lambda x: (int(x.get("turns_left") or 0),
                                         str(x.get("marshal", ""))))
        _names = [humanize_entity_name(x.get("marshal", "?"))
                  for x in _lapsing]
        _who = (_names[0] if len(_names) == 1
                else ", ".join(_names[:-1]) + f" and {_names[-1]}")
        _add("passage_lapsing",
             identity="passage_lapsing:" + "|".join(sorted(_names)),
             who=_who,
             is_are="is" if len(_names) == 1 else "are",
             his_their="his" if len(_names) == 1 else "their",
             it_they="it stands" if len(_names) == 1 else "they stand",
             region=_lapsing[0].get("region")
             or _lapsing[0].get("location", "?"),
             turns_left=int(_lapsing[0].get("turns_left") or 0))

    # Enemy army standing on own-controlled soil — state-based, fog-legal
    # (the player's own intel entries only, never omniscient reads — R5).
    for region_name, intel in world.intel.items():
        if intel.visibility == UNKNOWN:
            continue
        if int(intel.last_updated_turn) < world.current_turn - 1:
            continue
        region = world.regions.get(region_name)
        if region is None or region.controller != player_nation:
            continue
        # FA-N14: "enemy colours on French soil" of a province France had
        # CONQUERED. Measured: France holding Swabia with Mack standing on it
        # fired the class, and by T3 the ladder said the enemy had stood on
        # French soil three turns. Boot-dormant by construction — at boot
        # France's controlled set IS her home set, so the class is armed by
        # the first conquest. Sibling `home_captured` already reads
        # `home_regions`; this arm did not.
        if (SOIL_ALARM_IS_HOME_SOIL_ONLY
                and home_regions
                and region_name not in home_regions):
            continue
        enemy_entries = [km for km in intel.known_marshals
                         if _intel_marshal_is_enemy(world, player_nation, km)]
        if not enemy_entries:
            continue
        enemy_name = humanize_entity_name(enemy_entries[0].get("name", "an enemy army"))
        defenders = [m.name for m in world.get_marshals_in_region(region_name)
                     if m.nation == player_nation and m.strength > 0]
        if defenders:
            # WO slice 12 (found in passing): "Ney stand in his path."
            _verb = "stands" if len(defenders) == 1 else "stand"
            defenders_line = f"{' and '.join(defenders)} {_verb} in his path."
        else:
            defenders_line = "No French corps stands in his path."
        # FA-12 (slice 11): the identity was keyed on the PROVINCE, so the
        # standing-alarm run restarted every time the enemy moved. Measured on
        # both worlds: T3 "3 turns now with enemy colours on French soil", T4
        # the base template re-fires as fresh news for the next province, T6
        # "3 turns now" AGAIN. The run is about the enemy standing on our
        # ground, not about which acre — the class is the identity, and the
        # province rides the fields where the templates already read it. Only
        # a genuine gap (no enemy on any home province for a turn) restarts
        # the ladder, which is the intended semantics.
        _add("enemy_on_our_soil",
             identity=("enemy_on_our_soil"
                       if SOIL_ALARM_IS_ONE_RUN
                       else f"enemy_on_our_soil:{region_name}"),
             enemy=enemy_name, region=region_name,
             defenders_line=defenders_line)
        break  # one such headline candidate is enough

    # ES-7 erosion began (state-based; Europe-scoped).
    from backend.game_logic.dotation import (
        get_expectation, get_satisfaction, is_dotation_world, is_eroding,
    )
    if is_dotation_world(world):
        for m in world.marshals.values():
            if m.nation != player_nation or m.strength <= 0:
                continue
            if (get_expectation(m) > get_satisfaction(m, world)
                    and is_eroding(m, world)):
                _add("estate_eroding",
                     identity=f"estate_eroding:{m.name}", marshal=m.name)
                break

    # The corps is starving (econ spec review §5). `supply_attrition` was not
    # in HEADLINE_WEIGHTS at all, so an army bleeding 6% a turn — the drain
    # that took the played campaign from 189,000 men to 60,183 — could never
    # be the lead, while a 180g/turn household nag at weight 55 led half the
    # dispatches. Fires on two consecutive turns of loss, so a single bad turn
    # is not a crisis; names the number AND whichever remedy is legal.
    _strain = _supply_strain_candidate(world, player_nation)
    if _strain:
        _add("supply_strain", identity=f"supply_strain:{_strain['region']}",
             **_strain["fields"])

    # "The Levy is Open" (econ spec review §6 (a)) — state-based, Europe-only.
    # The measured defect: France boots +59,000 OVER its force limit, teaching
    # ten turns of "recruitment is forbidden"; by turn 12 it stood under the
    # limit with a full pool and nothing said so. Every figure below already
    # existed — the game simply never spoke them.
    from backend.commands.economy_executor import get_levy_status
    _levy = get_levy_status(world, player_nation)
    if _levy["open"]:
        _capital = world.get_nation_capital(player_nation) or "the depots"
        _add("levy_open",
             headroom=f"{_levy['headroom']:,}",
             pool=f"{_levy['infantry_pool']:,}",
             amount=f"{_levy['infantry_amount']:,}",
             price=f"{_levy['infantry_price']:,}",
             capital=_capital)

    # ────────────────────────────────────────────────────────────────────
    # CA8-9: the marshal's fall, told with the rise it reverses.
    #
    # Runs LAST and ABSORBS the fall candidate it restates, rather than
    # merely outranking it. The CA8-5 dedupe keys on (class, identity), so a
    # `marshal_reversal` at weight 91 sitting above `own_broken` at 90 would
    # lead with the joined sentence and then restate the bare one as its own
    # sub-beat — the exact duplicate-beat shape CA8-5 was landed to kill.
    # Absorption is by identity AND by which act the composer chose, so a
    # DIFFERENT marshal's break on the same turn is untouched, and a beat the
    # reversal does NOT narrate survives to be a sub-beat.
    #
    # Known residual (review §2.2, deliberately not fixed here): on the
    # confiscation path the headline tail "Austria holds Carniola now" and
    # the surviving anonymous `region_lost` sub-beat state the same map fact
    # one line apart. Absorbing `region_lost` would suppress a province loss
    # whenever any marshal had an arc, which is worse.
    #
    # A pure ascent cannot reach here: `reversal_line` is only composed when
    # the arc carries a fall as well as a rise, and since the review removed
    # `crown_lost` from that predicate, every remaining fall term is a real
    # misfortune (a defeat, a hunt, a forced rout, a dispossession) rather
    # than a classification. That is what keeps CA8-26 (no headline class
    # for a French success) gated rather than accidentally built — the first
    # draft's version of this sentence was true only by definition, and four
    # reviewers independently read the code as contradicting it.
    #
    # Second call to `_build_marshal_arcs` this dispatch (the roster builder
    # makes the other). Bounded: one pass over a 500-capped event log plus
    # the marshal roster, once per turn — not a hot path.
    # ────────────────────────────────────────────────────────────────────
    # ── CA8-26: compose the French-victory candidates ────────────────────
    # An annihilation win stands alone; a tactical win becomes news only
    # when the beaten marshal's corps actually broke ([B-F2]: joined by
    # the loser's NAME — geometry-independent). One candidate per field
    # per turn (CA8-5 discipline).
    for _loc, _win in _french_wins.items():
        _routed = _enemy_routs.get(str(_win.get("loser", "")), "")
        # NP-V (live-drive finding): the Emperor's own victories read
        # "Marshal Napoleon holds the field" — a sovereign is not a
        # marshal. Single-sourced honorific; "our arms" keeps no rank.
        # (This REPLACES the bare `humanize_entity_name` display name the
        # two lines below used to prefix with a literal "Marshal ".)
        _victor_hon = (marshal_honorific(world, _win["victor"])
                       if _win["victor"] else "Our arms")
        if _win["annihilation"]:
            _loser_disp = humanize_entity_name(_win["loser"]) if _win["loser"] else "the enemy"
            _add("victory_won", f"victory_won:{_loc}",
                 line=(f"{_victor_hon} has destroyed "
                       f"{_loser_disp}'s corps at {_loc}. No enemy "
                       f"formation remains in that field."))
        elif _routed:
            # WO slice 12 (§4 N-8b): "broken and flees" seven times across a
            # campaign is literally true and materially empty — the rout
            # sentence is repeat-aware, riding the serialized `battle_counts`
            # rotation seam (XR-5): the second and later battles on the same
            # field say so. Copy only; no new field.
            _add("victory_won", f"victory_won:{_loc}",
                 line=(f"{_victor_hon} holds the field at {_loc} — "
                       f"{_rout_clause(world, _loc, _routed)}"))
    # Absorption: the conquest of a field France just won is the SAME story
    # told twice — the victory line carries it; the bare map fact yields.
    # (`capital_stormed` is never absorbed: the capital falling and the
    # battle that took it are distinct facts, headline + sub-beat.)
    _victory_locs = {c["identity"].split(":", 1)[1] for c in candidates
                     if c["class"] == "victory_won"}
    if _victory_locs:
        candidates[:] = [c for c in candidates
                         if not (c["class"] == "region_taken"
                                 and c["identity"].split(":", 1)[1] in _victory_locs)]

    for _name, _arc in _build_marshal_arcs(world, player_nation,
                                           cap=None).items():
        if not _arc.get("reversal_line"):
            continue
        # ── The fall must be CURRENT NEWS ────────────────────────────────
        # CA8-9 review fix (the review's headline finding). The arc builder
        # reads a SIX-turn window; every other headline candidate is scored
        # from the two-turn window above. `marshal_reversal` was therefore a
        # state-derived class that re-manufactured its candidate every turn
        # — and it was not in STANDING_HEADLINE_CLASSES, so PC-7's cooldown
        # and the Berthier note hand-back were both structurally unreachable,
        # while the July-19 exact-repeat demotion could not catch it either
        # because `_turns_ago_phrase` rewrites the sentence every turn
        # ("last turn" -> "two turns ago" -> ...). Measured: the same
        # reversal led four to six consecutive dispatches at weight 91 and
        # froze Berthier's closing note for the whole run, burying a
        # bankruptcy, a declaration of war and a genuinely broken corps.
        # That is verbatim the defect PC-7 was landed to kill.
        #
        # Gating on the fall's own turn bounds the lead by construction and
        # needs no new cooldown: the arc keeps its six-turn memory for the
        # ROSTER note, but it may only take the lead on the turn the fall
        # actually happened. This also stops a five-turn-old defeat being
        # presented as this turn's news.
        _fall_turn = _arc.get("fall_turn")
        if _fall_turn is None or int(_fall_turn) < world.current_turn - 1:
            continue
        # ── Absorb ONLY the beat the reversal actually restates ──────────
        # CA8-9 review fix: absorption was keyed on the marshal, not on
        # which act the composer chose, so a reversal whose fall clause was
        # a dispossession deleted a battle France WON and its 12,000
        # casualties, which appeared nowhere else in the dispatch. Demoting
        # instead of deleting is not the answer either — that reinstates the
        # CA8-5 duplicate-beat shape when the reversal genuinely does
        # restate the beat.
        _absorbed = set()
        if _arc.get("fall_arm") == "defeat":
            _absorbed.add(f"own_mauled:{_name}")
        elif _arc.get("fall_arm") == "rout":
            _absorbed.add(f"own_broken:{_name}")
        if _absorbed:
            candidates[:] = [c for c in candidates
                             if c.get("identity") not in _absorbed]
        _add("marshal_reversal", identity=f"marshal_reversal:{_name}",
             line=_arc["reversal_line"])

    if not candidates:
        return None

    return _select_headline(world, candidates)


def _select_headline(world, candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Choose the lead from scored candidates and record what led.

    Extracted from `_build_headline` (PC-7) so the whole rule — weight order,
    the July-19 exact-repeat demotion, and the standing-class cooldown — is
    one testable source rather than a tail nobody could reach without
    building a world.
    """
    candidates.sort(key=lambda c: c["weight"], reverse=True)

    # Creative audit July 19 2026: several candidates are STATE-based
    # (estate_eroding, enemy_on_our_soil) rather than event-based, so a standing
    # condition re-won the lead every turn and the briefing opened with a
    # verbatim repeat — "Marshal Ney's household goes unpaid" led two turns
    # running, which reads as a frozen screen rather than a standing crisis.
    # When the top candidate repeats yesterday's headline, lead with the next
    # DISTINCT candidate and demote the repeat to a sub-beat: the news changes,
    # the standing crisis is still reported, nothing is lost. Reads the prior
    # dispatch (already serialized, and only overwritten AFTER this returns), so
    # no new state is introduced.
    _prev = (getattr(world, "last_morning_dispatch", None) or {})
    _prev_text = ((_prev.get("headline") or {}).get("text") or "")
    if _prev_text and len(candidates) > 1 and candidates[0]["text"] == _prev_text:
        for _i, _c in enumerate(candidates):
            if _c["text"] != _prev_text:
                candidates.insert(0, candidates.pop(_i))
                break

    # ── PC-7: the standing-class lead cooldown ──────────────────────────
    # The memory is its OWN serialized field, not a read of the prior
    # dispatch: `_build_headline` returns None on a candidate-free turn and
    # the caller then never writes `dispatch["headline"]`, so a memory
    # nested in the dispatch would be wiped by exactly the quiet turns that
    # a passive campaign is made of — freeing the standing class to lead
    # again immediately, which is the defect.
    memory = dict(getattr(world, "headline_lead_memory", None) or {})
    top_candidate = candidates[0]
    streak = 0
    if (top_candidate["class"] == memory.get("class")
            and top_candidate["identity"] == memory.get("identity")):
        streak = int(memory.get("streak") or 0)

    # ── CA9-N9: cross-turn memory for EVERY candidate, not just the lead ──
    # `streak` counts consecutive turns in the LEAD, so a standing crisis
    # demoted to a sub-beat by the PC-7 cooldown had its count reset — and
    # then repeated the same sentence in the sub-beat slot indefinitely.
    # Measured: the Tyrol supply line ran six consecutive dispatches
    # verbatim, and T15/T16 were the same three sentences permuted.
    #
    # `runs` rides `headline_lead_memory`, which is ALREADY a serialized
    # field, as a new KEY — so this needs no new state and pre-CA9 saves
    # land on `{}` and behave exactly as before. It counts consecutive
    # turns each identity has APPEARED anywhere on the page.
    prior_runs = dict(memory.get("runs") or {})
    # A pre-CA9 save (and the PC-7 unit fixtures) carry `streak` and no
    # `runs`. Seed the leader's run from it so a campaign already in
    # progress escalates on its next dispatch rather than restarting its
    # count — and so the PC-7 sole-crisis rule keeps its meaning.
    _mem_identity = memory.get("identity")
    if _mem_identity and _mem_identity not in prior_runs:
        prior_runs[_mem_identity] = int(memory.get("streak") or 0)
    runs = {c["identity"]: int(prior_runs.get(c["identity"], 0)) + 1
            for c in candidates}

    # ── CA9-N47: the escalation bank, hoisted out of the `for…else` ──────
    # `_STANDING_ESCALATION` had NEVER fired. It sat in the `else` of a
    # `for` that breaks on the first candidate with a different identity —
    # so it needed the standing class to be the ONLY candidate on the page
    # — AND it needed `streak > STANDING_LEAD_MAX`, which the yield below
    # makes unreachable by re-keying the memory to whatever led instead.
    # It was self-gating: reachable only from a state only it could produce.
    #
    # It now keys on the RUN (turns the crisis has been reported, wherever
    # it landed) rather than on the lead streak, and is applied BEFORE the
    # yield decision — so the sentence advances whether the standing class
    # leads or is demoted. That is what kills the verbatim repetition; the
    # variants say how long it has gone unanswered, which is the one thing
    # about a standing crisis that IS new each turn.
    for _idx, _cand in enumerate(candidates):
        if _cand["class"] not in STANDING_HEADLINE_CLASSES:
            continue
        _run = int(runs.get(_cand["identity"], 1))
        if _run <= STANDING_LEAD_MAX:
            continue
        variants = _STANDING_ESCALATION.get(_cand["class"]) or []
        if not variants:
            continue
        step = min(_run - STANDING_LEAD_MAX - 1, len(variants) - 1)
        fmt = dict(_cand.get("fields") or {})
        # The identity-derived name stays authoritative (it is what the
        # run is keyed on); for `estate_eroding` the two agree, so the
        # escalation copy renders exactly as it was authored to.
        fmt["marshal"] = _cand.get("identity", "").split(":", 1)[-1]
        fmt["turns"] = _run
        try:
            candidates[_idx] = dict(_cand, text=variants[step].format(**fmt))
        except (KeyError, IndexError):
            # A variant naming a field this candidate does not carry keeps
            # the authored line rather than crashing the briefing.
            continue
    top_candidate = candidates[0]

    if top_candidate["class"] in STANDING_HEADLINE_CLASSES and streak >= STANDING_LEAD_MAX:
        # Yield to any other candidate; the standing one falls to a sub-beat
        # through the loop below, so it is reported, never deleted.
        for _i, _c in enumerate(candidates):
            if _c["identity"] != top_candidate["identity"]:
                candidates.insert(0, candidates.pop(_i))
                break

    top = candidates[0]
    world.headline_lead_memory = {
        "class": top["class"],
        "identity": top["identity"],
        "streak": (streak + 1
                   if (top["class"] == memory.get("class")
                       and top["identity"] == memory.get("identity"))
                   else 1),
        "runs": runs,
    }
    # ────────────────────────────────────────────────────────────────────
    # CA8-5: dedupe on (class, identity), not on rendered TEXT.
    #
    # The played campaign's climax rendered as a triplicate arithmetic
    # report — `Ney was mauled at Bohemia: 2,218` / `2,099` / `2,269`, three
    # genuinely distinct battles taking all three editorial slots on the one
    # turn the player most needed the game to speak. Exact-text dedupe could
    # never catch it: three casualty figures are three strings. The identity
    # key that fixes it was already being computed four lines above and used
    # only for streak memory.
    #
    # Text remains in the key so a class that renders identically from two
    # different identities still collapses.
    # ────────────────────────────────────────────────────────────────────
    # ────────────────────────────────────────────────────────────────────
    # WO-D6 (slice 4): THE DIVERSE TAIL.
    #
    # Dedupe alone is not enough when the turn produces four of one kind.
    # Measured on the 1805 board — four homeland provinces lost, Soult
    # taken prisoner — the page read three province lines and Soult, at
    # weight 95, never appeared in ANY event ordering. The LAST slot is
    # therefore reserved for a kind of news not already on the page.
    #
    # The trap, and why this is a PREFERENCE and not a collapse: the naive
    # "one beat per class" reds CA8-5's own falsifiable negative
    # (`test_two_different_marshals_still_get_two_beats`) and CA8-9's
    # (`test_another_marshals_break_is_not_absorbed`). Two different men
    # broken on the same turn are two pieces of news. So the rule only
    # ever REORDERS what is eligible, and falls back to the ordinary
    # highest-weighted candidate when no fresh class exists.
    #
    # It DOES displace one candidate for another, and the first draft of
    # this comment claimed otherwise ("nothing is ever dropped") — which
    # the review round falsified on the real board: an unbounded freshness
    # preference evicted a weight-99 fallen homeland province in favour of
    # a weight-48 foreign congress. Hence the floor: the slot may vary the
    # KIND of news, never at a material cost in gravity.
    # ────────────────────────────────────────────────────────────────────
    seen_keys = {(top["class"], top["identity"]), ("", top["text"])}
    seen_classes = {top["class"]}
    sub_beats = []
    while len(sub_beats) < SUB_BEAT_SLOTS:
        eligible = [c for c in candidates[1:]
                    if not any(k in seen_keys for k in _headline_keys(c))]
        if not eligible:
            break
        pick = eligible[0]
        if len(sub_beats) == SUB_BEAT_SLOTS - 1:
            _floor = int(pick["weight"]) - DIVERSE_TAIL_MAX_WEIGHT_DROP
            pick = next((c for c in eligible
                         if c["class"] not in seen_classes
                         and int(c["weight"]) >= _floor), pick)
        seen_keys.update(_headline_keys(pick))
        seen_classes.add(pick["class"])
        sub_beats.append(pick["text"])
    return {
        "class": top["class"],
        "weight": int(top["weight"]),
        "text": top["text"],
        "sub_beats": sub_beats,
    }


# N26 (CA9): one number-word source for the file. `_derive_danger` had
# the word "two" hardcoded into a sentence that ran on a five-turn famine.
_COUNT_WORDS = {2: "two", 3: "three", 4: "four", 5: "five"}


def _turns_ago_phrase(turn: Optional[int], now: int) -> str:
    """'this turn' / 'last turn' / 'three turns ago' — CA8-9 joins beats
    that are up to five turns apart, so the gap has to be spoken."""
    if turn is None:
        return ""
    gap = int(now) - int(turn)
    if gap <= 0:
        return "this turn"
    if gap == 1:
        return "last turn"
    return f"{_COUNT_WORDS.get(gap, str(gap))} turns ago"


def _compose_reversal_line(world, marshal, crown_turn, estate, lost_estate,
                           crown_lost, consecutive, hunted_by, fled) -> str:
    """CA8-9: ONE sentence that names the rise and the fall together.

    The played campaign's five beats were each individually correct and
    mutually unaware. This is the join — it never invents a beat, it only
    states the two the event log already recorded, in order.
    """
    now = int(world.current_turn)
    who = humanize_entity_name(marshal.name)

    # ── the ascent ────────────────────────────────────────────────────────
    # CA8-9 review fix: the ESTATE is the object of "endowed with", not the
    # man's honorific. `derive_title` returns "Duke of Carniola" — the only
    # value any producer writes — so interpolating it here printed "endowed
    # with Duke of Carniola". Built from the region through the same single
    # source the capture prompts use.
    estate_noun = ""
    if estate and estate.get("region"):
        from backend.game_logic.dotation import derive_estate_noun
        estate_noun = derive_estate_noun(estate["region"])
    # The ascent is an APPOSITIVE and must close with a comma, or the
    # sentence runs on: "Ney, crowned three turns ago has been beaten".
    if crown_turn is not None and estate_noun:
        rise = (f"{who}, crowned {_turns_ago_phrase(crown_turn, now)} and "
                f"endowed with {estate_noun},")
    elif crown_turn is not None:
        rise = f"{who}, crowned {_turns_ago_phrase(crown_turn, now)},"
    elif estate_noun:
        rise = (f"{who}, endowed with {estate_noun} "
                f"{_turns_ago_phrase(estate.get('turn'), now)},")
    else:                                   # unreachable while rose is set
        rise = who

    # ── the fall, strongest first ─────────────────────────────────────────
    if hunted_by:
        # CA8 sweep 4 review: the roster arm stopped inventing a frontier
        # crossing and this one — the WEIGHT-91 HEADLINE, which is the string
        # the player actually reads, since `reversal_line` supersedes `line`
        # whenever it exists — kept asserting it unconditionally. `fled` here
        # is the FORCED-rout count, so the crossing clause is only claimed
        # when a rout really put him across one.
        hunter = humanize_entity_name(hunted_by)
        fall = (f"has been hunted across the frontier by {hunter}" if fled
                else f"has been hunted on consecutive turns by {hunter}")
    elif consecutive >= 2:
        fall = f"has been beaten {consecutive} turns running"
    elif consecutive == 1:
        fall = "has been beaten in the field"
    elif fled >= 1:
        fall = "has been driven back"
    else:
        fall = "has lost what it bought him"

    # No "Sire — " prefix here: the headline template owns the register
    # (the `war_touches_us` idiom), and the roster note is not addressed.
    head = f"{rise} {fall}"

    # ── the dispossession and the laurels, when they are the same story ──
    # Built WITHOUT leading conjunctions, so the join can place exactly one.
    tail: List[str] = []
    if lost_estate and lost_estate.get("region"):
        by = lost_estate.get("by") or ""
        taker = formed_display_name(world, by) if by else "the enemy"
        # CA8 sweep 4: PC-9 landed `with_definite_article` for exactly this —
        # the same sentence says "endowed with THE Duchy of Carniola" two
        # clauses earlier and then "Duchy of Normandy holds Berry now".
        tail.append(f"{with_definite_article(taker)} holds "
                    f"{lost_estate['region']} now")
    if crown_lost:
        # CA8-9 review fix: `recompute_crowns` VACATES the crown on a
        # top-of-ladder tie, so "passed to another" was a flat falsehood
        # whenever two marshals drew level — nobody holds them. The engine's
        # own sibling line says only "the laurels have passed", deliberately.
        _successor = any(
            getattr(p, "glory_crowned", False)
            for p in world.marshals.values()
            if p.nation == marshal.nation and p.name != marshal.name)
        tail.append("the laurels have passed to another" if _successor
                    else "the laurels sit vacant")

    if not tail:
        return head + "."
    if len(tail) == 1:
        return f"{head} — and {tail[0]}."
    return f"{head} — {tail[0]}, and {tail[1]}."


def _build_marshal_arcs(world, player_nation: str,
                        cap: Optional[int] = 3) -> Dict[str, Dict[str, Any]]:
    """W6-3 §5.3: derive per-marshal drama chains from the recent event-log
    window (last ~5 turns; bounded scan, GR8-safe) — no new serialized state.

    Returns marshal_name -> {consecutive_defeats, hunted_by, fled_across,
    rise, reversal_line, line} for marshals with an active chain; max 3
    lines per dispatch, highest-stakes first.

    ════════════════════════════════════════════════════════════════════════
    CA8-9 (creative audit, Aug 4 2026): THE ARC COULD NARRATE A FALL AND
    NEVER A RISE.

    The played campaign told a complete five-beat tragedy and joined none of
    it: Ney crowned (T3) -> ennobled Duke of Carniola (T8) -> broken at
    Bohemia (T10) -> the estate confiscated by Austria the same turn (T10) ->
    "the laurels have passed" (T12), that last one a bare warning bullet
    wedged between a supply note and a congratulation. Not one line referred
    to any other, though the engine knew the connection at battle time — the
    diorama payload for that very battle carries `"name": "Ney"` with
    `"crowned": true` while reporting him losing 2,218 men.

    The blindness was ONE `if`, not a missing vocabulary. The four victory
    outcomes arrive on the same `battle` event this loop already parses and
    were thrown away; `glory_crowned`, `dotation_granted` and
    `estate_confiscated` were all already in `world.log_event` and simply
    never read here.

    Two deliberate derivations, because the obvious sources do not exist:
      - THE CROWN LOSS has no `log_event` twin (only the GAIN branch writes
        one, `jealousy.py:333-337`) and `glory_crown_lost` is not a
        campaign-log type. It is derived instead from live serialized state:
        crowned inside the window + `marshal.glory_crowned` now False.
      - "HE TOOK THE PROVINCE" is not derivable at all — every
        `region_captured` producer writes {region, captured_by,
        captured_from, method} and names no marshal. Do not add an ascent
        arm for it here expecting the event to carry a man.

    Rise data ENRICHES existing arcs and never creates one on its own, so
    the `== {}` and cap-of-3 pins hold unchanged. The reversal — a rise and
    a fall inside one window — is the only new way in, and it requires a
    fall, so a pure ascent can never manufacture an arc (nor, by
    construction, a headline: see CA8-26, which is gated).
    ════════════════════════════════════════════════════════════════════════
    """
    window_start = world.current_turn - 5
    defeats: Dict[str, List[int]] = {}          # marshal -> defeat turns
    attackers: Dict[str, List[tuple]] = {}      # marshal -> [(turn, attacker)]
    retreats: Dict[str, int] = {}               # marshal -> retreat count
    routs: Dict[str, int] = {}                  # marshal -> FORCED only
    rout_turns: Dict[str, List[int]] = {}       # marshal -> forced-rout turns
    # CA8-9 rise/fall inputs — all already logged, no new producers.
    crowned: Dict[str, int] = {}                # marshal -> turn crowned
    endowed: Dict[str, Dict[str, Any]] = {}     # marshal -> {turn,title,region}
    dispossessed: Dict[str, Dict[str, Any]] = {}  # marshal -> {turn,region,by}

    for e in world.event_log:
        turn = e.get("turn", 0)
        if turn < window_start:
            continue
        etype = e.get("type", "")
        if etype == "battle":
            outcome = e.get("outcome", "")
            atk, dfn = e.get("attacker", ""), e.get("defender", "")
            atk_nation = e.get("attacker_nation", "")
            def_nation = e.get("defender_nation", "")
            if def_nation == player_nation:
                # CA8 sweep 4: this used to append on EVERY battle, with no
                # reference to `outcome`, so a marshal who WON two defensive
                # battles on consecutive turns was narrated as "hunted across
                # the frontier" — the exact shape the CA8-9 review believed it
                # had killed for `crown_lost`, surviving on a different term.
                # It was spared the headline only by accident (`fall_turn`
                # stays None for a pure win-hunt), which evaporates the moment
                # one of the two is lost. Being hunted means being pressed,
                # not being visited.
                if not ("defender" in outcome and "victory" in outcome):
                    attackers.setdefault(dfn, []).append((turn, atk))
                if "attacker" in outcome and "victory" in outcome:
                    defeats.setdefault(dfn, []).append(turn)
            if (atk_nation == player_nation
                    and "defender" in outcome and "victory" in outcome):
                defeats.setdefault(atk, []).append(turn)
        elif etype == "retreat":
            name = e.get("marshal", "")
            # CA8 sweep 4: every sibling branch guards on nation and this one
            # did not, while `world_state` logs retreats for ENEMY marshals by
            # name. Reachable through vassal assimilation, which keeps the
            # marshal's name and rewrites his nation: measured, a marshal who
            # routed three times under Bavaria's flag, was assimilated, and
            # was crowned under France, LED the French dispatch at weight 91
            # with "has been driven back" — his service under his old flag
            # following him across.
            if name and e.get("nation", player_nation) == player_nation:
                retreats[name] = retreats.get(name, 0) + 1
                # CA8-9 review fix: a VOLUNTARY withdrawal is not a fall.
                # `movement_executor`'s own retreat verb logs this same event
                # type; only the four rout sites stamp `forced: True`
                # (the discipline CA8-5 landed for `own_broken`). Counted
                # separately so `fled_across` keeps its pre-CA8-9 meaning and
                # its pins — the reversal reads THIS one.
                if e.get("forced"):
                    routs[name] = routs.get(name, 0) + 1
                    rout_turns.setdefault(name, []).append(int(turn))
        elif etype == "glory_crowned":
            # Producer is player-nation-only (jealousy.py:321), but the
            # nation guard is kept explicit so a future producer widening
            # cannot leak an enemy's rise into the player's dispatch.
            name = e.get("marshal", "")
            if name and e.get("nation", player_nation) == player_nation:
                crowned[name] = int(turn)
        elif etype == "dotation_granted":
            name = e.get("marshal", "")
            if name and e.get("nation", player_nation) == player_nation:
                endowed[name] = {"turn": int(turn),
                                 "title": e.get("title", ""),
                                 "region": e.get("region", "")}
        elif etype == "estate_confiscated":
            name = e.get("marshal", "")
            if name and e.get("nation", player_nation) == player_nation:
                dispossessed[name] = {"turn": int(turn),
                                      "region": e.get("region", ""),
                                      "by": e.get("confiscated_by", "")}

    arcs: Dict[str, Dict[str, Any]] = {}
    for m in world.marshals.values():
        if m.nation != player_nation or m.strength <= 0:
            continue
        d_turns = sorted(set(defeats.get(m.name, [])))
        consecutive = 0
        run = 1
        for i in range(1, len(d_turns)):
            if d_turns[i] - d_turns[i - 1] == 1:
                run += 1
            else:
                run = 1
            consecutive = max(consecutive, run)
        if len(d_turns) == 1:
            consecutive = 1

        hunted_by = ""
        by_attacker: Dict[str, List[int]] = {}
        for turn, atk in attackers.get(m.name, []):
            by_attacker.setdefault(atk, []).append(turn)
        for atk, turns in by_attacker.items():
            ts = sorted(set(turns))
            for i in range(1, len(ts)):
                if ts[i] - ts[i - 1] == 1:
                    hunted_by = atk
                    break
            if hunted_by:
                break

        fled = retreats.get(m.name, 0)

        # ── CA8-9: the ascent half, and the reversal that joins them ──────
        crown_turn = crowned.get(m.name)
        estate = endowed.get(m.name)
        lost_estate = dispossessed.get(m.name)
        # The crown loss has no event of its own — a crowning inside the
        # window against a marshal who no longer wears it IS the loss.
        crown_lost = bool(crown_turn is not None
                          and not getattr(m, "glory_crowned", False))
        rose = crown_turn is not None or estate is not None
        # ────────────────────────────────────────────────────────────────
        # A fall the reversal can hang on.
        #
        # CA8-9 review fix — `crown_lost` is NOT a fall. `recompute_crowns`
        # clears the flag whenever a same-nation marshal out-scores the
        # holder, i.e. on a French SUCCESS, and vacates it entirely on a
        # tie. Since `crown_lost` implies `crown_turn is not None`, which is
        # itself a disjunct of `rose`, one event satisfied BOTH halves of
        # `rose and fell` — so a marshal who fought nothing, retreated
        # nowhere and lost no estate produced a weight-91 tragedy headline
        # because a colleague won a battle. It stays as the TAIL clause it
        # already was, so a crown lost beside a real fall is still narrated.
        #
        # Retreats count only when FORCED: an ordered withdrawal must never
        # be narrated as a ruin (the CA8-5 discipline).
        # ────────────────────────────────────────────────────────────────
        routed = routs.get(m.name, 0)
        fell = (consecutive >= 1 or bool(hunted_by) or routed >= 1
                or lost_estate is not None)
        reversal = bool(rose and fell)

        # Which act the composer will narrate, and when it happened — the
        # headline arm needs both: it absorbs only the beat it restates, and
        # it must not present a five-turn-old defeat as this turn's news.
        if hunted_by:
            fall_arm = "hunted"
        elif consecutive >= 1:
            fall_arm = "defeat"
        elif routed >= 1:
            fall_arm = "rout"
        else:
            fall_arm = "estate"
        _fall_turns = list(d_turns) + list(rout_turns.get(m.name, []))
        if lost_estate:
            _fall_turns.append(int(lost_estate.get("turn", 0)))
        fall_turn = max(_fall_turns) if _fall_turns else None

        stakes = (consecutive >= 2) or hunted_by or (fled >= 2) or reversal
        if not stakes:
            continue

        if hunted_by:
            # CA8 sweep 4: `max(fled, 1)` invented a frontier crossing that
            # never happened — "across 1 frontier" for a marshal who never
            # withdrew. CA8-9 promoted this string into `status_note`, so it
            # is the marshal's headline row now, not a secondary note.
            hunter = humanize_entity_name(hunted_by)
            if fled:
                frontier_word = "frontier" if fled == 1 else "frontiers"
                line = (f"Hunted by {hunter} across {fled} {frontier_word} — "
                        f"stands at {m.location} with {int(m.strength):,} men.")
            else:
                line = (f"Hunted by {hunter} on consecutive turns — holds "
                        f"{m.location} with {int(m.strength):,} men.")
        elif consecutive >= 2:
            line = (f"{consecutive} defeats in as many turns — "
                    f"{int(m.strength):,} men remain at {m.location}.")
        elif fled >= 2:
            line = (f"Has fallen back {fled} times in five turns — "
                    f"now at {m.location} with {int(m.strength):,} men.")
        else:
            # Reversal-only entry: the fall is the dispossession or the
            # lost crown, so the roster note states the standing, not a
            # defeat tally that would read as zero.
            line = (f"Stands at {m.location} with {int(m.strength):,} men.")

        reversal_line = ""
        if reversal:
            reversal_line = _compose_reversal_line(
                world, m, crown_turn=crown_turn, estate=estate,
                lost_estate=lost_estate, crown_lost=crown_lost,
                consecutive=consecutive, hunted_by=hunted_by, fled=routed)

        arcs[m.name] = {
            "consecutive_defeats": int(consecutive),
            "hunted_by": hunted_by,
            "fled_across": int(fled),
            "line": line,
            # CA8-9 ascent/reversal payload. `reversal_line` is the joined
            # sentence; empty when the arc is a fall with no rise behind it.
            "rose": bool(rose),
            "crown_lost": crown_lost,
            "estate_lost": bool(lost_estate),
            "reversal_line": reversal_line,
            "fall_arm": fall_arm if reversal else "",
            "fall_turn": fall_turn,
            # Stakes score for the roster's max-3 display cap. NOT a claim
            # that a reversal outranks a bare chain: `consecutive + fled` is
            # unbounded, so a long chain legitimately scores higher. The
            # headline arm no longer consumes the capped dict (see `cap`),
            # so a 4th-ranked reversal is scored rather than deleted.
            "_stakes": ((2 if hunted_by else 0) + consecutive + fled
                        + (4 if reversal else 0)),
        }

    # Display cap: max 3 arc lines per dispatch, highest-stakes first.
    #
    # CA8-9 review fix: this cap was authored for the ROSTER's display lines
    # and the headline arm was reading the same capped dict, so a 4th-ranked
    # reversal was deleted before it could be scored — not demoted to a
    # sub-beat, and absent from the roster too. `cap=None` lets the headline
    # arm see every arc; it picks exactly one candidate by weight anyway.
    if cap is not None and len(arcs) > cap:
        keep = sorted(arcs.items(), key=lambda kv: kv[1]["_stakes"],
                      reverse=True)[:cap]
        arcs = dict(keep)
    for arc in arcs.values():
        arc.pop("_stakes", None)
    return arcs


def _intel_marshal_is_enemy(world, player_nation: str, km: dict) -> bool:
    """True when a known-marshal intel entry is an ACTIVE belligerent vs the
    player — the 'enemy' predicate for the danger/threat readings below.

    Excludes the player's own marshals AND non-belligerents (allies, vassals,
    neutrals). A co-located ALLY must never inflate a threat/danger reading
    (playtest F3: a Bavarian ally sharing the field at Munich lit a false
    "IN PERIL - an enemy force ... shares the field"). ``is_at_war`` is the
    single source; it already excludes allies, vassals, and neutrals.
    """
    km_nation = km.get("nation")
    if not km_nation or km_nation == player_nation:
        return False
    return bool(world.is_at_war(player_nation, km_nation))


def _derive_danger(marshal, world, player_nation: str,
                   supply_turns: Dict[str, List[int]]) -> str:
    """W6-3 §5.2: one danger string per marshal row ("" when none).

    Fog-legal: the co-located-enemy check reads the player's own intel of
    the marshal's region (never omniscient marshal data — R5).
    """
    # 1. Co-located with an enemy force >= 1.5x own strength (fog-legal).
    intel = world.intel.get(marshal.location)
    if intel is not None and intel.visibility != UNKNOWN and marshal.strength > 0:
        enemy_total = 0
        for km in intel.known_marshals:
            if not _intel_marshal_is_enemy(world, player_nation, km):
                continue
            if "strength" in km:
                enemy_total += int(km["strength"])
            elif "band" in km:
                enemy_total += BAND_MIDPOINTS.get(km["band"], 0)
        if enemy_total >= 1.5 * marshal.strength:
            return (f"IN PERIL — an enemy force of ~{enemy_total:,} shares "
                    f"the field ({marshal.location}).")
    # 2. Morale failing.
    if int(marshal.morale) < 40:
        return f"Morale failing ({int(marshal.morale)}) — the men waver."
    # 3. Force-retreated last phase.
    if getattr(marshal, "retreating", False) or getattr(
            marshal, "retreated_this_turn", False):
        return "Fell back under fire — the corps is recovering."
    # 4. Supply attrition 2+ consecutive turns.
    #
    # N26 (CA9): this said "two turns running" on a famine that had run
    # five, while the headline on the same screen said "3 turns". The
    # honest figure is the TRAILING CONSECUTIVE RUN — deliberately NOT
    # `len(turns)`, because the window (`_collect_supply_attrition_turns`,
    # current_turn - 5) can hold a gap: [3, 4, 8] has len 3 and a real
    # streak of 1, and correctly says nothing at all today.
    #
    # Recorded, not absorbed: the roster reads a 6-turn window and the
    # headline a 3-turn one, so a five-turn famine now reads "five turns
    # running" beside a headline that says "3 turns". Two honest numbers
    # from two windows is strictly better than one false one, but it is
    # not agreement — that window belongs to the headline's own row.
    turns = sorted(set(supply_turns.get(marshal.name, [])))
    if turns and turns[-1] >= world.current_turn - 1:
        run = 1
        for i in range(len(turns) - 1, 0, -1):
            if turns[i] - turns[i - 1] != 1:
                break
            run += 1
        if run >= 2:
            # WO-12 (slice 12): the under-capacity concentration tax is not
            # starvation — the province feeds him; the press of corps on
            # one road does the killing. The event carries the cause.
            if _latest_supply_cause(world, marshal.name) == "concentration":
                return (f"Crowded — {marshal.location} carries more corps "
                        f"than its roads can bear, "
                        f"{_COUNT_WORDS.get(run, str(run))} turns running.")
            return (f"Starving — supply has failed at {marshal.location} "
                    f"{_COUNT_WORDS.get(run, str(run))} turns running.")
    return ""


_ROUT_CLAUSES = (
    "{routed}'s corps is broken and flees.",
    "{routed}'s corps breaks a second time on this ground and flees.",
    "{routed}'s corps is driven from {loc} yet again — broken, and fleeing.",
)


def _rout_clause(world, region_name: str, routed: str) -> str:
    """WO slice 12 (N-8b): the enemy-rout clause, rotated by how many
    battles this field has seen (`world.battle_counts`, serialized,
    incremented by `compose_battle_name` before the dispatch reads it).
    The first battle keeps the sentence the game has always printed."""
    count = int((getattr(world, "battle_counts", {}) or {}).get(region_name, 1) or 1)
    index = min(max(count, 1) - 1, len(_ROUT_CLAUSES) - 1)
    return _ROUT_CLAUSES[index].format(routed=routed, loc=region_name)


# WO-16 (slice 12): the absolute floor under the proportional "mauled"
# predicate. In-band tunable. RECORDED DISSENT, carried from the eval's
# §7.7 (this is a conscious re-open of the playtest's own killed claim
# #4): if 500 is tuned TWICE, take the fraction-of-national-strength
# form instead of tuning a third time.
OWN_MAULED_MIN_CASUALTIES = 500


def _mauled_proportion(casualties: int, pre_battle: int) -> str:
    """The share of the corps that fell, in the briefing's words."""
    ratio = casualties / pre_battle if pre_battle > 0 else 0.0
    if ratio >= 0.75:
        return "three-quarters"
    if ratio >= 0.5:
        return "half"
    if ratio >= 0.33:
        return "a third"
    return "a quarter"


def _collect_supply_attrition_turns(world) -> Dict[str, List[int]]:
    """Recent supply_attrition events per marshal (event-log window)."""
    result: Dict[str, List[int]] = {}
    window_start = world.current_turn - 5
    for e in world.event_log:
        if e.get("type") != "supply_attrition":
            continue
        if e.get("turn", 0) < window_start:
            continue
        name = e.get("marshal", "")
        if name:
            result.setdefault(name, []).append(int(e.get("turn", 0)))
    return result


def _latest_supply_cause(world, marshal_name: str) -> str:
    """WO-12: the cause stamped on the marshal's most recent attrition
    event in the same window `_collect_supply_attrition_turns` reads
    ("shortage" / "concentration"; an unstamped legacy row reads
    "shortage")."""
    window_start = world.current_turn - 5
    cause, latest = "shortage", -1
    for e in world.event_log:
        if e.get("type") != "supply_attrition" or e.get("marshal") != marshal_name:
            continue
        turn = int(e.get("turn", 0) or 0)
        if turn < window_start or turn < latest:
            continue
        latest = turn
        cause = str(e.get("cause") or "shortage")
    return cause


def _lower_first(text: str) -> str:
    """Fold the executor's own refusal into the middle of a sentence
    without rewriting it — CA9-F10 quotes those strings verbatim so the
    briefing and the order cannot say different things."""
    text = str(text or "").rstrip(".")
    if not text:
        return text
    return text[0].lower() + text[1:]


def _supply_strain_candidate(world, player_nation: str) -> Optional[Dict[str, Any]]:
    """The starving-corps headline's data, or None (econ spec review §5).

    Two consecutive turns of loss in one province, our own marshals only.
    Returns the WORST such province by cumulative loss so a two-front famine
    leads with the one that is killing more men.

    The remedy clause is the point. ⊕ `supply_depot`'s `allowed_in` is
    capital/major_city/city, so it is ILLEGAL in 16 of France's 28 provinces
    — telling a starving army in a town to build a depot is advice the
    executor will refuse. Where a depot is legal we say so; where it is not
    we name the real remedy, which is the one the played campaign never
    took: disperse, using the military AP that sat idle.
    """
    from backend.models.region import BUILDING_TYPES
    window = [e for e in world.event_log
              if e.get("type") == "supply_attrition"
              and e.get("nation") == player_nation
              and e.get("turn", 0) >= world.current_turn - 2]
    if not window:
        return None

    by_region: Dict[str, Dict[str, Any]] = {}
    for e in window:
        region_name = e.get("region", "")
        if not region_name:
            continue
        slot = by_region.setdefault(
            region_name, {"turns": set(), "losses": 0, "marshals": set()})
        slot["turns"].add(int(e.get("turn", 0)))
        slot["losses"] += int(e.get("losses", 0) or 0)
        if e.get("marshal"):
            slot["marshals"].add(e["marshal"])

    # ────────────────────────────────────────────────────────────────────
    # CA8-2 (creative audit, Aug 4 2026): RECENCY. This picked by CUMULATIVE
    # loss over a 3-turn window with no requirement that any of those turns
    # be the current one, so turn 5 led with Munich quoting turn 4's frozen
    # 11,251 while every attrition line on that same dispatch read Tyrol.
    # The strain must be one the army is paying NOW.
    #
    # The predicate is "the latest turn the window actually saw", not
    # `world.current_turn`: the dispatch is built after the turn advances,
    # so pinning to the counter would silently match nothing.
    # ────────────────────────────────────────────────────────────────────
    latest_turn = max(int(e.get("turn", 0)) for e in window)
    persistent = {r: s for r, s in by_region.items()
                  if len(s["turns"]) >= 2 and latest_turn in s["turns"]}
    if not persistent:
        return None
    region_name = max(persistent, key=lambda r: persistent[r]["losses"])
    slot = persistent[region_name]

    region = world.get_region(region_name)
    if region is None:
        return None
    here = [m for m in world.get_marshals_in_region(region_name)
            if m.nation == player_nation and m.strength > 0]
    total = sum(int(m.strength) for m in here)
    # HC-4a (review round [13]): the SAME effective cap the attrition
    # pass applies — home turf AND the naval shore verdict. A strangled
    # home coast must headline as the strain it is; the old inline
    # formula read 1.5× and reported "no strain" while men died.
    cap = int(world.get_effective_supply_cap(player_nation, region))
    over = max(0, total - cap)
    # CA8-2 (a): the template said "stand MORE men over what X can feed" —
    # a word that fired precisely when the overage was ZERO. There is no
    # honest sentence to write when the stack is no longer over capacity:
    # the strain has ended, and claiming it stands is the falsehood the
    # played campaign led six of twelve dispatches with. Yield the slot.
    if over <= 0:
        return None

    # ────────────────────────────────────────────────────────────────────
    # CA9-F10: ask the EXECUTOR whether the depot is legal.
    #
    # This modelled two preconditions (region type, already-built) while
    # `_execute_build` enforced eight, so the briefing prescribed a depot
    # the executor refused — six identical false firings in the played
    # campaign, and the one time the player obeyed it: "Cannot build in
    # Tyrol — region stability too low (35/100). Need 51+." Same class as
    # closed CA8-2, different gate arm. §ECONOMY_REVISIT_SPEC:175 already
    # required this surface to name "whichever remedy is LEGAL".
    #
    # `can_build` returns the executor's own refusal string, so the
    # briefing can quote the exact sentence the order would have earned.
    # ────────────────────────────────────────────────────────────────────
    from backend.models.region import can_build
    depot_legal, depot_refusal, depot_remedy = can_build(
        world, region, "supply_depot", player_nation)

    # ────────────────────────────────────────────────────────────────────
    # PC15-D2: NAME THE SPLIT. "Move a corps" never once named a
    # destination while the legal remedy sat one province away all six
    # turns of the measured famine — the AI's own P6.5 dispersal rung
    # computes exactly this arithmetic. Headroom from the SAME
    # `get_effective_supply_cap` the attrition applies (shown = applied);
    # legality from the executor's own pure probe (CA9-F10 discipline —
    # an engaged marshal or a SHUT crossing is never counseled). Runs
    # once per dispatch on the ONE strained region: GR8-clean.
    # ────────────────────────────────────────────────────────────────────
    split_line = ""
    if here:
        from backend.commands.movement_executor import MovementExecutor
        probe_marshal = min(here, key=lambda m: int(m.strength))
        options = []
        for adj_name in getattr(region, "adjacent_regions", []) or []:
            adj_region = world.get_region(adj_name)
            if adj_region is None:
                continue
            adj_cap = int(world.get_effective_supply_cap(
                player_nation, adj_region))
            adj_occupancy = sum(
                int(m.strength) for m in world.get_marshals_in_region(
                    adj_name))
            headroom = adj_cap - adj_occupancy
            if headroom <= 0:
                continue
            if MovementExecutor.move_refusal_probe(
                    world, probe_marshal, adj_region, adj_name) is not None:
                continue
            options.append((headroom, adj_name))
        options.sort(reverse=True)
        if options:
            named = " and ".join(
                f"{name} can feed {headroom:,} more"
                for headroom, name in options[:2])
            split_line = (f"{named} — a corps marched there ends it.")

    disperse_clause = split_line or "Move a corps, or continue to pay."

    if depot_legal:
        remedy = (f"A supply depot at {region_name} would ease it; "
                  f"{split_line or 'dispersing a corps would end it.'}")
    elif depot_remedy == "repair":
        # The gate that made this row a lie: a DAMAGED depot reads as
        # absent to `has_building()` and blocks a build in the executor.
        remedy = (f"{region_name}'s depot is in ruins — repair it, or "
                  f"disperse a corps.")
    elif depot_remedy == "wait":
        turns = int((region.building_under_construction or {}).get(
            "turns_remaining", 0))
        remedy = (f"{region_name}'s depot is already going up "
                  f"({turns} turn{'s' if turns != 1 else ''} yet). "
                  f"{disperse_clause}")
    elif (region.controller and region.controller != player_nation
          and world.get_diplomatic_state(player_nation, region.controller)
          in world.ALLY_SUPPLY_STATES):
        # PC15-D2: on FED ally/vassal soil "not controlled by France" is
        # the wrong story — the host's magazines already feed us as our
        # own (the cap said so); the army is simply too large for the
        # province.
        from backend.game_logic.formations import formed_display_name
        remedy = (f"{formed_display_name(world, region.controller)}'s "
                  f"magazines feed us as our own — the army is simply too "
                  f"large for the province. {disperse_clause}")
    else:
        # CA9 review round, two defects in one sentence:
        #   (a) STUTTER — several of the executor's refusals open with
        #       "Cannot build in <region> — ", so wrapping them produced
        #       "No depot may be laid at Tyrol — cannot build in Tyrol —
        #       not controlled by France."
        #   (b) CASE — `_lower_first` lowercased the one refusal that
        #       opens with the region NAME: "tyrol already has a supply
        #       depot".
        # Strip the executor's own redundant lead-in and keep the prefix,
        # so the subject (a DEPOT) is never lost — my first cut dropped
        # the prefix wholesale and produced "town regions don't support
        # buildings" in a supply headline, with nothing saying of WHAT.
        _refusal = depot_refusal.rstrip(".")
        _lead = f"Cannot build in {region_name} — "
        if _refusal.startswith(_lead):
            _refusal = _refusal[len(_lead):]
        if _refusal.startswith(region_name):
            # Already a complete sentence about this province; prefixing
            # it would only repeat the name.
            remedy = f"{_refusal}. {disperse_clause}"
        else:
            remedy = (f"No depot may be laid at {region_name} — "
                      f"{_lower_first(_refusal)}. "
                      f"{disperse_clause}")

    # ────────────────────────────────────────────────────────────────────
    # CA8-2 (b)+(c): NAME THE MEN WHO ARE THERE. `slot["marshals"]`
    # accumulates across the whole 3-turn window, and the live-occupancy
    # fallback was unreachable whenever the window held any name at all —
    # so a turn-8 headline named five marshals of whom FOUR were in other
    # provinces, contradicted by the roster ten lines below on the same
    # dispatch. Worse, `over` was computed live from `here` while the names
    # came from the window: one sentence, two moments.
    #
    # Live occupancy is now authoritative and the window is only the
    # fallback, so the whole sentence describes one instant.
    # ────────────────────────────────────────────────────────────────────
    names = [m.name for m in here] or sorted(slot["marshals"])
    return {
        "region": region_name,
        "fields": {
            "who": _join_marshal_names(names),
            # PC15-12: subject-verb agreement — the fallback "our corps"
            # (empty names) reads singular too.
            "stand": "stand" if len(names) > 1 else "stands",
            "have": "have" if len(names) > 1 else "has",
            "over": f"{over:,}",
            "strength": f"{total:,}",
            # CA8-2: the capacity is stated — at the time, it appeared on
            # no screen the player could reach. (WO slice 8 has since put
            # the SAME effective figure on the ledger, the region panel
            # and the map tooltip; this line stays their dispatch twin.)
            "capacity": f"{cap:,}",
            "region": region_name,
            "losses": f"{int(slot['losses']):,} men",
            "turns": str(len(slot["turns"])),
            "remedy": remedy,
        },
    }


def _join_marshal_names(names) -> str:
    """"A", "A and B", "A, B and C" — the dispatch's own prose form."""
    clean = [str(n) for n in names if str(n or "").strip()]
    if not clean:
        return "our corps"
    if len(clean) == 1:
        return clean[0]
    return f"{', '.join(clean[:-1])} and {clean[-1]}"


def build_morning_dispatch(world, tactical_events: Optional[List] = None,
                           lapsed_offers: Optional[List] = None) -> Dict[str, Any]:
    """
    Build the morning dispatch dict for Godot rendering.

    Called AFTER turn_manager.end_turn() completes, so world state
    reflects the start of the new turn (post enemy phase, post tactical
    processing, post income).

    Args:
        world: WorldState instance
        tactical_events: Optional list of tactical event dicts from turn
            processing (attrition, construction, etc.). Absorbed into
            the dispatch's TURN EVENTS section.
        lapsed_offers: Optional list of lapse info dicts from turn-end.
            Each has nation, offer_type, proposal_type.

    Returns:
        Dict with turn, situation, marshals, intelligence, turn_events,
        berthier_note. All numeric values int()-wrapped.
    """
    # TODO: Post-EA — thread player_nation from world state
    player_nation = get_player_nation(world)

    dispatch = {
        "turn": int(world.current_turn),
        # HC-0: dated header ("" without an anchor — the client appends
        # only when non-empty, so legacy renders exactly as before).
        "calendar_label": world.get_calendar_label(),
        "situation": _build_situation(world, player_nation),
        "marshals": _build_marshal_status(world, player_nation),
        "intelligence": _build_intelligence(world, player_nation),
        "turn_events": _build_turn_events(tactical_events or [], player_nation),
    }

    # W6-3 §5.1: the dispatch opens with the turn's top story — one prose
    # headline + up to 2 sub-beats, scored from fog-visible events.
    headline = _build_headline(world, player_nation)
    if headline:
        dispatch["headline"] = headline

    # W6-7: captured marshals appear as a Prisoners line, not roster rows.
    prisoners = [
        {
            "name": m.name,
            "captor": m.captured_by,
            "captured_turn": int(m.captured_turn),
        }
        for m in world.marshals.values()
        if m.nation == player_nation and getattr(m, "captured_by", "")
    ]
    if prisoners:
        dispatch["prisoners"] = prisoners

    # Berthier note depends on marshals + situation (+ the headline, W6-3)
    # PC-7: the headline arm is priority 0 and short-circuits the ENTIRE
    # note ladder, so while a standing class holds the lead Berthier can
    # never reach "the treasury is exhausted", the treasury-bleeding note or
    # the idle-marshal note. Measured: 21 turns of a byte-identical note
    # about the estate rolls while an army starved. Once a standing class
    # has held the lead past its cooldown, hand the note back to the ladder
    # so the closing line can say something the opening line did not.
    _lead_class = (headline or {}).get("class", "")
    _memory = getattr(world, "headline_lead_memory", None) or {}
    if (_lead_class in STANDING_HEADLINE_CLASSES
            and int(_memory.get("streak") or 0) > STANDING_LEAD_MAX):
        _lead_class = ""
    dispatch["berthier_note"] = _pick_berthier_note(
        world, player_nation, dispatch["marshals"], dispatch["situation"],
        headline_class=_lead_class,
    )

    # ════════════════════════════════════════════════════════════
    # V2-85: TURN-LIMIT WARNINGS — alert player as campaign nears end
    # ════════════════════════════════════════════════════════════
    turn_limit_warning = _build_turn_limit_warning(world, player_nation)
    if turn_limit_warning:
        dispatch["turn_limit_warning"] = turn_limit_warning

    defeat_imminent_warning = _build_defeat_imminent_warning(world, player_nation)
    if defeat_imminent_warning:
        dispatch["defeat_imminent_warning"] = defeat_imminent_warning

    # Talleyrand's Report — proactive diplomatic suggestions (Session 4)
    dispatch["talleyrand_report"] = _build_talleyrand_report(world, player_nation)

    # ════════════════════════════════════════════════════════════
    # SESSION 6: Talleyrand sabotage discovery + override notes + redemption
    # ════════════════════════════════════════════════════════════
    dispatch["talleyrand_discovery"] = None
    dispatch["talleyrand_override_note"] = None
    dispatch["talleyrand_redemption"] = None

    _check_talleyrand_session6(dispatch, world, player_nation)

    # Coalition status (Session 7)
    dispatch["coalition_status"] = _build_coalition_section(world, player_nation)

    # WPS-A: Active war objectives
    war_objective_lines = _build_war_objective_section(world, player_nation)
    if war_objective_lines:
        dispatch["war_objectives"] = war_objective_lines

    # BPH-D §11.3: Peace settlement section from previous turn's ratifications
    peace_settlements = _build_peace_settlement_section(world)
    if peace_settlements:
        dispatch["peace_settlements"] = peace_settlements

    # Diplomatic events (Session 8D)
    diplomatic_events = _build_diplomatic_events_section(world, player_nation)

    # S2: Merge significant relation change events
    relation_events = _build_relation_change_events(world, player_nation)
    if relation_events:
        diplomatic_events.extend(relation_events)

    dispatch["diplomatic_events"] = diplomatic_events

    # ══════════════════════════════════════════════════════════════════
    # PT-E1, CORRECTED: the queue is retired where it is CONSUMED.
    #
    # The first cut pruned in `_advance_turn_internal` on the turn stamp,
    # and that is one frame off: the prune runs BEFORE the increment, so
    # events queued by systems INSIDE `advance_turn` — after it — carry
    # the NEW turn number and survived the next cycle's prune as well.
    # Probed: `diplomatic_dp_regen` stamped turn 2 was still in the queue
    # at turn 3, i.e. narrated in two consecutive briefings.
    #
    # Clearing at consumption is exact by construction: everything queued
    # since the last briefing is reported once, whether it was queued by
    # one of `end_turn`'s five phases or by a system inside `advance_turn`.
    # The turn-stamp prune stays as the safety net for the direct
    # `advance_turn()` callers that never build a dispatch.
    # ══════════════════════════════════════════════════════════════════
    if getattr(world, "pending_dispatch_events", None):
        world.pending_dispatch_events = []

    # Lapsed offers from previous turn-end
    if lapsed_offers:
        dispatch["lapsed_offers"] = [
            {
                "nation": offer["nation"],
                "proposal_type": (offer.get("proposal_type") or "proposal").replace("_", " "),
            }
            for offer in lapsed_offers
        ]

    pending_envoys = [
        {
            "nation": item.get("source_nation", "?"),
            "proposal_type": str(item.get("proposal_type", "proposal")).replace("_", " "),
            "state": item.get("state", "WAITING"),
        }
        for item in world.dialogue_manager.get_mailbox_items()
    ]
    if pending_envoys:
        dispatch["pending_envoy_count"] = int(len(pending_envoys))
        dispatch["pending_envoys"] = pending_envoys

    # Store on world for dispatch re-read screen (Session A)
    world.last_morning_dispatch = dispatch

    return dispatch


# ============================================================================
# SITUATION
# ============================================================================

def _build_situation(world, player_nation: str) -> Dict[str, Any]:
    """Build the SITUATION section of the dispatch."""
    player_regions = 0
    enemy_regions = 0
    for region in world.regions.values():
        if region.controller == player_nation:
            player_regions += 1
        elif region.controller is not None:
            enemy_regions += 1

    treasury = int(world.nation_gold.get(player_nation, 0))

    # Compute projected income/upkeep for this turn (same values the
    # executor shows in the turn header — recalculated on new-turn state)
    # CA9-N11: the dispatch describes the turn that JUST RAN, so every
    # component it names must be the one that was actually charged. Same
    # applied-cache preference the two turn-end banners already use
    # (meta_executor / executor); the fallback covers a loaded save and any
    # surface built before a turn has been processed.
    income_data = (getattr(world, "_income_phase_results", None) or {}).get(
        player_nation) or world.calculate_turn_income(player_nation)
    # Verify-fleet correction (Aug 2026): prefer the APPLIED upkeep too —
    # a recompute here reads post-_update_bankruptcy state (the F1 class).
    upkeep_data = income_data.get("upkeep_data") \
        or world.calculate_turn_upkeep(player_nation)
    income = int(income_data["income"])
    upkeep = int(upkeep_data["total"])
    # ES-2 (S6): occupation cost on non-homeland provinces — a separate
    # Net component (income above is GROSS), so the projection subtracts it
    occupation = int(income_data.get("occupation", 0))
    # EC-W1: income suspended by hostile armies — same treatment
    contributions = int(income_data.get("contributions", 0))
    # EB-5a: what our armies requisition from disrupted provinces (positive)
    requisitions = int(income_data.get("requisitions", 0))
    # EB-2: the authored overseas/colonial pool (positive)
    overseas = int(income_data.get("overseas", 0))
    # EB-1: the Charges of Empire (absorbs EC-W2's War Effort) — same treatment
    state_charges = int(income_data.get("state_charges", 0))
    # ES-7 (S7): income redirected to marshals' estates — same treatment
    dotation_skim = int(income_data.get("dotation_skim", 0))
    # ES-7 second pass (§0.6.8): the rente bill — same treatment
    rente_cost = int(income_data.get("rente_cost", 0))
    # EC-U2: infrastructure maintenance — same treatment (its own Net component)
    infrastructure = int(income_data.get("infrastructure", 0))

    # Trade income from diplomatic states (read-only calculation).
    # DEF-5 naval: gross trade shown; the blockade loss and the Admiralty
    # upkeep are their own components (the EC-W1 pattern).
    from backend.game_logic.diplomacy import calculate_trade_income
    trade_income_all = calculate_trade_income(world)
    trade_income = int(trade_income_all.get(player_nation, 0))
    blockade = 0
    if getattr(world, "fleets", None):
        from backend.game_logic.naval import blockade_trade_loss
        blockade = int(blockade_trade_loss(world).get(player_nation, 0))
    admiralty = int(income_data.get("admiralty", 0))

    # EB review [5] (the CA8-10 class, closed the CA8-10 way): this delta
    # was hand-assembled from a subset of the streams — it omitted vassal
    # tribute (712g at boot), the admin bonus, treaty gold and settlement
    # gold, so the morning briefing and the strategic ledger disagreed
    # about the same turn's net on every vassal-holding boot. Stop
    # hand-assembling: `_build_economy`'s net is the surface pinned to
    # equal the signed sum of its declared components.
    from backend.game_logic.ledger import _build_economy
    # CA9-N11: rendered to the player as "the turn's change", and it was
    # a fresh forward projection — wrong on all 15 turns of the played
    # campaign and wrong in SIGN twice.
    treasury_delta = int(_build_economy(
        world, player_nation,
        income_data=(getattr(world, "_income_phase_results", None) or {}).get(
            player_nation))["net"])
    # PT-C4: CA9-N11 is not fully closed, and this is its definitional half.
    # Every NAMED component agrees with the end-turn banner on all 18 turns
    # of the played campaign; only the total differs, because this surface
    # SUMS DECLARED COMPONENTS and the banner MEASURES the treasury. The
    # EC-W3 Butcher's Bill is charged outside Net by design (the plunder-gold
    # precedent), so the two can be individually correct and still disagree
    # — measured on 10 of 18 turns, this one always the more optimistic.
    #
    # The banner now names Materiel inside its own window. This surface says
    # what it is instead of claiming to be an observation: it is the ledger's
    # account of the turn, and a battle can still take gold it never
    # promised to predict.
    treasury_delta_label = "by the accounts"

    # ES-7 "Unmet Marshals" roll-up: every player marshal whose reward
    # expectation exceeds his estate income, with the eroding flag once the
    # grace window has elapsed (dotation.py — Europe-scoped, empty on the
    # legacy fixture). §0.6.8 item 4a: plus grace_turns_left (the action
    # window, counted down) and the marshal's current rente.
    unmet_marshals = []
    # §0.6.8 item 4a: expectation RISES since the last dispatch — "the game
    # tells you when they expect more". Reconciled against the serialized
    # Marshal.last_expectation_seen at dispatch build (once per turn).
    expectation_rises = []
    from backend.game_logic.dotation import (
        build_unmet_marshals, get_expectation, get_satisfaction,
        is_dotation_world,
    )
    if is_dotation_world(world):
        for m in world.marshals.values():
            if m.nation != player_nation or m.strength <= 0:
                continue
            expectation = get_expectation(m)
            satisfaction = get_satisfaction(m, world)
            previous_seen = int(getattr(m, "last_expectation_seen", 0))
            if expectation > previous_seen:
                if previous_seen > 0 or expectation > satisfaction:
                    # First-ever expectation with it already met stays
                    # quiet — announce demands, not bookkeeping.
                    expectation_rises.append({
                        "marshal": m.name,
                        "expectation": int(expectation),
                        "previous": int(previous_seen),
                        "satisfaction": int(satisfaction),
                    })
                m.last_expectation_seen = int(expectation)
        # UX23-R4: the rows themselves are now built by
        # `dotation.build_unmet_marshals`, so `GET /dispatch` can re-derive
        # them at read time without re-running this function — which latches
        # `last_expectation_seen` above, clears queued events, and rolls for
        # sabotage discovery. Byte-identical output; only the latch stayed.
        unmet_marshals = build_unmet_marshals(world, player_nation)

    bankrupt = int(world.nation_bankruptcy_turns.get(player_nation, 0)) > 0

    # Fog-filtered strength ratio
    french_strength = _get_nation_total_strength(world, player_nation)
    _estimate = _enemy_strength_estimate_detail(world, player_nation)
    estimated_enemy_strength = int(_estimate["total"])
    # WO-10 (slice 12): the estimator's own docstring records deliberate
    # under-estimation as the cost of poor intelligence; the sentence
    # rendered it unqualified ("2% of French forces" against a true 107%).
    # The client appends this note to the ratio sentence.
    enemy_strength_note = _enemy_strength_note(_estimate)
    if french_strength > 0:
        strength_ratio_pct = int(round(
            (estimated_enemy_strength / french_strength) * 100
        ))
    else:
        strength_ratio_pct = 999  # Edge case: no French forces

    # Authority — global player stat (V2b)
    authority = int(world.authority_tracker.authority) if hasattr(world, 'authority_tracker') else 100
    if authority >= 80:
        authority_label = "Strong"
    elif authority >= 50:
        authority_label = "Normal"
    else:
        authority_label = "Weak"

    return {
        "player_regions": int(player_regions),
        "enemy_regions": int(enemy_regions),
        "treasury": treasury,
        "treasury_delta": treasury_delta,
        "treasury_delta_label": treasury_delta_label,
        "trade_income": trade_income,
        # ES-2 (S6): occupation detail rides the dispatch like the ES-3
        # surcharge — the morning projection can explain the drain
        "occupation": occupation,
        # EC-W1/EB-1: the war-coupling drains ride the dispatch too, so
        # the morning projection can explain a wartime treasury squeeze
        "contributions": contributions,
        "state_charges": state_charges,
        # EB-5a/EB-2: the positive war-and-sea components, named so the
        # briefing can explain a rising chest too
        "requisitions": requisitions,
        "overseas": overseas,
        # ES-7 (S7): estate redirect + the Unmet Marshals roll-up — the
        # morning briefing names whose loyalty is at stake, not just a number
        "dotation_skim": dotation_skim,
        "unmet_marshals": unmet_marshals,
        # ES-7 second pass (§0.6.8): the rente bill + expectation rises —
        # the briefing announces WHEN a marshal starts expecting more
        "rente_cost": rente_cost,
        "expectation_rises": expectation_rises,
        # EC-U2: infrastructure maintenance — computed above since the EC-U2
        # slice but never returned until the Aug 2026 health-check audit, so
        # the briefing named every sibling drain except this one.
        "infrastructure": infrastructure,
        # DEF-5 naval: the blockade's trade loss + the Admiralty upkeep —
        # both in treasury_delta above, both named here so the briefing can
        # explain the squeeze
        "blockade": blockade,
        "admiralty": admiralty,
        # ES-3 (S5): over-limit breakdown rides the dispatch so the morning
        # projection can explain a heavy upkeep (treasury_delta above already
        # includes the surcharge via upkeep_data["total"]).
        "upkeep_surcharge": int(upkeep_data.get("surcharge", 0)),
        "force_limit": int(upkeep_data.get("force_limit") or 0),
        "over_force_limit": bool(upkeep_data.get("over_limit", False)),
        "bankrupt": bankrupt,
        "strength_ratio_pct": strength_ratio_pct,
        "enemy_strength_note": enemy_strength_note,
        "authority": int(authority),
        "authority_label": authority_label,
    }


def _get_nation_total_strength(world, nation: str) -> int:
    """Sum strength of all non-broken marshals for a nation."""
    total = 0
    for m in world.marshals.values():
        if m.nation == nation and not m.broken:
            total += m.strength
    return int(total)


def _estimate_enemy_strength_from_intel(world, player_nation: str) -> int:
    """
    Estimate total enemy strength using fog-filtered intel only.

    FULL visibility: use exact strength from known_marshals entries.
    PARTIAL/STALE/LAST_KNOWN: use band midpoint estimates.
    UNKNOWN: contributes 0 (we don't know).

    This intentionally underestimates when visibility is low —
    that's the cost of poor intelligence.
    """
    return int(_enemy_strength_estimate_detail(world, player_nation)["total"])


def _enemy_strength_note(detail: Dict[str, int]) -> str:
    """WO-10: the qualifier the ratio sentence owes its own estimator.
    Empty only when every known corps was read exactly AND something was
    counted — and even then the sentence says "known corps"."""
    counted = int(detail.get("counted", 0))
    exact = int(detail.get("exact", 0))
    if counted == 0:
        return "(no enemy corps in view — the figure counts nothing)"
    banded = counted - exact
    if banded > 0:
        return (f"(an estimate — {banded} of {counted} known corps read "
                f"from stale reports; unscouted armies are not counted)")
    return "(known corps only — unscouted armies are not counted)"


def _enemy_strength_estimate_detail(world, player_nation: str) -> Dict[str, int]:
    """WO-10 (slice 12): the estimator's arithmetic with its COVERAGE —
    `total` (what the dispatch always used), `counted` (known enemy corps)
    and `exact` (those read at FULL). One pass; the ratio and its
    qualifier come from the same walk."""
    total = 0
    counted = 0
    exact = 0
    # Track which marshal names we've already counted to avoid doubles
    counted_marshals: set = set()

    for region_name, intel in world.intel.items():
        if intel.visibility == UNKNOWN:
            continue

        for km in intel.known_marshals:
            if not _intel_marshal_is_enemy(world, player_nation, km):
                continue  # Skip own + non-belligerent (ally/vassal/neutral) forces
            name = km.get("name", "")
            if name in counted_marshals:
                continue
            counted_marshals.add(name)
            counted += 1

            if intel.visibility == FULL and "strength" in km:
                total += int(km["strength"])
                exact += 1
            elif "band" in km:
                total += BAND_MIDPOINTS.get(km["band"], 0)
            elif "strength" in km:
                # Frozen STALE snapshot — use band midpoint estimate
                band = get_strength_band(int(km["strength"]))
                total += BAND_MIDPOINTS.get(band, 0)
            else:
                # No strength data at all — use region-level band
                total += BAND_MIDPOINTS.get(intel.strength_band, 0)

    return {"total": int(total), "counted": int(counted), "exact": int(exact)}


# ============================================================================
# MARSHAL STATUS
# ============================================================================

def _build_marshal_status(world, player_nation: str) -> List[Dict[str, Any]]:
    """Build the MARSHAL STATUS section — one entry per friendly marshal.

    W6-3: rows gain a `danger` string (§5.2 — replaces the audit's
    "Awaiting orders" lie next to a 49k enemy) and an `arc_note` (§5.3 —
    the hunted-marshal callback) which also upgrades `status_note`.
    """
    arcs = _build_marshal_arcs(world, player_nation)
    supply_turns = _collect_supply_attrition_turns(world)
    result = []
    for marshal in world.marshals.values():
        if marshal.nation != player_nation:
            continue
        # W6-7: captured marshals leave the active roster — they appear in
        # the dispatch's Prisoners line instead (built in the main build).
        if getattr(marshal, "captured_by", ""):
            continue

        status, status_note = _derive_marshal_status(marshal, world)
        trust_val = int(marshal.trust.value) if hasattr(marshal.trust, 'value') else int(getattr(marshal, 'trust', 75))
        morale_val = int(marshal.morale)

        arc = arcs.get(marshal.name)
        # CA8-9: when the arc carries a reversal, the JOINED sentence is the
        # note — a man who was crowned and is now dispossessed is not
        # described by his defeat tally alone.
        arc_note = ""
        if arc:
            arc_note = arc.get("reversal_line") or arc["line"]
        if arc_note:
            status_note = arc_note

        entry = {
            "name": marshal.name,
            "location": marshal.location,
            "strength": int(marshal.strength),
            "status": status,
            "status_note": status_note,
            "arc_note": arc_note,
            # CA8-8/CA8-9: the idle count as an INT beside the prose. Rung 4
            # of Berthier's ladder used to recover it by `int(note.split()
            # [0])` off `status_note` — a slot the arc note legitimately
            # overwrites (pinned: test_arc_upgrades_the_status_note). Two
            # of the three arc shapes then raised and the rung was skipped;
            # the third ("4 defeats in as many turns") PARSED, and compared
            # a defeat count against an idle threshold — so a marshal beaten
            # four turns running was reported to the Emperor as growing
            # impatient for action.
            "idle_turns": int(getattr(marshal, "idle_turns", 0) or 0),
            "danger": _derive_danger(marshal, world, player_nation,
                                     supply_turns),
            "trust": trust_val,
            "trust_notable": trust_val < 55 or trust_val > 90,
            "morale": morale_val,
            "morale_warning": morale_val < 60,
        }
        result.append(entry)

    # Sort by strength descending (strongest marshal first)
    result.sort(key=lambda m: m["strength"], reverse=True)
    return result


def _derive_marshal_status(marshal, world) -> tuple:
    """
    Derive display status and note from marshal state.

    Returns (status_key: str, note: str).
    Priority order (highest wins):
    1. broken
    2. retreating
    3. strategic order active
    4. drilling / drilling_locked
    5. fortified
    6. artillery (at rest)
    7. idle_restless (aggressive personality, idle 3+ turns)
    8. awaiting (default)
    """
    # ETA is command-aware (MC gate Q3): high-command marshals rally 2 stages/turn.
    if marshal.broken:
        rally_stages = marshal.get_rally_stages_per_turn()
        recovery_turn = int(world.current_turn + -(-(4 - marshal.broken_recovery) // rally_stages))
        return "broken", f"Reforms T{recovery_turn}."

    if marshal.retreating:
        rally_stages = marshal.get_rally_stages_per_turn()
        recovery_turn = int(world.current_turn + -(-(3 - marshal.retreat_recovery) // rally_stages))
        return "retreating", f"Recovers T{recovery_turn}."

    if marshal.in_strategic_mode:
        order = marshal.strategic_order
        cmd = order.command_type
        target = order.target
        # Creative audit July 19 2026: a marshal holding a pending interrupt is
        # NOT marching — his order is frozen until the player answers. Reporting
        # "Moving to Swabia" for a man standing still awaiting a decision made
        # the dispatch lie about the one thing it exists to report. The pending
        # decision outranks the order it suspends.
        _pending = getattr(marshal, "pending_interrupt", None)
        if _pending:
            enemy = humanize_entity_name(_pending.get("enemy", "") or "")
            where = _pending.get("location", "") or marshal.location
            if enemy:
                return ("awaiting_decision",
                        f"HALTED at {where} — {enemy} bars the way. Awaiting your "
                        f"word.")
            return ("awaiting_decision",
                    f"HALTED at {where} — awaiting your word.")
        # W6-5 §7.2.3: a literal marshal's active order carries the doctrine
        # tell — he is doing exactly this, and only this.
        letter = (" (to the letter)"
                  if getattr(marshal, "personality", "") == "literal" else "")
        if cmd == "MOVE_TO":
            # PC-9 (quiet-France played campaign, Aug 3 2026): the dispatch
            # reported a marshal "Moving to Swabia" while he was standing in
            # Swabia. The order outlives the arrival on some paths, and the
            # status line read the ORDER rather than the man. Report where he
            # is when those are the same place — the Orders tab still shows
            # the standing order, so nothing is hidden.
            if target and target == marshal.location:
                return "arrived", f"Arrived at {marshal.location}.{letter}"
            return "en_route", f"Moving to {target}.{letter}"
        elif cmd == "PURSUE":
            return "en_route", f"Pursuing {target}.{letter}"
        elif cmd == "HOLD":
            return "en_route", f"Holding at {marshal.location}.{letter}"
        elif cmd == "SUPPORT":
            return "en_route", f"Supporting {target}.{letter}"
        else:
            return "en_route", f"{cmd} {target}.{letter}"

    if marshal.drilling or marshal.drilling_locked:
        return "drilling", "Drilling."

    if marshal.fortified:
        return "fortified", f"Fortified at {marshal.location}."

    if marshal.artillery:
        return "artillery", f"Artillery at {marshal.location}."

    personality = getattr(marshal, 'personality', 'balanced')
    if isinstance(personality, str):
        personality_str = personality.lower()
    else:
        personality_str = personality.value if hasattr(personality, 'value') else str(personality).lower()

    idle = getattr(marshal, 'idle_turns', 0)
    if personality_str == "aggressive" and idle >= 3:
        return "idle_restless", f"{idle} turns idle."

    return "awaiting", "Awaiting orders."


# ============================================================================
# INTELLIGENCE
# ============================================================================

def _build_intelligence(world, player_nation: str) -> List[Dict[str, Any]]:
    """
    Build fog-filtered INTELLIGENCE section.

    Iterates over all RegionIntel, extracts enemy marshals from
    known_marshals at PARTIAL+ visibility. Deduplicates by marshal name.

    W6-1 (BUG-CA-6): the dedup prefers RECENCY first, visibility rank as
    the tiebreak — a stale FULL snapshot must never beat this turn's
    PARTIAL truth (live audit: the intel table placed Mack at Swabia while
    the same turn's events and `status` had him in Franche-Comte).
    """
    # Collect sightings: marshal_name -> best sighting dict
    sightings: Dict[str, Dict[str, Any]] = {}

    visibility_rank = {FULL: 4, PARTIAL: 3, STALE: 2, LAST_KNOWN: 1, UNKNOWN: 0}

    for region_name, intel in world.intel.items():
        if intel.visibility == UNKNOWN:
            continue

        for km in intel.known_marshals:
            if km.get("nation") == player_nation:
                continue
            name = km.get("name", "Unknown")
            vis = intel.visibility
            rank = visibility_rank.get(vis, 0)
            updated = int(intel.last_updated_turn)

            existing = sightings.get(name)
            if existing and (
                (existing["intel_turn"],
                 visibility_rank.get(existing["visibility"], 0))
                >= (updated, rank)
            ):
                continue  # Already have fresher (or same-turn better) intel

            # Build strength display
            if vis == FULL and "strength" in km:
                strength_display = f"{int(km['strength']):,}"
            elif "band" in km:
                strength_display = km["band"]
            elif "strength" in km:
                # Frozen STALE snapshot — use band, not exact number
                strength_display = get_strength_band(int(km["strength"]))
            else:
                strength_display = intel.strength_band

            sightings[name] = {
                "name": humanize_entity_name(name),
                "location": region_name,
                "strength_display": strength_display,
                "visibility": vis,
                "intel_turn": int(intel.last_updated_turn),
            }

    # Sort: FULL first, then PARTIAL, etc.
    result = sorted(
        sightings.values(),
        key=lambda s: visibility_rank.get(s["visibility"], 0),
        reverse=True,
    )
    return result


# ============================================================================
# TURN EVENTS (absorbed from tactical events)
# ============================================================================

# Event types relevant to the dispatch (player-visible turn events).
# Acts as a WHITELIST: only these event types appear in the TURN EVENTS section.
_DISPATCH_EVENT_TYPES = {
    # Warning severity
    "supply_attrition", "bankruptcy_desertion",
    "occupation_abandoned", "cavalry_stance_forced",
    "cavalry_fortify_forced", "fortify_decayed",
    "fortify_collapsed", "counter_punch_expired",
    "capital_proximity_alert", "auto_glorious_charge",
    "reckless_move",
    # Good severity
    "construction_complete", "occupation_complete",
    "drill_complete", "retreat_recovery",
    # CA9-F13: a standing order voided by a battle the marshal answered
    # rather than chose. It died silently; the player learned of it by
    # giving him an order two turns later.
    "order_voided_by_battle",
    "garrison_regen", "broken_recovered",
    # Info severity (no special highlight)
    "occupation_continues", "drill_locked", "drill_started",
    "fortify_strengthened", "fortify_stable",
    "broken_recovery", "reckless_no_target",
    # W6-3 §5.4: vassal loyalty drift, with its CAUSE named at emission
    # ("Switzerland loyalty 84 (-8): puppet resentment, war weariness").
    "vassal_loyalty",
    # W6-5 §7.2.4: the literal fidelity beat ("Soult holds at Lorraine,
    # per your orders — the guns at Franche-Comte did not move him.")
    "literal_fidelity",
    # W6-7 Marshal Fates: capture + last stand reach the morning briefing.
    "marshal_captured",
    "last_stand",
    "marshal_released",
    # PC15-1: annihilation reaches the briefing's turn-events rail too.
    "marshal_destroyed",
    # Jealousy v3.2 (docs/JEALOUSY_SPEC.md §11): the grievance arc — from
    # Berthier's restlessness warning through fire, autonomous attack,
    # escalation, resolution, and the glory crown changing heads.
    "jealousy_restlessness",
    "jealousy_fired",
    "jealousy_autonomous_warning",
    "jealousy_autonomous_attack",
    # WO-28 (WO slice 17): the fore-warned attack that was REFUSED, with
    # the executor's reason — the beat above narrated it as fought.
    "jealousy_autonomous_refused",
    "jealousy_escalation",
    "jealousy_resolved",
    "jealousy_separation_warning",
    "glory_crowned",
    "glory_crown_lost",
    # ESP-1: the collective petition announcement line.
    "fontainebleau_petition",
    # NP-3 §6.3 (added by the NP promise audit, Aug 15 2026): the Petition
    # for Independent Command's arrival beat. The producer appends it to
    # the turn events and the narration cap already exempts it — but it was
    # never added HERE, so `_build_turn_events` dropped it at the whitelist
    # and the beat the slice's own commit describes never reached a
    # dispatch. Its sibling above has always been whitelisted.
    "shadow_petition",
    # A13 (CA9 row 3): the overflow tail when the routine drama lines are
    # capped. AI-6's `intent_movement_tail` idiom, on this pipeline.
    "jealousy_drama_tail",
    # Marshal recruitment: a new commander joins the roster.
    "marshal_commissioned",
    # PC15-10 B0 (F3): a petition moment the occupied channel swallowed —
    # the card is lost (WAD), the MOMENT must not be (no silent losses).
    "rivalry_blocked_note",
    "war_weary_blocked_note",
    # WO-38 (slice-18 review round): an unanswered strategic objection
    # lapsing at the turn boundary. The lapse's whole contract is that it
    # is TOLD — the shadow_petition entry above records what happens when
    # a new beat is appended to the turn events but never added HERE.
    "strategic_objection_lapsed",
}


def _build_turn_events(
    tactical_events: List[Dict], player_nation: str
) -> List[Dict[str, str]]:
    """
    Build the TURN EVENTS section from tactical events.

    Filters to player-relevant events and produces short one-liner messages.
    Each entry has 'message' (str) and 'severity' ('info' | 'warning' | 'good').
    """
    result = []
    for event in tactical_events:
        event_type = event.get("type", "")
        msg = event.get("message", "")
        if not msg:
            continue

        # Whitelist filter: only dispatch-relevant event types
        if event_type not in _DISPATCH_EVENT_TYPES:
            continue

        # Filter: only show events relevant to player nation
        event_nation = event.get("nation")
        if not event_nation:
            continue  # Skip events with no nation (safety net)
        if event_nation != player_nation:
            continue  # Skip enemy attrition etc.

        severity = "info"
        if event_type in ("supply_attrition", "bankruptcy_desertion",
                          "occupation_abandoned", "cavalry_stance_forced",
                          "cavalry_fortify_forced", "fortify_decayed",
                          "fortify_collapsed", "counter_punch_expired",
                          "capital_proximity_alert", "auto_glorious_charge",
                          "reckless_move", "reckless_no_target",
                          "marshal_captured", "last_stand",
                          "marshal_destroyed",
                          "jealousy_fired", "jealousy_autonomous_warning",
                          "jealousy_autonomous_attack",
                          "jealousy_autonomous_refused",   # WO-28: same register as its siblings
                          "jealousy_escalation",
                          "jealousy_separation_warning", "glory_crown_lost",
                          "fontainebleau_petition", "shadow_petition"):
            severity = "warning"
        elif event_type in ("construction_complete", "occupation_complete",
                            "drill_complete",
                            "garrison_regen", "broken_recovered",
                            "marshal_released",
                            "jealousy_resolved",
                            "glory_crowned", "marshal_commissioned"):
            severity = "good"
        elif event_type in ("order_voided_by_battle",
                            "strategic_objection_lapsed"):
            # CA9-F13 / WO-38: not good news — a plan the player made
            # (or a question they were owed) is gone.
            severity = "warning"
        elif event_type == "retreat_recovery":
            # N37 (CA9): a corps still carrying a -40% effectiveness
            # penalty was reported as GOOD news. It is good news only at
            # the stage where the penalty is gone.
            #
            # It must NOT simply become "info": `retreat_recovered` is not
            # in `_DISPATCH_EVENT_TYPES`, so the final stage of THIS event
            # is the only recovery news the player ever gets. Stage 3 keeps
            # `good`; the intermediate stages, which are reports of a corps
            # still broken, drop to `info`.
            severity = "good" if int(event.get("stage", 0)) >= 3 else "info"
        elif event_type == "vassal_loyalty":
            # W6-3: falling loyalty is a warning; rising is mere info.
            severity = "warning" if int(event.get("delta", 0)) < 0 else "info"

        result.append({"message": msg, "severity": severity,
                       "type": event_type, "_source": event})

    return collapse_turn_events(result)


# ── PT-E3: the turn report becomes readable ────────────────────────────
#
# The narration pillar is the only one that ROSE in the playtest, and it
# is held under 7 by VOLUME: 101 dispatch lines over 14 turns, 7.2 per
# morning, 30% of them supply, with the identical vassal remedy tail
# eleven times. Neither renderer caps or buckets anything — N events
# produce N lines, on both surfaces, byte-parallel.
#
# The machinery is IGR-B's, proven one surface over (`campaign_log.
# collapse_refusal_family`), and its discipline is copied exactly:
#
#   * PURE and view-layer. The producer and every serialized event are
#     untouched; this reduces the rendered list only.
#   * An explicit TYPE ALLOWLIST, never a bare key. IGR-B's own docstring
#     records why: a bucket key that is not unique to the family deletes
#     rows that merely share its vocabulary.
#   * A bucket of one passes through UNCHANGED — same object, same
#     sentence. Only a genuine repeat collapses.
#   * The collapsed row is a shallow copy carrying display-only keys, and
#     its sentence is built from the source events' STRUCTURED fields
#     (region, losses, vassal), never by re-parsing the prose.
#   * Zero `.gd` diff: the row keeps `message` + `severity`.
COLLAPSIBLE_TURN_EVENT_TYPES = ("supply_attrition", "vassal_loyalty")
TURN_EVENT_NAMED_LIMIT = 3


def _collapsed_supply_line(sources) -> str:
    losses = sum(int(e.get("losses", 0) or 0) for e in sources)
    places = []
    for event in sources:
        region = str(event.get("region", "") or "")
        if region and region not in places:
            places.append(region)
    where = _join_place_names(places)
    if not losses:
        return f"Supply told on the corps at {where}."
    return (f"Supply cost you {losses:,} men, at {where}."
            if where else f"Supply cost you {losses:,} men.")


def _collapsed_vassal_line(sources) -> str:
    """A bucket is severity-homogeneous by construction: the key includes
    `severity`, and a falling vassal is `warning` while a rising one is
    `info`. So a mixed bucket cannot occur, and no branch pretends to
    handle one — the direction is read off the bucket, not guessed."""
    names, falling = [], 0
    for event in sources:
        name = str(event.get("vassal", "") or "")
        if not name:
            continue
        names.append(name)
        if int(event.get("delta", 0) or 0) < 0:
            falling += 1
    if not names:
        return "The satellites shifted."
    verb = "drifted" if falling >= len(names) - falling else "steadied"
    return (f"{len(names)} satellite{'s' if len(names) != 1 else ''} "
            f"{verb} — {_join_place_names(names)}.")


_COLLAPSED_LINE_BUILDERS = {
    "supply_attrition": _collapsed_supply_line,
    "vassal_loyalty": _collapsed_vassal_line,
}


def _join_place_names(names) -> str:
    """Bounded like IGR-B's `COLLAPSE_NAMED_LIMIT` — a short list loses no
    names, a long one stops being a wall."""
    names = [str(n) for n in names if str(n).strip()]
    if not names:
        return ""
    if len(names) > TURN_EVENT_NAMED_LIMIT:
        rest = len(names) - TURN_EVENT_NAMED_LIMIT
        return f"{', '.join(names[:TURN_EVENT_NAMED_LIMIT])} and {rest} more"
    if len(names) == 1:
        return names[0]
    return ", ".join(names[:-1]) + " and " + names[-1]


def collapse_turn_events(rows: List[Dict]) -> List[Dict[str, str]]:
    """Bucket repeated families into one line each, in first-seen order."""
    buckets: Dict[tuple, List[int]] = {}
    for index, row in enumerate(rows):
        row_type = row.get("type", "")
        if row_type not in COLLAPSIBLE_TURN_EVENT_TYPES:
            continue
        buckets.setdefault((row_type, row.get("severity")), []).append(index)

    superseded = set()
    for key, indices in buckets.items():
        if len(indices) < 2:
            continue          # a bucket of one is not a repeat
        superseded.update(indices[1:])

    out: List[Dict[str, str]] = []
    for index, row in enumerate(rows):
        if index in superseded:
            continue
        key = (row.get("type", ""), row.get("severity"))
        indices = buckets.get(key) or []
        clean = {"message": row.get("message", ""),
                 "severity": row.get("severity", "info"),
                 "type": row.get("type", "")}
        if len(indices) >= 2 and index == indices[0]:
            builder = _COLLAPSED_LINE_BUILDERS.get(clean["type"])
            sources = [rows[i].get("_source") or {} for i in indices]
            if builder:
                clean["message"] = builder(sources)
            clean["collapsed_count"] = len(indices)
        out.append(clean)
    return out


# ============================================================================
# BERTHIER'S CLOSING NOTE
# ============================================================================

def _pick_berthier_note(
    world,
    player_nation: str,
    marshals_data: List[Dict],
    situation: Dict,
    headline_class: str = "",
) -> str:
    """
    Pick the highest-priority Berthier closing note.

    W6-3 §5.4: when the dispatch carries a headline, the note answers IT
    (one template per headline class) — Berthier closes on the story he
    opened with. Otherwise the existing priority ladder decides.

    Priority (highest first):
    0. Headline-aware note (W6-3)
    1. Marshal broken
    2. Bankrupt
    3. Treasury negative delta
    3.5 A live grievance among the marshals (Jealousy v3.2 §5)
    4. Aggressive marshal idle 4+ turns
    5. All marshals at full readiness
    6. Default

    CA8-8 (creative audit, Aug 4 2026): rung 3.5 was real, undocumented, and
    STARVING the rung below it. Berthier closed 7 of 11 played dispatches on
    the byte-identical "The marshals' rivalries demand attention, Sire" and
    never once mentioned Murat standing idle at Rhineland with 19,312 men
    for nine turns while the army bled.

    The spec ordering is NOT changed — §5 places a live grievance above
    idle_restless deliberately. What changed is that rung 3.5 now says
    WHICH grievance and, when the aggrieved marshal is also the idle one,
    names the idleness in the same breath.

    SCOPE, corrected after review: both new arms are gated on there being
    exactly ONE aggrieved player marshal. With two or more — reachable
    (`MAX_FIRES_PER_NATION_TURN = 2`) and guaranteed by the tier-3 mutual
    spiral, which makes the target jealous back by construction — the
    pre-CA8-8 collective sentence still returns. Rung 4 also remains
    shadowed by any live grievance, which is spec §5's deliberate ordering
    and not something this row changes. Widening either belongs at a gate.
    """
    if headline_class and headline_class in _HEADLINE_BERTHIER_NOTES:
        # PT-J4 "The Bench Speaks": when the headline is OUR marshal taken
        # and the executor's own commission gate would grant a replacement
        # RIGHT NOW, Berthier's answer names the bench and a price — the
        # loss moment is the teaching moment (the Marshalate was built as
        # W6-7's recovery path and no surface ever said so: "commission"
        # appeared zero times in 108 measured responses). Availability is
        # first_affordable_commission — the gate itself, never a copy —
        # so the sentence can never promise what the executor refuses.
        # PC15-1: a DESTROYED marshal shares the capture's recovery path —
        # the bench is the only way back, so the same commission arm rides
        # both loss classes.
        if headline_class in ("marshal_captured", "marshal_destroyed"):
            from backend.game_logic.recruitment import (
                first_affordable_commission,
            )
            bench = first_affordable_commission(world, player_nation)
            if bench is not None:
                return (
                    f"{_HEADLINE_BERTHIER_NOTES[headline_class]} And the "
                    f"Marshalate holds men yet, Sire — "
                    f"{bench.get('name', '?')} awaits a commission at "
                    f"{int(bench.get('cost', 0)):,}g."
                )
        return _HEADLINE_BERTHIER_NOTES[headline_class]
    # 1. Broken marshal — pick strongest broken one
    broken = [m for m in marshals_data if m["status"] == "broken"]
    if broken:
        worst = max(broken, key=lambda m: m["strength"])
        return (
            f"Sire, {worst['name']} requires time to reform "
            f"- he cannot be counted upon."
        )

    # 2. Bankrupt
    if situation.get("bankrupt"):
        return "Our finances are dire, Sire. The treasury is exhausted."

    # 3. Treasury bleeding
    delta = situation.get("treasury_delta", 0)
    if delta < 0:
        return f"Our finances strain, Sire. The treasury bleeds {abs(delta)}g this turn."

    # 3.5 Jealousy v3.2 (spec §5 priority: below broken/bankrupt/bleeding,
    # above idle_restless) — a live grievance among the marshals.
    #
    # CA8-8: this used to say the same eleven words every turn and name no
    # rival, no cause and no remedy. It now names WHO he resents, and — when
    # the aggrieved man is also the idle one — says so in the same sentence,
    # because that is not a coincidence: being passed over is what the
    # grievance IS. The rung below is thereby no longer starved of its only
    # actionable fact.
    _idle_by_name = {m.get("name"): int(m.get("idle_turns", 0) or 0)
                     for m in marshals_data}
    # A12 (CA9 row 3): this rung used to read `jealous[0]` and `jealous[:2]`
    # in `world.marshals` DICT ORDER — i.e. whichever Frenchman appears
    # earliest in the scenario JSON, never the most aggrieved. Measured over
    # a 40-turn ambient run, every one of the 27 grievance-bearing turns
    # fell to the collective fallback and named the same two men.
    #
    # Ranked by the system's own severity vocabulary, all from stored state
    # (no `_threshold_for` recompute at a display seam): escalation level
    # first, then how many times the quarrel has flared, then how long it
    # has left to run. Ties break on name so the sentence is stable.
    def _grievance_rank(m):
        rival_name = getattr(m, "jealous_of", "") or ""
        return (
            -int(get_escalation_level(m, rival_name)),
            -int(_lifetime_fires(m, rival_name)),
            -int(getattr(m, "jealousy_turns_remaining", 0) or 0),
            m.name,
        )

    try:
        from backend.game_logic.jealousy import (
            _lifetime_fires,
            any_player_grievance,
            get_escalation_level,
        )
        if any_player_grievance(world):
            jealous = sorted((
                m for m in world.marshals.values()
                if m.nation == player_nation and getattr(m, "jealous_of", None)
            ), key=_grievance_rank)
            if jealous:
                first = jealous[0]
                rival = humanize_entity_name(
                    getattr(first, "jealous_of", "") or "")
                who = humanize_entity_name(first.name)
                idle = _idle_by_name.get(first.name, 0)
                if len(jealous) == 1 and rival and idle >= 4:
                    return (f"{who} nurses a grievance against {rival}, Sire "
                            f"— and has stood idle {idle} turns. Those are "
                            f"the same fact.")
                if len(jealous) == 1 and rival:
                    return (f"{who} nurses a grievance against {rival}, Sire. "
                            f"The rivalry wants settling before it is tested.")
                # Two or more, worst first. The singular arm that used to
                # hang off this sentence was structurally dead — it sits
                # below two `len == 1` returns.
                names = ", ".join(humanize_entity_name(m.name)
                                  for m in jealous[:2])
                return (f"The marshals' rivalries demand attention, Sire — "
                        f"{names} nurse a grievance, {who}'s the deepest.")
    except Exception:
        pass

    # 4. Aggressive marshal idle 4+ turns
    #
    # CA8-8: reads the INT the roster row now carries. It used to recover the
    # count with `int(status_note.split()[0])` — a slot the arc note
    # legitimately overwrites (pinned by test_arc_upgrades_the_status_note),
    # so two of three arc shapes raised and were swallowed, and the third,
    # "N defeats in as many turns", parsed CLEANLY and compared a defeat
    # tally to an idle threshold. A marshal beaten four turns running was
    # reported to the Emperor as growing impatient for action.
    restless = [m for m in marshals_data if m["status"] == "idle_restless"]
    for m in restless:
        # Status fires at 3+; the note escalates at 4+ (deliberate dead zone,
        # pinned negatively by test_idle_restless_three_turns_no_note).
        if int(m.get("idle_turns", 0) or 0) >= 4:
            return (f"{m['name']} grows impatient, Sire. He will require "
                    f"action soon.")

    # 5. All marshals at full readiness (no broken, retreating, drilling)
    #
    # CA8-8: `idle_restless` joins the list. Without it, an army with a
    # marshal standing still for three turns was told "Your armies stand
    # ready, Sire. The initiative is ours." — the failure below rung 4 was
    # not a silent default but an active and false reassurance.
    non_ready_statuses = {"broken", "retreating", "drilling", "idle_restless"}
    all_ready = all(m["status"] not in non_ready_statuses for m in marshals_data)
    if all_ready and marshals_data:
        return "Your armies stand ready, Sire. The initiative is ours."

    # 6. Default
    return "Your orders, Sire."


# ============================================================================
# V2-85: TURN-LIMIT WARNINGS
# ============================================================================

def _build_turn_limit_warning(world, player_nation: str) -> Optional[Dict[str, Any]]:
    """Build turn-limit warning for the Morning Dispatch.

    Fires at 5/2/1 turns remaining (post-advance: remaining == 4/1/0).
    Also creates a notification for the notification bar.

    Returns warning dict or None.

    EC-6a: sandbox worlds get no turn-limit copy and no TURN_LIMIT_WARNING
    notification — the campaign is open-ended, there is no limit to warn about.
    """
    if getattr(world, "sandbox_mode", False):
        return None

    from backend.models.world_state import VICTORY_REGION_FRACTION

    current = int(world.current_turn)
    max_turns = int(world.max_turns)
    remaining = max_turns - current

    # 4C-2: Thresholds adjusted for post-advance_turn timing.
    # When dispatch builds, current_turn is already the NEW turn.
    # "5 turns remain" means 5 playable turns left → remaining == 4 after advance.
    if remaining > 4:
        return None

    total_regions = len(world.regions)
    threshold = max(1, int(total_regions * VICTORY_REGION_FRACTION))
    player_regions = len(world.get_player_regions())

    if remaining == 4:
        message = "The campaign enters its final phase — 5 turns remain."
        severity = "warning"
    elif remaining == 1:
        message = (
            f"Only 2 turns remain. France must control {threshold} regions for victory. "
            f"Current: {player_regions}/{threshold}."
        )
        severity = "warning"
    elif remaining == 0:
        message = (
            f"FINAL TURN. France must control {threshold} regions for victory. "
            f"Current: {player_regions}/{threshold}."
        )
        severity = "critical"
    elif remaining < 0:
        message = (
            f"The campaign has reached its conclusion. "
            f"France controls {player_regions}/{threshold} required regions."
        )
        severity = "critical"
    else:
        # remaining is 2 or 3 — no warning at these turns
        return None

    # Fire notification
    from backend.notifications import (
        create_notification, NotificationPriority, TURN_LIMIT_WARNING,
    )
    # remaining is post-advance; actual playable turns = remaining + 1 (includes current)
    actual_turns = remaining + 1 if remaining > 0 else 0
    world.notifications.add(create_notification(
        TURN_LIMIT_WARNING,
        NotificationPriority.HIGH,
        f"{actual_turns} turns remain" if actual_turns > 0 else "Final turn",
        message,
        current,
    ))

    return {
        "message": message,
        "severity": severity,
        "turns_remaining": int(remaining),
        "player_regions": int(player_regions),
        "victory_threshold": int(threshold),
    }


def _build_defeat_imminent_warning(world, player_nation: str) -> Optional[Dict[str, Any]]:
    """Build deterministic near-defeat warning aligned with live loss rules."""
    from backend.game_logic.turn_manager import get_defeat_imminent_state
    from backend.notifications import (
        create_notification, NotificationPriority, DEFEAT_IMMINENT_WARNING,
    )

    world.notifications.dismiss_by_type(DEFEAT_IMMINENT_WARNING)

    if getattr(world, "player_nation", player_nation) != player_nation:
        return None

    warning = get_defeat_imminent_state(world)
    if not warning:
        return None

    priority = (
        NotificationPriority.CRITICAL
        if warning["severity"] == "critical"
        else NotificationPriority.HIGH
    )
    world.notifications.add(create_notification(
        DEFEAT_IMMINENT_WARNING,
        priority,
        warning["notification_title"],
        warning["message"],
        int(world.current_turn),
        details={
            "living_marshal_count": int(warning["living_marshal_count"]),
            "living_marshals": list(warning["living_marshals"]),
            "controlled_region_count": int(warning["controlled_region_count"]),
            "controlled_regions": list(warning["controlled_regions"]),
        },
    ))

    return {
        "message": warning["message"],
        "severity": warning["severity"],
        "living_marshal_count": int(warning["living_marshal_count"]),
        "living_marshals": list(warning["living_marshals"]),
        "controlled_region_count": int(warning["controlled_region_count"]),
        "controlled_regions": list(warning["controlled_regions"]),
    }


# ============================================================================
# TALLEYRAND'S REPORT — Proactive diplomatic suggestions (Phase 8 Session 4)
# ============================================================================

# Trigger priority levels
_PROACTIVE_TRIGGERS = [
    # (trigger_type, priority, cooldown_turns, checker_function)
    # Priority: lower = higher priority. Max 2 suggestions per dispatch.
]


def _build_talleyrand_report(world, player_nation: str) -> List[Dict[str, str]]:
    """
    Build Talleyrand's Report section for the Morning Dispatch.

    Returns list of 0-2 observation dicts with 'message' and 'trigger_type'.
    Suppressed entirely if an incoming AI proposal is pending this turn.

    Trigger conditions (from CONV_DESIGN §5d):
    1. Acceptance crossed 50 threshold for a nation
    2. War score shifted ≥15 in one turn
    3. Vassal loyalty warnings (Phase 8 Session 5)
    4. Relation threshold crossed (-40, -20, 0, +20, +40)
    5. No diplomatic action for 3+ turns
    """
    # Suppression: if incoming AI proposal pending, Talleyrand is busy
    pending = getattr(world, 'pending_diplomatic_dialogue', None)
    if pending and pending.get("type") == "incoming_proposal":
        return []

    observations = []
    cooldowns = getattr(world, 'proactive_suggestion_cooldowns', {})

    # Helper: check if a trigger is on cooldown
    def _on_cooldown(nation: str, trigger_type: str) -> bool:
        key = f"{nation}|{trigger_type}"
        return cooldowns.get(key, 0) > 0

    def _set_cooldown(nation: str, trigger_type: str, turns: int) -> None:
        key = f"{nation}|{trigger_type}"
        cooldowns[key] = turns

    # R91: Map current diplomatic state to the next upgrade proposal type
    UPGRADE_MAP = {
        "WAR": "peace",
        "ARMISTICE": "peace",
        "PEACE": "open_borders",
        "OPEN_BORDERS": "non_aggression",
        "NON_AGGRESSION": "defensive_alliance",
        "DEFENSIVE_ALLIANCE": "alliance",
    }

    from backend.game_logic.diplomatic_dialogue import get_known_nations
    active = set(world.get_active_nations())  # DLF-11
    known_nations = sorted(n for n in get_known_nations(world) if n in active)

    for nation in known_nations:
        if len(observations) >= 2:
            break

        diplo_key = world._make_diplo_key(player_nation, nation)
        state = world.get_diplomatic_state(player_nation, nation)
        relation = world.nation_relations.get(diplo_key, 0)

        # ── Trigger 1: Acceptance crossed 50 (diplomatic opportunity) ──
        if not _on_cooldown(nation, "acceptance_crossed") and state != "WAR":
            try:
                from backend.game_logic.diplomacy import calculate_acceptance
                upgrade_type = UPGRADE_MAP.get(state, "non_aggression")
                hypothetical = {
                    "type": upgrade_type,
                    "proposer_nation": player_nation,
                    "target_nation": nation,
                    "sweeteners": [],
                    "demands": [],
                    "clauses": [],
                }
                result = calculate_acceptance(hypothetical, world)
                if result["score"] >= 50:
                    observations.append({
                        "message": (
                            f"Sire, I believe {nation} may be ready to discuss "
                            f"improved relations. The diplomatic winds favor us."
                        ),
                        "trigger_type": "acceptance_crossed",
                        "target_nation": nation,
                        "priority": 2,
                        "elaborate_type": "proposal_options",
                    })
                    _set_cooldown(nation, "acceptance_crossed", 10)
            except Exception:
                import logging
                logging.getLogger(__name__).exception("Error in acceptance trigger for %s", nation)

        # ── Trigger 2: War score shift ≥15 (per-turn delta) ──
        if not _on_cooldown(nation, "war_score_shift") and state == "WAR":
            raw_score = world.war_scores.get(diplo_key, 0)
            prev_raw = getattr(world, 'previous_war_scores', {}).get(diplo_key, 0)
            # Sign adjust for France perspective
            parts = diplo_key.split("|")
            if len(parts) == 2 and parts[0] == nation:
                war_score = -raw_score
                prev_score = -prev_raw
            else:
                war_score = raw_score
                prev_score = prev_raw
            delta = war_score - prev_score
            if abs(delta) >= 15:
                direction = "in our favor" if delta > 0 else "against us"
                observations.append({
                    "message": (
                        f"The war with {nation} has shifted dramatically {direction}. "
                        f"War score stands at {int(war_score)}. "
                        f"This changes our diplomatic options significantly."
                    ),
                    "trigger_type": "war_score_shift",
                    "target_nation": nation,
                    "priority": 1,
                    "elaborate_type": "advisory",
                })
                _set_cooldown(nation, "war_score_shift", 3)

        # ── Trigger 3: Vassal loyalty warnings (Phase 8 Session 5) ──
        if (nation in getattr(world, 'vassals', {})
                and not _on_cooldown(nation, "vassal_loyalty")):
            vassal_state = world.vassals[nation]
            if vassal_state.get("lord") == player_nation:
                loyalty = vassal_state.get("loyalty", 100)
                if loyalty < 20:
                    observations.append({
                        "message": (
                            f"Sire, our vassal {nation} grows dangerously restless. "
                            f"Loyalty stands at {int(loyalty)}. "
                            f"{'Rebellion is imminent!' if loyalty < 10 else 'Urgent intervention may be required.'}"
                        ),
                        "trigger_type": "vassal_loyalty",
                        "target_nation": nation,
                        "priority": 1 if loyalty < 10 else 2,
                        "elaborate_type": "advisory",
                    })
                    _set_cooldown(nation, "vassal_loyalty", 3)
                elif loyalty < 35:
                    # C1 (playtest): grip-aware advisory — the old copy hard-coded
                    # the healthy-band levers (incl. the dead "garrison their
                    # capital"), contradicting the grip-aware per-event line in
                    # the same dispatch and steering the player to spend on a
                    # VS-R-blunted invest during a spiral. Single source.
                    from backend.models.authority import get_imperial_grip
                    from backend.game_logic.vassal import recovery_hint_for_grip
                    _grip = get_imperial_grip(world, player_nation)
                    observations.append({
                        "message": (
                            f"Sire, Talleyrand notes growing discontent in {nation}. "
                            f"Loyalty stands at {int(loyalty)}. "
                            f"{recovery_hint_for_grip(_grip)}"
                        ),
                        "trigger_type": "vassal_loyalty",
                        "target_nation": nation,
                        "priority": 4,
                        "elaborate_type": "advisory",
                    })
                    _set_cooldown(nation, "vassal_loyalty", 3)

        # ── Trigger 4: Relation threshold CROSSED ──
        thresholds = [-40, -20, 0, 20, 40]
        if not _on_cooldown(nation, "relation_threshold"):
            previous = world.previous_nation_relations.get(diplo_key, relation)
            for threshold in thresholds:
                crossed_up = previous < threshold <= relation
                crossed_down = previous >= threshold > relation
                if crossed_up or crossed_down:
                    direction_word = "improved" if crossed_up else "deteriorated"
                    observations.append({
                        "message": (
                            f"Relations with {nation} have {direction_word} "
                            f"past {threshold} to {int(relation)}. "
                            f"{'This opens new diplomatic possibilities.' if crossed_up else 'Caution may be warranted.'}"
                        ),
                        "trigger_type": "relation_threshold",
                        "target_nation": nation,
                        "priority": 3,
                        "elaborate_type": "advisory" if crossed_down else "proposal_options",
                    })
                    _set_cooldown(nation, "relation_threshold", 5)
                    break  # One threshold per nation per dispatch

    # ── Trigger 5: No diplomatic action for 3+ turns ──
    if len(observations) < 2 and not _on_cooldown("global", "idle_nudge"):
        mission = getattr(world, 'active_diplomatic_mission', None)
        transit = getattr(world, 'proposal_in_transit', None)
        talleyrand_state = getattr(world, 'talleyrand_state', 'IDLE')

        if talleyrand_state == "IDLE" and not mission and not transit:
            # Check if player has taken any diplomatic action recently
            # (Simple heuristic: Talleyrand is idle = no recent action)
            if world.current_turn >= 4:  # Don't nag on early turns
                observations.append({
                    "message": (
                        "Sire, the diplomatic front has been quiet. Perhaps too quiet. "
                        "Shall I assess our options?"
                    ),
                    "trigger_type": "idle_nudge",
                    "target_nation": "",
                    "priority": 5,
                    "elaborate_type": "proposal_options",
                })
                _set_cooldown("global", "idle_nudge", 5)

    # Sort by priority (lower = more important), cap at 2
    observations.sort(key=lambda o: o.get("priority", 99))
    result = observations[:2]

    # Store cooldowns back
    world.proactive_suggestion_cooldowns = cooldowns

    return result


# ============================================================================
# SESSION 6: Talleyrand Defiance Discovery + Override Notes + Redemption
# ============================================================================

def _check_talleyrand_session6(dispatch: Dict, world, player_nation: str) -> None:
    """Check for Talleyrand sabotage discovery, override notes, and redemption.

    Modifies dispatch dict in place. Sets fields:
    - talleyrand_discovery: confrontation dialogue dict if discovery fires
    - talleyrand_override_note: string if recent override outcome

    Args:
        dispatch: The dispatch dict being built
        world: WorldState
        player_nation: The active player nation
    """
    diplomats = getattr(world, 'diplomats', {})
    talleyrand = diplomats.get(player_nation)
    if not talleyrand:
        return

    # ── 1. Sabotage Discovery Check ──
    sabotage = getattr(world, 'pending_talleyrand_sabotage', None)
    if sabotage and not sabotage.get("discovered"):
        from backend.commands.diplomatic_defiance import (
            check_sabotage_discovery, build_confrontation_dialogue,
        )
        if check_sabotage_discovery(sabotage, world):
            sabotage["discovered"] = True
            world.pending_talleyrand_sabotage = sabotage

            # Build confrontation dialogue and set it as pending
            confrontation = build_confrontation_dialogue(sabotage, talleyrand)
            confrontation["turn_created"] = int(world.current_turn)
            dispatch["talleyrand_discovery"] = confrontation

            # Also set on world for the dialogue system to pick up
            world.dialogue_manager.push(confrontation)

            # Notification: sabotage discovered (Session 8C)
            from backend.notifications import (
                create_notification, NotificationPriority, SABOTAGE_DISCOVERED,
            )
            target = sabotage.get("target_nation", "unknown")
            defiance_type = sabotage.get("defiance_type", "unknown")
            # BUGFIX: Translate raw defiance_type keys to human-readable strings.
            # Raw keys like "ap_downgrade" and "stalled" must not reach the player.
            # See BUGFIX_PLAN_PROPOSAL_FLOW.md.
            _DEFIANCE_TYPE_DISPLAY = {
                "stalled": "Delayed Delivery",
                "ap_downgrade": "Reduced Concessions",
                "unit_overpay": "Inflated Demands",
                "softened": "Softened Terms",
                "hardened": "Hardened Terms",
                "unknown": "Modified Terms",
            }
            display_type = _DEFIANCE_TYPE_DISPLAY.get(defiance_type, "Modified Terms")
            world.notifications.add(create_notification(
                SABOTAGE_DISCOVERED,
                NotificationPriority.HIGH,
                "Sabotage Discovered!",
                f"Talleyrand altered your proposal to {target} ({display_type}).",
                int(world.current_turn),
            ))

            # Set popup data for Godot (Session 8C)
            original = sabotage.get("original_proposal", {})
            modified = sabotage.get("modified_proposal", {})
            # FA-N5: the discovery popup is answered through the
            # `sabotage_confrontation` dialogue pushed a few lines above, but
            # it never carried that dialogue's identity, so the client
            # answered with a bare verb and the W6-0 stale-dialogue guard had
            # nothing to bind. `confront_sabotage` / `overlook_sabotage`
            # happen to resolve onto no other dialogue's options today — the
            # binding is what keeps that true when a future option label
            # contains one of those words.
            world.diplomatic_sabotage_popup = {
                "dialogue_id": confrontation.get("dialogue_id"),
                "target_nation": target,
                "defiance_type": defiance_type,
                "ordered_summary": sabotage.get("original_summary", str(original)),
                "delivered_summary": sabotage.get("modified_summary", str(modified)),
                "authority_bonus_if_confronted": int(5),
                "authority_penalty_if_overlooked": int(3),
            }

            # Dispatch event (Session 8D) — use translated display_type
            queue_dispatch_event(world, "diplomatic_sabotage_discovered",
                                {"nation": target, "change_description": display_type},
                                "always")

            # Campaign log entry
            world.log_event({
                "type": "diplomatic_discrepancy",
                "message": f"Talleyrand altered your proposal to {target}.",
                "turn": int(world.current_turn),
                "nation": player_nation,
            })

    # ── 2. Override History Note ──
    from backend.commands.diplomatic_defiance import get_override_dispatch_note
    override_note = get_override_dispatch_note(world)
    if override_note:
        dispatch["talleyrand_override_note"] = override_note

    # ── 3. Redemption Event — REMOVED (PL-23: trust system deleted) ──


def _build_war_objective_section(world, player_nation: str) -> List[Dict]:
    """WPS-A: Build war objective status lines for the Morning Dispatch."""
    from backend.game_logic.diplomacy import (
        OBJECTIVE_TYPE_DISPLAY, SETTLEMENT_TIER_DISPLAY,
        TICKING_RATES, get_settlement_tier, get_war_score_for,
    )

    lines = []
    war_objectives = getattr(world, 'war_objectives', {})

    for diplo_key, nation_objs in war_objectives.items():
        player_obj = nation_objs.get(player_nation)
        if not player_obj or player_obj.get("concluded_turn") is not None:
            continue

        obj_type = player_obj.get("type", "")
        target_nation = player_obj.get("target_nation", "Unknown")
        target_regions = player_obj.get("target_regions", [])
        accumulated = int(player_obj.get("accumulated_ticking", 0))
        rate = int(TICKING_RATES.get(obj_type, 0))
        type_display = OBJECTIVE_TYPE_DISPLAY.get(obj_type, obj_type)

        held_regions = []
        for rname in target_regions:
            if rname in world.regions:
                if world.regions[rname].controller == player_nation:
                    held_regions.append(rname)

        region_str = ", ".join(target_regions) if target_regions else "unknown"
        held_str = "HELD" if held_regions else "not held"
        tick_str = f"+{rate}/turn" if rate > 0 else ""

        line_text = f"War Purpose: {type_display} vs {target_nation} — {region_str} [{held_str}]"
        if accumulated > 0:
            line_text += f" (ticking: +{accumulated}{', ' + tick_str if tick_str else ''})"

        score = int(get_war_score_for(world, player_nation, target_nation))
        tier = get_settlement_tier(score)
        tier_display = SETTLEMENT_TIER_DISPLAY.get(tier, tier)
        line_text += f"  |  Settlement: {tier_display} ({score:+d})"

        lines.append({
            "text": line_text,
            "target_nation": target_nation,
            "objective_type": obj_type,
        })

    return lines


def _build_peace_settlement_section(world) -> List[Dict]:
    """BPH-D §11.3: Build peace settlement summaries for the Morning Dispatch.

    Returns entries from the ratification log that were signed the previous turn.
    """
    previous_turn = int(world.current_turn) - 1
    settlements = []
    for entry in getattr(world, 'peace_ratification_log', []):
        if int(entry.get("turn", 0)) != previous_turn:
            continue
        if entry.get("new_state", "PEACE") != "PEACE":
            continue
        dur = entry.get("war_duration_turns", 0)
        target = entry.get("target_nation", "Unknown")
        target_capital = entry.get("target_capital") or world.get_nation_capital(target) or target
        outcome = entry.get("war_outcome", "")
        gained = entry.get("territory_gained", [])
        score = entry.get("final_war_score", 0)

        headline = f"The Treaty of {target_capital}"
        if entry.get("previous_state") == "ARMISTICE":
            detail_parts = [
                f"{world.player_nation} and {target} have converted the armistice into peace",
            ]
        else:
            detail_parts = [
                f"{world.player_nation} and {target} have concluded peace"
                f" after {dur} turn{'s' if dur != 1 else ''} of war",
            ]
        if gained:
            detail_parts.append(f"{world.player_nation} gained {', '.join(gained)}")
        detail_parts.append(f"Final war score: {'+' if score > 0 else ''}{score}")

        # WPS-D §14.5: Surface forced alliance and liberation in dispatch
        terms_ratified = entry.get("terms_ratified", [])
        for term_label in terms_ratified:
            term_lower = term_label.lower()
            if "forced alliance" in term_lower or "enters alliance" in term_lower:
                detail_parts.append(f"{target} enters forced alliance with {world.player_nation}")
            elif "liberated" in term_lower:
                detail_parts.append(term_label)

        settlements.append({
            "headline": headline,
            "detail": ". ".join(detail_parts) + ".",
            "war_outcome": outcome,
            "target_nation": target,
        })
    return settlements


def _build_coalition_section(world, player_nation: str) -> Optional[Dict]:
    """Build coalition status section for Morning Dispatch (COALITION_SPEC §9c).

    Returns None if threat < 30 (nothing to show).
    """
    from backend.game_logic.coalition import (
        get_threat_tier, get_qualifying_nations, is_coalition_active,
        THREAT_TENSION_MIN,
    )

    threat = int(world.threat_level)
    if threat < THREAT_TENSION_MIN:
        return None

    _player = getattr(world, "player_nation", "France")
    # CA8-18: a coalition that has FORMED against France is not "Brewing".
    # Scoped to France's own coalition, exactly like the two sections below
    # — an eclipse coalition aimed at another power must not relabel this.
    _formed = bool(
        is_coalition_active(world)
        and (world.active_coalition.get("target_nation") or _player) == _player)
    tier = get_threat_tier(threat, coalition_formed=_formed)
    section = {
        "threat_level": threat,
        "tier": tier,
        # Stage D review fix [r1]: this is FRANCE's alarm breakdown —
        # producers now log every actor's deeds, so filter to
        # player-targeted entries (legacy target-less entries included).
        "sources": [
            s.copy() for s in world.threat_sources_this_turn
            if not isinstance(s, dict) or s.get("target", _player) == _player
        ],
    }

    # Brewing status — player-targeted brewing only (an eclipse brewing
    # against another power is not France's coalition section).
    if world.coalition_brewing:
        brewing = world.coalition_brewing
        if (brewing.get("target_nation") or _player) == _player:
            section["brewing"] = {
                "qualifying_nations": brewing.get("qualifying_nations", []),
                "turns_remaining": int(brewing.get("turns_remaining", 0)),
            }

    # Active coalition details — France's own coalition only (an eclipse
    # coalition against another power surfaces via its own dispatch lines).
    if is_coalition_active(world) and (
            (world.active_coalition.get("target_nation") or _player) == _player):
        from backend.game_logic.diplomatic_ledger import _get_nation_visibility, _format_army_strength
        coalition = world.active_coalition
        members_info = []
        for member in coalition.get("members", []):
            member_strength = sum(
                m.strength for m in world.marshals.values()
                if m.nation == member and m.strength > 0
            )
            vis = _get_nation_visibility(member, world)
            strength_display = _format_army_strength(member_strength, vis)
            partial_vis = vis in (FULL, PARTIAL)
            members_info.append({
                "nation": member,
                "war_exhaustion": int(world.war_exhaustion.get(member, 0)) if partial_vis else 0,
                "strength_display": strength_display,
                "strength": int(member_strength) if vis == FULL else 0,
                "gold": int(world.nation_gold.get(member, 0)) if vis == FULL else 0,
            })

        section["active_coalition"] = {
            "name": coalition.get("name", ""),
            "leader": coalition.get("leader", ""),
            "posture": coalition.get("strategic_posture", "defensive"),
            "formed_turn": int(coalition.get("formed_turn", 0)),
            "members": members_info,
        }

    # Qualifying nations (if not brewing/active, show who would join)
    if not world.coalition_brewing and not is_coalition_active(world):
        qualifying = get_qualifying_nations(world)
        if qualifying:
            section["qualifying_nations"] = qualifying

    return section


# ============================================================================
# SESSION 8D: DIPLOMATIC EVENTS DISPATCH SECTION
# ============================================================================

# Event text templates — keyed by event type
_DIPLOMATIC_EVENT_TEMPLATES = {
    "diplomatic_proposal_sent": "Talleyrand has departed for the {nation} court.",
    "diplomatic_proposal_returned": "Talleyrand returns from {nation} with a response.",
    "diplomatic_sabotage_discovered": "Talleyrand altered your proposal to {nation}. He {change_description}.",
    "diplomatic_treaty_signed": "{nation_a} and {nation_b} have signed the {treaty_type}.",
    "diplomatic_treaty_broken": "{nation} has broken the {treaty_type}.",
    "diplomatic_war_declared": "{nation} has declared war on {target}.",
    # FA-65: and what to DO about it — rendered by the per-type arm in
    # `_format_dispatch_event_text`, because the hint is optional and a
    # `.format()` with an unsupplied key emits the raw template.
    "diplomatic_vassal_unrest": "Talleyrand reports unrest in {nation}.",
    "diplomatic_vassal_rebellion_imminent": "{nation} is on the verge of rebellion!",
    "diplomatic_vassal_rebellion": "{nation} has rebelled against {lord}. It is war.",
    # FA-2 (slice 11): a satellite stops being one three ways, and the player
    # was told the same thing about all of them — that it had ceased to
    # exist. These are the other two exits, and on the shipped 1805 board the
    # PEACE one is the exit both big satellites actually take.
    "diplomatic_vassal_broke_free_armistice": "{nation} breaks free of {lord}, but the armistice holds — no war is declared.",
    "diplomatic_vassal_broke_free_peace": "{nation} breaks free of {lord} and stands alone — an independent power, and no war declared.",
    "diplomatic_vassal_refuses_call": "{vassal} refuses {lord}'s call to arms against {enemy} — loyalty {loyalty}.",
    "diplomatic_vassal_transferred": "{vassal} passes from {from_lord}'s suzerainty to {to_lord}'s.",
    "diplomatic_vassal_defected": "THE DEFECTION: {briber}'s gold turns {vassal} against {lord}.",
    "diplomatic_ai_proposal": "A {nation} envoy has arrived with a proposal.",
    "diplomatic_mission_progress": "Talleyrand's efforts in {nation} continue. Relations now at {value}.",
    "diplomatic_mission_completed": "Talleyrand has completed his mission in {nation}.",
    "diplomatic_mission_paused": "Talleyrand's diplomatic efforts curtailed — insufficient resources.",
    "diplomatic_mission_cancelled": "Talleyrand's efforts in {nation} have collapsed.",
    "diplomatic_feasibility_report": "Talleyrand assesses: {difficulty_tier}. {hint}",
    "diplomatic_alliance_cascade": "{nation} enters the war via alliance with {ally}.",
    "diplomatic_offensive_cascade": "{nation} has joined {aggressor}'s war against {target}, honoring their alliance.",
    "diplomatic_vassal_courting": "Talleyrand reports {enemy} agents in {vassal_capital}.",
    "diplomatic_continental_system": "{nation} has {action} the Continental System.",
    # Audit 2026-07-09 fix 3.1: name the actual lord — this event also fires
    # for AI-lord vassalizations (treaty ratification / settlement clauses),
    # where "French protection" misattributed the act.
    # PC-9: the article is resolved per-name in _render_diplomatic_event, not
    # hardcoded here — a carved client may be an institution ("the Duchy of
    # Warsaw") or a bare state ("Switzerland"), and the same sentence serves
    # both. Live: "The Switzerland has ceased to exist."
    "diplomatic_carved_vassal_created": "{carved_name} has been established under the protection of {protector}.",
    "diplomatic_carved_vassal_dissolved": "{carved_name} has ceased to exist.",
    "diplomatic_defection_cascade": "The empire trembles — multiple vassals are wavering!",
    "diplomatic_ai_ai_treaty": "Talleyrand reports: {nation_a} and {nation_b} have signed the {treaty_type}.",
    "diplomatic_treaty_payment_failed": "{from_nation} cannot meet treaty obligations to {to_nation} ({amount_paid}/{amount_due} gold paid).",
    "diplomatic_auto_downgrade": "Relations between {nation_a} and {nation_b} have collapsed: {from_state} → {to_state}.",
    "diplomatic_coalition_formed": "A coalition has formed against France! Members: {member_list}.",
    "diplomatic_coalition_dissolved": "The coalition against France has dissolved.",
    "diplomatic_coalition_brewing": "Talleyrand warns: a coalition may be forming against France.",
    # §4.4b (Stage D review fix [r6]): the eclipse variants — a coalition
    # against ANOTHER power must never wear the anti-France copy.
    "diplomatic_coalition_formed_other": "A coalition has formed against {target}. Members: {member_list}.",
    "diplomatic_coalition_dissolved_other": "The coalition against {target} has dissolved.",
    "diplomatic_coalition_brewing_other": "Word from the chanceries: a coalition is brewing against {target}.",
    # Marshal recruitment (Jealousy v3.2 build): word of an enemy commission
    # reaches the player only with intel on that court (partial_on_nation).
    "enemy_marshal_commissioned": "Intelligence reports {nation} has raised {marshal} to high command.",
    "balance_of_europe_shifted": "The balance of Europe shifts around {label}.",
    # Nation Agendas NA-1: the once-per-shift court-intent beat (values
    # arrive fully humanized — display nation + agenda title; the colon
    # shape survives verb-phrase titles like "Redeem Italy").
    "agenda_shift": "The court of {nation} takes up a new design: {focus}.",
    # Nation Agendas NA-3 §5.9 — the Ansbach trap (values arrive humanized).
    "agenda_violation": (
        "{guard_holder} seethes: {violator}'s columns cross {region} "
        "in defiance of its declared neutrality."
    ),
    # AI-2b beat 4 (AI_INTENT_SPEC §4.6a) — The Broken Bargain.
    "broken_bargain": (
        "The compact with {nation} lies torn — {breaker} is named the "
        "breaker in every chancery of Europe."
    ),
    # AI-2d §12.6 — the allegiance auction's Courier beat.
    "allegiance_in_play": (
        "The allegiance of {nation} is in play — every court with gold "
        "or standing now bids for the flip."
    ),
    # AI-2e §3.7 — the paymaster's gold, made visible.
    "paymaster_subsidy": (
        "{payer}'s gold reaches {nation} — the subsidy stands at "
        "{amount} this season."
    ),
    # AI-3 Stage D beats (AI_INTENT_SPEC §4.6a). Beat 2, The Brewing
    # Crisis: the fore-warning, instruments listed and honestly gated.
    "crisis_brewing": (
        "THE BREWING CRISIS: {nation} will move on {target}. "
        "You may {instruments}."
    ),
    # Beat 3's AI-AI arm — the coercive demand, the last rung before war.
    "coercive_demand": (
        "{nation} delivers a final demand to {target} — it is refused. "
        "The ladder has one rung left."
    ),
    # Beat 7, The Crisis Passes (pin 21): the stand-down, cause named,
    # instrument credited. Ochakov 1791; the Prussian mobilisation
    # dissolving after Austerlitz.
    "crisis_passed": (
        "{nation} stands down over {target}, Sire — {cause}."
    ),
    # D5-3's enforcement made personal: the ward pleads for the pledge.
    "guarantee_called": (
        "{ward} pleads for your guarantee, Sire — {aggressor} has "
        "declared war. Honour it in the field, or the abandonment "
        "will be remembered."
    ),
    # AI-4b beat 6, The Congress: a third-party war ends without France,
    # consequences named (who gained, what it means for us).
    "third_party_peace": (
        "THE CONGRESS: {proposer} and {accepter} have made their peace "
        "without France. {consequence}"
    ),
    # AI-5b(i) (§3.6) — the world writes content the author did not:
    # a humiliated court promotes its grievance into a real design.
    "design_promoted": (
        "REVANCHE: {nation} will not forgive {author} the loss of "
        "{province_line}. A new design hardens in their court."
    ),
    # AI-6 (§4.6, Stage F) — routine ladder movement, capped at
    # INTENT_DISPATCH_CAP lines per dispatch (weight x relevance), the
    # rest collapsed into the single tail line. Beats are events on
    # their own types and never pass through the cap.
    "intent_hardens": (
        "The court of {nation} hardens over {want} — prepared now to go "
        "as far as {price}."
    ),
    "intent_eases": (
        "The court of {nation} eases over {want} — {price} is now the "
        "length of its tether."
    ),
    "intent_movement_tail": (
        "And {count} other court{plural} stir{verb} at {poss} own "
        "design{plural}."
    ),
    # AI-5b(ii) beat 5 (§4.6a) — The Volte-Face: the beaten great power,
    # courted rather than humiliated, reverses in one signing. Tilsit.
    "volte_face": (
        "THE VOLTE-FACE: {nation}, beaten and then courted, takes "
        "{partner}'s hand. {gaze}"
    ),
    # DEF-5 naval (NAVAL_SPEC §9 dispatch beats — state-change only,
    # never per-turn repetition; the two strait beats carry a prebuilt
    # {line} because two emitters share the type).
    "blockade_begins": (
        "BLOCKADE: {blockader} closes {nation}'s ports. Trade is halved "
        "and the fleet is pinned at anchor, where crews rot."
    ),
    "blockade_broken": (
        "The blockade of {nation} is broken — her ports breathe, her "
        "crews may drill again."
    ),
    "boulogne_camp": (
        "THE CAMP: {nation} has massed {strength} men on the invasion "
        "coast. {against} has seen it — expect the fleet home to guard "
        "the water."
    ),
    "strait_open": "THE STRAIT: {line}.",
    "strait_shut": "THE STRAIT: {line}.",
    "cs_tier_shift": (
        "THE CONTINENTAL SYSTEM {direction}: {closure_pct}% of the "
        "Continent's ports are closed to {target}."
    ),
    "trafalgar": (
        "TRAFALGAR: {winner_admiral}'s line has shattered the {loser} "
        "fleet — {loser_ships_lost} sail lost in a decisive action. "
        "{winner} commands the sea."
    ),
    "fleet_action": (
        "ACTION AT SEA: {winner}'s squadrons under {winner_admiral} get "
        "the better of {loser} — {loser_ships_lost} sail lost."
    ),
    "expedition_landed": (
        "THE LANDING: {marshal} has put {troops} men ashore at {target}."
    ),
    "expedition_intercepted": (
        "INTERCEPTED AT SEA: {coverer}'s patrols caught {marshal}'s "
        "transports off {target} — {troops_lost} men lost to the guns "
        "and the water."
    ),
    # Nation Agendas NA-6 §11.8 stage 1 — the dispatch LEADS with a
    # proclamation (values arrive humanized: both display names).
    "nation_formed": (
        "By the will of the nation and the fortune of arms — "
        "{old_nation} is no more. {nation} stands."
    ),
    # NA-6c §11.4 — a CREATION, not a transformation. Nothing died to make
    # this nation, so it gets its own line rather than the formation
    # template with an empty `{old_nation}` ("— is no more.").
    "nation_created": (
        "By the fortune of arms and the pen at the table — "
        "{nation} is erected upon the map, a client of {sponsor}."
    ),
    "diplomatic_dp_regen": "Talleyrand reports: {dp} diplomatic points available ({breakdown}).",
    # NP-5 §8: once per war, the first dispatch after the Emperor rides out.
    "sovereign_takes_field": "The Emperor has taken the field — Talleyrand holds the portfolio at the capital.",
    "diplomatic_we_threshold": "War exhaustion grows — {nation} nears breaking point (exhaustion: {we}).",
    "diplomatic_relation_shift": "Relations with {nation} have {direction} significantly ({delta} this turn).",
    "diplomatic_armistice_expired_peace": "The armistice between {nation_a} and {nation_b} has concluded. Peace declared.",
    "diplomatic_armistice_expired_war": "The armistice between {nation_a} and {nation_b} has collapsed. War resumes!",
    "hard_reject_posture_triggered": "{victim_nation} has closed the chancery to {perpetrator_nation}.",
    "hard_reject_posture_cleared": "{victim_nation} has reopened deeper diplomacy with {perpetrator_nation}.",
    # Memory and Pressure v2.4.3 — Make Amends. Commitments routing owns the
    # final notice copy; this template is the dispatch fallback.
    "amends_offered": "{actor_nation} has offered amends to {target_nation}.",
    # DG-4 §8.8 — defender-side refusal of a legal, non-impossible call.
    # Commitments routing owns the rail copy; this template is the dispatch
    # fallback.
    "call_to_arms_refused_defensive": (
        "{breaker} has refused the defensive call from {victim}."
    ),
    "call_to_arms_refused_offensive": (
        "{breaker} has refused the offensive call from {victim}."
    ),
    "call_to_arms_honored_costly": (
        "{honorer} has honored a costly defensive call from {victim}."
    ),
    "oathbreaker_posture_triggered": (
        "{nation} is marked as an oathbreaker after repeated refusals."
    ),
    "oathbreaker_posture_cleared": (
        "{nation}'s oathbreaker posture has cleared."
    ),
    "commitment_paradox_resolved": (
        "In a crisis of commitments, {player_nation} chose {chosen_nation} over {spurned_nation}."
    ),
    "nation_eliminated": "{nation} has been eliminated from the war.",
    # Peace Deals BPH-A + BPH-D
    "peace_ratified": "Peace ratified between {proposer_nation} and {target_nation}.",
    # WB-B — war bargain lifecycle
    "bargain_ratified": "{promiser} and {beneficiary} ratified a bargain against {target_enemy}: French priority claim on {claim_region}.",
    "bargain_triggered": "{beneficiary} joins against {target_enemy}; the bargain over {claim_region} is now active.",
    "bargain_fulfilled": "{promiser} honored the bargain: {claim_region} secured.",
    "bargain_breached": "{fault_nation} broke the bargain with {beneficiary} over {claim_region}.",
    "bargain_voided": "Bargain with {beneficiary} over {claim_region} lapsed ({end_reason}).",
    "bargain_dormant_notice": "Bargain with {beneficiary} over {claim_region} has been idle for {turns_active} turns.",
    # SC-33 / G2-Slice-9 - recurring settlement gold payment events.
    "settlement_recurring_gold_paid": (
        "{from_nation} paid {amount_paid} gold to {to_nation} on the "
        "settlement of {war_label} ({turns_remaining} turns remaining)."
    ),
    "settlement_recurring_gold_partial": (
        "{from_nation} could only pay {amount_paid}/{amount_due} gold to "
        "{to_nation} on the settlement of {war_label}."
    ),
    "settlement_recurring_gold_completed": (
        "The settlement obligation of {total_amount} gold from "
        "{from_nation} to {to_nation} (for {war_label}) is fulfilled."
    ),
    "settlement_recurring_gold_cancelled": (
        "The recurring settlement payment from {from_nation} to "
        "{to_nation} (for {war_label}) has been cancelled ({reason})."
    ),
}

# Priority mapping: LOW for progress/sent/feasibility; MEDIUM for treaty/system; HIGH for rest
_DIPLOMATIC_EVENT_PRIORITY = {
    "enemy_marshal_commissioned": "MEDIUM",
    "agenda_shift": "MEDIUM",
    "agenda_violation": "HIGH",
    "nation_formed": "HIGH",
    "nation_created": "HIGH",
    # AI-2b/2d/2e (Stage C): the broken bargain is the phase's marquee
    # grievance beat and the flip announcement is the auction's Courier
    # moment — both HIGH like their treaty-broken siblings; the routine
    # subsidy line stays MEDIUM by design.
    "broken_bargain": "HIGH",
    "allegiance_in_play": "HIGH",
    "paymaster_subsidy": "MEDIUM",
    # AI-3/AI-4b (Stage D): beats are EVENTS, exempt from the routine
    # cap (§4.6's v1.2 amendment) — a beat is never collapsed into the
    # tail. The coercive demand is the one MEDIUM: the crisis lead
    # already owns the foreground that turn.
    "crisis_brewing": "HIGH",
    "coercive_demand": "MEDIUM",
    "crisis_passed": "HIGH",
    "guarantee_called": "HIGH",
    "third_party_peace": "HIGH",
    # AI-5b (Stage E): both are beats — a sworn revanche and a great
    # power changing sides are events, never routine ladder lines.
    "design_promoted": "HIGH",
    "volte_face": "HIGH",
    # DEF-5 naval beats: the campaign-defining moments ride HIGH, the
    # economic tides MEDIUM.
    "trafalgar": "HIGH",
    "strait_open": "HIGH",
    "strait_shut": "HIGH",
    "boulogne_camp": "HIGH",
    "expedition_landed": "HIGH",
    "expedition_intercepted": "HIGH",
    "fleet_action": "MEDIUM",
    "blockade_begins": "MEDIUM",
    "blockade_broken": "MEDIUM",
    "cs_tier_shift": "MEDIUM",
    # AI-6 (Stage F): the ROUTINE lines the cap governs — deliberately
    # below every beat, and the tail below the lines it summarises.
    "intent_hardens": "MEDIUM",
    "intent_eases": "LOW",
    "intent_movement_tail": "LOW",
    # Eclipse-coalition variants: Europe's business, not France's crisis.
    "diplomatic_coalition_formed_other": "MEDIUM",
    "diplomatic_coalition_dissolved_other": "MEDIUM",
    "diplomatic_coalition_brewing_other": "MEDIUM",
    "diplomatic_proposal_sent": "LOW",
    "diplomatic_proposal_returned": "HIGH",
    "diplomatic_sabotage_discovered": "HIGH",
    "diplomatic_treaty_signed": "MEDIUM",
    "diplomatic_treaty_broken": "HIGH",
    "diplomatic_war_declared": "HIGH",
    "diplomatic_vassal_unrest": "MEDIUM",
    "diplomatic_vassal_rebellion_imminent": "HIGH",
    "diplomatic_vassal_rebellion": "HIGH",
    "diplomatic_vassal_broke_free_armistice": "HIGH",
    "diplomatic_vassal_broke_free_peace": "HIGH",
    "diplomatic_vassal_refuses_call": "HIGH",
    "diplomatic_vassal_transferred": "HIGH",
    "diplomatic_vassal_defected": "HIGH",
    "diplomatic_ai_proposal": "HIGH",
    "diplomatic_mission_progress": "LOW",
    "diplomatic_mission_completed": "MEDIUM",
    "diplomatic_mission_paused": "MEDIUM",
    "diplomatic_mission_cancelled": "HIGH",
    "diplomatic_feasibility_report": "LOW",
    "diplomatic_alliance_cascade": "HIGH",
    "diplomatic_offensive_cascade": "HIGH",
    "diplomatic_vassal_courting": "MEDIUM",
    "diplomatic_continental_system": "MEDIUM",
    "diplomatic_carved_vassal_created": "MEDIUM",
    "diplomatic_carved_vassal_dissolved": "HIGH",
    "diplomatic_defection_cascade": "HIGH",
    "diplomatic_ai_ai_treaty": "MEDIUM",
    "diplomatic_treaty_payment_failed": "MEDIUM",
    "settlement_recurring_gold_paid": "LOW",
    "settlement_recurring_gold_partial": "MEDIUM",
    "settlement_recurring_gold_completed": "MEDIUM",
    "settlement_recurring_gold_cancelled": "MEDIUM",
    "diplomatic_auto_downgrade": "MEDIUM",
    "diplomatic_coalition_formed": "HIGH",
    "diplomatic_coalition_dissolved": "MEDIUM",
    "diplomatic_coalition_brewing": "MEDIUM",
    "balance_of_europe_shifted": "NORMAL",
    "diplomatic_dp_regen": "LOW",
    "sovereign_takes_field": "MEDIUM",
    "diplomatic_we_threshold": "MEDIUM",
    "diplomatic_relation_shift": "MEDIUM",
    "diplomatic_armistice_expired_peace": "HIGH",
    "diplomatic_armistice_expired_war": "HIGH",
    "hard_reject_posture_triggered": "HIGH",
    "hard_reject_posture_cleared": "MEDIUM",
    # Make Amends — NORMAL/MEDIUM per COMMITMENTS_PRESENTATION_SPEC §10.3.
    "amends_offered": "MEDIUM",
    # DG-4 refusal notices are CRITICAL per spec §8.8.10.
    "call_to_arms_refused_defensive": "CRITICAL",
    "call_to_arms_refused_offensive": "CRITICAL",
    "call_to_arms_honored_costly": "CRITICAL",
    "oathbreaker_posture_triggered": "HIGH",
    "oathbreaker_posture_cleared": "MEDIUM",
    "commitment_paradox_resolved": "MEDIUM",
    "nation_eliminated": "HIGH",
    "peace_ratified": "HIGH",
    # WB-B — war bargain lifecycle
    "bargain_ratified": "MEDIUM",
    "bargain_triggered": "HIGH",
    "bargain_fulfilled": "HIGH",
    "bargain_breached": "HIGH",
    "bargain_voided": "MEDIUM",
    "bargain_dormant_notice": "LOW",
}


def queue_dispatch_event(world, event_type: str, template_vars: dict, fog_rule: str) -> None:
    """Append a diplomatic event to the pending dispatch queue.

    Called by backend systems as events fire. The Morning Dispatch builder
    consumes and fog-filters these events when building the dispatch.

    Args:
        world: WorldState instance
        event_type: One of the _DIPLOMATIC_EVENT_TEMPLATES keys
        template_vars: Dict of template variable values (e.g. {"nation": "Prussia"})
        fog_rule: "always" | "partial_on_nation" | "player_vassal" |
                  "player_mission" | "detection_60pct"
    """
    world.pending_dispatch_events.append({
        "type": event_type,
        "template_vars": template_vars,
        "fog_rule": fog_rule,
        # PT-E1: the turn this was queued on, so `_advance_turn_internal`
        # can prune last cycle's leftovers instead of wiping the queue
        # mid-cycle and destroying the events it is about to report.
        "queued_turn": int(getattr(world, "current_turn", 0)),
    })


def _is_dispatch_event_visible(event: dict, world, player_nation: str) -> bool:
    """Apply fog rules to determine if a diplomatic dispatch event is visible.

    Fog rules (from DIPLOMACY_SPEC §11):
    - "always": Always shown to player
    - "partial_on_nation": Visible if PARTIAL+ on any relevant nation
    - "player_vassal": Visible if nation is player's vassal
    - "player_mission": Visible if Talleyrand's mission targets that nation
    - "detection_60pct": Already resolved at queue time (always show if queued)
    """
    from backend.game_logic.diplomatic_ledger import _get_nation_visibility

    # Settlement events (spec §11.6 line 1287) own their own fog rule
    # and never carry the legacy `template_vars` / `fog_rule` shape.
    event_type = event.get("type", "")
    if is_settlement_event_type(event_type):
        return is_settlement_event_visible(event, world, player_nation)

    fog_rule = event.get("fog_rule", "always")
    template_vars = event.get("template_vars", {})

    if fog_rule == "always":
        return True

    if fog_rule == "detection_60pct":
        # Already passed the roll at queue time
        return True

    if fog_rule == "partial_on_nation":
        # Check PARTIAL+ on any nation mentioned in template_vars.
        # `actor_nation` / `target_nation` keys added for B-B7 `amends_offered`
        # and any future events that prefer the explicit semantic names.
        # `breaker` / `victim` keys added for B-B4
        # `call_to_arms_refused_defensive`.
        nations_to_check = []
        for key in ("nation", "nation_a", "nation_b", "target", "aggressor", "ally", "enemy",
                   "vassal_capital", "witness_nation", "perpetrator_nation", "victim_nation",
                   "actor_nation", "target_nation", "breaker", "victim", "honorer"):
            val = template_vars.get(key)
            if val:
                nations_to_check.append(val)
        # Player nation events always visible
        for nation in nations_to_check:
            if nation == player_nation:
                return True
            vis = _get_nation_visibility(nation, world)
            if vis in (FULL, PARTIAL):
                return True
        return False

    if fog_rule == "player_vassal":
        nation = template_vars.get("nation", "")
        vassals = getattr(world, 'vassals', {})
        vassal_state = vassals.get(nation)
        if vassal_state and vassal_state.get("lord") == player_nation:
            return True
        return False

    if fog_rule == "player_mission":
        mission = getattr(world, 'active_diplomatic_mission', None)
        if mission:
            target = mission.get("target", "")
            if target == template_vars.get("nation", ""):
                return True
        return False

    # Unknown fog rule — default show
    return True


def _format_dispatch_event_text(event_type: str, template_vars: dict) -> str:
    """Format event text from template + variables."""
    if event_type in COMMITMENTS_ROUTES and event_type != "witness_strike_recorded":
        return format_commitments_notice(event_type, template_vars)

    if event_type == "settlement_summary":
        # Settlement events ship the full payload (no `template_vars`
        # wrapper). The dispatch consumer passes the event dict in via
        # `template_vars` so the existing call sites stay uniform.
        return compose_summary_oneliner(template_vars)
    if event_type == "settlement_digest":
        return compose_digest_oneliner(template_vars)

    # NOTE (verify fleet, Aug 2026 health check): as in campaign_log, every
    # COMMITMENTS_ROUTES type except witness_strike_recorded is formatted by
    # the early format_commitments_notice return above — the dead per-type
    # arms that sat below (diplomatic_treaty_broken, both
    # hard_reject_posture_* types) were removed; format_commitments_notice
    # owns their copy.

    if event_type == "diplomatic_vassal_unrest":
        # FA-65: the remedy rides this beat, and it is OPTIONAL — the event
        # is queued from one producer that supplies it, but an event built
        # anywhere else (or restored from a pre-fix save) must still render.
        # A `.format()` on a template with an unsupplied key silently emits
        # the RAW template, braces and all, which is how the first cut
        # shipped "Talleyrand reports unrest in {nation}."
        nation = template_vars.get("nation", "a satellite")
        hint = str(template_vars.get("recovery_hint") or "").strip()
        text = f"Talleyrand reports unrest in {nation}."
        return f"{text} {hint}" if hint else text

    if event_type == "diplomatic_war_declared":
        nation = template_vars.get("nation", "Unknown")
        target = template_vars.get("target", "Unknown")
        breached_treaty = template_vars.get("breached_treaty", "")
        defensive_joiners = int(template_vars.get("defensive_joiner_count", 0) or 0)
        offensive_joiners = int(template_vars.get("offensive_joiner_count", 0) or 0)
        extra_parts = []
        if breached_treaty:
            extra_parts.append(f"shattering the {breached_treaty}")
        total_joiners = defensive_joiners + offensive_joiners
        if total_joiners > 0:
            extra_parts.append(f"with {total_joiners} allied court{'s' if total_joiners != 1 else ''} poised to follow")
        if extra_parts:
            return f"{nation} has declared war on {target}, " + ", ".join(extra_parts) + "."
        return f"{nation} has declared war on {target}."

    if event_type == "witness_strike_recorded":
        witness = template_vars.get("witness_nation", "Unknown")
        perpetrator = template_vars.get("perpetrator_nation", "Unknown")
        victim = template_vars.get("victim_nation", "Unknown")
        scope_reason = template_vars.get("scope_reason", "")
        scope_phrase = {
            "ally": f"as an ally of {victim}",
            "rival": f"as a rival of {perpetrator}",
            "treaty_partner_of_breaker": f"as a treaty partner of {perpetrator}",
            "treaty_partner_of_honorer": f"as a treaty partner of {perpetrator}",
            "shared_enemy": "as a fellow belligerent",
            "region_observer": "from the sidelines",
        }.get(scope_reason, "")
        if scope_phrase:
            return f"{witness} has taken note of {perpetrator}'s breach against {victim} {scope_phrase}."
        return f"{witness} has taken note of {perpetrator}'s breach against {victim}."

    template = _DIPLOMATIC_EVENT_TEMPLATES.get(event_type, "")
    if not template:
        return f"Diplomatic event: {event_type}"
    if event_type in ("diplomatic_carved_vassal_created",
                      "diplomatic_carved_vassal_dissolved"):
        # PC-9: "the Duchy of Warsaw" but plain "Switzerland". Both sentences
        # are sentence-initial, so the article capitalizes. `carved_name` in
        # the event payload stays the RAW tag for any mechanical reader.
        from backend.display_names import display_nation, with_definite_article
        template_vars = dict(template_vars)
        template_vars["carved_name"] = with_definite_article(
            display_nation(template_vars.get("carved_name", "")),
            capitalize=True)
    try:
        return template.format(**template_vars)
    except (KeyError, IndexError):
        # Graceful fallback if template vars missing
        return template


def _build_relation_change_events(world, player_nation: str) -> list:
    """S2: Fire dispatch events for significant relation changes this turn."""
    deltas = getattr(world, '_relation_deltas_this_turn', {})
    events = []
    for nation, delta in deltas.items():
        if abs(delta) >= 10:
            direction = "improved" if delta > 0 else "worsened"
            events.append({
                "type": "diplomatic_relation_shift",
                "text": f"Relations with {nation} have {direction} significantly ({delta:+d} this turn).",
                "priority": "MEDIUM",
            })
    return events


def _build_diplomatic_events_section(world, player_nation: str) -> list:
    """Build the DIPLOMATIC EVENTS section from pending dispatch events.

    Pulls world.pending_dispatch_events, applies fog filter, formats text,
    returns list of {"type", "text", "priority"} dicts.
    """
    events = getattr(world, 'pending_dispatch_events', [])
    if not events:
        return []

    result = []
    witness_group_indexes = {}
    settlement_indexes: List[int] = []
    for event in events:
        if not _is_dispatch_event_visible(event, world, player_nation):
            continue

        event_type = event.get("type", "")
        # Settlement events carry the full payload directly (no
        # `template_vars` wrapper); the formatter accepts that shape.
        if is_settlement_event_type(event_type):
            text = _format_dispatch_event_text(event_type, event)
            priority = settlement_priority(event_type, event)
            entry = {
                "type": event_type,
                "text": text,
                "priority": priority,
                "event_family": "settlement",
                "war_id": str(event.get("war_id", "") or ""),
                "route_id": str(
                    (event.get("route") or {}).get("route_id", "") or ""
                ),
            }
            if event.get("awe_tags"):
                entry["awe_tags"] = list(event.get("awe_tags") or [])
            result.append(entry)
            settlement_indexes.append(len(result) - 1)
            continue

        template_vars = event.get("template_vars", {})
        if event_type == "witness_strike_recorded":
            episode_id = str(template_vars.get("episode_id", "") or "")
            key = episode_id or f"unkeyed_{len(result)}"
            witness = template_vars.get("witness_nation", "Unknown")
            if key not in witness_group_indexes:
                witness_group_indexes[key] = {
                    "index": len(result),
                    "vars": dict(template_vars),
                    "witnesses": [],
                }
                result.append({})
            group = witness_group_indexes[key]
            if witness not in group["witnesses"]:
                group["witnesses"].append(witness)
            result[group["index"]] = _format_witness_grouped_dispatch_event(group)
            continue

        text = _format_dispatch_event_text(event_type, template_vars)
        if event_type in COMMITMENTS_ROUTES:
            priority = commitments_priority(event_type, template_vars)
        else:
            priority = _DIPLOMATIC_EVENT_PRIORITY.get(event_type, "MEDIUM")

        result.append({
            "type": event_type,
            "text": text,
            "priority": priority,
        })

    # Spec §11.6 line 1279 — cap settlement-family dispatch lines at the
    # primary-beat threshold per ratification (`war_id:turn`). Overflow
    # rolls into a digest event so the rail does not blow up on
    # full-Europe ratifications. Only the primary `settlement_summary`
    # is capped; `settlement_digest` always renders because it IS the
    # overflow line.
    if settlement_indexes:
        result = _enforce_settlement_primary_beat_cap(result, settlement_indexes)
    return result


def _enforce_settlement_primary_beat_cap(
    rendered: List[Dict[str, Any]],
    settlement_indexes: List[int],
) -> List[Dict[str, Any]]:
    """Apply the spec §11.6 line 1279 top-four cap per ratification.

    Groups settlement summary lines by `war_id:turn`; keeps the first
    `SETTLEMENT_PRIMARY_BEAT_CAP` summaries per ratification and drops
    overflow. Digest lines are always preserved because they are the
    overflow signal.
    """
    if not settlement_indexes:
        return rendered
    keep_indexes: set = set(range(len(rendered)))
    summaries_per_ratification: Dict[str, List[int]] = {}
    for idx in settlement_indexes:
        entry = rendered[idx]
        if entry.get("type") != "settlement_summary":
            continue
        route_id = str(entry.get("route_id", "") or "")
        war_id = str(entry.get("war_id", "") or "")
        # Group on the route_id when present (carries `war_id:turn`),
        # else fall back to war_id.
        key = route_id or war_id or "unknown"
        # Strip the `settlement_summary:` prefix so summaries and any
        # future spotlight events from the same ratification land in the
        # same bucket.
        if key.startswith("settlement_summary:"):
            key = key.split("settlement_summary:", 1)[1]
        summaries_per_ratification.setdefault(key, []).append(idx)
    overflow_drops = 0
    for key, indexes in summaries_per_ratification.items():
        if len(indexes) <= SETTLEMENT_PRIMARY_BEAT_CAP:
            continue
        # Keep first N, drop the rest.
        for idx in indexes[SETTLEMENT_PRIMARY_BEAT_CAP:]:
            keep_indexes.discard(idx)
            overflow_drops += 1
    if overflow_drops == 0:
        return rendered
    return [entry for idx, entry in enumerate(rendered) if idx in keep_indexes]


def _format_witness_grouped_dispatch_event(group: dict) -> dict:
    vars_ = group.get("vars", {})
    witnesses = list(group.get("witnesses", []) or [])
    count = len(witnesses)
    perpetrator = vars_.get("perpetrator_nation", "Unknown")
    victim = vars_.get("victim_nation", "Unknown")
    if count <= 1:
        text = _format_dispatch_event_text("witness_strike_recorded", vars_)
    else:
        sample = ", ".join(str(w) for w in witnesses[:3])
        extra = count - 3
        if extra > 0:
            sample = f"{sample}, and {extra} more"
        text = (
            f"{count} courts have taken note of {perpetrator}'s conduct "
            f"toward {victim}: {sample}."
        )
    return {
        "type": "witness_strike_recorded",
        "text": text,
        "priority": commitments_priority("witness_strike_recorded", vars_),
        "episode_id": vars_.get("episode_id", ""),
        "witness_count": int(count),
        "witness_nations": witnesses,
    }
