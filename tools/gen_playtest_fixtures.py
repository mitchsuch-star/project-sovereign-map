"""Regenerate the committed playtest fixture saves.

The fixtures let a playtest START MID-CAMPAIGN instead of replaying ten
turns to reach the interesting part:

  tests/fixtures/playtest_saves/fixture_t10_ambient.json
      Turn 10, seed `historical`, France issued no orders — the boot
      coalition war has developed on its own (Britain ashore, Austria
      pressing, economy converging).
  tests/fixtures/playtest_saves/fixture_t20_ambient.json
      Turn 20, same run — late-war shape (settlements, exhaustion,
      naval blockade bite).

Deterministic: the driver pins SOVEREIGN_SEED and LLM_MODE=mock, so the
same repo state reproduces the same saves (module RNG varies per-turn
inside advance_turn, but the campaign's SHAPE is seed-stable and the
fixtures are regenerated wholesale, never hand-edited).

WHEN TO RE-RUN: a `FORMAT_VERSION` bump, a serialized-field change that
from_dict cannot default, or intentionally refreshing the fixtures to a
new balance state. Then commit the new JSONs with the change that
motivated them.

  python tools/gen_playtest_fixtures.py
"""

import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "playtest_saves"
RUN_NAME = "fixture-gen"
RUN_DIR = REPO_ROOT / "tools" / "playtest_runs" / RUN_NAME

FIXTURES = {
    f"{RUN_NAME}_t10.json": "fixture_t10_ambient.json",
    f"{RUN_NAME}_t20.json": "fixture_t20_ambient.json",
}


def main() -> int:
    print("[fixtures] driving 20 ambient turns (seed historical, mock)…")
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "tools" / "playtest_driver.py"),
         "--turns", "20", "--name", RUN_NAME, "--seed", "historical",
         "--save-at", "10,20", "--fresh"],
        cwd=REPO_ROOT,
    )
    if result.returncode != 0:
        print(f"[fixtures] driver failed ({result.returncode})", file=sys.stderr)
        return result.returncode

    FIXTURE_DIR.mkdir(parents=True, exist_ok=True)
    for source_name, target_name in FIXTURES.items():
        source = RUN_DIR / "saves" / source_name
        if not source.exists():
            print(f"[fixtures] missing {source}", file=sys.stderr)
            return 2
        shutil.copy2(source, FIXTURE_DIR / target_name)
        size_kb = (FIXTURE_DIR / target_name).stat().st_size // 1024
        print(f"[fixtures] wrote {target_name} ({size_kb} KB)")

    print("[fixtures] done — commit the JSONs under tests/fixtures/playtest_saves/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
