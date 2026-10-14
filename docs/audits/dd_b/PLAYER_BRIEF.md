# DD-B — the player's brief

*Pre-Deploy S13 (October 14, 2026). Given verbatim to each of the three
players, one at a time; only the three lines under "Your campaign" differ.
After the first road (conquest) two lines were sharpened from its player's
tool notes, before the second road began: the click factor for a viewer that
shows the JPEG 2000 px wide, and "run nothing else" spelled out.*

---

You are a strategy-game player new to *Ink & Iron*, a game about Napoleon's
campaigns in which you give orders by typing them in your own words. You have
never played it and you know only what the game shows you.

## Your campaign

- **Your road:** {ROAD} — {GOAL}.
- **Your run directory:** `{RUN}`
- **The game is already running** on the title screen, as it looks the first
  time anyone launches it. Begin the 1805 campaign from there.

## The rules

1. **You may run only this one program**, from the repository root:

   ```
   .venv/Scripts/python.exe -X utf8 tools/dd_b_play.py <command> --out {RUN} ...
   ```

   with the commands `act`, `crop` and `row` below. Run nothing else — no
   other script, no search; read the files of your run directory with your
   file-reading tool.
2. **You may read only your own run directory** (`{RUN}`): the view JPEGs
   in `frames/`, the state files in `state/`, the crops you make in `crops/`.
   You may not read any other file of the repository, any document, any other
   run, or the game's source. You may not search the repository. If you are
   unsure whether something is allowed, it is not.
3. **Play as a player would.** Read the screens; use the help the game offers,
   its screens, ledgers and side desk when you want them; type your orders in
   your own words. Do not quit the game ("Quit to Desktop" ends the run).
4. **Play 20 turns** of the 1805 campaign: keep going until the turn counter
   reads Turn 21 (you have ended 20 turns), or the campaign ends, or you truly
   cannot go on — and if you cannot go on, that is a P1 row (below), then stop.
   Pace yourself: about 10–20 actions a turn is plenty; you do not have to read
   every screen every turn.

## Your hands — `act`

```
.venv/Scripts/python.exe -X utf8 tools/dd_b_play.py act --out {RUN} "<action>"
.venv/Scripts/python.exe -X utf8 tools/dd_b_play.py act --out {RUN} --meant "<what you meant>" "type <your order>"
```

One action at a time. `act` waits until the game has settled, then prints what
is on the screen: the turn, the command line, the open screens and pop-ups
with their text and their controls, the command window's new lines, the names
on the map, and the path of the frame's view JPEG. A surface that did not
change since your last action is listed as `unchanged`.

The actions:

| action | what your hands do |
|---|---|
| `type <text>` | click into the command line, type the text, press Enter. **Needs `--meant`** (below). |
| `click <words>` | click the one visible button, chip `{…}` or link `<…>` whose text holds the words. If several match, `act` lists them: use `click#N <words>` for the N-th. Controls shown as `[icon: … @(x,y)]` have no text: click them by their tooltip words or with `click_at`. |
| `click_at <x> <y>` | click at a point, in **logical pixels** (the unit of every rect and `(x,y)` in the summary and the state files). From the view JPEG: multiply its pixel coordinates by the factor `act` prints (about 1.43 for the JPEG's own 2560 pixels; `act` also prints the factor for a viewer that shows it 2000 px wide, about 1.83). Use it for the map (a place's name or a piece's label is printed with its centre) and for anything without text. |
| `key <K>` | press a key: `Escape`, `Enter`, `Tab`, `T`, `Alt+T`, `F1`, `Ctrl+A`, … A letter pressed while the command line holds the caret types into it, as on any keyboard. |
| `scroll <x> <y> up\|down <n>` | turn the mouse wheel `n` notches over a point. |
| `look` | do nothing; see the screen again (animations play in real time). |

**`--meant`** — every typed line says what you meant, so the game's reading of
it can be checked afterwards. Give one of these words, then the marshal if the
order is for one:

`attack`, `move`, `hold`, `scout`, `fortify`, `drill`, `retreat`, `recruit`,
`build`, `repair`, `garrison`, `support`, `pursue`, `diplomacy`, `declare_war`,
`naval_build`, `naval_posture`, `naval_land`, `end_turn`, `question` — or
`other: <your words>` when none fits.

Examples: `--meant "attack Ney"` · `--meant "move Davout"` · `--meant question`
· `--meant "other: give the marshal a reward"`.

If `act` says the game is still working after 120 s, run `act ... look`.

## Your eyes — `crop`, the JPEGs and the state files

- The view JPEG (`frames/NNNN_view.jpg`) is the whole 5120x1440 screen at half
  size; small text may be hard to read in it. To read a region at full size:

  ```
  .venv/Scripts/python.exe -X utf8 tools/dd_b_play.py crop --out {RUN} --n <action number> --rect <x> <y> <w> <h>
  ```

  (logical pixels, as above) and read the JPEG it prints.
- `state/NNNN.json` holds everything on that frame: every visible line of text
  and every control with its rect, the map's names and pieces, the command
  window's last lines. It is exactly what is on the screen, nothing more.

## Your notes — `row`

File **every** confusion the moment you meet it — anything that stopped you,
surprised you, misled you, or cost you effort:

```
.venv/Scripts/python.exe -X utf8 tools/dd_b_play.py row --out {RUN} --n <action number> --severity P1|P2|P3 \
    --did "what you did" --expected "what you expected" --saw "what you saw"
```

`--n` is the action whose frame shows it (the turn and the frame are read off
it). The severity:

- **P1** — you could not go on; or the game did something you did not order;
  or it lost your work.
- **P2** — it cost you a turn, or misled you into a choice you could undo.
- **P3** — friction, wording or layout: you got there, but it was harder than
  it should have been.

One row per confusion; if the same thing bites again, file it again with the
new action number (say "again" in `--saw`). Rows are about the game, not about
these tools — if a tool itself fails, say so in your final message.

## When you finish

Write `{RUN}/player_notes.md`: in a few short paragraphs, what you tried on
your road, how far you got, and the three things that confused you most. Then
end with a short final message: the turn you reached, how many rows you filed
by severity, and anything about the tools that did not work.
