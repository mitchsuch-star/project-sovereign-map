"""DEF-14 "The Names Match the Map" - the province-name audit.

Does each province name sit where the painted map puts it, relative to its
neighbours? The art is a stylised Europe drawn by hand, and Slice 2 authored
historical names onto an auto-generated draft, so in places the name and the
drawn place disagreed ("Oslo" on the Danish peninsula, "Scania" on the German
Baltic coast, an inland "Toledo" on the Mediterranean shore). The registry
the game reads is consistent either way; this is legibility and trust.

Method (deterministic, standard library only - the test suite imports it):

  * GAZETTEER gives each name's real (lon, lat): an approximate centroid of
    the historical place, in degrees.
  * Real coordinates are projected equirectangularly (longitude scaled by
    cos 50 deg). No single transform fits a hand-drawn map, so the audit
    never fits the whole map at once:
  * for every province p, its K nearest provinces IN THE ART (p excluded;
    ties broken by name) fit an affine transform real -> pixels by least
    squares, TRIM times dropping the neighbour the fit misses most, so one
    mislabelled neighbour cannot drag the fit. p's real coordinates are then
    pushed through the transform and the miss is scored in units of p's
    local neighbour spacing (the median of its four nearest distances).
  * A score of THRESHOLD or more is an outlier: the name contradicts its
    neighbours by more than one and a half provinces.

Every outlier is either renamed (world_state.RENAMED_PROVINCES) or recorded
in STYLISED with its reason, and STYLISED also records the art's own
distortions DEF-14 named, where the name is right for its neighbours but the
painted sea or coast is not. `tests/test_def14_the_names_match_the_map.py`
pins both.

Usage:
    .venv\\Scripts\\python.exe -m tools.audit_province_names           # the table
    .venv\\Scripts\\python.exe -m tools.audit_province_names --check   # exit 1 on an unrecorded outlier

Run it after renaming a province, moving an anchor or repainting the map.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

REPO = Path(__file__).resolve().parents[1]
REGISTRY = REPO / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe.json"

K_NEIGHBOURS = 10
TRIM = 3
THRESHOLD = 1.5

# Real (lon, lat) of each province name: approximate centroids, degrees.
GAZETTEER: Dict[str, Tuple[float, float]] = {
    # Britain & Ireland
    "Highlands": (-4.5, 57.3), "Scotland": (-3.5, 55.8), "Northumbria": (-1.8, 54.9),
    "Ulster": (-6.7, 54.6), "Munster": (-8.5, 52.3), "Wales": (-3.8, 52.3),
    "Midlands": (-1.8, 52.7), "Cornwall": (-4.9, 50.4), "Wessex": (-1.9, 51.1),
    "East Anglia": (1.0, 52.4), "London": (-0.1, 51.5),
    # Scandinavia, Denmark and Finland
    "Nordland": (14.5, 67.0), "Trondheim": (10.4, 63.4), "Lapland": (19.0, 67.5),
    "Norrland": (17.5, 63.5), "Stockholm": (18.1, 59.3), "Scania": (13.5, 55.9),
    "Copenhagen": (12.6, 55.7), "Jutland": (9.3, 56.2), "Schleswig": (9.5, 54.6),
    "Holstein": (10.0, 54.1), "Stralsund": (13.1, 54.3),
    "Ostrobothnia": (22.5, 63.0), "Finland": (23.5, 61.0), "Uleaborg": (25.5, 65.0),
    "Karelia": (29.0, 62.0), "Estonia": (25.5, 58.8), "Livonia": (24.8, 57.2),
    # The Baltic, Poland and western Russia
    "East Prussia": (20.8, 54.4), "Samogitia": (22.5, 55.8), "Vilna": (25.3, 54.7),
    "Lithuania": (24.3, 53.7), "White Russia": (28.5, 53.9), "Volhynia": (26.5, 50.8),
    "Podolia": (27.5, 49.0), "Ukraine": (31.5, 50.0), "New Russia": (32.5, 47.0),
    "Posen": (16.9, 52.4), "Silesia": (17.0, 51.0), "Pomerania": (15.0, 53.8),
    "Brandenburg": (13.8, 53.0), "Berlin": (13.4, 52.5), "Dresden": (13.7, 51.05),
    # Germany and the Low Countries
    "Hanover": (9.7, 52.4), "Brunswick": (10.5, 52.3), "Oldenburg": (8.2, 53.1),
    "East Frisia": (7.4, 53.4), "Osnabruck": (8.0, 52.3), "Westphalia": (7.6, 51.9),
    "Friesland": (5.8, 53.2), "Amsterdam": (4.9, 52.4), "Gelderland": (5.9, 52.0),
    "Brabant": (4.5, 51.2), "Flanders": (3.5, 51.0), "Frankfurt": (8.7, 50.1),
    "Nassau": (7.9, 50.4), "Rhineland": (6.9, 50.3), "Franconia": (10.9, 49.8),
    "Swabia": (9.2, 48.5), "Munich": (11.6, 48.1), "Bohemia": (14.4, 50.0),
    "Vienna": (16.4, 48.2), "Moravia": (16.9, 49.4), "Hungary": (19.0, 47.3),
    "Croatia": (16.0, 45.5), "Carniola": (14.5, 46.0), "Tyrol": (11.4, 47.2),
    # France
    "Normandy": (0.0, 49.1), "Artois": (2.6, 50.4), "Picardy": (2.3, 49.9),
    "Champagne": (4.0, 49.0), "Ardennes": (4.7, 49.7), "Ile-de-France": (2.6, 49.0),
    "Paris": (2.35, 48.86), "Orleanais": (1.9, 47.9), "Lorraine": (6.2, 48.7),
    "Burgundy": (4.8, 47.3), "Nivernais": (3.5, 47.1), "Franche-Comte": (6.0, 47.2),
    "Maine": (0.2, 48.0), "Brittany": (-3.0, 48.2), "Anjou": (-0.5, 47.4),
    "Berry": (2.0, 47.0), "Limousin": (1.5, 45.8), "Lyonnais": (4.8, 45.8),
    "Provence": (5.9, 43.6), "Savoy": (6.4, 45.6), "Guyenne": (0.8, 44.6),
    "Gascony": (0.2, 43.7), "Bordelais": (-0.6, 44.8), "Bearn": (-0.5, 43.2),
    "Languedoc": (3.0, 43.6), "Corsica": (9.0, 42.1),
    # Switzerland and Italy
    "Bern": (7.4, 46.9), "Piedmont": (7.7, 45.1), "Milan": (9.2, 45.5),
    "Rome": (12.5, 41.9), "Naples": (14.3, 40.8), "Cagliari": (9.0, 39.8),
    # Iberia and Morocco
    "Galicia": (-8.0, 42.8), "Asturias": (-5.9, 43.3), "Leon": (-5.6, 42.6),
    "Aragon": (-0.9, 41.6), "Madrid": (-3.7, 40.4), "Cartagena": (-0.98, 37.6),
    "Andalusia": (-5.0, 37.4), "Porto": (-8.6, 41.2), "Beira": (-7.5, 40.3),
    "Lisbon": (-9.1, 38.7), "Alentejo": (-7.9, 38.3), "Balearics": (2.9, 39.6),
    "Morocco": (-6.0, 34.0),
    # The Ottoman lands and North Africa
    "Rumelia": (25.5, 42.2), "Constantinople": (29.0, 41.0), "Albania": (20.0, 41.0),
    "Epirus": (20.8, 39.6), "Anatolia": (32.0, 39.5), "Karaman": (33.5, 37.2),
    "Trebizond": (39.7, 41.0), "Syria": (37.0, 34.5), "Cyprus": (33.2, 35.1),
    "Crete": (24.9, 35.2), "Egypt": (31.2, 30.0), "Tripoli": (13.2, 32.9),
    "Algiers": (3.0, 36.7), "Oran": (-0.6, 35.7),
}

# The recorded stylisations. "outlier": the audit scores it at or above
# THRESHOLD and the name is kept on purpose. "art": the name fits its
# neighbours, but the painted sea or coast does not (DEF-14 named these).
STYLISED: Dict[str, Tuple[str, str]] = {
    # The Paris basin: the art rings Paris with generic shapes.
    "Orleanais": ("outlier", "Drawn east of Paris, beside Lorraine; historically "
                  "Orleans lies south-west. The art rings Paris with generic shapes, and "
                  "renaming inside France would only shuffle labels: every French province "
                  "stays in France with the borders the rules use."),
    "Ile-de-France": ("outlier", "Drawn east of Paris rather than around it - the "
                      "same Paris-basin shuffle as Orleanais."),
    "Ardennes": ("outlier", "Drawn just east of Paris, south of Picardy - the same "
                 "Paris-basin shuffle."),
    "Nivernais": ("outlier", "Drawn east of Burgundy rather than west of it - a "
                  "shuffle inside France."),
    # The North Sea and Baltic coasts are compressed.
    "Amsterdam": ("outlier", "Holland's capital is drawn inland; the art gives "
                  "Holland one coastal province (Friesland), where the Dutch fleet "
                  "anchors since NUI-2. Putting Amsterdam on the sea means moving "
                  "Holland's capital - a gameplay change owned by DEF-15."),
    "Westphalia": ("outlier", "The art interleaves Hanover's North Sea lands with "
                   "Holland's: Westphalia and East Frisia are painted WEST of Amsterdam "
                   "and Gelderland, which in fact lie west of them, and Dutch Friesland "
                   "does not touch the rest of Holland. Renaming the cluster means "
                   "re-deriving the Dutch and Hanoverian provinces together with "
                   "Holland's capital - DEF-15. (Surfaced by DEF-14: the misnamed "
                   "Danish neighbours had masked it.)"),
    "East Frisia": ("outlier", "The same interleaved North Sea coast as Westphalia "
                    "(DEF-15)."),
    "Livonia": ("outlier", "The art compresses the eastern Baltic: Livonia is drawn "
                "on the coast beside Pomerania, where West Prussia lies. DEF-7 cut its "
                "painted land borders with Prussia, so the rules keep it the Russian "
                "Baltic province, reached by sea."),
    # The art's own distortions DEF-14 named.
    "Moravia": ("art", "The art paints the Black Sea just east of Vienna, so "
                "Austria's eastern lands meet it. Moravia sits east of Vienna toward "
                "Russia, as Austria's north-eastern lands did; the sea is stylised."),
    "Hungary": ("art", "South-east of Vienna, as it should be; it touches the "
                "stylised Black Sea."),
    "Croatia": ("art", "South of Hungary and beside Ottoman Rumelia, as it should be; "
                "it touches the stylised Black Sea."),
    "Bern": ("art", "The stylised Adriatic reaches this landlocked place; DEF-8 keeps "
             "its coastal flag off."),
    "Franche-Comte": ("art", "The stylised Adriatic reaches it; DEF-8 keeps its "
                      "coastal flag off."),
    "Munich": ("art", "The stylised Adriatic reaches it; DEF-8 keeps its coastal "
               "flag off."),
    "Milan": ("art", "The stylised Adriatic reaches it; DEF-8 keeps its coastal flag "
              "off."),
    "Tyrol": ("art", "The stylised Adriatic reaches it; DEF-8 keeps its coastal flag "
              "off."),
    "Estonia": ("art", "Drawn inland (its only water is a lake pocket); it keeps the "
                "Gulf crossing to Finland as a DEF-7 sea link."),
    "East Prussia": ("art", "Drawn inland behind the compressed Baltic coast; DEF-7 "
                     "kept its border with Estonia as the Courland stand-in."),
    "Samogitia": ("art", "Drawn inland behind the compressed Baltic coast."),
    "Picardy": ("art", "Drawn east of Artois rather than south-west of it - a shuffle "
                "inside France."),
    "Artois": ("art", "The coastal pair of the Picardy shuffle."),
    "Flanders": ("art", "Drawn inland; the art gives the Flemish coast to the Dutch "
                 "province north of Artois (NUI-2 set its coastal flag off)."),
}


def _project(lon: float, lat: float) -> Tuple[float, float]:
    """Equirectangular, km-ish: longitude scaled by cos 50 deg."""
    return (lon * math.cos(math.radians(50.0)) * 111.0, -lat * 111.0)


def _fit_affine(src: List[Tuple[float, float]], dst: List[Tuple[float, float]]):
    """Least-squares affine map src -> dst, as (ax, bx, cx, ay, by, cy) with
    x' = ax*x + bx*y + cx. Centred first, so the 2x2 normal equations stay
    well conditioned."""
    n = float(len(src))
    mx = sum(p[0] for p in src) / n
    my = sum(p[1] for p in src) / n
    ux = sum(q[0] for q in dst) / n
    uy = sum(q[1] for q in dst) / n
    sxx = sxy = syy = 0.0
    tx = [0.0, 0.0]
    ty = [0.0, 0.0]
    for (x, y), (u, v) in zip(src, dst):
        dx, dy, du, dv = x - mx, y - my, u - ux, v - uy
        sxx += dx * dx
        sxy += dx * dy
        syy += dy * dy
        tx[0] += dx * du
        tx[1] += dy * du
        ty[0] += dx * dv
        ty[1] += dy * dv
    det = sxx * syy - sxy * sxy
    if abs(det) < 1e-12:
        raise ValueError("degenerate neighbourhood")

    def _solve(rhs):
        a = (rhs[0] * syy - rhs[1] * sxy) / det
        b = (rhs[1] * sxx - rhs[0] * sxy) / det
        return a, b

    ax, bx = _solve(tx)
    ay, by = _solve(ty)
    return (ax, bx, ux - ax * mx - bx * my, ay, by, uy - ay * mx - by * my)


def _apply(m, p: Tuple[float, float]) -> Tuple[float, float]:
    ax, bx, cx, ay, by, cy = m
    return (ax * p[0] + bx * p[1] + cx, ay * p[0] + by * p[1] + cy)


def _robust_fit(src, dst, trim: int):
    idx = list(range(len(src)))
    for _ in range(trim):
        m = _fit_affine([src[i] for i in idx], [dst[i] for i in idx])
        errs = [math.dist(_apply(m, src[i]), dst[i]) for i in idx]
        worst = max(range(len(idx)), key=lambda j: (errs[j], -j))
        idx.pop(worst)
    return _fit_affine([src[i] for i in idx], [dst[i] for i in idx])


def load_registry(path: Optional[Path] = None) -> dict:
    return json.loads(Path(path or REGISTRY).read_text(encoding="utf-8"))


def audit(registry: Optional[dict] = None) -> List[dict]:
    """One row per province, worst first: name, anchor, predicted pixel,
    miss (px), local spacing (px) and score (miss / spacing)."""
    reg = registry if registry is not None else load_registry()
    provinces = sorted((e["name"], tuple(e["anchor"])) for e in reg["regions"].values())
    missing = [name for name, _ in provinces if name not in GAZETTEER]
    if missing:
        raise KeyError(f"no gazetteer entry for {missing}")
    names = [name for name, _ in provinces]
    pixels = [(float(a[0]), float(a[1])) for _, a in provinces]
    real = [_project(*GAZETTEER[name]) for name in names]
    rows = []
    for i, name in enumerate(names):
        ranked = sorted(
            ((math.dist(pixels[i], pixels[j]), names[j], j)
             for j in range(len(names)) if j != i))
        near = [j for _, _, j in ranked[:K_NEIGHBOURS]]
        four = [d for d, _, _ in ranked[:4]]
        spacing = (four[1] + four[2]) / 2.0
        m = _robust_fit([real[j] for j in near], [pixels[j] for j in near], TRIM)
        predicted = _apply(m, real[i])
        miss = math.dist(predicted, pixels[i])
        rows.append({
            "name": name,
            "anchor": [int(pixels[i][0]), int(pixels[i][1])],
            "predicted": [int(round(predicted[0])), int(round(predicted[1]))],
            "miss": miss,
            "spacing": spacing,
            "score": miss / spacing,
        })
    rows.sort(key=lambda r: (-r["score"], r["name"]))
    return rows


def outliers(rows: Optional[List[dict]] = None, threshold: float = THRESHOLD) -> List[str]:
    rows = rows if rows is not None else audit()
    return [r["name"] for r in rows if r["score"] >= threshold]


def unrecorded_outliers(rows: Optional[List[dict]] = None) -> List[str]:
    return [name for name in outliers(rows) if name not in STYLISED]


def main(argv: List[str]) -> int:
    rows = audit()
    print(f"{'score':>6} {'miss_px':>8}  {'name':<16} {'anchor':<13} predicted     note")
    for r in rows:
        if r["score"] < 1.0 and r["name"] not in STYLISED:
            continue
        note = STYLISED.get(r["name"], ("", ""))[0]
        flag = "  <- UNRECORDED" if r["score"] >= THRESHOLD and not note else ""
        print(f"{r['score']:6.2f} {r['miss']:8.0f}  {r['name']:<16} "
              f"{str(r['anchor']):<13} {str(r['predicted']):<13} {note}{flag}")
    bad = unrecorded_outliers(rows)
    print(f"\n{len(outliers(rows))} outliers at score >= {THRESHOLD}; "
          f"{len(bad)} unrecorded")
    if "--check" in argv and bad:
        print("UNRECORDED:", ", ".join(bad))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
