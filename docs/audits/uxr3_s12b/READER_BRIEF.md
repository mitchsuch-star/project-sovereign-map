<!-- The template S12 part 1's three blind readers were given (with {N} and {PACKET} filled), written into the
     packet as READER_BRIEF_{N}.md and handed to each Agent-tool reader with a pointer to it. Reuse it verbatim. -->

# UXR-3 re-read — the blind reader's brief (Pre-Deploy S12 part 1)

You are reader **{N}** of three. You mark three items of a frozen look-and-feel
checklist on the surfaces of a strategy game's client: **R2 Hierarchy, R5
Affordance (the reader half), R8 Discoverability.** Other judges (instruments)
mark the other five items; you never mark those.

## Your evidence, and nothing else

Everything you may read is in the packet directory `{PACKET}`, plus the full-resolution frames its cards name by path:

- `UX_CHECKLIST_V1.json` — the frozen checklist. Its `items` hold the exact pass
  rule of R2, R5 and R8. Read those three rules first and apply them literally.
- `INDEX.md` and ten `group_NN_<key>.md` files — one card per surface: its
  purpose (the `must_show` line), its frames (PNG crops at 1920×1080 and at the
  player's 5120×1440, plus the full frames at the other three resolutions), and
  the action probe's record of every control on it: each control's words, class,
  whether pressing it changed the screen (VISIBLE), only signalled the game
  (HANDOFF), did nothing (SILENT), was not pressed (NOT PRESSED: it would leave
  the screen or quit), or was disabled (DISABLED, with its tooltip and the text
  beside it).
- `records/` — the instruments' records, if you want a number. Optional.

Rules of the reading:
- **Look at the frames.** Open each surface's 1920×1080 crop and its 5120×1440
  crop with your image-reading tool; open another resolution when you need it.
  Every mark cites the frame you judged it on (its path).
- **Blind.** Do not open any other reader's directory, any file outside the
  packet, the game's source, or any earlier review. Do not run programs.
- **No abstaining.** Every surface gets all three marks. If you cannot judge
  from the evidence, mark ✗ and say why.
- **R5 is about what you SEE plus the probe's record:** everything that is a
  control looks like one; nothing that looks clickable is inert (text styled as
  a link, a bordered card, a chevron, with no control in the probe's record);
  every disabled control states why (its tooltip in the record counts). A
  control the probe recorded as SILENT is already failed by the instrument — you
  may note it, it does not change your mark's logic.
- **R2:** the one thing the surface is for (its name and must_show line) is the
  largest or the first element, and the eye lands on it.
- **R8:** read the must_show line as a new player with no manual: is the key
  action reachable from what the frame shows (a visible control, a stated key, a
  named next step)? A surface whose purpose is to inform passes when the way to
  leave it is visible.
- **R4_note (optional, never scored):** one or two sentences on anything that
  looks inconsistent (chrome, chips, close controls, headings, spacing, cut
  lines). Leave it out when there is nothing to say.

## What you write

One JSON file per group, written as soon as you finish that group (so a long
reading never loses a finished group), to
`{PACKET}/panel_raw/reader_{N}/group_NN.json` (NN = the group's order, two
digits):

```json
{"reader": {N}, "group": "<group key>",
 "marks": {
  "<surface id>": {
   "R2": {"pass": true, "cite": "<frame path>", "why": "<one sentence>"},
   "R5": {"pass": false, "cite": "<frame path>", "why": "<one sentence>"},
   "R8": {"pass": true, "cite": "<frame path>", "why": "<one sentence>"},
   "R4_note": "<optional>"
  }
 }}
```

Write nothing else anywhere. When all ten groups are written, reply with one
line per group: its key and your ✓ count per item.
