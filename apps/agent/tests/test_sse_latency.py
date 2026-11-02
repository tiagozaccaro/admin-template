"""Regression tests for first-token latency (SC-002).

SC-002 requires 95% of chat requests to return the first token within 3
seconds. The SSE stream emits `first_token_ms` on the first delta; this
test asserts the value is sane (>= 0, < 3000ms) and that the stream
completes with a `done` event carrying `latency_ms`.
"""

import asyncio
import json
from unittest.mock import patch

from admin_template_agent.routers.chat import _agent


def _collect_events(response) -> list:
    """Drain a StreamingResponse's body iterator into parsed JSON events."""
    events = []

    async def _drain():
        async for line in response.body_iterator:
            if not line.startswith("data: "):
                continue
            payload = line[6:].strip()
            if payload == "[DONE]":
                break
            try:
                events.append(json.loads(payload))
            except json.JSONDecodeError:
                events.append({"raw": payload})

    asyncio.run(_drain())
    return events


def test_first_token_ms_emitted_within_budget() -> None:
    """SC-002: first_token_ms must be present and under the 3s budget."""
    with patch.object(_agent, "chat_stream") as mock_stream:

        async def _fake_stream(message, approvals=None):
            yield "Hello"
            yield " world"

        mock_stream.side_effect = lambda *a, **kw: _fake_stream(*a, **kw)

        from admin_template_agent.routers.chat import chat_agent

        response = asyncio.run(
            chat_agent(
                {"prompt_input": "hi", "session_id": "latency-test"},
                token=None,
            )
        )
        events = _collect_events(response)

    assert events, "SSE stream emitted no events"
    first = events[0]
    assert "first_token_ms" in first, f"first event missing first_token_ms: {first}"
    assert first["first_token_ms"] >= 0
    assert first["first_token_ms"] < 3000, (
        f"first_token_ms={first['first_token_ms']} exceeds 3s SC-002 budget"
    )
    # The stream must end with a `done` event carrying latency_ms.
    done = next((e for e in events if e.get("done")), None)
    assert done is not None, f"no done event in {events}"
    assert "latency_ms" in done


def test_first_token_ms_absent_when_no_tokens() -> None:
    """An empty stream still completes with a done event."""
    with patch.object(_agent, "chat_stream") as mock_stream:

        async def _empty(message, approvals=None):
            return
            yield  # pragma: no cover

        mock_stream.side_effect = lambda *a, **kw: _empty(*a, **kw)

        from admin_template_agent.routers.chat import chat_agent

        response = asyncio.run(
            chat_agent(
                {"prompt_input": "hi", "session_id": "empty-test"},
                token=None,
            )
        )
        events = _collect_events(response)

    done = next((e for e in events if e.get("done")), None)
    assert done is not None
    assert "latency_ms" in done
