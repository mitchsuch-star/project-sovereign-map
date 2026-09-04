"""PLAYTEST DRIVER — scripted campaigns at the /command surface, digested.

The standing playtest harness (Aug 2026, "make the test easier" session).
Documentation of record: docs/PLAYTESTING.md — future sessions START THERE.

What it is
----------
A player that drives the game through the SAME HTTP surface the Godot
client uses (parser -> executor -> response formatting -> popup
passthroughs), answers blocking popups/dialogues by a stated policy, and
writes a compact per-turn DIGEST so a session reads ONE small file
instead of a hundred raw JSON payloads. The Aug-9 CA9 playtest was 108
hand-driven request/response pairs; this replaces that loop.

Two transports, one driver:
  * in-process (default): FastAPI TestClient. No server to start, no
    stale-backend trap, no port collision, fully seeded. Saves are
    SANDBOXED via INK_IRON_SAVE_DIR before backend import, so /new_game's
    autosave NEVER touches the player's real saves (the TUT-F2 lesson).
  * --http URL: the same driving against a LIVE server (wire testing).
    That server's own autosave WILL be touched — the driver warns.

Honesty rules (same spirit as tools/a2_strangulation_drive.py):
  * every order goes through POST /command — the real parser and the
    real executor, never hand-set state;
  * every popup answered is LOGGED in the digest with the policy that
    answered it — an unattended run hides nothing;
  * unknown blocking shapes are logged loudly and, under --strict, fail
    the run (exit 3) instead of being silently clicked through.

Usage
-----
  # 12 ambient turns (France issues no orders), mock parser, seeded:
  python tools/playtest_driver.py --turns 12 --name ambient12

  # scripted campaign:
  python tools/playtest_driver.py --script tools/playtest_scripts/danube.json

  # continue from a fixture save:
  python tools/playtest_driver.py --from-save tests/fixtures/playtest_saves/fixture_t10_ambient.json --turns 5

  # drive a LIVE server instead (the wire test):
  python tools/playtest_driver.py --http http://127.0.0.1:8005 --turns 3

  # France actively sues for peace (WO slice 5) — the bilateral-peace
  # path, exercised instead of assumed:
  python tools/playtest_driver.py --turns 20 --diplomacy propose

Outputs (under --out, default tools/playtest_runs/<name>/ — gitignored):
  digest.md      the human read — one block per turn
  digest.jsonl   the machine read — one record per event
  meta.json      seed/mode/args/finish state + the RNG record (WO-H slice 1)
  saves/         the sandboxed SAVE_DIR (autosave + --save-at snapshots)

Determinism (WO-H slice 1, Aug 21 2026 — Mode A ONLY):
  * the module RNG is reseeded at boot and at every turn boundary from
    sha256(f"{seed}:{world_turn}") — sufficient because the backend has
    ZERO random.Random() instances (spec §2 H-1), so all twenty consuming
    modules share the module-level RNG this process owns;
  * PYTHONHASHSEED is pinned: main() re-execs the driver with
    PYTHONHASHSEED=0 when the variable is unset (hash order is
    load-bearing — the BASELINE_SERIES runner pins it for the same
    reason), and meta.json records the value either way;
  * --http (Mode B) drives a SEPARATE server process whose RNG the driver
    cannot reach — Mode B digests carry a "NONDETERMINISTIC" banner in
    meta.json, as does any --llm anthropic run (live parses vary).

Archiving (WO-H slice 1): tools/playtest_runs/ is gitignored and
overwritten, so a digest there is a local artifact, not evidence. The
--archive flag copies digest.md + meta.json to
docs/audits/playtest_digests/<name>/ (committed). A memo may only cite an
archived digest.

Script file format (all keys optional):
  {
    "name": "danube-opening",
    "seed": "historical",
    "llm": "mock",
    "turns": {"1": ["Ney, attack Mack", "status"], "3": ["end turn"]},
    "policy": {"objection": "trust", "diplomacy": "decline"}
  }
Turns not listed just end. An explicit "end turn" in a list is allowed
but implicit — the driver always ends the turn after the list runs.
"""

import argparse
import hashlib
import json
import os
import random
import re
import shutil
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# ═══════════════════════════════════════════════════════════════════════
# Determinism (WO-H slice 1) — the module-RNG seeding scheme, recorded
# verbatim in meta.json so a digest reader can audit the derivation.
# Seeding the DRIVER's `random` module seeds the BACKEND's too: Mode A is
# in-process, and the backend holds zero random.Random() instances
# (WEIRD_OUTCOMES_SPEC §2 H-1 — verified, not assumed).
# ═══════════════════════════════════════════════════════════════════════

RNG_SCHEME = ("module RNG reseeded at boot (world_turn=0) and at each "
              "turn boundary: random.seed(int(hashlib.sha256("
              "f'{seed}:{world_turn}'.encode()).hexdigest(), 16) "
              "& 0xFFFFFFFF)")


def seed_module_rng(campaign_seed, world_turn):
    """Deterministic module-RNG reseed — sha256, never hash() (PYTHONHASHSEED
    is pinned separately, but the derivation must not depend on it)."""
    digest = hashlib.sha256(f"{campaign_seed}:{world_turn}".encode()).hexdigest()
    random.seed(int(digest, 16) & 0xFFFFFFFF)

# ═══════════════════════════════════════════════════════════════════════
# Answer policy — every default is a DECISION a digest reader can audit.
# ═══════════════════════════════════════════════════════════════════════

POLICY_DEFAULTS = {
    # Marshal objection: trust builds goodwill and never dead-ends a run.
    "objection": "trust",           # trust | insist | compromise
    # Incoming proposals / settlement offers / envoy letters: decline —
    # an unattended run must not sign treaties nobody scripted. Override
    # per-run when the playtest IS about diplomacy.
    #
    # `propose` (WO slice 5) is the ACTIVE arm: France sues. It answers
    # incoming exactly as `accept` does — a run that asks for peace must
    # sign the peace it is handed, or it measures nothing — and in
    # addition sends ONE bilateral peace command per turn, round-robin
    # over the courts France is at war with. It exists because the WO
    # campaigns never once pressed the bilateral-peace path: every arm
    # declined, so a war that both sides would have ended stayed open for
    # thirty turns and nobody could tell whether that was the engine or
    # the harness.
    "diplomacy": "decline",         # decline | accept | first | propose
    # Post-capture: secure (plunder is the special case worth scripting).
    "capture": "secure",            # secure | plunder
    # W6-8 estate stage of the same popup:
    "estate": "respect",            # respect | confiscate
    # Ney's recklessness trigger:
    "glorious_charge": "restrain",  # restrain | charge
    # Talleyrand pre-proposal objection:
    "diplomatic_objection": "proceed",   # proceed | modify | cancel
    # A marshal's redemption audience (trust <= 20; rare). Answered through
    # POST /respond_to_redemption since Sept 1, 2026 — before that this key
    # was read by nothing (WO-41's landing found it).
    "redemption": "dismiss",        # dismiss | grant_autonomy | administrative_role
    # Marshal petitions (jealousy/rivalry/Fontainebleau/war-weary):
    # first ENABLED option — usually the free acknowledge arm.
    "petition": "first_enabled",
    # Strategic interrupts (cannon fire / blocked path / ally moving):
    # first offered option.
    "interrupt": "first",
    # PT-F1 war purpose gate: the script ORDERED the attack, so backing
    # out would contradict it — an unattended run declares Conquest.
    "war_purpose": "1",
    # NA-5 ultimatums: France does not bend unscripted.
    "ultimatum": "defy",
    # CR-2 / naval-confirm clarifications ("state": "awaiting_clarification"):
    # first offered option, answered as the typed index "1" — the server's
    # own interpret_clarification_answer resolves it to the first actionable
    # option's full command string (WO-H slice 1 item 4; before this arm the
    # driver was blind to EVERY clarification question, which was the whole
    # of WO-D3's measured failure).
    "clarification": "first",   # first | cancel
    # IGR-F letter-book rows (routine small-court asks): answered through
    # POST /mailbox/respond once per turn, EXPLICIT and counted in the
    # digest (WO-H slice 1 item 5). `diplomacy: accept` accepts them.
    # ⚠ An explicit decline is NOT the old silent lapse (review round):
    # it writes the serialized diplomatic_refusals record and a 3-turn
    # court cooldown where a lapse wrote no record and a 2-turn cooldown
    # (type cooldown 6 either way; the refusal entries are behaviorally
    # inert for the player direction — war_council's ladder is guarded
    # AI-vs-AI). A per-decline cadence shift vs pre-Aug-21 digests is the
    # HARNESS's doing, not the game's.
    # (No separate policy key: the letter-book is diplomacy.)
}

# Diplomacy modes that SIGN what is put in front of them. `propose` is
# here because an arm that sues for peace and then declines the peace it
# is offered measures nothing.
ACCEPTING_DIPLOMACY_MODES = ("accept", "first", "propose")

# Hard-stop dialogue types whose answer is a KEYWORD/index the driver
# knows even when the payload enumerates no options list. Anything not
# here and without options is left standing (and fails under --strict).
DIALOGUE_TYPE_ANSWERS = {
    "war_purpose_selection": "war_purpose",     # policy key
    "incoming_ultimatum": "ultimatum",          # policy key
    "incoming_proposal": "diplomacy",           # decline|accept|first
    "incoming_settlement_offer": "diplomacy",
    # The player's OWN action confirmation (e.g. the declare-war confirm
    # after Talleyrand's objection was answered "proceed") — confirming
    # is the only coherent continuation of the script's order.
    "proposal_confirm": "confirm",
    # The settlement sibling of proposal_confirm ("the terms on the
    # table"): ships WITHOUT an options list, so it must be in this table
    # to reach the keyword-less fallback ("1" under accept, "decline"
    # under decline). Found blocked in the Aug-15 comprehensive playtest
    # (diplomacy arm, fixture_t20 + --diplomacy accept).
    "settlement_confirm": "diplomacy",
    # PC15-3/PC15-H: the pair-substitute chooser — previously unanswerable
    # by policy (the Aug-15 wedge). An unattended run stays with the joint
    # settlement; typed "keep" resolves keep_joint_settlement.
    "settlement_pair_substitute_confirm": "keep",
}

# Popup keys that are DISPLAY-ONLY: delivered popped (the queue clears on
# inclusion), nothing to answer — digest and move on.
DISPLAY_ONLY_KEYS = (
    "coalition_popup",
    "diplomatic_sabotage",
    "vassal_rebellion_imminent",
    "nation_proclamation",
    "proposal_result",
    "commitment_paradox_popup",
    "battle_diorama",
)

# A popup answered can surface the next; cap the chain so a genuine loop
# cannot hang a run.
# Row NP (Aug 15, 2026): raised 8 -> 16. The Emperor's Presence makes a
# big stack win hard enough to take several provinces in ONE turn, and
# each capture is its own decision (plus a W6-8 estate stage behind it) —
# at 8 the chain ran out mid-sequence, `end turn` was refused forever
# ("you must decide the fate of Marshal X's estate first"), and the run
# reported `blocked` on what is a HARNESS limit, not an engine defect.
MAX_ANSWERS_PER_POST = 16
# FA-74: how many times one dialogue id may be ANSWERED in a chain when the
# backend keeps refusing it as STALE (a DIFFERENT dialogue was on top).
# Two attempts = one retry: the refusal reply carries the dialogue actually
# current, so the chain answers that and the original comes back under its
# own identity. A surface that goes stale twice is wedged, and the digest
# says so rather than spinning.
MAX_STALE_ATTEMPTS = 2


# FA-87/FA-86: a line of pure punctuation carries nothing. The bombardment
# message opens with `'=' * 40` on its own line (combat_executor), so every
# artillery attack in every archived digest rendered as
# `========================================` — six times in audit-ambient40
# alone, and once under a 🏴 capture flag.
_HAS_WORD_RE = re.compile(r"[0-9A-Za-z]")
# A leading bracketed annotation — `[Shield] …`, `[Combat] …`, `[!] …`,
# `[Square broken — …]` — is a tactical FOOTNOTE the engine prepends to the
# real prose. It won the summary slot on every row that carried one, which
# is why `audit-propose` reports "ArchdukeJohn's DEFENSIVE stance hampers
# offensive operations" as the enemy's action for a turn he captured two
# French provinces.
_ANNOTATION_RE = re.compile(r"^\[[^\]]*\]")


def first_line(text, limit=170):
    if not text:
        return ""
    for line in str(text).splitlines():
        line = line.strip()
        if line and _HAS_WORD_RE.search(line):
            return (line[: limit - 1] + "…") if len(line) > limit else line
    return ""


def salient_line(text, limit=170):
    """`first_line`, but a bracketed tactical annotation yields to the prose.

    Falls back to `first_line` when every line is an annotation — an
    annotation is better than nothing.
    """
    for line in str(text or "").splitlines():
        line = line.strip()
        if (line and _HAS_WORD_RE.search(line)
                and not _ANNOTATION_RE.match(line)):
            return (line[: limit - 1] + "…") if len(line) > limit else line
    return first_line(text, limit)


def matching_line(text, needles, limit=170):
    """The SENTENCE that carries one of `needles`; else `salient_line`.

    The capture detector greps the whole message and then printed its FIRST
    line, so a real conquest was captioned with whatever annotation happened
    to precede it — measured in the archive, `🏴 Austria: [Shield] Massena is
    at his best with his back to the wall!` and, once,
    `🏴 Austria: ========================================`.

    Sentence, not line, because the engine puts the conquest at the END of a
    long combat paragraph: *"…Casualties: ArchdukeCharles's army 1,188, Deroy
    7,465. Both armies remain in the field. Bohemia has been captured by
    Austria!"* — a whole-line answer truncates before the only clause that
    justifies the flag.
    """
    for line in str(text or "").splitlines():
        parts = [p.strip() for p in re.split(r"(?<=[.!?])\s+", line.strip())]
        for i, sentence in enumerate(parts):
            if not sentence or not any(n in sentence.lower() for n in needles):
                continue
            # Keep as much of the run-up as fits, ending on the match — the
            # capture clause is often a trailing fragment whose subject is
            # the sentence before it ("ArchdukeJohn marches from Tyrol into
            # Carniola unopposed! (232 lost to march) Captured: Bavaria →
            # Austria").
            start = i
            while start > 0 and len(" ".join(parts[start - 1:i + 1])) <= limit:
                start -= 1
            excerpt = " ".join(parts[start:i + 1])
            if len(excerpt) > limit:
                excerpt = "…" + excerpt[-(limit - 1):]
            return excerpt
    return salient_line(text, limit)


def dig(payload, *names, default=None):
    """Tolerant recursive search: first value under any of the given key
    names, breadth-first, dicts and lists. Digest extraction only — never
    used to make a game decision."""
    from collections import deque

    queue = deque([payload])
    while queue:
        node = queue.popleft()
        if isinstance(node, dict):
            for name in names:
                if name in node and node[name] is not None:
                    return node[name]
            queue.extend(node.values())
        elif isinstance(node, list):
            queue.extend(node)
    return default


# ═══════════════════════════════════════════════════════════════════════
# Transport
# ═══════════════════════════════════════════════════════════════════════

class Transport:
    """POST/GET against either an in-process TestClient or a live server.

    In-process, the backend prints its whole console to stdout; that
    noise defeats the read-one-file goal, so it is redirected to
    server_console.log unless --verbose."""

    def __init__(self, client, label, console_log=None):
        self.client = client
        self.label = label
        self.console_log = console_log

    def _call(self, fn):
        import contextlib
        if self.console_log is None:
            return fn()
        with self.console_log.open("a", encoding="utf-8", errors="replace") as fh:
            with contextlib.redirect_stdout(fh):
                return fn()

    def post(self, path, payload=None):
        response = self._call(lambda: self.client.post(path, json=payload or {}))
        response.raise_for_status()
        return response.json()

    def get(self, path):
        response = self._call(lambda: self.client.get(path))
        response.raise_for_status()
        return response.json()


def make_inprocess_transport(args, out_dir):
    """Set the env BEFORE the backend import — the import boots the world.

    load_dotenv() does not override existing env vars, so everything set
    here wins over the dev .env (which says LLM_MODE=anthropic and
    DEBUG_MODE=true — neither belongs in an unattended playtest unless
    asked for).
    """
    import contextlib

    os.environ["LLM_MODE"] = args.llm
    os.environ["SOVEREIGN_SEED"] = args.seed
    os.environ["INK_IRON_SAVE_DIR"] = str(out_dir / "saves")
    os.environ["DEBUG_MODE"] = "true" if args.cheats else "false"
    # Ambient leaks that would silently reshape the boot world:
    os.environ.pop("SOVEREIGN_SCENARIO", None)
    os.environ.pop("SOVEREIGN_SMOKE_START", None)
    os.environ.pop("SOVEREIGN_MAP", None)

    console_log = None if args.verbose else out_dir / "server_console.log"

    from fastapi.testclient import TestClient
    if console_log is not None:
        with console_log.open("w", encoding="utf-8", errors="replace") as fh:
            with contextlib.redirect_stdout(fh):
                import backend.main as backend_main
    else:
        import backend.main as backend_main

    return Transport(TestClient(backend_main.app), "in-process", console_log)


def make_http_transport(args):
    import httpx

    print(f"[driver] WARNING: driving LIVE server {args.http} — its autosave "
          f"and world state WILL be modified.", file=sys.stderr)
    client = httpx.Client(base_url=args.http, timeout=120.0)
    return Transport(client, args.http)


# ═══════════════════════════════════════════════════════════════════════
# Digest
# ═══════════════════════════════════════════════════════════════════════

class Digest:
    def __init__(self, out_dir, meta):
        self.md_path = out_dir / "digest.md"
        self.jsonl_path = out_dir / "digest.jsonl"
        self.meta_path = out_dir / "meta.json"
        self.meta = meta
        self.unknown_blockers = []
        self.recent = []
        self._last_provinces = None
        self.counters = {"commands": 0, "popups": 0, "battles": 0, "turns": 0}
        header = (f"# Playtest digest — {meta['name']}\n\n"
                  f"seed `{meta['seed']}` · llm `{meta['llm']}` · "
                  f"transport {meta['transport']} · policy "
                  f"`{json.dumps(meta['policy'])}`\n")
        self.md_path.write_text(header, encoding="utf-8")
        self.jsonl_path.write_text("", encoding="utf-8")
        self._write_meta()

    def _write_meta(self):
        self.meta_path.write_text(
            json.dumps(self.meta | {"counters": self.counters,
                                    "unknown_blockers": self.unknown_blockers},
                       indent=2),
            encoding="utf-8")

    def _md(self, line):
        with self.md_path.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")

    def record(self, kind, **fields):
        with self.jsonl_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"kind": kind} | fields, default=str) + "\n")

    def turn_header(self, turn, label):
        self.counters["turns"] += 1
        self._md(f"\n## Turn {turn}" + (f" — {label}" if label else ""))
        self.record("turn", turn=turn, label=label)

    def command(self, text, response):
        self.counters["commands"] += 1
        ok = "✓" if response.get("success", True) else "✗"
        self._md(f"- CMD `{text}` → {ok} {first_line(response.get('message'))}")
        self.record("command", text=text, success=response.get("success"),
                    message=first_line(response.get("message"), 400))

    def battle(self, report):
        self.counters["battles"] += 1
        summary = report.get("casualty_summary") if isinstance(report, dict) else None
        if isinstance(summary, dict) and summary.get("attacker_name"):
            head = (f"{summary['attacker_name']} (lost "
                    f"{summary.get('attacker_casualties', '?')}) vs "
                    f"{summary.get('defender_name', '?')} (lost "
                    f"{summary.get('defender_casualties', '?')})")
            observation = first_line(dig(report, "observation"), 120)
            if observation:
                head += f" — {observation}"
        else:
            head = (first_line(dig(report, "headline", "summary", "outcome",
                                   "observation", "message"))
                    or "battle report captured")
        self._md(f"  - ⚔ {head}")
        self.record("battle", headline=head)

    def popup(self, key, summary, answer):
        self.counters["popups"] += 1
        # Signature trail for drain()'s cycle guard — every answered
        # surface passes through here, so this is the one honest place
        # to notice that the run is going in circles.
        #
        # The signature MUST include the summary: every dialogue family
        # shares the key `diplomatic_dialogue`, so (key, answer) alone
        # read "decline an incoming proposal, then decline a settlement
        # offer" as a loop and stopped a chain that was making progress.
        # And a surface that was NOT answered is not evidence of
        # anything — only real answers count.
        # A skipped stale passthrough is likewise not an answer — it is the
        # guard WORKING. Counting it re-created the false cycle the same
        # review had just removed (measured: 4 spurious `ANSWER CYCLE`
        # blockers on an 18-turn propose run whose turns all ended clean).
        if (str(answer) not in ("(left standing)", "display-only",
                                "(no options)")
                and not str(answer).startswith("(stale passthrough")):
            self.recent.append((str(key), str(summary), str(answer)))
        self._md(f"  - POPUP {key}: {summary} → {answer}")
        self.record("popup", key=key, summary=summary, answer=answer)

    def discount_answer(self, key, summary, answer):
        """Retract an answer from the cycle-guard trail — it did not happen.

        FA-10/FA-74. `popup()` records the signature BEFORE the POST,
        because the digest line must read in order (the answer, then the
        `↳ refused` note under it). When the backend refuses the answer as
        STALE, that attempt never reached the executor: the dialogue is
        re-offered once, and without this the legitimate retry would answer
        the same surface with the same word twice in one chain — which is
        precisely what `drain()`'s guard calls an ANSWER CYCLE. It would
        stop the chain and leave every other blocker standing.

        The LINE stays in the digest (WO slice 5's rule: a wedge must be
        legible). Only the signature is withdrawn.
        """
        sig = (str(key), str(summary), str(answer))
        if sig in self.recent:
            self.recent.remove(sig)

    def note(self, text):
        self._md(f"  - {text}")
        self.record("note", text=text)

    def enemy_phase(self, actions):
        if not actions:
            return
        # The verb lives at row["ai_action"]["action"] (turn_manager.py:964
        # builds it, and _build_visible_enemy_phase only strips new_state).
        # PC15-H tried to fix the "0 attacks" under-read by reading
        # row["action"] — but that key does not exist, so the counter
        # stayed 0 on EVERY run, including the ones that concluded things
        # about how often the AI attacks. Read the real key, keep the old
        # ones as fallbacks.
        attacks = [a for a in actions if "attack" in _verb(a)]
        # FA-87: `salient_line`, not `first_line` — the engine prepends
        # tactical annotations (`[Shield] …`, `[Combat] …`, `[!] …`) and a
        # `'=' * 40` banner to the prose, and those won the slot on every
        # row that carried one.
        lines = [salient_line(a.get("message") or a.get("action")
                              or a.get("action_type"), 120)
                 for a in attacks[:4]]
        summary = f"enemy phase: {len(actions)} actions, {len(attacks)} attacks"
        if lines:
            summary += " — " + " · ".join(lines)
        self._md(f"- {summary}")

        # Aug-16 win-campaign: the digest showed ONLY attack lines, so a
        # province changing hands in the enemy phase was invisible. The
        # single most consequential event of that campaign — the ALLY,
        # Bavaria, taking Vienna and four more Austrian provinces while
        # France destroyed the field army — never appeared in any digest.
        # Surface conquest explicitly; keep it player-visible text only.
        needles = ("captur", "has fallen", "falls to", "taken by", "seized")
        taken = [a for a in actions
                 if any(w in str(a.get("message") or "").lower()
                        for w in needles)]
        for act in taken[:6]:
            # FA-87: the detector greps the WHOLE message and then printed
            # its FIRST line, so a real conquest was captioned with the
            # annotation above it — measured in the archive, `🏴 Austria:
            # ========================================` and `🏴 Austria:
            # [Shield] Massena is at his best with his back to the wall!`.
            self._md(f"  - 🏴 {act.get('nation', '?')}: "
                     f"{matching_line(act.get('message'), needles, 150)}")

        # WO-H2: an enemy-phase attack that resolved combat carries the full
        # battle_report on its own row (the fog filter strips only
        # `new_state`) — the driver counted none of them, so the `battles`
        # counter read 0 for campaigns the world logged a dozen battles in.
        for act in actions:
            if isinstance(act.get("battle_report"), dict):
                self.battle(act["battle_report"])

        verbs = {}
        for act in actions:
            verb = _verb(act) or "?"
            verbs[verb] = verbs.get(verb, 0) + 1
        if verbs:
            self._md("  - verbs: " + ", ".join(
                f"{v}×{n}" for v, n in sorted(verbs.items(),
                                              key=lambda kv: -kv[1])))
        # Full fidelity to the jsonl — the query surface should never be
        # thinner than the markdown.
        #
        # FA-87: it WAS thinner, in the exact way that comment forbids. The
        # message was stored as `first_line(..., 200)`, so the jsonl held the
        # bombardment banner or the tactical annotation and nothing else —
        # and a capture clause that sits later in the same line was cut off.
        # Measured while building this row: a probe scanning the jsonl for
        # capture prose found ONE of the three the markdown had flagged.
        # This is a machine surface; store the message.
        self.record("enemy_phase", count=len(actions), attacks=len(attacks),
                    captures=len(taken), verbs=verbs,
                    actions=[{"nation": a.get("nation"),
                              "action": _verb(a),
                              "marshal": (a.get("ai_action") or {}).get("marshal")
                              if isinstance(a.get("ai_action"), dict) else None,
                              "message": a.get("message")}
                             for a in actions])

    def autonomous_attacks(self, rows):
        """WO-H2: autonomous jealousy attacks ship on the end-turn result's
        `jealousy_attacks` key (turn_manager.py:405 — each row is the full
        executor result, new_state stripped, battle_report nested). The
        driver never read it, so the Pacifist arm's centrepiece — 11
        autonomous attacks, 12 battles — was structurally invisible to its
        own digest."""
        for row in rows or []:
            if not isinstance(row, dict):
                continue
            head = first_line(row.get("message"), 160)
            self._md(f"  - ⚡ AUTONOMOUS: {head or 'jealousy attack'}")
            self.record("autonomous_attack", message=head,
                        success=row.get("success"))
            if isinstance(row.get("battle_report"), dict):
                self.battle(row["battle_report"])

    def envoy_answer(self, row, choice, outcome):
        """WO-H slice 1 item 5: one letter-book row answered (or refused)
        through POST /mailbox/respond — explicit and counted, instead of
        silently lapsing at end turn."""
        self.counters["popups"] += 1
        summary = (f"{row.get('from_nation', '?')}: "
                   f"{row.get('proposal_type_display') or row.get('proposal_type', '?')}")
        self._md(f"  - LETTER {summary} → {choice}{outcome}")
        self.record("envoy_digest_answer", mailbox_id=row.get("mailbox_id"),
                    from_nation=row.get("from_nation"),
                    proposal_type=row.get("proposal_type"),
                    choice=choice, outcome=outcome.strip() or "answered")

    # FA-37: the signed Net components, in the order the ledger states them.
    # `net` alone answers "is France solvent"; it cannot answer WHY, which is
    # the only question an economy evaluation asks. Every archived digest had
    # to be re-derived with a bespoke probe to learn that Contributions fired
    # when Paget stood on Normandy, or that the restless-interior term flipped
    # Net negative. The keys are `GET /ledger`'s own — measured against a live
    # payload, not guessed.
    NET_COMPONENTS = (
        ("income", "income"), ("trade_income", "trade"),
        ("overseas", "overseas"), ("vassal_tribute", "tribute"),
        ("treaty_gold", "treaty"), ("settlement_gold", "settlement"),
        ("upkeep", "upkeep"), ("state_charges", "charges"),
        ("contributions", "contributions"), ("requisitions", "requisitions"),
        ("occupation", "occupation"), ("blockade", "blockade"),
        ("admiralty", "admiralty"), ("infrastructure", "infrastructure"),
        ("dotation_skim", "dotations"), ("rente_cost", "rentes"),
    )
    MAX_RAIL_ROWS = 6

    def ledger_line(self, treasury, net, threat, provinces=None,
                    economy=None):
        bits = []
        if treasury is not None:
            bits.append(f"treasury {treasury}")
        if net is not None:
            bits.append(f"net {net:+}" if isinstance(net, int) else f"net {net}")
        if threat is not None:
            bits.append(f"threat {threat}")
        # The conquest scoreboard. `territories` is the player's OWN
        # region list, so this is fog-free and honest. Without it a
        # campaign can destroy an empire's whole army and never notice
        # that its own map did not grow (Aug-16: France held 29 provinces
        # on turn 1 and 29 on turn 11, having won every battle).
        if provinces is not None:
            delta = ("" if self._last_provinces is None
                     else f" ({provinces - self._last_provinces:+d})")
            bits.append(f"provinces {provinces}{delta}")
            self._last_provinces = provinces
        if bits:
            self._md("- LEDGER " + " · ".join(bits))
            self.record("ledger", treasury=treasury, net=net, threat=threat,
                        provinces=provinces)
        # FA-37. Only the components that MOVED — a run's economy story is
        # which term turned on, and a line of eleven zeroes hides it.
        if isinstance(economy, dict):
            moved = {label: int(economy[key])
                     for key, label in self.NET_COMPONENTS
                     if isinstance(economy.get(key), (int, float))
                     and int(economy[key])}
            if moved:
                self._md("  - NET " + " · ".join(
                    f"{label} {value}" for label, value in moved.items()))
            self.record("economy", **moved)

    def dispatch(self, text, events=None, turn_events=None):
        head = first_line(text, 200)
        if head:
            self._md(f"- DISPATCH: {head}")
            self.record("dispatch", headline=head)
        # FA-37: the DIPLOMATIC EVENTS rail. Defections, transfers,
        # rebellions, eliminations, war declarations and every naval and
        # AI-Intent beat land here and nowhere else, so the archived
        # audit-ambient40 digest holds 40 turns with no mention of France's
        # three vassals although all three were lost.
        #
        # HIGH only. The six LOW types are the AI-6 routine intent chatter
        # the cap already governs, and MEDIUM is the tide rather than the
        # event; every family this row was filed for — vassal defected /
        # transferred / rebelled, nation eliminated, treaty broken, war
        # declared — is graded HIGH in `dispatch._DIPLOMATIC_EVENT_PRIORITY`,
        # which a drift pin holds there.
        rows = [e for e in (events or [])
                if isinstance(e, dict) and str(e.get("priority")) == "HIGH"]
        for event in rows[:self.MAX_RAIL_ROWS]:
            self._md(f"  - RAIL {event.get('type', '?')}: "
                     f"{first_line(event.get('text'), 150)}")
            self.record("rail", dtype=event.get("type"), text=event.get("text"))
        if len(rows) > self.MAX_RAIL_ROWS:
            self._md(f"  - RAIL +{len(rows) - self.MAX_RAIL_ROWS} more")
        if turn_events:
            self._md(f"  - TURN EVENTS {len(turn_events)}")
            self.record("turn_events", count=len(turn_events))

    def unknown_blocker(self, key, payload):
        self.unknown_blockers.append(key)
        self._md(f"  - ⚠ UNKNOWN BLOCKER `{key}` — answered nothing; "
                 f"payload logged in jsonl")
        self.record("unknown_blocker", key=key, payload=payload)

    def finish(self, status):
        self.meta["status"] = status
        self._md(f"\n---\nfinished: **{status}** · commands "
                 f"{self.counters['commands']} · popups {self.counters['popups']}"
                 f" · battles {self.counters['battles']}")
        self._write_meta()


# ═══════════════════════════════════════════════════════════════════════
# Popup / dialogue answering
# ═══════════════════════════════════════════════════════════════════════

# WO-H1: the ally-entry review's options carry `action` keys and no `id` —
# `_option_id` returned None for every one, `find()` matched nothing, and the
# literal-"confirm" fallback answered a word the endpoint's keyword list does
# not contain. The World Burns arm ran FIFTEEN complete declare-war ceremonies
# and declared war on ZERO nations, every one logged as a success. Read every
# key an option legitimately answers by — but NEVER `label`: labels are
# display strings, and matching them would couple the driver to copy.
_OPTION_ID_KEYS = ("id", "choice", "keyword", "action", "command", "value")


def _option_id(option):
    if isinstance(option, dict):
        for key in _OPTION_ID_KEYS:
            value = option.get(key)
            if value is not None and value != "":
                return value
        return None
    return option


def _enabled(option):
    if isinstance(option, dict):
        return option.get("enabled", True) is not False
    return True


def _summ(payload, *names):
    if not isinstance(payload, dict):
        return str(payload)
    vals = [str(payload.get(n)) for n in names if payload.get(n)]
    return ", ".join(vals) if vals else "(no summary fields)"


def _as_dict(value):
    """Popup fields arrive as a dict OR as a bare flag (True) with the
    detail on sibling keys — normalize for the answer arms."""
    return value if isinstance(value, dict) else {}


def _verb(action_row):
    """The AI verb for one enemy-phase row, lower-cased ('' if absent)."""
    if not isinstance(action_row, dict):
        return ""
    inner = action_row.get("ai_action")
    if isinstance(inner, dict) and inner.get("action"):
        return str(inner["action"]).lower()
    return str(action_row.get("action")
               or action_row.get("action_type") or "").lower()


def _interrupt_reports(response):
    """EVERY strategic report awaiting player input, in row order.

    FA slice 3 review round (R2-F6): FA-68 made the backend ask every
    deferred marshal and the Godot client queues every row — but this
    driver answered one question per response, so the second marshal
    stood idle a turn and was asked a turn late in every sweep digest."""
    if not isinstance(response, dict):
        return []
    return [report for report in response.get("strategic_reports") or []
            if isinstance(report, dict) and report.get("requires_input")]


def _interrupt_report(response):
    """The first strategic report awaiting player input (NPC-16).

    An end-turn interrupt never reaches response["pending_interrupt"];
    the client finds it here and so must the driver. Returns {} when
    there is none, so callers can treat it as a falsy payload."""
    reports = _interrupt_reports(response)
    return reports[0] if reports else {}


class Answerer:
    """Scans a response for blocking surfaces, answers them by policy,
    and digests everything. Returns the FOLLOW-UP responses it produced
    (each of which is scanned in turn by the caller, up to a cap)."""

    def __init__(self, transport, digest, policy, strict):
        self.t = transport
        self.d = digest
        self.policy = policy
        self.strict = strict
        # W6-0 dialogue identities already answered during the CURRENT
        # answer chain (reset by drain()). See begin_post().
        self._answered_dialogue_ids = set()
        # Choices the backend REFUSED, per dialogue identity. Never reset:
        # a word the executor rejected is not worth re-sending on any later
        # turn either. See the refusal arm in scan(). (WO slice 5 review.)
        #
        # FA-10: an ORDERING refusal never lands here. `stale_dialogue` says
        # only that a different dialogue was on top at that instant — the
        # executor did not judge the word, and treating it as a judgement
        # blacklisted the only sane answer to four major-court offers for
        # the whole run.
        self._refused_choices = {}
        # FA-74: how often a dialogue id has been refused as STALE in this
        # chain. Bounded so a genuinely wedged surface is left standing with
        # its reason instead of spinning. Reset by begin_post().
        self._stale_refusals = {}

    def begin_post(self):
        """Start a fresh answer chain (called by drain()).

        NOTE the scope is the CHAIN, not one POST: drain() calls this once
        and then walks a queue of follow-up responses produced by many
        POSTs. The name is kept because three test doubles implement it.

        Why (found by WO slice 5's own `--diplomacy propose` arm): every
        POST handler rebuilds the popup passthroughs, so a response
        generated BEFORE an answer lands re-carries the dialogue that
        answer has since popped. When one command raises two surfaces —
        a marshal petition AND a proposal confirm, which is ordinary on
        a turn France sues for peace — the petition's reply still shows
        the pending confirm, and the driver answered dialogue #27 twice:
        once for real, once against whatever the stack had promoted in
        the meantime (the CA9 typed-router shape, from the harness side).
        The cycle guard then STOPPED THE CHAIN, leaving real blockers
        standing. Nine of eighteen turns under `propose`; zero under
        every other policy, which is why it had never been seen.

        `dialogue_id` is a monotonic per-dialogue identity stamped on
        every push (`dialogue_manager._assign_dialogue_id`), so this
        skips only a surface that is provably the same instance.
        """
        self._answered_dialogue_ids = set()
        self._stale_refusals = {}

    def scan(self, response):
        followups = []

        for key in DISPLAY_ONLY_KEYS:
            payload = response.get(key)
            if payload:
                self.d.popup(key, _summ(payload, "title", "message", "nation",
                                        "headline"), "display-only")

        if response.get("battle_report"):
            self.d.battle(response["battle_report"])

        # WO-H2 (review round, Aug 21): battles AUTO-resolved during
        # end-turn strategic processing DISCARD their battle_report from
        # the report row (WO-33 — the aggressive auto-attack and the
        # pursue-completion keep only a message with action=="combat"; the
        # HOLD sally keeps its report under the different key
        # `battle_details`). Count what is recoverable, and say when the
        # report itself was discarded.
        for report in response.get("strategic_reports") or []:
            if not isinstance(report, dict) or report.get("requires_input"):
                continue
            if isinstance(report.get("battle_details"), dict):
                self.d.battle(report["battle_details"])
            elif str(report.get("action") or "") == "combat":
                self.d.battle({"headline": (
                    first_line(report.get("message"), 150)
                    or "auto-resolved battle (report discarded — WO-33)")})

        # 1. Marshal objection ------------------------------------------------
        if response.get("pending_objection"):
            payload = _as_dict(response["pending_objection"])
            if not payload:
                payload = _as_dict(response.get("objection"))
            choice = self.policy["objection"]
            self.d.popup("objection",
                         _summ(payload or response.get("message"),
                               "marshal", "objection_text", "message"),
                         choice)
            followups.append(self.t.post("/respond_to_objection",
                                         {"choice": choice}))

        # 2. Strategic interrupt ----------------------------------------------
        # NPC-16 (harness half): an interrupt raised during END-TURN
        # processing is never promoted to response["pending_interrupt"] —
        # it rides ONLY strategic_reports[i].requires_input, which is
        # where the Godot client reads it (main.gd:4218). A driver that
        # scanned only the top-level key never saw it: step 0a then
        # returned "awaiting_response" forever, the marshal froze, and the
        # turn loop froze behind him (measured Aug 16: current_turn stuck
        # at 7, ONE interrupt answered across four campaign arms). Read
        # BOTH sources, exactly like the client does.
        elif response.get("pending_interrupt") or _interrupt_report(response):
            # FA slice 3 review round (R2-F6): answer EVERY marshal awaiting
            # input on this response, not only the promoted first one — the
            # /strategic_response replies carry no strategic_reports, so a
            # question not answered here waits a whole turn.
            payloads = []
            seen = set()
            promoted = _as_dict(response.get("pending_interrupt"))
            for payload in [promoted] + _interrupt_reports(response):
                if not payload:
                    continue
                key = str(payload.get("marshal", ""))
                if key in seen:
                    continue
                seen.add(key)
                payloads.append(payload)
            for payload in payloads:
                options = payload.get("options") or payload.get("choices") or []
                choice = None
                for opt in options:
                    if _enabled(opt):
                        choice = _option_id(opt)
                        break
                choice = choice or "continue"
                self.d.popup("strategic_interrupt",
                             _summ(payload, "marshal", "interrupt_type", "message"),
                             choice)
                followups.append(self.t.post("/strategic_response", {
                    "marshal_name": payload.get("marshal", ""),
                    # handle_response dispatches on the STORED interrupt_type,
                    # so this field is advisory — send the real one anyway.
                    "response_type": (payload.get("interrupt_type")
                                      or payload.get("response_type")
                                      or payload.get("type", "")),
                    "choice": str(choice),
                }))

        # 3. Capture / estate choice ------------------------------------------
        if response.get("pending_capture_choice"):
            # WO-H3: on the /command path `pending_capture_choice` arrives as
            # a bare True with the detail on the SIBLING `capture_data`
            # (stage / dialogue_id / region — main.py stamps both keys at
            # every producer). Reading only the flag lost the stage, so the
            # ESTATE stage was answered with the plunder/secure token — which
            # the executor refuses WITHOUT clearing, wedging the whole rest
            # of the campaign behind "You must decide the fate of…".
            payload = (_as_dict(response["pending_capture_choice"])
                       or _as_dict(response.get("capture_data")))
            stage = payload.get("stage", "capture")
            # WO slice 5 review: an identity guard was drafted here and then
            # REMOVED — the claimed mechanism ("the keys are stamped on every
            # response while the world attribute is set") reads `main.py:4054`,
            # which is `/load`'s filler; the command paths carry these keys off
            # the executor RESULT. `/capture_choice` also has its own
            # `dialogue_id` + `stale_dialogue` arm, so a duplicate is refused,
            # not misapplied. Unproven mechanism, no guard.
            choice = (self.policy["estate"] if stage == "estate"
                      else self.policy["capture"])
            self.d.popup(f"capture_choice[{stage}]",
                         _summ(payload, "region", "capturer", "estate_holder"),
                         choice)
            body = {"choice": choice}
            # Carry the W6-0 identity so the stale-answer guard arms.
            if payload.get("dialogue_id") is not None:
                body["dialogue_id"] = payload["dialogue_id"]
            followups.append(self.t.post("/capture_choice", body))

        # 3b. Clarification question (CR-2 / naval confirm / pursuit ask) ------
        # WO-H slice 1 item 4: the driver never read response["state"], so it
        # was blind to EVERY awaiting_clarification question — the Grand
        # Diversion confirm, "Which marshal, Sire?", the pursuit ask. Answer
        # by stated policy: the typed index "1" resolves server-side
        # (interpret_clarification_answer) to the FIRST ACTIONABLE option's
        # own command string — the driver never guesses at copy.
        if response.get("state") == "awaiting_clarification":
            options = response.get("options") or []
            actionable = [o for o in options if isinstance(o, dict)
                          and (o.get("command") or o.get("target"))]
            summary = _summ(response, "marshal", "clarification_kind",
                            "message")
            if not actionable or response.get("clarification_registered") is False:
                # No option the server's own interpreter can resolve (or the
                # question never reached the dialogue manager, so a typed
                # index would parse as a command) — the question stands, and
                # the next command's unconditional pop will discard it: the
                # recorded H-13 seam, not the driver's to fix. Say so rather
                # than burning a blind token.
                self.d.popup("clarification", summary, "(left standing)")
            elif self.policy["clarification"] == "cancel":
                self.d.popup("clarification", summary, "cancel")
                followups.append(self.t.post("/command",
                                             {"command": "cancel"}))
            else:
                label = str(actionable[0].get("label")
                            or actionable[0].get("command")
                            or actionable[0].get("target") or "")
                self.d.popup("clarification", summary,
                             f"1 (first option: {first_line(label, 60)})")
                followups.append(self.t.post("/command", {"command": "1"}))

        # 4. Marshal petition --------------------------------------------------
        if response.get("marshal_petition"):
            payload = _as_dict(response["marshal_petition"])
            options = payload.get("options") or []
            choice = None
            for opt in options:
                if _enabled(opt):
                    choice = _option_id(opt)
                    break
            if choice is None and options:
                choice = _option_id(options[0])
            self.d.popup("marshal_petition",
                         _summ(payload, "marshal", "kind", "title"),
                         choice or "(no options)")
            if choice is not None:
                followups.append(self.t.post("/marshal_petition_response",
                                             {"choice": str(choice)}))

        # 5. Talleyrand pre-proposal objection ---------------------------------
        if response.get("diplomatic_objection"):
            payload = _as_dict(response["diplomatic_objection"])
            choice = self.policy["diplomatic_objection"]
            self.d.popup("diplomatic_objection",
                         _summ(payload, "action", "target_nation", "message"),
                         choice)
            followups.append(self.t.post("/respond_to_diplomatic_objection", {
                "choice": choice,
                "action": payload.get("action"),
                "target_nation": payload.get("target_nation"),
            }))

        # 6. Glorious charge ----------------------------------------------------
        if response.get("glorious_charge") or response.get("pending_glorious_charge"):
            payload = _as_dict(response.get("glorious_charge")
                               or response.get("pending_glorious_charge"))
            choice = self.policy["glorious_charge"]
            self.d.popup("glorious_charge", _summ(payload, "marshal", "target"),
                         choice)
            followups.append(self.t.post("/respond_to_glorious_charge",
                                         {"choice": choice}))

        # 6b. Redemption audience (found by the WO-41 landing, Sept 1 2026) ----
        # The `"redemption"` policy key had existed since Aug 15 and was READ
        # BY NOTHING: no unattended arm could answer
        # `awaiting_redemption_choice`, so the whole trust-collapse arc was a
        # blind spot of every digest before this date. Same shape as the
        # glorious-charge arm; the choice is logged like every other answer.
        if response.get("redemption_event"):
            payload = _as_dict(response.get("redemption_event"))
            choice = self.policy.get("redemption", "dismiss")
            self.d.popup("redemption", _summ(payload, "marshal", "trust"),
                         choice)
            followups.append(self.t.post("/respond_to_redemption",
                                         {"choice": choice}))

        # 7. Diplomatic dialogue (incoming proposals, settlement offers,
        #    ultimatums, envoys — anything answerable on the dialogue stack).
        dialogue = (response.get("diplomatic_dialogue")
                    or response.get("incoming_proposal")
                    or response.get("incoming_settlement_offer"))
        if dialogue and isinstance(dialogue, dict):
            did = dialogue.get("dialogue_id")
            summary = _summ(dialogue, "type", "nation", "from_nation",
                            "proposal_type")
            if did is not None and did in self._answered_dialogue_ids:
                # Same instance, already answered in this chain — a stale
                # passthrough, not a new question. See begin_post().
                #
                # WO slice 5 review: SAY SO. The first cut set `dialogue =
                # None` and fell through, so thirteen answer-surface events
                # vanished from an 18-turn digest — the reported cycle became
                # a silent one, in a harness whose whole point is that a
                # wedge is legible.
                self.d.popup("diplomatic_dialogue", summary,
                             f"(stale passthrough — #{did} already answered "
                             f"this chain)")
                dialogue = None
            elif (did is not None
                  and self._stale_refusals.get(did, 0) >= MAX_STALE_ATTEMPTS):
                # FA-74: the retry bound. One re-offer per chain; a surface
                # the backend calls stale twice is genuinely wedged, and the
                # honest digest line is that it was left standing AND WHY —
                # not a silent skip, and not an ANSWER CYCLE the guard would
                # otherwise raise on the third attempt.
                self.d.popup("diplomatic_dialogue", summary,
                             f"(left standing — #{did} refused as stale "
                             f"{self._stale_refusals[did]}× this chain)")
                dialogue = None
        if dialogue and isinstance(dialogue, dict):
            choice = self._dialogue_choice(dialogue)
            # The cycle guard's signature carries the dialogue identity, so
            # two DIFFERENT surfaces of the same type answered the same way
            # in one chain no longer read as a loop (WO slice 5 review: the
            # legitimate five-stage settlement ceremony ends in two distinct
            # `proposal_confirm`s and tripped it every long propose run).
            label = summary + (f" #{did}" if did is not None else "")
            self.d.popup("diplomatic_dialogue", label,
                         choice or "(left standing)")
            if choice is not None:
                body = {"choice": choice}
                if did is not None:
                    body["dialogue_id"] = did
                reply = self.t.post("/respond_to_diplomatic_dialogue", body)
                # ══════════════════════════════════════════════════════
                # FA-10 + FA-74: A STALE REFUSAL IS NOT AN ANSWER.
                #
                # The backend's W6-0 guard returns success False with
                # `stale_dialogue` purely because a DIFFERENT dialogue was
                # on top at that instant ("Sire, another matter has arrived
                # since") — it is the guard WORKING, and it says nothing
                # about the word we sent. The driver was recording it in
                # three separate memories as though it did:
                #
                #   `_answered_dialogue_ids` (chain-scoped) — so the same
                #       offer, promoted back in the same chain, logged
                #       "(stale passthrough — already answered)" [FA-74];
                #   `_refused_choices` (RUN-scoped, never reset) — so the
                #       only sane answer to that offer was blacklisted for
                #       the rest of the campaign, and a bare-shape popup
                #       with no options list had nothing else to try, so it
                #       was "(left standing)" forever [FA-10];
                #   the digest's cycle signature — which is why the naive
                #       fix cannot stop at the first two: a legitimate
                #       retry answers the same dialogue with the same word
                #       twice in one chain, which is exactly what
                #       `drain()`'s guard calls an ANSWER CYCLE. It would
                #       have stopped the chain and left every OTHER
                #       blocker standing — a worse failure than the one
                #       being fixed.
                #
                # Measured cost of the old behaviour: four major-court
                # offers in the archived 24-turn flagship (Russia and
                # Britain armistices, Prussia open borders twice) neither
                # accepted nor declined, and an `--diplomacy accept` run
                # answering a settlement with "request revision" because
                # `accept` had been banned.
                #
                # The reply CARRIES the dialogue actually on top, so the
                # chain answers that one next and the original comes back
                # under its own identity. One retry per chain is the bound
                # — a surface that goes stale twice is genuinely wedged and
                # is left standing WITH ITS REASON, which is the honest
                # digest line.
                # ══════════════════════════════════════════════════════
                stale = bool(reply.get("stale_dialogue"))
                if did is not None:
                    if stale:
                        self._stale_refusals[did] = (
                            self._stale_refusals.get(did, 0) + 1)
                        self.d.discount_answer(
                            "diplomatic_dialogue", label, choice)
                    else:
                        self._answered_dialogue_ids.add(did)
                # WO slice 5 review: the digest rendered a REFUSED answer
                # exactly like a signed one. Measured on the archived run:
                # of the seven bare-shape popups the new arm answered, FIVE
                # were refused (`stale_dialogue` — a queued popup answered
                # against whatever dialogue was actually active) and two
                # landed, and the digest said the same thing about all
                # seven. So "0 (left standing)" was never evidence the
                # offers were answered; they only stopped saying so. The
                # letter-book has done this since IGR-F — the same shape.
                if reply.get("success") is False:
                    self.d.note(
                        f"    ↳ refused: "
                        f"{first_line(reply.get('message'), 110)}")
                # WO slice 5 review: a REFUSED answer must never be repeated.
                # Measured: `--diplomacy propose` spends 3 DP a turn, the
                # settlement_confirm's first option (`seek_bilateral_peace`)
                # then costs DP France no longer has, the executor refuses
                # WITHOUT popping, and the driver re-sent the same word every
                # turn until `end turn` was refused forever — `blocked` on 3
                # of 7 seeds. Remembering the refusal turns the DP shortage
                # into the evidence the arm was built to produce.
                #
                # FA-10: an ORDERING refusal is exempt — the executor never
                # judged the word, so there is nothing to remember.
                if reply.get("success") is False and not stale:
                    self._refused_choices.setdefault(
                        self._refusal_key(dialogue), set()).add(str(choice))
                followups.append(reply)

        return followups

    def answer_envoy_digest(self, digest_payload):
        """WO-H slice 1 item 5: answer the IGR-F letter-book by policy.

        The letter-book rides GET /mailbox (the /command copy is nulled on
        every enemy-phase response, so an ambient run never sees it there).
        Called once per turn BEFORE the turn's commands — unanswered letters
        lapse when the turn ends. Default `decline`, explicit and counted;
        `--diplomacy accept` accepts them. NOTE an explicit decline is not
        a lapse — see the POLICY_DEFAULTS comment for the mechanical delta
        (refusal record + 3-turn court cooldown vs none + 2-turn).
        Returns the reply responses for the caller to drain."""
        if not isinstance(digest_payload, dict):
            return []
        choice = ("accept"
                  if self.policy["diplomacy"] in ACCEPTING_DIPLOMACY_MODES
                  else "decline")
        replies = []
        for row in digest_payload.get("items") or []:
            if not isinstance(row, dict) or row.get("mailbox_id") is None:
                continue
            reply = self.t.post("/mailbox/respond",
                                {"mailbox_id": int(row["mailbox_id"]),
                                 "choice": choice})
            answered = reply.get("digest_row_answered") is not None
            outcome = ("" if answered else
                       f" (refused: {first_line(reply.get('message'), 90)})")
            self.d.envoy_answer(row, choice, outcome)
            replies.append(reply)
        return replies

    @staticmethod
    def _refusal_key(dialogue):
        """Identity for the refused-choice memory.

        `dialogue_id` when the surface carries one; otherwise the shape —
        because the surfaces that lack an id are exactly the ones the W6-0
        identity binding cannot reach either.
        """
        did = dialogue.get("dialogue_id")
        if did is not None:
            return ("id", did)
        return ("shape", str(dialogue.get("type") or ""),
                str(dialogue.get("target_nation")
                    or dialogue.get("from_nation") or ""),
                tuple(str(_option_id(o) or "")
                      for o in (dialogue.get("options")
                                or dialogue.get("choices") or [])))

    def _dialogue_choice(self, dialogue):
        """Pick a dialogue answer. Order: the type table (types whose
        right answer the driver knows even without an options list), then
        the diplomacy policy over the dialogue's OWN option keywords.

        A choice the backend already REFUSED for this dialogue is never
        re-offered — the next option is tried instead, and when the list is
        exhausted the surface is left standing and SAID so.
        """
        refused = self._refused_choices.get(self._refusal_key(dialogue))
        picked = self._pick_dialogue_choice(dialogue)
        if not refused or picked is None or str(picked) not in refused:
            return picked
        for option in (dialogue.get("options")
                       or dialogue.get("choices") or []):
            candidate = _option_id(option)
            if candidate is not None and str(candidate) not in refused:
                return candidate
        return None

    def _pick_dialogue_choice(self, dialogue):
        dtype = str(dialogue.get("type") or "")
        options = dialogue.get("options") or dialogue.get("choices") or []
        keywords = [str(_option_id(o) or "").lower() for o in options]

        # WO slice 5 REVIEW (August 22, 2026) — the ultimatum discriminator.
        # An `incoming_ultimatum` recovers through the SAME transport as a
        # proposal: `main.py`'s incoming_proposal safety valve and the popup
        # queue both render it with `mailbox_payloads.
        # build_pending_envoy_popup_from_terms`, which stamps neither a
        # `type` key nor an options list. The bare-shape arm below therefore
        # could not tell the two apart, and MEASURED end to end: under any
        # accepting policy the driver answered "accept", the router mapped it
        # to `accept_ai_ultimatum`, and France YIELDED — Hanover ceded to
        # Prussia, 300g/turn tribute, 5,000 conscripts — silently overriding
        # the `ultimatum` policy the run's own meta.json records as `defy`.
        # `is_ultimatum` is the producer's own field
        # (`ai_diplomacy._build_ai_ultimatum_dialogue`) and `ultimatum_demand`
        # is its terms type; either restores the dtype the table owns.
        if not dtype and (dialogue.get("is_ultimatum")
                          or str(dialogue.get("proposal_type", "")
                                 ).startswith("ultimatum")):
            dtype = "incoming_ultimatum"

        # WO slice 5. The AI's own peace offer arrives as the incoming-
        # proposal POPUP payload (`mailbox_payloads.
        # build_pending_envoy_popup_from_terms` — the review corrected a
        # fabricated name here): a rendering of a real dialogue that carries
        # its `dialogue_id` but neither the `type` key nor an options list.
        # FOUR dialogue types render through it — `incoming_proposal`,
        # `counter_offer`, `counter_offer_response` and `incoming_ultimatum`
        # — which is precisely why the ultimatum arm above exists. The
        # driver's type table and both keyword searches missed the shape and
        # it was logged `(left standing)` — measured seven times in eighteen
        # turns the first time an arm ever made France sue for peace,
        # including Russia's own answer to the overture. An arm that asks for
        # peace and then cannot sign it measures nothing.
        #
        # Answered exactly as the client answers it: a bare keyword plus
        # the payload's dialogue_id (`main.gd _on_incoming_proposal_
        # choice`), the words taken from the router's own table
        # (`dialogue_routing.DIALOGUE_ACTION_KEYWORDS`: accept ->
        # accept_ai_proposal, reject -> reject_ai_proposal).
        #
        # ⚠ Digest delta, same shape as the letter-book's: a run that used
        # to LAPSE these now refuses them explicitly.
        if (not dtype and not options
                and dialogue.get("from_nation")
                and dialogue.get("proposal_type")):
            return ("accept"
                    if self.policy["diplomacy"] in ACCEPTING_DIPLOMACY_MODES
                    else "reject")

        def find(*needles):
            for i, kw in enumerate(keywords):
                for needle in needles:
                    if needle in kw:
                        return _option_id(options[i])
            return None

        if dtype in DIALOGUE_TYPE_ANSWERS:
            policy_key = DIALOGUE_TYPE_ANSWERS[dtype]
            if policy_key == "confirm":
                return find("confirm", "yes", "proceed", "send") or "confirm"
            # PC15-3/PC15-H: the pair-substitute chooser. `keep` is a
            # documented NO-OP that restores the prior settlement_confirm
            # — so under an ACCEPTING policy it cycles forever against
            # that dialogue's own option 1 (Aug-16 win campaign). An
            # accepting run commits to the substitute it just chose;
            # a declining run keeps the joint draft.
            if policy_key == "keep":
                # WO slice 5 review: the constant, not a third hand-written
                # copy of it — `first` is an accepting mode, and taking the
                # documented NO-OP `keep` under it restages the substitute
                # forever.
                if self.policy["diplomacy"] in ACCEPTING_DIPLOMACY_MODES:
                    return (find("confirm_pair", "confirm", "substitute")
                            or "confirm_pair_substitute")
                return find("keep") or "keep"
            if policy_key in ("war_purpose", "ultimatum"):
                answer = self.policy[policy_key]
                if answer == "defy":
                    return find("defy", "refuse") or "defy"
                return answer

        mode = self.policy["diplomacy"]
        if mode in ("accept", "propose"):
            # NOT the constant: `first` keeps its own "take options[0]"
            # meaning here, which is the whole point of the mode.
            picked = find("accept", "agree", "yes", "sign")
        elif mode == "first":
            picked = _option_id(options[0]) if options else None
        else:  # decline
            picked = find("decline", "reject", "refuse", "no")
        if picked is None and options:
            picked = _option_id(options[-1] if mode == "decline" else options[0])
        if picked is None and dtype in DIALOGUE_TYPE_ANSWERS:
            # Known-answerable family with no options list: the endpoint
            # accepts a keyword — "decline" is the family's safe word.
            picked = "decline" if self.policy["diplomacy"] == "decline" else "1"
        return picked


# ═══════════════════════════════════════════════════════════════════════
# The campaign loop
# ═══════════════════════════════════════════════════════════════════════

def _flatten_enemy_phase(enemy_phase):
    """main.py ships {"nations": {name: {"actions": [...]}}, "total_actions": N}
    (fog-filtered). Flatten to one action list with the nation stamped."""
    if not isinstance(enemy_phase, dict):
        return []
    flat = []
    for nation, nation_data in (enemy_phase.get("nations") or {}).items():
        for action in (nation_data or {}).get("actions", []) or []:
            if isinstance(action, dict):
                flat.append({"nation": nation} | action)
    return flat


def peace_overture(status_payload, turn_index):
    """The `--diplomacy propose` arm (WO slice 5): ONE bilateral peace
    command per turn, or None.

    Why it exists: across every WO campaign the driver's diplomacy policy
    was `decline` on incoming and SILENT outbound, so the bilateral-peace
    path was never pressed once — and a France|Russia war that both courts
    would have signed out of sat open for thirty turns with no way to tell
    whether the engine or the harness was at fault.

    Two roads, chosen off the game's OWN honest-availability field rather
    than a copy of its rules: if this court leads a war whose
    `request_terms_state` is `available`, ask them to name terms (the
    surface the war room's counsel points at); otherwise propose peace
    directly. Both phrasings are golden-corpus rows.

    Round-robin by turn index over the sorted at-war courts, so a long run
    asks everyone and DP shortage / cooldowns / refusals all land in the
    digest as evidence instead of being engineered around. (That claim was
    FALSE as first shipped — a DP shortage stopped the run on 3 of 7 seeds
    rather than landing as evidence, because the driver re-sent a choice the
    executor had already refused. The refused-choice memory in
    `Answerer._dialogue_choice` is what makes it true; WO slice 5 review.) The driver keeps
    typed diplomacy deliberately (spec §6 never-do 12): the slice-7 Cabinet
    redirect lives in main.gd, client-side, and POST /command is the
    surface under test.
    """
    wars = ((status_payload or {}).get("active_wars") or {}).get("wars") or []
    courts = {}
    for row in wars:
        if str(row.get("status", "")) != "war":
            continue
        leader = str(row.get("opponent", "") or "")
        terms_ok = str((row.get("request_terms_state") or {}).get(
            "state", "")) == "available"
        for court in (row.get("opponents") or [leader]):
            if not court:
                continue
            courts.setdefault(str(court),
                              terms_ok and str(court) == leader)
    if not courts:
        return None
    names = sorted(courts)
    court = names[(int(turn_index) - 1) % len(names)]
    if courts[court]:
        return f"request terms from {court}"
    return f"propose peace with {court}"


def drain(transport, digest, answerer, response, strict):
    """Digest a response and answer its blockers, chaining follow-ups.

    Cycle guard (Aug-16 win campaign): two surfaces can legally answer
    each other forever. `settlement_confirm` option 1 stages a bilateral
    PAIR SUBSTITUTE; the chooser's `keep_joint_settlement` is documented
    to restore the prior dialogue — so "1" then "keep" returns exactly
    where it started. Neither is a game defect, but the pair spun 97
    popups and reported the campaign `blocked`, which reads like an
    engine fault and is not one. Answering the SAME surface with the
    SAME choice twice in one post means the policy cannot make progress:
    stop, and say so in the words of what actually happened."""
    seen = 0
    queue = [response]
    digest.recent = []
    answerer.begin_post()
    while queue and seen < MAX_ANSWERS_PER_POST:
        current = queue.pop(0)
        followups = answerer.scan(current)
        seen += len(followups)
        queue.extend(followups)

        counts = {}
        for sig in digest.recent:
            counts[sig] = counts.get(sig, 0) + 1
        looping = [s for s, n in counts.items() if n >= 2]
        if looping:
            key, summary, choice = looping[0]
            digest.note(f"⚠ ANSWER CYCLE — `{key}` ({summary}) answered "
                        f"`{choice}` {counts[looping[0]]}× in one post; the "
                        f"policy cannot resolve this surface. Stopping the "
                        f"chain.")
            digest.unknown_blockers.append(
                {"key": key, "summary": summary, "choice": choice,
                 "reason": "answer-cycle"})
            if strict:
                raise RuntimeError(f"answer cycle on {key} under --strict")
            return

    if queue and seen >= MAX_ANSWERS_PER_POST:
        digest.note(f"⚠ answer chain capped at {MAX_ANSWERS_PER_POST} "
                    f"for one post — see jsonl")
        if strict:
            raise RuntimeError("answer chain cap hit under --strict")


def run(args):
    script = {}
    if args.script:
        script = json.loads(Path(args.script).read_text(encoding="utf-8"))
    # Precedence (WO-H slice 1, learned the expensive way): an EXPLICIT CLI
    # flag beats the script's own key, which beats the built-in default. The
    # old rule — script always wins — silently ignored `--seed` (making a
    # seed sweep over committed scripts impossible) and redirected `--name`
    # into the script's canonical run dir, where `--fresh` then DELETED the
    # original evidence digest. name/seed/llm default to None in argparse so
    # "explicitly passed" is distinguishable from "left at default".
    args.name = args.name or script.get("name") or "run"
    args.seed = args.seed or script.get("seed") or "historical"
    args.llm = args.llm or script.get("llm") or "mock"
    # FA-40: a script that only makes sense on one scenario must be able to
    # SAY so. `scenario` was CLI-only, so `tutorial_lesson.json` could be run
    # against the 1805 campaign — silently, and the archive could not show
    # which board produced it. Same precedence as name/seed/llm: the flag
    # wins, the script fills in.
    args.scenario = args.scenario or script.get("scenario") or ""

    out_dir = Path(args.out) / args.name
    if out_dir.exists() and args.fresh:
        shutil.rmtree(out_dir)
    (out_dir / "saves").mkdir(parents=True, exist_ok=True)

    policy = POLICY_DEFAULTS | (script.get("policy") or {})
    if args.objection:
        policy["objection"] = args.objection
    if args.diplomacy:
        policy["diplomacy"] = args.diplomacy

    if args.http:
        transport = make_http_transport(args)
    else:
        transport = make_inprocess_transport(args, out_dir)

    # WO-H slice 1 item 6/7: the RNG record — meta.json states whether this
    # digest is a measurement or an anecdote, and exactly how the dice were
    # pinned. Mode B cannot be made deterministic from the driver (separate
    # server process); a live-parser run varies even with the RNG pinned.
    if args.http:
        rng_meta = {
            "deterministic": False,
            "scheme": ("NONDETERMINISTIC — Mode B (--http): the server "
                       "process's RNG is unreachable from the driver"),
        }
    else:
        rng_meta = {"deterministic": args.llm == "mock", "scheme": RNG_SCHEME}
        if args.llm != "mock":
            rng_meta["llm_note"] = ("NONDETERMINISTIC — live parser "
                                    "(--llm anthropic): parses vary run to "
                                    "run even with the module RNG pinned")
    rng_meta["pythonhashseed"] = os.environ.get("PYTHONHASHSEED", "(unset)")

    digest = Digest(out_dir, {
        "name": args.name, "seed": args.seed, "llm": args.llm,
        "transport": transport.label, "policy": policy,
        "turns_requested": args.turns, "started": time.strftime("%Y-%m-%d %H:%M"),
        "from_save": args.from_save or "",
        "rng": rng_meta,
    })
    answerer = Answerer(transport, digest, policy, args.strict)

    # Boot ------------------------------------------------------------------
    if not args.http:
        seed_module_rng(args.seed, 0)
    if args.from_save:
        fixture = Path(args.from_save)
        target = out_dir / "saves" / fixture.name
        shutil.copy2(fixture, target)
        boot = transport.post("/load", {"filename": fixture.name})
        digest.note(f"loaded save `{fixture.name}` → "
                    f"{first_line(boot.get('message'))}")
    else:
        boot = transport.post("/new_game", {"scenario": args.scenario})
        digest.note(f"new game → {first_line(boot.get('message'))}")
    if not boot.get("success", True):
        digest.finish("boot-failed")
        print(f"[driver] boot failed: {boot.get('message')}", file=sys.stderr)
        return 2
    drain(transport, digest, answerer, boot, args.strict)

    save_at = {int(x) for x in args.save_at.split(",") if x.strip()} \
        if args.save_at else set()
    turn_scripts = {str(k): v for k, v in (script.get("turns") or {}).items()}

    status = "completed"
    for turn_index in range(1, args.turns + 1):
        # NB: `status` is the run's finish state — this one is the payload.
        status_payload = transport.get("/status")
        current_turn = dig(status_payload, "turn", default=turn_index)
        # WO-H slice 1 item 6: the turn-boundary reseed. Identical
        # trajectories produce identical (seed, world_turn) labels, so two
        # invocations of the same script at the same seed draw the same dice
        # all campaign long.
        if not args.http:
            seed_module_rng(args.seed, current_turn)
        label = dig(transport.get("/ledger"), "calendar_label", "date_label",
                    default="")
        digest.turn_header(current_turn, label)

        # WO-H slice 1 item 5: the letter-book, answered BEFORE the turn's
        # commands — unanswered letters lapse when the turn ends, and the
        # /command copy of envoy_digest is nulled on every enemy-phase
        # response, so GET /mailbox is where an unattended run must read it.
        for reply in answerer.answer_envoy_digest(
                (transport.get("/mailbox") or {}).get("envoy_digest")):
            drain(transport, digest, answerer, reply, args.strict)

        for text in turn_scripts.get(str(turn_index), []):
            if text.strip().lower() == "end turn":
                continue  # implicit below
            response = transport.post("/command", {"command": text})
            digest.command(text, response)
            drain(transport, digest, answerer, response, args.strict)

        # WO slice 5: the active peace arm, drained like any other command
        # so the settlement dialogue it raises is answered by the same
        # accept-family policy.
        #
        # Sent AFTER the script's own orders (WO slice 5 review). The first
        # cut sent it first, reasoning that "a scripted campaign's commands
        # still decide the turn" — true of military orders, and exactly
        # inverted for diplomatic ones: the overture costs 3 DP and takes
        # Talleyrand out of the country, so a script's own
        # `propose peace to Austria` was refused wholesale ("Talleyrand is
        # currently en route to a foreign court") for want of points the
        # harness had just spent. Ambient runs have no script lines, so the
        # move is a no-op there — measured byte-identical.
        if policy["diplomacy"] == "propose":
            overture = peace_overture(status_payload, turn_index)
            if overture:
                response = transport.post("/command", {"command": overture})
                digest.command(overture, response)
                drain(transport, digest, answerer, response, args.strict)

        if turn_index in save_at:
            saved = transport.post("/save",
                                   {"save_name": f"{args.name}_t{turn_index}"})
            digest.note(f"saved `{args.name}_t{turn_index}` → "
                        f"{first_line(saved.get('message'))}")

        response = transport.post("/command", {"command": "end turn"})
        digest.command("end turn", response)
        digest.enemy_phase(_flatten_enemy_phase(response.get("enemy_phase")))
        digest.autonomous_attacks(response.get("jealousy_attacks"))
        drain(transport, digest, answerer, response, args.strict)

        if response.get("success") is False:
            # A blocker refused the end turn; the drain above answered
            # what it could — retry ONCE, then stop rather than spin.
            response = transport.post("/command", {"command": "end turn"})
            digest.command("end turn (retry)", response)
            digest.enemy_phase(_flatten_enemy_phase(response.get("enemy_phase")))
            digest.autonomous_attacks(response.get("jealousy_attacks"))
            drain(transport, digest, answerer, response, args.strict)
            if response.get("success") is False:
                digest.note("⚠ end turn still refused after the answer "
                            "pass — stopping the run")
                status = "blocked"
                break

        ledger = transport.get("/ledger")
        # `territories` is the player's own region list (ledger.py
        # _build_territories filters on controller == player), so len()
        # is the honest conquest scoreboard. GET /ledger wraps it as
        # {"success":…, "ledger": {…}} — read that nesting explicitly
        # rather than via dig(), which would happily find some other list.
        body = ledger.get("ledger") if isinstance(ledger, dict) else None
        own = (body or {}).get("territories") if isinstance(body, dict) else None
        try:
            morning = (transport.get("/dispatch") or {}).get("dispatch") or {}
        except Exception:
            morning = {}
        # FA-37 / FA-39: `threat` sat in `ledger_line`'s signature and never
        # printed. Measured against a live payload: `GET /ledger` carries no
        # `threat_level` and no `threat` at any depth, so the recursive dig
        # returned None on EVERY turn of every archived run — no digest has
        # a coalition-threat trajectory. The figure lives on the morning
        # dispatch, under `coalition_status`.
        digest.ledger_line(dig(ledger, "treasury", "gold"),
                           dig(ledger, "net_gold", "net"),
                           dig(morning.get("coalition_status"), "threat_level",
                               "threat"),
                           len(own) if isinstance(own, list) else None,
                           economy=(body or {}).get("economy"))
        try:
            digest.dispatch(dig(morning, "text", "content", "message",
                                default=""),
                            events=morning.get("diplomatic_events"),
                            turn_events=morning.get("turn_events"))
        except Exception:
            pass

        if response.get("game_over"):
            digest.note("GAME OVER reported — stopping")
            status = "game-over"
            break

    digest.finish(status)
    print(f"[driver] {status}: {digest.md_path}")

    # WO-H slice 1 item 8: tools/playtest_runs/ is gitignored and
    # overwritten — a digest there is a local artifact, not evidence. The
    # archive copy (digest.md + meta.json, never the raw jsonl) is the
    # committed, citable record. A memo may only cite an archived digest.
    if args.archive:
        archive_dir = (REPO_ROOT / "docs" / "audits" / "playtest_digests"
                       / args.name)
        archive_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(digest.md_path, archive_dir / "digest.md")
        shutil.copy2(digest.meta_path, archive_dir / "meta.json")
        print(f"[driver] archived: {archive_dir}")

    if digest.unknown_blockers and args.strict:
        return 3
    return 0


def main():
    # WO-H slice 1 item 6: PYTHONHASHSEED must be pinned — hash order is
    # load-bearing (the BASELINE_SERIES runner pins it for the same reason),
    # and an "instrument fixed" claim that skipped hash seeding would still
    # be nondeterministic across shells. Re-exec with 0 when unset; the value
    # is recorded in meta.json either way.
    if os.environ.get("PYTHONHASHSEED") is None:
        import subprocess
        env = dict(os.environ, PYTHONHASHSEED="0")
        raise SystemExit(subprocess.call([sys.executable, *sys.argv], env=env))

    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    # name/seed/llm default to None so run() can tell "explicitly passed"
    # from "left at default" — an explicit flag beats the script's own key.
    ap.add_argument("--name", default=None)
    ap.add_argument("--turns", type=int, default=10)
    ap.add_argument("--seed", default=None)
    ap.add_argument("--llm", default=None, choices=["mock", "anthropic"])
    ap.add_argument("--scenario", default="",
                    help="allowlist name for /new_game ('' = default 1805)")
    ap.add_argument("--script", default="",
                    help="JSON script file (see module docstring)")
    ap.add_argument("--from-save", default="",
                    help="save file to load instead of /new_game")
    ap.add_argument("--http", default="",
                    help="drive a live server at this base URL instead of "
                         "in-process (its state WILL be modified)")
    ap.add_argument("--out", default=str(REPO_ROOT / "tools" / "playtest_runs"))
    ap.add_argument("--save-at", default="",
                    help="comma-separated turn numbers to POST /save at")
    ap.add_argument("--objection", default="",
                    choices=["", "trust", "insist", "compromise"])
    ap.add_argument("--diplomacy", default="",
                    choices=["", "decline", "accept", "first", "propose"],
                    help="propose = France actively sues for peace (one "
                         "bilateral overture per turn) and signs what she "
                         "is offered")
    ap.add_argument("--cheats", action="store_true",
                    help="arm DEBUG_MODE for the run (cheat commands work)")
    ap.add_argument("--strict", action="store_true",
                    help="unknown blockers / capped answer chains fail the run")
    ap.add_argument("--verbose", action="store_true",
                    help="let the backend console print to stdout instead of "
                         "server_console.log")
    ap.add_argument("--fresh", action="store_true",
                    help="delete the run directory first")
    ap.add_argument("--archive", action="store_true",
                    help="copy digest.md + meta.json to docs/audits/"
                         "playtest_digests/<name>/ — the committed, citable "
                         "record (memos may only cite archived digests)")
    args = ap.parse_args()
    raise SystemExit(run(args))


if __name__ == "__main__":
    main()
