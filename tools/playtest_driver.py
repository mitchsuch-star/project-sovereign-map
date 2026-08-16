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

Outputs (under --out, default tools/playtest_runs/<name>/ — gitignored):
  digest.md      the human read — one block per turn
  digest.jsonl   the machine read — one record per event
  meta.json      seed/mode/args/finish state
  saves/         the sandboxed SAVE_DIR (autosave + --save-at snapshots)

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
import json
import os
import shutil
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# ═══════════════════════════════════════════════════════════════════════
# Answer policy — every default is a DECISION a digest reader can audit.
# ═══════════════════════════════════════════════════════════════════════

POLICY_DEFAULTS = {
    # Marshal objection: trust builds goodwill and never dead-ends a run.
    "objection": "trust",           # trust | insist | compromise
    # Incoming proposals / settlement offers / envoy letters: decline —
    # an unattended run must not sign treaties nobody scripted. Override
    # per-run when the playtest IS about diplomacy.
    "diplomacy": "decline",         # decline | accept | first
    # Post-capture: secure (plunder is the special case worth scripting).
    "capture": "secure",            # secure | plunder
    # W6-8 estate stage of the same popup:
    "estate": "respect",            # respect | confiscate
    # Ney's recklessness trigger:
    "glorious_charge": "restrain",  # restrain | charge
    # Talleyrand pre-proposal objection:
    "diplomatic_objection": "proceed",   # proceed | modify | cancel
    # Talleyrand redemption arc (rare):
    "redemption": "dismiss",
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
}

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


def first_line(text, limit=170):
    if not text:
        return ""
    for line in str(text).splitlines():
        line = line.strip()
        if line:
            return (line[: limit - 1] + "…") if len(line) > limit else line
    return ""


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
        self.recent.append((str(key), str(answer)))
        self._md(f"  - POPUP {key}: {summary} → {answer}")
        self.record("popup", key=key, summary=summary, answer=answer)

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
        lines = [first_line(a.get("message") or a.get("action")
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
        taken = [a for a in actions
                 if any(w in str(a.get("message") or "").lower()
                        for w in ("captur", "has fallen", "falls to",
                                  "taken by", "seized"))]
        for act in taken[:6]:
            self._md(f"  - 🏴 {act.get('nation', '?')}: "
                     f"{first_line(act.get('message'), 150)}")

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
        self.record("enemy_phase", count=len(actions), attacks=len(attacks),
                    captures=len(taken), verbs=verbs,
                    actions=[{"nation": a.get("nation"),
                              "action": _verb(a),
                              "marshal": (a.get("ai_action") or {}).get("marshal")
                              if isinstance(a.get("ai_action"), dict) else None,
                              "message": first_line(a.get("message"), 200)}
                             for a in actions])

    def ledger_line(self, treasury, net, threat, provinces=None):
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

    def dispatch(self, text):
        head = first_line(text, 200)
        if head:
            self._md(f"- DISPATCH: {head}")
            self.record("dispatch", headline=head)

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

def _option_id(option):
    if isinstance(option, dict):
        return option.get("id") or option.get("choice") or option.get("keyword")
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


def _interrupt_report(response):
    """The first strategic report awaiting player input (NPC-16).

    An end-turn interrupt never reaches response["pending_interrupt"];
    the client finds it here and so must the driver. Returns {} when
    there is none, so callers can treat it as a falsy payload."""
    if not isinstance(response, dict):
        return {}
    for report in response.get("strategic_reports") or []:
        if isinstance(report, dict) and report.get("requires_input"):
            return report
    return {}


class Answerer:
    """Scans a response for blocking surfaces, answers them by policy,
    and digests everything. Returns the FOLLOW-UP responses it produced
    (each of which is scanned in turn by the caller, up to a cap)."""

    def __init__(self, transport, digest, policy, strict):
        self.t = transport
        self.d = digest
        self.policy = policy
        self.strict = strict

    def scan(self, response):
        followups = []

        for key in DISPLAY_ONLY_KEYS:
            payload = response.get(key)
            if payload:
                self.d.popup(key, _summ(payload, "title", "message", "nation",
                                        "headline"), "display-only")

        if response.get("battle_report"):
            self.d.battle(response["battle_report"])

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
            payload = (_as_dict(response.get("pending_interrupt"))
                       or _interrupt_report(response))
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
            payload = _as_dict(response["pending_capture_choice"])
            stage = payload.get("stage", "capture")
            choice = (self.policy["estate"] if stage == "estate"
                      else self.policy["capture"])
            self.d.popup(f"capture_choice[{stage}]",
                         _summ(payload, "region", "capturer"), choice)
            body = {"choice": choice}
            if payload.get("dialogue_id") is not None:
                body["dialogue_id"] = payload["dialogue_id"]
            followups.append(self.t.post("/capture_choice", body))

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

        # 7. Diplomatic dialogue (incoming proposals, settlement offers,
        #    ultimatums, envoys — anything answerable on the dialogue stack).
        dialogue = (response.get("diplomatic_dialogue")
                    or response.get("incoming_proposal")
                    or response.get("incoming_settlement_offer"))
        if dialogue and isinstance(dialogue, dict):
            choice = self._dialogue_choice(dialogue)
            self.d.popup("diplomatic_dialogue",
                         _summ(dialogue, "type", "nation", "from_nation",
                               "proposal_type"),
                         choice or "(left standing)")
            if choice is not None:
                body = {"choice": choice}
                if dialogue.get("dialogue_id") is not None:
                    body["dialogue_id"] = dialogue["dialogue_id"]
                followups.append(
                    self.t.post("/respond_to_diplomatic_dialogue", body))

        return followups

    def _dialogue_choice(self, dialogue):
        """Pick a dialogue answer. Order: the type table (types whose
        right answer the driver knows even without an options list), then
        the diplomacy policy over the dialogue's OWN option keywords."""
        dtype = str(dialogue.get("type") or "")
        options = dialogue.get("options") or dialogue.get("choices") or []
        keywords = [str(_option_id(o) or "").lower() for o in options]

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
                if self.policy["diplomacy"] == "accept":
                    return (find("confirm_pair", "confirm", "substitute")
                            or "confirm_pair_substitute")
                return find("keep") or "keep"
            if policy_key in ("war_purpose", "ultimatum"):
                answer = self.policy[policy_key]
                if answer == "defy":
                    return find("defy", "refuse") or "defy"
                return answer

        mode = self.policy["diplomacy"]
        if mode == "accept":
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
            key, choice = looping[0]
            digest.note(f"⚠ ANSWER CYCLE — `{key}` answered `{choice}` "
                        f"{counts[looping[0]]}× in one post; the policy "
                        f"cannot resolve this surface. Stopping the chain.")
            digest.unknown_blockers.append(
                {"key": key, "choice": choice, "reason": "answer-cycle"})
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
        args.name = script.get("name", args.name)
        args.seed = script.get("seed", args.seed)
        args.llm = script.get("llm", args.llm)

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

    digest = Digest(out_dir, {
        "name": args.name, "seed": args.seed, "llm": args.llm,
        "transport": transport.label, "policy": policy,
        "turns_requested": args.turns, "started": time.strftime("%Y-%m-%d %H:%M"),
        "from_save": args.from_save or "",
    })
    answerer = Answerer(transport, digest, policy, args.strict)

    # Boot ------------------------------------------------------------------
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
        current_turn = dig(transport.get("/status"), "turn", default=turn_index)
        label = dig(transport.get("/ledger"), "calendar_label", "date_label",
                    default="")
        digest.turn_header(current_turn, label)

        for text in turn_scripts.get(str(turn_index), []):
            if text.strip().lower() == "end turn":
                continue  # implicit below
            response = transport.post("/command", {"command": text})
            digest.command(text, response)
            drain(transport, digest, answerer, response, args.strict)

        if turn_index in save_at:
            saved = transport.post("/save",
                                   {"save_name": f"{args.name}_t{turn_index}"})
            digest.note(f"saved `{args.name}_t{turn_index}` → "
                        f"{first_line(saved.get('message'))}")

        response = transport.post("/command", {"command": "end turn"})
        digest.command("end turn", response)
        digest.enemy_phase(_flatten_enemy_phase(response.get("enemy_phase")))
        drain(transport, digest, answerer, response, args.strict)

        if response.get("success") is False:
            # A blocker refused the end turn; the drain above answered
            # what it could — retry ONCE, then stop rather than spin.
            response = transport.post("/command", {"command": "end turn"})
            digest.command("end turn (retry)", response)
            digest.enemy_phase(_flatten_enemy_phase(response.get("enemy_phase")))
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
        digest.ledger_line(dig(ledger, "treasury", "gold"),
                           dig(ledger, "net_gold", "net"),
                           dig(ledger, "threat_level", "threat"),
                           len(own) if isinstance(own, list) else None)
        try:
            digest.dispatch(dig(transport.get("/dispatch"),
                                "text", "content", "message", default=""))
        except Exception:
            pass

        if response.get("game_over"):
            digest.note("GAME OVER reported — stopping")
            status = "game-over"
            break

    digest.finish(status)
    print(f"[driver] {status}: {digest.md_path}")
    if digest.unknown_blockers and args.strict:
        return 3
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--name", default="run")
    ap.add_argument("--turns", type=int, default=10)
    ap.add_argument("--seed", default="historical")
    ap.add_argument("--llm", default="mock", choices=["mock", "anthropic"])
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
                    choices=["", "decline", "accept", "first"])
    ap.add_argument("--cheats", action="store_true",
                    help="arm DEBUG_MODE for the run (cheat commands work)")
    ap.add_argument("--strict", action="store_true",
                    help="unknown blockers / capped answer chains fail the run")
    ap.add_argument("--verbose", action="store_true",
                    help="let the backend console print to stdout instead of "
                         "server_console.log")
    ap.add_argument("--fresh", action="store_true",
                    help="delete the run directory first")
    args = ap.parse_args()
    raise SystemExit(run(args))


if __name__ == "__main__":
    main()
