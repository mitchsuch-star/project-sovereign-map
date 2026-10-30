"""Bundle the client's shipped fonts, textures, ornaments and heraldry as data
URIs into mock_assets.js (window.ASSETS = {key: dataURI}) for the HTML mocks.
Read-only on the repo; writes only beside itself."""
import base64
import json
import mimetypes
import os
import sys

REPO = r"C:\Users\User\PycharmProjects\project-sovereign-map"
A = os.path.join(REPO, "godot-client", "project-sovereign", "assets")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mock_assets.js")

FILES = {
    # fonts (the theme: Cinzel headings, EB Garamond body; IM Fell for the plate)
    "font_cinzel": "fonts/Cinzel[wght].ttf",
    "font_garamond": "fonts/EBGaramond[wght].ttf",
    "font_garamond_it": "fonts/EBGaramond-Italic[wght].ttf",
    "font_fell": "fonts/IMFeENrm28P.ttf",
    "font_fell_it": "fonts/IMFeENit28P.ttf",
    # textures — the alpha twin is the one the designs found (torn edge transparent)
    "parchment_alpha": "textures/old-parchment_alpha.png",
    # ornaments
    "wax_seal": "ui/ornaments/wax_seal.png",
    "corner_floral_01": "ui/ornaments/corner_floral_01.svg",
    "corner_floral_02": "ui/ornaments/corner_floral_02.svg",
    "laurel_golden": "ui/ornaments/laurel_golden.svg",
    "laurel_wreath": "ui/ornaments/laurel_wreath.svg",
    "flourish_left": "ui/ornaments/flourish_left.svg",
    "flourish_right": "ui/ornaments/flourish_right.svg",
    "flourish_scroll": "ui/ornaments/flourish_scroll.svg",
    "divider_wavy": "ui/ornaments/divider_wavy.svg",
    "fleuron_flowers": "ui/ornaments/fleuron_flowers.svg",
    # heraldry
    "arms_France": "ui/heraldry/France.svg",
    "arms_Britain": "ui/heraldry/Britain.svg",
    "arms_Spain": "ui/heraldry/Spain.svg",
    "arms_Bavaria": "ui/heraldry/Bavaria.svg",
    "arms_Holland": "ui/heraldry/Holland.svg",
    "arms_Austria": "ui/heraldry/Austria.svg",
    # icons
    "icon_folder": "ui/icons/phosphor/folder-open.svg",
    "icon_hourglass": "ui/icons/phosphor/hourglass.svg",
}

out = {}
missing = []
for key, rel in FILES.items():
    path = os.path.join(A, rel)
    if not os.path.exists(path):
        missing.append(rel)
        continue
    mime, _ = mimetypes.guess_type(path)
    if path.endswith(".ttf"):
        mime = "font/ttf"
    elif path.endswith(".svg"):
        mime = "image/svg+xml"
    with open(path, "rb") as fh:
        data = base64.b64encode(fh.read()).decode("ascii")
    out[key] = f"data:{mime};base64,{data}"

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("window.ASSETS = ")
    json.dump(out, fh)
    fh.write(";\n")

print(f"bundled {len(out)} assets -> {OUT} ({os.path.getsize(OUT) // 1024} KB)")
if missing:
    print("missing:", missing)
    sys.exit(1)
