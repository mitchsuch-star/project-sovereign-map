extends RefCounted
class_name VoiceLine

# =============================================================================
# Row IC, Session 4 (IC-13, the voice): ONE helper for "a marshal's quoted line
# with his portrait and name beside it". The server sends `{speaker, says}`;
# every surface that shows what a marshal SAID draws it through here, so the
# line is always in curly quotes (never doubled) and always beside his name.
#
#   make(speaker, says, plain)  - a Control row: locket + name + line (+ plain)
#   bbcode(speaker, says)       - "[b]Name[/b]: “line”" for a RichTextLabel
#   quoted(says)                - just the “line”, escaped, for a text row
#   rows(list)                  - a `voices` array as a list of `make` rows
# =============================================================================

const LOCKET_PX := 38.0
const MAX_TEXT_PX := 360.0


static func clean(says: String) -> String:
	# The server may hand the line already wrapped (curly, or plain) - ONE
	# matching pair is taken off, so it is never doubled; a quote INSIDE the
	# line, or at one end only (Tell Mack "go"), is his own and stays.
	var s := says.strip_edges()
	if s.length() >= 2:
		if (s.begins_with("“") and s.ends_with("”")) 				or (s.begins_with("\"") and s.ends_with("\"")):
			s = s.substr(1, s.length() - 2).strip_edges()
	return s


static func _escape(text: String) -> String:
	return text.replace("[", "\u0001").replace("]", "[rb]").replace("\u0001", "[lb]")


static func quoted(says: String) -> String:
	var line := clean(says)
	if line == "":
		return ""
	return "“" + _escape(line) + "”"


static func plain_text(speaker: String, says: String) -> String:
	"""`Name: “line”` as plain text, for a tooltip."""
	var line := clean(says)
	if line == "":
		return ""
	var who := Utils.display_marshal_name(speaker)
	return ((who + ": ") if who != "" else "") + "“" + line + "”"


# Row IC, Session 4 (IC-13): "his portrait and name stand beside his line" on
# the TEXT surfaces too (the terminal, the read-back, the morning's report are
# RichTextLabels): a small inline portrait, cropped to the centre square the
# round locket shows (`PortraitLocket` - KEEP_ASPECT_COVERED). "" for a man
# with no portrait file (the name alone stands).
const INLINE_PX := 26
static var _inline_cache := {}   # speaker -> "[img ...]path[/img] " or ""


static func portrait_bbcode(speaker: String) -> String:
	if _inline_cache.has(speaker):
		return str(_inline_cache[speaker])
	var out := ""
	var path := PortraitLocket._portrait_path(speaker)
	if path != "":
		var tex := load(path) as Texture2D
		if tex != null:
			var w := int(tex.get_width())
			var h := int(tex.get_height())
			var side := mini(w, h)
			var x := int((w - side) / 2.0)
			var y := int((h - side) / 2.0)
			out = "[img width=%d height=%d region=%d,%d,%d,%d]%s[/img] " % [
				INLINE_PX, INLINE_PX, x, y, side, side, path]
	_inline_cache[speaker] = out
	return out


static func bbcode(speaker: String, says: String) -> String:
	var line := quoted(says)
	if line == "":
		return ""
	var who := Utils.display_marshal_name(speaker)
	if who == "":
		return line
	return portrait_bbcode(speaker) + "[b]" + _escape(who) + "[/b]: " + line


static func make(speaker: String, says: String, plain: String = "") -> Control:
	var row := HBoxContainer.new()
	row.name = "VoiceLine"
	row.add_theme_constant_override("separation", 8)
	row.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.mouse_filter = Control.MOUSE_FILTER_IGNORE

	var locket := PortraitLocket.new()
	locket.setup(speaker, LOCKET_PX, false)
	locket.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	row.add_child(locket)

	var column := VBoxContainer.new()
	column.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	column.add_theme_constant_override("separation", 2)
	column.mouse_filter = Control.MOUSE_FILTER_IGNORE
	row.add_child(column)

	var who := Label.new()
	who.name = "Name"
	who.text = Utils.display_marshal_name(speaker)
	who.theme_type_variation = &"Caption"
	who.add_theme_color_override("font_color", Utils.UI_GOLD_BRIGHT)
	who.mouse_filter = Control.MOUSE_FILTER_IGNORE
	column.add_child(who)

	var line := Label.new()
	line.name = "Line"
	line.text = "“" + clean(says) + "”"
	line.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	line.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	line.custom_minimum_size = Vector2(0, 0)
	line.mouse_filter = Control.MOUSE_FILTER_IGNORE
	column.add_child(line)

	if plain.strip_edges() != "":
		var note := Label.new()
		note.name = "Plain"
		note.text = plain.strip_edges()
		note.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		note.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		note.theme_type_variation = &"Caption"
		note.add_theme_color_override("font_color", Utils.toned(Utils.UI_TEXT_DIM))
		note.mouse_filter = Control.MOUSE_FILTER_IGNORE
		column.add_child(note)
	return row


static func rows(list: Array) -> Array:
	var out: Array = []
	for entry in list:
		if not (entry is Dictionary):
			continue
		var said := str((entry as Dictionary).get("says", "")).strip_edges()
		if clean(said) == "":
			continue
		out.append(make(str((entry as Dictionary).get("speaker", "")), said))
	return out
