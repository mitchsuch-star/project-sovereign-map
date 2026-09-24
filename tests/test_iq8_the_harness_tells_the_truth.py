"""IQ-8 "The Harness Tells the Truth" — the row's own test file.

Build contract: the IQ-8 recon §5 as amended by the lead's rulings (the
addendum wins where they differ). The row exists because a published table
(PR-D4: 20 / 24 / 22 provinces, "160 of 160 action points") could not be
reproduced and could not be root-caused either — `meta.json` recorded what a
run ASKED for as though it were what the run PLAYED, carried no platform and
no engine revision, hashed the driver's raw bytes (so one commit hashed two
ways across a CRLF and an LF checkout), counted no action points at all, and
let a repo `.env` put back the board variables the driver had popped.

The seven pins, written BEFORE the fix (the pin writer's slice):

1. `TestMetaCarriesProvenance` — `meta.json` gains `requested` + `resolved` +
   `platform` + `engine_revision`, and `resolved` names what the world IS
   (campaign seed, scenario name, map, region count, player nation, boot
   turn, the dice label, the post-import game-shaping env).
2. `TestTheFromSaveSeedRule` — a `--from-save` run plays the SAVE's campaign
   seed; an explicit `--seed` is honoured for the module dice only, recorded
   as `resolved.dice_label` beside `resolved.campaign_seed`, and the digest
   header prints a WARNING naming both. No silent hybrid.
3. `TestTheDotenvHole` — a `.env` read through dotenv's own loader cannot
   reshape the board, and `resolved.env` is the environment AFTER the import.
4. `TestDriverRevisionIgnoresLineEndings` — one driver, CRLF or LF, one hash.
5. `TestActionPointCounters` — `ap_available` / `ap_spent` / `cmd_refused`
   exist and reconcile with the backend's own end-turn warnings.
6. `TestCrossHashSeedSentinel` (slow) — two driver subprocesses at
   PYTHONHASHSEED 0 and 1 write byte-identical `digest.jsonl`.
7. `TestTheNavalWalkIsOrdered` — `_tracked_links_for` / `link_verdicts_for` /
   `_emit_verdict_flips` / the serialized `meta["verdicts"]` walk the sea
   links in `_link_key` order whatever order the frozenset iterates in.

Every run is Mode A (in-process driver, mock parser) in a subprocess, with
saves and output sandboxed under pytest's tmp dir, so nothing here touches
the developer's `saves/`, `tools/playtest_runs/` or the repo `.env`.
"""

import hashlib
import importlib.util
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DRIVER = ROOT / "tools" / "playtest_driver.py"
COMMANDED = ROOT / "tools" / "playtest_scripts" / "commanded_full40.json"
FIXTURE_T10 = ROOT / "tests" / "fixtures" / "playtest_saves" / "fixture_t10_ambient.json"
SCENARIO_1805 = (ROOT / "godot-client" / "project-sovereign" / "assets" / "maps"
                 / "europe_1805.json")

BOARD_1805 = "The Third Coalition, 1805"
# The game-shaping variables the driver must control (recon §5.1).
ENV_KEYS = ("SOVEREIGN_SCENARIO", "SOVEREIGN_SMOKE_START", "SOVEREIGN_MAP",
            "LLM_MODE", "DEBUG_MODE")
_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_HEX40 = re.compile(r"^[0-9a-f]{40}$")


# ═══════════════════════════════════════════════════════════════════════
# Harness
# ═══════════════════════════════════════════════════════════════════════

def _env(save_dir, hashseed="0", **extra):
    """A clean child environment. PYTHONHASHSEED is always SET, so the
    driver's re-exec never fires (a re-exec would also lose a wrapper's
    patch). The three board variables are removed so the only source of one
    is whatever the test stages on purpose; conftest pins
    SOVEREIGN_SCENARIO=none in this process and the child must not inherit
    it by accident."""
    env = dict(os.environ)
    env.pop("PYTHONIOENCODING", None)          # standing rule: never set it
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_SMOKE_START", "SOVEREIGN_MAP"):
        env.pop(key, None)
    env["PYTHONHASHSEED"] = str(hashseed)
    env["INK_IRON_SAVE_DIR"] = str(save_dir)
    env.update(extra)
    return env


def _drive(out_root, name, *argv, hashseed="0", env=None, prefix=None,
           timeout=900):
    """Run the driver (or `prefix` + the driver's argv) and return
    (CompletedProcess, run_dir). Output lands at `out_root/name`."""
    out_root = Path(out_root)
    out_root.mkdir(parents=True, exist_ok=True)
    child_env = env if env is not None else _env(out_root / "_saves", hashseed)
    cmd = list(prefix) if prefix else [sys.executable, str(DRIVER)]
    cmd += ["--name", name, "--fresh", "--out", str(out_root), *argv]
    proc = subprocess.run(cmd, cwd=str(ROOT), env=child_env,
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace", timeout=timeout)
    return proc, out_root / name


def _ok(proc):
    assert proc.returncode == 0, (
        f"driver exit {proc.returncode}\n--- stdout ---\n{proc.stdout[-2500:]}"
        f"\n--- stderr ---\n{proc.stderr[-2500:]}")


def _meta(run_dir):
    return json.loads((run_dir / "meta.json").read_text(encoding="utf-8"))


def _header(run_dir):
    """The digest header — everything before the first turn block."""
    text = (run_dir / "digest.md").read_text(encoding="utf-8")
    return text.split("\n## Turn", 1)[0]


def _world_of_autosave(run_dir):
    save = json.loads((run_dir / "saves" / "autosave.json").read_text(
        encoding="utf-8"))
    return save["world_state"]


def _jsonl(run_dir):
    return [json.loads(line) for line in
            (run_dir / "digest.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()]


def _block(meta, key):
    assert key in meta, (
        f"meta.json has no `{key}` block — keys present: {sorted(meta)}")
    assert isinstance(meta[key], dict), f"`{key}` is not an object: {meta[key]!r}"
    return meta[key]


def _stage_save(tmp_dir, campaign_seed, filename):
    """A copy of the t10 fixture whose campaign seed is `campaign_seed` — the
    sensitivity arm that defeats a reader hard-coding "historical" (the
    committed fixture's own seed, which is also the driver's default)."""
    data = json.loads(FIXTURE_T10.read_text(encoding="utf-8"))
    data["world_state"]["campaign_seed"] = campaign_seed
    if isinstance(data.get("metadata"), dict):
        data["metadata"]["campaign_seed"] = campaign_seed
    path = Path(tmp_dir) / filename
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


# ═══════════════════════════════════════════════════════════════════════
# 1. meta.json carries requested / resolved / platform / engine_revision
# ═══════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="module")
def default_run(tmp_path_factory):
    """One ambient turn of the default 1805 boot."""
    out = tmp_path_factory.mktemp("iq8_default")
    proc, run_dir = _drive(out, "iq8-default", "--turns", "1")
    _ok(proc)
    return run_dir


class TestMetaCarriesProvenance:

    def test_the_four_blocks_exist(self, default_run):
        meta = _meta(default_run)
        for key in ("requested", "resolved", "platform", "engine_revision"):
            _block(meta, key)

    def test_requested_records_what_was_asked(self, default_run):
        requested = _block(_meta(default_run), "requested")
        assert requested.get("seed") == "historical"
        assert requested.get("scenario") == ""
        assert requested.get("from_save") == ""
        assert requested.get("llm") == "mock"

    def test_resolved_names_the_board_the_world_booted(self, default_run):
        """The discriminating case: the default run REQUESTS scenario `""`
        and the world it plays is the 1805 campaign. The expectations are read
        off the run's own autosave, not restated."""
        resolved = _block(_meta(default_run), "resolved")
        world = _world_of_autosave(default_run)
        assert world["scenario_name"] == BOARD_1805          # the control
        assert resolved.get("scenario_name") == world["scenario_name"]
        assert resolved.get("campaign_seed") == world["campaign_seed"] == "historical"
        assert resolved.get("sovereign_map") == world["sovereign_map"] == "europe"
        assert resolved.get("regions") == len(world["regions"]) == 126
        assert resolved.get("player_nation") == world["player_nation"] == "France"
        assert resolved.get("boot_turn") == 1
        assert resolved.get("dice_label") == "historical"

    def test_resolved_env_names_the_game_shaping_variables(self, default_run):
        env = _block(_block(_meta(default_run), "resolved"), "env")
        missing = [k for k in ENV_KEYS if k not in env]
        assert not missing, f"resolved.env lacks {missing}: {env}"
        assert env["LLM_MODE"] == "mock"
        assert env["DEBUG_MODE"] == "false"
        assert env["SOVEREIGN_MAP"] == "europe"
        assert env["SOVEREIGN_SCENARIO"] in ("", None)
        assert env["SOVEREIGN_SMOKE_START"] in ("", None)

    def test_platform_names_the_interpreter(self, default_run):
        """The child is this interpreter (`sys.executable`), so its platform
        facts are this process's."""
        plat = _block(_meta(default_run), "platform")
        assert plat.get("python") == platform.python_version()
        assert plat.get("implementation") == platform.python_implementation()
        assert plat.get("machine") == platform.machine()
        assert isinstance(plat.get("os"), str) and plat["os"].strip()
        assert plat.get("pythonhashseed") == "0"

    def test_engine_revision_names_the_commit_and_the_content(self, default_run):
        rev = _block(_meta(default_run), "engine_revision")
        assert isinstance(rev.get("content_hash"), str) and _HEX64.match(
            rev["content_hash"]), rev
        # Format alone is satisfied by a hash of nothing (a throwaway
        # prototype of this slice did exactly that and stayed green): the hash
        # must at least have been fed some bytes.
        assert rev["content_hash"] != hashlib.sha256(b"").hexdigest(), (
            "engine_revision.content_hash is the hash of zero bytes")
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(ROOT),
                              capture_output=True, text=True)
        if head.returncode != 0:
            pytest.skip("no git in this checkout — the no-git arm covers it")
        assert rev.get("git_commit") == head.stdout.strip()
        assert _HEX40.match(rev["git_commit"])
        assert rev.get("dirty") in (True, False)

    def test_the_content_hash_covers_the_engine_sources(self, default_run):
        """The hash is fed the engine's SOURCES, not only their names (the
        format pin above is satisfied by a hash over paths alone). Recomputed
        here over the driver's own declared scope — every `backend/**/*.py`
        plus the files it names, each framed `<repo-relative posix path>\\0
        <LF-normalised bytes>\\0` in sorted path order — it must reproduce the
        stamp and must have counted the tree. A drift pin by construction:
        the scope constants are read off the driver, so widening the scope
        moves both sides. Builder's addition (IQ-8), so the mutation "feed
        the hash nothing but the names" is killable rather than INERT."""
        drv = _load_driver_copy(DRIVER, "iq8_driver_content")
        files = []
        for rel_dir in drv.ENGINE_CONTENT_DIRS:
            files.extend(p for p in (ROOT / rel_dir).rglob("*.py")
                         if "__pycache__" not in p.parts)
        files.extend(ROOT / rel for rel in drv.ENGINE_CONTENT_FILES
                     if (ROOT / rel).is_file())
        digest = hashlib.sha256()
        for path in sorted(files, key=lambda p: p.relative_to(ROOT).as_posix()):
            digest.update(path.relative_to(ROOT).as_posix().encode("utf-8") + b"\0")
            digest.update(path.read_bytes().replace(b"\r\n", b"\n") + b"\0")
        rev = _block(_meta(default_run), "engine_revision")
        assert rev.get("content_files") == len(files) >= 100, rev
        assert rev["content_hash"] == digest.hexdigest(), (
            "the content hash does not reproduce over the driver's own scope")

    def test_the_header_prints_resolved_and_platform(self, default_run):
        """Ruling 2: the digest header prints `resolved` and `platform`, so a
        reader of the markdown alone can tell which board and which
        interpreter produced it."""
        header = _header(default_run)
        assert BOARD_1805 in header, header
        assert platform.python_version() in header, header

    def test_a_scenario_request_resolves_through_the_world(self, tmp_path):
        """Coverage arm. `tutorial` names its own world `tutorial`, so this
        arm cannot tell a reader from a restater — the default run above is
        the discriminating case. The tutorial never autosaves (TUT-F2), so
        nothing is read back from a save here."""
        proc, run_dir = _drive(tmp_path, "iq8-tutorial", "--turns", "0",
                               "--scenario", "tutorial")
        _ok(proc)
        meta = _meta(run_dir)
        assert _block(meta, "requested").get("scenario") == "tutorial"
        resolved = _block(meta, "resolved")
        assert resolved.get("scenario_name") == "tutorial"
        assert resolved.get("sovereign_map") == "europe"
        assert resolved.get("regions") == 126

    def test_a_checkout_without_git_records_unknown(self, tmp_path):
        """The engine revision is guarded: with no `git` on PATH the run still
        completes and says so, rather than crashing or inventing a commit."""
        dirs = [d for d in os.environ.get("PATH", "").split(os.pathsep) if d]
        no_git = os.pathsep.join(d for d in dirs if not shutil.which("git", path=d))
        if shutil.which("git", path=no_git):
            pytest.skip("could not stage a PATH without git")
        env = _env(tmp_path / "_saves", PATH=no_git)
        proc, run_dir = _drive(tmp_path, "iq8-nogit", "--turns", "0", env=env)
        _ok(proc)
        rev = _block(_meta(run_dir), "engine_revision")
        assert rev.get("git_commit") == "unknown", rev
        assert rev.get("dirty") not in (True, False), rev
        assert isinstance(rev.get("content_hash"), str) and _HEX64.match(
            rev["content_hash"]), rev


# ═══════════════════════════════════════════════════════════════════════
# 2. The from-save seed rule
# ═══════════════════════════════════════════════════════════════════════

def _seed_warning_lines(header):
    return [line for line in header.splitlines()
            if "warning" in line.lower() and "seed" in line.lower()]


class TestTheFromSaveSeedRule:

    def test_the_lead_case_plays_the_saves_seed_and_warns(self, tmp_path):
        """`--from-save fixture_t10 --seed austerlitz`: the world plays the
        save's `historical`; the dice follow the explicit `austerlitz`; both
        are recorded and the header names both. Today meta says `austerlitz`
        and nothing warns."""
        proc, run_dir = _drive(tmp_path, "iq8-fromsave", "--from-save",
                               str(FIXTURE_T10), "--seed", "austerlitz",
                               "--turns", "1")
        _ok(proc)
        assert _world_of_autosave(run_dir)["campaign_seed"] == "historical"  # control
        # The header first: it is the half a reader of the markdown alone sees,
        # and it fails today for the defect itself rather than for a missing key.
        warnings = [line for line in _seed_warning_lines(_header(run_dir))
                    if "historical" in line and "austerlitz" in line]
        assert warnings, ("the digest header carries no WARNING naming both "
                          "seeds:\n" + _header(run_dir))
        meta = _meta(run_dir)
        assert _block(meta, "requested").get("seed") == "austerlitz"
        resolved = _block(meta, "resolved")
        assert resolved.get("campaign_seed") == "historical"
        assert resolved.get("dice_label") == "austerlitz"
        assert resolved.get("scenario_name") == BOARD_1805
        assert resolved.get("boot_turn") == 10

    def test_a_staged_seed_is_read_off_the_save(self, tmp_path):
        """Sensitivity arm: a save whose campaign seed is NOT the driver's
        default. A reader hard-coding `historical` goes red here."""
        save = _stage_save(tmp_path, "marengo", "fixture_t10_marengo.json")
        proc, run_dir = _drive(tmp_path / "out", "iq8-marengo", "--from-save",
                               str(save), "--seed", "austerlitz", "--turns", "1")
        _ok(proc)
        assert _world_of_autosave(run_dir)["campaign_seed"] == "marengo"  # control
        assert any("marengo" in line and "austerlitz" in line
                   for line in _seed_warning_lines(_header(run_dir))), (
            "no WARNING naming the save's seed and the dice seed:\n"
            + _header(run_dir))
        resolved = _block(_meta(run_dir), "resolved")
        assert resolved.get("campaign_seed") == "marengo"
        assert resolved.get("dice_label") == "austerlitz"

    def test_without_a_seed_flag_the_dice_follow_the_save(self, tmp_path):
        """No `--seed` on a `--from-save` run: one seed, no hybrid, no
        warning — AND the dice really are the save's. Behavioural: the run is
        byte-identical to the same load with `--seed <the save's seed>`.
        Measured before the fix: the flagless run rolled `historical` dice,
        byte-identical to `--seed historical` and different from
        `--seed marengo` within one turn."""
        save = _stage_save(tmp_path, "marengo", "fixture_t10_marengo.json")
        proc, bare = _drive(tmp_path / "bare", "iq8-bare", "--from-save",
                            str(save), "--turns", "1")
        _ok(proc)
        proc, named = _drive(tmp_path / "named", "iq8-named", "--from-save",
                             str(save), "--seed", "marengo", "--turns", "1")
        _ok(proc)
        # Behaviour first, so today's failure is the silent hybrid itself.
        assert (bare / "digest.jsonl").read_bytes() == \
            (named / "digest.jsonl").read_bytes(), (
            "the flagless from-save run did not roll the save's dice")
        assert not _seed_warning_lines(_header(bare)), _header(bare)
        assert not _seed_warning_lines(_header(named)), (
            "an explicit --seed equal to the save's seed is not a hybrid:\n"
            + _header(named))
        meta = _meta(bare)
        # Ruling 3 as built: a flagless load records the REQUEST as `""` —
        # "the save decides" — never the save's own seed restated as though
        # it had been asked for (sweep row IQ8-S7).
        assert _block(meta, "requested").get("seed") == "", meta["requested"]
        resolved = _block(meta, "resolved")
        assert resolved.get("campaign_seed") == "marengo"
        assert resolved.get("dice_label") == "marengo"


# ═══════════════════════════════════════════════════════════════════════
# 3. The .env hole
# ═══════════════════════════════════════════════════════════════════════

# The wrapper routes BOTH of the backend's `load_dotenv()` calls through
# python-dotenv's own loader at a FAKE file (the repo `.env` is never read):
#   * FAKE (override=False, the backend's real call): the three board
#     variables plus a sentinel that proves the file was loaded at all;
#   * HOSTILE (override=True): DEBUG_MODE only — a value that exists ONLY
#     after the backend import, so `resolved.env` can be shown to be the
#     post-import read rather than the driver's own intention.
_WRAPPER = r'''
import json, os, runpy, sys
fake, hostile, driver, probe = sys.argv[1:5]
import dotenv
import dotenv.main
_real = dotenv.main.load_dotenv
def _load(*args, **kwargs):
    _real(dotenv_path=fake)
    _real(dotenv_path=hostile, override=True)
    return True
dotenv.load_dotenv = _load
dotenv.main.load_dotenv = _load
sys.argv = [driver] + sys.argv[5:]
code = 0
try:
    runpy.run_path(driver, run_name="__main__")
except SystemExit as exc:
    code = exc.code if isinstance(exc.code, int) else (0 if exc.code is None else 1)
with open(probe, "w", encoding="utf-8") as fh:
    json.dump({"sentinel": os.environ.get("IQ8_FAKE_DOTENV_SENTINEL"),
               "debug_mode": os.environ.get("DEBUG_MODE"), "exit": code}, fh)
sys.exit(code)
'''

_HOSTILE_DEBUG = "iq8-after-import"


@pytest.fixture(scope="module")
def dotenv_run(tmp_path_factory):
    base = tmp_path_factory.mktemp("iq8_dotenv")
    fake = base / "fake.env"
    fake.write_text("SOVEREIGN_SCENARIO=none\n"
                    "SOVEREIGN_SMOKE_START=settlement_losing\n"
                    "SOVEREIGN_MAP=legacy\n"
                    "IQ8_FAKE_DOTENV_SENTINEL=loaded\n", encoding="utf-8")
    hostile = base / "hostile.env"
    hostile.write_text(f"DEBUG_MODE={_HOSTILE_DEBUG}\n", encoding="utf-8")
    wrapper = base / "wrap_driver.py"
    wrapper.write_text(_WRAPPER, encoding="utf-8")
    probe = base / "probe.json"
    proc, run_dir = _drive(
        base / "out", "iq8-dotenv", "--turns", "1",
        prefix=[sys.executable, str(wrapper), str(fake), str(hostile),
                str(DRIVER), str(probe)])
    return proc, run_dir, probe


class TestTheDotenvHole:

    def test_the_fake_dotenv_was_actually_loaded(self, dotenv_run):
        """Non-vacuity: without this the board assertions below could pass
        because the patch never took."""
        proc, _run_dir, probe = dotenv_run
        _ok(proc)
        seen = json.loads(probe.read_text(encoding="utf-8"))
        assert seen["sentinel"] == "loaded", seen
        assert seen["debug_mode"] == _HOSTILE_DEBUG, seen

    def test_the_driver_still_boots_the_1805_board(self, dotenv_run):
        """The hole itself. Read off the world's own save, not the meta."""
        proc, run_dir, _probe = dotenv_run
        _ok(proc)
        world = _world_of_autosave(run_dir)
        assert (world.get("scenario_name"), world.get("sovereign_map"),
                len(world.get("regions") or {})) == (BOARD_1805, "europe", 126), (
            "a .env reshaped the board: scenario "
            f"{world.get('scenario_name')!r}, map {world.get('sovereign_map')!r}, "
            f"{len(world.get('regions') or {})} regions")

    def test_resolved_records_the_board_and_the_neutralised_env(self, dotenv_run):
        proc, run_dir, _probe = dotenv_run
        _ok(proc)
        resolved = _block(_meta(run_dir), "resolved")
        assert resolved.get("scenario_name") == BOARD_1805
        assert resolved.get("sovereign_map") == "europe"
        env = _block(resolved, "env")
        assert env.get("SOVEREIGN_MAP") == "europe", env
        assert env.get("SOVEREIGN_SCENARIO") in ("", None), env
        assert env.get("SOVEREIGN_SMOKE_START") in ("", None), env
        assert env.get("LLM_MODE") == "mock", env

    def test_resolved_env_is_read_after_the_backend_import(self, dotenv_run):
        """DEBUG_MODE=iq8-after-import exists only after `import backend.main`
        ran its `load_dotenv()`; a snapshot taken before the import records
        the driver's own `false`."""
        proc, run_dir, _probe = dotenv_run
        _ok(proc)
        env = _block(_block(_meta(run_dir), "resolved"), "env")
        assert env.get("DEBUG_MODE") == _HOSTILE_DEBUG, env


# ═══════════════════════════════════════════════════════════════════════
# 4. driver_revision is line-ending-normalised
# ═══════════════════════════════════════════════════════════════════════

def _load_driver_copy(path, name):
    saved_path = list(sys.path)
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path[:] = saved_path


class TestDriverRevisionIgnoresLineEndings:

    def _copies(self, tmp_path):
        raw = DRIVER.read_bytes()
        lf = raw.replace(b"\r\n", b"\n")
        crlf = lf.replace(b"\n", b"\r\n")
        (tmp_path / "lf").mkdir()
        (tmp_path / "crlf").mkdir()
        lf_path = tmp_path / "lf" / "playtest_driver.py"
        crlf_path = tmp_path / "crlf" / "playtest_driver.py"
        lf_path.write_bytes(lf)
        crlf_path.write_bytes(crlf)
        return lf, crlf, lf_path, crlf_path

    def test_one_file_two_line_endings_one_revision(self, tmp_path):
        lf, crlf, lf_path, crlf_path = self._copies(tmp_path)
        assert lf != crlf                           # the copies really differ
        rev_lf = _load_driver_copy(lf_path, "iq8_driver_lf").driver_revision()
        rev_crlf = _load_driver_copy(crlf_path, "iq8_driver_crlf").driver_revision()
        assert rev_lf == rev_crlf, (
            f"the same driver hashes {rev_lf} with LF and {rev_crlf} with CRLF")

    def test_the_revision_is_the_lf_normalised_hash(self, tmp_path):
        lf, _crlf, _lf_path, crlf_path = self._copies(tmp_path)
        expected = hashlib.sha256(lf).hexdigest()[:12]
        assert _load_driver_copy(crlf_path, "iq8_driver_crlf2").driver_revision() == expected

    def test_the_repo_driver_stamps_its_normalised_hash(self):
        module = _load_driver_copy(DRIVER, "iq8_driver_repo")
        expected = hashlib.sha256(
            DRIVER.read_bytes().replace(b"\r\n", b"\n")).hexdigest()[:12]
        assert module.driver_revision() == expected


# ═══════════════════════════════════════════════════════════════════════
# 5. Action-point counters
# ═══════════════════════════════════════════════════════════════════════

_COMMANDED_TURNS = 3
# F2 (row EP, LV-9): "(Warning: 2 actions unused)" / "(Warning: 1 action unused)";
# the old hedge form is still accepted so a committed pre-F2 digest reads.
_UNUSED = re.compile(r"\(Warning: (\d+) action(?:s|\(s\))? unused\)")


@pytest.fixture(scope="module")
def commanded_run(tmp_path_factory):
    out = tmp_path_factory.mktemp("iq8_commanded")
    proc, run_dir = _drive(out, "iq8-commanded", "--script", str(COMMANDED),
                           "--diplomacy", "accept",
                           "--turns", str(_COMMANDED_TURNS))
    _ok(proc)
    return run_dir


def _france_turn_allotment():
    """France's per-turn action points on the 1805 boot, read off a booted
    world rather than restated."""
    import contextlib
    import io
    from backend.models.world_state import WorldState
    with contextlib.redirect_stdout(io.StringIO()):
        world = WorldState.from_scenario(str(SCENARIO_1805))
    return int(world.actions_remaining)


class TestActionPointCounters:

    def test_the_counters_exist(self, commanded_run):
        counters = _meta(commanded_run)["counters"]
        for key in ("ap_available", "ap_spent", "cmd_refused"):
            assert isinstance(counters.get(key), int), (
                f"counters.{key} missing or not an int: {counters}")

    def test_available_is_the_turn_start_allotment(self, commanded_run):
        counters = _meta(commanded_run)["counters"]
        assert counters.get("ap_available") == \
            _france_turn_allotment() * _COMMANDED_TURNS, counters

    def test_spent_reconciles_with_the_end_turn_warnings(self, commanded_run):
        """The recon reproduced PR-D4's 81 / 77 / 75 by hand from these very
        warnings (spent = available − Σ unused). The counter must agree with
        that arithmetic on a run where every loop's explicit `end turn` is the
        one that ended the turn."""
        text = (commanded_run / "digest.md").read_text(encoding="utf-8")
        end_turns = [line for line in text.splitlines()
                     if line.startswith("- CMD `end turn`")]
        assert len(end_turns) == _COMMANDED_TURNS, end_turns
        assert all(" ended." in line for line in end_turns), end_turns
        unused = sum(int(m) for line in end_turns for m in _UNUSED.findall(line))
        counters = _meta(commanded_run)["counters"]
        assert counters.get("ap_spent") == counters.get("ap_available", 0) - unused, (
            f"counters {counters}, Σ unused {unused}")
        # A commanded arm spends, and is not the old "160 of 160" line count.
        assert 0 < counters["ap_spent"] < counters["ap_available"]
        assert counters["ap_spent"] != counters["commands"]

    def test_refused_counts_the_refused_commands(self, commanded_run):
        refused = sum(1 for rec in _jsonl(commanded_run)
                      if rec.get("kind") == "command" and rec.get("success") is False)
        counters = _meta(commanded_run)["counters"]
        assert refused > 0                          # the commanded arm is refused
        assert counters.get("cmd_refused") == refused, counters


def _summary(turn, ap, advanced=None):
    """A POST response as the meter sees it: `action_summary` rides every one
    (`build_base_response`); `action_info.turn_advanced` only an order the
    engine auto-ended the turn on."""
    body = {"action_summary": {"turn": turn, "actions_remaining": ap}}
    if advanced is not None:
        body["action_info"] = {"turn_advanced": advanced}
    return body


class TestTheActionPointMeterArithmetic:
    """The builder's unit pins for `ActionPointMeter`, the shapes the 3-turn
    commanded run does not reach: a turn the engine AUTO-ended (measured zero
    of them on all three 40-turn IQ-8 archives, so no driven pin covers it), a
    run that stops mid-turn, and the turn every completed run ends ON."""

    @pytest.fixture(scope="class")
    def drv(self):
        return _load_driver_copy(DRIVER, "iq8_driver_meter")

    def test_an_explicit_end_turn_counts_what_was_left(self, drv):
        meter = drv.ActionPointMeter()
        meter.observe("/new_game", {}, _summary(1, 4))
        meter.turn_start(1, 4)
        meter.observe("/command", {}, _summary(1, 3))
        meter.observe("/command", {}, _summary(1, 1))
        meter.before_end_turn(1)
        meter.observe("/command", {"command": "end turn"}, _summary(2, 4, False))
        assert meter.snapshot() == {"ap_available": 4, "ap_spent": 3}

    def test_an_auto_ended_turn_ended_at_zero_whatever_was_last_read(self, drv):
        """`/command` auto-ends only when both pools are empty, and the
        response that did it already shows the NEXT turn — so the last reading
        in the old turn (1 AP, before the order that spent it) is stale."""
        meter = drv.ActionPointMeter()
        meter.observe("/new_game", {}, _summary(1, 4))
        meter.turn_start(1, 4)
        meter.observe("/command", {}, _summary(1, 1))
        meter.observe("/command", {}, _summary(2, 4, True))      # auto-advanced
        meter.observe("/command", {}, _summary(2, 2))
        meter.before_end_turn(2)
        meter.observe("/command", {"command": "end turn"}, _summary(3, 4, False))
        assert meter.snapshot() == {"ap_available": 8, "ap_spent": 4 + 2}

    def test_the_turn_a_completed_run_ends_on_is_not_counted(self, drv):
        meter = drv.ActionPointMeter()
        meter.turn_start(1, 4)
        meter.observe("/command", {"command": "end turn"}, _summary(2, 4, False))
        assert meter.snapshot() == {"ap_available": 4, "ap_spent": 0}

    def test_a_played_turn_the_run_stopped_inside_is_counted(self, drv):
        meter = drv.ActionPointMeter()
        meter.turn_start(5, 4)
        meter.observe("/command", {}, _summary(5, 2))
        meter.observe("/command", {"command": "end turn"},
                      {"success": False, **_summary(5, 2)})     # refused
        assert meter.snapshot() == {"ap_available": 4, "ap_spent": 2}

    def test_a_response_without_a_summary_changes_nothing(self, drv):
        meter = drv.ActionPointMeter()
        meter.turn_start(1, 4)
        for junk in ({}, {"action_summary": None}, "not a dict",
                     {"action_summary": {"turn": True, "actions_remaining": 1}},
                     {"action_summary": {"turn": "1", "actions_remaining": 1}}):
            meter.observe("/x", {}, junk)
        assert meter.snapshot() == {"ap_available": 4, "ap_spent": 0}

    def test_the_transport_hands_every_post_to_its_observers(self, drv):
        seen = []

        class _Resp:
            def raise_for_status(self):
                return None

            def json(self):
                return {"ok": 1}

        class _Client:
            def post(self, path, json=None):
                return _Resp()

        tx = drv.Transport(_Client(), "stub")
        tx.observers.append(lambda path, payload, body: seen.append((path, body)))
        tx.observers.append(lambda *_a: 1 / 0)                  # never stops a run
        assert tx.post("/command", {"command": "status"}) == {"ok": 1}
        assert seen == [("/command", {"ok": 1})]


# ═══════════════════════════════════════════════════════════════════════
# 6. The cross-hash-seed sentinel (slow)
# ═══════════════════════════════════════════════════════════════════════

_SENTINEL_TURNS = "6"


@pytest.mark.slow
class TestCrossHashSeedSentinel:

    def test_two_hash_seeds_write_the_same_jsonl(self, tmp_path):
        """Stable by construction, checked — not stable because every harness
        happens to pin 0. Measured before the fix: the two runs diverge at
        turn 4, where the London–Normandy `strait_open` row moves within the
        turn (`naval._tracked_links_for` walks a frozenset)."""
        procs = {}
        for seed in ("0", "1"):
            out = tmp_path / f"hs{seed}"
            out.mkdir()
            cmd = [sys.executable, str(DRIVER), "--script", str(COMMANDED),
                   "--diplomacy", "accept", "--turns", _SENTINEL_TURNS,
                   "--name", "iq8-sentinel", "--fresh", "--out", str(out)]
            procs[seed] = subprocess.Popen(
                cmd, cwd=str(ROOT), env=_env(out / "_saves", hashseed=seed),
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                encoding="utf-8", errors="replace")
        for seed, proc in procs.items():
            stdout, stderr = proc.communicate(timeout=900)
            assert proc.returncode == 0, f"hash seed {seed}: {stderr[-2000:]}"
        runs = {seed: tmp_path / f"hs{seed}" / "iq8-sentinel" for seed in procs}
        for seed, run_dir in runs.items():
            meta = _meta(run_dir)
            assert meta["status"] == "completed", (seed, meta["status"])
            assert meta["counters"]["turns"] == int(_SENTINEL_TURNS)
            assert meta["rng"]["pythonhashseed"] == seed
        a = (runs["0"] / "digest.jsonl").read_text(encoding="utf-8").splitlines()
        b = (runs["1"] / "digest.jsonl").read_text(encoding="utf-8").splitlines()
        first = next((i for i, (x, y) in enumerate(zip(a, b)) if x != y), None)
        assert a == b, (
            f"PYTHONHASHSEED 0 and 1 diverge at jsonl line {first}:\n"
            f"  0: {a[first] if first is not None else '(length)'}\n"
            f"  1: {b[first] if first is not None else '(length)'}\n"
            f"  lengths {len(a)} / {len(b)}")


# ═══════════════════════════════════════════════════════════════════════
# 6b. The re-exec pin (ruling 5: "keep the driver's re-exec pin")
# ═══════════════════════════════════════════════════════════════════════

class TestTheReExecPin:
    """`main()` re-execs the driver with PYTHONHASHSEED=0 when the variable
    is UNSET, so a run is hash-seeded the same way whatever the shell
    exported — and both records (`rng.pythonhashseed`, the platform block)
    say `0`, never `(unset)`. Driven with the variable REMOVED from the
    child's environment: the only arm on which the pin fires, and the one
    arm no other run in this file takes (every other `_env` SETS it so a
    wrapper's patch survives). The sweep's row `IQ8-X1` removes the pin; the
    run then completes and records `(unset)` on both keys."""

    def test_an_unset_hash_seed_is_pinned_to_zero_and_recorded(self, tmp_path):
        env = _env(tmp_path / "_saves")
        env.pop("PYTHONHASHSEED", None)
        assert "PYTHONHASHSEED" not in env                   # the arm is real
        proc, run_dir = _drive(tmp_path, "iq8-reexec", "--turns", "0", env=env)
        _ok(proc)
        meta = _meta(run_dir)
        assert meta["rng"]["pythonhashseed"] == "0", meta["rng"]
        assert _block(meta, "platform").get("pythonhashseed") == "0", meta["platform"]


# ═══════════════════════════════════════════════════════════════════════
# 7. The naval walk is ordered
# ═══════════════════════════════════════════════════════════════════════

_OPEN_FAMILY = {"open", "open_ratio", "window"}


@pytest.fixture
def world_1805():
    import contextlib
    import io
    from backend.models.world_state import WorldState
    with contextlib.redirect_stdout(io.StringIO()):
        return WorldState.from_scenario(str(SCENARIO_1805))


def _flip_everything(verdicts):
    """A `before` map under which every tracked link flips."""
    return {key: ("shut" if v["verdict"] in _OPEN_FAMILY else "open")
            for key, v in verdicts.items()}


class TestTheNavalWalkIsOrdered:
    """Direct pins: feed `_tracked_links_for` the SAME pairs in two different
    iteration orders (a stand-in for two hash seeds, which one process cannot
    have) and require one answer, in `_link_key` order."""

    def _orders(self, naval, world):
        pairs = sorted(naval.get_sea_link_pairs(world), key=naval._link_key)
        assert len(pairs) >= 2
        return tuple(pairs), tuple(reversed(pairs))

    def _tracked(self, naval, world, monkeypatch, pairs):
        monkeypatch.setattr(naval, "get_sea_link_pairs", lambda _w: pairs)
        return [naval._link_key(p) for p in naval._tracked_links_for(world, "France")]

    def test_tracked_links_come_back_in_link_key_order(self, world_1805, monkeypatch):
        from backend.game_logic import naval
        forward, backward = self._orders(naval, world_1805)
        got_forward = self._tracked(naval, world_1805, monkeypatch, forward)
        got_backward = self._tracked(naval, world_1805, monkeypatch, backward)
        assert len(got_forward) >= 2, "France must track two links for order to matter"
        assert got_forward == sorted(got_forward)                  # the control
        assert got_backward == got_forward, (
            f"the walk follows the frozenset's iteration order: {got_backward}")

    def test_verdicts_and_their_flips_come_back_in_link_key_order(
            self, world_1805, monkeypatch):
        from backend.game_logic import naval
        _forward, backward = self._orders(naval, world_1805)
        monkeypatch.setattr(naval, "get_sea_link_pairs", lambda _w: backward)
        verdicts = naval.link_verdicts_for(world_1805, "France")
        assert list(verdicts) == sorted(verdicts), list(verdicts)
        start = len(world_1805.event_log)
        naval._emit_verdict_flips(world_1805, _flip_everything(verdicts), verdicts)
        emitted = [f"{e['link_a']}|{e['link_b']}"
                   for e in world_1805.event_log[start:]
                   if str(e.get("type", "")).startswith("strait_")]
        assert len(emitted) == len(verdicts) >= 2
        assert emitted == sorted(emitted), emitted


# Run in a child per hash seed: the raw frozenset order, the tracked walk,
# the verdict keys, the flip emission order and the SERIALIZED
# `fleets["__naval__"]["verdicts"]` key order after a real naval tick.
_NAVAL_PROBE = r'''
import contextlib, io, json, os, random, sys
sys.path.insert(0, sys.argv[1])
with contextlib.redirect_stdout(io.StringIO()):
    from backend.game_logic import naval
    from backend.models.world_state import WorldState
    world = WorldState.from_scenario(sys.argv[2])
open_family = {"open", "open_ratio", "window"}
raw = [naval._link_key(p) for p in naval.get_sea_link_pairs(world)]
tracked = [naval._link_key(p) for p in naval._tracked_links_for(world, "France")]
verdicts = naval.link_verdicts_for(world, "France")
before = {k: ("shut" if v["verdict"] in open_family else "open") for k, v in verdicts.items()}
start = len(world.event_log)
with contextlib.redirect_stdout(io.StringIO()):
    naval._emit_verdict_flips(world, before, verdicts)
emitted = [f"{e['link_a']}|{e['link_b']}" for e in world.event_log[start:]
           if str(e.get("type", "")).startswith("strait_")]
random.seed(0)
with contextlib.redirect_stdout(io.StringIO()):
    naval.process_naval_turn(world)
stored = list((world.fleets.get(naval.META_KEY) or {}).get("verdicts", {}))
print("IQ8NAVAL " + json.dumps({"raw": raw, "tracked": tracked,
                                "verdicts": list(verdicts), "emitted": emitted,
                                "stored": stored}))
'''


class TestTheNavalWalkIsHashSeedFree:

    SEEDS = ("0", "1", "12345")

    @pytest.fixture(scope="class")
    def probes(self, tmp_path_factory):
        base = tmp_path_factory.mktemp("iq8_naval")
        script = base / "naval_probe.py"
        script.write_text(_NAVAL_PROBE, encoding="utf-8")
        out = {}
        for seed in self.SEEDS:
            env = _env(base / "_saves", hashseed=seed)
            proc = subprocess.run(
                [sys.executable, str(script), str(ROOT), str(SCENARIO_1805)],
                cwd=str(ROOT), env=env, capture_output=True, text=True,
                encoding="utf-8", errors="replace", timeout=600)
            assert proc.returncode == 0, proc.stderr[-2000:]
            line = next(ln for ln in proc.stdout.splitlines()
                        if ln.startswith("IQ8NAVAL "))
            out[seed] = json.loads(line[len("IQ8NAVAL "):])
        return out

    def test_the_raw_frozenset_still_varies_so_this_pin_can_see_a_revert(self, probes):
        """Sensitivity arm. The fix sorts the WALK, not the cache; if the raw
        iteration order ever stopped varying across these seeds, the
        agreement pins below would pass on an unsorted walk too."""
        raws = {tuple(probes[s]["raw"]) for s in self.SEEDS}
        assert len(raws) > 1, "the sea-link frozenset iterates identically on every seed"

    @pytest.mark.parametrize("field", ["tracked", "verdicts", "emitted", "stored"])
    def test_every_walk_agrees_across_hash_seeds(self, probes, field):
        orders = {seed: probes[seed][field] for seed in self.SEEDS}
        assert len(orders["0"]) >= 2, orders
        assert all(order == orders["0"] for order in orders.values()), (
            f"`{field}` order depends on PYTHONHASHSEED: {orders}")
        assert orders["0"] == sorted(orders["0"]), orders["0"]


# ═══════════════════════════════════════════════════════════════════════
# 8. The table rule (recon §5.4 item 7 — the builder's addition)
# ═══════════════════════════════════════════════════════════════════════

PLAYTESTING = ROOT / "docs" / "PLAYTESTING.md"
ARCHIVES = ROOT / "docs" / "audits" / "playtest_digests"
_PROVENANCE_COLUMNS = ("platform", "engine", "`PYTHONHASHSEED`", "flags", "archive")


def _cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def _commanded_table():
    """The commanded-arm table in PLAYTESTING.md as (header cells, rows)."""
    lines = PLAYTESTING.read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(lines):
        cells = _cells(line)
        if cells[:1] == ["measurement"] and "archive" in cells:
            rows = []
            for row in lines[i + 2:]:
                if not row.startswith("|"):
                    break
                rows.append(_cells(row))
            return cells, rows
    raise AssertionError("PLAYTESTING.md has no commanded table headed `measurement`")


class TestTheTableRule:
    """Ruling 6: every measured table carries platform, commit, hash seed,
    flags and the archived digest names; a figure with no archive is marked
    UNCITABLE. A census over the one measured table the page holds, against
    the archive directory itself."""

    def test_the_commanded_table_carries_the_provenance_columns(self):
        header, rows = _commanded_table()
        missing = [c for c in _PROVENANCE_COLUMNS if c not in header]
        assert not missing, (missing, header)
        assert len(rows) >= 3, rows

    def test_every_row_names_an_existing_archive_or_says_uncitable(self):
        header, rows = _commanded_table()
        col, seed_col = header.index("archive"), header.index("`PYTHONHASHSEED`")
        named = uncitable = 0
        for row in rows:
            cell = row[col]
            if "UNCITABLE" in cell:
                uncitable += 1
                continue
            names = re.findall(r"`([^`]+)`", cell)
            assert names, f"a row with neither an archive nor UNCITABLE: {row[0]!r}"
            for name in names:
                assert (ARCHIVES / name / "meta.json").is_file(), (row[0], name)
                assert (ARCHIVES / name / "digest.md").is_file(), (row[0], name)
                meta = json.loads((ARCHIVES / name / "meta.json").read_text(
                    encoding="utf-8"))
                # The row's hash seed is the archive's own, not restated.
                assert meta.get("rng", {}).get("pythonhashseed") == \
                    row[seed_col].strip("`"), (row[0], name, row[seed_col])
            named += 1
        assert named >= 1 and uncitable >= 1, (named, uncitable)

    def test_the_iq8_row_cites_archives_whose_meta_names_the_engine(self):
        """The row added at this HEAD is citable in the new sense: its three
        archives carry the four blocks and the counters, and each resolved
        seed is the seed the row's column names."""
        header, rows = _commanded_table()
        col = header.index("archive")
        assert any("iq8-cmd-historical" in r[col] for r in rows), [r[0] for r in rows]
        for seed in ("historical", "austerlitz", "marengo"):
            meta = json.loads((ARCHIVES / f"iq8-cmd-{seed}" / "meta.json").read_text(
                encoding="utf-8"))
            for key in ("requested", "resolved", "platform", "engine_revision"):
                assert isinstance(meta.get(key), dict), (seed, key)
            assert meta["resolved"]["campaign_seed"] == seed
            assert meta["resolved"]["scenario_name"] == BOARD_1805
            assert meta["status"] == "completed" and meta["counters"]["turns"] == 40
            assert {"ap_available", "ap_spent", "cmd_refused"} <= set(meta["counters"])
            assert _HEX40.match(meta["engine_revision"]["git_commit"] or "")


# ═══════════════════════════════════════════════════════════════════════
# Item 8 (IQ6-X1) — an in-process run equals a fresh one: Berthier's
# rotation begins with the campaign
# ═══════════════════════════════════════════════════════════════════════

_BATTLE = {"attacker": {"name": "Ney", "nation": "France", "casualties": 3000,
                        "personality": "aggressive"},
           "defender": {"name": "Mack", "nation": "Austria", "casualties": 5000,
                        "personality": "literal"},
           "outcome": "attacker_victory", "attacker_original_strength": 40000,
           "defender_original_strength": 30000, "location": "Swabia",
           "terrain": "plains"}


def _drive_in_process(name, turns, out_root):
    """The IQ-6 `_drive` idiom: the driver's own `run()` in THIS process —
    the only way to drive two campaigns through one process, which is what
    the item is about. NO test-side reset of `_OBSERVATION_COUNTS` anywhere
    in here: the invariant under test is that production does it. Everything
    the driver touches is restored (the env it sets, `backend.main`'s world
    and parser — `/new_game` never rebuilds the parser, so a mock one is
    installed, as IQ-6/IQ-7 do)."""
    import argparse
    import contextlib
    import io
    keys = ("LLM_MODE", "SOVEREIGN_SEED", "INK_IRON_SAVE_DIR", "DEBUG_MODE",
            "SOVEREIGN_SCENARIO", "SOVEREIGN_SMOKE_START", "SOVEREIGN_MAP")
    prior_env = {k: os.environ.get(k) for k in keys}
    os.environ["LLM_MODE"] = "mock"
    os.environ["SOVEREIGN_SEED"] = "historical"
    with contextlib.redirect_stdout(io.StringIO()):
        import backend.main as M
        from backend.commands.parser import CommandParser
    prior_main = (M.world, M.game_state.get("world"), M.parser)
    spec = importlib.util.spec_from_file_location(
        f"playtest_driver_iq8_item8_{name}", str(DRIVER))
    drv = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(drv)
    out_root = Path(out_root)
    try:
        os.environ["INK_IRON_SAVE_DIR"] = str(out_root / f"saves_{name}")
        with contextlib.redirect_stdout(io.StringIO()):
            M.parser = CommandParser()
        ns = argparse.Namespace(
            name=name, turns=turns, seed="historical", llm="mock", scenario="",
            script="", from_save="", http="", out=str(out_root / "out"),
            save_at="", objection="", diplomacy="accept", redemption="",
            petition="", declare_war="", paradox="", rebellion="", sabotage="",
            reward="", last_stand="", contact="", missions="",
            client_petition="", reload_every=0, cheats=False,
            strict=False, verbose=False, fresh=True, archive=False)
        with contextlib.redirect_stdout(io.StringIO()):
            rc = drv.run(ns)
        assert rc == 0, rc
    finally:
        M.world, M.parser = prior_main[0], prior_main[2]
        M.game_state["world"] = prior_main[1]
        for key, value in prior_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
    run_dir = out_root / "out" / name
    return {
        "jsonl": (run_dir / "digest.jsonl").read_text(encoding="utf-8").splitlines(),
        "md": (run_dir / "digest.md").read_text(encoding="utf-8").splitlines(),
        "records": _jsonl(run_dir),
    }


def _boot_1805():
    import contextlib
    import io
    from backend.models.world_state import WorldState
    with contextlib.redirect_stdout(io.StringIO()):
        return WorldState.from_scenario(str(SCENARIO_1805))


class TestTheRotationBeginsWithTheCampaign:
    """IQ-8 item 8 — IQ6-X1 (`BUG_FIXES.md` §Europe Speaks Its Mind).

    FA-D24 made Berthier's after-battle line ROTATE through its bank per
    pair of commanders on a process-global counter that nothing reset, so a
    SECOND campaign created in one process continued the first campaign's
    count and printed a different line for the same battle — measured on
    this board: turn 1, Charles vs Massena, *"Stalemate … glare at each
    other"* against *"An inconclusive affair"*, casualties identical. The
    counter is now emptied at the ONE chokepoint every world passes,
    `WorldState.__init__` (`battle_report.reset_observation_rotation`,
    lever `THE_ROTATION_BEGINS_WITH_THE_CAMPAIGN`).

    THE RULE, stated and pinned: the rotation begins with the CAMPAIGN'S
    CREATION — a new game, a scenario boot or a LOAD alike. A loaded
    campaign does NOT continue its own rotation (it cannot: the counter is
    display-only and never serialized, FA-D24's own contract); it restarts
    exactly as loading that save in a fresh process would. The invariant is
    "in-process equals fresh", and "rotates within a campaign" still holds
    from the creation onward. Display only (GR6): the reset spends no RNG
    draw, so M1–M7 and `BASELINE_SERIES` cannot move.
    """

    @pytest.fixture(scope="class")
    def twice(self, tmp_path_factory):
        """Two consecutive in-process drives of the same short ambient
        campaign — the completion item, with the production lever as it
        ships and NO test-side reset."""
        root = tmp_path_factory.mktemp("iq8_item8_twice")
        first = _drive_in_process("first", 2, root)
        second = _drive_in_process("second", 2, root)
        return first, second

    def test_two_consecutive_in_process_drives_are_byte_identical(self, twice):
        """The completion item (IQ6-X1): the second campaign driven in the
        same process writes the same digest as the first — records and
        prose — with no test-side reset anywhere."""
        first, second = twice
        assert first["jsonl"] == second["jsonl"]
        assert first["md"][1:] == second["md"][1:]   # line 1 is the run name
        # Vacuity guard: the compared span carries at least one battle line,
        # which is where the two drives used to disagree.
        battles = [r for r in first["records"] if r.get("kind") == "battle"]
        assert battles, "the ambient board must fight in the compared span"
        assert any(" — " in str(r.get("headline", "")) for r in battles), (
            "a battle line carries Berthier's observation after the dash")

    def test_with_the_reset_removed_the_second_drive_diverges(self, tmp_path,
                                                            monkeypatch):
        """The sensitivity arm — the lever DOWN is the reset removed, and it
        is also today's behaviour reproduced: the second drive continues the
        first drive's count and the first differing digest line is a BATTLE
        line (the observation), not a mechanic."""
        from backend.game_logic import battle_report as BR
        monkeypatch.setattr(BR, "THE_ROTATION_BEGINS_WITH_THE_CAMPAIGN", False)
        # The arm needs the first drive to be the fresh one, so it starts
        # clean by hand — this is the sensitivity arm, not the completion pin.
        BR._OBSERVATION_COUNTS.clear()
        try:
            first = _drive_in_process("down_first", 2, tmp_path)
            assert BR._OBSERVATION_COUNTS, "the first drive fought and counted"
            second = _drive_in_process("down_second", 2, tmp_path)
        finally:
            BR._OBSERVATION_COUNTS.clear()
        assert first["jsonl"] != second["jsonl"]
        diverged = next((a, b) for a, b in zip(first["jsonl"], second["jsonl"])
                        if a != b)
        assert all('"kind": "battle"' in line for line in diverged), diverged
        # Same men, same butcher's bill, a different line: display only.
        head = lambda line: json.loads(line)["headline"].split(" — ")[0]  # noqa: E731
        assert head(diverged[0]) == head(diverged[1])

    def test_every_world_creation_empties_the_counter(self):
        """The three roads to a world — the bare constructor, `from_dict`
        (which is `load_game`'s road) and `from_scenario` — all pass the
        reset. No other production seam does (the census below)."""
        from backend.game_logic import battle_report as BR
        from backend.models.world_state import WorldState
        boot = _boot_1805()
        saved = boot.to_dict()
        for label, make in (
                ("bare", lambda: WorldState(player_nation="France")),
                ("from_dict", lambda: WorldState.from_dict(saved)),
                ("from_scenario", _boot_1805)):
            BR._OBSERVATION_COUNTS[("Ney", "Mack")] = 3
            make()
            assert BR._OBSERVATION_COUNTS == {}, label

    def test_a_loaded_campaign_restarts_its_rotation_as_a_fresh_process_would(self):
        """The rule for a LOAD, pinned: after two battles between one pair,
        loading a save (a `from_dict`) makes the next line the FIRST line a
        fresh process would print — not the third."""
        from backend.game_logic import battle_report as BR
        from backend.models.world_state import WorldState
        boot = _boot_1805()
        BR._OBSERVATION_COUNTS.clear()
        fresh_first = BR._pick_observation(dict(_BATTLE), "France")
        fresh_second = BR._pick_observation(dict(_BATTLE), "France")
        assert fresh_first != fresh_second        # FA-D24: it rotates
        WorldState.from_dict(boot.to_dict())      # the load
        assert BR._pick_observation(dict(_BATTLE), "France") == fresh_first
        BR._OBSERVATION_COUNTS.clear()

    def test_lever_down_keeps_the_process_global_counter(self, monkeypatch):
        """False reproduces today: a world creation leaves the count alone,
        so the loaded campaign would print the THIRD line."""
        from backend.game_logic import battle_report as BR
        from backend.models.world_state import WorldState
        monkeypatch.setattr(BR, "THE_ROTATION_BEGINS_WITH_THE_CAMPAIGN", False)
        BR._OBSERVATION_COUNTS.clear()
        first = BR._pick_observation(dict(_BATTLE), "France")
        BR._pick_observation(dict(_BATTLE), "France")
        WorldState(player_nation="France")
        assert BR._OBSERVATION_COUNTS != {}
        assert BR._pick_observation(dict(_BATTLE), "France") != first
        BR._OBSERVATION_COUNTS.clear()

    def test_the_reset_is_display_only(self):
        """GR6 twice over: the reset spends no module-random draw, and the
        counter reaches no save (nothing to continue from — which is why a
        load restarts)."""
        import random
        from backend.game_logic import battle_report as BR
        random.seed(3)
        expected = random.random()
        random.seed(3)
        BR._OBSERVATION_COUNTS[("Ney", "Mack")] = 5
        BR.reset_observation_rotation()
        assert random.random() == expected
        assert "_OBSERVATION_COUNTS" not in json.dumps(_boot_1805().to_dict())

    def test_the_world_boot_is_the_only_production_caller(self):
        """Census over `backend/`: the counter is written in `battle_report`
        alone, and the reset is called from `WorldState.__init__` alone —
        so nothing can restart the rotation mid-campaign."""
        writers, callers = [], []
        for path in (ROOT / "backend").rglob("*.py"):
            src = path.read_text(encoding="utf-8")
            if "_OBSERVATION_COUNTS" in src:
                writers.append(path.name)
            if "reset_observation_rotation(" in src:
                callers.append(path.name)
        assert sorted(writers) == ["battle_report.py"], writers
        assert sorted(callers) == ["battle_report.py", "world_state.py"], callers
        world_src = (ROOT / "backend" / "models" / "world_state.py").read_text(
            encoding="utf-8")
        init_body = world_src[world_src.index("    def __init__(self, player_nation"):]
        init_body = init_body[:init_body.index("\n    def ", 10)]
        assert init_body.count("reset_observation_rotation()") == 1
        assert world_src.count("reset_observation_rotation()") == 1
