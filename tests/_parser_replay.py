"""IQ-9 "The Keyless Parser Gate" — replay support for the live-LLM escalation
path (September 18, 2026).

The escalation path — the 0.7 gate, prompt/body assembly, the SDK call, the
typed-exception ladder, the `stop_reason` discard, tool_use extraction, the
strategic-verb remap, `validate_parse_result`, the parser's consumers of a
live result, the CR-5 arms and the Berthier second call — is exercised HERE
without a key and without a network, by injecting a fake SDK client through
the provider's named seam (`AnthropicProvider.bind_sdk_client`) that serves
REAL `anthropic.types.Message` objects from cassettes keyed on
``(kind, utterance, world)``.

Load-bearing rules (each measured in the recon prototype):

* **A cassette miss is a `BaseException`.** Both catch-alls on the path
  (`AnthropicProvider._post_messages` and
  `LLMClient._parse_with_live_provider`) swallow `Exception` into a green
  fast-parser fallback with `llm_error=True`. An `Exception`-derived miss
  therefore lets a "fallback works" pin pass VACUOUSLY. So does an
  `AssertionError` raised inside `create` — which is why the request
  invariants below raise `RequestInvariantViolation(BaseException)` too.
* **The key is the utterance, never the prompt hash.** The prompt is ~16.6 KB
  and changes the moment one order sits in `world.command_history`
  (+355 chars measured), so a hash cannot key a cassette inside a campaign.
  Hashes are PROVENANCE: on replay the live fingerprint is compared with the
  recorded one and a mismatch is tallied as DRIFT, never treated as a miss.
* **The suite never records.** `ReplayMessages.create` has exactly two
  outcomes — serve, or raise. Recording is `tools/record_parser_cassettes.py`,
  opt-in, and no test module imports it (an AST pin in the gate file).
* **The network guard allows loopback.** asyncio's Windows self-pipe is a
  loopback socketpair that CONNECTS to 127.0.0.1, `TestClient` needs an event
  loop, and the IQ-8 driver pins bind a real server on loopback. A blanket
  `connect` ban breaks all three (measured). Everything else — including the
  SDK's own httpx transport, which is refused by host — explodes.

The measured deviation from recon §4.5, stated here so the sensitivity test
is honest: the guard's `RuntimeError` does NOT reach the caller as a
`RuntimeError` through the SDK. `anthropic`'s base client wraps every
transport exception into `APIConnectionError` (after its retries) with the
original as `__cause__`. The sensitivity pin asserts the CAUSE chain.

Imported as ``tests._parser_replay`` everywhere (the repo root is on
``sys.path`` via pyproject's ``pythonpath``), so the guard's state has one
owner module.
"""

from __future__ import annotations

import contextlib
import hashlib
import json
import re
import socket
import warnings
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import anthropic
import httpx
import pydantic
from anthropic.types import Message

REPO_ROOT = Path(__file__).resolve().parents[1]
CASSETTE_DIR = REPO_ROOT / "tests" / "data" / "parser_cassettes"
MANIFEST_PATH = CASSETTE_DIR / "MANIFEST.json"
PHRASINGS_PATH = CASSETTE_DIR / "phrasings.json"

CASSETTE_VERSION = 1
MODEL_PIN = "claude-haiku-4-5"
# The BYOK path: `LLMClient(provider="anthropic", api_key=...)` stamps the key
# on the provider, so `validate_config` passes and the 0.7 gate's key guard
# opens WITHOUT any environment variable. Never `use_real_llm=True` (that
# reads the env key).
REPLAY_API_KEY = "sk-replay-fake"

# The prompt builder's own markers (backend/ai/prompt_builder.py). NON-greedy:
# the greedy form over-captured the moment a `## RECENT PLAYER COMMANDS` block
# followed the utterance (measured).
UTTERANCE_RE = re.compile(r'## Command to Parse\n"(.*?)"\n', re.DOTALL)
BERTHIER_RE = re.compile(r'The Emperor said: "(.*?)"\n', re.DOTALL)

PROVENANCE_VALUES = ("recorded", "authored")
KINDS = ("parse", "berthier")


# ═══════════════════════════════════════════════════════════════════════════
# Faults — BaseException on purpose (see the module docstring)
# ═══════════════════════════════════════════════════════════════════════════

class ReplayFault(BaseException):
    """Base of every replay fault. NOT an Exception: the provider's catch-all
    and the client's catch-all both swallow Exception into a green
    fast-parser fallback (measured), which would turn a broken replay into a
    passing test."""


class CassetteMiss(ReplayFault):
    """No cassette for this (kind, utterance, world). The suite never
    records; a miss is a test-authoring defect and must propagate."""


class RequestInvariantViolation(ReplayFault):
    """The request body broke a CR-3/CR-5 guardrail (forced tool, temperature
    0, model pin, max_tokens, no tools on the Berthier body)."""


class CassetteDriftWarning(UserWarning):
    """A recorded cassette's prompt hash no longer matches the live prompt
    (acknowledged in MANIFEST.json). Raised as a warning every run so the
    summary counts it; an UNacknowledged drift fails the hygiene pin."""


# ═══════════════════════════════════════════════════════════════════════════
# The network guard (T0)
# ═══════════════════════════════════════════════════════════════════════════

LOOPBACK_HOSTS = frozenset({"127.0.0.1", "::1", "localhost", "0.0.0.0", "::"})

_GUARD: Dict[str, Any] = {"installed": False}


def _host_of(address) -> str:
    if isinstance(address, (tuple, list)) and address:
        host = address[0]
    else:
        host = address
    if isinstance(host, bytes):
        host = host.decode("ascii", "replace")
    return str(host)


def is_loopback_host(host: Any) -> bool:
    """The allow-list. Loopback by name or by address (IPv4 127/8 and ::1);
    everything else is the network."""
    host = str(host or "")
    if host in LOOPBACK_HOSTS:
        return True
    if host.startswith("127."):
        return True
    return False


def _guarded_connect(self, address, *args, **kwargs):
    host = _host_of(address)
    if is_loopback_host(host):
        return _GUARD["socket_connect"](self, address, *args, **kwargs)
    raise RuntimeError(
        f"IQ-9 network guard: network disabled in the test suite "
        f"(socket connect to {host!r})")


def _guarded_handle_request(self, request):
    host = request.url.host
    if is_loopback_host(host):
        return _GUARD["httpx_handle_request"](self, request)
    raise RuntimeError(
        f"IQ-9 network guard: network disabled in the test suite "
        f"(HTTP {request.method} {request.url})")


async def _guarded_handle_async_request(self, request):
    host = request.url.host
    if is_loopback_host(host):
        return await _GUARD["httpx_handle_async_request"](self, request)
    raise RuntimeError(
        f"IQ-9 network guard: network disabled in the test suite "
        f"(async HTTP {request.method} {request.url})")


def install_network_guard() -> None:
    """Refuse every non-loopback connection for the rest of the process.

    Idempotent. Patches the two httpx transports (what the SDK — and any
    httpx user — actually sends through) and `socket.socket.connect` (the
    belt under everything else: urllib, requests, raw sockets)."""
    if _GUARD["installed"]:
        return
    _GUARD["socket_connect"] = socket.socket.connect
    _GUARD["httpx_handle_request"] = httpx.HTTPTransport.handle_request
    _GUARD["httpx_handle_async_request"] = (
        httpx.AsyncHTTPTransport.handle_async_request)
    socket.socket.connect = _guarded_connect
    httpx.HTTPTransport.handle_request = _guarded_handle_request
    httpx.AsyncHTTPTransport.handle_async_request = _guarded_handle_async_request
    _GUARD["installed"] = True


def uninstall_network_guard() -> None:
    if not _GUARD["installed"]:
        return
    socket.socket.connect = _GUARD["socket_connect"]
    httpx.HTTPTransport.handle_request = _GUARD["httpx_handle_request"]
    httpx.AsyncHTTPTransport.handle_async_request = (
        _GUARD["httpx_handle_async_request"])
    _GUARD["installed"] = False


def network_guard_installed() -> bool:
    return bool(_GUARD["installed"])


@contextlib.contextmanager
def network_guard():
    """Install the guard for a block (a no-op when the suite already installed
    it at conftest import — the guard is process-wide and idempotent)."""
    was_installed = _GUARD["installed"]
    install_network_guard()
    try:
        yield
    finally:
        if not was_installed:
            uninstall_network_guard()


# ═══════════════════════════════════════════════════════════════════════════
# Request shape: kind, utterance, fingerprint, invariants
# ═══════════════════════════════════════════════════════════════════════════

def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def body_kind(body: Dict) -> str:
    """A tool-mode body is the PARSE call; a body with no tools is Berthier's
    text-mode recovery call."""
    return "parse" if "tools" in body else "berthier"


def utterance_of(body: Dict) -> Optional[str]:
    """The player's utterance, read off the prompt the body carries."""
    try:
        content = body["messages"][0]["content"]
    except (KeyError, IndexError, TypeError):
        return None
    if not isinstance(content, str):
        return None
    pattern = UTTERANCE_RE if body_kind(body) == "parse" else BERTHIER_RE
    m = pattern.search(content)
    return m.group(1) if m else None


def fingerprint(body: Dict) -> Dict[str, Any]:
    """Provenance hashes of a request body — NEVER the cassette key."""
    prompt = ""
    try:
        prompt = body["messages"][0]["content"]
    except (KeyError, IndexError, TypeError):
        pass
    if not isinstance(prompt, str):
        prompt = json.dumps(prompt, sort_keys=True)
    fp = {
        "system_sha256": _sha256(str(body.get("system") or "")),
        "prompt_sha256": _sha256(prompt),
        "prompt_chars": len(prompt),
    }
    if "tools" in body:
        fp["tool_schema_sha256"] = _sha256(
            json.dumps(body["tools"], sort_keys=True))
    return fp


def request_snapshot(body: Dict) -> Dict[str, Any]:
    """The `request` block a cassette stores: pinned scalars + hashes."""
    snap = {
        "model": body.get("model"),
        "max_tokens": body.get("max_tokens"),
    }
    if "temperature" in body:
        snap["temperature"] = body["temperature"]
    if "tool_choice" in body:
        snap["tool_choice"] = body["tool_choice"]
    snap.update(fingerprint(body))
    return snap


def check_request_invariants(body: Dict) -> None:
    """The CR-3/CR-5 guardrails, asserted on EVERY replayed request. Raises
    RequestInvariantViolation (a BaseException — an AssertionError here would
    be swallowed into a green fallback)."""
    from backend.ai.providers import PARSE_TOOL, PARSE_TOOL_NAME

    def fail(what: str) -> None:
        raise RequestInvariantViolation(
            f"IQ-9 replay: request invariant broken — {what}")

    if body.get("model") != MODEL_PIN:
        fail(f"model {body.get('model')!r} != {MODEL_PIN!r}")
    if body.get("max_tokens") != 1000:
        fail(f"max_tokens {body.get('max_tokens')!r} != 1000")
    if not isinstance(body.get("system"), str) or not body["system"]:
        fail("system prompt missing")
    if body_kind(body) == "parse":
        if body.get("tools") != [PARSE_TOOL]:
            fail("tools != [PARSE_TOOL] (the tool schema drifted or is absent)")
        if body.get("tool_choice") != {"type": "tool", "name": PARSE_TOOL_NAME}:
            fail(f"tool_choice {body.get('tool_choice')!r} is not the forced "
                 f"{PARSE_TOOL_NAME!r}")
        if body.get("temperature") != 0:
            fail(f"temperature {body.get('temperature')!r} != 0 on the parse "
                 f"body (CR-5 guardrail b)")
    else:
        if "tools" in body or "tool_choice" in body:
            fail("the Berthier text-mode body must carry no tools/tool_choice")
        if "temperature" in body:
            fail("the Berthier text-mode body must not pin temperature")


# ═══════════════════════════════════════════════════════════════════════════
# Message builders — real anthropic.types.Message objects
# ═══════════════════════════════════════════════════════════════════════════

def wire_message(content: List[Dict], stop_reason: str = "tool_use", *,
                 message_id: str = "msg_replay",
                 usage: Optional[Dict] = None) -> Dict:
    """The full wire shape of a Messages response (what message.to_dict()
    yields): id/type/role/model/stop_reason/stop_sequence/content/usage."""
    return {
        "id": message_id, "type": "message", "role": "assistant",
        "model": MODEL_PIN, "stop_sequence": None,
        "stop_reason": stop_reason,
        "content": content,
        "usage": usage or {"input_tokens": 5000, "output_tokens": 120},
    }


def tool_use_content(input_obj: Any, *, tool_name: Optional[str] = None,
                     block_id: str = "toolu_replay") -> List[Dict]:
    from backend.ai.providers import PARSE_TOOL_NAME
    return [{"type": "tool_use", "id": block_id,
             "name": tool_name or PARSE_TOOL_NAME, "input": input_obj}]


def tool_message(input_obj: Any, stop_reason: str = "tool_use", *,
                 tool_name: Optional[str] = None) -> Message:
    """A Messages response carrying the forced tool call."""
    return message_from_wire(
        wire_message(tool_use_content(input_obj, tool_name=tool_name),
                     stop_reason))


def text_message(text: str, stop_reason: str = "end_turn") -> Message:
    """A text-mode Messages response (Berthier recovery, or the S14 fallback)."""
    return message_from_wire(wire_message(
        [{"type": "text", "text": text}], stop_reason,
        message_id="msg_replay_text",
        usage={"input_tokens": 500, "output_tokens": 40}))


def message_from_wire(wire: Dict) -> Message:
    """Build the SDK's own Message type from a wire dict.

    `Message.model_validate` first — the SDK's pydantic model validates the
    cassette shape, so a mistyped cassette fails loudly. A shape the API's own
    schema forbids (S3: a STRING tool input) is rejected by validation but is
    exactly what the SDK's lenient RESPONSE construction (`construct_type`)
    would hand back from a real wire — so that arm falls back to
    `Message.construct`, mirroring the SDK. Either way `to_dict()` yields the
    wire dict `_post_messages` reads (measured)."""
    try:
        return Message.model_validate(wire)
    except pydantic.ValidationError:
        return Message.construct(**wire)


API_ERROR_KINDS = (
    "rate_limit", "auth", "permission", "not_found", "bad_request",
    "timeout", "connection", "overloaded", "generic",
)


def make_api_error(kind: str) -> BaseException:
    """The nine typed failures `_post_messages` distinguishes, constructed
    offline exactly as the SDK would raise them."""
    req = httpx.Request("POST", "https://api.anthropic.com/v1/messages")

    def status(code: int, error_type: str):
        return httpx.Response(
            code, request=req,
            json={"type": "error",
                  "error": {"type": error_type, "message": kind}})

    if kind == "rate_limit":
        return anthropic.RateLimitError(
            "rate limited", response=status(429, "rate_limit_error"), body=None)
    if kind == "auth":
        return anthropic.AuthenticationError(
            "invalid api key", response=status(401, "authentication_error"),
            body=None)
    if kind == "permission":
        return anthropic.PermissionDeniedError(
            "forbidden", response=status(403, "permission_error"), body=None)
    if kind == "not_found":
        return anthropic.NotFoundError(
            "no such model", response=status(404, "not_found_error"), body=None)
    if kind == "bad_request":
        return anthropic.BadRequestError(
            "malformed request", response=status(400, "invalid_request_error"),
            body=None)
    if kind == "timeout":
        return anthropic.APITimeoutError(request=req)
    if kind == "connection":
        return anthropic.APIConnectionError(request=req)
    if kind == "overloaded":
        return anthropic.APIStatusError(
            "overloaded", response=status(529, "overloaded_error"), body=None)
    if kind == "generic":
        return ValueError("something unexpected inside the SDK call")
    raise KeyError(f"unknown API error kind {kind!r}; one of {API_ERROR_KINDS}")


# ═══════════════════════════════════════════════════════════════════════════
# Cassettes
# ═══════════════════════════════════════════════════════════════════════════

def cassette_key(cassette: Dict) -> Tuple[str, str, str]:
    return (cassette.get("kind", "parse"), cassette["utterance"],
            cassette["world"])


def authored_cassette(cassette_id: str, utterance: str, world: str, *,
                      response: Optional[Message] = None,
                      error: Optional[str] = None,
                      kind: str = "parse",
                      notes: str = "") -> Dict:
    """An in-code cassette (Tier C/D shapes): a served Message OR a raised
    typed error (by `make_api_error` kind)."""
    if (response is None) == (error is None):
        raise ValueError("an authored cassette serves a response OR an error")
    entry = {"id": cassette_id, "kind": kind, "utterance": utterance,
             "world": world, "history": [], "provenance": "authored",
             "notes": notes}
    if response is not None:
        entry["response"] = response.to_dict()
    else:
        entry["error"] = error
    return entry


def load_cassette(cassette_id: str) -> Dict:
    path = CASSETTE_DIR / f"{cassette_id}.json"
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def cassette_files() -> List[Path]:
    return sorted(p for p in CASSETTE_DIR.glob("*.json")
                  if p.name not in ("MANIFEST.json", "phrasings.json"))


def load_all_cassettes() -> Dict[str, Dict]:
    out = {}
    for path in cassette_files():
        with open(path, encoding="utf-8") as fh:
            entry = json.load(fh)
        out[entry["id"]] = entry
    return out


def load_manifest() -> Dict:
    with open(MANIFEST_PATH, encoding="utf-8") as fh:
        return json.load(fh)


def load_phrasings() -> Dict:
    with open(PHRASINGS_PATH, encoding="utf-8") as fh:
        return json.load(fh)


def write_cassette(entry: Dict) -> Path:
    CASSETTE_DIR.mkdir(parents=True, exist_ok=True)
    path = CASSETTE_DIR / f"{entry['id']}.json"
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(entry, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    return path


class ReplayMessages:
    """Stands in for `anthropic.Anthropic().messages`. Serves by
    (kind, utterance, world); NEVER records — a miss raises."""

    def __init__(self, cassettes: Iterable[Dict], world_key: str,
                 manifest: Optional[Dict] = None):
        self.world_key = world_key
        self.by_key: Dict[Tuple[str, str, str], Dict] = {}
        for entry in cassettes:
            self.by_key[cassette_key(entry)] = entry
        self.manifest = manifest
        self.calls: List[Dict] = []
        self.served: List[str] = []
        self.misses: List[Tuple[str, str, str]] = []
        # id -> (recorded_prompt_sha256, live_prompt_sha256)
        self.drifted: Dict[str, Tuple[str, str]] = {}

    def create(self, **body):
        self.calls.append(body)
        check_request_invariants(body)
        kind = body_kind(body)
        utterance = utterance_of(body)
        key = (kind, utterance, self.world_key)
        entry = self.by_key.get(key)
        if entry is None:
            self.misses.append(key)
            raise CassetteMiss(
                f"IQ-9 replay: cassette MISS for {key!r} (the suite never "
                f"records; author or record a cassette)")
        self._tally_drift(entry, body)
        self.served.append(entry["id"])
        if entry.get("error"):
            raise make_api_error(entry["error"])
        if "raise" in entry:
            raise entry["raise"]
        return message_from_wire(entry["response"])

    def _tally_drift(self, entry: Dict, body: Dict) -> None:
        recorded = (entry.get("request") or {}).get("prompt_sha256")
        if not recorded:
            return
        live = fingerprint(body)["prompt_sha256"]
        if live != recorded:
            self.drifted[entry["id"]] = (recorded, live)
            if entry.get("provenance") == "recorded":
                ack = ((self.manifest or {}).get("cassettes", {})
                       .get(entry["id"], {}).get("drift"))
                warnings.warn(
                    f"cassette {entry['id']!r} prompt drifted "
                    f"({'acknowledged' if ack else 'UNACKNOWLEDGED'})",
                    CassetteDriftWarning, stacklevel=3)


class ReplayClient:
    """The fake SDK client: `.messages.create(**body)` is all the provider
    reads (`_post_messages`)."""

    def __init__(self, cassettes: Iterable[Dict], world_key: str,
                 manifest: Optional[Dict] = None):
        self.messages = ReplayMessages(cassettes, world_key, manifest)

    # conveniences the tests read
    @property
    def calls(self) -> List[Dict]:
        return self.messages.calls

    @property
    def misses(self) -> List[Tuple[str, str, str]]:
        return self.messages.misses

    @property
    def drifted(self) -> Dict[str, Tuple[str, str]]:
        return self.messages.drifted

    @property
    def served(self) -> List[str]:
        return self.messages.served

    def call_kinds(self) -> List[str]:
        return [body_kind(b) for b in self.calls]


def armed_parser(cassettes: Iterable[Dict], world_key: str,
                 manifest: Optional[Dict] = None):
    """A CommandParser whose LLM client is a BYOK Anthropic client bound to a
    ReplayClient — the /config/llm swap shape. Returns (parser, replay)."""
    from backend.ai.llm_client import LLMClient
    from backend.commands.parser import CommandParser

    parser = CommandParser(use_real_llm=False)
    parser.llm = LLMClient(provider="anthropic", api_key=REPLAY_API_KEY)
    replay = ReplayClient(cassettes, world_key, manifest)
    parser.llm.provider.bind_sdk_client(replay)
    if parser.llm.provider._client() is not replay:
        raise RuntimeError("IQ-9 replay: the provider did not honour the bound "
                           "SDK client")
    return parser, replay


def all_file_cassettes_for(world_key: Optional[str] = None) -> List[Dict]:
    """Every committed cassette (optionally one world's)."""
    entries = list(load_all_cassettes().values())
    if world_key:
        entries = [e for e in entries if e["world"] == world_key]
    return entries
