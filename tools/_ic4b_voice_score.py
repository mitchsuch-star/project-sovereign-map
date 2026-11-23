"""Row IC, Session 4b (IC4-R1) — score the blind readers' answers against the
key written before they read (`tools/_ic4b_voice_key.py`).

    .venv/Scripts/python.exe tools/_ic4b_voice_score.py KEY.json ANSWERS1.txt [ANSWERS2.txt ...]

The bar (written first, the plan): every reader right on every question, none
guessing. Each answer file is a reader's plain-text reply in the sheet's format:
    PAIR <n>: Line 1 = <man>, Line 2 = <man> | SURE or PARTLY GUESSED | <why>
    SET <n>: A=<man>, ... F=<man> | guessed letters: <letters or none>
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
import unicodedata


def _norm(name: str) -> str:
    plain = unicodedata.normalize("NFKD", str(name)).encode("ascii", "ignore").decode()
    return plain.strip().strip("*").strip().lower()


def score(key: dict, text: str) -> dict:
    out = {"pairs_right": 0, "pairs": len(key["pairs"]), "pairs_guessed": [], "pairs_wrong": [],
           "six_right": 0, "six": 6 * len(key["sixway"]), "six_guessed": [], "six_wrong": []}
    pair_re = re.compile(r"PAIR\s*(\d+)\s*:\s*Line\s*1\s*=\s*([^,|]+),\s*Line\s*2\s*=\s*([^|]+)\|\s*([^|]+)",
                         re.IGNORECASE)
    for m in pair_re.finditer(text):
        n = int(m.group(1))
        pair = next((p for p in key["pairs"] if p["n"] == n), None)
        if pair is None:
            continue
        right = (_norm(m.group(2)) == _norm(pair["key"]["line1"])
                 and _norm(m.group(3)) == _norm(pair["key"]["line2"]))
        out["pairs_right"] += 1 if right else 0
        if not right:
            out["pairs_wrong"].append(n)
        if "guess" in m.group(4).lower():
            out["pairs_guessed"].append(n)
    set_re = re.compile(r"SET\s*(\d+)\s*:(.*?)\|\s*guessed letters\s*:\s*([^\n]*)", re.IGNORECASE)
    for m in set_re.finditer(text):
        n = int(m.group(1))
        if not 1 <= n <= len(key["sixway"]):
            continue
        rows = {r["letter"]: r["key"] for r in key["sixway"][n - 1]["rows"]}
        given = dict((a.strip().upper(), b) for a, b in re.findall(r"([A-F])\s*=\s*([^,|]+)", m.group(2)))
        for letter, who in rows.items():
            if _norm(given.get(letter, "")) == _norm(who):
                out["six_right"] += 1
            else:
                out["six_wrong"].append(f"{n}{letter}")
        guessed = m.group(3).strip().lower()
        if guessed and not guessed.startswith("none"):
            out["six_guessed"].extend(f"{n}{x.upper()}" for x in re.findall(r"[a-f]", guessed.split("(")[0]))
    return out


def main(argv=None) -> int:
    argv = list(argv if argv is not None else sys.argv[1:])
    key = json.loads(pathlib.Path(argv[0]).read_text(encoding="utf-8"))
    met = True
    rows = []
    for path in argv[1:]:
        s = score(key, pathlib.Path(path).read_text(encoding="utf-8"))
        rows.append({"reader": pathlib.Path(path).name, **s})
        met = met and not s["pairs_wrong"] and not s["six_wrong"] and not s["pairs_guessed"] \
            and not s["six_guessed"] and s["pairs_right"] == s["pairs"] and s["six_right"] == s["six"]
    print(json.dumps({"readers": rows, "bar_met": met}, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
