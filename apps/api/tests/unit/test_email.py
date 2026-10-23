"""Unit tests for email abstraction."""

import asyncio
import logging

from admin_template.core.email import (
    EmailMessage,
    NoOpEmailProvider,
    get_email_provider,
    send_email,
    set_email_provider,
)


class _RecordingProvider:
    def __init__(self):
        self.sent = []

    async def send(self, message):
        self.sent.append(message)


def test_noop_provider_logs(caplog):
    caplog.set_level(logging.INFO)
    provider = NoOpEmailProvider()
    msg = EmailMessage(to="a@b.com", subject="s", body="hello")
    asyncio.run(provider.send(msg))
    assert any("email.noop" in r.message for r in caplog.records)


def test_send_email_uses_provider():
    rec = _RecordingProvider()
    set_email_provider(rec)
    try:
        msg = EmailMessage(to="a@b.com", subject="s", body="hello")
        asyncio.run(send_email(msg))
        assert rec.sent == [msg]
        assert get_email_provider() is rec
    finally:
        set_email_provider(NoOpEmailProvider())


def test_html_optional():
    msg = EmailMessage(to="a@b.com", subject="s", body="b", html="<b>x</b>")
    assert msg.html == "<b>x</b>"
