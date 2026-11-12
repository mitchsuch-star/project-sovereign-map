"""Before / after pairs for docs/audits/ui_gilt2/: each of the 30 rating frames side by side.

usage: python -I make_pairs.py <before_mapping.json> <after_mapping.json> <out_dir> [<prefix>]
(<prefix> names the files, UIGILT2 by default — Session UI-3 passes UIGILT3.)
Each mapping is {Fnn: {stem, src}} (make_rating_set.py writes them). JPEGs, 2412 px wide, captioned.
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

LABELS = {
    "F01": "The war room", "F02": "The war room at 5120x1440", "F03": "The war room at Interface Scale 2.0",
    "F04": "The School of War card", "F05": "Ledger: Forces", "F06": "Ledger: Economy",
    "F07": "Ledger: Territories", "F08": "Ledger: Manpower", "F09": "The Generals: the Emperor",
    "F10": "The Generals: Ney", "F11": "Diplomacy: Nations", "F12": "Diplomacy: Vassals",
    "F13": "Diplomacy: Balance of Europe", "F14": "The Cabinet", "F15": "The Cabinet: Austria",
    "F16": "The settlement table", "F17": "The Morning Dispatch", "F18": "Le Moniteur",
    "F19": "The enemy phase", "F20": "The battle diorama", "F21": "A client's petition",
    "F22": "An affair of state", "F23": "A marshal's objection", "F24": "The region panel: Paris",
    "F25": "The war detail", "F26": "The campaign end", "F27": "The main menu",
    "F28": "The Campaign Menu: Settings", "F29": "The envoys' mailbox", "F30": "The Correspondence",
}


def font(size: int):
    for name in ("C:/Windows/Fonts/georgia.ttf", "C:/Windows/Fonts/times.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def main() -> int:
    before = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    after = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    out = Path(sys.argv[3])
    prefix = sys.argv[4] if len(sys.argv) > 4 else "UIGILT2"
    out.mkdir(parents=True, exist_ok=True)
    f = font(26)
    made = 0
    for fid in sorted(before):
        if fid not in after:
            continue
        a = Image.open(before[fid]["src"]).convert("RGB")
        b = Image.open(after[fid]["src"]).convert("RGB")
        w = 1200
        a = a.resize((w, int(a.height * w / a.width)))
        b = b.resize((w, int(b.height * w / b.width)))
        h = max(a.height, b.height)
        sheet = Image.new("RGB", (w * 2 + 12, h + 44), (8, 10, 18))
        sheet.paste(a, (0, 44))
        sheet.paste(b, (w + 12, 44))
        d = ImageDraw.Draw(sheet)
        name = LABELS.get(fid, fid)
        d.text((10, 8), "BEFORE — " + name, fill=(200, 196, 186), font=f)
        d.text((w + 22, 8), "AFTER — " + name, fill=(225, 200, 140), font=f)
        stem = before[fid]["stem"].replace("IQ10_", "").replace("@", "_")
        sheet.save(out / f"{prefix}_{fid}_{stem}.jpg", quality=86)
        made += 1
    print("pairs", made)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
