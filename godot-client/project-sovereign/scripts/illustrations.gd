extends RefCounted
class_name Illustrations

# =============================================================================
# Session UI-5 (November 12, 2026) — the pictures: one catalogue.
# =============================================================================
# Period paintings and engravings (public domain, Wikimedia Commons; every one
# credited in THIRD_PARTY_LICENSES.md and on Settings → CREDITS) illustrate the
# letters and the reading screens, as a commercial strategy game illustrates
# its events. Each picture exists twice in assets/ui/illustrations/, made by
# tools/ui5_illustrations.py with one treatment (a warm grade toward the
# parchment, a soft vignette): `<key>_banner.jpg` (3:1, for letters and
# headers) and `<key>_plate.jpg` (16:9, for the campaign end).
#
# A surface asks by MEANING — `for_letter(payload)` or `for_surface(name)` —
# and gets a path; every key falls back along FALLBACK to a family picture, so
# no surface is ever handed a missing file. Nothing here is cached: Godot's
# own ResourceLoader keeps a loaded texture.
# A banner is the FIRST thing to step aside on a compact view (the end card's
# crest rule) — `banner_height(width)` answers 0 there.
# =============================================================================

const DIR := "res://assets/ui/illustrations/"

# key -> {title, artist, year}. Filled from the sourcing record.
const WORKS := {
	"council": {"title": "Kutuzov's Council of War at Fili", "artist": "Aleksey Kivshenko", "year": 1880},
	"court": {"title": "The Distribution of the Eagle Standards", "artist": "Jacques-Louis David", "year": 1810},
	"coronation": {"title": "The Coronation of Napoleon", "artist": "Jacques-Louis David", "year": 1807},
	"treaty": {"title": "The Meeting of Napoleon and Francis II after Austerlitz", "artist": "Antoine-Jean Gros", "year": 1812},
	"tilsit": {"title": "The Meeting of Napoleon and Alexander I at Tilsit", "artist": "Adolphe Roehn", "year": 1808},
	"congress": {"title": "The Congress of Vienna", "artist": "after Jean-Baptiste Isabey", "year": 1819},
	"study": {"title": "The Emperor Napoleon in His Study at the Tuileries", "artist": "Jacques-Louis David", "year": 1812},
	"talleyrand": {"title": "Talleyrand, Prince of Benevento", "artist": "François Gérard", "year": 1808},
	"courier": {"title": "An Officer of the Chasseurs of the Guard, Charging", "artist": "Théodore Géricault", "year": 1812},
	"moniteur": {"title": "The Arrival of a Stage-coach at the Messageries", "artist": "Louis-Léopold Boilly", "year": 1803},
	"ceremony": {"title": "The Legion of Honour Given at the Boulogne Camp", "artist": "Philippe-Auguste Hennequin", "year": 1806},
	"te_deum": {"title": "Notre-Dame's Choir Dressed for the Coronation", "artist": "Charles Percier", "year": 1804},
	"treasury": {"title": "The Port of Bayonne", "artist": "Joseph Vernet", "year": 1755},
	"fleet": {"title": "The Redoutable at Trafalgar", "artist": "Louis-Philippe Crépin", "year": 1806},
	"rising": {"title": "The Second of May 1808", "artist": "Francisco Goya", "year": 1814},
	"repression": {"title": "The Third of May 1808", "artist": "Francisco Goya", "year": 1814},
	"disasters": {"title": "The Disasters of War, plate 30: Ravages of War", "artist": "Francisco Goya", "year": 1810},
	"retreat": {"title": "Napoleon's Retreat from Moscow", "artist": "Adolph Northen", "year": 1851},
	"fontainebleau": {"title": "Napoleon at Fontainebleau, 31 March 1814", "artist": "Paul Delaroche", "year": 1846},
	"arcole": {"title": "Bonaparte at the Pont d'Arcole", "artist": "Antoine-Jean Gros", "year": 1796},
	"horatii": {"title": "The Oath of the Horatii", "artist": "Jacques-Louis David", "year": 1784},
	"pius_vii": {"title": "Pope Pius VII", "artist": "Jacques-Louis David", "year": 1806},
	"santo_domingo": {"title": "The Capture of Gros-Morne, Saint-Domingue, 1802", "artist": "Martinet and Réville", "year": 1836},
	"camp": {"title": "Napoleon's Bivouac on the Eve of Wagram", "artist": "Adolphe Roehn", "year": 1810},
	"horses": {"title": "The Horse Fair", "artist": "Rosa Bonheur", "year": 1855},
	"convoy": {"title": "The Crossing of the Berezina", "artist": "Peter von Hess", "year": 1844},
	"berlin": {"title": "Napoleon Entering Berlin", "artist": "Charles Meynier", "year": 1810},
	"ulm": {"title": "The Surrender of Ulm", "artist": "Charles Thévenin", "year": 1815},
	"borodino": {"title": "The Battle of Borodino", "artist": "Louis-François Lejeune", "year": 1822},
	"somosierra": {"title": "The Battle of Somosierra", "artist": "Louis-François Lejeune", "year": 1810},
	"aboukir": {"title": "The Battle of Aboukir", "artist": "Antoine-Jean Gros", "year": 1806},
	"copenhagen": {"title": "The Battle of Copenhagen, 2 April 1801", "artist": "Nicholas Pocock", "year": 1806},
	"marengo": {"title": "The Battle of Marengo", "artist": "Louis-François Lejeune", "year": 1801},
	"wedding": {"title": "The Marriage of Prince Eugène and Princess Augusta of Bavaria", "artist": "François-Guillaume Ménageot", "year": 1808},
	"holland": {"title": "Louis Bonaparte, King of Holland", "artist": "Charles Howard Hodges", "year": 1809},
	"reich": {"title": "Francis II, the Last Holy Roman Emperor", "artist": "Friedrich von Amerling", "year": 1832},
}

# When a picture is absent, its family's stands in (a chain, never a loop).
const FALLBACK := {
	"council": "camp", "court": "coronation", "treaty": "tilsit", "tilsit": "court",
	"congress": "treaty", "talleyrand": "study", "courier": "study", "moniteur": "courier",
	"ceremony": "court", "te_deum": "ceremony", "treasury": "study", "fleet": "marengo",
	"rising": "repression", "repression": "disasters", "disasters": "retreat",
	"retreat": "marengo", "fontainebleau": "study", "arcole": "marengo",
	"horatii": "study", "pius_vii": "court", "santo_domingo": "fleet", "camp": "study",
	"horses": "camp", "convoy": "camp", "berlin": "marengo",
	"ulm": "marengo", "borodino": "marengo", "somosierra": "marengo",
	"aboukir": "marengo", "copenhagen": "fleet", "wedding": "court", "holland": "court",
	"reich": "court", "coronation": "court", "marengo": "camp", "study": "camp",
}

# An authored letter's template (the payload's `moment_id`, before any "#N").
const LETTER_BY_TEMPLATE := {
	"chancellors_letters": "study",
	"the_host": "camp",
	"berthiers_memorial": "camp",
	"santo_domingo": "santo_domingo",
	"the_magazines": "convoy",
	"the_remounts": "horses",
	"camps_of_instruction": "ceremony",
	"the_proclamation": "arcole",
	"the_bank": "treasury",
	"the_popes_ports": "pius_vii",
	"the_people_stir": "rising",
	"the_ulcer": "disasters",
	"the_nation_in_arms": "horatii",
	"bavarian_match": "wedding",
	"throne_of_holland": "holland",
	"crown_of_the_reich": "reich",
	"decree_of_berlin": "berlin",
}

# A court's own letter (an envoy's, not an affair or a moment) by its court.
const LETTER_BY_COURT := {"Russia": "council"}

# A court's letter by what it proposes (`proposal_type`, matched by substring).
const LETTER_BY_PROPOSAL := [
	["armistice", "treaty"], ["peace", "treaty"], ["settlement", "tilsit"],
	["alliance", "tilsit"], ["trade", "treasury"], ["subsidy", "treasury"],
	["loan", "treasury"], ["marriage", "wedding"], ["vassal", "court"],
	["protect", "court"], ["ultimatum", "camp"], ["war", "camp"],
	["coalition", "congress"], ["call_to_arms", "camp"], ["petition", "court"],
	["recognition", "coronation"], ["crown", "coronation"],
]

# A surface by name; "war:<court>" and "campaign_end:<style>" are resolved below.
# The interim blind reading (November 13) saw one bivouac on three sheets in a
# row (the petition, the memorial, the objection) and a portrait cropped to its
# eyes in the Cabinet's strip: each surface has its own picture, and a strip
# header carries a wide scene, never a face.
const SURFACES := {
	"dispatch": "courier", "gazette": "moniteur", "cabinet": "congress",
	"correspondence": "treaty",
	"congress": "congress", "settlement": "tilsit", "rebellion": "rising",
	"sabotage": "talleyrand", "paradox": "horatii", "school": "arcole",
	"redemption": "talleyrand", "interrupt": "camp", "coalition": "congress",
	"proclamation": "ceremony", "reward": "ceremony", "objection": "council",
	"petition": "court", "capture": "berlin", "charge": "horses",
	"enemy_phase": "marengo", "strategic_report": "camp", "te_deum": "te_deum",
}
const WAR_BY_COURT := {
	"Austria": "ulm", "Russia": "borodino", "Spain": "somosierra", "Portugal": "somosierra",
	"Ottoman": "aboukir", "Denmark": "copenhagen", "Sweden": "copenhagen",
	"Britain": "fleet", "Prussia": "berlin", "Saxony": "berlin", "Hanover": "berlin",
	"Hesse": "berlin", "Bavaria": "ulm", "Naples": "marengo", "Sardinia": "marengo",
	"PapalStates": "pius_vii", "Holland": "holland", "KingdomOfItaly": "marengo",
	"Switzerland": "marengo",
}
const END_BY_STYLE := {
	"imperial_peace": "coronation", "decisive_peace": "treaty", "humbled_peace": "fontainebleau",
	"fall": "retreat", "verdict": "study",
}


static func path_of(key: String, form: String = "banner") -> String:
	"""The file for `key` in `form` ("banner" | "plate"), walking the fallback
	chain to the first picture on disk; "" only when none of the family is."""
	var seen := {}
	var k := key
	while k != "" and not seen.has(k):
		seen[k] = true
		var p := DIR + k + "_" + form + ".jpg"
		if ResourceLoader.exists(p):
			return p
		k = String(FALLBACK.get(k, ""))
	return ""


static func key_for_letter(payload: Dictionary) -> String:
	var template := str(payload.get("moment_id", "")).split("#")[0]
	if LETTER_BY_TEMPLATE.has(template):
		return String(LETTER_BY_TEMPLATE[template])
	var court := str(payload.get("from_nation", ""))
	var register := str(payload.get("register", ""))
	if register == "" and LETTER_BY_COURT.has(court):
		return String(LETTER_BY_COURT[court])
	var kind := str(payload.get("proposal_type", "")).to_lower()
	for pair in LETTER_BY_PROPOSAL:
		if kind.find(String(pair[0])) >= 0:
			return String(pair[1])
	if register == "affair":
		return "study"
	if register == "moment":
		return "court"
	return "courier"


static func for_letter(payload: Dictionary, form: String = "banner") -> String:
	return path_of(key_for_letter(payload), form)


static func key_for_surface(surface: String) -> String:
	if surface.begins_with("war:"):
		return String(WAR_BY_COURT.get(surface.substr(4), "marengo"))
	if surface.begins_with("campaign_end:"):
		return String(END_BY_STYLE.get(surface.substr(13), "study"))
	return String(SURFACES.get(surface, "study"))


static func for_surface(surface: String, form: String = "banner") -> String:
	return path_of(key_for_surface(surface), form)


static func credit(key: String) -> String:
	"""'Title — Artist (year)' for a hover or a caption; "" when unrecorded."""
	var work: Dictionary = WORKS.get(key, {})
	var title := str(work.get("title", ""))
	if title == "":
		return ""
	var artist := str(work.get("artist", ""))
	var year := int(work.get("year", 0))
	var tail := (" — " + artist) if artist != "" else ""
	if year > 0:
		tail += " (%d)" % year
	return title + tail


static func credit_for_path(path: String) -> String:
	var key := path.get_file().get_basename().trim_suffix("_banner").trim_suffix("_plate")
	return credit(key)


static func banner_height(width: float) -> float:
	"""How tall a 3:1 banner stands at `width` — 0 on the compact view (it is
	the first thing to step aside there) and never over 22 % of the view."""
	if Utils.compact_view():
		return 0.0
	var view_h := 900.0
	var ml := Engine.get_main_loop()
	if ml is SceneTree and (ml as SceneTree).root != null:
		view_h = (ml as SceneTree).root.get_visible_rect().size.y
	return minf(width / 3.0, view_h * 0.22)


# The top bar's band and its margin: a centred card stands at or below it
# (SF-RR5's rule — "below the bar and inside the window").
const BAR_BAND := 44.0
const BANNER_FLOOR := 72.0     # under this a banner steps aside rather than stand as a strip


static func card_room(view_h: float) -> float:
	"""The tallest a centred card may stand and keep its top below the bar."""
	return view_h - 2.0 * BAR_BAND


static func fit_banner_to_card(panel: Control, view_h: float) -> bool:
	"""A card's banner gives up its height first: shrunk until the card stands
	in `card_room`, it steps aside under BANNER_FLOOR. True while it stands."""
	var pic := panel.find_child("Illustration", true, false) as Control
	if pic == null or not pic.visible:
		return false
	var over := panel.get_combined_minimum_size().y - card_room(view_h)
	if over <= 0.0:
		return true
	var h := pic.custom_minimum_size.y - over
	if h < BANNER_FLOOR:
		pic.visible = false
		return false
	pic.set_meta("banner_cap", h)
	pic.custom_minimum_size = Vector2(0, h)
	return true


static func make_banner(surface_or_path: String, width: float = 0.0, follow_width: bool = false) -> TextureRect:
	"""A ready banner node (null when there is no picture or no room): the
	picture cropped to fill, its credit as the hover. `follow_width`: the height
	follows the width the banner is actually laid out at — a card measured
	before its fitter ran asked for a sliver (the interim shoot's objection
	banner stood 48 px tall over a 560-px card)."""
	var path := surface_or_path if surface_or_path.begins_with("res://") else for_surface(surface_or_path)
	if path == "" or not ResourceLoader.exists(path):
		return null
	var rect := TextureRect.new()
	rect.name = "Illustration"
	rect.texture = load(path)
	rect.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	rect.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
	rect.mouse_filter = Control.MOUSE_FILTER_PASS
	rect.tooltip_text = credit_for_path(path)
	if width > 0.0:
		var h := banner_height(width)
		if h <= 0.0:
			rect.free()
			return null
		rect.custom_minimum_size = Vector2(0, h)
		if follow_width:
			rect.resized.connect(func(): _refit_banner(rect))
	return rect


static func _refit_banner(rect: TextureRect) -> void:
	"""`follow_width`'s hook: the 3:1 height of the width the banner got, never
	over the cap a card's fit gave it (`fit_banner_to_card`)."""
	if not is_instance_valid(rect) or rect.size.x <= 1.0:
		return
	var h := banner_height(rect.size.x)
	if rect.has_meta("banner_cap"):
		h = minf(h, float(rect.get_meta("banner_cap")))
	if h <= 0.0:
		return
	if absf(rect.custom_minimum_size.y - h) > 1.0:
		rect.custom_minimum_size = Vector2(0, h)
