extends SceneTree
# Session UI-6 (November 13, 2026) — UI6-X22, THE SCROLL THAT FLIPPED FOREVER.
#
#   Godot --headless --path godot-client/project-sovereign \
#         --script <abs path>/tools/ui6_scroll_flip_probe.gd -- <bbcode file> <out json> <auto|reserve>
#
# The province panel's own nesting (a PanelContainer, a VBox, a ScrollContainer
# whose RichTextLabel fills its width with fit_content), the shipped Text size
# (115 %), Interface Scale 2.0, the panel 360 px wide and its scroll 335 px tall
# — the geometry the full shoot hung on (Paris, the compact view). The text is
# the panel's own BBCode for Paris, dumped at that moment
# (tests/fixtures/ui6_scroll_flip_paris.bbcode).
#
# Its height is not monotonic in its width: 336 px tall at 336 px wide (one
# more than the scroll — the bar shows), 333 px tall at 328 (the bar's 8 px
# gone — the bar is not needed, it hides). In SCROLL_MODE_AUTO the container
# re-sorts on every flip and Godot runs the queued sorts inside ONE frame
# until the queue is empty: it never is — the frame never ends and the memory
# climbs until the engine dies (signal 11). SCROLL_MODE_RESERVE keeps the
# bar's gutter whether the bar shows or not, so the label's width — and its
# height — never depend on the bar.
#
# `reserve` writes {"done": true, ...} to <out json> and quits; `auto` hangs
# (the caller's timeout kills it — tests/test_ui6_scroll_gutter.py).

var _out := ""


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	var a := OS.get_cmdline_user_args()
	if a.size() < 3:
		push_error("usage: -- <bbcode file> <out json> <auto|reserve>")
		quit(2)
		return
	var text := FileAccess.get_file_as_string(a[0])
	_out = a[1]
	var mode := str(a[2])
	Utils.apply_text_size(1.15)
	root.content_scale_factor = 2.0
	var panel := PanelContainer.new()
	panel.position = Vector2(12, 48)
	root.add_child(panel)
	var vbox := VBoxContainer.new()
	panel.add_child(vbox)
	var scroll := ScrollContainer.new()
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	if mode == "reserve":
		scroll.vertical_scroll_mode = ScrollContainer.SCROLL_MODE_RESERVE
	vbox.add_child(scroll)
	var rtl := RichTextLabel.new()
	rtl.bbcode_enabled = true
	rtl.fit_content = true
	rtl.scroll_active = false
	rtl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(rtl)
	rtl.text = text
	var width := 360.0
	scroll.custom_minimum_size = Vector2(width - 24.0, 335.0)
	rtl.custom_minimum_size.x = width - 44.0
	panel.size = Vector2.ZERO
	for _i in range(6):
		await process_frame
	var f := FileAccess.open(_out, FileAccess.WRITE)
	f.store_string(JSON.stringify({
		"done": true,
		"mode": mode,
		"label_width": int(rtl.size.x),
		"scroll_height": int(scroll.size.y),
		"bar_shown": scroll.get_v_scroll_bar().visible,
	}))
	f.close()
	quit(0)
