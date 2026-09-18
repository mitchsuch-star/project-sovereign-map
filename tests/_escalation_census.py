"""IQ-9 escalation census — a pytest plugin, loaded ONLY by the T0 census pin
(`-p tests._escalation_census`), never auto-registered.

Counts the suite's LIVE-ESCALATION OPPORTUNITIES without setting a mode or a
key: every ENV-DERIVED LLMClient (a bare `LLMClient()` / `CommandParser()` /
`LLMClient.create()` whose mode came from `LLM_MODE`) that reaches a call
which WOULD escalate to the provider under the shipped gate minus its two
mode/key guards:

  * `_should_fallback_to_llm` minus the provider-is-mock / no-key guards
  * `reparse_with_llm` (the CR-2 forced retry) minus the same two guards
  * `generate_berthier_recovery`'s live arm (not mock, not skip_llm)

One JSON line per opportunity to `ESCALATION_CENSUS_OUT`. The recon of
September 16, 2026 ran this over the whole suite and found 267 opportunities,
263 on clients the test itself pinned to mock and **4 on env-derived clients
in 3 test ids** — which went LIVE on any checkout whose `.env` said
`LLM_MODE=anthropic`. T0 (the conftest pin) makes an env-derived client mock
by construction; the census pin re-runs those three ids under
`LLM_MODE=anthropic` and asserts the env-derived count is zero.
"""

from __future__ import annotations

import json
import os

OUT_ENV = "ESCALATION_CENSUS_OUT"


def _emit(kind, client, text, extra=None):
    out = os.environ.get(OUT_ENV)
    if not out:
        return
    rec = {
        "kind": kind,
        "test": os.environ.get("PYTEST_CURRENT_TEST", "?"),
        "env_derived": bool(getattr(client, "_iq9_env_derived", False)),
        "provider_name": getattr(client, "provider_name", "?"),
        "text": (text or "")[:80],
    }
    if extra:
        rec.update(extra)
    with open(out, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec) + "\n")


def install_census() -> None:
    """Wrap the client's constructors and the three escalation seams."""
    import backend.ai.llm_client as lc
    from backend.ai.validation import NON_ORDER_ACTIONS

    if getattr(lc.LLMClient, "_iq9_census_installed", False):
        return

    orig_init = lc.LLMClient.__init__

    def init(self, use_real_api=None, provider=None, api_key=None):
        # env-derived == the mode came from LLM_MODE
        self._iq9_env_derived = (provider is None and use_real_api is None
                                 and api_key is None)
        orig_init(self, use_real_api=use_real_api, provider=provider,
                  api_key=api_key)
    lc.LLMClient.__init__ = init

    orig_create = lc.LLMClient.create.__func__

    def create(cls, user_api_key=None):
        client = orig_create(cls, user_api_key)
        client._iq9_env_derived = (user_api_key is None)
        return client
    lc.LLMClient.create = classmethod(create)

    orig_gate = lc.LLMClient._should_fallback_to_llm

    def gate(self, fast_result, game_state):
        would = (fast_result.confidence < lc.LLM_FALLBACK_CONFIDENCE_THRESHOLD
                 and not fast_result.refusal
                 and game_state is not None
                 and fast_result.action not in NON_ORDER_ACTIONS)
        if would:
            _emit("parse_escalation", self, fast_result.raw_command,
                  {"confidence": fast_result.confidence,
                   "action": fast_result.action})
        return orig_gate(self, fast_result, game_state)
    lc.LLMClient._should_fallback_to_llm = gate

    orig_reparse = lc.LLMClient.reparse_with_llm

    def reparse(self, command_text, game_state, fast_result_dict):
        if (isinstance(game_state, dict)
                and not (fast_result_dict or {}).get("llm_error")):
            _emit("cr2_retry", self, command_text)
        return orig_reparse(self, command_text, game_state, fast_result_dict)
    lc.LLMClient.reparse_with_llm = reparse

    orig_berthier = lc.LLMClient.generate_berthier_recovery

    def berthier(self, raw_command, game_state=None, partial_parse=None,
                 skip_llm=False):
        if not skip_llm:
            _emit("berthier_live_arm", self, raw_command)
        return orig_berthier(self, raw_command, game_state=game_state,
                             partial_parse=partial_parse, skip_llm=skip_llm)
    lc.LLMClient.generate_berthier_recovery = berthier

    lc.LLMClient._iq9_census_installed = True


def pytest_configure(config):
    # The census must never itself be a live-call vector: it is run with
    # LLM_MODE=anthropic in the environment to PROVE the pin holds, so the
    # loopback-allowing guard goes up here too (idempotent with conftest's).
    from tests._parser_replay import install_network_guard
    install_network_guard()
    install_census()


def read_census(path) -> list:
    rows = []
    try:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
    except FileNotFoundError:
        pass
    return rows
