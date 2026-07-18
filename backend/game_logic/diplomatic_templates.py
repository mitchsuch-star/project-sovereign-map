"""
Diplomatic Template Library — Phase 8 Session 3

Templates T1-T10 for Talleyrand's conversational diplomacy.
Templates T11-T27 are Session 4-6 scope.

Architecture:
  DIPLOMATIC_TEMPLATES keyed by (situation, game_bucket, specificity)
  Each template has text (with {slots}), options, and recommendation index.
"""

from typing import Any, Dict, List, Mapping, Optional

from backend.nation_config import get_player_nation


def _diplomat_name_from_record(record: Any) -> str:
    if record is None:
        return ""
    if isinstance(record, dict):
        return str(record.get("name", "") or "")
    return str(getattr(record, "name", "") or "")


def resolve_named_diplomat(
    speaker: str,
    nation: str,
    world: Any = None,
) -> str:
    """Resolve a presentation speaker to a named envoy or chancery fallback."""
    speaker_key = str(speaker or "").strip().lower()
    nation_name = str(nation or "").strip()

    if speaker_key == "system":
        return ""
    if speaker_key == "foreign_office":
        return f"The Chancery of {nation_name}" if nation_name else "The Chancery"
    if speaker_key == "talleyrand":
        return "Talleyrand"

    if speaker_key in {"envoy", "named_diplomat", "diplomat"}:
        diplomats = getattr(world, "diplomats", None) if world is not None else None
        if isinstance(diplomats, dict):
            resolved = _diplomat_name_from_record(diplomats.get(nation_name))
            if resolved:
                return resolved
            return f"The Chancery of {nation_name}" if nation_name else "The Chancery"

        from backend.models.diplomat import STARTING_DIPLOMATS
        resolved = _diplomat_name_from_record(STARTING_DIPLOMATS.get(nation_name))
        if resolved:
            return resolved
        return f"The Chancery of {nation_name}" if nation_name else "The Chancery"

    if speaker:
        return str(speaker)
    return f"The Chancery of {nation_name}" if nation_name else "The Chancery"

# ═══════════════════════════════════════════════════════════════════
# W6-10 (E-CA-6) — THE DIPLOMAT SPEAKS: incoming-proposal voice lines.
#
# A deterministic per-register bank (hawk / schemer / dove / chancery
# fallback — registers per DIPLOMAT_VOICE_BIBLE.md) that VOICES an
# incoming proposal and its motive: the decision_reason rendered
# in-character, never as a tag. Named-cast overrides keep the Bible's
# register distinctions (Castlereagh = institutional hawk, Hardenberg =
# personal hawk, Metternich = schemer-at-us, Einsiedel = the dove).
# The `loyalist` register (6 client-court nations) now has its own
# defined register (DEF-1 Roster Voices — the dutiful crown-servant);
# only unknown/absent personalities fall back to the chancery register.
# No LLM (GR6); rotation is deterministic (turn + nation length).
# ═══════════════════════════════════════════════════════════════════

# Motive clauses per (register, decision_reason) — {nation} slot only.
_INCOMING_MOTIVE_LINES = {
    ("hawk", "war_overload"): [
        "The war has taken from {nation} more than it returns.",
        "{nation}'s armies are spent, and they know it as well as we do.",
    ],
    ("hawk", "shared_enemy_survival"): [
        "We share an enemy, and {nation} would rather share the fighting.",
        "{nation} sees the same storm we do, and would stand under one roof.",
    ],
    ("hawk", "hegemony_pressure"): [
        "Europe grows uneasy at France's shadow, and {nation} would rather watch the roads than the frontier.",
        "{nation} does not love our reach — but they would sooner treat with it than test it.",
    ],
    ("hawk", "unknown_baseline"): [
        "{nation} judges the moment favorable and moves plainly.",
        "{nation} wastes no words on sentiment; the offer is the argument.",
    ],
    ("hawk", "agenda_pursuit"): [
        "What {nation} wants it has named before all Europe — and it will have it by treaty or by war.",
        "{nation} presses its design without apology; the papers merely march ahead of the columns.",
    ],
    ("schemer", "war_overload"): [
        "{nation} finds the war… no longer economical.",
        "The ledgers of {nation} have voted for peace, whatever their generals say.",
    ],
    ("schemer", "shared_enemy_survival"): [
        "{nation} observes that our enemies are, conveniently, the same.",
        "{nation} proposes that we be useful to one another — for as long as that lasts.",
    ],
    ("schemer", "hegemony_pressure"): [
        "{nation} finds France's ascent… instructive, and prefers a seat near the fire to a place in it.",
        "{nation} is most attentive to our progress — attentive enough to want papers signed.",
    ],
    ("schemer", "unknown_baseline"): [
        "{nation} offers no reason, which is itself a reason.",
        "{nation} moves quietly; the terms will say what the letter does not.",
    ],
    ("schemer", "agenda_pursuit"): [
        "{nation} advances a design of long standing — the ink is merely its quietest instrument.",
        "Every court has its wants; {nation} has folded its own into this offer, neatly.",
    ],
    ("dove", "war_overload"): [
        "{nation} begs an end to the bleeding, for both our peoples.",
        "{nation} asks most humbly that the guns be given rest.",
    ],
    ("dove", "shared_enemy_survival"): [
        "{nation} fears the same power we do, and asks to fear it beside us.",
        "{nation} seeks shelter, Sire — and offers friendship as the rent.",
    ],
    ("dove", "hegemony_pressure"): [
        "{nation} asks only to be reassured that France's greatness leaves room for small nations.",
        "{nation} watches our armies grow and prays a signature will suffice.",
    ],
    ("dove", "unknown_baseline"): [
        "{nation} extends the offer in evident good faith.",
        "{nation} hopes, most respectfully, that we will hear them out.",
    ],
    ("dove", "agenda_pursuit"): [
        "{nation} asks for what its court has always wanted — and would far rather sign for it than bleed for it.",
        "{nation}'s desire is old and openly held; they pray a treaty may serve where armies need not.",
    ],
    ("chancery", "war_overload"): [
        "Their chancery writes that the war serves {nation} no longer.",
        "The court of {nation} counts its losses and asks for quiet.",
    ],
    ("chancery", "shared_enemy_survival"): [
        "Their chancery notes that {nation} and France look at the same enemy.",
        "The court of {nation} would make common cause against a common danger.",
    ],
    ("chancery", "hegemony_pressure"): [
        "Their chancery conveys that {nation} would rather have terms with France than reasons to fear her.",
        "The court of {nation} watches our ascent and asks for ink instead of iron.",
    ],
    ("chancery", "unknown_baseline"): [
        "Their chancery conveys the offer without further comment.",
        "The court of {nation} lets the terms speak for themselves.",
    ],
    ("chancery", "agenda_pursuit"): [
        "Their chancery pursues the court's declared design; this instrument is drafted in its service.",
        "The court of {nation} advances its stated ambitions — the present offer follows from them directly.",
    ],
    # DEF-1 Roster Voices — the LOYALIST register (the dutiful servant of
    # the Crown). He speaks for his sovereign, not himself: every position
    # is His Majesty's, every act a matter of service. Distinct from the
    # Dove (who fears) and the Schemer (who serves himself). Content varies
    # by a court's stance toward France; the register — faithful, formal,
    # self-effacing — does not. See DIPLOMAT_VOICE_BIBLE.md §Loyalist.
    ("loyalist", "war_overload"): [
        "His Majesty's servant conveys that {nation} has borne its share of this war, and its sovereign would see it closed.",
        "The Crown's instruction is peace; {nation} has spent enough of its people in this quarrel.",
    ],
    ("loyalist", "shared_enemy_survival"): [
        "By the Crown's judgment, one hand threatens {nation} and France alike, and should be answered by both.",
        "His Majesty instructs that {nation} stand beside France against the danger both thrones can see.",
    ],
    ("loyalist", "hegemony_pressure"): [
        "{nation}'s sovereign would keep his house at peace with France's greatness, and sends his servant to say as much.",
        "As my master wills, {nation} seeks France's good regard rather than France's displeasure.",
    ],
    ("loyalist", "unknown_baseline"): [
        "His Majesty's servant lays {nation}'s offer before France, exactly as instructed.",
        "By the Crown's command, {nation} sets these terms before France for her consideration.",
    ],
    ("loyalist", "agenda_pursuit"): [
        "My master's design is known to all Europe; {nation} sends this offer in its pursuit.",
        "As his sovereign has long willed, {nation} moves toward what the Crown desires.",
    ],
}

# Named-cast motive overrides — the Voice Bible's register distinctions.
_NAMED_MOTIVE_LINES = {
    ("Castlereagh", "war_overload"): [
        "His Majesty's Government observes that this war profits no one — least of all its authors.",
        "London finds the present hostilities without further object.",
    ],
    ("Castlereagh", "shared_enemy_survival"): [
        "His Majesty's Government notes a common danger, and proposes a common answer.",
        "London observes that our interests, for once, run in the same channel.",
    ],
    ("Castlereagh", "hegemony_pressure"): [
        "His Majesty's Government observes the growth of French power with concern, and prefers instruments to incidents.",
        "London does not negotiate from fear; it negotiates from arithmetic. The arithmetic has changed.",
    ],
    ("Castlereagh", "unknown_baseline"): [
        "His Majesty's Government transmits the following for France's consideration.",
        "London announces its terms; it does not explain them.",
    ],
    ("Castlereagh", "agenda_pursuit"): [
        "His Majesty's Government pursues stated objects, not adventures; the present terms serve those objects.",
        "London's requirements in this matter are of record. The offer follows from them.",
    ],
    ("Hardenberg", "war_overload"): [
        "Prussia has bled enough for other men's quarrels.",
        "Prussia counts her dead and finds the ledger unacceptable.",
    ],
    ("Hardenberg", "shared_enemy_survival"): [
        "Prussia knows her enemies. Today, France is not first among them.",
        "Prussia does not forget — but she can postpone. We face the same foe.",
    ],
    ("Hardenberg", "hegemony_pressure"): [
        "Europe grows uneasy at France's shadow, and Prussia would rather watch the roads than the frontier.",
        "Prussia does not bow. But Prussia can sign.",
    ],
    ("Hardenberg", "unknown_baseline"): [
        "Prussia says what she means: here is the offer.",
        "Prussia does not dress her asks in ribbons. Read the terms.",
    ],
    ("Hardenberg", "agenda_pursuit"): [
        "Prussia wants what Prussia is owed. This paper says so plainly.",
        "Berlin does not disguise its object. Read the terms; the object is there.",
    ],
    ("Metternich", "war_overload"): [
        "Austria finds the war has outlived its arguments.",
        "Vienna observes, with some weariness, that the fighting no longer serves even its winners.",
    ],
    ("Metternich", "shared_enemy_survival"): [
        "Austria notes that we are, for the moment, inconvenienced by the same power.",
        "Vienna finds our interests aligned — a rare weather, best used before it turns.",
    ],
    ("Metternich", "hegemony_pressure"): [
        "Austria is… attentive to France's progress, and would prefer that attention remain cordial.",
        "Vienna finds France's reach remarkable, and remarkable things are best bound in treaties.",
    ],
    ("Metternich", "unknown_baseline"): [
        "Austria offers terms; Vienna trusts France will find them — considered.",
        "Vienna sends papers, not explanations. The papers are thorough.",
    ],
    ("Metternich", "agenda_pursuit"): [
        "Austria's designs are not secrets; they are policies — and policies, unlike secrets, may be purchased.",
        "Vienna has wanted the same things for a decade; one merely finds this the convenient season to put them in writing.",
    ],
    ("Einsiedel", "war_overload"): [
        "His Majesty asks most respectfully that the suffering be brought to an end.",
        "We beg France's understanding — Saxony cannot carry this war further.",
    ],
    ("Einsiedel", "shared_enemy_survival"): [
        "His Majesty asks most respectfully to stand nearer France in these dangerous days.",
        "We beg France's protection against a danger we cannot face alone.",
    ],
    ("Einsiedel", "hegemony_pressure"): [
        "His Majesty asks most respectfully for assurance — Europe has grown loud, and Saxony is small.",
        "We beg France's patience; a small court must have papers where great ones have armies.",
    ],
    ("Einsiedel", "unknown_baseline"): [
        "His Majesty submits the offer most respectfully for France's consideration.",
        "We hope, most sincerely, that France will find the terms agreeable.",
    ],
    # ── DEF-1 Roster Voices: the 15 Europe courts (Slice B, bespoke + adversarially verified against DIPLOMAT_VOICE_BIBLE.md) ──
    # Araujo
    ('Araujo', 'war_overload'): [
        'Portugal is a small kingdom at the edge of a great storm, and she grows weary of bracing her shutters against winds that are not of her making.',
        'Lisbon has counted the cost of these campaigns in ports left idle and harvests left unsold, and she would gladly close that ledger before the season turns.',
    ],
    ('Araujo', 'shared_enemy_survival'): [
        'Portugal has learned that a danger which unsettles Paris will not long spare Lisbon, and a court with few soldiers does well to keep close to the strong when one peril overhangs them both.',
        'It would be a poor sort of prudence for Lisbon to look quietly away while a threat gathers that troubles France no less than herself.',
    ],
    ('Araujo', 'hegemony_pressure'): [
        'Portugal has watched France grow so vast that a careful minister in Lisbon thinks less of resisting such a tide than of finding a quiet harbor within it.',
        "A kingdom as modest as ours does not measure itself against the Empire's shadow, and Lisbon would far rather reach an understanding than be caught standing in its path.",
    ],
    ('Araujo', 'unknown_baseline'): [
        'Lisbon sends this proposal in the plain hope that two courts may speak frankly and part on better terms than they met.',
        'Portugal lays this matter before France without ceremony or hidden design, trusting that a fair word offered today spares a hard one tomorrow.',
    ],
    # Bernstorff
    ('Bernstorff', 'war_overload'): [
        "Season upon season this war has pressed against Denmark's coasts and crowded her narrows, and the Crown Prince has charged his servants to spare the realm any further of it.",
        "Denmark's neutral flag has been made to bear the whole weight of a quarrel not her own, and her sovereign now judges that burden long enough carried.",
    ],
    ('Bernstorff', 'shared_enemy_survival'): [
        'A power that keeps its fleets forever off the narrows presses upon Denmark and France alike, and the Crown Prince holds that courts so menaced do well to stand as one.',
        "The same navy that shadows Denmark's straits and throttles the commerce of the Baltic bears no less heavily upon France, and by her sovereign's reckoning two realms so pressed are better joined than sundered.",
    ],
    ('Bernstorff', 'hegemony_pressure'): [
        "The Crown of Denmark marks how far France's power now reaches across Europe, and her sovereign judges it the part of a careful neighbour to settle matters by agreement rather than by arms.",
        "As France's ascendancy spreads over the map of the Continent, the Crown Prince would keep his narrows clear of so great a contest and treat plainly with Paris instead.",
    ],
    ('Bernstorff', 'unknown_baseline'): [
        'The Crown of Denmark sends her minister to set a proposal plainly before France, one neutral court speaking correctly to another across the narrow seas.',
        'By command of the Crown Prince, Denmark lays this matter before the French court directly and without disguise, that it may be weighed on its own terms.',
    ],
    # Cevallos
    ('Cevallos', 'war_overload'): [
        'His Catholic Majesty has watched the treasure and the sons of Spain spent in a war that wearies the whole kingdom, and it is His will that this burden now be set down.',
        'The Crown of Spain has borne the length of this war in good faith, and His Majesty judges that a loyal realm may be asked to bear no more.',
    ],
    ('Cevallos', 'shared_enemy_survival'): [
        "His Catholic Majesty sees the very foe that threatens France standing in equal enmity against the Spanish throne, and it is the King's command that the two crowns face it as one.",
        'Spain and France are menaced by a single power upon the seas, and His Majesty holds that the safety of both kingdoms rests in common cause.',
    ],
    ('Cevallos', 'hegemony_pressure'): [
        "His Catholic Majesty marks how far the power of France now reaches, and it is the King's wish that so weighty a friendship be fixed in settled terms and not left to chance.",
        "The Crown of Spain beholds the greatness to which France has risen, and it is His Majesty's wish that a friendship of such weight rest upon plain and honorable articles rather than upon trust alone.",
    ],
    ('Cevallos', 'unknown_baseline'): [
        'His Catholic Majesty has charged this ministry to set His terms before you plainly, in the very form the King intends and no other.',
        'The Crown of Spain sets this proposal before you as it stands, by the direct command of His Majesty.',
    ],
    # Chancery of Hanover
    ('Chancery of Hanover', 'war_overload'): [
        "Hanover has been a high-road for other men's armies too long, and the electorate has quietly learned that a still country outlasts a loud one.",
        "This court has watched a quarrel that was never Hanover's own empty its granaries and wear its lanes to ruts, and weariness now speaks more plainly than any allegiance could.",
    ],
    ('Chancery of Hanover', 'shared_enemy_survival'): [
        "There is a peril that troubles both Paris and this court alike, and Hanover would sooner meet it at France's shoulder than across the field from her.",
        "The electorate finds its own dangers and France's have grown to wear the same face, and a small country learns early to keep to the lee of a stronger one.",
    ],
    ('Chancery of Hanover', 'hegemony_pressure'): [
        'Hanover has watched France grow until her shadow lies across the whole of the north, and a prudent electorate does not set itself against a tide it has no power to turn.',
        "This court holds no illusion of matching France's strength, and it judges a quiet understanding far the wiser course beside a proud and empty resistance.",
    ],
    ('Chancery of Hanover', 'unknown_baseline'): [
        'The Chancery of Hanover sets a plain proposal before France, without ornament and without any hidden design folded inside it.',
        'This court comes forward softly, as an electorate must that weighs each word before two watching masters, and lays its offer open for France to read.',
    ],
    # Chancery of Helvetia
    ('Chancery of Helvetia', 'war_overload'): [
        'The cantons have watched foreign armies cross the passes so long that our valleys are worn thin, and Helvetia has no men to spare for the quarrels of greater crowns.',
        'Helvetia was fashioned for the tending of herds and the guarding of the snows, not for the long carriage of war, and the Confederation is weary to the very bone.',
    ],
    ('Chancery of Helvetia', 'shared_enemy_survival'): [
        'A shadow gathers beyond our eastern mountains that menaces the cantons no less than France, and a small folk does well to stand where the larger shield already stands.',
        'The same power that would spill across our passes would press upon France in the same season, and Helvetia would sooner share the watch than keep it alone.',
    ],
    ('Chancery of Helvetia', 'hegemony_pressure'): [
        'France has grown so vast that even an old neutrality feels its weight against the mountains, and the Confederation has always held it wiser to bend early than to be broken late.',
        'We are a small confederation that covets nothing beyond the quiet of its own valleys, and before a power so vast the cantons hold it no dishonor to seek terms rather than a stand they could not keep.',
    ],
    ('Chancery of Helvetia', 'unknown_baseline'): [
        'The Diet has sent me with a plain proposal and no long oration, for the cantons like their business as they like their mountain roads, straight and without ornament.',
        'Helvetia comes in its own name and by the common wish of its cantons, with the offer laid out plainly and nothing folded away out of sight.',
    ],
    # Chancery of Hesse
    ('Chancery of Hesse', 'war_overload'): [
        'Hesse is a small country that has been trodden by the passage of larger armies, and it wishes only to be left out of what remains of this war.',
        'The war has asked more of Hesse than so modest a land can give, and it longs for nothing so much as quiet.',
    ],
    ('Chancery of Hesse', 'shared_enemy_survival'): [
        'Hesse and France look upon the same danger, and so slight a country would far rather stand quietly beside France than face it alone.',
        "A land as small as Hesse cannot weather the common enemy unaided, and it would sooner be counted, however modestly, among France's friends.",
    ],
    ('Chancery of Hesse', 'hegemony_pressure'): [
        'Hesse has watched France grow very great, and a court so small knows better than to stand in the path of such a power, preferring an understanding to any quarrel.',
        'So great a power has nothing to fear from a house as small as Hesse, which asks only to come quietly to terms and give France no trouble at all.',
    ],
    ('Chancery of Hesse', 'unknown_baseline'): [
        'Hesse comes to the French court with no design and no complaint, asking only to settle a small matter between them.',
        'The Chancery of Hesse lays this before France plainly, as one small court that would prefer its arrangements to remain simple.',
    ],
    # Chancery of Sardinia
    ('Chancery of Sardinia', 'war_overload'): [
        'From his island the King of Sardinia has counted every winter of this war, and the Crown grows weary of a struggle that spares neither his people nor his patience.',
        "His Majesty's house has given years and its soldiers to this long quarrel, and in the King's name his chancery submits that a court so long displaced need bleed no further.",
    ],
    ('Chancery of Sardinia', 'shared_enemy_survival'): [
        "A common danger now stands against both France and the King of Sardinia, and His Majesty's chancery is charged to say that even a displaced crown knows when two swords must meet one enemy.",
        'The same power that would harm France reaches also toward what little remains to the King upon his island, and the Crown, dutiful before necessity, will not face it alone.',
    ],
    ('Chancery of Sardinia', 'hegemony_pressure'): [
        'The King of Sardinia has already felt the full weight of France upon his lost mainland, and the Crown judges it the wiser course to treat with such a power than to defy it to no purpose.',
        "His Majesty marks how far the reach of France now extends across Europe, and in the King's name his chancery would sooner secure an honorable understanding than court a ruin it already knows too well.",
    ],
    ('Chancery of Sardinia', 'unknown_baseline'): [
        "The chancery of Sardinia comes before France in the King's name, charged to set this offer plainly and without ornament before you.",
        "His Majesty's servants are instructed to lay this proposal before you exactly as the King has framed it, adding neither argument nor plea of their own.",
    ],
    # Consalvi
    ('Consalvi', 'war_overload'): [
        "The Holy See has watched too many of God's children fall to the sword, and a shepherd cannot bless what only widows his flock.",
        'War has drawn from Rome more grief than any treasury could hold, and the Church was not raised to preside over so much dying.',
    ],
    ('Consalvi', 'shared_enemy_survival'): [
        'A common adversary now threatens both the throne of France and the See of Peter, and Providence seldom hands two houses the same shield without meaning them to stand behind it together.',
        'The Holy See and France face the same wolf at the fold, Emperor, and even a churchman knows that the lambs who scatter are the lambs who are lost.',
    ],
    ('Consalvi', 'hegemony_pressure'): [
        'France has grown so vast that her shadow now falls even upon the altar, and Rome, having no armies to set against it, would far sooner offer her friendship than her fear.',
        'Rome has outlasted the storms of many centuries by bowing her head to the wind rather than breaking against it, and she would seek only to shelter beneath the greatness of France, never to strive against it.',
    ],
    ('Consalvi', 'unknown_baseline'): [
        'The Holy See comes to the Emperor bearing neither complaint nor condition, only a matter it would set plainly before him.',
        'Rome lays this before the Emperor without adornment, a matter she would rather he judged for its own worth than for the ceremony that might dress it.',
    ],
    # Czartoryski
    ('Czartoryski', 'war_overload'): [
        'Russia has spent enough of her strength upon a war that advances no vision equal to the century, and the reordering of Europe cannot be raised upon exhausted armies.',
        'The blood Russia now pours out would be better husbanded for the larger work that history reserves for her, and this present quarrel only postpones that appointment.',
    ],
    ('Czartoryski', 'shared_enemy_survival'): [
        "There is an adversary whose ambition menaces the whole architecture of Europe, and two powers who grasp the continent's future would do well to face him as one.",
        'Both Petersburg and Paris look upon a rival who would keep Europe fettered in its old and broken shape, and two crowns acting as one might yet decide what should rise in its place.',
    ],
    ('Czartoryski', 'hegemony_pressure'): [
        'A Europe in which one crown grows to eclipse all the others can never settle into the design that a lasting peace requires, and Russia would far rather compose that balance by agreement than leave it to the arbitration of arms.',
        "France's star climbs so swiftly that the lesser courts grow restive, and it would honor the wisdom of both our thrones to settle the shape of things before that unease hardens into coalition.",
    ],
    ('Czartoryski', 'unknown_baseline'): [
        'Russia lays this proposal before you in the plain conviction that the affairs of Europe are best arranged by those with the vision to see the whole board.',
        'Petersburg extends these terms without ornament, trusting that two courts of consequence need no long preamble to perceive where their interests already point.',
    ],
    # Ehrenheim
    ('Ehrenheim', 'war_overload'): [
        "His Majesty's servant is charged to avow plainly that Sweden has spent her strength in the King's long quarrel with Bonaparte beyond what her means can sustain.",
        "The Crown does not disguise from France that Sweden's armies and her treasury are alike worn thin by a war the King no longer has the means to press.",
    ],
    ('Ehrenheim', 'shared_enemy_survival'): [
        "His Majesty makes no secret of his distaste for France, yet the Crown instructs its servant to own that a nearer foe now threatens the kingdom's very survival and menaces both thrones alike.",
        "By the King's own command his minister is bidden to set aside the quarrel of years, for a common enemy presses upon France and Sweden together and would see both undone.",
    ],
    ('Ehrenheim', 'hegemony_pressure'): [
        "His Majesty regards the spread of French power across the north with plain disquiet, yet the Crown, weighing that disquiet against Sweden's slender means, instructs its servant to prefer terms to the trial of arms.",
        'The King does not pretend to welcome the shadow France now casts over Europe, and it is precisely because he cannot answer it in the field that his servant is sent seeking accommodation.',
    ],
    ('Ehrenheim', 'unknown_baseline'): [
        "His Majesty's servant is instructed to set this proposal before France exactly as the Crown has framed it, and to add nothing to it of his own.",
        'The King has decided what he would put to France, and his minister comes only to convey that decision plainly, neither pressing it nor coloring it.',
    ],
    # Marescalchi
    ('Marescalchi', 'war_overload'): [
        "The Kingdom of Italy has poured out its sons and its treasure in its sovereign's wars, and now, its duty faithfully done, it lays its weariness before the throne it shares with France.",
        "Italy has followed wherever its King's eagles have led, and the kingdom's fields, so long trampled beneath the march of armies, now long for quiet.",
    ],
    ('Marescalchi', 'shared_enemy_survival'): [
        "The same foe that menaces France stands equally against the crown Italy shares with her, and the Kingdom would gladly set its shoulder beside the Emperor's own.",
        "Italy sees the enemy at the Empire's gate as an enemy at its own, for the King who guards Paris is the King who guards Milan.",
    ],
    ('Marescalchi', 'hegemony_pressure'): [
        'His Majesty has raised France to a greatness Europe has never beheld, and the Kingdom of Italy, which shares his crown, asks only to be joined to that grandeur by firm covenant rather than left to stand apart from it.',
        "Where the Emperor's star climbs so high above the other courts of Europe, the Kingdom of Italy seeks no station of its own apart from his, and asks that its loyal place at his side be set down plainly for all the continent to read.",
    ],
    ('Marescalchi', 'unknown_baseline'): [
        'The Kingdom of Italy comes before France in the plain good faith of a house that answers to the very same sovereign.',
        'Italy lays its proposal before the Emperor without condition or artifice, as a faithful kingdom owes its plain word to its King.',
    ],
    # Medici
    ('Medici', 'war_overload'): [
        'Naples is a small kingdom that has spent both its treasure and its quiet on a quarrel that was never truly its own.',
        'The Two Sicilies have watched this war pass over them like weather, and even weather, in time, wears the stone.',
    ],
    ('Medici', 'shared_enemy_survival'): [
        'Naples and France feel the same cold shadow move upon the water, and a small kingdom learns early which storms it dares not face alone.',
        'There is a danger that troubles Paris and Naples alike, and it would be an ungracious thing to stand apart when our concerns lean the same way.',
    ],
    ('Medici', 'hegemony_pressure'): [
        'The greatness of France fills the whole of the continent now, and a court as modest as Naples has never thought it wise to stand in the path of so great a river.',
        'Naples has never confused the friendship of great powers with a burden, and a small court stays whole only by knowing where the safer shore lies.',
    ],
    ('Medici', 'unknown_baseline'): [
        'Naples comes to Paris in the old manner, with courtesy and an open hand, and lays a simple proposal upon the table.',
        'There is a small matter the court of Naples would set before the Emperor, plainly and without any ceremony.',
    ],
    # Montgelas
    ('Montgelas', 'war_overload'): [
        'Bavaria has spent more blood and coin on this war than any peace could ever repay, and a well-kept state does not go on funding a loss.',
        "Each further campaign quietly undoes a year of Munich's reforms, and Bavaria did not remake itself merely to be marched across a second time.",
    ],
    ('Montgelas', 'shared_enemy_survival'): [
        'Bavaria and France are pressed by the same court to the east, and two states facing one neighbor are worth more set side by side than kept apart.',
        "Vienna's designs weigh on Munich as heavily as on Paris, and it would be poor arithmetic to answer the same enemy in two separate quarters.",
    ],
    ('Montgelas', 'hegemony_pressure'): [
        'Bavaria has marked where the weight of Europe now settles, and a prudent state places itself beside the rising power, never beneath it.',
        "France's reach lengthens with every season, and Munich would sooner write the terms of that nearness now than be handed them later.",
    ],
    ('Montgelas', 'unknown_baseline'): [
        'Bavaria finds a plain advantage in this arrangement and prefers to settle such matters while they are still only advantages.',
        'Munich lays the question before Paris without ornament, as one balances an account between two parties who each know their own interest.',
    ],
    # Reis Efendi
    ('Reis Efendi', 'war_overload'): [
        'The Porte has outlasted longer storms than this one, yet it sees no wisdom in spending good years upon a quarrel that time itself would sooner settle.',
        'The Empire is old and has grown weary of these long reckonings, and it would far rather let this war drift quietly out of season than press it another mile.',
    ],
    ('Reis Efendi', 'shared_enemy_survival'): [
        "It has not escaped the Porte's patient notice that France and the House of Osman are vexed by the very same restless neighbor, and where two men share a shadow they may as easily share a lamp.",
        'The Sublime Porte, which forgets nothing and hurries nothing, perceives that its concerns and those of France now incline toward one and the same disturber of the general peace.',
    ],
    ('Reis Efendi', 'hegemony_pressure'): [
        'The Porte watches the star of France climb ever higher and, being an old admirer of whatever endures, would sooner arrange itself gracefully beneath so great a light than stand across its path.',
        "The Sublime Porte has learned across many centuries that it is the wiser house which comes to terms with the rising tide rather than argue with it, and it finds in France's greatness every reason for accommodation and none for dispute.",
    ],
    ('Reis Efendi', 'unknown_baseline'): [
        'The Sublime Porte approaches France in the plain and unhurried manner of an old house, laying its proposal upon the table with neither urgency nor concealment.',
        "The Porte offers this matter simply, as one offers coffee to a guest, and is content to await France's pleasure in its own good time.",
    ],
    # Schimmelpenninck
    ('Schimmelpenninck', 'war_overload'): [
        "Holland has spent its treasure and its seamen in France's wars until the Republic can furnish no more, and the States have charged me to say so plainly.",
        "The commonwealth has borne the war at France's side to the very limit of what a small nation can bear, and it is the duty of this office to report that limit reached.",
    ],
    ('Schimmelpenninck', 'shared_enemy_survival'): [
        "Holland and France are pressed by the same power upon the same seas, and the Republic holds that its safety and its patron's have become one cause.",
        'The enemy that threatens France threatens first the coasts of Holland, and the States have resolved that the two nations must now stand or fall as one.',
    ],
    ('Schimmelpenninck', 'hegemony_pressure'): [
        "Holland lives already within the reach of France's power and knows better than any nation what that reach can compass, and the Republic would have that relation settled by treaty rather than proved by arms.",
        "France now stands foremost among the powers of Europe, and the States, mindful that Holland's fortunes have long been joined to hers, have charged me to seek that this connection be made firm and lasting by treaty.",
    ],
    ('Schimmelpenninck', 'unknown_baseline'): [
        'The States of Holland have directed this proposal to your Majesty, and I lay it before you as the office requires, without addition of my own.',
        'Holland presents these terms in the plain form the Republic has settled upon, and it is mine only to deliver them faithfully.',
    ],
}

# Attribution prefixes (the "face" of the line).
_NAMED_ATTRIBUTIONS = {
    "Castlereagh": "Castlereagh writes, without warmth:",
    "Hardenberg": "Hardenberg, stiffly:",
    "Metternich": "Metternich, with perfect politeness:",
    "Einsiedel": "Einsiedel, anxiously:",
    # DEF-1 Roster Voices — the 15 Europe courts (bespoke, Voice-Bible verified).
    'Araujo': 'Araujo, measuring the room:',
    'Bernstorff': 'Bernstorff, watchful and correct:',
    'Cevallos': "Cevallos, in his King's name:",
    'Chancery of Hanover': 'The Chancery of Hanover, guardedly:',
    'Chancery of Helvetia': 'The Helvetic Chancery, unhurried:',
    'Chancery of Hesse': 'Hesse, wishing to go unnoticed:',
    'Chancery of Sardinia': 'The Sardinian chancery, dutifully:',
    'Consalvi': 'Cardinal Consalvi, serenely:',
    'Czartoryski': 'Czartoryski, with sweeping calm:',
    'Ehrenheim': "Ehrenheim, conveying his King's word:",
    'Marescalchi': 'Marescalchi, with ardent devotion:',
    'Medici': 'Medici, smoothly evasive:',
    'Montgelas': 'Montgelas, coolly reckoning the gains:',
    'Reis Efendi': 'Reis Efendi, serene and unhurried:',
    'Schimmelpenninck': 'Schimmelpenninck, correct and unillusioned:',
}

# The ask, in-register, per acceptance type (terms["type"]).
_INCOMING_ASK_LINES = {
    "open_borders": "Open the borders.",
    "non_aggression": "Sign the pact of non-aggression.",
    "defensive_alliance": "Stand with them if war comes.",
    "alliance": "Join their cause in full.",
    "armistice_losing": "Grant the armistice.",
    "armistice": "Grant the armistice.",
    "peace": "Let there be peace.",
    "harsh_peace": "Weigh their terms.",
    "trade_agreement": "Open the trade.",
    # NA-5 §8: the ultimatum's ask, spoken plainly.
    "ultimatum_demand": "Grant what is demanded, or the cannon will collect it.",
}

# Legacy/response decision reasons collapse to the generic motive.
_MOTIVE_REASONS = {"war_overload", "shared_enemy_survival",
                   "hegemony_pressure", "agenda_pursuit",
                   "unknown_baseline"}


def compose_incoming_diplomat_line(
    world: Any,
    *,
    nation: str,
    proposal_type: str,
    decision_reason: str = "",
) -> str:
    """One in-register spoken line for an incoming proposal: attribution +
    motive (the decision_reason, voiced) + the ask. Deterministic (GR6):
    variant rotation keys on turn + nation, never RNG. Every name resolves
    through resolve_named_diplomat (Voice Bible rule)."""
    nation_name = str(nation or "").strip()
    if not nation_name:
        return ""
    name = resolve_named_diplomat("envoy", nation_name, world)
    reason = str(decision_reason or "").strip()
    if reason not in _MOTIVE_REASONS:
        reason = "unknown_baseline"

    variants = _NAMED_MOTIVE_LINES.get((name, reason))
    if variants:
        attribution = _NAMED_ATTRIBUTIONS.get(name, f"{name}:")
    else:
        # Register from the diplomat record. Loyalist now has its own
        # defined register (DEF-1 Roster Voices); only unknown/absent
        # personalities fall back to the chancery register.
        diplomats = getattr(world, "diplomats", {}) or {}
        record = diplomats.get(nation_name)
        register = ""
        if record is not None:
            raw = getattr(record, "personality", "")
            register = str(getattr(raw, "value", raw) or "").lower()
        if register not in ("hawk", "schemer", "dove", "loyalist"):
            register = "chancery"
        variants = _INCOMING_MOTIVE_LINES[(register, reason)]
        if register == "chancery" or name.startswith("The Chancery"):
            attribution = f"{name} conveys:" if name else "Their chancery conveys:"
        else:
            attribution = f"{name}:"

    turn = int(getattr(world, "current_turn", 0))
    motive = variants[(turn + len(nation_name)) % len(variants)]
    motive = motive.format(nation=nation_name)
    ask = _INCOMING_ASK_LINES.get(str(proposal_type or ""), "")
    quote = f"{motive} {ask}".strip()
    return f"{attribution} \"{quote}\""


# ═══════ TEMPLATE LIBRARY ═══════
# Key: (intent_type, diplo_state, bucket_group)
# bucket_group: specific bucket name OR "any" for wildcard
# Lookup order: exact match → (intent, state, "any") → fallback

DIPLOMATIC_TEMPLATES = {
    # ══════════════════════════════════════════════
    # T1: VAGUE + WAR + winning_comfortably
    # ══════════════════════════════════════════════
    ("proposal_options", "WAR", "winning_comfortably"): {
        "text": (
            "Sire, we hold a commanding position against {target_nation}. "
            "Their armies falter and their courts grow anxious. I see several paths forward."
        ),
        "options": [
            {
                "label": "Generous peace",
                "description": "Offer magnanimous terms — build goodwill for the future.",
                "action": "execute_proposal",
                "proposal_type": "peace",
            },
            {
                "label": "Harsh demands",
                "description": "Press our advantage — demand territory and tribute.",
                "action": "execute_proposal",
                "proposal_type": "peace",
            },
            {
                "label": "Continue fighting",
                "description": "We can extract more concessions on the battlefield.",
                "action": "dismiss",
            },
        ],
        "recommendation": 0,
    },

    # ══════════════════════════════════════════════
    # T2: VAGUE + WAR + losing_badly
    # ══════════════════════════════════════════════
    ("proposal_options", "WAR", "losing_badly"): {
        "text": (
            "Sire, our position against {target_nation} is... precarious. "
            "The battlefield has not favored us. We must act before things deteriorate further."
        ),
        "options": [
            {
                "label": "Sue for peace",
                "description": "Request peace on reasonable terms while we still can.",
                "action": "execute_proposal",
                "proposal_type": "peace",
            },
            {
                "label": "Offer concessions",
                "description": "Sweeten the deal with gold or territory to secure acceptance.",
                "action": "execute_proposal",
                "proposal_type": "peace",
            },
            {
                "label": "Stall",
                "description": "Buy time — request an armistice while we regroup.",
                "action": "execute_proposal",
                "proposal_type": "armistice",
            },
        ],
        "recommendation": 0,
    },

    # ══════════════════════════════════════════════
    # T3: VAGUE + WAR + stalemate (also winning_slightly, losing_slightly)
    # ══════════════════════════════════════════════
    ("proposal_options", "WAR", "stalemate"): {
        "text": (
            "Sire, the war with {target_nation} is at a standstill. "
            "Neither side has won a decisive advantage on the battlefield."
        ),
        "options": [
            {
                "label": "Propose peace",
                "description": "End the bloodshed on balanced terms.",
                "action": "execute_proposal",
                "proposal_type": "peace",
            },
            {
                "label": "Press advantage",
                "description": "Continue the campaign — one victory could tip the balance.",
                "action": "dismiss",
            },
            {
                "label": "Wait",
                "description": "Hold position and see how events unfold.",
                "action": "dismiss",
            },
        ],
        "recommendation": 0,
    },

    # ══════════════════════════════════════════════
    # T4: VAGUE + PEACE + hostile
    # ══════════════════════════════════════════════
    ("proposal_options", "PEACE", "hostile"): {
        "text": (
            "Sire, relations with {target_nation} are tense. "
            "There is deep mistrust between our courts. "
            "Tread carefully."
        ),
        "options": [
            {
                "label": "Improve relations",
                "description": "Send me to build bridges — a diplomatic mission.",
                "action": "start_mission",
                "terms": {"mission_type": "IMPROVE_RELATIONS"},
            },
            {
                "label": "Propose open borders",
                "description": "A small step — opening borders shows good faith.",
                "action": "execute_proposal",
                "proposal_type": "open_borders",
            },
            {
                "label": "Leave them be",
                "description": "Some wounds need time to heal.",
                "action": "dismiss",
            },
        ],
        "recommendation": 0,
    },

    # ══════════════════════════════════════════════
    # T5: VAGUE + PEACE + friendly
    # ══════════════════════════════════════════════
    ("proposal_options", "PEACE", "friendly"): {
        "text": (
            "Sire, {target_nation} views us favorably. "
            "Their court speaks well of {player_nation}. "
            "The time may be ripe to deepen our ties."
        ),
        "options": [
            {
                "label": "Propose alliance",
                "description": "A full military alliance — mutual defense and cooperation.",
                "action": "execute_proposal",
                "proposal_type": "alliance",
            },
            {
                "label": "Non-aggression pact",
                "description": "A more cautious step — guarantee peace without military commitment.",
                "action": "execute_proposal",
                "proposal_type": "non_aggression",
            },
            {
                "label": "Vassalage",
                "description": "Bind them to our will as a vassal state.",
                "action": "execute_proposal",
                "proposal_type": "vassalage",
            },
        ],
        "recommendation": 0,
    },

    # ══════════════════════════════════════════════
    # T6: MEDIUM + WAR (any bucket) — suggest specific terms
    # ══════════════════════════════════════════════
    ("proposal_confirm", "WAR", "any"): {
        "text": (
            "Sire, regarding the {proposal_type} proposal to {target_nation}, "
            "I have prepared terms appropriate to the current military situation."
        ),
        "options": [
            {
                "label": "Send as suggested",
                "description": "Send the proposal with my recommended terms.",
                "action": "execute_proposal",
            },
            {
                "label": "Harsher terms",
                "description": "Demand more — we can afford to push.",
                "action": "modify_harsh",
            },
            {
                "label": "More generous",
                "description": "Sweeten the offer to improve chances of acceptance.",
                "action": "modify_generous",
            },
            {
                "label": "Adjust terms",
                "description": "Build the offer step by step.",
                "action": "adjust_terms",
            },
            {
                "label": "Reconsider",
                "description": "Let me think about this.",
                "action": "reconsider",
            },
        ],
        "recommendation": 0,
    },

    # ══════════════════════════════════════════════
    # T6b: MEDIUM + PEACE (any bucket)
    # ══════════════════════════════════════════════
    ("proposal_confirm", "PEACE", "any"): {
        "text": (
            "Sire, regarding the {proposal_type} proposal to {target_nation}, "
            "I have prepared terms that reflect the current diplomatic climate."
        ),
        "options": [
            {
                "label": "Send as suggested",
                "description": "Send the proposal with my recommended terms.",
                "action": "execute_proposal",
            },
            # BUGFIX (Bug 4B): These options were missing from PEACE template.
            # Without them, peacetime proposals only offered "Adjust terms" which
            # hit the terms_guidance dead-end in Godot. Must match WAR template (T6).
            # See BUGFIX_PLAN_PROPOSAL_FLOW.md.
            {
                "label": "Harsher terms",
                "description": "Demand more — press our advantage.",
                "action": "modify_harsh",
            },
            {
                "label": "More generous",
                "description": "Sweeten the offer to improve chances of acceptance.",
                "action": "modify_generous",
            },
            {
                "label": "Adjust terms",
                "description": "Build the offer step by step.",
                "action": "adjust_terms",
            },
            {
                "label": "Reconsider",
                "description": "Let me think about this.",
                "action": "reconsider",
            },
        ],
        "recommendation": 0,
    },

    # ══════════════════════════════════════════════
    # T7: SPECIFIC + agree (Talleyrand agrees)
    # Fast-track: immediate execution with [Send][Reconsider]
    # ══════════════════════════════════════════════
    ("proposal_execute", "WAR", "any"): {
        "text": "At once, Sire. I shall deliver your {proposal_type} proposal to {target_nation}.",
        "options": [
            {
                "label": "Send",
                "description": "Dispatch Talleyrand immediately.",
                "action": "send",
            },
            {
                "label": "Reconsider",
                "description": "Wait — let me reconsider.",
                "action": "reconsider",
            },
        ],
        "recommendation": 0,
    },

    ("proposal_execute", "PEACE", "any"): {
        "text": "At once, Sire. I shall present your {proposal_type} proposal to {target_nation}.",
        "options": [
            {
                "label": "Send",
                "description": "Dispatch Talleyrand immediately.",
                "action": "send",
            },
            {
                "label": "Reconsider",
                "description": "Wait — let me reconsider.",
                "action": "reconsider",
            },
        ],
        "recommendation": 0,
    },

    # ══════════════════════════════════════════════
    # T8: SPECIFIC + object (Talleyrand disagrees)
    # STUB for Session 3 — always agrees (T7 used instead)
    # Real objection logic added in Session 6
    # ══════════════════════════════════════════════

    # ══════════════════════════════════════════════
    # T9: FEASIBILITY — handled by generate_feasibility_dialogue()
    # Template not needed here; logic is in diplomatic_dialogue.py
    # ══════════════════════════════════════════════

    # ══════════════════════════════════════════════
    # T10: MISSION START — handled by generate_mission_dialogue()
    # Template not needed here; logic is in diplomatic_dialogue.py
    # ══════════════════════════════════════════════

    # ══════════════════════════════════════════════════════════════
    # SESSION 4 TEMPLATES (T11-T20)
    # ══════════════════════════════════════════════════════════════

    # ══════════════════════════════════════════════
    # T11: INCOMING PROPOSAL — AI proposes to player
    # Used by deliver_ai_proposal() in ai_diplomacy.py
    # ══════════════════════════════════════════════
    ("incoming_proposal", "WAR", "any"): {
        "text": (
            "Sire, {target_diplomat} has arrived with a proposal from {target_nation}:\n\n"
            "  {proposal_summary}\n\n"
            "{talleyrand_assessment}"
        ),
        "options": [
            {
                "label": "Accept",
                "description": "Ratify the treaty as presented.",
                "action": "accept_ai_proposal",
            },
            {
                "label": "Reject",
                "description": "Send the envoy away empty-handed. (Relation -5)",
                "action": "reject_ai_proposal",
            },
            {
                "label": "Counter-offer",
                "description": "Propose modified terms. (Costs 1 DP)",
                "action": "counter_ai_proposal",
            },
        ],
        "recommendation": 0,
    },

    ("incoming_proposal", "PEACE", "any"): {
        "text": (
            "Sire, {target_diplomat} has arrived with a proposal from {target_nation}:\n\n"
            "  {proposal_summary}\n\n"
            "{talleyrand_assessment}"
        ),
        "options": [
            {
                "label": "Accept",
                "description": "Ratify the proposal.",
                "action": "accept_ai_proposal",
            },
            {
                "label": "Reject",
                "description": "Decline. (Relation -5)",
                "action": "reject_ai_proposal",
            },
            {
                "label": "Counter-offer",
                "description": "Suggest modified terms. (Costs 1 DP)",
                "action": "counter_ai_proposal",
            },
        ],
        "recommendation": 0,
    },

    # ══════════════════════════════════════════════
    # T12: PROPOSAL WITH TALLEYRAND ASSESSMENT
    # When Talleyrand adds his own spin on AI proposal
    # ══════════════════════════════════════════════
    ("incoming_proposal_assessed", "WAR", "any"): {
        "text": (
            "Sire, a proposal from {target_nation}:\n\n"
            "  {proposal_summary}\n\n"
            "My assessment: {talleyrand_assessment}\n\n"
            "The Diplomatic Ledger (D key) has the precise figures."
        ),
        "options": [
            {
                "label": "Accept",
                "description": "Accept the terms.",
                "action": "accept_ai_proposal",
            },
            {
                "label": "Reject",
                "description": "Refuse. (Relation -5)",
                "action": "reject_ai_proposal",
            },
            {
                "label": "Counter-offer",
                "description": "Propose modifications. (1 DP)",
                "action": "counter_ai_proposal",
            },
        ],
        "recommendation": 0,
    },

    # ══════════════════════════════════════════════
    # T13: ADVISORY — Nation status assessment
    # Used by diplomatic_advisory.py
    # ══════════════════════════════════════════════
    ("advisory", "WAR", "any"): {
        "text": (
            "You ask about {target_nation}, Sire? Let me assess the situation.\n\n"
            "{target_nation} is currently at war with {player_nation}. "
            "The campaign continues and passions run deep.\n\n"
            "The Diplomatic Ledger (D key) has the precise figures."
        ),
        "options": [
            {
                "label": "What should we do?",
                "description": "Ask Talleyrand for a recommendation.",
                "action": "expand_to_proposal",
            },
            {
                "label": "Thank you",
                "description": "Dismiss.",
                "action": "dismiss",
            },
        ],
        "recommendation": 0,
    },

    ("advisory", "PEACE", "any"): {
        "text": (
            "You ask about {target_nation}, Sire?\n\n"
            "{target_nation} is at peace with {player_nation}. "
            "The diplomatic situation is as one might expect between our courts.\n\n"
            "The Diplomatic Ledger (D key) has the precise figures."
        ),
        "options": [
            {
                "label": "What should we do?",
                "description": "Ask Talleyrand for a recommendation.",
                "action": "expand_to_proposal",
            },
            {
                "label": "Thank you",
                "description": "Dismiss.",
                "action": "dismiss",
            },
        ],
        "recommendation": 0,
    },

    # ══════════════════════════════════════════════
    # T14: ADVISORY — Threat assessment (multi-nation)
    # ══════════════════════════════════════════════
    ("advisory_threat", "any", "any"): {
        "text": (
            "An assessment of the diplomatic landscape, Sire.\n\n"
            "{threat_analysis}\n\n"
            "{recommendation}"
        ),
        "options": [
            {
                "label": "What should we do?",
                "description": "Ask for a specific recommendation.",
                "action": "expand_to_proposal",
            },
            {
                "label": "Thank you",
                "description": "Dismiss.",
                "action": "dismiss",
            },
        ],
        "recommendation": 0,
    },

    # ══════════════════════════════════════════════
    # T15: ADVISORY — Recommendation
    # ══════════════════════════════════════════════
    ("advisory_recommendation", "any", "any"): {
        "text": (
            "{recommendation_text}\n\n"
            "The Diplomatic Ledger (D key) has the precise figures, Sire."
        ),
        "options": [
            {
                "label": "Do it",
                "description": "Proceed with Talleyrand's suggestion.",
                "action": "execute_proposal",
            },
            {
                "label": "Tell me more",
                "description": "Elaborate on the recommendation.",
                "action": "expand_to_proposal",
            },
            {
                "label": "Not now",
                "description": "Dismiss.",
                "action": "dismiss",
            },
        ],
        "recommendation": 0,
    },

    # ══════════════════════════════════════════════
    # T16: COUNTER-OFFER PRESENTATION
    # When M3 algorithm generates a counter-offer
    # ══════════════════════════════════════════════
    ("counter_offer", "WAR", "any"): {
        "text": (
            "Sire, I have modified the terms. {target_nation} may find these more acceptable:\n\n"
            "  {counter_summary}\n\n"
            "My assessment: this counter-offer has improved chances of acceptance."
        ),
        "options": [
            {
                "label": "Accept counter",
                "description": "Accept these modified terms.",
                "action": "accept_ai_proposal",
            },
            {
                "label": "Reject",
                "description": "Reject the entire negotiation.",
                "action": "reject_ai_proposal",
            },
        ],
        "recommendation": 0,
    },

    ("counter_offer", "PEACE", "any"): {
        "text": (
            "Sire, I have adjusted the terms for {target_nation}:\n\n"
            "  {counter_summary}\n\n"
            "These modified terms should be more palatable."
        ),
        "options": [
            {
                "label": "Accept counter",
                "description": "Accept the modified terms.",
                "action": "accept_ai_proposal",
            },
            {
                "label": "Reject",
                "description": "Reject entirely.",
                "action": "reject_ai_proposal",
            },
        ],
        "recommendation": 0,
    },

    # ══════════════════════════════════════════════
    # T17: CONFLICT ALERT — Alliance conflict detected
    # ══════════════════════════════════════════════
    ("conflict_alert", "any", "any"): {
        "text": (
            "Sire, a complication. Accepting this proposal would conflict with "
            "our existing obligations.\n\n"
            "{conflict_description}\n\n"
            "{target_nation} must choose which alliance to honor."
        ),
        "options": [
            {
                "label": "Accept anyway",
                "description": "Accept — the conflicting party must decide.",
                "action": "accept_with_conflict",
            },
            {
                "label": "Reject",
                "description": "Reject to avoid the conflict.",
                "action": "reject_ai_proposal",
            },
        ],
        "recommendation": 0,
    },

    # ══════════════════════════════════════════════
    # T18: PROPOSAL REJECTED RESPONSE
    # AI's response to player rejecting their proposal
    # ══════════════════════════════════════════════
    ("proposal_rejected", "WAR", "any"): {
        "text": (
            "{target_diplomat} receives your rejection with "
            "{rejection_reaction}. Relations with {target_nation} have cooled."
        ),
        "options": [
            {
                "label": "So be it",
                "description": "Dismiss.",
                "action": "dismiss",
            },
        ],
        "recommendation": 0,
    },

    ("proposal_rejected", "PEACE", "any"): {
        "text": (
            "{target_diplomat} accepts your decision with "
            "{rejection_reaction}. Relations have shifted."
        ),
        "options": [
            {
                "label": "Understood",
                "description": "Dismiss.",
                "action": "dismiss",
            },
        ],
        "recommendation": 0,
    },

    # ══════════════════════════════════════════════
    # T19: FEASIBILITY UPDATE
    # Updated feasibility after game state changes
    # ══════════════════════════════════════════════
    ("feasibility_update", "any", "any"): {
        "text": (
            "Sire, the diplomatic landscape has shifted. My previous assessment "
            "of {target_nation} requires revision.\n\n"
            "{updated_assessment}"
        ),
        "options": [
            {
                "label": "Pursue this",
                "description": "Act on the new assessment.",
                "action": "execute_proposal",
            },
            {
                "label": "Noted",
                "description": "Dismiss.",
                "action": "dismiss",
            },
        ],
        "recommendation": 0,
    },

    # ══════════════════════════════════════════════
    # T20: PROACTIVE DISPATCH ENTRY
    # Talleyrand's observation for Morning Dispatch
    # ══════════════════════════════════════════════
    ("proactive_suggestion", "any", "any"): {
        "text": (
            "A diplomatic observation, Sire: {observation}\n\n"
            "{suggested_action_text}"
        ),
        "options": [
            {
                "label": "Ask Talleyrand to elaborate",
                "description": "Open a diplomatic conversation.",
                "action": "elaborate",
            },
            {
                "label": "Dismiss",
                "description": "Noted.",
                "action": "dismiss",
            },
        ],
        "recommendation": 0,
    },
    # ══════════════════════════════════════════════════════════════
    # SESSION 6 TEMPLATES (T21-T27)
    # ══════════════════════════════════════════════════════════════

    # ══════════════════════════════════════════════
    # T21: PRE-PROPOSAL OBJECTION — MILD
    # Flavor text, no blocking — Talleyrand grumbles
    # ══════════════════════════════════════════════
    ("pre_proposal_objection_mild", "any", "any"): {
        "text": (
            "{objection_text}\n\n"
            "Nevertheless, I shall carry out your wishes, Sire."
        ),
        "options": [
            {
                "label": "Send as ordered",
                "description": "Dispatch Talleyrand with your original terms.",
                "action": "send",
            },
            {
                "label": "Reconsider",
                "description": "Perhaps Talleyrand has a point.",
                "action": "reconsider",
            },
        ],
        "recommendation": 0,
    },

    # ══════════════════════════════════════════════
    # T22: SABOTAGE CONFRONTATION
    # What was ordered vs what was delivered + reasoning
    # ══════════════════════════════════════════════
    ("sabotage_confrontation", "any", "any"): {
        "text": (
            "Berthier's agents report that the proposal delivered to "
            "{target_nation} was not precisely as you ordered.\n\n"
            "You ordered: {original_summary}\n"
            "Talleyrand sent: {modified_summary}\n\n"
            "Talleyrand: \"{sabotage_reasoning}\""
        ),
        "options": [
            {
                "label": "Confront",
                "description": "Authority +5, cooldown 5 turns.",
                "action": "confront_sabotage",
            },
            {
                "label": "Overlook",
                "description": "Authority -3. Talleyrand gains confidence.",
                "action": "overlook_sabotage",
            },
        ],
        "recommendation": 0,
    },

    # ══════════════════════════════════════════════
    # T23: SABOTAGE CONFRONTATION — OVERLOOK AFTERMATH
    # Confirmation after overlooking sabotage
    # ══════════════════════════════════════════════
    ("sabotage_confrontation_overlook", "any", "any"): {
        "text": (
            "You choose to overlook the discrepancy. Talleyrand inclines "
            "his head — a small acknowledgment that his judgment was trusted."
        ),
        "options": [
            {
                "label": "Understood",
                "description": "Dismiss.",
                "action": "dismiss",
            },
        ],
        "recommendation": 0,
    },

    # ══════════════════════════════════════════════
    # T24: ENEMY RESPONSE — HAWK (Castlereagh, Hardenberg)
    # Grudging accept, demanding counter, contemptuous reject
    # ══════════════════════════════════════════════
    ("enemy_response_hawk", "any", "accept"): {
        "text": (
            "{target_diplomat} receives your terms with barely concealed displeasure. "
            "\"We accept — for now. Do not mistake pragmatism for weakness.\""
        ),
        "options": [
            {"label": "Noted", "description": "Dismiss.", "action": "dismiss"},
        ],
        "recommendation": 0,
    },
    ("enemy_response_hawk", "any", "counter"): {
        "text": (
            "{target_diplomat} slams the table. \"These terms are insulting. "
            "Here is what {target_nation} will accept — and nothing less.\""
        ),
        "options": [
            {"label": "Consider counter", "description": "Review the counter-offer.", "action": "review_counter"},
            {"label": "Reject", "description": "Refuse.", "action": "reject_ai_proposal"},
        ],
        "recommendation": 0,
    },
    ("enemy_response_hawk", "any", "reject"): {
        "text": (
            "{target_diplomat}'s contempt is palpable. \"You waste our time "
            "with this? {target_nation} will remember this insult.\""
        ),
        "options": [
            {"label": "So be it", "description": "Dismiss.", "action": "dismiss"},
        ],
        "recommendation": 0,
    },

    # ══════════════════════════════════════════════
    # T25: ENEMY RESPONSE — SCHEMER (Metternich)
    # Calculating accept, probing counter, deflecting reject
    # ══════════════════════════════════════════════
    ("enemy_response_schemer", "any", "accept"): {
        "text": (
            "{target_diplomat} smiles — never a reassuring sign. "
            "\"An acceptable arrangement. {target_nation} agrees... with interest.\""
        ),
        "options": [
            {"label": "Noted", "description": "Dismiss.", "action": "dismiss"},
        ],
        "recommendation": 0,
    },
    ("enemy_response_schemer", "any", "counter"): {
        "text": (
            "{target_diplomat} examines the terms at length. \"Interesting. "
            "But perhaps we could adjust... here, and here. "
            "A small modification that benefits us both.\""
        ),
        "options": [
            {"label": "Consider counter", "description": "Review the counter-offer.", "action": "review_counter"},
            {"label": "Reject", "description": "Refuse.", "action": "reject_ai_proposal"},
        ],
        "recommendation": 0,
    },
    ("enemy_response_schemer", "any", "reject"): {
        "text": (
            "{target_diplomat} merely raises an eyebrow. \"A pity. "
            "But doors that close today may open tomorrow. "
            "{target_nation} is patient.\""
        ),
        "options": [
            {"label": "Understood", "description": "Dismiss.", "action": "dismiss"},
        ],
        "recommendation": 0,
    },

    # ══════════════════════════════════════════════
    # T26: ENEMY RESPONSE — DOVE (Einsiedel / future diplomats)
    # Grateful accept, apologetic counter, regretful reject
    # ══════════════════════════════════════════════
    ("enemy_response_dove", "any", "accept"): {
        "text": (
            "{target_diplomat} visibly relaxes. \"This is most welcome. "
            "{target_nation} accepts with gratitude and hopes for lasting peace.\""
        ),
        "options": [
            {"label": "Good", "description": "Dismiss.", "action": "dismiss"},
        ],
        "recommendation": 0,
    },
    ("enemy_response_dove", "any", "counter"): {
        "text": (
            "{target_diplomat} wrings his hands. \"We appreciate the gesture, "
            "truly. But our court requires... adjustments. "
            "Please, consider this modest counter-proposal.\""
        ),
        "options": [
            {"label": "Consider counter", "description": "Review the counter-offer.", "action": "review_counter"},
            {"label": "Reject", "description": "Refuse.", "action": "reject_ai_proposal"},
        ],
        "recommendation": 0,
    },
    ("enemy_response_dove", "any", "reject"): {
        "text": (
            "{target_diplomat} looks pained. \"I am sorry, truly. "
            "{target_nation} cannot accept these terms. "
            "Perhaps... in time... we might try again?\""
        ),
        "options": [
            {"label": "Perhaps", "description": "Dismiss.", "action": "dismiss"},
        ],
        "recommendation": 0,
    },

    # ══════════════════════════════════════════════
    # T27: ENEMY RESPONSE — LOYALIST (generic formal)
    # Formal accept, formal counter, formal reject
    # ══════════════════════════════════════════════
    ("enemy_response_loyalist", "any", "accept"): {
        "text": (
            "{target_diplomat} delivers the response formally. "
            "\"{target_nation} accepts the terms as presented.\""
        ),
        "options": [
            {"label": "Noted", "description": "Dismiss.", "action": "dismiss"},
        ],
        "recommendation": 0,
    },
    ("enemy_response_loyalist", "any", "counter"): {
        "text": (
            "{target_diplomat} presents the response with precision. "
            "\"{target_nation} proposes the following modifications to the terms.\""
        ),
        "options": [
            {"label": "Consider counter", "description": "Review the counter-offer.", "action": "review_counter"},
            {"label": "Reject", "description": "Refuse.", "action": "reject_ai_proposal"},
        ],
        "recommendation": 0,
    },
    ("enemy_response_loyalist", "any", "reject"): {
        "text": (
            "{target_diplomat} delivers the rejection without emotion. "
            "\"{target_nation} declines the proposed terms.\""
        ),
        "options": [
            {"label": "Understood", "description": "Dismiss.", "action": "dismiss"},
        ],
        "recommendation": 0,
    },
    "settlement_open_war_detail_recovery_talleyrand": (
        "Sire, I will keep the draft intact and return us to the live war "
        "detail for {war_label}."
    ),
    "settlement_open_history_recovery_talleyrand": (
        "Sire, this war has ended; the settlement record now belongs in "
        "the diplomatic ledger."
    ),
    "settlement_no_alternative_route_chancery": (
        "This settlement cannot currently be recovered from the existing "
        "surfaces. Close the review and reassess the war next turn."
    ),
}

# ═══════ COALITION TEMPLATES (T28-T34, Session 7) ═══════
# Template categories for coalition events. These use coalition-specific slot variables.

COALITION_TEMPLATES = {
    # T28: Coalition murmur (threat 40-59)
    "coalition_murmur": {
        "text": (
            "Sire, at threat level {threat_level}, the courts of {hostile_nations} "
            "grow restless. Our recent successes alarm them."
        ),
        "priority": "normal",
    },
    # T29: Coalition brewing (threat 60+)
    "coalition_brewing": {
        "text": (
            "Your Majesty, I must speak with the utmost urgency. {qualifying_nations} "
            "are forming a coalition against us. We have {turns_remaining} turns to prevent it. "
            "Shall I approach the weakest member with terms?"
        ),
        "priority": "high",
    },
    # T30: Coalition declared
    "coalition_declared": {
        "text": (
            "The {coalition_name} has declared against us. {leader} leads "
            "{member_list}. All of Europe stands against you, Sire."
        ),
        "priority": "critical",
    },
    # T31: Coalition member weakening
    "coalition_member_weak": {
        "text": (
            "{nation}'s resolve is faltering. Their war exhaustion has reached "
            "{war_exhaustion}. They may be amenable to separate terms."
        ),
        "priority": "normal",
    },
    # T32: Coalition split advice
    "coalition_advice_split": {
        "text": (
            "I recommend approaching {target_nation} with generous peace terms. "
            "They are the weakest link in the coalition. A separate peace would "
            "fracture the alliance."
        ),
        "priority": "normal",
    },
    # T33: Coalition dissolved
    "coalition_dissolved": {
        "text": (
            "The {coalition_name} has collapsed. A moment of respite, Sire. "
            "But I counsel moderation — harsh demands breed the next coalition."
        ),
        "priority": "normal",
    },
    # T34: Coalition harsh warning
    "coalition_harsh_warning": {
        "text": (
            "Sire, these terms will add {threat_increase} to our threat level. "
            "At the current rate, another coalition may form within turns. "
            "I urge restraint."
        ),
        "priority": "normal",
    },
}


SETTLEMENT_VOICE_TEMPLATES: Dict[str, str] = {
    "settlement_advisory_common_peace_talleyrand": (
        "Sire, the settlement of {war_label} is not a curtain call; it is an "
        "accounting. {standing_summary} must be read beside {contribution_summary}, "
        "and the largest political cost remains {top_blocker}."
    ),
    "settlement_advisory_defensive_talleyrand": (
        "Sire, a defensive peace is judged by what it preserves. Returning "
        "{restored_claim} steadies the coalition, while {limited_concession} "
        "buys quiet without dressing necessity as conquest."
    ),
    "settlement_acceptance_castlereagh": (
        "His Majesty's Government accepts the settlement of {war_label}. "
        "London records the terms and reserves its judgment on the consequences."
    ),
    "settlement_acceptance_hardenberg": (
        "Prussia accepts the settlement of {war_label}. Hardenberg notes what "
        "has been conceded, and what honor will require us to remember."
    ),
    "settlement_acceptance_metternich": (
        "Vienna accepts the settlement of {war_label}. Metternich observes that "
        "the arrangement is sufficient for today, which is not the same as final."
    ),
    "settlement_acceptance_einsiedel": (
        "Saxony accepts the settlement of {war_label}, respectfully and with "
        "relief. Einsiedel asks only that small courts may now breathe."
    ),
    "settlement_rejection_castlereagh": (
        "London cannot accept the settlement of {war_label}. The obstacle is "
        "{top_blocker}; His Majesty's Government will not pretend otherwise."
    ),
    "settlement_rejection_hardenberg": (
        "Prussia rejects the settlement of {war_label}. {top_blocker} is not a "
        "detail to be filed away; it is an insult to Prussian standing."
    ),
    "settlement_rejection_metternich": (
        "Vienna declines the settlement of {war_label}. The difficulty, if one "
        "must name it plainly, is {top_blocker}; Austria prefers clarity before ink."
    ),
    "settlement_rejection_einsiedel": (
        "Saxony cannot accept the settlement of {war_label}. Einsiedel begs "
        "France to understand that {top_blocker} leaves us no safe answer."
    ),
    "settlement_sold_out_by_leader_castlereagh": (
        "London observes that {leader} purchased peace with {victim}. Such an "
        "arrangement will be remembered in the next coalition."
    ),
    "settlement_sold_out_by_leader_hardenberg": (
        "Hardenberg names the matter plainly: {leader} sold out {victim}. "
        "Prussia does not forget who treats an ally as payment."
    ),
    "settlement_sold_out_by_leader_metternich": (
        "Vienna notes that {leader} found {victim} a convenient price. "
        "Metternich will adjust the ledger accordingly."
    ),
    "settlement_sold_out_by_leader_einsiedel": (
        "Einsiedel records, with regret, that {leader} has left {victim} to bear "
        "the cost. Small courts understand that lesson too well."
    ),
    "settlement_rewarded_ally_castlereagh": (
        "London acknowledges that {beneficiary} received {reward}. The reward "
        "is material; the obligation it creates is political."
    ),
    "settlement_rewarded_ally_hardenberg": (
        "Hardenberg accepts {reward} for {beneficiary} as recognition, not charity. "
        "Prussia values a settlement that honors contribution."
    ),
    "settlement_rewarded_ally_metternich": (
        "Metternich observes that {beneficiary} has been granted {reward}. "
        "A favor so precisely placed is rarely accidental."
    ),
    "settlement_rewarded_ally_einsiedel": (
        "Einsiedel thanks France for {reward} to {beneficiary}. It is a modest "
        "security perhaps, but for Saxony security is never modest."
    ),
    "settlement_excluded_ally_castlereagh": (
        "London notes that {excluded_ally} contributed {contribution_summary} "
        "and received no seat in the settlement. The omission is legible."
    ),
    "settlement_excluded_ally_hardenberg": (
        "Hardenberg will not dress this as oversight. {excluded_ally} gave "
        "{contribution_summary}, and the settlement answered with silence."
    ),
    "settlement_excluded_ally_metternich": (
        "Vienna has noticed that {excluded_ally}'s {contribution_summary} did "
        "not survive into the articles. Such absences have weight."
    ),
    "settlement_excluded_ally_einsiedel": (
        "Einsiedel asks, respectfully, how {excluded_ally} should explain "
        "{contribution_summary} when the treaty grants nothing in return."
    ),
    "settlement_advisory_common_peace_serial_peace_weapon": (
        "Sire, peeling {departing_enemy} from {war_label} weakens {remaining_leader}, "
        "but it also teaches the remaining courts that separate peace has a price."
    ),
    # Settlement aftermath digest (spec §11.6 line 1288). Voiced in
    # Talleyrand register so the rolled-up overflow line keeps the
    # settlement family's narrative voice rather than reading as system
    # log text. Spec §16.1 line 1602.
    "settlement_aftermath_digest_talleyrand": (
        "Sire, {hidden_count} further courts have entered the {war_label} "
        "settlement into their ledgers — quieter reactions, but each one "
        "remembered."
    ),
    # SC-19 settlement voice families (Settlement UI Cleanup G2-Slice-5).
    # Each family is bound to a specific trigger and surface; using any
    # of these on the wrong surface fails the SC-19 row's required test.
    #
    # Live review heading — replaces the raw verdict f-string at the
    # settlement_confirm popup heading. Talleyrand voice for outgoing
    # review where France authored the package.
    "settlement_review_heading_talleyrand": (
        "Sire, the settlement of {war_label} stands ready for ratification. "
        "Acceptance reads as {acceptance_band}; the largest pressure remains "
        "{top_blocker}."
    ),
    # Foreign-court / observer settlement voice for fog-visible
    # foreign-only settlements where France is neither proposer nor
    # accepting member. SC-19 amendment: chancery voice, not Talleyrand
    # authorship.
    "settlement_observed_foreign_court_chancery": (
        "Foreign Office records the settlement of {war_label}. The court of "
        "{accepting_leader} reviews the terms; we observe rather than author."
    ),
    # Blocked ratification banner — shown when fresh acceptance verdict
    # is reject/blocked or hard stops exist and the Ratify Settlement
    # option is absent from the dialogue. SC-15b/SC-3 amendment: must
    # not use "Will they accept?" framing.
    "settlement_blocked_for_ratification_talleyrand": (
        "Sire, the settlement of {war_label} cannot be ratified now: "
        "{top_blocker}. Revise terms or stand down before pressing further."
    ),
    # Rescore-after-staging banner — fresh ratification scoring changed
    # an accepted staged package into rejected/below-threshold/hard-stop.
    "settlement_rescored_after_staging_talleyrand": (
        "Sire, the situation has shifted since this settlement was staged. "
        "Acceptance now reads {acceptance_band}; review the terms again "
        "before ratifying."
    ),
    # Discard-confirm prompt (SC-2) — Back Out from a non-empty authored
    # draft asks the player to confirm before clearing terms.
    "settlement_discard_confirm_talleyrand": (
        "Sire, the authored terms for {war_label} will be discarded if we "
        "back out now. Shall I keep the draft, or strike it from the table?"
    ),
    # Cross-war collision (SC-26) — a second settlement entry was
    # attempted while a different war already holds the active dialogue.
    "settlement_collision_active_review_talleyrand": (
        "Sire, the settlement of {active_war_label} is already on the table; "
        "resolve it before opening a separate review for {blocked_war_label}."
    ),
    # Reopen-cap exhausted (SC-14b) — attempt 4 for the same
    # (war_id, turn) — pin the player to the choose-from-war-detail
    # escape rather than another reopen loop.
    "settlement_scope_replace_confirm_talleyrand": (
        "Sire, {war_label} already has a settlement draft for {current_scope}. "
        "Shall I replace it with the new scope, {incoming_scope}, or keep the "
        "current draft?"
    ),
    "settlement_reopen_cap_exhausted_talleyrand": (
        "Sire, this settlement of {war_label} cannot be reopened again — "
        "choose the war from war detail and stage afresh."
    ),
    # SC-29 / G2-Slice-7 pair-scoped peace substitute CTAs. The rejected
    # settlement popup may surface these only when the selected target
    # pair is eligible under `evaluate_pair_peace_substitute_eligibility`.
    # Talleyrand frames the substitute as a pair-scoped fallback, not as a
    # repeated settlement attempt.
    "settlement_seek_bilateral_peace_instead_talleyrand": (
        "Sire, since the larger settlement of {war_label} cannot ratify, "
        "I shall open a separate bilateral peace with {target_nation}; "
        "the other hostile pairs remain at war until they are addressed "
        "in turn."
    ),
    "settlement_seek_armistice_instead_talleyrand": (
        "Sire, an armistice with {target_nation} buys quiet on that "
        "front while {war_label} continues elsewhere; it does not end "
        "the war, but it does end the bleeding."
    ),
    # G4F-8 (Gate-4 smoke): the pair substitute is no longer a one-click
    # trapdoor — Talleyrand states what leaving the joint settlement MEANS
    # (the other courts fight on; the drafted terms for the target travel
    # into the new talks) and asks before he moves.
    "settlement_pair_substitute_confirm_talleyrand": (
        "Sire, this sets aside the joint settlement of {war_label} to "
        "treat with {target_nation} alone — every other court keeps its "
        "war. Your drafted terms for {target_nation} travel with me. "
        "Shall I proceed?"
    ),
    # SC-31 / G2-Slice-8 Voice Bible §16.1 surrender / dependency families.
    # Surrender preset is a structured, labeled action — Talleyrand frames
    # it as deliberate concession, not collapse — and the foreign-court
    # reactions answer the dependency consequence (loss of sovereignty,
    # lord assimilation, Continental System pull) rather than treating it
    # as a generic peace acceptance.
    "settlement_surrender_preset_authored_talleyrand": (
        "Sire, the surrender draft for {war_label} is set: peace, and "
        "{vassal_kind} of {proposer_leader} under {accepting_leader}. "
        "It costs us our sovereignty; it ends the war."
    ),
    "settlement_surrender_preset_blocked_talleyrand": (
        "Sire, surrender terms cannot be drafted now: {top_blocker}. "
        "Author concessions or hold the line until the field changes."
    ),
    "settlement_dependency_ratified_talleyrand": (
        "Sire, the settlement of {war_label} binds {vassal_nation} "
        "to {lord_nation} as a {vassal_kind}. The crown survives; "
        "the court answers to {lord_nation} now."
    ),
    "settlement_dependency_acceptance_castlereagh": (
        "His Majesty's Government accepts the settlement of {war_label} "
        "with {vassal_nation} under {lord_nation}. London notes the "
        "submission and will measure {lord_nation} by what it does next."
    ),
    "settlement_dependency_acceptance_hardenberg": (
        "Prussia accepts the settlement of {war_label}. Hardenberg records "
        "that {vassal_nation} now answers to {lord_nation}, and that "
        "Prussian standing must adjust accordingly."
    ),
    "settlement_dependency_acceptance_metternich": (
        "Vienna accepts the settlement of {war_label}. Metternich "
        "observes that {vassal_nation}'s submission to {lord_nation} "
        "rearranges Europe quietly; quiet does not mean settled."
    ),
    "settlement_dependency_acceptance_einsiedel": (
        "Saxony accepts the settlement of {war_label}. Einsiedel hopes, "
        "with care, that {lord_nation} remembers small courts when "
        "{vassal_nation} kneels."
    ),
    "settlement_dependency_rejection_castlereagh": (
        "London cannot accept the settlement of {war_label}. The "
        "subjection of {vassal_nation} to {lord_nation} is more than "
        "a treaty matter; {top_blocker} forbids it."
    ),
    "settlement_dependency_rejection_hardenberg": (
        "Prussia rejects the settlement of {war_label}. Hardenberg "
        "names the obstacle plainly: {top_blocker}. {vassal_nation} "
        "cannot be handed to {lord_nation} under those circumstances."
    ),
    "settlement_dependency_rejection_metternich": (
        "Vienna declines the settlement of {war_label}. The difficulty "
        "is {top_blocker}; Austria will not consent to {vassal_nation} "
        "becoming a vassal of {lord_nation} on those terms."
    ),
    "settlement_dependency_rejection_einsiedel": (
        "Saxony cannot accept the settlement of {war_label}. Einsiedel "
        "begs {lord_nation} to understand that {top_blocker} leaves "
        "{vassal_nation} no safe answer."
    ),
    "settlement_liberation_ratified_talleyrand": (
        "Sire, the settlement of {war_label} frees {vassal_nation} from "
        "{former_lord} into a defensive alliance with {liberator}. The "
        "court of {vassal_nation} will remember who opened the door."
    ),
    # SC-33 / G2-Slice-9 recurring gold payment Voice Bible families.
    # Authored / ratified / completed split mirrors the surrender preset
    # authored / ratified pattern so the player hears a deliberate
    # framing when the obligation is drafted, when it ratifies, and
    # when it concludes.
    "settlement_recurring_gold_authored_talleyrand": (
        "Sire, the draft commits {payer} to {amount_per_turn} gold per "
        "turn to {recipient} for {turns} turns ({projected_total} gold "
        "in total). Recurring payments steady the peace; they also "
        "tie the treasury for years."
    ),
    "settlement_recurring_gold_ratified_talleyrand": (
        "Sire, the settlement of {war_label} obliges {payer} to send "
        "{amount_per_turn} gold per turn to {recipient} for {turns} "
        "turns. The first installment leaves the treasury next turn."
    ),
    "settlement_recurring_gold_completed_talleyrand": (
        "Sire, the recurring obligation from {payer} to {recipient} "
        "for {war_label} is fulfilled — {total_amount} gold has changed "
        "hands. The clause closes itself."
    ),
    # SC-5 reversal / Slice G1 commit 2 incoming-offer Voice Bible §16.1
    # families. Talleyrand frames the offer for the player's reading;
    # each foreign court's voice is what the proposer-side leader puts
    # on the dispatch. The committed copy distinguishes incoming
    # acceptance framing ("they are asking for") from outgoing review
    # framing ("we are asking for").
    "settlement_incoming_offer_arrival_talleyrand": (
        "Sire, {proposer_leader} has dispatched a settlement of "
        "{war_label}. They ask {amount} gold to close the war; the "
        "table is theirs to set, the signature is ours to give or "
        "withhold."
    ),
    "settlement_incoming_offer_arrival_castlereagh": (
        "His Majesty's Government offers terms for {war_label}. London "
        "asks {amount} gold and a return to peace; the price is set, "
        "and London is not in the habit of revising figures lightly."
    ),
    "settlement_incoming_offer_arrival_hardenberg": (
        "Prussia proposes a settlement of {war_label}. Hardenberg names "
        "{amount} gold as the close; what Prussia gives by signing is "
        "quiet, and what Prussia keeps is the lesson."
    ),
    "settlement_incoming_offer_arrival_metternich": (
        "Vienna submits terms for {war_label}. Metternich asks {amount} "
        "gold; the figure is modest by Vienna's reckoning and the "
        "alternative is another season of campaign."
    ),
    "settlement_incoming_offer_arrival_einsiedel": (
        "Saxony forwards a settlement of {war_label}. Einsiedel asks "
        "{amount} gold, respectfully — small courts cannot afford long "
        "wars, and the offer is shaped accordingly."
    ),
    "settlement_incoming_offer_arrival_chancery": (
        "The chancery of {proposer_leader} has forwarded a settlement "
        "of {war_label}. The terms ask {amount} gold; the court awaits "
        "France's answer."
    ),
    "settlement_ally_petition_request_open_settlement_castlereagh": (
        "London asks to be heard before {war_label} closes. "
        "His Majesty's Government still presses {claim_region} in "
        "{claim_war_label}, and expects France not to settle around it."
    ),
    "settlement_ally_petition_request_open_settlement_hardenberg": (
        "Hardenberg asks France to keep Prussia's claim in view before "
        "{war_label} is closed. {claim_region} remains before "
        "{target_enemy}, and silence would read as abandonment."
    ),
    "settlement_ally_petition_request_open_settlement_metternich": (
        "Metternich requests that Vienna's claim to {claim_region} be "
        "consulted before {war_label} is sealed. A settlement that "
        "forgets {claim_war_label} will not be forgotten in Vienna."
    ),
    "settlement_ally_petition_request_open_settlement_einsiedel": (
        "Einsiedel asks France not to close {war_label} while Saxony's "
        "claim to {claim_region} in {claim_war_label} remains unsettled."
    ),
    "settlement_ally_petition_request_open_settlement_chancery": (
        "The chancery of {ally_nation} asks to be heard before "
        "{war_label} is closed. Its claim to {claim_region} remains "
        "unsettled in {claim_war_label}."
    ),
    "settlement_ally_petition_warn_against_sellout_castlereagh": (
        "London warns that {ally_nation}'s claim to {claim_region} "
        "against {target_enemy} is absent from {war_label}. A treaty can "
        "sell out an ally without naming the price."
    ),
    "settlement_ally_petition_warn_against_sellout_hardenberg": (
        "Hardenberg warns that {claim_region} against {target_enemy} has "
        "vanished from {war_label}. Prussia will not call that omission "
        "a clerical detail."
    ),
    "settlement_ally_petition_warn_against_sellout_metternich": (
        "Metternich observes that {ally_nation}'s claim to {claim_region} "
        "has no place in {war_label}. Vienna recognizes an ally being "
        "set aside even when the article is politely drafted."
    ),
    "settlement_ally_petition_warn_against_sellout_einsiedel": (
        "Einsiedel warns, respectfully, that Saxony's claim to "
        "{claim_region} against {target_enemy} is missing from "
        "{war_label}; small courts know when peace is bought with them."
    ),
    "settlement_ally_petition_warn_against_sellout_chancery": (
        "The chancery of {ally_nation} warns that its claim to "
        "{claim_region} against {target_enemy} is absent from "
        "{war_label}."
    ),
    # Slice H (approved July 3, 2026) — request_reward_or_restoration:
    # a formal claim with the basis always named (§13.4 rule).
    "settlement_ally_petition_request_reward_or_restoration_castlereagh": (
        "London presses its claim to {claim_region} at this table. "
        "{basis_display} His Majesty's Government expects the settlement "
        "of {war_label} to reflect it."
    ),
    "settlement_ally_petition_request_reward_or_restoration_hardenberg": (
        "Hardenberg lays Prussia's claim to {claim_region} before France. "
        "{basis_display} A settlement that rewards its authors should "
        "remember its allies."
    ),
    "settlement_ally_petition_request_reward_or_restoration_metternich": (
        "Metternich enters Vienna's claim to {claim_region} in the "
        "protocol. {basis_display} Austria's arms have earned a line in "
        "this settlement."
    ),
    "settlement_ally_petition_request_reward_or_restoration_einsiedel": (
        "Einsiedel begs leave to name Saxony's claim to {claim_region}. "
        "{basis_display} Small courts ask plainly, Sire, or not at all."
    ),
    "settlement_ally_petition_request_reward_or_restoration_chancery": (
        "The chancery of {ally_nation} petitions for {claim_region} in "
        "the settlement of {war_label}. {basis_display}"
    ),
    # Slice H — demand_bargain_honor: wounded honor, the promise quoted.
    "settlement_ally_petition_demand_bargain_honor_castlereagh": (
        "At {created_turn_label}, France pledged its claim on "
        "{claim_region} to secure our arms. London asks whether that "
        "pledge survives this draft of {war_label}."
    ),
    "settlement_ally_petition_demand_bargain_honor_hardenberg": (
        "At {created_turn_label}, Sire, France pledged its claim on "
        "{claim_region} to secure our arms. Hardenberg asks France to "
        "read this draft beside that pledge."
    ),
    "settlement_ally_petition_demand_bargain_honor_metternich": (
        "Metternich recalls, with precision, the pledge of "
        "{created_turn_label}: France's claim on {claim_region}. The "
        "draft before us unmakes it."
    ),
    "settlement_ally_petition_demand_bargain_honor_einsiedel": (
        "Einsiedel must speak of the pledge of {created_turn_label} — "
        "{claim_region}, promised while Saxony marched. This draft "
        "forgets it."
    ),
    "settlement_ally_petition_demand_bargain_honor_chancery": (
        "The chancery of {ally_nation} recalls France's pledge of "
        "{created_turn_label} on {claim_region}; the staged terms put "
        "it at risk."
    ),
    # Slice H — grant / decline / honor acknowledgments per family (§7).
    "settlement_ally_petition_granted_castlereagh": (
        "London takes note, and will remember which ally France chose to "
        "be. The claim on {claim_region} stands in the treaty."
    ),
    "settlement_ally_petition_granted_hardenberg": (
        "Hardenberg thanks France plainly: {claim_region} is written in. "
        "Prussia marches easier beside a patron who pays."
    ),
    "settlement_ally_petition_granted_metternich": (
        "Vienna acknowledges the grant of {claim_region}. Metternich "
        "will say so where it matters."
    ),
    "settlement_ally_petition_granted_einsiedel": (
        "Einsiedel conveys Saxony's gratitude for {claim_region} — a "
        "small court does not forget."
    ),
    "settlement_ally_petition_granted_chancery": (
        "The chancery of {ally_nation} acknowledges the grant of "
        "{claim_region} with gratitude."
    ),
    "settlement_ally_petition_declined_castlereagh": (
        "London notes the refusal without surprise, and files it where "
        "such answers are kept."
    ),
    "settlement_ally_petition_declined_hardenberg": (
        "Hardenberg withdraws the petition. Prussia has asked once "
        "already, Sire; it will not ask twice this season."
    ),
    "settlement_ally_petition_declined_metternich": (
        "Metternich records the refusal in Vienna's ledger — "
        "courteously, and permanently."
    ),
    "settlement_ally_petition_declined_einsiedel": (
        "Einsiedel bows and withdraws; Saxony hears the answer clearly "
        "enough."
    ),
    "settlement_ally_petition_declined_chancery": (
        "The chancery of {ally_nation} records France's refusal in cool "
        "terms."
    ),
    "settlement_ally_petition_honored_castlereagh": (
        "London withdraws the protest: the pledge on {claim_region} "
        "stands, and so does British confidence in it."
    ),
    "settlement_ally_petition_honored_hardenberg": (
        "Hardenberg is satisfied: the pledge on {claim_region} survives "
        "the draft, and Prussia's arms stay warm."
    ),
    "settlement_ally_petition_honored_metternich": (
        "Metternich amends the protocol: the pledge on {claim_region} is "
        "kept. Vienna prefers a France that keeps its word."
    ),
    "settlement_ally_petition_honored_einsiedel": (
        "Einsiedel thanks France: the pledge on {claim_region} stands, "
        "and Saxony with it."
    ),
    "settlement_ally_petition_honored_chancery": (
        "The chancery of {ally_nation} acknowledges that France's pledge "
        "on {claim_region} stands."
    ),
    # Slice H — the click-time lapse notice (G1 re-run pattern).
    "settlement_ally_petition_lapsed_talleyrand": (
        "Sire, the table has moved since {ally_nation} petitioned — the "
        "ask can no longer be granted as it was made. If they still "
        "hunger, they will ask again."
    ),
    "settlement_ally_petition_talleyrand": (
        "Sire, {ally_nation}'s petition is advisory. It records the claim "
        "to {claim_region} without blocking ratification."
    ),
    # Request Revision is the accepting-side counter authoring route.
    # Talleyrand explains that the offered package is laid out on OUR
    # settlement table (the guided per-court PROPOSE surface — Guided
    # Terms §5 copy retarget, GT-Slice-V) so the player revises before
    # sending a counter; this must NOT reuse outgoing "Revise Terms"
    # framing, and it no longer references opening an editor.
    "settlement_incoming_offer_request_revision_talleyrand": (
        "Sire, I shall lay the offered terms for {war_label} on our own "
        "table, court by court. We answer the dispatch from "
        "{proposer_leader} with a counter draft, not silence."
    ),
    # Blocked recovery for the accepting-side review (player accepted the
    # offer but it cannot ratify in its current form). Talleyrand names
    # the blocker and points the player at Request Revision rather than
    # outgoing Revise Terms copy.
    "settlement_incoming_offer_blocked_recovery_talleyrand": (
        "Sire, the offer from {proposer_leader} cannot ratify as it "
        "stands: {top_blocker}. Request a revision and we answer with "
        "our own draft instead of refusing without a reply."
    ),
    # Cross-court observer copy when a non-French court learns that a
    # settlement was blocked. Spec §SC-19 amendment + §SC-30 Voice Bible
    # cross-court rule require chancery voice (not Talleyrand) so the
    # observed-from-outside reading does not pretend French authorship.
    "settlement_blocked_for_ratification_observer": (
        "The chancery records the draft of {war_label} as blocked. "
        "{top_blocker} leaves no court with signatures to exchange."
    ),
    # SC-30 / Slice G1 — the Request Terms lifecycle voice family
    # (Voice Bible §16.1). The GRANT beat deliberately has no template of
    # its own: a granted request produces a real incoming offer, which
    # speaks through the existing `settlement_incoming_offer_arrival_*`
    # family. The refusal is spoken FOR the answering court by its named
    # diplomat / chancery (never anonymous — §16.1a resolver rule).
    "settlement_request_terms_sent_talleyrand": (
        "I shall ask {court}'s chancery to name its terms for {war_label}, "
        "Sire. Expect an answer with the next dispatches."
    ),
    "settlement_request_terms_refused_court": (
        "{speaker} answers for {court}: the court sees no need to name "
        "terms while the war runs in its favor. The request may be "
        "renewed when the field has spoken again."
    ),
    "settlement_request_terms_lapsed_talleyrand": (
        "Our request for terms on {war_label} has lapsed, Sire — the war "
        "has changed shape since we asked."
    ),
    # G2-Slice-W1 white-peace heading families. Authored as part of the
    # May 24, 2026 audit punch list Tier 2: `build_settlement_confirm_dialogue`
    # already calls `resolve_settlement_voice_line` for these two keys at
    # the white_peace branches of the heading text logic, but the templates
    # were missing — the resolver therefore returned empty and the popup
    # fell through to inline f-string fallbacks. Authoring them here brings
    # the white-peace heading under Voice Bible §16.1 alongside the
    # blocked / ratifiable / observer variants above.
    "settlement_white_peace_heading_talleyrand": (
        "Sire, the white peace for {war_label} is ready: no terms exchanged, "
        "no map redrawn — only the war ends. Ratify and the field falls quiet."
    ),
    "settlement_white_peace_blocked_talleyrand": (
        "Sire, a white peace for {war_label} cannot be sealed as it stands: "
        "{top_blocker}. Author terms or hold until the field shifts."
    ),
    # Losing-side concession-baseline Voice Bible families. Authored as
    # part of the May 24, 2026 audit punch list Tier 2 so the concession
    # baseline reasoning the popup already renders is registered Voice
    # Bible copy rather than a hard-coded f-string in
    # `_format_concession_reasoning(...)`. `{summary}` is the formatted
    # one-line concession action the helper already constructs ("pay X
    # gold", "cede Y", or both joined). `{accepting_leader}` echoes the
    # foreign-court target so the line reads as deliberate authoring
    # rather than as a generic acceptance hint.
    "settlement_concession_authored_talleyrand": (
        "Sire, the concession draft — {summary} — would lift acceptance "
        "toward {accepting_leader}. It is what the field asks of us."
    ),
    # Losing-side pressure-explanation family. Authored alongside the
    # concession-baseline family so the dialogue can surface a Talleyrand
    # reading of why the player is on the losing side (top negative
    # pressure component + accepting leader), not only the baseline
    # reasoning. Surfaced on the dialogue as `losing_side_pressure_voice`
    # when `losing_for_concession_baseline=True` and resolved with
    # `{war_label}`, `{top_pressure_label}`, and `{accepting_leader}`.
    "settlement_losing_side_pressure_explained_talleyrand": (
        "Sire, the pressure on {war_label} reads against us — {top_pressure_label} "
        "is the loudest blocker, and {accepting_leader} is the court whose "
        "acceptance must shift before terms move."
    ),
    # ───────────────────────────────────────────────────────────────────
    # Re-front Slice 1 / REFRONT-V — multi-court settlement-table voice
    # (closes Voice Bible gap B4). Each covered court's line is spoken by
    # its NAMED diplomat (resolved through `resolve_named_diplomat` /
    # chancery fallback — no anonymous beats), and Talleyrand narrates the
    # table and flags the binding constraint. Per cleanup SC-32 D5, NONE of
    # this committed copy uses "conference", "congress", or "veto".
    # ───────────────────────────────────────────────────────────────────
    "settlement_multi_court_court_will_sign": (
        "{speaker} signals that {court} will sign the settlement of {war_label}."
    ),
    "settlement_multi_court_court_leaning": (
        "{speaker} says {court} leans toward terms, though {top_blocker} still "
        "gives the court pause."
    ),
    "settlement_multi_court_court_holds_out": (
        "{speaker} holds {court} back from the table — {top_blocker} is the "
        "sticking point before they will sign."
    ),
    "settlement_multi_court_court_hard_stop": (
        "{speaker} has no standing to settle {court} here — there is no live "
        "quarrel between us to close."
    ),
    "settlement_multi_court_table_talleyrand": (
        "Sire, this settlement of {war_label} seats {court_count} courts at the "
        "table. {binding_constraint}"
    ),
    "settlement_multi_court_all_carry_talleyrand": (
        "Every court at the table will sign; the settlement of {war_label} carries."
    ),
    "settlement_multi_court_holdout_blocks_talleyrand": (
        "Sire, {holdout_court} will not sign; the settlement of {war_label} cannot "
        "be ratified until that court is eased toward terms or dropped to fight on."
    ),
    # ───────────────────────────────────────────────────────────────────
    # PF-1 / DC-2 (Gate-4 pre-flight audit) — the binding-constraint voice.
    # Spoken in the PROPOSE advisory slot when the treasury can no longer
    # raise the gold offer to every concede-direction holdout (the
    # solvency ceiling caps reachable acceptance): Talleyrand names the
    # constraint instead of counselling dials that would only fail.
    # France in 1813 could not buy peace from everyone; the game says so.
    # ───────────────────────────────────────────────────────────────────
    "settlement_budget_bound_constraint_talleyrand": (
        "Sire, the treasury cannot satisfy {holdout_names} in gold — what "
        "remains will not move them. Set a court aside to fight on, or pay "
        "in land."
    ),
    # PF-1 / UX-6 — submit-time validation failure stays in character. The
    # {blocker} slot carries the humanized validator reason (a full
    # sentence); Talleyrand owns the failure rather than blaming the player
    # for a draft he helped author.
    "settlement_submit_failed_validation_talleyrand": (
        "Sire, I cannot carry these terms to review as written. {blocker}"
    ),
    # ───────────────────────────────────────────────────────────────────
    # Guided Terms GT-Slice-V — voice for guided per-court demand
    # authoring (spec §9 GT-Slice-V; Voice Bible §16.1a). Three families:
    # the DC-4 guard line (verbatim from the Gate-4 pre-flight audit),
    # the named-court authoring reactions, and the OQ-6 budget-bound
    # recommendation extension. Per cleanup SC-32 D5, none of this
    # committed copy uses "conference", "congress", or "veto".
    # ───────────────────────────────────────────────────────────────────
    # DC-4 / D5 (press-past-zero): fired whenever a demand is authored or
    # seeded on a concede-direction court — demanding tribute from the
    # nation that is beating France is legal player agency; Talleyrand
    # prices the absurdity in character instead of authoring it wordlessly.
    "settlement_demand_on_concede_court_caution_talleyrand": (
        "They are not the ones suing for peace, Sire — but as you wish."
    ),
    # Named-court reactions when the player authors a line on that court's
    # row (the §16.1a resolver rule: named diplomat via
    # `resolve_named_diplomat`, chancery fallback — never anonymous).
    "settlement_multi_court_demand_received": (
        "{speaker} receives the demand — {demand_label} — without warmth; "
        "{court} will weigh it against the cost of fighting on."
    ),
    "settlement_multi_court_offer_received": (
        "{speaker} notes the offer — {offer_label}; {court} reads it as a "
        "reason to keep talking."
    ),
    # OQ-6 (GT-A2) — the budget-bound recommendation, extending
    # `settlement_budget_bound_constraint_talleyrand`: Talleyrand voices
    # the COMPUTED cheapest-signature allocation (Golden Rule #6 — the
    # arithmetic decides; he merely phrases it). Pressburg logic: buy the
    # peace you can afford and let the dearest enemy fight on.
    "settlement_budget_bound_recommendation_talleyrand": (
        "Sire, what remains in the purse will buy {concentrate_names} — "
        "the cheapest signatures at this table. I would let "
        "{set_aside_court} keep their war; we are not obliged to purchase "
        "every peace at once."
    ),
    "settlement_budget_bound_recommendation_concentrate_only_talleyrand": (
        "Sire, what remains in the purse will buy {concentrate_names} — "
        "the cheapest signatures at this table."
    ),
    "settlement_budget_bound_recommendation_set_aside_only_talleyrand": (
        "Sire, no sum we hold will buy these signatures. I would set "
        "{set_aside_court} aside; a peace one cannot afford is not a "
        "peace, it is a debt."
    ),
    # ───────────────────────────────────────────────────────────────────
    # Guided Terms GT-Slice-V — Talleyrand's per-option suggestion
    # reasons (`reason_display`, spec §3.1 / GT-R1-15). The bilateral
    # flow's signature beat ("I suggest Silesia — {reason}") generalized
    # to the per-court rows; resolved by `_court_demand_suggestions` so
    # the committed register lives here, not in f-strings.
    # ───────────────────────────────────────────────────────────────────
    "settlement_guided_reason_territory_demand_border_talleyrand": (
        "{region} sits beside what we already hold; {court} would keep it "
        "only on paper."
    ),
    "settlement_guided_reason_territory_demand_yield_talleyrand": (
        "Of {court}'s holdings, {region} is the one they can part with "
        "and still call themselves whole."
    ),
    "settlement_guided_reason_gold_demand_talleyrand": (
        "{court}'s treasury can bear {amount} gold — priced to wound the "
        "purse, not the pride."
    ),
    "settlement_guided_reason_recurring_demand_talleyrand": (
        "A tribute of {amount} gold a turn for {turns} turns — collected "
        "quietly, resented slowly, and well within {court}'s means."
    ),
    "settlement_guided_reason_vassalage_talleyrand": (
        "At {power_pct}% of our strength, {court} is better acquired than "
        "argued with."
    ),
    "settlement_guided_reason_subjugation_talleyrand": (
        "At {power_pct}% of our strength, {court} cannot decline a "
        "master; subjugation merely sets it down in ink."
    ),
    "settlement_guided_reason_forced_alliance_talleyrand": (
        "An alliance signed under necessity still signs, Sire — {court}'s "
        "weight moves to our side of the ledger."
    ),
    "settlement_guided_reason_liberation_talleyrand": (
        "Free {vassal} and {court} loses a servant it never paid well; "
        "the freed court will remember whose hand opened the door."
    ),
    "settlement_guided_reason_vassal_transfer_talleyrand": (
        "{vassal} already knows how to kneel, Sire — let it simply change "
        "the throne it kneels to. {court} loses a servant; we gain one."
    ),
    "settlement_guided_reason_gold_offer_talleyrand": (
        "A sweetener of {amount} gold — {court}'s resolve has a price, "
        "and it is conveniently paid in coin rather than provinces."
    ),
    "settlement_guided_reason_territory_offer_talleyrand": (
        "Ceding {region} purchases {court}'s signature; a province spent "
        "at the right table buys more than it earns."
    ),
    "settlement_guided_reason_recurring_offer_talleyrand": (
        "A pension of {amount} gold a turn for {turns} turns — {court}'s "
        "peace bought on installment, gentler on the treasury than the "
        "war."
    ),
    # ───────────────────────────────────────────────────────────────────
    # GT-A5 (GT-Slice-5) — the dial's ceiling escalation, voiced. Fired
    # as `talleyrand_line` authoring beats when a press/ease at an
    # exhausted gold lever authors the court's suggested territory clause
    # instead (spec §3.5 GT-A5; re-front OQ#7 amendment). Per cleanup
    # SC-32 D5, no "conference"/"congress"/"veto" copy.
    # ───────────────────────────────────────────────────────────────────
    "settlement_dial_escalation_demand_talleyrand": (
        "{court}'s purse is spent, Sire, so I have asked for land in its "
        "place — {region}."
    ),
    "settlement_dial_escalation_offer_talleyrand": (
        "The treasury can spare no more coin, Sire — I have offered "
        "{court} {region} instead."
    ),
}


def get_settlement_voice_template(template_key: str) -> Optional[str]:
    """Return committed Imperial Settlement copy by exact template key."""
    return SETTLEMENT_VOICE_TEMPLATES.get(str(template_key or ""))


def resolve_settlement_voice_line(template_key: str, **slots: Any) -> str:
    """Resolve a committed settlement voice template with caller-supplied slots."""
    template = get_settlement_voice_template(template_key)
    if not template:
        return ""
    safe_slots = {key: str(value) for key, value in slots.items()}
    return template.format_map(_MissingSettlementSlot(safe_slots))


_MULTI_COURT_BAND_TEMPLATE = {
    "accept": "settlement_multi_court_court_will_sign",
    "near_acceptable": "settlement_multi_court_court_leaning",
    "reject": "settlement_multi_court_court_holds_out",
}


def resolve_multi_court_settlement_voice(
    world: Any,
    *,
    per_court_acceptance: Any,
    overall_acceptance: Any = None,
    war_label: str = "",
) -> Dict[str, Any]:
    """Re-front Slice 1 / REFRONT-V — resolve the multi-court table voice.

    Returns ``{"per_court_voice": [{nation, speaker, band, line}, ...],
    "table_narration": str}``. Each covered court's line is spoken by its
    NAMED diplomat via ``resolve_named_diplomat`` (chancery fallback when the
    court has no named envoy — never an anonymous beat). Talleyrand narrates
    the table and names the binding constraint (the first holdout). Committed
    copy obeys the SC-32 D5 boundary: no "conference"/"congress"/"veto".
    """
    rows = list(per_court_acceptance or [])
    overall = dict(overall_acceptance or {})
    per_court_voice: List[Dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        court = str(row.get("nation") or "")
        speaker = resolve_named_diplomat("envoy", court, world)
        hard_stopped = bool(row.get("hard_stops")) and row.get("total") is None
        band = str(row.get("band") or "reject")
        top_blocker = str(row.get("top_blocker_display") or "the standing terms")
        if hard_stopped:
            template_key = "settlement_multi_court_court_hard_stop"
        else:
            template_key = _MULTI_COURT_BAND_TEMPLATE.get(
                band, "settlement_multi_court_court_holds_out"
            )
        line = resolve_settlement_voice_line(
            template_key,
            speaker=speaker,
            court=court,
            war_label=war_label or "this war",
            top_blocker=top_blocker,
        )
        per_court_voice.append({
            "nation": court,
            "speaker": speaker,
            "band": band,
            "line": line,
        })

    holdouts = list(overall.get("holdout_courts") or [])
    if not rows:
        binding = ""
    elif overall.get("carries"):
        binding = resolve_settlement_voice_line(
            "settlement_multi_court_all_carry_talleyrand",
            war_label=war_label or "this war",
        )
    else:
        binding = resolve_settlement_voice_line(
            "settlement_multi_court_holdout_blocks_talleyrand",
            holdout_court=(holdouts[0] if holdouts else "a covered court"),
            war_label=war_label or "this war",
        )
    table_narration = resolve_settlement_voice_line(
        "settlement_multi_court_table_talleyrand",
        war_label=war_label or "this war",
        court_count=len(rows),
        binding_constraint=binding,
    )
    return {
        "per_court_voice": per_court_voice,
        "table_narration": table_narration,
    }


class _MissingSettlementSlot(dict):
    def __missing__(self, key: str) -> str:
        return f"{{{key}}}"


def resolve_coalition_template(category: str, world, **kwargs) -> Optional[str]:
    """Resolve a coalition template with slot variables.

    Accepts keyword arguments for coalition-specific slots like
    threat_level, hostile_nations, qualifying_nations, etc.
    """
    template = COALITION_TEMPLATES.get(category)
    if not template:
        return None

    text = template["text"]
    slots = {k: str(v) for k, v in kwargs.items()}

    # Auto-fill from world state
    slots.setdefault("threat_level", str(int(getattr(world, 'threat_level', 0))))

    try:
        return text.format_map(_SafeFormatMap(slots))
    except (KeyError, ValueError):
        return text


# ═══════ FALLBACK TEMPLATES ═══════
# Used when no exact template match is found

FALLBACK_TEMPLATES = {
    "proposal_options": {
        "text": (
            "Sire, how shall I approach {target_nation}? "
            "I await your instructions."
        ),
        "options": [
            {
                "label": "Propose peace",
                "description": "Seek a peaceful resolution.",
                "action": "execute_proposal",
                "proposal_type": "peace",
            },
            {
                "label": "Improve relations",
                "description": "Send me on a diplomatic mission.",
                "action": "start_mission",
                "terms": {"mission_type": "IMPROVE_RELATIONS"},
            },
            {
                "label": "Dismiss",
                "description": "Not now.",
                "action": "dismiss",
            },
        ],
        "recommendation": 0,
    },
    "proposal_confirm": {
        "text": (
            "Sire, I shall prepare a {proposal_type} proposal for {target_nation}. "
            "Shall I proceed with standard terms?"
        ),
        "options": [
            {
                "label": "Proceed",
                "description": "Send with suggested terms.",
                "action": "execute_proposal",
            },
            # BUGFIX (Bug 4B): Modify options were missing from fallback template.
            # See BUGFIX_PLAN_PROPOSAL_FLOW.md.
            {
                "label": "Harsher terms",
                "description": "Demand more — press our advantage.",
                "action": "modify_harsh",
            },
            {
                "label": "More generous",
                "description": "Sweeten the offer to improve chances of acceptance.",
                "action": "modify_generous",
            },
            {
                "label": "Adjust terms",
                "description": "Build the offer step by step.",
                "action": "adjust_terms",
            },
            {
                "label": "Reconsider",
                "description": "Let me think about this.",
                "action": "reconsider",
            },
        ],
        "recommendation": 0,
    },
    "proposal_execute": {
        "text": "At once, Sire. I shall deliver your proposal to {target_nation}.",
        "options": [
            {
                "label": "Send",
                "description": "Dispatch immediately.",
                "action": "send",
            },
            {
                "label": "Reconsider",
                "description": "Wait.",
                "action": "reconsider",
            },
        ],
        "recommendation": 0,
    },
}


def get_template(intent_type: str, diplo_state: str, bucket: str,
                 proposal_type: Optional[str] = None) -> Dict:
    """Look up the best matching template.

    Lookup order:
    1. Exact match: (intent_type, diplo_state, bucket)
    2. Wildcard bucket: (intent_type, diplo_state, "any")
    3. Similar buckets for WAR states
    4. Fallback by intent_type
    """
    # 1. Exact match
    key = (intent_type, diplo_state, bucket)
    if key in DIPLOMATIC_TEMPLATES:
        template = _deep_copy_template(DIPLOMATIC_TEMPLATES[key])
        if proposal_type:
            template["_proposal_type"] = proposal_type
        return template

    # 2. Wildcard bucket
    key = (intent_type, diplo_state, "any")
    if key in DIPLOMATIC_TEMPLATES:
        template = _deep_copy_template(DIPLOMATIC_TEMPLATES[key])
        if proposal_type:
            template["_proposal_type"] = proposal_type
        return template

    # 3. Similar buckets for WAR
    if diplo_state == "WAR":
        similar_map = {
            "winning_slightly": "winning_comfortably",
            "losing_slightly": "losing_badly",
        }
        similar = similar_map.get(bucket)
        if similar:
            key = (intent_type, diplo_state, similar)
            if key in DIPLOMATIC_TEMPLATES:
                template = _deep_copy_template(DIPLOMATIC_TEMPLATES[key])
                if proposal_type:
                    template["_proposal_type"] = proposal_type
                return template

    # 4. Neutral bucket for PEACE
    if diplo_state == "PEACE" and bucket == "neutral":
        # Try hostile template as fallback for neutral
        key = (intent_type, diplo_state, "hostile")
        if key in DIPLOMATIC_TEMPLATES:
            template = _deep_copy_template(DIPLOMATIC_TEMPLATES[key])
            if proposal_type:
                template["_proposal_type"] = proposal_type
            return template

    # 5. Fallback
    if intent_type in FALLBACK_TEMPLATES:
        template = _deep_copy_template(FALLBACK_TEMPLATES[intent_type])
        if proposal_type:
            template["_proposal_type"] = proposal_type
        return template

    # Ultimate fallback
    return {
        "text": "Sire, I await your instructions regarding {target_nation}.",
        "options": [
            {"label": "Dismiss", "description": "Never mind.", "action": "dismiss"},
        ],
        "recommendation": 0,
    }


def _deep_copy_template(template: Dict) -> Dict:
    """Deep copy a template dict (simple structures only)."""
    result = {
        "text": template["text"],
        "options": [opt.copy() for opt in template.get("options", [])],
        "recommendation": template.get("recommendation", 0),
    }
    # Copy terms dicts in options
    for i, opt in enumerate(result["options"]):
        if "terms" in template.get("options", [])[i]:
            result["options"][i]["terms"] = template["options"][i]["terms"].copy()
    return result


def resolve_template_text(text: str, world, target_nation: Optional[str] = None) -> str:
    """Resolve {slot_name} placeholders in template text.

    Golden Rule #2: ALL numeric slots are int() wrapped.
    """
    if not text:
        return text

    slots = {}

    if target_nation:
        slots["target_nation"] = target_nation
        slots["player_nation"] = get_player_nation(world)

        # Get diplomat for target nation
        diplomats = getattr(world, 'diplomats', {})
        target_diplomat = diplomats.get(target_nation)
        slots["target_diplomat"] = target_diplomat.name if target_diplomat else "their diplomat"

        # Numeric values
        player_nation = get_player_nation(world)
        diplo_key = world._make_diplo_key(player_nation, target_nation)
        relation = int(world.nation_relations.get(diplo_key, 0))
        state = world.get_diplomatic_state(player_nation, target_nation)
        # R38: Only show war score when nations are at war
        if state == "WAR":
            from backend.game_logic.diplomacy import get_war_score_for
            slots["war_score"] = str(int(get_war_score_for(world, player_nation, target_nation)))
        else:
            slots["war_score"] = "N/A"
        slots["relation"] = str(relation)
        slots["current_state"] = state
        slots["dp_cost"] = "1"  # Default, overridden per-context

        # R82: rejection_reaction based on relation
        if relation < -40:
            slots["rejection_reaction"] = "cold fury"
        elif relation < 0:
            slots["rejection_reaction"] = "barely concealed displeasure"
        else:
            slots["rejection_reaction"] = "diplomatic composure"

    # Generic slots
    slots["dp"] = str(int(getattr(world, 'diplomatic_points', 0)))

    # Coalition slots (Session 7)
    slots["threat_level"] = str(int(getattr(world, 'threat_level', 0)))
    coalition = getattr(world, 'active_coalition', None)
    if coalition:
        slots["coalition_name"] = coalition.get("name", "The Coalition")
        slots["leader"] = coalition.get("leader", "")
        slots["member_list"] = ", ".join(coalition.get("members", []))

    # Resolve — use .get for safety
    try:
        return text.format_map(_SafeFormatMap(slots))
    except (KeyError, ValueError):
        return text


class _SafeFormatMap(dict):
    """Format map that returns {key} for missing keys instead of raising."""
    def __missing__(self, key):
        return "{" + key + "}"


def resolve_template_text_with_type(text: str, world, target_nation: Optional[str],
                                     proposal_type: Optional[str] = None) -> str:
    """Resolve template text with proposal_type slot."""
    result = resolve_template_text(text, world, target_nation)
    if proposal_type and "{proposal_type}" in result:
        result = result.replace("{proposal_type}", proposal_type)
    return result


# ═══════ NATION DESIRE PROFILES ═══════

NATION_DESIRE_PROFILES = {
    "Prussia": {
        "covets_regions": ["Saxony", "Dresden"],
        "values_gold": "low",
        "values_territory": "high",
        "values_ap": "medium",
        "diplomatic_lever": "ambition",
        "weakness": "overextension",
    },
    "Austria": {
        "covets_regions": ["Bavaria", "Tyrol", "Bohemia"],
        "values_gold": "medium",
        "values_territory": "high",
        "values_ap": "low",
        "diplomatic_lever": "stability",
        "weakness": "pride",
    },
    "Britain": {
        "covets_regions": ["Netherlands", "Hanover"],
        "values_gold": "low",
        "values_territory": "medium",
        "values_ap": "medium",
        "diplomatic_lever": "trade",
        "weakness": "isolation",
    },
    "Saxony": {
        "covets_regions": ["Saxony", "Dresden"],
        "values_gold": "high",
        "values_territory": "low",
        "values_ap": "high",
        "diplomatic_lever": "survival",
        "weakness": "desperation",
    },
    # ── Full-Europe (126-province) roster additions — Map Slice 3 ──
    # `NATION_DESIRE_PROFILES` is a `.get()` lookup, so authoring these is
    # additive: AI proposals for these nations no longer degrade to empty
    # desires. `covets_regions` uses real europe.json province names (things
    # the nation does NOT already own where possible). Per-nation Talleyrand
    # commentary falls back to the `("_default", …)` lines below — bespoke
    # in-voice copy is owner-row DEF-1 ("Roster Voices").
    "France": {
        "covets_regions": ["Hanover", "Piedmont"],
        "values_gold": "low",
        "values_territory": "high",
        "values_ap": "medium",
        "diplomatic_lever": "grandeur",
        "weakness": "overreach",
    },
    "Russia": {
        "covets_regions": ["Finland", "Constantinople"],
        "values_gold": "low",
        "values_territory": "high",
        "values_ap": "medium",
        "diplomatic_lever": "prestige",
        "weakness": "distance",
    },
    "Spain": {
        "covets_regions": ["Lisbon", "Morocco"],
        "values_gold": "medium",
        "values_territory": "medium",
        "values_ap": "low",
        "diplomatic_lever": "dynasty",
        "weakness": "dependence",
    },
    "Ottoman": {
        "covets_regions": [],
        "values_gold": "high",
        "values_territory": "high",
        "values_ap": "low",
        "diplomatic_lever": "survival",
        "weakness": "decay",
    },
    "Sweden": {
        "covets_regions": ["Trondheim", "Nordland"],
        "values_gold": "high",
        "values_territory": "medium",
        "values_ap": "low",
        "diplomatic_lever": "honor",
        "weakness": "isolation",
    },
    "Naples": {
        "covets_regions": ["Rome"],
        "values_gold": "medium",
        "values_territory": "low",
        "values_ap": "low",
        "diplomatic_lever": "survival",
        "weakness": "exposure",
    },
    "Portugal": {
        "covets_regions": [],
        "values_gold": "medium",
        "values_territory": "low",
        "values_ap": "low",
        "diplomatic_lever": "trade",
        "weakness": "isolation",
    },
    "Denmark": {
        "covets_regions": [],
        "values_gold": "high",
        "values_territory": "low",
        "values_ap": "low",
        "diplomatic_lever": "neutrality",
        "weakness": "exposure",
    },
    "Bavaria": {
        "covets_regions": ["Tyrol"],
        "values_gold": "medium",
        "values_territory": "high",
        "values_ap": "medium",
        "diplomatic_lever": "ambition",
        "weakness": "dependence",
    },
    "Hanover": {
        "covets_regions": [],
        "values_gold": "high",
        "values_territory": "low",
        "values_ap": "low",
        "diplomatic_lever": "survival",
        "weakness": "occupation",
    },
    "Hesse": {
        "covets_regions": [],
        "values_gold": "high",
        "values_territory": "low",
        "values_ap": "low",
        "diplomatic_lever": "survival",
        "weakness": "desperation",
    },
    "PapalStates": {
        "covets_regions": [],
        "values_gold": "low",
        "values_territory": "low",
        "values_ap": "low",
        "diplomatic_lever": "legitimacy",
        "weakness": "defenselessness",
    },
    "Sardinia": {
        "covets_regions": ["Piedmont"],
        "values_gold": "medium",
        "values_territory": "high",
        "values_ap": "low",
        "diplomatic_lever": "legitimacy",
        "weakness": "exile",
    },
    "Holland": {
        "covets_regions": [],
        "values_gold": "high",
        "values_territory": "low",
        "values_ap": "low",
        "diplomatic_lever": "trade",
        "weakness": "dependence",
    },
    "KingdomOfItaly": {
        "covets_regions": [],
        "values_gold": "low",
        "values_territory": "medium",
        "values_ap": "low",
        "diplomatic_lever": "patronage",
        "weakness": "dependence",
    },
    "Switzerland": {
        "covets_regions": [],
        "values_gold": "medium",
        "values_territory": "low",
        "values_ap": "low",
        "diplomatic_lever": "neutrality",
        "weakness": "dependence",
    },
}


# ═══════ TALLEYRAND COMMENTARY ═══════

TALLEYRAND_COMMENTARY = {
    # --- Prussia ---
    ("Prussia", "coveted_territory_offered"): "Saxony is the prize Hardenberg dreams of. Offering it buys more than gold ever could.",
    ("Prussia", "gold_useless"): "Prussia's treasury is adequate — they desire land, not coin. I've weighted the offer accordingly.",
    ("Prussia", "border_territory_demanded"): "The Rhineland gives us a buffer against Prussian ambition. A wise demand.",
    ("Prussia", "dominant_terms"): "Hardenberg will bristle, but Prussia is in no position to refuse. Press the advantage.",
    ("Prussia", "neutral_deal"): "A straightforward arrangement. Hardenberg is practical — he'll weigh the terms honestly.",
    ("Prussia", "friendly_deal"): "Hardenberg is well-disposed toward us. A generous arrangement cements the friendship.",
    ("Prussia", "hostile_deal"): "Hardenberg bristles at our very name. Only substantial concessions will move him.",
    # --- Austria ---
    ("Austria", "coveted_territory_offered"): "Bavaria is Austria's natural sphere. Returning it costs us little and buys Metternich's goodwill.",
    ("Austria", "gold_for_poor"): "Vienna's treasury grows thin after years of war. Gold per turn steadies their hand — and their loyalty.",
    ("Austria", "desperate_terms"): "Metternich is a schemer — even generous terms may not satisfy him. But we must try.",
    ("Austria", "neutral_deal"): "Metternich will study every clause for hidden advantage. I've kept the terms clean.",
    ("Austria", "friendly_deal"): "Metternich sees advantage in cooperation. Let us reward his pragmatism.",
    ("Austria", "hostile_deal"): "Metternich is hostile but calculating. A sufficiently attractive offer may still tempt him.",
    # --- Britain ---
    ("Britain", "gold_useless"): "Britain's coffers overflow — offering gold insults the British cabinet. Territory speaks louder.",
    ("Britain", "coveted_territory_offered"): "The Netherlands secures Britain's continental foothold. The British chancery values it above gold.",
    ("Britain", "dominant_terms"): "Britain's continental army is small. Their cabinet knows its position — it will accept reasonable terms.",
    ("Britain", "desperate_terms"): "The British chancery drives a hard bargain. I've included everything short of Paris itself.",
    ("Britain", "neutral_deal"): "An island nation with continental ambitions. This arrangement serves both parties' interests.",
    ("Britain", "friendly_deal"): "The British chancery is amenable, for once. Best to lock in terms before the mood shifts.",
    ("Britain", "hostile_deal"): "The British cabinet despises us openly. Only overwhelming terms have any chance.",
    # --- Saxony ---
    ("Saxony", "gold_for_poor"): "Saxony's treasury is nearly empty. Even modest gold buys Einsiedel's eternal gratitude.",
    ("Saxony", "protection_offered"): "Saxony lives in fear of Prussian annexation. A French guarantee is worth more than gold to them.",
    ("Saxony", "ap_for_weak"): "An extra action each turn transforms a small nation's capabilities. Einsiedel will understand this.",
    ("Saxony", "coveted_territory_offered"): "Einsiedel cares only for the survival of his homeland. Territorial guarantees speak loudest.",
    ("Saxony", "neutral_deal"): "A small nation, easily satisfied. Einsiedel will accept any arrangement that preserves Saxony.",
    ("Saxony", "friendly_deal"): "Einsiedel is a loyal friend. A gentle deal strengthens bonds cheaply.",
    ("Saxony", "hostile_deal"): "Even gentle Einsiedel has turned cold. We must offer more than usual.",
    # --- Full-Europe roster flavor (Map Slice 3): the largest new courts. ---
    # Every other new nation resolves through the ("_default", …) lines below;
    # bespoke voice for the full roster is owner-row DEF-1 ("Roster Voices").
    ("Russia", "neutral_deal"): "The Tsar's court weighs prestige above coin. I've kept the terms dignified — Petersburg does not haggle.",
    ("Russia", "hostile_deal"): "Alexander regards us as the disturber of Europe. Only terms that flatter his sense of destiny will move him.",
    ("Russia", "dominant_terms"): "Russia is vast but her armies are far away. Press now, while the distance is on our side.",
    ("Spain", "gold_for_poor"): "Madrid's treasury bleeds silver to keep its fleet afloat. Gold steadies a nervous ally.",
    ("Spain", "neutral_deal"): "Godoy binds Spain to our star for now. A clean arrangement keeps that convenient loyalty intact.",
    ("Ottoman", "neutral_deal"): "The Porte answers slowly and forgets nothing. I've made the terms plain, so nothing is lost in the delay.",
    ("Ottoman", "gold_for_poor"): "Constantinople's coffers are hollow. Gold, discreetly offered, opens doors that armies cannot.",
    # --- Coveted unavailable (France doesn't control what they want) ---
    ("Prussia", "coveted_unavailable"): "Hardenberg dreams of Saxony, but it is not yet ours to offer. Conquer it first, Sire, and he will come to the table eagerly.",
    ("Austria", "coveted_unavailable"): "Metternich yearns for Bavaria, but we do not hold it. Secure it first, and these negotiations transform entirely.",
    ("Britain", "coveted_unavailable"): "Britain values its continental footholds, but they are beyond our gift at present. We must work with what we have.",
    ("Saxony", "coveted_unavailable"): "Einsiedel's homeland is not ours to return. Until we hold it, we cannot offer what matters most to him.",
    ("_default", "coveted_unavailable"): "They desire territory we do not yet control. Conquer it first, Sire, and our bargaining position transforms.",
    # --- Defaults ---
    ("_default", "coveted_territory_offered"): "I've included territory they particularly desire. It should tip the balance in our favor.",
    ("_default", "gold_for_poor"): "Their treasury is strained. Gold speaks loudly to those who lack it.",
    ("_default", "gold_useless"): "Gold would be wasted here — I've substituted something they actually value.",
    ("_default", "smart_cession"): "I've selected our least valuable border territory for cession. We lose little of strategic worth.",
    ("_default", "desperate_terms"): "We are not in a position to be choosy, Sire. I've assembled the most persuasive package possible.",
    ("_default", "dominant_terms"): "They have little choice but to accept. I've kept the demands firm but not humiliating.",
    ("_default", "neutral_deal"): "Standard terms, Sire. Neither generous nor harsh — a foundation for negotiation.",
    ("_default", "protection_offered"): "A guarantee of protection costs us nothing but obligation. For them, it means survival.",
    ("_default", "ap_for_weak"): "An extra action per turn is transformative for a smaller power. They will value this highly.",
    ("_default", "border_territory_demanded"): "Border territory provides strategic depth. A prudent demand.",
    ("_default", "friendly_deal"): "They are well-disposed. I've proposed fair terms that reward the friendship.",
    ("_default", "cautious_deal"): "Relations are tepid. I've balanced the terms to avoid giving offense.",
    ("_default", "hostile_deal"): "Relations are poor. I've included extra incentives to overcome their reluctance.",
    # --- Modified terms (harsh/generous iterations) ---
    ("Prussia", "modified_harsh"): "Hardenberg's pride is wounded, but Prussia cannot refuse. Press the advantage, Sire.",
    ("Prussia", "modified_generous"): "Generosity toward Prussia costs us little. Hardenberg will remember this kindness.",
    ("Austria", "modified_harsh"): "Metternich will protest, but his options narrow with each demand. Hold firm.",
    ("Austria", "modified_generous"): "Metternich appreciates magnanimity — it allows him to save face at court.",
    ("Britain", "modified_harsh"): "Britain's island position gives its cabinet options we cannot eliminate. Harsh terms risk outright rejection.",
    ("Britain", "modified_generous"): "Even the British chancery may warm to terms this favorable. Britain values pragmatism.",
    ("Saxony", "modified_harsh"): "Poor Einsiedel has little left to give. These demands may break Saxony entirely.",
    ("Saxony", "modified_generous"): "Einsiedel will weep with gratitude. Such generosity buys a loyal vassal, Sire.",
    ("_default", "modified_harsh"): "I have drafted more demanding terms, Sire. They will not accept lightly.",
    ("_default", "modified_generous"): "I have drafted more generous terms, Sire. Such magnanimity should improve acceptance.",
}


# ═══════ ULTIMATUM TERMS GENERATION (PL-14 §2) ═══════

def generate_ultimatum_terms(target_nation: str, world, *, issuer: str = None,
                             demand_regions: list = None) -> Dict:
    """Generate coercive demands based on military advantage.

    Returns: {"demands": [...], "sweeteners": [], "clauses": [], "type": "ultimatum_demand"}
    No AP demands (requires war_score > 80, impossible in peacetime).
    No sweeteners ever — ultimatums are pure extortion.
    No proposal_type key — uses "type" only (PL-13 lesson).

    NA-5 §8 (Building Blocks): the AI ultimatum rung reuses this SAME
    generator with `issuer=<AI nation>` and `demand_regions=<agenda
    targets>` — the territory demand becomes exactly the issuer's design
    targets (pre-gated by the rung), replacing the adjacency scan. With
    both kwargs omitted the player-issued output is byte-identical.
    """
    demands = []
    issuer = issuer or get_player_nation(world)

    # ── Gold demand: capped at 50% of target income (AM-15.7: use get_nation_regions) ──
    target_income = 0
    target_gold = 0
    regions = getattr(world, 'regions', {})
    for rname in world.get_nation_regions(target_nation):
        region = regions.get(rname)
        if region:
            target_income += getattr(region, 'income_value', 0)
    target_gold = getattr(world, 'nation_gold', {}).get(target_nation, 0)

    if target_income > 0:
        gold_demand = min(300, max(50, int(target_income * 0.5)))
        demands.append({"type": "gold_per_turn", "value": int(gold_demand)})
    elif target_gold > 0:
        gold_lump = min(500, max(50, int(target_gold * 0.3)))
        demands.append({"type": "gold_lump", "value": int(gold_lump)})

    # ── Territory demand: coveted regions if issuer controls adjacent (AM-15.7) ──
    issuer_regions = set(world.get_nation_regions(issuer))
    target_regions = set(world.get_nation_regions(target_nation))

    # Calculate military superiority
    marshals = getattr(world, 'marshals', {})
    issuer_strength = sum(m.strength for m in marshals.values() if m.nation == issuer and m.strength > 0)
    target_strength = sum(m.strength for m in marshals.values() if m.nation == target_nation and m.strength > 0)
    has_military_superiority = issuer_strength > target_strength * 1.2

    if demand_regions:
        # NA-5: the agenda target IS the demand. Filter to what the target
        # actually controls minus its capital (never demand the seat of the
        # crown — the elimination guard's little sibling).
        capital = world.get_nation_capital(target_nation)
        named = [r for r in demand_regions
                 if r in target_regions and r != capital]
        if named:
            demands.append({"type": "territory_cede", "value": 1,
                            "regions": named[:1]})
    elif has_military_superiority and len(target_regions) > 2:
        # Prefer regions adjacent to issuer-controlled territory
        adjacent_targets = []
        for t_name in target_regions:
            t_region = regions.get(t_name)
            if not t_region:
                continue
            # Skip capitals (world-scoped — 1805 pre-slice item 7 family)
            if t_name == world.get_nation_capital(target_nation):
                continue
            connections = getattr(t_region, 'adjacent_regions', [])
            if any(c in issuer_regions for c in connections):
                adjacent_targets.append(t_name)
        if adjacent_targets:
            demands.append({"type": "territory_cede", "value": 1, "regions": adjacent_targets[:1]})

    # ── Manpower demand: proportional to troop advantage ──
    troop_advantage = issuer_strength - target_strength
    if troop_advantage > 5000:
        manpower_demand = min(5000, int(troop_advantage * 0.1))
        if manpower_demand >= 500:
            demands.append({"type": "manpower_infantry", "value": int(manpower_demand)})

    # Ensure at least one demand (gold floor)
    if not demands:
        demands.append({"type": "gold_lump", "value": 100})

    return {
        "demands": demands,
        "sweeteners": [],
        "clauses": [],
        "type": "ultimatum_demand",
        # Phase review (July 18, 2026): every other AI proposal builder
        # stamps the issuer; this one did not, so the fallback prose
        # rendered "Unknown demands 300 gold per turn" for an AI-issued
        # ultimatum. `issuer` already defaults to the player above, so the
        # player-issued path keeps its previous value rather than gaining
        # a surprise one.
        "proposer_nation": issuer,
    }


# ═══════ SUGGESTED TERMS GENERATION ═══════

def generate_suggested_terms(target_nation: str, proposal_type: str, world) -> Dict:
    """Generate smart treaty terms based on game state AND nation-specific knowledge.

    5-stage pipeline:
      1. Base terms (war_score/relation thresholds)
      2. Nation-specific clause injection (coveted territory, gold calibration, protection)
      3. Economic reality check (cap offers/demands to feasible levels)
      4. Talleyrand commentary (explain WHY these terms)
      5. Return
    """
    from backend.game_logic.diplomacy import get_war_score_for, SPECIAL_BONUSES

    player_nation = get_player_nation(world)
    war_score = get_war_score_for(world, player_nation, target_nation)

    # --- Stage 1: Base terms ---
    terms = _build_base_terms(target_nation, proposal_type, world)

    # --- Stage 2: Nation-specific injection ---
    context_tags = []
    profile = NATION_DESIRE_PROFILES.get(target_nation, {})

    # 2a. Territory sweeteners: prefer coveted regions.
    # NA-2 §5.2 covets unification: the target's ACTIVE agenda targets are
    # the authoritative first source (Austria's live design wants Milan,
    # not the authored Bavaria row); the static profile remains the
    # fallback when the agenda yields no territorial wants.
    has_territory_sweetener = any(
        s.get("type") == "territory_cede" for s in terms.get("sweeteners", []))
    try:
        from backend.game_logic.agendas import get_agenda_covets
        agenda_covets = get_agenda_covets(target_nation, world)
    except Exception:
        agenda_covets = []
    all_coveted = agenda_covets or profile.get("covets_regions", [])
    coveted = [r for r in all_coveted
               if r in world.get_nation_regions(player_nation)]
    target_holds_all_coveted = all(
        r in world.get_nation_regions(target_nation)
        for r in all_coveted
    ) if all_coveted else True

    # Check if target covets regions France doesn't control (hint to conquer first)
    coveted_unavailable = [r for r in all_coveted
                           if r not in world.get_nation_regions(player_nation)
                           and r not in world.get_nation_regions(target_nation)]

    if has_territory_sweetener or (coveted and war_score < 0 and not target_holds_all_coveted):
        if coveted:
            terms["sweeteners"] = [s for s in terms.get("sweeteners", [])
                                   if s.get("type") != "territory_cede"]
            terms["sweeteners"].append(
                {"type": "territory_cede", "value": 1, "regions": [coveted[0]]})
            bonus_clause = f"territory_{coveted[0].lower()}"
            terms.setdefault("clauses", [])
            if bonus_clause not in terms["clauses"]:
                terms["clauses"].append(bonus_clause)
            context_tags.append("coveted_territory_offered")
        elif has_territory_sweetener:
            candidates = rank_cession_candidates(world, player_nation, target_nation)
            if candidates:
                terms["sweeteners"] = [s for s in terms["sweeteners"]
                                       if s.get("type") != "territory_cede"]
                terms["sweeteners"].append(
                    {"type": "territory_cede", "value": 1, "regions": [candidates[0][0]]})
                context_tags.append("smart_cession")
    elif coveted_unavailable and not coveted:
        # France doesn't control what they want — hint to conquer it first
        context_tags.append("coveted_unavailable")

    # 2b. Territory demands: prefer border regions
    has_territory_demand = any(
        d.get("type") in ("territory_cede", "territory")
        for d in terms.get("demands", []))
    target_regions = world.get_nation_regions(target_nation)
    player_regions = world.get_nation_regions(player_nation)
    border = []
    for rname in target_regions:
        region = world.regions.get(rname)
        if region and any(adj in player_regions for adj in region.adjacent_regions):
            if rname != world.get_nation_capital(target_nation):
                border.append(rname)

    if has_territory_demand or (war_score > 30 and border):
        if border:
            terms["demands"] = [d for d in terms.get("demands", [])
                                if d.get("type") not in ("territory_cede", "territory")]
            terms["demands"].append(
                {"type": "territory_cede", "value": 1, "regions": [border[0]]})
            context_tags.append("border_territory_demanded")

    # 2c. Gold calibration — only tag when gold sweeteners actually exist
    gold_pref = profile.get("values_gold", "medium")
    has_gold_sweetener = any("gold" in s.get("type", "") for s in terms.get("sweeteners", []))
    if gold_pref == "high":
        for s in terms.get("sweeteners", []):
            if "gold" in s.get("type", ""):
                s["value"] = int(s["value"] * 1.5)
        if has_gold_sweetener:
            context_tags.append("gold_for_poor")
    elif gold_pref == "low":
        # Bug 4 fix: Remove gold sweeteners when nation doesn't value gold
        # AND alternative sweeteners (territory) exist. If gold is the only
        # sweetener, keep it at 50% to avoid empty offers.
        non_gold = [s for s in terms.get("sweeteners", [])
                    if "gold" not in s.get("type", "")]
        if has_gold_sweetener and non_gold:
            # Alternative sweeteners exist — drop gold entirely
            terms["sweeteners"] = non_gold
            context_tags.append("gold_useless")
        elif has_gold_sweetener:
            # Gold is the only sweetener — reduce but keep
            for s in terms.get("sweeteners", []):
                if "gold" in s.get("type", ""):
                    s["value"] = int(s["value"] * 0.5)

    # 2d. Protection clause for survival-driven nations
    if (profile.get("diplomatic_lever") == "survival"
            and proposal_type in ("peace", "defensive_alliance", "alliance")):
        if "protection_promised" in SPECIAL_BONUSES.get(target_nation, {}):
            if "protection_promised" not in terms.get("clauses", []):
                terms.setdefault("clauses", []).append("protection_promised")
                context_tags.append("protection_offered")

    # 2e. AP for nations that value extra actions
    ap_pref = profile.get("values_ap", "medium")
    if ap_pref == "high" and war_score < -30:
        if not any(s.get("type") == "ap_per_turn" for s in terms.get("sweeteners", [])):
            terms["sweeteners"].append({"type": "ap_per_turn", "value": 1})
            context_tags.append("ap_for_weak")

    # --- Stage 3: Economic reality check ---
    _validate_economic_feasibility(terms, target_nation, world, war_score=war_score)

    # --- Stage 3.5: G4F-9 — estimate convergence (peace family only) ---
    # The advisor must never SUGGEST a package his own displayed estimate
    # REJECTS (live Gate-4 smoke: 200/turn + a region at war score +50
    # scored 3/REJECT under `calculate_acceptance` while the assessment
    # read PUNITIVE and the commentary claimed the terms fit the
    # situation). Mirrors the settlement baseline's degrade-to-peace-floor
    # ladder: drop territory demands → halve gold demands → white peace,
    # stopping at the first package the estimator does not REJECT. The
    # acceptance FORMULA is untouched — its conservative war-score credit
    # (+15 at +50) is a standing calibration question owned by the
    # pre-flight audit ledger, not a smoke fix.
    if proposal_type in (
        "peace", "armistice", "armistice_winning", "armistice_losing",
    ):
        terms = _ease_suggestion_until_not_rejected(
            terms,
            target_nation=target_nation,
            player_nation=player_nation,
            world=world,
        )

    # --- Stage 4: Commentary ---
    if not context_tags:
        if war_score < -30:
            context_tags.append("desperate_terms")
        elif war_score > 30:
            context_tags.append("dominant_terms")
        else:
            from backend.game_logic.diplomatic_dialogue import get_game_bucket
            bucket = get_game_bucket(target_nation, world)
            if bucket == "friendly":
                context_tags.append("friendly_deal")
            elif bucket == "hostile":
                context_tags.append("hostile_deal")
            elif bucket == "neutral":
                context_tags.append("cautious_deal")
            else:
                context_tags.append("neutral_deal")

    # NA-2 (adversarial-review fix): when the coveted region came from the
    # LIVE AGENDA source, the bespoke TALLEYRAND_COMMENTARY rows — authored
    # against the static profile covets (Austria=Bavaria, Prussia=Saxony) —
    # would name the wrong region and give dead conquer-this-first advice.
    # Agenda-sourced tags compose a region-accurate line instead; profile-
    # sourced tags keep the authored voice unchanged (legacy worlds).
    commentary = None
    if agenda_covets and context_tags:
        from backend.display_names import display_nation
        lead_tag = context_tags[0]
        if lead_tag == "coveted_territory_offered" and coveted:
            commentary = (
                f"{coveted[0]} is the very object of "
                f"{display_nation(target_nation)}'s design. Returning it "
                f"costs us little and buys their court's goodwill.")
        elif lead_tag == "coveted_unavailable" and coveted_unavailable:
            commentary = (
                f"Their court's design fixes on {coveted_unavailable[0]}, "
                f"Sire — which we do not hold. Secure it first, and these "
                f"negotiations transform entirely.")
    if commentary is None:
        commentary = _get_smart_commentary(target_nation, context_tags[0])

    # PL-25: Append situational flavor from recent events (AM-25.5/25.6)
    flavor = _get_situational_flavor(target_nation, world)
    if flavor and flavor != commentary:
        commentary = f"{commentary}\n\n{flavor}"
    terms["talleyrand_commentary"] = commentary

    # --- Stage 5: Return ---
    return terms


def _ease_suggestion_until_not_rejected(
    terms: Dict,
    *,
    target_nation: str,
    player_nation: str,
    world,
) -> Dict:
    """G4F-9 — ease a suggested peace/armistice package until the bilateral
    estimator no longer REJECTS it (self-consistency: the popup shows the
    estimator's verdict next to Talleyrand's suggestion, so the two must
    agree). Ladder: drop territory demands → halve gold demands (floor 50)
    → white-peace floor. Sweeteners and identity metadata are untouched;
    the original dict is never mutated. ``suggestion_eased_to_estimate``
    marks an eased result for tests/telemetry.
    """
    from backend.game_logic.diplomacy import calculate_acceptance

    def _verdict(candidate: Dict) -> str:
        proposal = {
            "type": candidate.get("type", "peace"),
            "proposer_nation": player_nation,
            "target_nation": target_nation,
            "demands": candidate.get("demands", []),
            "sweeteners": candidate.get("sweeteners", []),
            "clauses": candidate.get("clauses", []),
        }
        try:
            result = calculate_acceptance(proposal, world)
        except Exception:
            return ""
        if isinstance(result, dict):
            return str(result.get("verdict") or result.get("outcome") or "")
        return ""

    if _verdict(terms) != "REJECT":
        return terms
    eased = {
        **terms,
        "demands": [dict(d) for d in terms.get("demands", [])],
        "sweeteners": [dict(s) for s in terms.get("sweeteners", [])],
    }
    eased["suggestion_eased_to_estimate"] = True
    # Step 1: drop territory demands — the steepest rung of the bilateral
    # harshness curve (the live-smoke package crossed the cliff on the
    # region + recurring-gold combination).
    without_territory = [
        d for d in eased["demands"]
        if d.get("type") not in ("territory_cede", "territory")
    ]
    if len(without_territory) != len(eased["demands"]):
        eased["demands"] = without_territory
        if _verdict(eased) != "REJECT":
            return eased
    # Step 2: halve gold demand magnitudes (floor 50).
    halved = False
    for demand in eased["demands"]:
        if demand.get("type") in ("gold_per_turn", "gold_lump"):
            value = int(demand.get("value", 0) or 0)
            if value > 50:
                demand["value"] = max(50, value // 2)
                halved = True
    if halved and _verdict(eased) != "REJECT":
        return eased
    # Step 3: white-peace floor — no demand survives the estimator. (If
    # even this rejects, there is nothing softer to suggest; the verdict
    # display stays honest.)
    eased["demands"] = []
    return eased


def _build_base_terms(target_nation: str, proposal_type: str, world, deterministic: bool = False) -> Dict:
    """Build base treaty terms using war_score/relation thresholds.

    Args:
        target_nation: Target nation name
        proposal_type: Type of proposal
        world: WorldState
        deterministic: If True, skip jitter (for testing). Default False.
    """
    from backend.game_logic.diplomacy import get_war_score_for
    player_nation = get_player_nation(world)
    diplo_key = world._make_diplo_key(player_nation, target_nation)
    relation = world.nation_relations.get(diplo_key, 0)
    war_score = get_war_score_for(world, player_nation, target_nation)

    terms = {
        "type": proposal_type,
        "proposal_type": proposal_type,  # PL-13-D: normalize dual-key at source
        "proposer_nation": player_nation,
        "target_nation": target_nation,
        "sweeteners": [],
        "demands": [],
        "clauses": [],
    }

    if proposal_type == "peace":
        # Include open borders if relation isn't too hostile
        if relation > -20:
            terms["clauses"].append("open_borders")

        # If winning, demand gold/turn proportional to advantage
        if war_score > 20:
            gold_demand = min(300, war_score * 5)
            terms["demands"].append({"type": "gold_per_turn", "value": int(gold_demand)})
        elif war_score < -20 or relation < -50:
            # If losing or deeply hostile, offer gold to sweeten
            gold_factor = max(abs(war_score) * 3, abs(relation))
            gold_offer = min(200, max(50, int(gold_factor)))
            terms["sweeteners"].append({"type": "gold_per_turn", "value": int(gold_offer)})

            # R147: Offer territory cession when losing
            # Non-capital regions first; capital only as desperate last resort
            player_capital = world.get_nation_capital(player_nation) or "Paris"
            player_regions = world.get_nation_regions(player_nation)
            non_capital = [r for r in player_regions if r != player_capital]
            max_cede = 1 if war_score >= -40 else 2
            for region in non_capital[:max_cede]:
                terms["sweeteners"].append({"type": "territory_cede", "value": 1, "regions": [region]})
            # Capital offered only as desperate last resort (war_score < -60)
            if war_score < -60 and len(non_capital) < max_cede:
                terms["sweeteners"].append({"type": "territory_cede", "value": 1, "regions": [player_capital]})

            # R148: Offer manpower when losing badly
            if war_score < -30:
                player_pool = getattr(world, 'manpower_pools', {}).get(player_nation, {}).get("infantry", 0)
                offer_amount = min(5000, int(player_pool * 0.25))
                if offer_amount >= 1000:
                    terms["sweeteners"].append({"type": "manpower_infantry", "value": int(offer_amount)})

            # R148: Offer AP when desperate
            if war_score < -50:
                terms["sweeteners"].append({"type": "ap_per_turn", "value": 1})

    elif proposal_type == "defensive_alliance":
        # Defensive alliance: mutual defense, open borders
        terms["clauses"].append("open_borders")

    elif proposal_type == "alliance":
        # Alliance: minimal terms, mutual defense
        terms["clauses"].append("open_borders")

    elif proposal_type == "vassalage":
        # Vassalage: tribute based on target economy
        target_gold = world.nation_gold.get(target_nation, 500)
        tribute = max(100, int(target_gold * 0.15))
        terms["demands"].append({"type": "gold_per_turn", "value": int(tribute)})

    elif proposal_type == "open_borders":
        terms["clauses"].append("open_borders")

    elif proposal_type == "non_aggression":
        pass  # No special terms needed

    elif proposal_type in ("armistice", "armistice_losing", "armistice_winning"):
        # Armistice is a temporary ceasefire
        terms["type"] = "armistice_losing" if war_score < 0 else "armistice_winning"

        # R150: Sweeten armistice when losing OR when relation is very hostile
        # Hostile nations won't accept bare armistice even at neutral war score
        needs_sweetener = war_score < -10 or relation < -50
        if needs_sweetener:
            gold_amount = max(200, min(2000, max(abs(war_score), abs(relation)) * 20))
            terms["sweeteners"].append({"type": "gold_lump", "value": int(gold_amount)})

        if war_score < -30:
            # Offer 1 territory as armistice sweetener (non-capital first)
            player_capital = world.get_nation_capital(player_nation) or "Paris"
            player_regions = world.get_nation_regions(player_nation)
            non_capital = [r for r in player_regions if r != player_capital]
            if non_capital:
                terms["sweeteners"].append({"type": "territory_cede", "value": 1, "regions": [non_capital[0]]})
            elif war_score < -60:
                # Capital only as desperate last resort
                terms["sweeteners"].append({"type": "territory_cede", "value": 1, "regions": [player_capital]})

    # PL-25: Amount jitter ±20% on gold/manpower values (demands + sweeteners)
    if not deterministic:
        import random
        jitter = random.uniform(0.8, 1.2)
    else:
        jitter = 1.0
    _JITTER_TYPES = {"gold_per_turn", "gold_lump", "manpower_infantry", "manpower_cavalry", "manpower_artillery"}
    for d in terms.get("demands", []):
        if d.get("type") in _JITTER_TYPES:
            d["value"] = int(d["value"] * jitter)
    for s in terms.get("sweeteners", []):
        if s.get("type") in _JITTER_TYPES:
            s["value"] = int(s["value"] * jitter)

    return terms


def _validate_economic_feasibility(terms, target_nation, world, war_score=0):
    """Cap gold/territory offers and demands to economically feasible levels."""
    player_nation = get_player_nation(world)
    player_gold = world.nation_gold.get(player_nation, 0)
    player_income = world.calculate_turn_income(player_nation).get("income", 0)
    target_income = world.calculate_turn_income(target_nation).get("income", 0)
    gold_cap_pct = 0.50 if war_score < -30 else 0.25

    for s in terms.get("sweeteners", []):
        if s.get("type") == "gold_lump":
            s["value"] = int(min(s["value"], max(50, int(player_gold * gold_cap_pct))))
        elif s.get("type") == "gold_per_turn":
            s["value"] = int(min(s["value"], max(25, int(player_income * 0.2))))
    for d in terms.get("demands", []):
        if d.get("type") == "gold_per_turn":
            d["value"] = int(min(d["value"], max(25, int(target_income * 0.5))))
    # Force all values to int (Godot crashes on floats)
    for s in terms.get("sweeteners", []):
        if "value" in s:
            s["value"] = int(s["value"])
    for d in terms.get("demands", []):
        if "value" in d:
            d["value"] = int(d["value"])


def _get_smart_commentary(target_nation, context_tag):
    """Look up Talleyrand's commentary for a nation + context tag."""
    key = (target_nation, context_tag)
    if key in TALLEYRAND_COMMENTARY:
        return TALLEYRAND_COMMENTARY[key]
    default_key = ("_default", context_tag)
    if default_key in TALLEYRAND_COMMENTARY:
        return TALLEYRAND_COMMENTARY[default_key]
    return "I have assembled terms befitting the situation, Sire."


def _get_situational_flavor(target_nation: str, world) -> str:
    """PL-25: Generate situational flavor line from recent events.

    Uses event API (AM-25.6: NOT battle_history which is a zombie field).
    Safe access throughout (AM-25.5: no crash on turn 1 / empty events).

    Returns:
        Flavor string, or default TALLEYRAND_COMMENTARY fallthrough
    """
    player_nation = get_player_nation(world)

    # Check recent battles (last 3 turns) — AM-25.6: use event API
    recent_events = world.get_events_since_turn(max(1, world.current_turn - 3)) if hasattr(world, 'get_events_since_turn') else []
    recent_battles = [e for e in recent_events if e.get("type") == "battle"] if recent_events else []

    # Victory over target nation
    if recent_battles:
        for battle in reversed(recent_battles):
            att_nation = battle.get("attacker_nation", "")
            def_nation = battle.get("defender_nation", "")
            outcome = battle.get("outcome", "")
            if def_nation == target_nation and att_nation == player_nation and outcome in ("attacker_victory", "decisive_attacker_victory"):
                return "They are weakened, Sire. Our recent victory gives us the advantage at the table."
            if att_nation == target_nation and def_nation == player_nation and outcome in ("defender_victory", "decisive_defender_victory"):
                return "They are weakened, Sire. Their failed attack leaves them in no position to refuse."

    # Check diplomatic history for recent alliance breaks
    diplo_history = getattr(world, 'diplomatic_history', [])
    if diplo_history:
        for event in reversed(diplo_history[-10:]):
            if event.get("type") == "alliance_broken" and target_nation in (event.get("nation_a"), event.get("nation_b")):
                return "They stand alone. A generous offer now buys loyalty cheaply."

    # High coalition threat
    if hasattr(world, 'coalition_threat'):
        threat = getattr(world, 'coalition_threat', 0)
        if threat > 60:
            return "The courts watch us, Sire. Moderation may serve us better than force."

    # No situational event → return empty (base commentary already covers the default)
    return ""


def get_desire_profile_nudge_bias(target_nation: str) -> Dict:
    """PL-25 AM-25.9: Get desire profile bias for pen nudge targeting.

    Returns multipliers that influence which demand the pen nudge targets.
    Higher multiplier = more likely to be targeted for softening.

    Returns:
        Dict with 'territory_mult', 'nudge_override_type', 'sweetener_bias'
    """
    profile = NATION_DESIRE_PROFILES.get(target_nation, {})
    result = {
        "territory_mult": 1.0,
        "nudge_override_type": None,  # If set, this type becomes nudge target
        "sweetener_bias": None,       # Preferred sweetener type
    }

    # AM-25.9: Territory-valuing nations → territory demands get 1.5x harshness
    if profile.get("values_territory") == "high":
        result["territory_mult"] = 1.5

    # AM-25.9: Weakness → nudge override
    weakness = profile.get("weakness", "")
    if weakness == "overextension":
        result["nudge_override_type"] = "territory_cede"
    elif weakness == "isolation":
        # Diplomatic demands — AP is closest proxy
        result["nudge_override_type"] = "ap_per_turn"

    # AM-25.9: Sweetener bias from diplomatic_lever
    lever = profile.get("diplomatic_lever", "")
    if lever == "trade":
        result["sweetener_bias"] = "gold_per_turn"
    elif lever == "stability":
        result["sweetener_bias"] = "non_aggression"

    return result


# ═══════ CONVERSATIONAL TERMS GUIDANCE ═══════

def rank_cession_candidates(world, player_nation: str, target_nation: str) -> list:
    """Rank player regions for cession, prioritizing border + empty + cheap.

    Returns list of [region_name, reason_text] pairs, sorted best-to-cede first.
    Excludes the player's capital.
    """
    from backend.models.region import REGION_TYPE_INCOME

    capital = world.get_nation_capital(player_nation) or ""
    player_regions = world.get_nation_regions(player_nation)
    target_regions = world.get_nation_regions(target_nation)

    candidates = []
    for region_name in player_regions:
        if region_name == capital:
            continue
        region = world.regions.get(region_name)
        if not region:
            continue

        # Score components
        is_border = any(adj in target_regions for adj in region.adjacent_regions)
        has_buildings = len(region.buildings) > 0
        income = REGION_TYPE_INCOME.get(region.region_type, 100)

        # Build reason text
        building_types = ", ".join(b["type"].replace("_", " ") for b in region.buildings)
        if is_border and not has_buildings:
            reason = (f"{region_name} borders {target_nation} territory and has no "
                      f"strategic improvements — an ideal concession.")
        elif is_border and has_buildings:
            reason = (f"{region_name} borders {target_nation} territory — a logical "
                      f"concession, though we lose its {building_types}.")
        elif not has_buildings:
            reason = f"{region_name} has no strategic improvements — we lose little by offering it."
        else:
            reason = f"{region_name} is a {region.region_type} of modest strategic value."

        # Sort key: border first (not is_border=False first), then empty, then cheap
        candidates.append([region_name, reason, (not is_border, has_buildings, income)])

    candidates.sort(key=lambda c: c[2])
    return [[c[0], c[1]] for c in candidates]


def rank_ultimatum_territory_candidates(world, player_nation: str, target_nation: str) -> list:
    """Rank target regions for ultimatum demands, prioritizing border + valuable.

    Returns list of [region_name, reason_text] pairs, sorted best-to-demand first.
    Only includes regions adjacent to player territory. Excludes target's capital.
    """
    from backend.models.region import REGION_TYPE_INCOME

    capital = world.get_nation_capital(target_nation) or ""
    player_regions = set(world.get_nation_regions(player_nation))
    target_region_names = world.get_nation_regions(target_nation)

    candidates = []
    for region_name in target_region_names:
        if region_name == capital:
            continue
        region = world.regions.get(region_name)
        if not region:
            continue

        # Only regions adjacent to player territory
        is_border = any(adj in player_regions for adj in region.adjacent_regions)
        if not is_border:
            continue

        has_buildings = len(region.buildings) > 0
        income = REGION_TYPE_INCOME.get(region.region_type, 100)

        # Build reason text
        if has_buildings:
            building_types = ", ".join(b["type"].replace("_", " ") for b in region.buildings)
            reason = (f"{region_name} borders our territory and has {building_types} "
                      f"— a valuable acquisition.")
        else:
            reason = f"{region_name} borders our territory — a natural extension of our domain."

        # Sort: buildings first (more valuable), then higher income
        candidates.append([region_name, reason, (not has_buildings, -income)])

    candidates.sort(key=lambda c: c[2])
    return [[c[0], c[1]] for c in candidates]


# ═══════ ENEMY DIPLOMAT VOICE RESOLUTION ═══════

# Maps diplomat personality to template key prefix
_PERSONALITY_TO_TEMPLATE = {
    "hawk": "enemy_response_hawk",
    "schemer": "enemy_response_schemer",
    "dove": "enemy_response_dove",
    "loyalist": "enemy_response_loyalist",
}


def get_enemy_response_template(
    target_nation: str,
    outcome: str,
    world,
) -> Dict:
    """Get personality-keyed enemy response template.

    Looks up the target nation's diplomat personality and returns
    the appropriate T24-T27 template variant.

    Args:
        target_nation: The responding nation
        outcome: "accept", "counter", or "reject"
        world: WorldState (for diplomat lookup)

    Returns:
        Template dict with personality-appropriate text
    """
    # Look up diplomat personality
    diplomats = getattr(world, 'diplomats', {})
    diplomat = diplomats.get(target_nation)
    personality = getattr(diplomat, 'personality', 'loyalist') if diplomat else 'loyalist'

    template_key = _PERSONALITY_TO_TEMPLATE.get(personality, "enemy_response_loyalist")

    # Try exact match: (template_key, "any", outcome)
    key = (template_key, "any", outcome)
    if key in DIPLOMATIC_TEMPLATES:
        template = _deep_copy_template(DIPLOMATIC_TEMPLATES[key])
        return template

    # Fallback to loyalist
    key = ("enemy_response_loyalist", "any", outcome)
    if key in DIPLOMATIC_TEMPLATES:
        template = _deep_copy_template(DIPLOMATIC_TEMPLATES[key])
        return template

    # Ultimate fallback
    return {
        "text": f"{target_nation} responds to your proposal.",
        "options": [
            {"label": "Noted", "description": "Dismiss.", "action": "dismiss"},
        ],
        "recommendation": 0,
    }


def resolve_enemy_response_text(template: Dict, world, target_nation: str) -> str:
    """Resolve slots in an enemy response template.

    Resolves {target_diplomat} and {target_nation} slots.

    Args:
        template: Template dict from get_enemy_response_template()
        world: WorldState
        target_nation: The responding nation

    Returns:
        Resolved text string
    """
    text = template.get("text", "")
    return resolve_template_text(text, world, target_nation)


def _accumulate_raw_treaty_harshness(treaty: Dict) -> float:
    """Sum the raw clause + demand harshness weights without any clamp.

    Internal helper shared by `calculate_treaty_harshness()` (1.0-clamped,
    bilateral) and `calculate_raw_treaty_harshness()` (unclamped, used by
    the common-peace acceptance formula's `term_harshness_penalty` per
    `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` §6.acceptance line 1115).
    """
    harshness = 0.0
    for clause in treaty.get("clauses", []):
        ctype = clause.get("type", "")
        if ctype == "gold_per_turn":
            # SC-33 / G2-Slice-9: finite-duration recurring gold (settlement
            # clauses carry an explicit `turns` field) uses the lump-sum
            # gold-indemnity weight (`0.08 per 100 gold`) applied to the
            # full projected obligation `amount * turns`. Bilateral
            # treaties record `gold_per_turn` without a `turns` field —
            # those are perpetual streams and keep the original per-turn
            # weight so existing bilateral acceptance is not perturbed.
            turns = int(clause.get("turns", 0) or 0)
            if turns > 0:
                harshness += 0.08 * (
                    (clause.get("amount", 0) or 0) * turns / 100
                )
            else:
                harshness += 0.1 * (clause.get("amount", 0) / 100)
        elif ctype == "gold_indemnity":
            # Gate-4 G4F-1: settlement lump-sum gold uses the same
            # 0.08-per-100-gold weight as the bilateral `gold_lump` demand.
            # The settlement type name was never priced here, so ratified
            # common-peace treaty records (settlement_ratify rates
            # `{"clauses": pair_terms}`) stored zero gold harshness.
            harshness += 0.08 * ((clause.get("amount", 0) or 0) / 100)
        elif ctype == "territory_cede":
            # Settlement clauses carry a singular `region`; bilateral treaty
            # clauses carry a `regions` list. Count whichever is present so
            # the settlement shape no longer rates 0.0 (G4F-1).
            regions = clause.get("regions", [])
            region_count = (
                len(regions) if regions else (1 if clause.get("region") else 0)
            )
            harshness += 0.3 * region_count
        elif ctype == "manpower_per_turn":
            harshness += 0.15
        elif ctype == "forced_alliance":
            harshness += 0.4
        elif ctype == "liberation":
            harshness += 0.3
        elif ctype in ("vassalage", "subjugation"):
            # Settlement dependency clauses (G4F-1): the same 0.5 weight the
            # demands dialect applies. Bilateral clauses never carry these
            # type names, so bilateral sums are unchanged.
            harshness += 0.5
        elif ctype == "vassal_transfer":
            # VS-5: losing an existing satellite weighs like liberation
            # (the lord loses a client, but no NEW nation is subjugated).
            harshness += 0.3
    # PL-12-B: Include demands in harshness calculation
    for demand in treaty.get("demands", []):
        if not isinstance(demand, dict):
            continue
        dtype = demand.get("type", "")
        amt = abs(demand.get("value", 0) or demand.get("amount", 0) or 0)
        if dtype == "gold_per_turn":
            # SC-33 / G2-Slice-9: finite settlement-style stream projects
            # to lump-sum weight; bilateral perpetual stream keeps the
            # legacy per-turn weight. See clause branch above for details.
            d_turns = int(demand.get("turns", 0) or 0)
            if d_turns > 0:
                harshness += 0.08 * (amt * d_turns / 100)
            else:
                harshness += 0.1 * (amt / 100)
        elif dtype in ("territory_cede", "territory"):
            regions = demand.get("regions", [])
            count = len(regions) if regions else max(1, amt)
            harshness += 0.3 * count
        elif dtype == "ap_per_turn":
            harshness += 0.3 * max(1, amt)
        elif dtype == "manpower_per_turn":
            harshness += 0.15
        elif dtype in ("gold_lump", "gold_indemnity"):
            # Gate-4 G4F-1: `gold_indemnity` is the settlement name for the
            # same lump-sum demand — it fell through unmatched, so every
            # settlement gold demand priced at ZERO acceptance cost and the
            # Harsher/Ease gold dials could never move a court's score.
            harshness += 0.08 * (amt / 100)
        elif dtype in ("manpower_infantry", "manpower_cavalry", "manpower_artillery", "manpower"):
            harshness += 0.15
        elif dtype == "forced_alliance":
            harshness += 0.4
        elif dtype == "liberation":
            harshness += 0.3
        elif dtype in ("vassalage", "subjugation"):
            harshness += 0.5
        elif dtype == "vassal_transfer":
            harshness += 0.3  # VS-5 — mirrors the clause branch above
    return harshness


def calculate_treaty_harshness(treaty: Dict) -> float:
    """Calculate harshness score (0.0-1.0) from treaty clauses AND demands.

    Used for DD8-4 escalating harshness tracking and PL-12 acceptance penalty.
    Bilateral acceptance callers MUST keep using this 1.0-clamped helper.
    Common-peace acceptance must call `calculate_raw_treaty_harshness()`
    instead — the 1.5 ceiling is applied inside the C1b acceptance helper.
    """
    return min(1.0, _accumulate_raw_treaty_harshness(treaty))


def get_treaty_harshness_for_consumer(
    treaty: Dict,
    *,
    consumer: str = "common_peace",
) -> float:
    """SC-24: pick the right harshness scale for a treaty record.

    Common-peace consumers (ledger, AI proposal generation, coalition
    threat interpretation, dispatch one-liners, notification warnings)
    read the raw common-peace harshness (`raw_harshness`) so authored
    multi-clause packages that exceed 1.0 stay legible. Legacy bilateral
    consumers may still read the 1.0-clamped `harshness` field.

    Treaty records produced by `_record_common_peace_treaties` carry
    both fields plus a `source="common_peace"` tag. Records that pre-
    date SC-24 (or come from bilateral ratification) only carry the
    legacy clamped field; this helper falls back to it transparently.
    """
    if not isinstance(treaty, Mapping):
        return 0.0
    consumer = str(consumer or "").lower()
    source = str(treaty.get("source") or "").lower()
    if consumer in {
        "diplomatic_ledger",
        "ai_diplomacy",
        "coalition",
        "dispatch",
        "notifications",
    } and source == "common_peace":
        if "raw_harshness" in treaty:
            try:
                return float(treaty.get("raw_harshness") or 0.0)
            except (TypeError, ValueError):
                pass
    if "raw_harshness" in treaty and consumer == "common_peace_acceptance":
        try:
            return float(treaty.get("raw_harshness") or 0.0)
        except (TypeError, ValueError):
            pass
    try:
        return float(treaty.get("harshness") or treaty.get("clamped_harshness") or 0.0)
    except (TypeError, ValueError):
        return 0.0


def calculate_raw_treaty_harshness(treaty: Dict) -> float:
    """Unclamped sum of treaty clause + demand harshness weights.

    Used exclusively by common-peace acceptance per
    `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` §6.acceptance line 1115:

        term_harshness_penalty =
            -min(45, round((min(raw_total_harshness, 1.5) / 1.5) * 45))

    The 1.5 ceiling is applied at the acceptance helper, NOT here, so
    callers can audit the raw weight (settlement reviews show this in
    debug output) and detect packages that exceed the spec's
    settlement-tier harshness ceilings (white_peace 0.10 / favorable_terms
    0.25 / dictated_terms 0.45 / harsh_peace 0.70 / total_victory 1.00 —
    spec §6.acceptance line 1188-1196).
    """
    return _accumulate_raw_treaty_harshness(treaty)


# ═══════ BPH-A: TERM OWNERSHIP ANNOTATION ═══════

_TERM_DISPLAY_LABELS = {
    "territory_cede": "{from_nation} cedes {detail} to {to_nation}",
    "territory": "{from_nation} cedes {detail} to {to_nation}",
    "territory_return": "{from_nation} returns {detail} to {to_nation}",
    "gold_lump": "{from_nation} pays {value} gold to {to_nation}",
    "gold_per_turn": "{from_nation} pays {value} gold per turn to {to_nation}",
    "manpower_infantry": "{from_nation} transfers {value} infantry to {to_nation}",
    "manpower_cavalry": "{from_nation} transfers {value} cavalry to {to_nation}",
    "manpower_artillery": "{from_nation} transfers {value} artillery to {to_nation}",
    "ap_per_turn": "{from_nation} cedes {value} AP per turn to {to_nation}",
    "open_borders": "Mutual open borders between {nation_a} and {nation_b}",
    "military_access": "{from_nation} grants military access to {to_nation}",
    "protection": "{from_nation} guarantees {to_nation}'s sovereignty",
    "protection_promised": "{from_nation} guarantees {to_nation}'s sovereignty",
    "continental_system_lifted": "{from_nation} closes ports to Britain",
    "forced_alliance": "{from_nation} enters ALLIANCE with {to_nation} and joins the Continental System",
    "liberation": "{from_nation} is liberated from vassalage",
    # VS-5: vassal re-homing — `detail` carries the transferred court's name
    "vassal_transfer": "{from_nation} yields its vassal {detail} to {to_nation}",
    # W6-7 Marshal Fates: ransom clause summary. Marshal-name-free — the
    # shared label formatter only carries nation/detail/value kwargs.
    "prisoner_return": "{from_nation} releases a captured marshal to {to_nation}",
}


_VASSAL_TERRITORY_ADJECTIVES = {
    "Bavaria": "Bavarian",
    "Saxony": "Saxon",
}


def _safe_int(value, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def _coerce_regions(raw_regions) -> list:
    if not raw_regions:
        return []
    if isinstance(raw_regions, str):
        return [raw_regions]
    try:
        return [str(region) for region in raw_regions if region]
    except TypeError:
        return []


def _vassal_territory_label(vassal_nation: str) -> str:
    adjective = _VASSAL_TERRITORY_ADJECTIVES.get(vassal_nation, vassal_nation)
    return f"{adjective} territory"


def _get_vassal_nation(term: Dict) -> str:
    if not isinstance(term, dict):
        return ""
    return (
        term.get("vassal_nation")
        or term.get("vassal_name")
        or term.get("vassal")          # VS-5: the vassal_transfer subject
        or term.get("territory_nation")
        or term.get("sovereign_nation")
        or term.get("original_owner")
        or ""
    )


def _build_display_label(clause_type: str, from_nation: str, to_nation: str,
                         regions: list, value: int, vassal_nation: str = "") -> str:
    template = _TERM_DISPLAY_LABELS.get(clause_type)
    if not template:
        from backend.display_names import clause_display_name
        return clause_display_name(clause_type)

    detail = ", ".join(regions) if regions else "territory"
    if vassal_nation and clause_type in ("territory_cede", "territory", "territory_return"):
        detail = f"{detail} ({_vassal_territory_label(vassal_nation)})"
    elif vassal_nation and clause_type == "vassal_transfer":
        # VS-5: `detail` names the transferred court, not a region list
        detail = vassal_nation
    return template.format(
        from_nation=from_nation, to_nation=to_nation,
        detail=detail, value=int(value),
        nation_a=from_nation, nation_b=to_nation,
    )


def annotate_peace_terms(terms: Dict, proposer_nation: str, target_nation: str) -> list:
    """Annotate every clause/sweetener/demand with ownership fields per BPH §7.1.

    Returns a list of annotated term dicts, each with:
      clause_type, from_nation, to_nation, regions, term_direction,
      sweetener_value (if applicable), display_label
    """
    annotated = []
    explicit_concession_regions = set()
    for sweetener in terms.get("sweeteners", []):
        if not isinstance(sweetener, dict):
            continue
        if sweetener.get("type") in ("territory_cede", "territory"):
            explicit_concession_regions.update(
                region.strip().lower()
                for region in _coerce_regions(sweetener.get("regions", []))
                if region
            )

    for sweetener in terms.get("sweeteners", []):
        if not isinstance(sweetener, dict):
            continue
        stype = sweetener.get("type", "")
        regions = _coerce_regions(sweetener.get("regions", []))
        value = _safe_int(sweetener.get("value", 0))
        vassal_nation = _get_vassal_nation(sweetener)
        annotated.append({
            "clause_type": stype,
            "from_nation": proposer_nation,
            "to_nation": target_nation,
            "regions": regions,
            "term_direction": "concession",
            "sweetener_value": value,
            "display_label": _build_display_label(
                stype, proposer_nation, target_nation, regions, value, vassal_nation),
        })

    for demand in terms.get("demands", []):
        if not isinstance(demand, dict):
            continue
        dtype = demand.get("type", "")
        regions = _coerce_regions(demand.get("regions", []))
        value = _safe_int(demand.get("value", 0))
        vassal_nation = _get_vassal_nation(demand)
        annotated.append({
            "clause_type": dtype,
            "from_nation": target_nation,
            "to_nation": proposer_nation,
            "regions": regions,
            "term_direction": "demand",
            "sweetener_value": -value if value else 0,
            "display_label": _build_display_label(
                dtype, target_nation, proposer_nation, regions, value, vassal_nation),
        })

    for clause in terms.get("clauses", []):
        if isinstance(clause, str):
            ctype = clause
            regions = []
            value = 0
            vassal_nation = ""
        elif isinstance(clause, dict):
            ctype = clause.get("type", "")
            regions = _coerce_regions(clause.get("regions", []))
            value = _safe_int(clause.get("value", 0))
            vassal_nation = _get_vassal_nation(clause)
        else:
            continue

        if ctype in ("open_borders",):
            annotated.append({
                "clause_type": ctype,
                "from_nation": proposer_nation,
                "to_nation": target_nation,
                "regions": [],
                "term_direction": "mutual",
                "sweetener_value": 0,
                "display_label": _build_display_label(ctype, proposer_nation, target_nation, [], 0),
            })
        elif ctype == "protection_promised":
            annotated.append({
                "clause_type": ctype,
                "from_nation": proposer_nation,
                "to_nation": target_nation,
                "regions": [],
                "term_direction": "concession",
                "sweetener_value": 0,
                "display_label": _build_display_label(ctype, proposer_nation, target_nation, [], 0),
            })
        elif ctype == "continental_system_lifted":
            annotated.append({
                "clause_type": ctype,
                "from_nation": target_nation,
                "to_nation": proposer_nation,
                "regions": [],
                "term_direction": "demand",
                "sweetener_value": 0,
                "display_label": _build_display_label(ctype, target_nation, proposer_nation, [], 0),
            })
        elif ctype == "military_access":
            granting = proposer_nation
            receiving = target_nation
            if isinstance(clause, dict):
                granting = (
                    clause.get("granting_nation")
                    or clause.get("from_nation")
                    or clause.get("from")
                    or granting
                )
                receiving = (
                    clause.get("receiving_nation")
                    or clause.get("to_nation")
                    or clause.get("to")
                    or receiving
                )
            direction = "mutual"
            if granting == proposer_nation and receiving == target_nation:
                direction = "concession"
            elif granting == target_nation and receiving == proposer_nation:
                direction = "demand"
            annotated.append({
                "clause_type": ctype,
                "from_nation": granting,
                "to_nation": receiving,
                "regions": [],
                "term_direction": direction,
                "sweetener_value": 0,
                "display_label": _build_display_label(ctype, granting, receiving, [], 0),
            })
        elif ctype.startswith("territory_"):
            region_name = ctype.split("_", 1)[1] if "_" in ctype else ""
            if region_name and region_name not in ("cede", "return"):
                if region_name.strip().lower() in explicit_concession_regions:
                    continue
                annotated.append({
                    "clause_type": "territory_cede",
                    "from_nation": proposer_nation,
                    "to_nation": target_nation,
                    "regions": [region_name.title()],
                    "term_direction": "concession",
                    "sweetener_value": 0,
                    "display_label": _build_display_label(
                        "territory_cede", proposer_nation, target_nation,
                        [region_name.title()], 0),
                })
            else:
                annotated.append({
                    "clause_type": ctype,
                    "from_nation": proposer_nation,
                    "to_nation": target_nation,
                    "regions": regions,
                    "term_direction": "concession",
                    "sweetener_value": 0,
                    "display_label": _build_display_label(
                        ctype, proposer_nation, target_nation, regions, value, vassal_nation),
                })
        else:
            annotated.append({
                "clause_type": ctype,
                "from_nation": proposer_nation,
                "to_nation": target_nation,
                "regions": regions,
                "term_direction": "mutual",
                "sweetener_value": 0,
                "display_label": _build_display_label(
                    ctype, proposer_nation, target_nation, regions, value, vassal_nation),
            })

    return annotated
